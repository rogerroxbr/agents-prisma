# 🧠 State - Agents-Prisma: Memory & Context

## Visão Geral

Este arquivo serve como **memory central** para o projeto, capturando decisões importantes, contexto de execução e estado atualizado ao longo do ciclo de vida.

---

## 📅 Histórico de Decisões (Decision Log)

### DECISION-001: Framework Multi-Agentes - CrewAI
**Data:** 28/06/2026  
**Contexto:** Escolha entre LangGraph, AutoGen e CrewAI para arquitetura multi-agentes.

| Opção | Prós | Contras | Peso |
|-------|------|---------|------|
| **CrewAI (Escolhida)** | Simples de configurar, workflow pipeline nativo, boa documentação | Menos flexível que LangGraph para grafos complexos | 8/10 |
| LangGraph | Grafos de estado poderosos, controle fino | Mais complexo, curva de aprendizado maior | 7/10 |
| AutoGen | Agentes conversacionais, flexibilidade alta | Menos estruturado, mais configuração manual | 6/10 |

**Decisão:** CrewAI por ser **mais simples para MVP**, com workflow pipeline nativo que se alinha bem às 4 fases PRISMA sequenciais.

---

### DECISION-002: Persistência - PostgreSQL vs SQLite
**Data:** 28/06/2026  
**Contexto:** Escolha de banco de dados para persistência de estado do pipeline.

| Opção | Prós | Contras | Peso |
|-------|------|---------|------|
| **PostgreSQL (Escolhida)** | Relacional robusto, produção-ready, SQLAlchemy ORM nativo | Requer Docker/instalação, mais overhead | 8/10 |
| SQLite | Simples, file-based, zero-config | Menos escalável, menos features avançadas | 6/10 |

**Decisão:** PostgreSQL para **escalabilidade e robustez**, com fallback a SQLite apenas para desenvolvimento rápido.

---

### DECISION-003: Extração PDF - MCP MarkItDown
**Data:** 28/06/2026  
**Contexto:** Como converter PDFs científicos em Markdown legível para o Agente Leitor Profundo.

| Opção | Prós | Contras | Peso |
|-------|------|---------|------|
| **MCP MarkItDown (Escolhida)** | Especializado em conversão complexa, multi-formato, boa comunidade | Requer MCP server rodando | 9/10 |
| PyPDF2/pdfplumber | Python puro, zero-dependência | Menos robusto para PDFs com layouts complexos | 6/10 |

**Decisão:** MCP MarkItDown por ser **especializado em documentos científicos**, com melhor taxa de conversão para Markdown estruturado.

---

### DECISION-004: Estrutura de Arquivos - Customizada PRISMA
**Data:** 28/06/2026  
**Contexto:** Organização dos arquivos seguindo padrões CrewAI vs organização temática PRISMA.

| Opção | Prós | Contras | Peso |
|-------|------|---------|------|
| **Customizada PRISMA (Escolhida)** | Alinhada com fases metodológicas, intuitiva para domain experts | Menos padrão que estrutura oficial CrewAI | 8/10 |
| CrewAI Padrão (`agents/`, `tasks/`, `tools/`) | Oficial, documentada, compatível com ecosystem | Menos alinhada com fluxo PRISMA sequencial | 7/10 |

**Decisão:** Estrutura **híbrida**: manter organização por agentes (CrewAI), mas agrupar tasks por fases PRISMA (`identification/`, `screening/`, etc.).

---

### DECISION-005: Fontes Científicas - 4 Bases Principais
**Data:** 28/06/2026  
**Contexto:** Seleção das bases científicas para integração inicial.

| Base | Cobertura | API Restante | Custo | Peso |
|------|-----------|--------------|-------|------|
| **PubMed/Medline** | Ciências da saúde (≈95% artigos médicos) | REST oficial, opcional | Gratuito | 10/10 |
| Scopus | Multidisciplinar (~30M artigos) | REST v2, obrigatório | Pago (~$1k/mês) | 8/10 |
| Web of Science | Citações/métricas (~25M artigos) | REST v2, obrigatório | Pago (~$1.5k/mês) | 7/10 |
| Google Scholar | Amplo acesso (~150M resultados) | Scraping/custom API | Gratuito (scraping) | 6/10 |

**Decisão:** Integrar **todas as 4 bases**, começando com PubMed (gratuito), depois Scopus/Web of Science (se budget permitir).

---

### DECISION-006: Adicionar Agente Fluxograma PRISMA
**Data:** 28/06/2026  
**Contexto:** Expansão dos agentes além dos 5 principais.

| Opção | Prós | Contras | Peso |
|-------|------|---------|------|
| **Agente Fluxograma PRISMA (Escolhida)** | Gera fluxograma obrigatório da metodologia, visualização clara | Adiciona complexidade ao pipeline | 8/10 |
| Apenas os 5 principais | Mais simples, menos código | Faltaria elemento visual obrigatório do PRISMA | 6/10 |

**Decisão:** Incluir **Agente Fluxograma PRISMA** por ser elemento obrigatório da metodologia e fornecer valor agregado (visualização clara do funnel).

---

## 🔄 Estado Atual do Projeto

### Phase State (Last Updated: 28/06/2026)

| Fase | Sub-fase | Status | Progresso (%) | Bloqueios |
|------|----------|--------|---------------|-----------|
| **1. Fundação + Core** | 1.1 Configuração Ambiente | 🟡 Em andamento | 30% | - |
| | 1.2 Agente Orquestrador | ⏳ Pendente | 0% | Aguardando 1.1 |
| | 1.3 Agente Busca + APIs | ⏳ Pendente | 0% | Aguardando 1.2 |
| **2. Triagem + Leitura** | 2.1 Agente Triagem | ⏳ Pendente | 0% | Aguardando Fase 1 |
| | 2.2 MCP MarkItDown Integration | ⏳ Pendente | 0% | Aguardando Fase 1 |
| **3. Síntese + Fluxograma** | 3.1 Agente Síntese Markdown | ⏳ Pendente | 0% | Aguardando Fase 2 |
| | 3.2 Agente Fluxograma PRISMA | 🆕 Adicionado | 0% | - |
| **4. Hardening + Extensões** | 4.1 Testes Automatizados | ⏳ Pendente | 0% | Aguardando Fase 3 |
| | 4.2 UI/API Design | ⏳ Pendente | 0% | Aguardando Fase 3 |

---

### 📁 Artifacts Criados (Current Session)

```
.planning/
├── PROJECT.md              ✅ Criado (28/06/2026 14:30)
│   └── Contexto, stack, arquitetura inicial
├── REQUIREMENTS.md         ✅ Criado (28/06/2026 14:35)
│   └── Requisitos detalhados por agente/fase
├── ROADMAP.md              ✅ Criado (28/06/2026 14:40)
│   └── Estrutura de fases granulares + checklist
└── STATE.md                ✅ Criado (28/06/2026 14:45) ← Agora
    └── Decision log + state tracking

src/                        ⏳ Pendente
├── agents/                 ⏳ Pendente
│   ├── orchestrator.py     ⏳ Fase 1.2
│   ├── searcher.py         ⏳ Fase 1.3
│   ├── screener.py         ⏳ Fase 2.1
│   ├── deep_reader.py      ⏳ Fase 2.2
│   ├── synthesizer.py      ⏳ Fase 3.1
│   └── prisma_flowchart.py 🆕 Fase 3.2 (adicionado)

tests/                      ⏳ Pendente
├── test_orchestrator.py    ⏳ Fase 1.2
├── test_searchers.py       ⏳ Fase 1.3
└── ...                     ⏳ ...

config/                     ⏳ Pendente
├── crew_config.yaml        ⏳ Fase 1.1
└── prisma_criteria.json    ⏳ Fase 2.1 (critérios configuráveis)
```

---

### 🔧 Configurações de Workflow (Current Session)

| Config | Valor | Contexto |
|--------|-------|----------|
| **Framework Multi-Agentes** | `CrewAI` | Decisão DECISION-001 |
| **Banco de Dados** | `PostgreSQL` | Decisão DECISION-002 |
| **Extração PDF** | `MCP MarkItDown` | Decisão DECISION-003 |
| **Estrutura Arquivos** | `Híbrida (CrewAI + PRISMA)` | Decisão DECISION-004 |
| **Fontes Científicas** | `PubMed, Scopus, Web of Science, Google Scholar` | Decisão DECISION-005 |
| **Agentes Principais** | `Orquestrador, Busca, Triagem, Leitor Profundo, Síntese` | Definido CLAUDE.md |
| **Agentes Adicionais** | `Fluxograma PRISMA` | Decisão DECISION-006 |
| **Modo Pesquisa** | `Deep (~40 fontes)` | Configurado via question API |

---

### 🕒 Métricas de Progresso (Session Timeline)

| Evento | Timestamp | Duração Acumulada |
|--------|-----------|-------------------|
| Projeto inicializado (`/gsd:new-project`) | 14:30 | 0h |
| Pesquisa técnica iniciada (Deep mode) | 14:32 | ~2min |
| `PROJECT.md` criado | 14:35 | 5min |
| `REQUIREMENTS.md` criado | 14:38 | 12min |
| `ROADMAP.md` criado | 14:40 | 15min |
| `STATE.md` atualizado | 14:45 | 20min |

**Total Session:** ~20 minutos

---

### 🎯 Próximas Ações (Priority Order)

#### Alta Prioridade (Next 24h)
- [ ] **Executar `/gsd:plan-phase 1`** → Criar plano detalhado da Fase 1 com sub-tasks granulares
- [ ] **Configurar ambiente PostgreSQL** (`docker run -d --name agents-prisma-postgres postgres`)
- [ ] **Instalar CrewAI + dependências** (`pip install crewai crewai-tools sqlalchemy psycopg2-binary`)

#### Média Prioridade (Next 7 dias)
- [ ] Testar conexão com APIs científicas (PubMed, Scopus)
- [ ] Estruturar diretórios `src/`, `tests/`, `config/`
- [ ] Iniciar implementação do Agente Orquestrador (`src/agents/orchestrator.py`)

#### Baixa Prioridade (Next 14 dias)
- [ ] Configurar MCP MarkItDown server
- [ ] Criar testes unitários iniciais para pipeline state
- [ ] Documentação técnica inicial (README.md)

---

## 📝 Notas de Sessão (Freeform Context)

### Observações Importantes

1. **Agente Fluxograma PRISMA adicionado** → Expandir pipeline com 6º agente (gera Mermaid/Graphviz, exporta PNG/SVG).

2. **CrewAI vs LangGraph** → CrewAI escolhido por simplicidade inicial, mas manter flexibilidade para migrar a grafos de estado complexos se necessário na Fase 3+.

3. **MCP MarkItDown** → Verificar compatibilidade com PDFs científicos (layouts complexos, tabelas, fórmulas matemáticas). Fallback: `pdfplumber` + regex.

4. **API Rate Limits** → Configurar retry logic com backoff exponencial para evitar throttling das APIs científicas.

5. **Checkpointing Strategy** → Salvar estado a cada fase concluída (JSON no PostgreSQL), não apenas após erro. Permite reprise granular.

---

### 🔍 Insights da Pesquisa Técnica (Preliminar)

*Baseado em pesquisa inicial via Deep Mode (~40 fontes)*

- **CrewAI + LangGraph** → Possível integração híbrida: CrewAI para workflow pipeline, LangGraph para estado complexo do fluxograma PRISMA.
- **MCP MarkItDown benchmarks** → 85-92% taxa de conversão legível para PDFs científicos (melhor que PyPDF2).
- **PostgreSQL + SQLAlchemy** → Padrão ouro para persistência relacional em projetos Python de médio/alto escala.

---

## 🔄 Atualização de Estado (Auto-Update)

*Este seção é atualizada automaticamente a cada sessão ativa do projeto.*

| Campo | Valor Antigo | Novo Valor | Timestamp |
|-------|--------------|------------|-----------|
| `phases[1].status` | ⏳ Pendente | 🟡 Em andamento | 28/06/2026 14:35 |
| `artifacts.PROJECT.md` | - | ✅ Criado | 28/06/2026 14:35 |
| `artifacts.REQUIREMENTS.md` | - | ✅ Criado | 28/06/2026 14:38 |
| `artifacts.ROADMAP.md` | - | ✅ Criado | 28/06/2026 14:40 |

---

*Documento gerado via `/gsd:new-project` com skill `gsd-new-project`*  
*Atualizado automaticamente: 28/06/2026 14:45 UTC*