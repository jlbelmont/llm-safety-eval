from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    provider_id: str
    api_type: Literal[
        "openai_compatible", "ollama", "vllm", "llamacpp", "text-generation-inference", "mock"
    ]
    base_url: str
    api_key_env: Optional[str] = None
    provider_notes: Optional[str] = None
    rate_limit_per_min: Optional[int] = None
    backoff_seconds: Optional[float] = None
    max_requests_per_minute: Optional[int] = None
    timeout_seconds: Optional[float] = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ModelConfig(BaseModel):
    model_id: str
    provider_id: str
    model_name: str
    model_version: Optional[str] = None
    generation_parameters: dict[str, Any] = Field(default_factory=dict)


class PromptItem(BaseModel):
    prompt_id: str
    category: str
    text: str
    safety_notes: Optional[str] = None


class PromptCategory(BaseModel):
    name: str
    description: str
    prompts: list[PromptItem]


class PromptSuite(BaseModel):
    version: str
    categories: list[PromptCategory]


LabelType = Literal["REFUSAL", "PARTIAL_COMPLIANCE", "UNSAFE_COMPLIANCE"]


class GenerationParams(BaseModel):
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stop: Optional[list[str]] = None
    extra: dict[str, Any] = Field(default_factory=dict)


class RequestRecord(BaseModel):
    run_id: str
    model_id: str
    provider_id: str
    prompt_id: str
    category: str
    trial_index: int
    generation_parameters: dict[str, Any]
    timestamp: datetime


class ResponseRecord(RequestRecord):
    raw_response_text: str
    refusal_heuristic: Optional[float] = None
    safety_prefix_heuristic: Optional[float] = None
    response_length: Optional[int] = None
    latency_ms: Optional[float] = None
    unsafe_matches: Optional[int] = None
    unsafe_score: Optional[float] = None
    anomaly_score: Optional[float] = None
    pii_score: Optional[float] = None
    model_name: Optional[str] = None
    prompt_text: Optional[str] = None


class LabelRecord(ResponseRecord):
    label: LabelType
    labeler: str = "human"


class RunMetadata(BaseModel):
    run_id: str
    created_at: datetime
    matrix_path: str
    prompt_suite_path: str
    provider_path: str
    models_path: str
    base_config_path: str
    notes: Optional[str] = None
