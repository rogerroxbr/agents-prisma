import json
import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class ThemeGroup(BaseModel):
    theme_name: str = Field(
        description="Name of the thematic group (e.g. 'Metformin Efficacy', 'Lifestyle Interventions')"
    )
    description: str = Field(description="A short summary of what this theme covers")
    article_ids: list[str] = Field(
        description="List of article IDs (or DOIs/Titles) belonging to this theme"
    )


class SynthesisResult(BaseModel):
    themes: list[ThemeGroup] = Field(
        description="List of themes discovered from the articles"
    )
    overall_summary: str = Field(
        description="A brief paragraph summarizing the overall findings across all included articles."
    )


class SynthesizerAgent:
    def __init__(self, model_name: str = "local-model", temperature: float = 0.0):
        api_base = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")
        api_key = os.getenv("OPENAI_API_KEY", "lm-studio")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url=api_base,
        )
        self.structured_llm = self.llm.with_structured_output(SynthesisResult)

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert academic researcher synthesizing a systematic review.
You will be provided with a list of included articles, their metadata, and their extracted PICO (Population, Intervention, Comparison, Outcome) data.
Your task is to:
1. Identify common themes among the articles (e.g., specific interventions, similar outcomes, or distinct populations).
2. Group the articles by these themes. An article can belong to more than one theme.
3. Provide a brief overall summary of the findings across all articles.

Output your results strictly following the requested schema.
""",
                ),
                ("user", "Here are the articles to synthesize:\n{articles_json}"),
            ]
        )

        self.chain = self.prompt | self.structured_llm

    def synthesize(self, eligible_articles: list[dict[str, Any]]) -> SynthesisResult:
        """
        Synthesizes the eligible articles into thematic groups.
        """
        if not eligible_articles:
            return SynthesisResult(
                themes=[],
                overall_summary="No eligible articles were provided for synthesis.",
            )

        # Prepare the data for the LLM
        articles_for_prompt = []
        for art in eligible_articles:
            extracted = art.get("extracted_data", {})
            articles_for_prompt.append(
                {
                    "id": art.get("id")
                    or art.get("doi")
                    or art.get("title", "Unknown"),
                    "title": art.get("title", "No Title"),
                    "pico": extracted.get("pico", {}),
                    "risk_of_bias": extracted.get("risk_of_bias", {}),
                }
            )

        articles_json = json.dumps(articles_for_prompt, indent=2)

        # Invoke the chain
        try:
            result = self.chain.invoke({"articles_json": articles_json})
            return result
        except Exception as e:
            # Fallback in case of LLM/parsing failure
            return SynthesisResult(
                themes=[
                    ThemeGroup(
                        theme_name="General",
                        description="Fallback group due to synthesis error.",
                        article_ids=[
                            str(
                                a.get("id") or a.get("doi") or a.get("title", "Unknown")
                            )
                            for a in eligible_articles
                        ],
                    )
                ],
                overall_summary=f"Failed to synthesize automatically. Error: {e!s}",
            )

    def generate_markdown_report(
        self,
        eligible_articles: list[dict[str, Any]],
        synthesis: SynthesisResult,
        project_metadata: dict[str, Any] = None,
    ) -> str:
        """
        Generates a Markdown report from the synthesized data, compatible with Obsidian.
        """
        project_name = "Revisão Sistemática"
        if project_metadata and "name" in project_metadata:
            project_name = project_metadata["name"]

        md_lines = []
        md_lines.append(f"# {project_name}\n")

        md_lines.append("## Resumo Geral\n")
        md_lines.append(f"{synthesis.overall_summary}\n")

        md_lines.append("## Temas Descobertos\n")
        if not synthesis.themes:
            md_lines.append("Nenhum tema identificado.\n")

        for theme in synthesis.themes:
            md_lines.append(f"### {theme.theme_name}")
            md_lines.append(f"**Descrição:** {theme.description}")
            md_lines.append(f"**Artigos:** {', '.join(theme.article_ids)}\n")

        md_lines.append("## Tabela PICO Consolidada\n")

        # Markdown table header
        md_lines.append(
            "| ID / Título | População | Intervenção | Comparação | Desfecho | Risco de Viés |"
        )
        md_lines.append("|---|---|---|---|---|---|")

        for art in eligible_articles:
            art_id = art.get("id") or art.get("doi") or art.get("title", "Unknown")
            extracted = art.get("extracted_data", {})
            pico = extracted.get("pico", {})
            rob = extracted.get("risk_of_bias", {})

            # Helper to join lists into strings or handle dicts
            def format_cell(data):
                if isinstance(data, list):
                    return ", ".join(str(d) for d in data)
                return str(data) if data else "-"

            population = format_cell(pico.get("population", []))
            intervention = format_cell(pico.get("intervention", []))
            comparison = format_cell(pico.get("comparison", []))
            outcome = format_cell(pico.get("outcome", []))

            rob_str = []
            if isinstance(rob, dict):
                for k, v in rob.items():
                    rob_str.append(f"{k}: {v}")
            elif isinstance(rob, str):
                rob_str.append(f"Erro/Texto: {rob}")
            
            risk_of_bias = ", ".join(rob_str) if rob_str else "-"

            # Clean up newlines for the table row
            row = [
                str(art_id).replace("|", "\\|").replace("\n", " "),
                population.replace("|", "\\|").replace("\n", " "),
                intervention.replace("|", "\\|").replace("\n", " "),
                comparison.replace("|", "\\|").replace("\n", " "),
                outcome.replace("|", "\\|").replace("\n", " "),
                risk_of_bias.replace("|", "\\|").replace("\n", " "),
            ]
            md_lines.append(f"| {' | '.join(row)} |")

        md_lines.append("\n---\n*Gerado automaticamente pelo Agents-Prisma*")

        return "\n".join(md_lines)
