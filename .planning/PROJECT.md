# 🧬 Agents-Prisma: Sistema Multi-Agente para Revisões Sistemáticas PRISMA

## Visão Geral

Um sistema automatizado de **revisões sistemáticas** baseado na metodologia **PRISMA** (Preferred Reporting Items for Systematic Reviews and Meta-Analyses), utilizando uma arquitetura multi-agentes com **LangChain/LangGraph**.

### Objetivo Principal
Automatizar o processo completo de revisão sistemática, desde a busca em bases de dados científicas até a síntese dos resultados finais, seguindo os 4 estágios obrigatórios do PRISMA:

1. **Identificação** → Busca em PubMed/Medline, Scopus, Web of Science, Google Scholar
2. **Triagem** → Filtragem baseada em critérios de inclusão/exclusão
3. **Elegibilidade** → Análise profunda do texto integral (PDFs via MCP)
4. **Síntese/Inclusão** → Formatação para consumo (Markdown/Obsidian)

---

## 🏗️ Arquitetura Multi-Agentes (CrewAI)

### Agentes Principais

| Agente | Responsabilidade | Fase PRISMA | Status |
|--------|------------------|-------------|--------|
| **Orquestrador** | Gerencia estado e fluxo do funil de revisão | Todas | ✅ Definido |
| **Agente de Busca** | Extrai metadados das bases científicas | 1 - Identificação | ✅ Definido |
| **Agente de Triagem** | Filtra resumos/títulos com critérios | 2 - Triagem | ✅ Definido |
| **Agente Leitor Profundo** | Analisa texto integral via MCP (MarkItDown) | 3 - Elegibilidade | ✅ Definido |
| **Agente de Síntese** | Formata dados para Obsidian/Markdown | 4 - Inclusão/Síntese | ✅ Definido |
| **Agente Fluxograma PRISMA** | Gera fluxograma obrigatório da metodologia | Pós-processamento | 🆕 Adicionado |

### Arquitetura Técnica (LangGraph + LangChain)

```mermaid
graph TD
    subgraph "Main Orchestrator Graph"
        A[Identify Node] --> B{More Sources?}
        B -- Yes |PubMed/Scopus| C1[Publish Subgraph]
        B -- Yes |Scopus| C2[Scopus Subgraph]
        C1 --> D1[Aggregate Results]
        C2 --> D2[Aggregate Results]
        D1 --> E{All Sources?}
        D2 --> E
        E -- Yes --> F[Screen Node]
        
        F --> G{More Articles?}
        G -- Yes |Batch 2| H[Read Node (Deep Reader)]
        G -- No |Done| I[Synthesize Node]
        
        H --> J{All Batches Done?}
        J -- Yes --> I
        
        I --> K[Finalize + Checkpoint]
    end
    
    subgraph "Database Layer"
        A -.-> L[(projects)]
        F -.-> M[(phases)]
        C1 -.-> N[(articles)]
        F -.-> O[(screening_results)]
        H -.-> P[(article_data)]
        I -.-> Q[(synthesis_outputs)]
    end
    
    subgraph "LLM Layer"
        A -.-> R[Ollama/Anthropic]
        F -.-> S
        H -.-> T
    end
    
    subgraph "Tool Layer"
        C1 -.-> U[pubmed_tool.py + LangChain Tools]
        C2 -.-> V[scopus_tool.py + LangChain Tools]
    end
    
    style A fill:#4CAF50,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#9C27B0,stroke:#333,stroke-width:2px,color:#fff
    style H fill:#673AB7,stroke:#333,stroke-width:2px,color:#fff
```

---

## 🛠️ Stack Tecnológico (LangChain/LangGraph)

### Core Multi-Agentes
- **Framework:** `langgraph` + `langchain-core` (agente autônomo com orquestração baseada em grafos de estado)
- **Estado:** TypedDict + Pydantic validation, nested by phase

### Persistência e Banco de Dados
- **Banco Principal:** PostgreSQL (relacional, produção-ready) + SQLAlchemy ORM
- **Async Integration:** `asyncpg` driver para I/O não-bloqueante
- **Schema Design:** Tabelas normalizadas por fase PRISMA + `langgraph_checkpoints`

### Extração e Processamento de PDFs
- **MCP Server:** `MarkItDown` (conversão PDF → Markdown estruturado)
- **Fallback:** `Filesystem MCP` + regex extraction

### Automação Web/Scraping
- **Bases Integradas:** PubMed, Medline, Scopus, Web of Science, Google Scholar
- **APIs:** RESTful endpoints oficiais das bases científicas
- **Tool Interface:** LangChain Tools interface para integração padronizada

### Memory & Context
- **DB-Backed Persistence:** Armazenamento de histórico de conversas no PostgreSQL por fase
- **Auto-checkpointing:** Persistência automática do estado após cada nó completar

---

## 📁 Estrutura de Projetos (LangChain/LangGraph Style)

```
Agents-Prisma/
├── .planning/                    # GSD Planning Artifacts
│   ├── PROJECT.md               # Contexto do projeto
│   ├── REQUIREMENTS.md          # Requisitos escopados
│   ├── ROADMAP.md               # Estrutura de fases
│   ├── STATE.md                 # Memory & Context
│   └── ARCHITECTURE.md          # Arquitetura técnica (MERMAID)
│
├── src/
│   ├── agents/                  # LangGraph agent definitions
│   │   ├── __init__.py         # Exports: MainStateGraph, PubMedSubgraph, ScopusSubgraph
│   │   ├── main.py             # Entry point + CLI/FastAPI setup
│   │   └── orchestrator.py     # Main StateGraph implementation
│   │       ├── state.py        # TypedDict state schema definitions
│   │       ├── nodes/          # Pure function nodes (per phase)
│   │       │   ├── identify_node.py
│   │       │   ├── screen_node.py
│   │       │   ├── read_node.py
│   │       │   └── synthesize_node.py
│   │       └── subgraphs/      # Parallel source graphs
│   │           ├── pubmed_subgraph.py
│   │           └── scopus_subgraph.py
│   │
│   ├── tools/                   # LangChain Tools interface (adapted from existing)
│   │   ├── __init__.py
│   │   ├── base_tool.py         # Abstract base class for all tools
│   │   ├── pubmed_tool_langchain.py  # Adapted pubmed_mcp + tool wrapper
│   │   └── scopus_tool_langchain.py  # Adapted scopus_mcp + tool wrapper
│   │
│   ├── db/                      # Async PostgreSQL integration
│   │   ├── __init__.py
│   │   ├── async_session.py     # AsyncSession factory, context managers
│   │   ├── models.py            # Existing SQLAlchemy models (unchanged)
│   │   └── langgraph_checkpoint.py  # New: LangGraph checkpoint table + ops
│   │
│   ├── llm/                     # LLM configuration & wrappers
│   │   ├── __init__.py
│   │   ├── base.py              # BaseLLM abstraction
│   │   ├── ollama_llm.py        # Local Ollama integration
│   │   └── anthropic_llm.py     # Cloud Anthropic (fallback)
│   │
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py          # pydantic-settings + .env loading
│   │   └── langgraph_config.yaml # LangGraph-specific runtime config
│   │
│   ├── cli/                     # CLI interface (existing)
│   │   └── main.py              # Existing `python -m src.agents.main` entry point
│   │
│   └── tests/                   # Test suite
│       ├── unit/                # Unit tests per node/function
│       ├── integration/         # End-to-end workflow tests
│       └── fixtures/            # Test data, mocks, fixtures
│
├── docs/                        # Documentation (new)
│   └── YYYY-MM-DD-*.md          # Date-prefixed design/spec files
│
└── .planning/research/          # Pesquisa de domínio (opcional)
    └── SUMMARY.md               # Síntese da pesquisa técnica
```

---

## 🚀 Roadmap Inicial (LangGraph + LangChain Style)

### Fase 1: Fundação (MVP + Core) - ✅ COMPLETA

**Checklist de Execução:**
- [x] Configurar ambiente LangChain/LangGraph + PostgreSQL (~45 min vs 8h est.)
- [x] Implementar MainStateGraph (4 fases PRISMA + subgraphs paralelos)
- [x] Integrar APIs das bases científicas com LangChain Tools interface

**Entregáveis:**
- ✅ `src/agents/orchestrator.py` - State machine, transitions, checkpointing
- ✅ `src/tools/pubmed_tool.py`, `scopus_tool.py` - API wrappers (adaptados para LangChain Tools)
- ✅ `src/db/models.py` - SQLAlchemy models + asyncpg integration
- ✅ 19 testes unitários passando (orchestrator: 4, pubmed: 3, screener: 12)

---

### Fase 1.5: LangGraph Migration (~3 dias est.) - 🆕 PENDENTE

**Checklist de Execução:**
- [ ] **TypedDict State Schema** (`src/agents/state.py`) - Nested by phase (identification/screening/read/synthesis)
- [ ] **MainStateGraph Implementation** (`src/agents/orchestrator_langgraph.py`) - Identify/Screen/Read/Synthesize nodes (pure functions)
- [ ] **PubMed/Scopus Subgraphs** (`src/agents/subgraphs/*.py`) - Parallel execution com Diamond Pattern
- [ ] **Async PostgreSQL + Auto-checkpointing** (`src/db/langgraph_checkpoint.py`) - Per-phase persistence

**Como Aproveitar Fase 1:**
| Artefato Existente | Como Reutilizar na Phase 1.5 |
|-------------------|------------------------------|
| `src/agents/orchestrator.py` | Base para `orchestrator_langgraph.py` - mesma lógica, mas migrar para LangGraph StateGraph |
| `src/tools/pubmed_tool.py` | Adaptar como **LangChain Tool wrapper** (`pubmed_tool_langchain.py`) |
| `src/tools/scopus_tool.py` | Completar (~80%) + adaptar como **LangChain Tool wrapper** |
| `src/agents/screener.py` | Adaptar como **Screen Node pure function** dentro do MainStateGraph (PICO + keywords já implementados!) |
| PostgreSQL Connection | Converter para **asyncpg** + JSONB checkpointing |

---

### Fase 2: Triagem + Leitura Profunda (~7 dias est.) - 🟡 EM ANDAMENTO (Issue #002)

**Objetivo:** Implementar agentes de triagem automática e leitura profunda para processamento de artigos científicos.

**Checklist de Execução (Phase 2):**
- [ ] **Agente de Triagem** (`src/agents/screener.py` - já implementado!)
  - LLM-based title/abstract filtering com PICO + keywords
  - Critérios configuráveis via JSON (`.planning/prisma_criteria.json`)
  - Interactive CLI para revisão manual em batches
  
- [ ] **MCP MarkItDown Integration** (`src/tools/markitdown_tool.py`)
  - PDF → Markdown estruturado via MCP server
  - Fallback: `pdfplumber` + regex extraction
  
- [ ] **Agente Leitor Profundo** (`src/agents/deep_reader.py`)
  - Download de PDFs via DOI (PubMed, Scopus)
  - Extração estruturada PICO com confidence score
  - Risk of bias assessment

**Entregáveis:**
- ✅ `src/agents/screener.py` - LLM-based filtering (PICO + keywords, 12 testes passando)
- ⏳ `src/tools/markitdown_tool.py` - MCP MarkItDown wrapper
- ⏳ `src/agents/deep_reader.py` - PDF processing pipeline

**Métricas de Sucesso:**
| Métrica | Meta Mínima | Meta Otimista |
|---------|-------------|---------------|
| Artigos processados/hora | 50 | 200+ |
| Taxa de conversão PDF→Markdown | >90% | >98% |
| Confiança extração PICO | >0.7 | >0.85 |
| Tempo médio por artigo (screening) | <30s | <15s |

---

### Fase 3: Síntese e Fluxograma (~4 dias est.) - ⏳ PENDENTE

- [ ] **Agente Síntese** (`src/agents/synthesizer.py`)
  - Agrupamento por temas/categorias dos artigos elegíveis
  - Tabelas Markdown compatíveis com Obsidian
  
- [ ] **Agente Fluxograma PRISMA** (`src/agents/prisma_flowchart.py`)
  - Geração de Mermaid.js diagrams baseado nos dados de triagem
  - Exportação PNG/SVG via `graphviz` ou `mermaid.js`

---

### Fase 4: Hardening e Extensões (~6 dias est.) - ⏳ PENDENTE

- [ ] **UI/API Design** para interação humana (CLI/REST API)
- [ ] **Testes automatizados** dos agentes (integration tests, E2E flows)
- [ ] **Documentação completa** + exemplos de uso

---

## 📊 Dados de Entrada/Saída

| Entrada | Formato | Origem |
|---------|---------|--------|
| Query de pesquisa | String | Usuário/API externa |
| Metadados artigos | JSON (DOI, título, autores) | PubMed/Scopus APIs |
| PDFs integrais | Binary/PDF | Download via API ou upload local |

| Saída | Formato | Destino |
|-------|---------|---------|
| Funnel de revisão | Markdown tabela | Obsidian/Notion |
| Fluxograma PRISMA | PNG/SVG/Mermaid | Relatório final |
| Dados sintetizados | JSON/Markdown | Consumo downstream |

---

## 🔄 Estado Atual (Last Updated: 2026-07-05 01:55)

### Phase State

| Fase | Sub-fase | Status | Progresso (%) | Bloqueios |
|------|----------|--------|---------------|-----------|
| **1. Fundação + Core** | 1.1 Configuração Ambiente | ✅ COMPLETA (45min vs 8h est.) | 100% | - |
| | 1.2 Agente Orquestrador | ✅ COMPLETA (~16h est.) | 100% | - |
| | 1.3 Agente Busca + APIs | ✅ COMPLETA (PubMed + Scopus MVP) | 100% | - |
| | **1.4 Screening Agent** | ✅ COMPLETA (~2h est., Issue #002) | 100% | - |
| | **1.5 LangGraph Migration** | 🆕 Pendente | 0% | Aguardando `/gsd:plan-phase 1.5` |
| **2. Triagem + Leitura** | 2.1 Agente Triagem | ✅ COMPLETA (Issue #002) | 100% | - |
| | 2.2 MCP MarkItDown Integration | ⏳ Pendente | 0% | Aguardando Fase 2.3 |
| | 2.3 Agente Leitor Profundo | ⏳ Pendente (Issue #002) | 0% | - |

---

### 📁 Artifacts Criados (Current Session)

```
.planning/
├── PROJECT.md              ✅ Atualizado ← LangGraph architecture + Issue #002 sync
│   └── Contexto, stack, roadmap atualizado
├── REQUIREMENTS.md         ✅ Detalhado (564 lines)
│   └── Requisitos por agente, DB schema, LangChain Tools interface
├── ROADMAP.md              ✅ Atualizado ← Phase 1.4/1.5 added
│   └── Estrutura de fases granulares + checklist
├── STATE.md                ✅ Atualizado (393 lines)
│   └── Decision log (DECISION-001 a DECISION-007) + state tracking
├── ARCHITECTURE.md         ✅ Criado (MERMAID diagrams, TypedDict schema)
├── docs/                   ✅ Criado
│   └── 2026-07-05-langgraph-migration-design.md
└── prisma_criteria.json    ✅ Template PRISMA

src/agents/                 ✅ Implementado
├── orchestrator.py         ✅ Fase 1.2 - State machine, transitions, checkpointing
├── searcher.py             ✅ Fase 1.3 - Multi-source search (PubMed + Scopus)
└── screener.py             ✅ Fase 1.4 - LLM-based filtering (PICO + keywords, 12 tests passing)

src/tools/                  ✅ Implementado
├── pubmed_tool.py          ✅ PubMed E-utilities integration
└── scopus_tool.py          ⏳ ~80% completo (Abstract extraction done)

tests/                      ✅ Testes rodando
├── test_orchestrator.py    ✅ 4 cases, all passing
├── test_pubmed_tool.py     ✅ 3 cases, all passing
└── test_screener.py        ✅ 12 cases, all passing

config/                     ✅ Configurados
└── prisma_criteria.json    ✅ Critérios configuráveis por projeto
```

---

### 🎯 Próximas Ações (Priority Order)

#### Alta Prioridade (Next 24-48h) - Issue #002
1. **Review `src/agents/orchestrator.py`** → Validação com stakeholder
2. **Adaptar para LangChain Tools** (`pubmed_tool_langchain.py`, `scopus_tool_langchain.py`)
3. **Execute Full Pipeline Test** (`python -m src.agents.main --query "diabetes" --max-results 3`)

#### Média Prioridade (Next Week)
4. **Migrar para LangGraph** (`src/agents/state.py`, `orchestrator_langgraph.py`)
5. **Setup Async PostgreSQL + JSONB checkpointing** (`src/db/langgraph_checkpoint.py`)

#### Baixa Prioridade (Next 14 dias)
6. **Configurar MCP MarkItDown server** → Verificar compatibilidade com PDFs científicos
7. **Estruturar diretórios `src/nodes/`, `src/subgraphs/`** → Para Phase 1.5 migration

---

*Documento gerado via `/gsd:new-project` com skill `gsd-new-project`, atualizado para LangGraph architecture + Issue #002 sync.*