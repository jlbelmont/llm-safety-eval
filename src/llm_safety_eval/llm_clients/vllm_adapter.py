from __future__ import annotations

from typing import Any, Dict
import httpx

from .base import GenerationResult, LLMClient, allow_network, require_network
from ..data_models import ModelConfig, ProviderConfig


class VLLMClient(LLMClient):
    """vLLM OpenAI-compatible route with opt-in execution guard."""

    def __init__(self, model_config: ModelConfig, provider_config: ProviderConfig) -> None:
        super().__init__(model_config, provider_config)

    def generate(self, prompt: str, parameters: Dict[str, Any], execute: bool = False) -> GenerationResult:
        if not (execute and allow_network()):
            text = f"[vLLM stub for {self.model_name}]"
            return GenerationResult(text=text, latency_ms=None, raw={"prompt": prompt, "params": parameters})

        require_network(execute)
        self._respect_rate_limit()
        payload = {"model": self.model_name, "messages": [{"role": "user", "content": prompt}], **parameters}
        with httpx.Client(timeout=self._timeout_seconds(20.0)) as client:
            resp = client.post(f"{self.provider_config.base_url}/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            latency = resp.elapsed.total_seconds() * 1000
            return GenerationResult(text=text, latency_ms=latency, raw=data)
