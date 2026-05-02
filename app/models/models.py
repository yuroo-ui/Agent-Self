"""Database models for Agent-Self marketplace."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Float, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SkillStatus(str, Enum):
    PENDING = "pending"
    SCANNING = "scanning"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class ScanResult(str, Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class User(Base):
    """Skill developer / agent user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, index=True)
    
    # Trust
    reputation_score = Column(Float, default=0.0)
    total_skills = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    skills = relationship("Skill", back_populates="author")
    reviews = relationship("Review", back_populates="reviewer")


class Skill(Base):
    """A skill that can be used by AI agents."""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(20), default="1.0.0")
    
    # Author
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="skills")
    
    # Content
    code = Column(Text, nullable=False)  # The actual skill code
    manifest = Column(JSON)  # skill.yaml parsed as JSON
    dependencies = Column(JSON, default=list)
    
    # Security & Trust
    status = Column(SQLEnum(SkillStatus), default=SkillStatus.PENDING)
    trust_score = Column(Float, default=0.0)
    scan_result = Column(SQLEnum(ScanResult))
    scan_details = Column(JSON)
    
    # Stats
    download_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    fork_count = Column(Integer, default=0)
    
    # Fork tree
    parent_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    forks = relationship("Skill", backref="parent", remote_side=[id])
    
    # Metadata
    tags = Column(JSON, default=list)
    category = Column(String(50))
    license = Column(String(50), default="MIT")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Immutable hash (content-addressable)
    content_hash = Column(String(64), unique=True, index=True)
    
    # Relations
    reviews = relationship("Review", back_populates="skill")
    scan_logs = relationship("ScanLog", back_populates="skill")


class Review(Base):
    """User review of a skill."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    skill = relationship("Skill", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


class ScanLog(Base):
    """Security scan log for a skill."""
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    scan_type = Column(String(50))  # static, dynamic, network, permission
    result = Column(SQLEnum(ScanResult))
    details = Column(JSON)
    warnings = Column(JSON, default=list)
    errors = Column(JSON, default=list)
    
    scanned_at = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer)
    
    # Relations
    skill = relationship("Skill", back_populates="scan_logs")


class LearningEvent(Base):
    """Federated learning event (anonymized)."""
    __tablename__ = "learning_events"

    id = Column(Integer, primary_key=True, index=True)
    
    skill_id = Column(Integer, ForeignKey("skills.id"))
    event_type = Column(String(50))  # improvement, bugfix, pattern
    
    # Anonymized data only
    anonymous_data = Column(JSON)  # Gradients/patterns, NO user data
    source_hash = Column(String(64))  # Anonymized source identifier
    
    created_at = Column(DateTime, default=datetime.utcnow)
