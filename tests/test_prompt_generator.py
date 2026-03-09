from pathlib import Path

from llm_safety_eval.adversary.prompt_generator import inject_generated_prompts
from llm_safety_eval.prompts.loader import load_prompt_suite


def test_inject_generated_prompts_adds_prompts_to_existing_category():
    suite = load_prompt_suite(Path("prompts/prompt_suites.yaml"))
    before = len(suite.categories["baseline_direct"].prompts)
    generated = inject_generated_prompts(
        suite,
        {
            "enabled": True,
            "requests": [
                {
                    "category": "baseline_direct",
                    "attack_style": "obfuscation",
                    "count": 2,
                    "seed": 11,
                    "example_prompt_id": "base_direct_01",
                }
            ],
        },
    )
    after = len(generated.categories["baseline_direct"].prompts)
    assert after == before + 2
    assert generated.categories["baseline_direct"].prompts[-1].prompt_id.startswith("generated_baseline_direct_")

