"""Screening agent for LLM-based article filtering."""
import json
import os
from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# Pydantic schema for Structured Output
class PICOExtracted(BaseModel):
    population: str = Field(description="The patient population or problem described in the abstract.")
    intervention: str = Field(description="The intervention, treatment, or exposure being studied.")
    comparison: str = Field(description="The control or comparison group, if any.")
    outcome: str = Field(description="The main outcomes measured in the study.")

class ScreeningDecision(BaseModel):
    decision: Literal['include', 'exclude'] = Field(description="Whether to include or exclude the article based on criteria.")
    reason: str = Field(description="A short justification for the decision.")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0 for this decision.")
    extracted_pico: Optional[PICOExtracted] = Field(description="The extracted PICO elements, if applicable.")


class ScreeningAgent:
    """LLM-based screening agent with PICO extraction and keyword validation."""
    
    def __init__(self, model_name: str = "local-model", temperature: float = 0.0):
        self.criteria = {}
        self.load_criteria()
        
        # Configure local LM Studio server
        # Typically runs on localhost:1234
        api_base = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")
        api_key = os.getenv("OPENAI_API_KEY", "lm-studio")
        
        # Initialize the Chat model
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url=api_base,
        )
        
        # We bind the LLM to return our structured schema
        self.structured_llm = self.llm.with_structured_output(ScreeningDecision)

    def load_criteria(self, criteria_file: str = ".planning/prisma_criteria.json"):
        """Load PRISMA criteria from JSON file."""
        try:
            with open(criteria_file, 'r') as f:
                self.criteria = json.load(f)
            print(f"[SCREENING] Loaded criteria from {criteria_file}")
        except FileNotFoundError:
            print("[SCREENING] Criteria file not found, using default template")
            self.criteria = {
                "inclusion_criteria": ["Relevant disease", "Human subjects"],
                "exclusion_criteria": ["Animal studies", "Review articles"]
            }
            
    def _build_prompt(self, article: Dict[str, Any]) -> str:
        title = article.get("title", "No Title")
        abstract = article.get("abstract", "No Abstract")
        
        # Get inclusion/exclusion from PRISMA criteria JSON structure
        screening_criteria = self.criteria.get("stages", {}).get("screening", {})
        inclusion_list = screening_criteria.get("inclusion_criteria", self.criteria.get("inclusion_criteria", []))
        exclusion_list = screening_criteria.get("exclusion_criteria", self.criteria.get("exclusion_criteria", []))
        
        inclusion = "\n- ".join(inclusion_list)
        exclusion = "\n- ".join(exclusion_list)
        
        prompt = f"""
You are an expert medical researcher performing a systematic review screening.
Evaluate the following article based on the inclusion and exclusion criteria.

INCLUSION CRITERIA:
- {inclusion}

EXCLUSION CRITERIA:
- {exclusion}

ARTICLE TO EVALUATE:
Title: {title}
Abstract: {abstract}

Task:
1. Extract the PICO (Population, Intervention, Comparison, Outcome) elements from the abstract.
2. Decide whether to 'include' or 'exclude' this article based on the criteria.
3. Provide a brief reason for your decision.
4. Assign a confidence score (0.0 to 1.0).
"""
        return prompt

    def _evaluate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate single article against screening criteria using LLM."""
        prompt_text = self._build_prompt(article)
        
        try:
            # Call the LLM
            decision: ScreeningDecision = self.structured_llm.invoke(prompt_text)
            
            pico_dict = None
            if decision.extracted_pico:
                pico_dict = decision.extracted_pico.model_dump()
                
            return {
                "decision": decision.decision,
                "reason": decision.reason,
                "score": decision.confidence_score,
                "pico_extracted": pico_dict
            }
        except Exception as e:
            # Fallback in case LLM fails or LM Studio is offline
            print(f"[SCREENING] LLM Error evaluating article '{article.get('title')[:30]}...': {e}")
            return self._fallback_evaluate_article(article)
            
    def _fallback_evaluate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Simple keyword-based fallback if LLM fails."""
        title = article.get("title", "").lower()
        
        exclude_keywords = ["review", "meta-analysis", "meta analysis", "editorial", "animal"]
        if any(kw in title for kw in exclude_keywords):
            return {"decision": "exclude", "reason": "Fallback: Exclusion keyword in title", "score": 0.1, "pico_extracted": None}
            
        return {"decision": "include", "reason": "Fallback: Default include", "score": 0.5, "pico_extracted": None}
    
    def screen_batch(
        self, 
        articles: List[Dict[str, Any]],
        batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """Screen a batch of articles using LLM-based filtering."""
        print(f"[SCREENING] Screening batch of {min(len(articles), batch_size)} articles with LLM...")
        
        screened = []
        
        for article in articles[:batch_size]:
            evaluation = self._evaluate_article(article)
            
            result = {
                "article": article,
                "decision": evaluation["decision"],
                "reason": evaluation["reason"],
                "score": evaluation["score"],
                "pico_extracted": evaluation["pico_extracted"]
            }
            
            screened.append(result)
        
        included = [s for s in screened if s["decision"] == "include"]
        excluded = [s for s in screened if s["decision"] == "exclude"]
        
        print(f"[SCREENING] Batch complete: {len(included)} included, {len(excluded)} excluded")
        
        return included + excluded

__all__ = ["ScreeningAgent", "ScreeningDecision", "PICOExtracted"]
