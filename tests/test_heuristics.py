from llm_safety_eval.analysis.heuristics import heuristic_bundle


def test_heuristics_scores():
    text = "As an AI, I cannot comply with unsafe requests."
    scores = heuristic_bundle(text)
    assert scores.refusal > 0
    assert scores.safety_prefix >= 0
    assert scores.length == len(text)
