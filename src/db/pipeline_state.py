"SQLAlchemy ORM models for PRISMA pipeline state."

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Models específicos da pipeline PRISMA (Fase 1.2+)"
class PipelineState(Base):
    """Centralized pipeline state for PRISMA workflow."""

    __tablename__ = "pipeline_state"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    phase = Column(String(50), nullable=False)  # identification, screening, etc.
    progress = Column(Integer, default=0)  # 0-100% per phase
    articles_processed = Column(Integer, default=0)
    total_target = Column(Integer, default=100)  # Target number of articles
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScreeningResult(Base):
    """Screening agent results (title/abstract filtering)."""

    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    score = Column(Float)  # Relevance score (0-100)
    decision = Column(String(20), default="pending")  # include/exclude/pending
    justification = Column(Text)  # Reason for the decision
    created_at = Column(DateTime, default=datetime.utcnow)


class ArticleData(Base):
    """Structured data extracted from full article (Deep Reader Agent)."""

    __tablename__ = "article_data"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)

    # PRISMA PICO framework
    population = Column(JSONB)  # Demographics, inclusion criteria
    intervention = Column(JSONB)  # Type, dose, duration
    comparison = Column(JSONB)  # Control, placebos
    outcomes = Column(JSONB)  # Primary and secondary

    # Extraction metadata
    extracted_by_agent = Column(String(100), default="deep_reader")
    extraction_confidence = Column(Float)  # LLM confidence (0-1)
    created_at = Column(DateTime, default=datetime.utcnow)


class SynthesisOutput(Base):
    """Final outputs for Obsidian (Synthesizer Agent)."""

    __tablename__ = "synthesis_outputs"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    output_type = Column(String(50))  # markdown_table/mermaid_flowchart/json_backup
    content = Column(Text)  # Formatted content
    created_at = Column(DateTime, default=datetime.utcnow)
