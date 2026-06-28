# Phase 1: Foundation + Core (MVP) - Detailed Plan

## Overview
**Duration:** ~5-7 days  
**Goal:** Configure environment, implement orchestrator with state management, integrate scientific APIs, add reviewer agent for human-in-the-loop validation.

---

## 1.1 Configuração do Ambiente (~1 dia / 8h)

### Tasks:

#### 1.1.1 Setup Python Environment (2h)
- [ ] Initialize virtual environment via uv venv
- [ ] Install core dependencies (crewai, crewai-tools, sqlalchemy, psycopg2-binary)
- [ ] Verify installation with test script

**Acceptance Criteria:**
- ✅ pip list shows all packages installed
- ✅ Test script runs without errors: python -c "import crewai; print(crewai.__version__)"

#### 1.1.2 Configure PostgreSQL Docker (2h)
- [ ] Create docker-compose.yml with postgres service
- [ ] Define database name, user, password (env vars)
- [ ] Verify container running: docker ps | grep postgres
- [ ] Test connection via SQLAlchemy

**Acceptance Criteria:**
- ✅ Container runs persistently on port 5432
- ✅ Connection test passes: SELECT 1; returns result
- ✅ .env.example file created with credentials template

#### 1.1.3 Configure SQLAlchemy ORM (2h)
- [ ] Create project-level database models (projects, phases, rticles)
- [ ] Define relationships and foreign keys
- [ ] Test CRUD operations via test script

**Acceptance Criteria:**
- ✅ Models defined in src/db/models.py
- ✅ Basic CRUD works: create, read, update, delete records
- ✅ Relationships validated (project → phases → articles)

#### 1.1.4 Structure Directories & Configs (2h)
- [ ] Create directory structure (src/agents/, src/tasks/, src/tools/, 	ests/, config/)
- [ ] Initialize crew_config.yaml with default settings
- [ ] Create prisma_criteria.json template for configurable criteria

**Acceptance Criteria:**
- ✅ VS Code recognizes all directories as Python packages
- ✅ .gitignore updated (.venv, __pycache__, etc.)
- ✅ Config files load correctly via YAML/JSON parsers

---

## 1.2 Agente Orquestrador + Revisor (~3 dias / 24h)

### Tasks:

#### 1.2.1 Define Pipeline State Schema (3h)
- [ ] Design state model for 5-phase pipeline (Identification → Screening → Eligibility → Synthesis → Review)
- [ ] Include metadata tracking (created_at, last_updated, total_articles, included_articles, etc.)
- [ ] Serialize to JSON/PostgreSQL

**Acceptance Criteria:**
- ✅ State schema matches REQUIREMENTS.md specification
- ✅ Serialization/deserialization works bidirectionally
- ✅ Checkpointing saves state after each phase completion

#### 1.2.2 Implement Core Orchestrator Logic (5h)
- [ ] Create OrchestratorAgent class extending CrewAI Agent base
- [ ] Define transition functions between phases (phase_1_complete(), phase_2_complete(), etc.)
- [ ] Implement error handling and retry logic

**Acceptance Criteria:**
- ✅ Orchestrator creates initial state in PostgreSQL
- ✅ Sequential phase transitions work without errors
- ✅ Error recovery works (retries failed API calls up to 3x)

#### 1.2.3 Add Checkpointing & Reprise (4h)
- [ ] Implement checkpoint save after each phase completion
- [ ] Create reprise function that loads last saved state and continues from there
- [ ] Test failure scenario: stop mid-pipeline, resume successfully

**Acceptance Criteria:**
- ✅ State persisted to PostgreSQL after each phase
- ✅ Reprise loads correct state (last completed phase)
- ✅ No data loss on interruption/resume

#### 1.2.4 Implement Structured Logging (3h)
- [ ] Create JSON logger with fields: timestamp, phase, article_id, action, status, metadata
- [ ] Log to file + PostgreSQL for audit trail
- [ ] Test log retrieval via query

**Acceptance Criteria:**
- ✅ All transitions logged with consistent schema
- ✅ Logs searchable by phase/article_id in database
- ✅ CLI can display logs in human-readable format (optional)

#### 1.2.5 Add Agente Revisor - Interactive UI (4h)
- [ ] Create ReviewerAgent class that validates outputs from previous phases
- [ ] Implement **Interactive CLI with JSON preview** for criteria configuration
    - Ex: input("population_keywords: ") → shows live JSON update
    - Save to .planning/prisma_criteria.json
- [ ] Design CLI interaction: show results (batch of 50) → accept recommendations → apply to next phase

**Acceptance Criteria:**
- ✅ Reviewer displays structured output after each **50-article batch**
- ✅ User can provide text recommendations via interactive prompts
    - Ex: input("Observações sobre este batch: ")
- ✅ Dual validation implemented:
    1. **PICO quality check**: Regex match on extracted Population, Intervention, Comparison, Outcome fields
    2. **Keywords match check**: Verify user-defined keywords found in full text (in operator)
- ✅ Recommendations stored and applied before proceeding to next batch

#### 1.2.6 Unit Tests for Orchestrator + Revisor (3h)
- [ ] Mock PostgreSQL connection in tests
- [ ] Test state transitions: pending → running → completed
- [ ] Test checkpoint/reprise with mocked data
- [ ] Test reviewer output formatting

**Acceptance Criteria:**
- ✅ ≥80% code coverage for orchestrator logic
- ✅ All unit tests pass: pytest tests/test_orchestrator.py -v
- ✅ Mocked database connection works without live PostgreSQL

---

## 1.3 Agente Busca + APIs Científicas (~23h total)

### Tasks:

#### 1.3.1 Integrate Academic Search MCP (4h)
From user input: https://pypi.org/project/academic-search/ and https://hub.docker.com/mcp/server/paper-search/tools

- [ ] Research available MCP servers for academic search
- [ ] Install/configure Academic Search MCP server via uv add -r academic-search-mcp or Docker
- [ ] Create wrapper tool in Python: src/tools/academic_search_mcp.py
- [ ] Test with sample query: "diabetes AND complications"

**Acceptance Criteria:**
- ✅ MCP server installed and running (Docker or pip)
- ✅ Wrapper tool loads without errors
- ✅ Sample query returns ≥10 valid results

#### 1.3.2 Integrate PubMed API Directly (4h)
- [ ] Create src/tools/pubmed_tool.py with EMBASE REST integration
- [ ] Implement boolean query parsing (AND, OR, NOT, parentheses)
- [ ] Extract metadata: DOI, title, authors, year, journal

**Acceptance Criteria:**
- ✅ Query "diabetes AND complications" returns ≥50 results
- ✅ All required fields populated for ≥90% of results
- ✅ Error handling for rate limits (retry with backoff)

#### 1.3.3 Integrate Scopus API (4h)
- [ ] Create src/tools/scopus_tool.py with Elsevier v2 REST integration
- [ ] Handle authentication via Client ID + API Key
- [ ] Extract extended metadata (abstract, PDF URL if available)

**Acceptance Criteria:**
- ✅ Query returns ≥30 results for sample query
- ✅ Abstracts extracted successfully for ≥85% of results
- ✅ PDF URLs present for peer-reviewed articles

#### 1.3.4 Integrate Web of Science API (4h)
- [ ] Create src/tools/web_of_science_tool.py with Clarivate v2 REST integration
- [ ] Implement authentication flow
- [ ] Extract citation metrics if available

**Acceptance Criteria:**
- ✅ Query returns ≥20 results for sample query
- ✅ Citation counts populated where available
- ✅ Fallback handling for offline/incomplete records

#### 1.3.5 Tool de Busca com Browser (Selenium/Playwright - 3h)
- [ ] Create src/tools/browser_search.py with **headless Chrome** via Selenium or Playwright
    - Method: search(query) → returns list of URLs + basic metadata (title, year if available)
    - Sources: PubMed web, Scopus web, Google Scholar, Web of Science web
- [ ] Implement dynamic selectors detection
    - Regex patterns for common academic result layouts
    - Auto-adjust selectors based on page structure

**Acceptance Criteria:**
- ✅ Executes parallel searches across 4+ sources (PubMed, Scopus, WoS, Google Scholar)
- ✅ Extracts valid URLs + basic metadata for each result
- ✅ Headless Chrome runs without GUI interface
- ✅ Retry logic: if first attempt fails, retry with different timeout

#### 1.3.6 Tool de Scraping Avançado com Playwright (3h)
- [ ] Create src/tools/browser_scraping.py with **full Playwright** + advanced CSS selectors
    - Methods: scrape_pdf_url(url), extract_full_text(), parse_structured_data()
    - Sources: All academic databases (PubMed, Scopus, WoS, Google Scholar), institutional repositories, preprints (arXiv, bioRxiv)
- [ ] Implement fallback chain for complex PDF layouts
    - Chain: Direct API → Browser navigation to download page → Regex extraction
    - Handle iframes, popups, lazy loading

**Acceptance Criteria:**
- ✅ Structured scraping with dynamic CSS/xpath selectors
- ✅ Handles iframes, modals, lazy-loaded content
- ✅ Rate limiting: max 2 requests/second to prevent blocking
- ✅ Configurable timeout per source (e.g., Google Scholar = 30s, PubMed = 15s)

#### 1.3.7 Parallel Execution Flow (Integration - 2h)
- [ ] Implement parallel execution of **Thread 1: Direct APIs** + **Thread 2: Browser Tools**
    - Thread 1: Fast metadata extraction via REST APIs (PubMed, Scopus v2)
    - Thread 2: Fallback/browser enrichment for complex layouts or iframe-hosted PDFs
- [ ] Consolidate results from both sources into unified metadata object

**Acceptance Criteria:**
- ✅ Both threads run concurrently without blocking each other
- ✅ Results merged intelligently (deduplicate by DOI, prefer richer data)
- ✅ Total execution time ≤ max(Thread1_time, Thread2_time), not sum

#### 1.3.8 Unit Tests for Search Tools (4h)
- [ ] Mock all external API responses in tests
- [ ] Test metadata extraction with sample JSON payloads
- [ ] Test error handling and fallback chains
- [ ] Achieve ≥80% code coverage

**Acceptance Criteria:**
- ✅ All 6 search tools tested independently
- ✅ Sample integration test: run full pipeline for "diabetes AND complications"
- ✅ ≥80% code coverage across all search tools: pytest tests/test_searchers.py -v --cov=src/tools

---

## Dependencies & Sequencing

`mermaid
graph TD
    A[1.1 Configuração Ambiente] --> B{All 4 subtasks complete?}
    B -- Yes --> C[1.2 Agente Orquestrador + Revisor]
    
    C --> D{All 6 subtasks complete?}
    D -- Yes --> E[1.3 Agente Busca + APIs]
    
    E --> F{All 7 subtasks complete?}
    F -- Yes --> G[Fase 1: APROVADA]
    
    B -- No --> A
    D -- No --> C
    F -- No --> E
`

**Sequencing:**
- **1.1 → 1.2:** Sequential (environment must be ready before agent dev)
- **1.2 → 1.3:** Parallel possible, but 1.2 preferred first for state management foundation
- **Within each phase:** Tasks can run in parallel if independent

---

## Risk Analysis & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| MCP server compatibility issues | Medium | High | Have direct API fallbacks ready (PubMed, Scopus) |
| PostgreSQL Docker conflicts with existing containers | Low | Medium | Use unique container name: gents-prisma-postgres-1 |
| **Browser automation conflicts with existing Chrome instances** | **Medium** | **High** | Use unique headless Chrome instance names via Selenium/Playwright config (options.add_argument('--remote-debugging-port=9222')) |
| API rate limits during testing | Medium | Medium | Implement exponential backoff retry logic upfront |
| Reviewer agent CLI UX complexity | Medium | Medium | Start simple (markdown tables), iterate based on feedback |
| State serialization/deserialization bugs | Low | High | Use Pydantic models for type-safe state management |

---

## Time Allocation Summary

| Sub-task | Planned Hours | Estimated Completion |
|----------|---------------|----------------------|
| 1.1 Configuração Ambiente | 8h | Day 1 |
| 1.2 Agente Orquestrador + Revisor | 24h | Days 2-3 |
| 1.3 Agente Busca + APIs | **23h** | Days 4-6 |
| &nbsp;&nbsp;├── 1.3.1 Academic Search MCP | 4h | Day 4 morning |
| &nbsp;&nbsp;├── 1.3.2 PubMed API | 4h | Day 4 afternoon |
| &nbsp;&nbsp;├── 1.3.3 Scopus API | 4h | Day 5 morning |
| &nbsp;&nbsp;├── 1.3.4 Web of Science API | 4h | Day 5 afternoon |
| &nbsp;&nbsp;├── **1.3.5 Browser Search (Headless Chrome)** | **3h** | Day 6 morning |
| &nbsp;&nbsp;├── **1.3.6 Browser Scraping (Playwright + CSS)** | **3h** | Day 6 afternoon |
| &nbsp;&nbsp;├── **1.3.7 Parallel Execution Flow** | **2h** | Day 6 evening |
| &nbsp;&nbsp;└── 1.3.8 Unit Tests for Search Tools | 4h | Day 7 morning |
| **Total** | **55h (~8 days)** | **~End of Week 2** |

---

## Deliverables Checklist

### Code Artifacts:
- [ ] src/db/models.py - SQLAlchemy ORM models
- [ ] src/agents/orchestrator.py - Core orchestrator agent
- [ ] src/agents/reviewer.py - Human-in-the-loop reviewer agent (Interactive UI)
- [ ] src/tools/pubmed_tool.py, scopus_tool.py, etc. - API integrations
- [ ] **src/tools/browser_search.py** - Headless Chrome browser search
- [ ] **src/tools/browser_scraping.py** - Advanced Playwright scraping with CSS selectors
- [ ] 	ests/test_orchestrator.py, 	est_searchers.py - Unit tests

### Config Artifacts:
- [ ] docker-compose.yml - PostgreSQL container definition
- [ ] .env.example - Environment variables template
- [ ] crew_config.yaml - CrewAI configuration
- [ ] **.planning/prisma_criteria.json** - User-configurable PRISMA criteria (via Interactive CLI)

### Documentation:
- [ ] README.md - Project setup instructions
- [ ] docs/api-keys.md - API key documentation (Scopus, Web of Science)
- [ ] .gitignore - Updated with Python/Docker patterns
- [ ] **docs/browser-tools-config.md** - Browser automation configuration guide

---

## Verification Plan (Post-Phase 1)

### Interactive UI Test:
`ash
# 1. Configure PRISMA criteria via Interactive CLI
python src/agents/test_reviewer_ui.py
# Expects prompts like:
#   "=== População ===" → input("Digite keywords: ")
#   Shows live JSON preview as you type

# 2. Test batch processing (50 articles)
python tests/integration_test_batches.py --batch-size 50
# Expects CLI output with formatted tables + prompts like:
#   "Review completo? (Y/n): "
`

### Manual Tests:
`ash
# 1. Environment setup
docker-compose up -d
uv sync
python src/db/test_connection.py  # Should print "Connected to PostgreSQL"

# 2. Orchestrator state management
python src/agents/test_orchestrator.py  # Should create, save, and load state

# 3. Search API integration (parallel execution)
python tests/integration_test_searchers.py --parallel-mode
# Should query PubMed & Scopus via REST APIs AND Browser tools simultaneously

# 4. Full pipeline test (small scale)
python main.py --query "diabetes AND complications" --limit 100 --batch-size 50
# Should complete Phase 1 in <10min with interactive review prompts
`

### Automated Tests:
`ash
pytest tests/ -v --cov=src --cov-report=html
# Target: ≥80% code coverage across all modules
`

---

## Next Steps After Plan Approval

1. **Execute 1.1 Configuração Ambiente** (Day 1)
   `ash
   cd C:\Users\Roger\Documents\Projetos\Agents-Prisma
   uv venv && uv sync
   docker-compose up -d
   `

2. **Daily Progress Tracking:** Update .planning/STATE.md with:
   - Completed sub-tasks (check off list)
   - New issues encountered + solutions
   - Time spent vs estimated

3. **Mid-Phase Review (Day 4):** Verify 1.2+1.3 progress, adjust timeline if needed

4. **Final Phase 1 Sign-off:** Run verification plan above, get stakeholder approval before proceeding to Phase 2

---

*Created: 28/06/2026 | Version: 1.1 (Updated with Browser Tools + Interactive UI) | Author: GSD-Plan-Phase Agent*
