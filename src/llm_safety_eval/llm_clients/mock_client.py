from __future__ import annotations

from typing import Any, Dict

from .base import GenerationResult, LLMClient
from ..data_models import ModelConfig, ProviderConfig


class MockClient(LLMClient):
    """Deterministic mock client for tests and dry runs."""

    def __init__(self, model_config: ModelConfig, provider_config: ProviderConfig) -> None:
        super().__init__(model_config, provider_config)

    def generate(self, prompt: str, parameters: Dict[str, Any], execute: bool = False) -> GenerationResult:
        text = f"[mock response for {self.model_name}]"
        return GenerationResult(text=text, latency_ms=0.0, raw={"prompt": prompt, "params": parameters})
