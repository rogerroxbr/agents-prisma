# Agents-Prisma 🔬🤖

**Agents-Prisma** é um sistema multiagente inteligente construído sobre o [LangGraph](https://python.langchain.com/docs/langgraph) focado na automação de **Revisões Sistemáticas de Literatura** baseadas na metodologia **PRISMA** (Preferred Reporting Items for Systematic Reviews and Meta-Analyses).

O projeto orquestra múltiplos "nós" e subgrafos que atuam de forma paralela e assíncrona para buscar artigos científicos em diversas bases de dados gratuitas, cruzar os dados, remover duplicatas, realizar a triagem (Screening) baseada em LLMs (Modelos de Linguagem) utilizando os critérios PICO (População, Intervenção, Comparação, Desfecho) e, por fim, extrair PDFs em texto puro gerando relatórios ricos em Markdown e JSON estruturado.

---

## 🌟 Principais Recursos (Features)

* **Busca Paralela Gratuita e Aberta**: Orquestração assíncrona de 4 subgrafos acadêmicos poderosos sem a necessidade de chaves de API comerciais fechadas:
  * 🧬 **PubMed** (via E-Utilities / Entrez)
  * 📐 **ArXiv** (focado em Exatas e Computação)
  * 🌐 **OpenAlex** (Catálogo global com mais de 250 milhões de artigos)
  * 🧠 **Semantic Scholar** (Focado em IA e grafos acadêmicos)
* **Triagem com Inteligência Artificial (LLM)**: Utiliza seu modelo de linguagem local (via integração compatível com OpenAI, ex: LM Studio ou Ollama) para classificar os artigos lendo título e resumo, aprovando ou reprovando baseado nos seus critérios (PICO).
* **Obtenção de PDF em Texto**: Usa a ferramenta `MarkItDown` e a API do `Unpaywall` para tentar encontrar versões gratuitas (Open Access) do artigo, baixar o PDF e convertê-lo em Markdown para uso pelo LLM.
* **Saída Pronta para o Obsidian**: Gera arquivos Markdown (`outputs/reports/`) totalmente estruturados, perfeitos para serem jogados no seu cofre do Obsidian ou Notion, juntamente com o arquivo JSON consolidado da revisão.
* **CLI Rápida e API REST**: Você pode rodar a revisão pelo terminal (Typer) ou iniciar o servidor web (FastAPI) para chamadas externas.

---

## 📋 Pré-requisitos

1. **Python 3.12+** instalado.
2. Gerenciador de pacotes **`uv`** da Astral (extremamente rápido e recomendado): `pip install uv`.
3. **LLM Local (LM Studio / Ollama)**: O projeto está configurado para consumir um servidor compatível com OpenAI rodando em `http://localhost:1234/v1`. Baixe o [LM Studio](https://lmstudio.ai), carregue um modelo instrucional leve (como Llama 3 8B Instruct ou similar) e ligue o Servidor Local.

---

## 🚀 Como fazer funcionar (Quick Start)

### 1. Instalação

Faça o clone do repositório e instale as dependências usando o `uv`:

```bash
# Sincroniza e instala todas as dependências no ambiente virtual
uv sync --all-extras
```

### 2. Configurando seus critérios (PICO)

Antes de rodar a busca, edite o arquivo **`config/prisma_criteria.json`** localizado na pasta de configurações. O Agente de Screening (Triagem) vai ler este arquivo para decidir quais artigos incluir na sua revisão:

```json
{
  "inclusion_criteria": [
    "Estudos focados no tratamento de diabetes tipo 2",
    "Estudos com humanos"
  ],
  "exclusion_criteria": [
    "Revisões narrativas",
    "Estudos em ratos/animais"
  ],
  "required_pico": {
    "population": "Adultos com diabetes tipo 2",
    "intervention": "Metformina ou insulina",
    "comparison": "Placebo ou outra droga",
    "outcome": "Redução da HbA1c"
  }
}
```

*(Opcional)* Você pode ajustar o arquivo `.env` para o banco de dados (SQLite ou Postgres). O padrão usará o SQLite na memória do StateGraph.

### 3. Rodando o Pipeline pela CLI (Terminal)

Com o seu LM Studio rodando, execute o comando de busca do CLI:

```bash
uv run python src/cli.py run --query "diabetes treatments" --max-results 10
```

* **`--query`**: O termo de busca que será jogado no PubMed, ArXiv, OpenAlex e Semantic Scholar.
* **`--max-results`**: Limite de quantos artigos ele vai trazer **POR FONTE** (ex: 10 no PubMed + 10 no ArXiv... resultando em até 40 artigos para triar).

### 4. Acompanhando a Execução

Acompanhe os logs no terminal. O pipeline passará pelas seguintes etapas:
1. `[IDENTIFY_NODE]`: Consulta as 4 fontes de dados em paralelo.
2. `[EXTRACT_METADATA]`: Padroniza os retornos num formato único de dicionário.
3. `[SCREENING]`: O LLM entra em ação. Para cada artigo, ele analisará Título e Resumo e dirá se ele atende ao `prisma_criteria.json`.
4. `[SYNTHESIZE]`: Consolida os artigos elegíveis num documento de leitura.

No final, cheque a pasta **`outputs/reports/`**. Você terá um `.md` lindo com os resultados da sua Revisão Sistemática!

---

## 🛠️ Entendendo a Arquitetura (LangGraph)

O fluxo do LangGraph foi modelado mapeando rigorosamente o fluxograma padrão do PRISMA (2020):

```
(START)
   │
   ▼
[Identify Node] (Busca paralela via Subgrafos)
   │
   ▼
[Screening Node] (LLM lê Título/Abstract usando PICO)
   │
   ▼
[Eligibility Node] (Tentativa de PDF Full-Text Fetch via Unpaywall)
   │
   ▼
[Synthesize Node] (Gera o output final MD/JSON)
   │
   ▼
 (END)
```

**Estrutura de Pastas:**
```text
src/
├── agents/
│   ├── orchestrator_langgraph.py  # A raiz onde o fluxo PRISMA é montado
│   ├── screener.py                # Lógica do LangChain conversando com o LLM
│   ├── synthesizer.py             # Classe que escreve o Markdown na pasta outputs
│   ├── nodes/                     # Nós isolados do grafo (Identify, Screen, etc)
│   └── subgraphs/                 # Subgrafos por provedor (PubMed, ArXiv...)
├── tools/                         # Integração com APIs externas HTTP
├── api/                           # Endpoint FastAPI para uso remoto
└── db/                            # Persistência via SQLAlchemy 
```

---

## 🔌 Rodando como um Servidor (REST API)

Se quiser usar o Agents-Prisma como um backend (chamado por uma interface web ou outro sistema), você pode levantar a API FastAPI:

```bash
uv run uvicorn src.api.server:app --reload --port 8000
```

**Disparando uma busca via cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/projects/run" \
     -H "Content-Type: application/json" \
     -d '{"query": "diabetes", "max_results": 10}'
```

Acesse a documentação Swagger interativa em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ⚙️ Dicas Avançadas

* **OpenAlex Politeness**: O OpenAlex é gratuito e aberto, mas se quiser ter requisições ainda mais rápidas na "Polite Pool", você pode definir a variável de ambiente `OPENALEX_EMAIL=seuemail@example.com`.
* **Uso de Modelos Grandes**: Para uma triagem complexa (ex: muitos critérios de exclusão), o desempenho de um Llama 3 8B pode não ser suficiente para entender contextos profundos. Considere apontar a sua base URL no código do `screener.py` para o Ollama (usando `llama3:70b` ou `qwen2.5`) ou, se for rodar na nuvem, usar as credenciais da OpenAI (gpt-4o).
