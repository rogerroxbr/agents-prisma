"""SQLAlchemy ORM models for PRISMA pipeline data."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import os
from urllib.parse import quote_plus

def get_database_url():
    """Build PostgreSQL connection URL from environment variables."""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME", "prisma_dev")
    DB_USER = os.getenv("DB_USER", "postgres_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "secure_password_123")
    
    return f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

from sqlalchemy.orm import declarative_base
Base = declarative_base()

class Project(Base):
    """Top-level project representing a systematic review."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Phase(Base):
    """PRISMA phase tracking (Identification, Screening, etc.)."""
    __tablename__ = "phases"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    phase_name = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Article(Base):
    """Individual article tracked through the PRISMA funnel."""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True)
    phase_id = Column(Integer, ForeignKey("phases.id"), nullable=False)
    doi = Column(String(255), unique=True, index=True)
    title = Column(Text, nullable=False)
    authors = Column(JSONB, default=list)
    abstract = Column(Text, default="")
    article_metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)