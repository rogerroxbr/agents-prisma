# Agents-Prisma

Multi-agent system for systematic review pipeline using LangGraph.

## ?? Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run the orchestrator
python src/main.py
```

## ?? MVP Status (Phase 1)

? **Core Agents Implemented:**
- `SearcherAgent`: Searches PubMed and Scopus databases
- `ScreeningAgent`: Filters articles by keywords (title/abstract)  
- `OrchestratorAgent`: Coordinates the full PRISMA pipeline

? **Database Models:** Full SQLAlchemy ORM with async support

? **Testing Suite:** 19 passing tests covering all agents and database operations

## ??? Architecture

```
src/
+-- agents/          # Core agent implementations
   +-- searcher.py  # PubMed + Scopus search
   +-- screener.py  # Keyword filtering
   +-- orchestrator.py # Pipeline coordination
+-- db/              # SQLAlchemy models & async engine
+-- tools/           # External tool integrations
+-- mcp/             # Model Context Protocol integration
```

## ?? Prerequisites

- Python 3.12+
- PostgreSQL or SQLite (configured in `.env`)
- PubMed API access (optional, for Scopus see [Scopus docs](https://www.elsevier.com/solutions/scopus))

## ?? Configuration

Edit `.env`:

```env
USE_SQLITE=true
DB_HOST=localhost
DB_PORT=5432
DB_NAME=prisma_dev
DB_USER=postgres_user
DB_PASSWORD=secure_password_123
```

## ?? Documentation

- See `PROJECT.md` for detailed architecture
- See `CLAUDE.md` for development guidelines  
- See `.github/workflows/ci.yml` for CI/CD pipeline

## ?? Running Tests

```bash
pytest tests/ -v
```

## ?? Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request

---

*Built with LangGraph, SQLAlchemy, and CrewAI*
