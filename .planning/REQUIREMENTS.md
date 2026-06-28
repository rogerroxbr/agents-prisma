# 📋 Requisitos Detalhados - Agents-Prisma

## Visão Geral dos Requisitos

Este documento detalha os requisitos funcionais, não-funcionais e de qualidade para cada componente do sistema multi-agentes PRISMA.

---

## 1. Requisitos por Agente

### 1.1 Agente Orquestrador (Core)

| ID | Tipo | Descrição | Prioridade |
|----|------|-----------|------------|
| REQ-ORC-01 | Funcional | Gerenciar estado do pipeline PRISMA (4 fases sequenciais) | Alta |
| REQ-ORC-02 | Funcional | Roteamento condicional entre agentes baseado em critérios | Alta |
| REQ-ORC-03 | Não-Funcional | Tempo de decisão < 50ms por transição de fase | Média |
| REQ-ORC-04 | Funcional | Persistência de estado (checkpointing) para reprise após falha | Alta |
| REQ-ORC-05 | Funcional | Logging estruturado JSON de todas as transições | Alta |

#### Sub-requisitos de Estado

```yaml
Pipeline State:
  phases:
    - name: identification
      status: pending/running/completed/error
      artifacts: []
    - name: screening
      status: pending/running/completed/error
      artifacts: []
    - name: eligibility
      status: pending/running/completed/error
      artifacts: []
    - name: synthesis
      status: pending/running/completed/error
      artifacts: []
  
  metadata:
    created_at: ISO8601
    last_updated: ISO8601
    total_articles: int
    included_articles: int
    excluded_articles: int
```

---

### 1.2 Agente de Busca (Fase 1 - Identificação)

| ID | Tipo | Descrição | Prioridade |
|----|------|-----------|------------|
| REQ-BUS-01 | Funcional | Buscar PubMed/Medline via EMBASE API REST | Alta |
| REQ-BUS-02 | Funcional | Buscar Scopus/Web of Science via APIs oficiais | Alta |
| REQ-BUS-03 | Funcional | Buscar Google Scholar via scraping ou API (se disponível) | Média |
| REQ-BUS-04 | Não-Funcional | Suportar queries booleanas complexas (AND, OR, NOT, parentheses) | Alta |
| REQ-BUS-05 | Funcional | Extrair metadados mínimos: DOI, título, autores, ano, periódico | Alta |
| REQ-BUS-06 | Não-Funcional | Retornar máximo 1.000 resultados por base (configurável) | Média |

#### Formato de Saída (Metadados)

```json
{
  "source": "pubmed/scopus/web_of_science/google_scholar",
  "query": "diabetes AND complications",
  "metadata": {
    "doi": "10.xxxx/xxxxx",
    "title": "String completa",
    "authors": ["string"],
    "year": 2024,
    "journal": "string",
    "volume": "int",
    "pages": "string"
  },
  "abstract": "Texto completo do resumo (para fase de triagem)",
  "pdf_url": "URL do PDF oficial ou local_path"
}
```

---

### 1.3 Agente de Triagem (Fase 2)

| ID | Tipo | Descrição | Prioridade |
|----|------|-----------|------------|
| REQ-SCR-01 | Funcional | Ler títulos e resumos dos artigos da Fase 1 | Alta |
| REQ-SCR-02 | Funcional | Aplicar critérios de exclusão rápida (ex: revisão sistemática, metanálise) | Alta |
| REQ-SCR-03 | Funcional | Aplicar critérios de inclusão temática (ex: doença X, intervenção Y) | Alta |
| REQ-SCR-04 | Não-Funcional | Suportar critérios JSON personalizáveis por projeto | Média |
| REQ-SCR-05 | Funcional | Classificar cada artigo como `include`, `exclude` ou `maybe` (triagem manual) | Alta |

#### Critérios Configuráveis (JSON Schema)

```json
{
  "exclusion_criteria": {
    "study_type": ["systematic_review", "meta_analysis", "editorial"],
    "language": ["pt-br", "es", "fr"]
  },
  "inclusion_criteria": {
    "population_keywords": ["diabetes", "hypertension"],
    "intervention_keywords": ["metformin", "lifestyle"],
    "outcome_keywords": ["mortality", "complications"]
  }
}
```

#### Formato de Saída (Triagem)

```json
{
  "article_id": "uuid",
  "decision": "include/exclude/maybe",
  "reason": "Texto justificativo",
  "criteria_matched": ["keyword1", "keyword2"],
  "phase_3_candidates": true/false
}
```

---

### 1.4 Agente Leitor Profundo (Fase 3 - Elegibilidade)

| ID | Tipo | Descrição | Prioridade |
|----|------|-----------|------------|
| REQ-READ-01 | Funcional | Baixar PDFs dos artigos classificados como `include` ou `maybe` na triagem | Alta |
| REQ-READ-02 | Funcional | Converter PDF → Markdown estruturado via MCP MarkItDown | Alta |
| REQ-READ-03 | Funcional | Extrair dados estruturados (PICO: Population, Intervention, Comparison, Outcome) | Alta |
| REQ-READ-04 | Não-Funcional | Lidar com fallback para PDFs corrompidos ou layouts complexos | Média |
| REQ-READ-05 | Funcional | Validar qualidade da extração (texto legível > 80%) | Alta |

#### Fluxo de Extração com MCP

```mermaid
graph LR
    A[PDF Download] --> B{Validar arquivo?}
    B -- Sim --> C[MCP MarkItDown]
    B -- Não --> D[Fallback: regex/text extraction]
    C --> E[Markdown Estruturado]
    D --> E
```

#### Formato de Saída (Dados Estruturados)

```json
{
  "article_id": "uuid",
  "pico": {
    "population": ["string"],
    "intervention": ["string"],
    "comparison": ["string"],
    "outcome": ["string"]
  },
  "risk_of_bias": {
    "selection": "low/unclear/high",
    "confounding": "low/unclear/high"
  },
  "quality_score": float,
  "full_text_summary": "Texto resumido da análise"
}
```

---

### 1.5 Agente Síntese (Fase 4 - Inclusão/Síntese)

| ID | Tipo | Descrição | Prioridade |
|----|------|-----------|------------|
| REQ-SYN-01 | Funcional | Consolidar dados de todos os artigos elegíveis em tabela Markdown | Alta |
| REQ-SYN-02 | Não-Funcional | Formatação compatível com Obsidian/Notion (headers, tabelas, links) | Média |
| REQ-SYN-03 | Funcional | Gerar JSON exportável para consumo downstream (ex: R, Python statsmodels) | Alta |
| REQ-SYN-04 | Não-Funcional | Suportar múltiplos idiomas de saída (en/es/fr/de) | Baixa |

#### Formato de Saída (Markdown - Obsidian Ready)

```markdown
# Revisão Sistemática: Diabetes Mellitus Tipo 2

## Métodos

**Bases de Dados:** PubMed, Scopus, Web of Science, Google Scholar  
**Período:** 2014-2024  
**Linguagem:** Inglês, Espanhol  

**Critérios de Inclusão:**
- Population: Adultos com DM2 (≥18 anos)
- Intervention: Metformina
- Outcome: Mortallidade ou complicações

## Resultados

| Autor | Ano | N | PICO Summary | Risk of Bias |
|-------|-----|---|--------------|--------------|
| Smith et al. | 2023 | 1,250 | Metformina vs placebo → redução mortalidade | Low |
| ... | ... | ... | ... | ... |

## Fluxograma PRISMA

![[PRISMA_Flowchart_Diabetes.png]]

## Dados Exportáveis

\`\`\`json
{
  "total_included": 15,
  "articles": [
    {
      "author": "...",
      "year": ...,
      "pico": {...}
    }
  ]
}
\`\`\`

---
*Gerado automaticamente via Agents-Prisma • Data: YYYY-MM-DD*
```

---

### 1.6 Agente Fluxograma PRISMA (Pós-processamento)

| ID | Tipo | Descrição | Prioridade |
|----|------|-----------|------------|
| REQ-FLOW-01 | Funcional | Gerar fluxograma Mermaid/Graphviz baseado nos dados de triagem | Alta |
| REQ-FLOW-02 | Funcional | Exportar para PNG/SVG via biblioteca (ex: `graphviz`, `mermaid.js`) | Média |
| REQ-FLOW-03 | Não-Funcional | Suportar fluxogramas até 1.000 artigos (performance otimizada) | Baixa |

#### Formato de Saída (Mermaid)

```mermaid
flowchart TD
    Start[Start] --> Search{Search Databases}
    Search --> ID["Identified: N"]
    ID --> Screen[Screening Titles/Abstracts]
    Screen --> Dupl{"Duplicate?"}
    Dupl -- Yes --> Exclude1["Excluded: Duplicate (N)"]
    Dupl -- No --> IncExc["Inclusion/Exclusion Criteria"]
    
    IncExc --> Inc["Included: N"]
    IncExc --> Exc1["Excluded: N"]
    
    Inc --> Elig[Full-Text Review]
    Elig --> Eligible["Eligible: N"]
    Elig --> Excl2["Excluded: N (reason)"]
    
    style ID fill:#ff9999,stroke:#333
    style Screen fill:#ffffcc,stroke:#333
```

---

## 2. Requisitos de Persistência (PostgreSQL)

### 2.1 Esquema de Tabelas

| Tabela | Propósito | Campos Principais |
|--------|-----------|-------------------|
| `projects` | Controle de projetos revisões | id, name, created_at, status |
| `phases` | Estado por fase PRISMA | project_id, phase_name, status, artifacts_json |
| `articles` | Metadados dos artigos buscados | id, project_id, source, doi, title, authors, year, abstract, pdf_url |
| `screening_results` | Resultados de triagem | article_id, decision (include/exclude/maybe), reason, criteria_matched |
| `eligibility_data` | Dados estruturados da leitura profunda | article_id, pico_json, risk_of_bias_json, quality_score |
| `synthesis_output` | Saída final consolidada | project_id, markdown_content, json_export_url, created_at |

### 2.2 Relações e Constraints

```sql
-- Exemplo: Tabela artigos (normalizada)
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    
    -- Metadados básicos
    source VARCHAR(50) NOT NULL,  -- pubmed/scopus/etc.
    doi VARCHAR(255) UNIQUE,
    title TEXT NOT NULL,
    authors JSONB,  -- Array de strings
    
    -- Dados temporais e bibliográficos
    year INT CHECK (year BETWEEN 1900 AND 2099),
    journal VARCHAR(255),
    volume INT,
    pages VARCHAR(100),
    
    -- Links para conteúdo
    abstract TEXT,
    pdf_url TEXT,  -- URL oficial ou path local
    
    -- Status de processamento
    screening_decision VARCHAR(20) CHECK (screening_decision IN ('include', 'exclude', 'maybe')),
    eligibility_status VARCHAR(50) DEFAULT 'pending',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes para performance
CREATE INDEX idx_articles_project ON articles(project_id);
CREATE INDEX idx_articles_doi ON articles(doi);
CREATE INDEX idx_articles_screening ON articles(screening_decision);
```

---

## 3. Requisitos Não-Funcionais Globais

### 3.1 Performance

| Métrica | Meta | Contexto |
|---------|------|----------|
| Tempo de busca (PubMed) | < 2s para 1.000 resultados | API REST oficial |
| Tempo de triagem (500 artigos) | < 60s total | Batch processamento |
| Tempo de extração PDF (30 páginas) | < 10s via MarkItDown | CPU single-threaded |
| Tempo de síntese final | < 5s para projeto completo | Memory optimization |

### 3.2 Confiabilidade

- **Retry Logic:** Máximo 3 tentativas com backoff exponencial (para APIs externas)
- **Fallback Chains:** MCP → Filesystem → Regex extraction
- **Checkpointing:** Estado salvo a cada fase concluída (reprise após falha)
- **Logging:** Nível INFO padrão, DEBUG opcional para debugging

### 3.3 Escalabilidade

| Cenário | Meta |
|---------|------|
| Projetos paralelos | Máximo 10 projetos simultâneos |
| Artigos por projeto | Até 5.000 artigos (batched processamento) |
| Memória RAM | < 2GB por instância de agente |

---

## 4. Requisitos de Integração Externa

### 4.1 APIs das Bases Científicas

| Base | Endpoint | Autenticação | Rate Limit |
|------|----------|--------------|------------|
| PubMed | `https://eutils.ncbi.nlm.nih.gov/efetch` | API Key opcional (NCBI) | ~30 req/min |
| Scopus | `https://dev.api.elsevier.com/v2/search/articles` | API Key + Client ID | 100 req/min |
| Web of Science | `https://api.clarivate.com/wos/v2/articles` | API Key + Client ID | 60 req/min |
| Google Scholar | Scraping/Custom API | N/A | ~30 req/min |

### 4.2 MCP Servers Externos

| MCP Server | Função | Configuração |
|------------|--------|--------------|
| MarkItDown | PDF → Markdown | `markitdown://convert` |
| Filesystem | Arquivos locais | `filesystem://read/write` |
| GitHub/GitLab | Repositórios de código (opcional) | `github://repo`, `gitlab://project` |

---

## 5. Requisitos de UX/Interatividade (Fase 4 - Extensão)

### 5.1 Interface Humana-Computador

| ID | Tipo | Descrição | Prioridade |
|----|------|-----------|------------|
| REQ-UX-01 | Funcional | CLI interativa para definir queries e critérios | Média |
| REQ-UX-02 | Não-Funcional | Progresso em tempo real (percentual por fase) | Média |
| REQ-UX-03 | Funcional | Webhook/API para integração com Notion/Obsidian Sync | Baixa |

### 5.2 API REST (Fase 4 - Extensão)

```yaml
Base: https://api.agents-prisma.com/v1

Endpoints:
  POST /projects/{id}/run          # Iniciar pipeline PRISMA completo
  GET  /projects/{id}/status       # Status atual por fase
  GET  /projects/{id}/export/markdown  # Download Markdown
  GET  /projects/{id}/export/json   # Download JSON estruturado
```

---

## 6. Requisitos de Teste e Validação

| ID | Tipo | Descrição | Critério de Aceite |
|----|------|-----------|-------------------|
| REQ-TEST-01 | Funcional | Agente Orquestrador completa pipeline sequencial | 4 fases concluídas sem erro |
| REQ-TEST-02 | Funcional | Agente Busca retorna metadados válidos para PubMed/Scopus | ≥95% campos preenchidos |
| REQ-TEST-03 | Funcional | Agente Triagem classifica corretamente com critérios JSON | 100% alinhamento manual |
| REQ-TEST-04 | Funcional | MCP MarkItDown converte PDFs legíveis >80% | Texto extraído >500 palavras |
| REQ-TEST-05 | Não-Funcional | Reprise após falha no meio do pipeline | Estado recomeça da fase anterior |

---

## 7. Critérios de Sucesso (Go/No-Go para Fase 1)

### 7.1 MVP (Mínimo Produto Viável)

✅ **Fase 1 aprovada se:**
- [ ] Agente Orquestrador gerencia estado das 4 fases sequencialmente
- [ ] Agente Busca extrai metadados de PubMed/Scopus com sucesso
- [ ] Persistência PostgreSQL salva e recupera estado corretamente
- [ ] Logging JSON estruturado para todas as transições

### 7.2 Core Completo (Fase 1 + 2)

✅ **Core aprovado se:**
- [ ] Todos os requisitos funcionais acima atendidos
- [ ] Agente Triagem classifica ≥90% dos artigos corretamente
- [ ] MCP MarkItDown converte PDFs com qualidade aceitável
- [ ] Reprise após falha funciona sem perda de dados

---

*Documento gerado via `/gsd:new-project` com skill `gsd-new-project`*