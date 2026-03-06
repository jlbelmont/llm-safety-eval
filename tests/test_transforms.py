from llm_safety_eval.transforms.base import apply_transform


def test_chain_of_denial_inserts_prefix():
    text, meta = apply_transform("chain_of_denial", "request text")
    assert "must refuse" in text
    assert meta["name"] == "chain_of_denial"


def test_perturbation_preserves_segments():
    prompt = "A. B. C."
    text, meta = apply_transform("perturbation", prompt)
    assert len(text.split(". ")) == len(prompt.split(". "))
    assert meta["segments"] == len(prompt.split(". "))
