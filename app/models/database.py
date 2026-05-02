"""Database setup — supports SQLite (local) and PostgreSQL (Railway/production)."""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError

from app.models.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentself.db")

# Railway PostgreSQL sometimes uses postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🔧 DATABASE_URL raw: {DATABASE_URL[:30]}..." if len(DATABASE_URL) > 30 else f"🔧 DATABASE_URL raw: {DATABASE_URL}")

# Try PostgreSQL first, fallback to SQLite
if DATABASE_URL.startswith("postgresql://"):
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False,
            connect_args={"connect_timeout": 5},
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to PostgreSQL")
    except OperationalError as e:
        print(f"⚠️ PostgreSQL connection failed: {e}")
        print("⚠️ Falling back to SQLite")
        DATABASE_URL = "sqlite:///./agentself.db"
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False,
        )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    print("✅ Using SQLite")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        db_type = "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite"
        print(f"✅ Database initialized: {db_type}")
    except Exception as e:
        print(f"❌ Database init failed: {e}")
        raise


def get_db() -> Session:
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
