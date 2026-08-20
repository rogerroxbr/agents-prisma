"""LM Studio Wrapper for LangChain-style integration."""

from src.llm.base import BaseLLM


class LMStudio(BaseLLM):
    """Simple wrapper to connect to LM Studio via litellm."""

    def __init__(self, model: str = "gpt-4o", **kwargs):
        super().__init__(model=model, **kwargs)
