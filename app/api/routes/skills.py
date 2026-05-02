"""Skill marketplace API routes."""

import hashlib
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.database import get_db, init_db
from app.models.models import Skill, User, Review, SkillStatus, ScanResult as ScanResultEnum
from app.sandbox.scanner import SkillScanner, ScanResult
from app.services.trust import TrustEngine

router = APIRouter(prefix="/api/v1", tags=["skills"])
scanner = SkillScanner()
trust_engine = TrustEngine()


# === Schemas ===

class SkillSubmit(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    code: str = Field(..., min_length=10)
    category: str = "general"
    tags: list[str] = []
    license: str = "MIT"
    manifest: Optional[dict] = None


class SkillResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    version: str
    category: str
    tags: list[str]
    trust_score: float
    status: str
    download_count: int
    usage_count: int
    created_at: str
    published_at: Optional[str]
    scan_result: Optional[str]
    
    class Config:
        from_attributes = True


class SkillDetail(SkillResponse):
    code: str
    manifest: Optional[dict]
    dependencies: list[str]
    scan_details: Optional[dict]
    author: dict


class ReviewSubmit(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ScanResponse(BaseModel):
    result: str
    trust_score: float
    findings: list[dict]
    permissions: list[str]
    content_hash: str


# === Helpers ===

def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:100]


def generate_api_key() -> str:
    """Generate a random API key."""
    import secrets
    return f"as_{secrets.token_hex(32)}"


# === Endpoints ===

@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(
    category: Optional[str] = None,
    search: Optional[str] = None,
    status: str = "approved",
    sort: str = "trust_score",
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List approved skills with filtering."""
    query = db.query(Skill).filter(Skill.status == status)
    
    if category:
        query = query.filter(Skill.category == category)
    
    if search:
        query = query.filter(
            Skill.name.ilike(f"%{search}%") | 
            Skill.description.ilike(f"%{search}%")
        )
    
    # Sorting
    if sort == "trust_score":
        query = query.order_by(Skill.trust_score.desc())
    elif sort == "downloads":
        query = query.order_by(Skill.download_count.desc())
    elif sort == "recent":
        query = query.order_by(Skill.published_at.desc())
    
    skills = query.offset(offset).limit(limit).all()
    
    return [
        SkillResponse(
            id=s.id,
            slug=s.slug,
            name=s.name,
            description=s.description or "",
            version=s.version or "1.0.0",
            category=s.category or "general",
            tags=s.tags or [],
            trust_score=s.trust_score or 0,
            status=s.status.value if s.status else "pending",
            download_count=s.download_count or 0,
            usage_count=s.usage_count or 0,
            created_at=s.created_at.isoformat() if s.created_at else "",
            published_at=s.published_at.isoformat() if s.published_at else None,
            scan_result=s.scan_result.value if s.scan_result else None,
        )
        for s in skills
    ]


@router.get("/skills/{slug}", response_model=SkillDetail)
async def get_skill(slug: str, db: Session = Depends(get_db)):
    """Get skill details."""
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    author = db.query(User).filter(User.id == skill.author_id).first()
    
    return SkillDetail(
        id=skill.id,
        slug=skill.slug,
        name=skill.name,
        description=skill.description or "",
        version=skill.version or "1.0.0",
        category=skill.category or "general",
        tags=skill.tags or [],
        trust_score=skill.trust_score or 0,
        status=skill.status.value if skill.status else "pending",
        download_count=skill.download_count or 0,
        usage_count=skill.usage_count or 0,
        created_at=skill.created_at.isoformat() if skill.created_at else "",
        published_at=skill.published_at.isoformat() if skill.published_at else None,
        scan_result=skill.scan_result.value if skill.scan_result else None,
        code=skill.code or "",
        manifest=skill.manifest,
        dependencies=skill.dependencies or [],
        scan_details=skill.scan_details,
        author={
            "id": author.id if author else 0,
            "username": author.username if author else "unknown",
            "reputation": author.reputation_score if author else 0,
            "verified": author.verified if author else False,
        }
    )


@router.post("/skills", response_model=SkillResponse)
async def submit_skill(
    skill_data: SkillSubmit,
    db: Session = Depends(get_db),
):
    """Submit a new skill for review."""
    init_db()
    
    # Generate slug
    slug = slugify(skill_data.name)
    existing = db.query(Skill).filter(Skill.slug == slug).first()
    if existing:
        slug = f"{slug}-{hashlib.md5(skill_data.code.encode()).hexdigest()[:6]}"
    
    # Content hash (immutable identifier)
    content = json.dumps({
        "name": skill_data.name,
        "code": skill_data.code,
        "version": "1.0.0",
    }, sort_keys=True)
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Check for duplicate
    existing_hash = db.query(Skill).filter(Skill.content_hash == content_hash).first()
    if existing_hash:
        raise HTTPException(status_code=409, detail="This skill version already exists")
    
    # Get or create default user
    user = db.query(User).first()
    if not user:
        user = User(
            username="anonymous",
            email="anon@agentself.dev",
            hashed_password="none",
            api_key=generate_api_key(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create skill
    skill = Skill(
        slug=slug,
        name=skill_data.name,
        description=skill_data.description,
        code=skill_data.code,
        category=skill_data.category,
        tags=skill_data.tags,
        license=skill_data.license,
        manifest=skill_data.manifest or {},
        dependencies=skill_data.manifest.get("dependencies", []) if skill_data.manifest else [],
        author_id=user.id,
        status=SkillStatus.SCANNING,
        content_hash=content_hash,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    
    # Run security scan
    scan_report = scanner.scan(skill_data.code, skill_data.manifest)
    
    # Update skill with scan results
    skill.scan_result = ScanResultEnum(scan_report.result.value)
    skill.scan_details = scan_report.to_dict()
    skill.trust_score = scan_report.trust_score
    
    # Calculate full trust score
    skill.trust_score = trust_engine.calculate_skill_trust_score(
        security_scan_result=scan_report.result.value,
        security_trust_score=scan_report.trust_score,
        avg_rating=0,
        review_count=0,
        download_count=0,
        usage_count=0,
        author_reputation=user.reputation_score,
        days_since_update=0,
    )
    
    # Set status based on scan
    if scan_report.result == ScanResult.MALICIOUS:
        skill.status = SkillStatus.REJECTED
    elif scan_report.result == ScanResult.SUSPICIOUS:
        skill.status = SkillStatus.PENDING  # Needs manual review
    else:
        skill.status = SkillStatus.APPROVED
        skill.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(skill)
    
    return SkillResponse(
        id=skill.id,
        slug=skill.slug,
        name=skill.name,
        description=skill.description or "",
        version=skill.version or "1.0.0",
        category=skill.category or "general",
        tags=skill.tags or [],
        trust_score=skill.trust_score or 0,
        status=skill.status.value,
        download_count=0,
        usage_count=0,
        created_at=skill.created_at.isoformat(),
        published_at=skill.published_at.isoformat() if skill.published_at else None,
        scan_result=skill.scan_result.value if skill.scan_result else None,
    )


@router.post("/skills/{slug}/scan", response_model=ScanResponse)
async def scan_skill(slug: str, db: Session = Depends(get_db)):
    """Re-scan a skill for security."""
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    report = scanner.scan(skill.code, skill.manifest)
    
    return ScanResponse(
        result=report.result.value,
        trust_score=report.trust_score,
        findings=report.to_dict()["findings"],
        permissions=report.permissions,
        content_hash=report.content_hash,
    )


@router.post("/skills/{slug}/reviews")
async def add_review(
    slug: str,
    review_data: ReviewSubmit,
    db: Session = Depends(get_db),
):
    """Add a review to a skill."""
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Get or create user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="No users found")
    
    review = Review(
        skill_id=skill.id,
        reviewer_id=user.id,
        rating=review_data.rating,
        comment=review_data.comment,
    )
    db.add(review)
    
    # Update skill stats
    skill.usage_count = (skill.usage_count or 0) + 1
    
    db.commit()
    
    return {"status": "ok", "message": "Review added"}


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get marketplace statistics."""
    init_db()
    
    total_skills = db.query(Skill).count()
    approved_skills = db.query(Skill).filter(Skill.status == SkillStatus.APPROVED).count()
    total_users = db.query(User).count()
    
    return {
        "total_skills": total_skills,
        "approved_skills": approved_skills,
        "total_users": total_users,
        "categories": [
            "general", "coding", "data", "web", "automation",
            "writing", "analysis", "integration", "testing"
        ],
    }
