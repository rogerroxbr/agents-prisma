"""LangChain LLM Base - Replace CrewAI's BaseLLM."""
from typing import Any, Dict, List, Optional


class BaseLLM:
    """Base LLM class for LangChain-style integration."""
    
    def __init__(
        self, 
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ):
        self.model = model
        self.base_url = base_url or "http://127.0.0.1:1234"
        self.api_key = api_key or "lm-studio-test-key"
        self.temperature = temperature
    
    def call(self, messages: List[Dict[str, Any]]) -> str:
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
