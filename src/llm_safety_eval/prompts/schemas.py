from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Prompt(BaseModel):
    prompt_id: str
    category: str
    text: str
    safety_notes: Optional[str] = None


class PromptSuite(BaseModel):
    version: str
    categories: dict[str, "PromptCategory"]

    def by_category(self, category: str) -> list[Prompt]:
        return self.categories[category].prompts


class PromptCategory(BaseModel):
    description: str
    prompts: list[Prompt]
