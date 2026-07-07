"""LLM Module - LangChain-style base and LM Studio wrapper."""
from src.llm.base import BaseLLM
from src.llm.lmstudio import LMStudio


__all__ = ["BaseLLM", "LMStudio"]
