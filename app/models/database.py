"""Database setup — supports SQLite (local) and PostgreSQL (Railway/production)."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.models import Base

# PostgreSQL (Railway) or SQLite (local)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentself.db")

# Railway PostgreSQL sometimes uses postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs special args, PostgreSQL uses connection pool
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {'PostgreSQL' if 'postgresql' in DATABASE_URL else 'SQLite'}")


def get_db() -> Session:
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
