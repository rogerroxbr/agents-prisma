# 🧬 LangGraph Migration Design Spec

**Date:** 2026-07-05  
**Version:** 1.0  
**Project:** Agents-Prisma Multi-Agent System  
**Migration:** CrewAI → LangChain/LangGraph (Full Rewrite)

---

## 📋 Executive Summary

Migrate the existing **CrewAI-based PRISMA pipeline** to a **LangGraph + LangChain hybrid architecture**. All 3 agents will be rewritten from scratch using `langgraph` and `langchain-core`, with PostgreSQL-backed state persistence, async I/O, and full ecosystem integration.

### Key Decisions (Approved)

| Category | Decision |
|----------|----------|
| **Scope** | Total rewrite - all 3 agents (Orchestrator, Searcher, Screener) |
| **DB State** | Keep existing tables (`projects`, `phases`, `articles`) + adapt for LangGraph |
| **State Approach** | Hybrid: LangGraph internal state + PostgreSQL persistence |
| **Migration Strategy** | Reescrever do zero - clean LangGraph implementation |
| **Components** | LangGraph StateGraph + Tool calling (Core + Tools) |
| **Agent Structure** | Single StateGraph with subgraphs for parallel sources |
| **DB Integration** | Async PostgreSQL + auto-checkpointing per phase |
| **MVP Level** | Completo - full LangChain ecosystem integration |
| **State Modeling** | TypedDict + Pydantic validation, nested by phase |
| **Parallel Execution** | LangGraph subgraphs (1 graph per source: PubMed/Scopus) |
| **Checkpointing** | Auto-checkpoint configured per node completion |
| **Testing** | Hybrid - unit tests + integration tests |
| **LLM Config** | LangChain ChatModels (Ollama/Anthropic standard interface) |
| **Tool Integration** | LangChain Tools interface for existing tools |
| **Migration Order** | Sequential: Orchestrator → Searcher → Screener |
| **Workflow Pattern** | Diamond Pattern + Loop-enabled (revisit failed phases) |
| **Memory/Context** | DB-backed - store context in PostgreSQL |
| **Error Handling** | Hybrid - retry + manual fallback paths |
| **Logging/Tracing** | Hybrid - LangGraph tracer + structured JSON logging |
| **Configuration** | `.env` + pydantic-settings (standard env vars) |
| **API/CLI Interface** | Hybrid - CLI (`python -m src.agents.main`) + FastAPI |
| **File Structure** | Full reorg to LangChain-style folders |

---

## 🏗️ Architecture Overview

### High-Level Diagram

```mermaid
graph TD
    subgraph "Main Orchestrator Graph"
        A[Start] --> B{Phase?}
        B -->|Identification| C[Identify Node]
        B -->|Screening| D[Screen Node]
        B -->|Eligibility| E[Read Node]
        B -->|Synthesis| F[Synthesize Node]
        
        C --> G{More Sources?}
        G -- Yes |PubMed/Scopus| H1[PubMed Subgraph]
        G -- Yes |Scopus| H2[Scopus Subgraph]
        H1 --> I1[Aggregate Results]
        H2 --> I2[Aggregate Results]
        I1 --> M{All Sources?}
        I2 --> M
        M -- Yes --> C
        M -- No --> D
        
        E --> F
        F --> End[End]
    end
    
    subgraph "PubMed Subgraph"
        H1 --> J1[Query PubMed Tool]
        J1 --> K1[Extract Metadata]
        K1 --> L1[Checkpoint State]
    end
    
    subgraph "Scopus Subgraph"
        H2 --> J2[Query Scopus Tool]
        J2 --> K2[Extract Metadata]
        K2 --> L2[Checkpoint State]
    end
```

### Core Components

| Component | Type | Responsibility |
|-----------|------|----------------|
| **MainStateGraph** | `StateGraph` | Orchestrates 4 PRISMA phases + parallel source processing |
| **PubMedSubgraph** | `StateGraph` | Parallel execution for PubMed source |
| **ScopusSubgraph** | `StateGraph` | Parallel execution for Scopus source |
| **AgentNodes** | Functions | Pure functions with controlled side effects (DB writes, LLM calls) |

---

## 🗄️ State Management

### TypedDict Schema (Nested by Phase)

```python
from typing import TypedDict, List, Any, Optional
from pydantic import BaseModel, Field

class IdentificationState(BaseModel):
    """Identification phase state"""
    sources: dict[str, list[dict]] = Field(default_factory=dict)  # {pubmed: [...], scopus: [...]}
    total_found: int = 0
    metadata_extracted: bool = False

class ScreeningState(BaseModel):
    """Screening phase state"""
    batches_processed: int = 0
    articles_reviewed: List[int] = Field(default_factory=list)
    decisions: dict[int, str] = Field(default_factory=dict)  # {article_id: "include/exclude"}

class EligibilityState(BaseModel):
    """Eligibility phase state"""
    pdfs_extracted: int = 0
    pico_data: List[dict] = Field(default_factory=list)

class SynthesisState(BaseModel):
    """Synthesis phase state"""
    markdown_outputs: List[str] = Field(default_factory=list)
    flowchart_generated: bool = False

# Main StateGraph TypedDict (Nested structure)
class PRISMAState(TypedDict):
    identification: IdentificationState
    screening: ScreeningState
    eligibility: EligibilityState
    synthesis: SynthesisState
    
    # Global state
    project_id: int
    phase: str  # "identification" | "screening" | "eligibility" | "synthesis"
    progress: float  # 0.0 - 100.0
    articles_count: int
```

### Pydantic Validation

```python
from pydantic import BaseModel, Field, field_validator

class ArticleMetadata(BaseModel):
    """Standardized article metadata across all sources"""
    doi: Optional[str] = None
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    source: str  # "pubmed" | "scopus" | ...
    created_at: datetime
    
    @field_validator('doi')
    def validate_doi(cls, v):
        if v and not re.match(r'^10\.\d{4,}\/\S+$', v):
            raise ValueError(f'Invalid DOI format: {v}')
        return v
```

---

## 🔄 Agent Structure (Single StateGraph + Subgraphs)

### Main Orchestrator Graph

**Nodes:** 6 total (4 phases + 2 parallel aggregators)

| Node | Function | Dependencies | DB Ops |
|------|----------|--------------|--------|
| `identify` | Initialize Identification phase | - | Create/Update `Phase` record |
| `pubmed_subgraph` | Execute PubMed subgraph | `IdentificationState` | Append to `articles` table |
| `scopus_subgraph` | Execute Scopus subgraph | `IdentificationState` | Append to `articles` table |
| `aggregate_results` | Merge parallel source results | Both subgraphs | Update `Phase.progress` |
| `screen` | Screening phase (title/abstract) | Aggregated results | Create `ScreeningResult` records |
| `finalize` | Complete pipeline + checkpoint | All phases | Final state save, create outputs |

**Edges:** Conditional routing based on:
- Source availability (PubMed/Scopus presence in state)
- Phase completion status
- Retry conditions (failed LLM calls, API errors)

### PubMed Subgraph

**Nodes:** 3 total

| Node | Function | DB Ops |
|------|----------|--------|
| `query_pubmed` | Call `pubmed_mcp.py` tool | - |
| `extract_metadata` | Parse response → `ArticleMetadata` | Insert into `articles` table |
| `checkpoint` | Save intermediate state | Update `pipeline_state.last_updated` |

### Scopus Subgraph (Mirror of PubMed)

**Nodes:** 3 total (parallel to PubMed subgraph)

---

## 🗃️ Database Integration (Async + Auto-Checkpointing)

### Async PostgreSQL Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Async engine configuration
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/prisma_dev"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### Auto-Checkpointing Strategy

**Per-node checkpointing:** Save state after each node completes successfully.

```python
from langgraph.checkpoint.sql import SQLNodeCheckpointSaver

# Configure auto-checkpoint per phase
checkpoint_saver = SQLNodeCheckpointSaver(
    engine=engine,
    table_name="langgraph_checkpoints",  # New table for LangGraph state
)

app = build_app(checkpointer=checkpoint_saver)
```

**Checkpoint Frequency:**
- **Phase nodes:** Save after completion (e.g., `identify` → checkpoint)
- **Subgraph nodes:** Save on exit from subgraph
- **Streaming writes:** Optional fine-grained saves for critical operations (e.g., article extraction)

### Database Schema (Minimal + Existing Tables)

**Existing tables (kept as-is):**
- `projects`, `phases`, `articles` → Core PRISMA data
- `screening_results`, `article_data`, `synthesis_outputs` → Phase-specific data

**New LangGraph table:**
```sql
CREATE TABLE langgraph_checkpoints (
    id SERIAL PRIMARY KEY,
    config JSONB NOT NULL,  -- Graph configuration
    parent_id INTEGER REFERENCES langgraph_checkpoints(id),
    state JSONB NOT NULL,   -- Full TypedDict state snapshot
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_checkpoint_state ON langgraph_checkpoints USING GIN (state);
```

---

## 🛠️ Tool Integration (LangChain Tools Interface)

### Existing Tools → LangChain Adaptation

**pubmed_tool.py / scopus_tool.py:** Already REST API wrappers. Wrap as LangChain Tools:

```python
from langchain.tools import tool

@tool("query_pubmed")
def query_pubmed(query: str, max_results: int = 50) -> dict:
    """Search PubMed for articles matching query."""
    results = pubmed_mcp_client.search(query, limit=max_results)
    return {
        "count": len(results),
        "articles": [
            {"doi": a.doi, "title": a.title, "authors": a.authors} 
            for a in results
        ]
    }

@tool("query_scopus")
def query_scopus(query: str, max_results: int = 50) -> dict:
    """Search Scopus for articles matching query."""
    results = scopus_mcp_client.search(query, limit=max_results)
    return {
        "count": len(results),
        "articles": [
            {"doi": a.doi, "title": a.title, "abstract": a.abstract} 
            for a in results
        ]
    }
```

**Integration:** Tools called via `AgentExecutor` within graph nodes.

---

## 🧠 Memory & Context (DB-Backed Persistence)

### Conversation History Storage

Store LLM conversation history in PostgreSQL:

```python
class ConversationHistory(BaseModel):
    """LLM context storage"""
    project_id: int
    phase: str
    node_name: str  # Track which node generated the response
    messages: List[dict]  # Full message history (user/assistant/tool)
    created_at: datetime
    
    @field_validator('messages')
    def validate_messages(cls, v):
        for msg in v:
            if 'role' not in msg or 'content' not in msg:
                raise ValueError("Each message must have 'role' and 'content'")
        return v
```

**Usage Pattern:**
1. Before LLM call → Load previous messages from DB
2. After LLM response → Append to conversation + save back to DB
3. Pass full history to next node via state

---

## ⚡ Error Handling (Hybrid Retry + Manual Fallback)

### Retry Logic (Per-Node)

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    reraise=True
)
async def call_llm_with_retry(llm, prompt: str) -> str:
    """LLM call with automatic retry + exponential backoff."""
    response = await llm.ainvoke(prompt)
    return response.content
```

### Manual Fallback Paths

**Error Types → Recovery Strategy:**

| Error Type | Automatic Retry? | Manual Fallback |
|------------|------------------|-----------------|
| `APIRateLimitError` | Yes (3x, exponential backoff) | Pause batch + notify user |
| `LLMConnectionError` | Yes (3x, linear backoff) | Switch to fallback LLM or manual review |
| `PDFExtractionError` | Yes (2x, immediate) | Fallback parser (pdfplumber) or skip article |
| `DataValidationError` | No | Log + route to "pending_review" state |

---

## 🧪 Testing Strategy (Hybrid Unit + Integration)

### Unit Tests (pytest)

**Coverage Target:** 80%+ for each node function.

```python
# tests/test_identify_node.py
import pytest
from src.langgraph.nodes.identify import identify_node

@pytest.mark.asyncio
async def test_identify_node_creates_phase_record():
    """Verify Phase record created in DB on phase start."""
    async with AsyncSessionLocal() as session:
        state = await identify_node(session, initial_state)
        
        # Check Phase was created
        phase = await session.get(Phase, 1)
        assert phase.status == "in_progress"
```

### Integration Tests (End-to-End)

**Test Scenarios:**

| Test | Description | Expected Result |
|------|-------------|-----------------|
| `test_full_pipeline_pubmed_only` | Run full flow with PubMed only | All 4 phases complete, results in DB |
| `test_parallel_sources_merge` | PubMed + Scopus parallel execution | Aggregated results match both sources |
| `test_retry_on_api_error` | Simulate rate limit error | Retry 3x, then fallback path triggered |
| `test_checkpoint_recovery` | Fail mid-phase, resume from checkpoint | Resume at correct state without reprocessing |

---

## 📁 File Structure (LangChain-Style Reorg)

### New Directory Layout

```
src/
├── agents/                    # LangGraph agent definitions
│   ├── __init__.py           # Exports: MainStateGraph, PubMedSubgraph, ScopusSubgraph
│   ├── main.py               # Entry point + CLI/FastAPI setup
│   │
│   └── orchestrator.py       # Main StateGraph implementation
│       ├── state.py          # TypedDict state schema definitions
│       ├── nodes/            # Pure function nodes (per phase)
│       │   ├── identify_node.py
│       │   ├── screen_node.py
│       │   ├── read_node.py
│       │   └── synthesize_node.py
│       └── subgraphs/        # Parallel source graphs
│           ├── pubmed_subgraph.py
│           └── scopus_subgraph.py
│
├── tools/                    # LangChain Tools interface (adapted from existing)
│   ├── __init__.py
│   ├── base_tool.py          # Abstract base class for all tools
│   ├── pubmed_tool_langchain.py  # Adapted pubmed_mcp + tool wrapper
│   └── scopus_tool_langchain.py  # Adapted scopus_mcp + tool wrapper
│
├── db/                       # Async PostgreSQL integration
│   ├── __init__.py
│   ├── async_session.py      # AsyncSession factory, context managers
│   ├── models.py             # Existing SQLAlchemy models (unchanged)
│   └── langgraph_checkpoint.py  # New: LangGraph checkpoint table + ops
│
├── llm/                      # LLM configuration & wrappers
│   ├── __init__.py
│   ├── base.py               # BaseLLM abstraction
│   ├── ollama_llm.py         # Local Ollama integration
│   └── anthropic_llm.py      # Cloud Anthropic (fallback)
│
├── config/                   # Configuration management
│   ├── __init__.py
│   ├── settings.py           # pydantic-settings + .env loading
│   └── langgraph_config.yaml # LangGraph-specific runtime config
│
├── api/                      # FastAPI integration (optional, for future)
│   ├── __init__.py
│   ├── app.py                # FastAPI app setup
│   └── routes/               # API endpoints
│       ├── pipeline.py       # POST /pipeline/run
│       └── state.py          # GET /state/{project_id}
│
├── cli/                      # CLI interface (existing)
│   └── main.py               # Existing `python -m src.agents.main` entry point
│
└── tests/                    # Test suite
    ├── unit/                 # Unit tests per node/function
    │   ├── test_identify_node.py
    │   ├── test_screen_node.py
    │   └── ...
    ├── integration/          # End-to-end workflow tests
    │   ├── test_full_pipeline.py
    │   └── test_parallel_execution.py
    └── fixtures/             # Test data, mocks, fixtures
```

---

## 🚀 Migration Approach (Sequential: Orchestrator → Searcher → Screener)

### Phase 1.5.1: Main Orchestrator Graph

**Goal:** Build core orchestration layer with parallel subgraphs.

**Deliverables:**
- ✅ `src/agents/orchestrator/state.py` - TypedDict state schema
- ✅ `src/agents/orchestrator/nodes/*.py` - 4 phase nodes (pure functions)
- ✅ `src/agents/orchestrator/subgraphs/*.py` - PubMed/Scopus subgraphs
- ✅ `src/db/langgraph_checkpoint.py` - Checkpoint table + ops
- ✅ Unit tests: 10+ test cases, all passing

**Success Criteria:**
- Graph executes full pipeline (4 phases) without error
- Parallel subgraphs process both sources correctly
- State checkpoints saved to PostgreSQL after each phase
- Manual retry paths trigger on simulated errors

---

### Phase 1.5.2: Searcher Agent Integration

**Goal:** Integrate PubMed/Scopus tools with LangGraph subgraphs.

**Deliverables:**
- ✅ `src/tools/pubmed_tool_langchain.py` - Tool wrapper + validation
- ✅ `src/tools/scopus_tool_langchain.py` - Tool wrapper + validation
- ✅ Subgraph nodes updated to use LangChain Tools interface
- ✅ Integration tests with mocked API responses

**Success Criteria:**
- PubMed/Scopus tools call successfully via LangGraph
- Metadata extracted and stored in existing `articles` table
- Parallel execution processes both sources concurrently
- Aggregation merges results correctly

---

### Phase 1.5.3: Screener Agent Integration

**Goal:** Integrate ScreeningAgent (LLM-based filtering) with graph.

**Deliverables:**
- ✅ Screen node updated to use `ScreeningCriteria` + LLM calls
- ✅ PICO extraction integrated into screening workflow
- ✅ Interactive CLI for batch review (existing code adapted)
- ✅ Integration tests with sample article batches

**Success Criteria:**
- ScreeningAgent filters articles based on PRISMA criteria
- PICO elements extracted and stored in `article_data` table
- Manual review path works via interactive CLI
- All 12 existing screener tests pass (adapted to new structure)

---

## 📦 Dependencies (Minimal Setup)

### Core Packages

```toml
[project.dependencies]
langgraph = ">=0.2.0"           # LangGraph core + StateGraph
langchain-core = ">=0.3.0"      # ChatModels, Tools interface
pydantic-settings = ">=2.5.0"   # Config management (from CrewAI)
asyncpg = ">=0.30.0"            # Async PostgreSQL driver

# Optional: Enhanced features
tenacity = ">=9.0.0"            # Retry logic with backoff
fastapi = ">=0.115.0"           # API server (optional, future)
uvicorn[standard] = ">=0.34.0"  # ASGI server for FastAPI

# Existing dependencies (kept as-is)
sqlalchemy = ">=2.0"            # ORM models
psycopg2-binary = ">=2.9"       # Sync DB driver (fallback)
```

### LLM Options

| Provider | Package | Use Case |
|----------|---------|----------|
| **Ollama** | `langchain-ollama` | Local, free, self-hosted (MVP default) |
| **Anthropic** | `langchain-anthropic` | Cloud, better quality (production fallback) |

---

## 🔧 Configuration Management (.env + pydantic-settings)

### `.env.example`

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=prisma_dev
DB_USER=postgres_user
DB_PASSWORD=secure_password_123

# LLM (Ollama default, switch to Anthropic for production)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b-instruct

# LangGraph Checkpointing
LANGGRAPH_CHECKPOINT=true
CHECKPOINT_INTERVAL=phase  # "node" | "phase" | "always"

# API (optional, for FastAPI)
FASTAPI_PORT=8000
FASTAPI_HOST=localhost

# Logging
LOG_LEVEL=INFO
JSON_LOGGING=true
```

### Pydantic Settings Loader

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "prisma_dev"
    db_user: str = "postgres_user"
    db_password: str = "secure_password_123"
    
    # LLM
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:7b-instruct"
    
    # LangGraph
    langgraph_checkpoint: bool = True
    checkpoint_interval: str = "phase"
    
    # API (optional)
    fastapi_port: int = 8000
    fastapi_host: str = "localhost"
    
    @property
    def database_url(self) -> str:
        from urllib.parse import quote_plus
        return f"postgresql+asyncpg://{self.db_user}:{quote_plus(self.db_password)}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = Settings()  # Singleton instance
```

---

## 🎯 API/CLI Interface (Hybrid Approach)

### CLI Entry Point (Existing, Minimal Changes)

**File:** `src/cli/main.py` (existing structure kept)

```python
# Existing entry point - minimal changes needed
from src.agents.orchestrator import MainStateGraph

async def main():
    graph = MainStateGraph()
    config = {"configurable": {"thread_id": "main"}}
    
    # Run pipeline with async/await pattern
    result = await graph.ainvoke(
        {"project_id": 1, "phase": "identification"},
        config=config
    )
```

### FastAPI Integration (Future-Proof)

**File:** `src/api/app.py` (new, optional for future web UI)

```python
from fastapi import FastAPI, HTTPException
from src.agents.orchestrator import MainStateGraph

app = FastAPI(title="PRISMA Pipeline API")
graph = MainStateGraph()

@app.post("/pipeline/run")
async def run_pipeline(project_id: int, phase: str):
    config = {"configurable": {"thread_id": f"project_{project_id}"}}
    
    result = await graph.ainvoke(
        {"project_id": project_id, "phase": phase},
        config=config
    )
    
    return {"status": "running", "project_id": project_id}

@app.get("/pipeline/state/{project_id}")
async def get_state(project_id: int):
    config = {"configurable": {"thread_id": f"project_{project_id}"}}
    state = await graph.aget_state(config)
    return state.values if state else {}
```

---

## 📊 Logging & Tracing (Hybrid Approach)

### LangGraph Tracer + Structured JSON Logs

**LangGraph Tracer:** Built-in visualization of node execution paths.

```python
from langgraph.tracers.print import ConsolePrintTracer

app = build_app(tracer=ConsolePrintTracer())  # Enable tracing
```

**Structured Logging (JSON):** Complement LangGraph tracer with detailed logs.

```python
import logging
import json

logger = logging.getLogger("prisma_langgraph")

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "node": getattr(record, "node_name", "unknown"),
            "message": record.getMessage(),
            "state_hash": getattr(record, "state_hash", None),
        }
        return json.dumps(log_entry)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

---

## ✅ Success Criteria (Per Phase)

### Phase 1.5.1: Main Orchestrator Graph

| Criterion | Target | Verification |
|-----------|--------|--------------|
| **Code Quality** | Clean, testable functions | Code review + linter pass |
| **Unit Tests** | 80%+ coverage | `pytest` report |
| **Integration Test** | Full pipeline end-to-end | Manual + automated run |
| **DB Persistence** | Checkpoints saved per phase | Query `langgraph_checkpoints` table |
| **Parallel Execution** | Both sources processed concurrently | Verify timing with both subgraphs active |

---

### Phase 1.5.2: Searcher Agent Integration

| Criterion | Target | Verification |
|-----------|--------|--------------|
| **Tool Interface** | LangChain Tools compatible | `tool()` decorator works |
| **Metadata Extraction** | ≥90% fields populated | Validate against schema |
| **Parallel Processing** | Concurrent execution | Verify async I/O patterns |
| **Error Handling** | Retry + fallback paths | Simulate API errors, verify recovery |

---

### Phase 1.5.3: Screener Agent Integration

| Criterion | Target | Verification |
|-----------|--------|--------------|
| **LLM Filtering** | ≥80% accuracy vs manual review | Sample test batch of 50 articles |
| **PICO Extraction** | All 4 elements detected | Validate against ground truth |
| **Interactive CLI** | Batch review works (50/articles) | Manual test session |
| **Test Suite** | 12+ tests, all passing | `pytest` coverage report |

---

## 🚦 Next Steps

1. **Initialize LangGraph dependencies** (`uv pip install langgraph langchain-core`)
2. **Create TypedDict state schema** (Phase 1.5.1 step 1)
3. **Build MainStateGraph skeleton** (4 phase nodes + subgraph structure)
4. **Implement first node: `identify_node.py`** (pure function, DB checkpoint)
5. **Test single-phase execution** (verify state persistence works)

---

*Document generated from collaborative design session.*  
*Last updated: 2026-07-05 01:52*
