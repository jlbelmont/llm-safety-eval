from llm_safety_eval.runner import Runner


def test_matrix_generation_parameters_override_model_defaults():
    params = Runner._build_generation_parameters(
        {"temperature": 0.4, "max_tokens": 512, "top_p": 0.9},
        temperature=0.2,
        max_tokens=1024,
        transform="none",
        transform_meta={"name": "none"},
    )

    assert params["temperature"] == 0.2
    assert params["max_tokens"] == 1024
    assert params["top_p"] == 0.9
    assert params["transform"] == "none"
    assert params["transform_meta"] == {"name": "none"}
