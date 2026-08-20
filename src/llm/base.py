"""LangChain LLM Base - Replace CrewAI's BaseLLM."""

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


class BaseLLM:
    """Base LLM class for LangChain-style integration."""

    def __init__(
        self,
        model: str = "gpt-4o",
        base_url: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.7,
        **kwargs,
    ):
        self.model = model
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "lm-studio-test-key")
        self.temperature = temperature

    def call(self, messages: list[dict[str, Any]]) -> str:
        """Call the LLM with a list of message dicts."""
        import litellm

        response = litellm.completion(
            model=self.model,
            provider="lm-studio",
            base_url=self.base_url,
            api_key=self.api_key,
            messages=messages,
            temperature=self.temperature,
        )

        return response.choices[0].message.content or ""
