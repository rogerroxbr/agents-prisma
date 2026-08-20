"""SQLAlchemy ORM models for PRISMA pipeline data."""

import os
from datetime import datetime
from urllib.parse import quote_plus

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import JSON as SQLiteJSON


def get_database_url() -> str:
    """Build database connection URL from environment variables."""
    USE_SQLITE = os.getenv("USE_SQLITE", "").lower() == "true"

    if USE_SQLITE:
        return "sqlite:///./prisma_test.db"
    else:
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = int(os.getenv("DB_PORT", "5432"))
        DB_NAME = os.getenv("DB_NAME", "prisma_dev")
        DB_USER = os.getenv("DB_USER", "postgres_user")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "secure_password_123")

        return f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Para SQLite, usamos JSON em vez de JSONB
JSON = SQLiteJSON if "sqlite" in get_database_url().lower() else JSONB

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
    progress = Column(Float, default=0)
    artifacts = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class Article(Base):
    """Individual article tracked through the PRISMA funnel."""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    phase_id = Column(Integer, ForeignKey("phases.id"), nullable=False)
    doi = Column(String(255), unique=True, index=True)
    title = Column(Text, nullable=False)
    authors = Column(JSON, default=list)
    abstract = Column(Text, default="")
    article_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class PipelineState(Base):
    """Centralized pipeline state for PRISMA workflow."""

    __tablename__ = "pipeline_state"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    phase = Column(String(50), nullable=False)
    progress = Column(Float, default=0)
    articles_processed = Column(Integer, default=0)
    total_target = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScreeningResult(Base):
    """Screening agent results (title/abstract filtering)."""

    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    score = Column(Float)
    decision = Column(String(20), default="pending")
    justification = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ArticleData(Base):
    """Structured data extracted from full article (Deep Reader Agent)."""

    __tablename__ = "article_data"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)

    population = Column(JSON)
    intervention = Column(JSON)
    comparison = Column(JSON)
    outcomes = Column(JSON)

    extracted_by_agent = Column(String(100), default="deep_reader")
    extraction_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class SynthesisOutput(Base):
    """Final outputs for Obsidian (Synthesizer Agent)."""

    __tablename__ = "synthesis_outputs"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    output_type = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class LangGraphCheckpoint(Base):
    """LangGraph checkpoint for fault-tolerant execution."""

    __tablename__ = "langgraph_checkpoints"

    id = Column(Integer, primary_key=True)
    config = Column(JSONB, default=lambda: {"thread_id": "main"})
    parent_id = Column(Integer, ForeignKey("langgraph_checkpoints.id"))
    state = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LangGraphConversation(Base):
    """LLM conversation history per phase."""

    __tablename__ = "langgraph_conversations"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    phase = Column(String(50))
    node_name = Column(String(100))
    messages = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
