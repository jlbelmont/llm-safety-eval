from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict
import time
import random

from ..data_models import ModelConfig, ProviderConfig
from ..util.rate_limit import TokenBucket


@dataclass
class GenerationResult:
    text: str
    latency_ms: float | None
    raw: dict[str, Any]


def allow_network() -> bool:
    """Check env guard for network calls."""

    return os.getenv("LSE_ALLOW_NETWORK", "0") == "1"


def require_network(execute: bool) -> None:
    if execute and not allow_network():
        raise RuntimeError(
            "Network execution requested but LSE_ALLOW_NETWORK!=1. Set env var to opt-in."
        )


class LLMClient:
    """Abstract client interface."""

    def __init__(self, model_config: ModelConfig, provider_config: ProviderConfig) -> None:
        self.model_config = model_config
        self.provider_config = provider_config
        self._last_request_ts: float | None = None
        self._bucket = (
            TokenBucket.create(self.provider_config.max_requests_per_minute)
            if self.provider_config.max_requests_per_minute
            else None
        )

    @property
    def model_name(self) -> str:
        return self.model_config.model_name

    def generate(
        self, prompt: str, parameters: Dict[str, Any], execute: bool = False
    ) -> GenerationResult:  # pragma: no cover - interface
        raise NotImplementedError

    def _timeout_seconds(self, default: float) -> float:
        if self.provider_config.timeout_seconds is not None:
            return float(self.provider_config.timeout_seconds)
        extra_timeout = self.provider_config.extra.get("timeout_seconds")
        if extra_timeout is not None:
            return float(extra_timeout)
        return default

    def _respect_rate_limit(self) -> None:
        """Simple polite backoff using provider backoff_seconds."""

        backoff = self.provider_config.backoff_seconds or 0.0
        if backoff > 0:
            if self._last_request_ts is not None:
                elapsed = time.time() - self._last_request_ts
                if elapsed < backoff:
                    time.sleep(backoff - elapsed + random.random() * 0.05)
        self._last_request_ts = time.time()
        if self._bucket:
            wait = self._bucket.consume()
            if wait > 0:
                time.sleep(wait)


class ClientRegistry:
    """Registry mapping model_id to instantiated clients."""

    def __init__(self, models: dict[str, ModelConfig], clients: dict[str, LLMClient]) -> None:
        self._models = models
        self._clients = clients

    def get_client(self, model_id: str) -> LLMClient:
        return self._clients[model_id]

    def get_model_config(self, model_id: str) -> ModelConfig:
        return self._models[model_id]

    @classmethod
    def from_configs(
        cls, models_cfg: list[dict[str, Any]], providers_cfg: list[dict[str, Any]]
    ) -> "ClientRegistry":
        models: dict[str, ModelConfig] = {
            m["model_id"]: ModelConfig(**m) for m in models_cfg
        }
        providers: dict[str, ProviderConfig] = {
            p["provider_id"]: ProviderConfig(**p) for p in providers_cfg
        }

        clients: dict[str, LLMClient] = {}
        from .mock_client import MockClient
        from .openai_compatible import OpenAIClient
        from .ollama_client import OllamaClient
        from .vllm_adapter import VLLMClient
        from .llamacpp_adapter import LlamaCppClient
        from .tgi_adapter import TGIClient

        for model_id, model in models.items():
            provider = providers[model.provider_id]
            if provider.api_type == "mock":
                clients[model_id] = MockClient(model, provider)
            elif provider.api_type == "openai_compatible":
                clients[model_id] = OpenAIClient(model, provider)
            elif provider.api_type == "ollama":
                clients[model_id] = OllamaClient(model, provider)
            elif provider.api_type == "vllm":
                clients[model_id] = VLLMClient(model, provider)
            elif provider.api_type == "llamacpp":
                clients[model_id] = LlamaCppClient(model, provider)
            elif provider.api_type == "text-generation-inference":
                clients[model_id] = TGIClient(model, provider)
            else:
                clients[model_id] = MockClient(model, provider)

        return cls(models, clients)
