import re
from datetime import UTC, datetime
from typing import Any, TypedDict

from pydantic import BaseModel, Field, field_validator

# ==================== PHASE-SPECIFIC STATES ====================


class IdentificationState(BaseModel):
    """Identification phase state - source-specific data"""

    # Source-specific metadata (parallel processing)
    sources: dict[str, list[dict[str, Any]]] = Field(
        default_factory=dict, description="PubMed/Scopus results with metadata"
    )

    total_found: int = 0

    # Processing state
    metadata_extracted: bool = False
    raw_response_processed: bool = False


class ScreeningState(BaseModel):
    """Screening phase state - batch processing"""

    batches_processed: int = 0
    articles_reviewed: list[int] = Field(default_factory=list)
    decisions: dict[int, Any] = Field(
        default_factory=dict
    )  # {article_id: {"decision": "include", "reason": "...", "pico": {...}}}

    # Interactive CLI state
    current_batch_size: int = 50
    pending_review_count: int = 0


class EligibilityState(BaseModel):
    """Eligibility phase state - deep reading"""

    pdfs_extracted: int = 0
    pico_data: list[dict[str, Any]] = Field(default_factory=list)

    # Deep Reader specific
    markdown_outputs: list[str] = Field(default_factory=list)
    extraction_confidence: float = 0.0


class SynthesisState(BaseModel):
    """Synthesis phase state - final outputs"""

    markdown_outputs: list[str] = Field(default_factory=list)
    flowchart_generated: bool = False

    # Obsidian/Markdown format options
    obsidian_format: bool = True
    json_backup: bool = True


# ==================== MAIN STATEGRAPH TYPEDDICT ====================


class PRISMAState(TypedDict, total=False):
    """Main StateGraph TypedDict with nested phase states."""

    # Nested phase-specific state objects
    identification: IdentificationState
    screening: ScreeningState
    eligibility: EligibilityState
    synthesis: SynthesisState

    # Global orchestrator state (flat)
    project_id: int
    query: str
    max_results: int
    date_range: tuple | None

    phase: str  # "identification" | "screening" | "eligibility" | "synthesis"
    progress: float  # 0.0 - 100.0, per-phase percentage
    articles_count: int

    # Execution metadata
    created_at: datetime
    last_updated: datetime


# ==================== PYDANTIC VALIDATION MODELS ====================


class ArticleMetadata(BaseModel):
    """Standardized article metadata across all sources."""

    doi: str | None = Field(None, description="Digital Object Identifier")
    title: str = Field(..., min_length=1)  # Required
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None

    source: str = Field(
        ...,
        pattern=r"^(pubmed|scopus|web_of_science|google_scholar)$",
        description="Source of the article",
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("doi")
    @classmethod
    def validate_doi(cls, v: str | None) -> str | None:
        """Validate DOI format (10.xxxx/xxxxx)."""
        if v and not re.match(r"^10\.\d{4,}\/\S+$", v):
            raise ValueError(f"Invalid DOI format: {v}")
        return v

    @field_validator("authors")
    @classmethod
    def validate_authors(cls, v: list[str]) -> list[str]:
        """Ensure authors list is non-empty if title exists."""
        if v and not any(a.strip() for a in v):
            raise ValueError("Authors must have at least one valid name")
        return v
