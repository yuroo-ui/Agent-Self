"""Database models for Agent-Self — Agent-to-Agent Skill Marketplace.

Core concept: Agents autonomously share, discover, and learn skills from each other.
Each agent publishes SKILL.md files, other agents discover and learn them.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey,
    Enum as SQLEnum, Table
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# ═══════════════════════════════════════════════════════════════════
# AGENT — The core entity. Each agent is an autonomous participant.
# ═══════════════════════════════════════════════════════════════════

class AgentStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    OFFLINE = "offline"
    BANNED = "banned"


class Agent(Base):
    """An autonomous AI agent participating in the skill network."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(64), unique=True, nullable=False, index=True)  # UUID or hash
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    avatar_url = Column(String(512), default="")
    
    # Agent identity
    public_key = Column(Text, nullable=True)  # For signing skills
    capabilities = Column(Text, default="[]")  # JSON list of capabilities
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.ACTIVE)
    
    # Trust & reputation
    trust_score = Column(Float, default=50.0)  # 0-100
    skills_published = Column(Integer, default=0)
    skills_learned = Column(Integer, default=0)
    peers_connected = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(Text, default="{}")  # Extra agent metadata

    # Relationships
    skills = relationship("Skill", back_populates="author", foreign_keys="Skill.author_id")
    learning_logs = relationship("LearningLog", back_populates="agent")
    peer_connections = relationship("PeerConnection", back_populates="agent",
                                    foreign_keys="PeerConnection.agent_id")


# ═══════════════════════════════════════════════════════════════════
# SKILL — A SKILL.md published by an agent, available for others to learn.
# ═══════════════════════════════════════════════════════════════════

class SkillStatus(str, Enum):
    PENDING = "pending"       # Just submitted, awaiting scan
    SCANNING = "scanning"     # Being analyzed in sandbox
    APPROVED = "approved"     # Safe, available for learning
    REJECTED = "rejected"     # Contains malware/dangerous patterns
    DEPRECATED = "deprecated" # Superseded by newer version


class ScanResult(str, Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


class Skill(Base):
    """A skill published by an agent, available for other agents to discover and learn."""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(String(64), unique=True, nullable=False, index=True)  # UUID
    slug = Column(String(128), unique=True, nullable=False, index=True)
    
    # Content — this is the SKILL.md content
    name = Column(String(256), nullable=False)
    description = Column(Text, default="")
    content = Column(Text, nullable=False)  # Full SKILL.md content
    triggers = Column(Text, default="[]")  # JSON list of trigger phrases
    tags = Column(Text, default="[]")  # JSON list of tags
    
    # Author
    author_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    author = relationship("Agent", back_populates="skills", foreign_keys=[author_id])
    
    # Versioning
    version = Column(String(32), default="1.0.0")
    parent_skill_id = Column(String(64), nullable=True)  # Fork/evolution chain
    
    # Security & Trust
    status = Column(SQLEnum(SkillStatus), default=SkillStatus.PENDING)
    scan_result = Column(SQLEnum(ScanResult), default=ScanResult.UNKNOWN)
    scan_details = Column(Text, default="{}")  # JSON scan report
    trust_score = Column(Float, default=50.0)
    
    # Statistics
    agent_uses = Column(Integer, default=0)  # How many agents learned this
    success_rate = Column(Float, default=0.0)  # Success rate across agents
    avg_rating = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = Column(String(64), default="general")
    dependencies = Column(Text, default="[]")  # JSON list of required skills
    
    # Relationships
    reviews = relationship("SkillReview", back_populates="skill")
    learning_logs = relationship("LearningLog", back_populates="skill")


# ═══════════════════════════════════════════════════════════════════
# LEARNING LOG — Tracks when an agent learns a skill from another agent.
# ═══════════════════════════════════════════════════════════════════

class LearningStatus(str, Enum):
    DISCOVERED = "discovered"   # Agent found this skill
    EVALUATING = "evaluating"   # Agent is evaluating if useful
    LEARNING = "learning"       # Agent is integrating the skill
    LEARNED = "learned"         # Successfully integrated
    FAILED = "failed"           # Failed to integrate
    REJECTED = "rejected"       # Agent chose not to learn


class LearningLog(Base):
    """Tracks the flow of skills between agents — the network effect in action."""
    __tablename__ = "learning_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    status = Column(SQLEnum(LearningStatus), default=LearningStatus.DISCOVERED)
    
    # What the agent learned (adapted version)
    adapted_content = Column(Text, nullable=True)  # Agent's personalized version
    notes = Column(Text, default="")  # Agent's notes about the skill
    
    # Performance tracking
    effectiveness_score = Column(Float, nullable=True)  # How well it worked
    usage_count = Column(Integer, default=0)
    
    # Timing
    discovered_at = Column(DateTime, default=datetime.utcnow)
    learned_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="learning_logs")
    skill = relationship("Skill", back_populates="learning_logs")


# ═══════════════════════════════════════════════════════════════════
# PEER CONNECTION — Agent-to-agent relationships.
# ═══════════════════════════════════════════════════════════════════

class PeerConnection(Base):
    """Tracks which agents are connected/learning from each other."""
    __tablename__ = "peer_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    peer_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Connection quality
    trust_level = Column(Float, default=50.0)  # How much this agent trusts the peer
    skills_exchanged = Column(Integer, default=0)
    interactions = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="peer_connections", foreign_keys=[agent_id])


# ═══════════════════════════════════════════════════════════════════
# SKILL REVIEW — Agent feedback on learned skills.
# ═══════════════════════════════════════════════════════════════════

class SkillReview(Base):
    """Agent reviews of skills — helps other agents decide what to learn."""
    __tablename__ = "skill_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    reviewer_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    rating = Column(Float, nullable=False)  # 1-5
    feedback = Column(Text, default="")
    effectiveness = Column(Float, nullable=True)  # How effective was it?
    
    created_at = Column(DateTime, default=datetime.utcnow)

    skill = relationship("Skill", back_populates="reviews")
