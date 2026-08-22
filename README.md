# Agents-Prisma

Multi-agent system for systematic review pipeline using LangGraph.

## 🚀 Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Run the pipeline via CLI
uv run python src/cli.py run --query "diabetes AND complications" --max-results 10
```

## 📊 Features

- **End-to-End Pipeline**: Identification -> Screening -> Eligibility -> Synthesis
- **Searchers**: PubMed, Scopus, Google Scholar
- **LLM-Based Screening**: Automated PICO extraction and filtering
- **LangGraph Integration**: Robust state tracking and workflow orchestration
- **CLI & REST API**: Flexible interfaces for executing and tracking projects
- **Markdown & JSON Reports**: Synthesis output in Obsidian-ready Markdown and structured JSON.

## 🛠️ Architecture

```
src/
+-- agents/          # Core LangGraph orchestration and nodes
+-- api/             # FastAPI REST endpoints and server
+-- cli.py           # Typer CLI interface
+-- db/              # SQLAlchemy models & async engine
+-- tools/           # External tool integrations
+-- mcp/             # Model Context Protocol integration
```

## 🔌 Using the REST API

Start the FastAPI server:
```bash
uv run uvicorn src.api.server:app --reload --port 8000
```

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/projects/run" \
     -H "Content-Type: application/json" \
     -d '{"query": "diabetes", "max_results": 20}'
```

Access the interactive API documentation at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 💻 Using the CLI

Run the full PRISMA pipeline directly from the terminal:
```bash
uv run python src/cli.py run -q "hypertension" -m 50
```

Check the status of a project (requires DB integration):
```bash
uv run python src/cli.py status -p "project-uuid"
```

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL or SQLite (configured in `.env`)
- Local LLM via LM Studio (port 1234)

## ⚙️ Configuration

Edit `.env`:

```env
USE_SQLITE=true
DB_HOST=localhost
DB_PORT=5432
DB_NAME=prisma_dev
DB_USER=postgres_user
DB_PASSWORD=secure_password_123
```

## 🧪 Running Tests

```bash
# Run unit and integration tests
uv run pytest tests/ -v
```

---

*Built with LangGraph, FastAPI, Typer, and SQLAlchemy*
