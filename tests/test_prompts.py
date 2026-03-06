from pathlib import Path

from llm_safety_eval.prompts.loader import load_prompt_suite


def test_prompt_suite_unique_ids(tmp_path: Path):
    # reuse existing prompt suite to validate uniqueness and category matching
    suite = load_prompt_suite(Path("prompts/prompt_suites.yaml"))
    seen = set()
    for cat, category in suite.categories.items():
        for prompt in category.prompts:
            assert prompt.category == cat
            assert prompt.prompt_id not in seen
            seen.add(prompt.prompt_id)


def test_benign_control_present():
    suite = load_prompt_suite(Path("prompts/prompt_suites.yaml"))
    assert "benign_control" in suite.categories
    assert len(suite.categories["benign_control"].prompts) >= 2
