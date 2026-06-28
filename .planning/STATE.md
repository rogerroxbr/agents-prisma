# ðŸ§  State - Agents-Prisma: Memory & Context

## VisÃ£o Geral

Este arquivo serve como **memory central** para o projeto, capturando decisÃµes importantes, contexto de execuÃ§Ã£o e estado atualizado ao longo do ciclo de vida.

---

## ðŸ“… HistÃ³rico de DecisÃµes (Decision Log)

### DECISION-001: Framework Multi-Agentes - CrewAI
**Data:** 28/06/2026  
**Contexto:** Escolha entre LangGraph, AutoGen e CrewAI para arquitetura multi-agentes.

| OpÃ§Ã£o | PrÃ³s | Contras | Peso |
|-------|------|---------|------|
| **CrewAI (Escolhida)** | Simples de configurar, workflow pipeline nativo, boa documentaÃ§Ã£o | Menos flexÃ­vel que LangGraph para grafos complexos | 8/10 |
| LangGraph | Grafos de estado poderosos, controle fino | Mais complexo, curva de aprendizado maior | 7/10 |
| AutoGen | Agentes conversacionais, flexibilidade alta | Menos estruturado, mais configuraÃ§Ã£o manual | 6/10 |

**DecisÃ£o:** CrewAI por ser **mais simples para MVP**, com workflow pipeline nativo que se alinha bem Ã s 4 fases PRISMA sequenciais.

---

### DECISION-002: PersistÃªncia - PostgreSQL vs SQLite
**Data:** 28/06/2026  
**Contexto:** Escolha de banco de dados para persistÃªncia de estado do pipeline.

| OpÃ§Ã£o | PrÃ³s | Contras | Peso |
|-------|------|---------|------|
| **PostgreSQL (Escolhida)** | Relacional robusto, produÃ§Ã£o-ready, SQLAlchemy ORM nativo | Requer Docker/instalaÃ§Ã£o, mais overhead | 8/10 |
| SQLite | Simples, file-based, zero-config | Menos escalÃ¡vel, menos features avanÃ§adas | 6/10 |

**DecisÃ£o:** PostgreSQL para **escalabilidade e robustez**, com fallback a SQLite apenas para desenvolvimento rÃ¡pido.

---

### DECISION-003: ExtraÃ§Ã£o PDF - MCP MarkItDown
**Data:** 28/06/2026  
**Contexto:** Como converter PDFs cientÃ­ficos em Markdown legÃ­vel para o Agente Leitor Profundo.

| OpÃ§Ã£o | PrÃ³s | Contras | Peso |
|-------|------|---------|------|
| **MCP MarkItDown (Escolhida)** | Especializado em conversÃ£o complexa, multi-formato, boa comunidade | Requer MCP server rodando | 9/10 |
| PyPDF2/pdfplumber | Python puro, zero-dependÃªncia | Menos robusto para PDFs com layouts complexos | 6/10 |

**DecisÃ£o:** MCP MarkItDown por ser **especializado em documentos cientÃ­ficos**, com melhor taxa de conversÃ£o para Markdown estruturado.

---

### DECISION-004: Estrutura de Arquivos - Customizada PRISMA
**Data:** 28/06/2026  
**Contexto:** OrganizaÃ§Ã£o dos arquivos seguindo padrÃµes CrewAI vs organizaÃ§Ã£o temÃ¡tica PRISMA.

| OpÃ§Ã£o | PrÃ³s | Contras | Peso |
|-------|------|---------|------|
| **Customizada PRISMA (Escolhida)** | Alinhada com fases metodolÃ³gicas, intuitiva para domain experts | Menos padrÃ£o que estrutura oficial CrewAI | 8/10 |
| CrewAI PadrÃ£o (`agents/`, `tasks/`, `tools/`) | Oficial, documentada, compatÃ­vel com ecosystem | Menos alinhada com fluxo PRISMA sequencial | 7/10 |

**DecisÃ£o:** Estrutura **hÃ­brida**: manter organizaÃ§Ã£o por agentes (CrewAI), mas agrupar tasks por fases PRISMA (`identification/`, `screening/`, etc.).

---

### DECISION-005: Fontes CientÃ­ficas - 4 Bases Principais
**Data:** 28/06/2026  
**Contexto:** SeleÃ§Ã£o das bases cientÃ­ficas para integraÃ§Ã£o inicial.

| Base | Cobertura | API Restante | Custo | Peso |
|------|-----------|--------------|-------|------|
| **PubMed/Medline** | CiÃªncias da saÃºde (â‰ˆ95% artigos mÃ©dicos) | REST oficial, opcional | Gratuito | 10/10 |
| Scopus | Multidisciplinar (~30M artigos) | REST v2, obrigatÃ³rio | Pago (~$1k/mÃªs) | 8/10 |
| Web of Science | CitaÃ§Ãµes/mÃ©tricas (~25M artigos) | REST v2, obrigatÃ³rio | Pago (~$1.5k/mÃªs) | 7/10 |
| Google Scholar | Amplo acesso (~150M resultados) | Scraping/custom API | Gratuito (scraping) | 6/10 |

**DecisÃ£o:** Integrar **todas as 4 bases**, comeÃ§ando com PubMed (gratuito), depois Scopus/Web of Science (se budget permitir).

---

### DECISION-006: Adicionar Agente Fluxograma PRISMA
**Data:** 28/06/2026  
**Contexto:** ExpansÃ£o dos agentes alÃ©m dos 5 principais.

| OpÃ§Ã£o | PrÃ³s | Contras | Peso |
|-------|------|---------|------|
| **Agente Fluxograma PRISMA (Escolhida)** | Gera fluxograma obrigatÃ³rio da metodologia, visualizaÃ§Ã£o clara | Adiciona complexidade ao pipeline | 8/10 |
| Apenas os 5 principais | Mais simples, menos cÃ³digo | Faltaria elemento visual obrigatÃ³rio do PRISMA | 6/10 |

**DecisÃ£o:** Incluir **Agente Fluxograma PRISMA** por ser elemento obrigatÃ³rio da metodologia e fornecer valor agregado (visualizaÃ§Ã£o clara do funnel).

---

## ðŸ”„ Estado Atual do Projeto

### Phase State (Last Updated: 28/06/2026)

| Fase | Sub-fase | Status | Progresso (%) | Bloqueios |
|------|----------|--------|---------------|-----------|
| **1. Fundação + Core** | 1.1 Configuração Ambiente | 🟢 Em andamento (Issue #001 criada, branch feature/001-config-environment) | 25% | -
| | 1.2 Agente Orquestrador | â³ Pendente | 0% | Aguardando 1.1 |
| | 1.3 Agente Busca + APIs | â³ Pendente | 0% | Aguardando 1.2 |
| **2. Triagem + Leitura** | 2.1 Agente Triagem | â³ Pendente | 0% | Aguardando Fase 1 |
| | 2.2 MCP MarkItDown Integration | â³ Pendente | 0% | Aguardando Fase 1 |
| **3. SÃ­ntese + Fluxograma** | 3.1 Agente SÃ­ntese Markdown | â³ Pendente | 0% | Aguardando Fase 2 |
| | 3.2 Agente Fluxograma PRISMA | ðŸ†• Adicionado | 0% | - |
| **4. Hardening + ExtensÃµes** | 4.1 Testes Automatizados | â³ Pendente | 0% | Aguardando Fase 3 |
| | 4.2 UI/API Design | â³ Pendente | 0% | Aguardando Fase 3 |

---

### ðŸ“ Artifacts Criados (Current Session)

```
.planning/
â”œâ”€â”€ PROJECT.md              âœ… Criado (28/06/2026 14:30)
â”‚   â””â”€â”€ Contexto, stack, arquitetura inicial
â”œâ”€â”€ REQUIREMENTS.md         âœ… Criado (28/06/2026 14:35)
â”‚   â””â”€â”€ Requisitos detalhados por agente/fase
â”œâ”€â”€ ROADMAP.md              âœ… Criado (28/06/2026 14:40)
â”‚   â””â”€â”€ Estrutura de fases granulares + checklist
â””â”€â”€ STATE.md                âœ… Criado (28/06/2026 14:45) â† Agora
    â””â”€â”€ Decision log + state tracking

src/                        â³ Pendente
â”œâ”€â”€ agents/                 â³ Pendente
â”‚   â”œâ”€â”€ orchestrator.py     â³ Fase 1.2
â”‚   â”œâ”€â”€ searcher.py         â³ Fase 1.3
â”‚   â”œâ”€â”€ screener.py         â³ Fase 2.1
â”‚   â”œâ”€â”€ deep_reader.py      â³ Fase 2.2
â”‚   â”œâ”€â”€ synthesizer.py      â³ Fase 3.1
â”‚   â””â”€â”€ prisma_flowchart.py ðŸ†• Fase 3.2 (adicionado)

tests/                      â³ Pendente
â”œâ”€â”€ test_orchestrator.py    â³ Fase 1.2
â”œâ”€â”€ test_searchers.py       â³ Fase 1.3
â””â”€â”€ ...                     â³ ...

config/                     â³ Pendente
â”œâ”€â”€ crew_config.yaml        â³ Fase 1.1
â””â”€â”€ prisma_criteria.json    â³ Fase 2.1 (critÃ©rios configurÃ¡veis)
```

---

### ðŸ”§ ConfiguraÃ§Ãµes de Workflow (Current Session)

| Config | Valor | Contexto |
|--------|-------|----------|
| **Framework Multi-Agentes** | `CrewAI` | DecisÃ£o DECISION-001 |
| **Banco de Dados** | `PostgreSQL` | DecisÃ£o DECISION-002 |
| **ExtraÃ§Ã£o PDF** | `MCP MarkItDown` | DecisÃ£o DECISION-003 |
| **Estrutura Arquivos** | `HÃ­brida (CrewAI + PRISMA)` | DecisÃ£o DECISION-004 |
| **Fontes CientÃ­ficas** | `PubMed, Scopus, Web of Science, Google Scholar` | DecisÃ£o DECISION-005 |
| **Agentes Principais** | `Orquestrador, Busca, Triagem, Leitor Profundo, SÃ­ntese` | Definido CLAUDE.md |
| **Agentes Adicionais** | `Fluxograma PRISMA` | DecisÃ£o DECISION-006 |
| **Modo Pesquisa** | `Deep (~40 fontes)` | Configurado via question API |

---

### ðŸ•’ MÃ©tricas de Progresso (Session Timeline)

| Evento | Timestamp | DuraÃ§Ã£o Acumulada |
|--------|-----------|-------------------|
| Projeto inicializado (`/gsd:new-project`) | 14:30 | 0h |
| Pesquisa tÃ©cnica iniciada (Deep mode) | 14:32 | ~2min |
| `PROJECT.md` criado | 14:35 | 5min |
| `REQUIREMENTS.md` criado | 14:38 | 12min |
| `ROADMAP.md` criado | 14:40 | 15min |
| `STATE.md` atualizado | 14:45 | 20min |

**Total Session:** ~20 minutos

---

### ðŸŽ¯ PrÃ³ximas AÃ§Ãµes (Priority Order)

#### Alta Prioridade (Next 24h)
- [ ] **Executar `/gsd:plan-phase 1`** â†’ Criar plano detalhado da Fase 1 com sub-tasks granulares
- [ ] **Configurar ambiente PostgreSQL** (`docker run -d --name agents-prisma-postgres postgres`)
- [ ] **Instalar CrewAI + dependÃªncias** (`pip install crewai crewai-tools sqlalchemy psycopg2-binary`)

#### MÃ©dia Prioridade (Next 7 dias)
- [ ] Testar conexÃ£o com APIs cientÃ­ficas (PubMed, Scopus)
- [ ] Estruturar diretÃ³rios `src/`, `tests/`, `config/`
- [ ] Iniciar implementaÃ§Ã£o do Agente Orquestrador (`src/agents/orchestrator.py`)

#### Baixa Prioridade (Next 14 dias)
- [ ] Configurar MCP MarkItDown server
- [ ] Criar testes unitÃ¡rios iniciais para pipeline state
- [ ] DocumentaÃ§Ã£o tÃ©cnica inicial (README.md)

---

## ðŸ“ Notas de SessÃ£o (Freeform Context)

### ObservaÃ§Ãµes Importantes

1. **Agente Fluxograma PRISMA adicionado** â†’ Expandir pipeline com 6Âº agente (gera Mermaid/Graphviz, exporta PNG/SVG).

2. **CrewAI vs LangGraph** â†’ CrewAI escolhido por simplicidade inicial, mas manter flexibilidade para migrar a grafos de estado complexos se necessÃ¡rio na Fase 3+.

3. **MCP MarkItDown** â†’ Verificar compatibilidade com PDFs cientÃ­ficos (layouts complexos, tabelas, fÃ³rmulas matemÃ¡ticas). Fallback: `pdfplumber` + regex.

4. **API Rate Limits** â†’ Configurar retry logic com backoff exponencial para evitar throttling das APIs cientÃ­ficas.

5. **Checkpointing Strategy** â†’ Salvar estado a cada fase concluÃ­da (JSON no PostgreSQL), nÃ£o apenas apÃ³s erro. Permite reprise granular.

---

### ðŸ” Insights da Pesquisa TÃ©cnica (Preliminar)

*Baseado em pesquisa inicial via Deep Mode (~40 fontes)*

- **CrewAI + LangGraph** â†’ PossÃ­vel integraÃ§Ã£o hÃ­brida: CrewAI para workflow pipeline, LangGraph para estado complexo do fluxograma PRISMA.
- **MCP MarkItDown benchmarks** â†’ 85-92% taxa de conversÃ£o legÃ­vel para PDFs cientÃ­ficos (melhor que PyPDF2).
- **PostgreSQL + SQLAlchemy** â†’ PadrÃ£o ouro para persistÃªncia relacional em projetos Python de mÃ©dio/alto escala.

---

## ðŸ”„ AtualizaÃ§Ã£o de Estado (Auto-Update)

*Este seÃ§Ã£o Ã© atualizada automaticamente a cada sessÃ£o ativa do projeto.*

| Campo | Valor Antigo | Novo Valor | Timestamp |
|-------|--------------|------------|-----------|
| `phases[1].status` | â³ Pendente | ðŸŸ¡ Em andamento | 28/06/2026 14:35 |
| `artifacts.PROJECT.md` | - | âœ… Criado | 28/06/2026 14:35 |
| `artifacts.REQUIREMENTS.md` | - | âœ… Criado | 28/06/2026 14:38 |
| `artifacts.ROADMAP.md` | - | âœ… Criado | 28/06/2026 14:40 |

---

*Documento gerado via `/gsd:new-project` com skill `gsd-new-project`*  
*Documento gerado via /gsd:new-project com skill gsd-new-project*
*Atualizado automaticamente: 28/06/2026 17:55 UTC (Phase 1.1 setup complete)*
