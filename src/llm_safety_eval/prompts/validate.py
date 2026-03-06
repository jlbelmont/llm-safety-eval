from __future__ import annotations

from .schemas import PromptSuite


def validate_prompt_suite(suite: PromptSuite) -> None:
    """Lightweight validation: presence, unique prompt_ids, category alignment."""

    assert suite.categories, "Prompt suite must contain at least one category."
    seen_ids: set[str] = set()
    for name, category in suite.categories.items():
        assert category.prompts, f"Category {name} has no prompts."
        for prompt in category.prompts:
            assert prompt.category == name, f"Prompt {prompt.prompt_id} category mismatch {prompt.category} != {name}"
            if prompt.prompt_id in seen_ids:
                raise ValueError(f"Duplicate prompt_id: {prompt.prompt_id}")
            seen_ids.add(prompt.prompt_id)
