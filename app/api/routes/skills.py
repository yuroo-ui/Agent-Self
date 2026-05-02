"""Agent-to-Agent Skill Marketplace API.

Agents can:
1. Register themselves
2. Publish SKILL.md files
3. Discover skills from other agents
4. Learn/adapt skills into their own knowledge
5. Review and rate learned skills

The network effect: more agents → more skills → smarter everyone.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.models import (
    Agent, Skill, LearningLog, PeerConnection, SkillReview,
    AgentStatus, SkillStatus, ScanResult, LearningStatus
)
from app.sandbox.scanner import SkillScanner
from app.services.trust import TrustEngine

router = APIRouter(prefix="/api/v1", tags=["marketplace"])


# ═══════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════

class AgentRegister(BaseModel):
    name: str
    description: str = ""
    agent_id: Optional[str] = None  # Auto-generated if not provided
    public_key: Optional[str] = None


class AgentResponse(BaseModel):
    id: int
    agent_id: str
    name: str
    description: str
    status: str
    trust_score: float
    skills_published: int
    skills_learned: int
    peers_connected: int
    created_at: datetime

    class Config:
        from_attributes = True


class SkillPublish(BaseModel):
    name: str
    description: str = ""
    content: str  # The full SKILL.md content
    triggers: list[str] = []
    tags: list[str] = []
    category: str = "general"
    version: str = "1.0.0"
    dependencies: list[str] = []


class SkillResponse(BaseModel):
    id: int
    skill_id: str
    slug: str
    name: str
    description: str
    content: str
    triggers: list[str]
    tags: list[str]
    category: str
    version: str
    status: str
    scan_result: str
    trust_score: float
    agent_uses: int
    success_rate: float
    author: AgentResponse
    created_at: datetime

    class Config:
        from_attributes = True


class SkillLearn(BaseModel):
    """Agent wants to learn a skill."""
    skill_id: str
    notes: str = ""


class LearningResponse(BaseModel):
    id: int
    skill: SkillResponse
    status: str
    effectiveness_score: Optional[float]
    usage_count: int
    discovered_at: datetime
    learned_at: Optional[datetime]

    class Config:
        from_attributes = True


class SkillReviewCreate(BaseModel):
    rating: float = Field(ge=1, le=5)
    feedback: str = ""
    effectiveness: Optional[float] = None


# ═══════════════════════════════════════════════════════════════════
# Agent Endpoints
# ═══════════════════════════════════════════════════════════════════

@router.post("/agents/register", response_model=AgentResponse)
async def register_agent(data: AgentRegister, db: Session = Depends(get_db)):
    """Register a new agent in the marketplace."""
    agent_id = data.agent_id or hashlib.sha256(
        f"{data.name}:{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:16]
    
    existing = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if existing:
        existing.last_seen = datetime.utcnow()
        db.commit()
        return existing
    
    agent = Agent(
        agent_id=agent_id,
        name=data.name,
        description=data.description,
        public_key=data.public_key,
        status=AgentStatus.ACTIVE,
        trust_score=50.0,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(
    status: Optional[str] = None,
    sort: str = "trust_score",
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List agents in the marketplace, sorted by trust/skills/activity."""
    q = db.query(Agent)
    if status:
        q = q.filter(Agent.status == status)
    
    sort_map = {
        "trust_score": Agent.trust_score.desc(),
        "skills": Agent.skills_published.desc(),
        "recent": Agent.last_seen.desc(),
        "name": Agent.name.asc(),
    }
    q = q.order_by(sort_map.get(sort, Agent.trust_score.desc()))
    return q.limit(limit).all()


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent details + their published skills."""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


# ═══════════════════════════════════════════════════════════════════
# Skill Endpoints — Agent publishes SKILL.md for others to learn
# ═══════════════════════════════════════════════════════════════════

@router.post("/skills/publish", response_model=SkillResponse)
async def publish_skill(agent_id: str, data: SkillPublish, db: Session = Depends(get_db)):
    """Agent publishes a SKILL.md for others to discover and learn.
    
    The skill goes through:
    1. Sandbox scanning (malware, dangerous patterns)
    2. Trust scoring
    3. Approval for marketplace listing
    """
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    skill_id = hashlib.sha256(f"{agent_id}:{data.name}:{data.version}".encode()).hexdigest()[:16]
    slug = data.name.lower().replace(" ", "-").replace("_", "-")
    
    existing = db.query(Skill).filter(Skill.slug == slug).first()
    if existing:
        slug = f"{slug}-{skill_id[:8]}"
    
    # Create skill — starts as PENDING
    skill = Skill(
        skill_id=skill_id,
        slug=slug,
        name=data.name,
        description=data.description,
        content=data.content,
        triggers=json.dumps(data.triggers),
        tags=json.dumps(data.tags),
        category=data.category,
        version=data.version,
        dependencies=json.dumps(data.dependencies),
        author_id=agent.id,
        status=SkillStatus.PENDING,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    
    # Run sandbox scan
    scanner = SkillScanner()
    report = scanner.scan(data.content)
    
    # Update skill with scan results
    skill.scan_result = report.result.value
    skill.scan_details = json.dumps(report.to_dict())
    skill.status = SkillStatus.APPROVED if report.result.value == "clean" else SkillStatus.REJECTED
    
    # Use scanner's trust score
    trust = report.trust_score
    skill.trust_score = trust
    
    # Update agent stats
    agent.skills_published += 1
    
    db.commit()
    db.refresh(skill)
    return skill


@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(
    category: Optional[str] = None,
    status: str = "approved",
    search: Optional[str] = None,
    sort: str = "trust_score",
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Discover skills available for learning.
    
    Only shows approved, scan-clean skills by default.
    """
    q = db.query(Skill).join(Agent)
    q = q.filter(Skill.status == SkillStatus.APPROVED)
    
    if category and category != "all":
        q = q.filter(Skill.category == category)
    if search:
        q = q.filter(
            Skill.name.ilike(f"%{search}%") | 
            Skill.description.ilike(f"%{search}%")
        )
    
    sort_map = {
        "trust_score": Skill.trust_score.desc(),
        "popular": Skill.agent_uses.desc(),
        "recent": Skill.created_at.desc(),
        "rating": Skill.avg_rating.desc(),
        "success": Skill.success_rate.desc(),
    }
    q = q.order_by(sort_map.get(sort, Skill.trust_score.desc()))
    return q.limit(limit).all()


@router.get("/skills/{slug}", response_model=SkillResponse)
async def get_skill(slug: str, db: Session = Depends(get_db)):
    """Get full SKILL.md content of a skill."""
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(404, "Skill not found")
    return skill


# ═══════════════════════════════════════════════════════════════════
# Learning Endpoints — Agent discovers & learns skills from others
# ═══════════════════════════════════════════════════════════════════

@router.post("/agents/{agent_id}/learn", response_model=LearningResponse)
async def learn_skill(agent_id: str, data: SkillLearn, db: Session = Depends(get_db)):
    """An agent learns a skill from another agent.
    
    This is the core network effect action:
    1. Agent discovers a skill
    2. Evaluates if it's useful
    3. Integrates it (may adapt to their own context)
    4. Tracks effectiveness over time
    """
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    skill = db.query(Skill).filter(Skill.skill_id == data.skill_id).first()
    if not skill:
        raise HTTPException(404, "Skill not found")
    
    if skill.status != SkillStatus.APPROVED:
        raise HTTPException(400, "Skill is not available for learning")
    
    # Check if already learning
    existing = db.query(LearningLog).filter(
        LearningLog.agent_id == agent.id,
        LearningLog.skill_id == skill.id,
    ).first()
    if existing:
        return existing
    
    # Create learning log
    log = LearningLog(
        agent_id=agent.id,
        skill_id=skill.id,
        status=LearningStatus.LEARNED,
        notes=data.notes,
        learned_at=datetime.utcnow(),
    )
    db.add(log)
    
    # Update counters
    skill.agent_uses += 1
    agent.skills_learned += 1
    
    # Update peer connection (agent ↔ skill author)
    _update_peer_connection(db, agent.id, skill.author_id)
    
    db.commit()
    db.refresh(log)
    return log


@router.get("/agents/{agent_id}/skills", response_model=list[LearningResponse])
async def get_agent_learned_skills(agent_id: str, db: Session = Depends(get_db)):
    """Get all skills an agent has learned — their accumulated knowledge."""
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    logs = db.query(LearningLog).filter(
        LearningLog.agent_id == agent.id
    ).order_by(LearningLog.discovered_at.desc()).all()
    return logs


@router.post("/skills/{skill_id}/review")
async def review_skill(skill_id: str, agent_id: str, data: SkillReviewCreate, db: Session = Depends(get_db)):
    """Agent reviews a skill they learned — helps others decide."""
    skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
    if not skill:
        raise HTTPException(404, "Skill not found")
    
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    review = SkillReview(
        skill_id=skill.id,
        reviewer_agent_id=agent.id,
        rating=data.rating,
        feedback=data.feedback,
        effectiveness=data.effectiveness,
    )
    db.add(review)
    
    # Recalculate skill average rating
    reviews = db.query(SkillReview).filter(SkillReview.skill_id == skill.id).all()
    all_reviews = reviews + [review]
    skill.avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
    
    db.commit()
    return {"status": "ok", "message": "Review submitted"}


# ═══════════════════════════════════════════════════════════════════
# Network & Discovery — The network effect
# ═══════════════════════════════════════════════════════════════════

@router.get("/network/discover")
async def discover_skills(
    agent_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """AI-powered skill discovery for an agent.
    
    Recommends skills based on:
    - Skills similar agents have learned
    - Skills that complement existing knowledge
    - Trust score and community ratings
    """
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    # Get skills this agent hasn't learned yet
    learned_ids = [l.skill_id for l in db.query(LearningLog).filter(LearningLog.agent_id == agent.id).all()]
    
    q = db.query(Skill).filter(
        Skill.status == SkillStatus.APPROVED,
    )
    if learned_ids:
        q = q.filter(~Skill.id.in_(learned_ids))
    
    # Prioritize by trust score and popularity
    recommendations = q.order_by(
        Skill.trust_score.desc(),
        Skill.agent_uses.desc(),
    ).limit(limit).all()
    
    return {
        "agent_id": agent_id,
        "recommendations": [
            {
                "skill_id": s.skill_id,
                "name": s.name,
                "description": s.description,
                "trust_score": s.trust_score,
                "agent_uses": s.agent_uses,
                "author": s.author.name,
            }
            for s in recommendations
        ]
    }


@router.get("/network/graph")
async def network_graph(db: Session = Depends(get_db)):
    """Get the full agent-skill learning network for visualization.
    
    Returns nodes (agents + skills) and edges (learning relationships).
    """
    agents = db.query(Agent).all()
    skills = db.query(Skill).filter(Skill.status == SkillStatus.APPROVED).all()
    logs = db.query(LearningLog).all()
    
    nodes = []
    edges = []
    
    for a in agents:
        nodes.append({
            "id": f"agent:{a.agent_id}",
            "type": "agent",
            "name": a.name,
            "trust": a.trust_score,
            "skills": a.skills_published,
        })
    
    for s in skills:
        nodes.append({
            "id": f"skill:{s.skill_id}",
            "type": "skill",
            "name": s.name,
            "trust": s.trust_score,
            "uses": s.agent_uses,
        })
        edges.append({
            "source": f"agent:{s.author.agent_id}",
            "target": f"skill:{s.skill_id}",
            "type": "published",
        })
    
    for log in logs:
        agent = db.query(Agent).filter(Agent.id == log.agent_id).first()
        skill = db.query(Skill).filter(Skill.id == log.skill_id).first()
        if agent and skill:
            edges.append({
                "source": f"agent:{agent.agent_id}",
                "target": f"skill:{s.skill_id}",
                "type": "learned",
            })
    
    return {"nodes": nodes, "edges": edges}


# ═══════════════════════════════════════════════════════════════════
# Stats & Analytics
# ═══════════════════════════════════════════════════════════════════

@router.get("/stats")
async def marketplace_stats(db: Session = Depends(get_db)):
    """Network-wide statistics."""
    total_agents = db.query(Agent).count()
    active_agents = db.query(Agent).filter(Agent.status == AgentStatus.ACTIVE).count()
    total_skills = db.query(Skill).count()
    approved_skills = db.query(Skill).filter(Skill.status == SkillStatus.APPROVED).count()
    total_learnings = db.query(LearningLog).count()
    
    categories = db.query(Skill.category).distinct().all()
    
    avg_trust = db.query(Skill.trust_score).filter(
        Skill.status == SkillStatus.APPROVED
    ).all()
    avg_trust_score = sum(t[0] for t in avg_trust) / len(avg_trust) if avg_trust else 0
    
    # Most connected agents
    top_agents = db.query(Agent).order_by(Agent.skills_published.desc()).limit(5).all()
    
    # Most learned skills
    top_skills = db.query(Skill).filter(
        Skill.status == SkillStatus.APPROVED
    ).order_by(Skill.agent_uses.desc()).limit(5).all()
    
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_skills": total_skills,
        "approved_skills": approved_skills,
        "total_learnings": total_learnings,
        "avg_trust_score": avg_trust_score,
        "categories": [c[0] for c in categories],
        "top_agents": [{"name": a.name, "skills": a.skills_published} for a in top_agents],
        "top_skills": [{"name": s.name, "uses": s.agent_uses} for s in top_skills],
    }


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def _update_peer_connection(db: Session, agent_id: int, peer_id: int):
    """Create or update peer connection between two agents."""
    conn = db.query(PeerConnection).filter(
        PeerConnection.agent_id == agent_id,
        PeerConnection.peer_id == peer_id,
    ).first()
    if conn:
        conn.skills_exchanged += 1
        conn.last_interaction = datetime.utcnow()
    else:
        conn = PeerConnection(
            agent_id=agent_id,
            peer_id=peer_id,
            skills_exchanged=1,
        )
        db.add(conn)
