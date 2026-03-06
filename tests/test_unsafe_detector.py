from llm_safety_eval.analysis.unsafe_detector import unsafe_score


def test_unsafe_detector_scores():
    text = "This payload opens a reverse shell"
    score = unsafe_score(text)
    assert score.matches > 0
    assert score.score > 0
