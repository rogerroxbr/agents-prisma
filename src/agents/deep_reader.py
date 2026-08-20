"""Deep Reader Agent for full-text extraction and analysis."""

import logging
import os
import time
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DeepExtractionResult(BaseModel):
    """Detailed PICO extraction and Risk of Bias evaluation from full text."""

    population: str = Field(
        description="Detailed description of the study population (e.g., sample size, age, condition)."
    )
    intervention: str = Field(
        description="Detailed description of the intervention/exposure."
    )
    comparison: str = Field(
        description="Detailed description of the control/comparison group."
    )
    outcome: str = Field(
        description="Detailed description of the primary and secondary outcomes measured, including results."
    )
    risk_of_bias: str = Field(
        description="Evaluation of the study's risk of bias (e.g., high, low, some concerns) and reasons."
    )
    methodology: str = Field(description="Study design and methodology details.")
    confidence_score: float = Field(
        description="Confidence score in the extraction quality from 0.0 to 1.0."
    )


class DeepReaderAgent:
    """Agent responsible for analyzing the full markdown text of an article."""

    def __init__(self, model_name: str = "local-model", temperature: float = 0.0):
        # Default to local LM Studio
        api_base = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")
        api_key = os.getenv("OPENAI_API_KEY", "lm-studio")

        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url=api_base,
        )

        self.structured_llm = self.llm.with_structured_output(DeepExtractionResult)

    def _build_prompt(self, article_title: str, markdown_text: str) -> str:
        """Build the extraction prompt."""
        # Truncate markdown if it's too long to avoid token limits in local models
        # Assuming around 8000 tokens limit for local models, 30000 chars is safe
        if len(markdown_text) > 30000:
            markdown_text = markdown_text[:30000] + "\n...[CONTENT TRUNCATED]..."

        return f"""
You are an expert academic researcher. Your task is to perform a deep reading and extraction of the following academic article.
Extract detailed PICO elements (Population, Intervention, Comparison, Outcome), assess the Risk of Bias, and summarize the methodology.

Article Title: {article_title}

Full Text (Markdown format):
==================================================
{markdown_text}
==================================================

Please analyze the text and extract the required structured information.
"""

    def analyze_article(
        self, article_metadata: dict[str, Any], markdown_text: str, retries: int = 2
    ) -> dict[str, Any]:
        """Analyze the full markdown text of an article with retry logic."""
        title = article_metadata.get("title", "Unknown Title")
        prompt = self._build_prompt(title, markdown_text)

        logger.info(f"[DEEP_READER] Analyzing full text for: {title[:50]}...")
        
        for attempt in range(retries):
            try:
                result = self.structured_llm.invoke(prompt)
                return {
                    "population": result.population,
                    "intervention": result.intervention,
                    "comparator": result.comparison,
                    "outcome": result.outcome,
                    "risk_of_bias": result.risk_of_bias,
                    "methodology": result.methodology,
                    "confidence": result.confidence_score,
                    "markdown": markdown_text,
                }
            except Exception as e:
                logger.warning(f"[DEEP_READER] Error during LLM extraction (attempt {attempt + 1}/{retries}): {e}")
                time.sleep(1)
        
        logger.error(f"[DEEP_READER] Failed to extract details for {title[:50]} after {retries} attempts.")
        # Fallback response
        return {
            "population": "Error during extraction",
            "intervention": "Error during extraction",
            "comparator": "Error during extraction",
            "outcome": "Error during extraction",
            "risk_of_bias": "Unknown",
            "methodology": "Unknown",
            "confidence": 0.0,
            "markdown": markdown_text,
        }
