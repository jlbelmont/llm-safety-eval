from llm_safety_eval.experiment_matrix import build_matrix
import yaml
from pathlib import Path


def test_matrix_counts():
    cfg = yaml.safe_load(Path("configs/matrix.yaml").read_text())
    cells = list(build_matrix(cfg))
    expected = (
        len(cfg["matrix"]["models"])
        * len(cfg["matrix"]["prompt_categories"])
        * len(cfg["matrix"]["transforms"])
        * cfg["matrix"]["trials"]
        * len(cfg["matrix"]["generation_parameters"]["temperature"])
        * len(cfg["matrix"]["generation_parameters"]["max_tokens"])
    )
    assert len(cells) == expected


def test_matrix_includes_benign():
    cfg = yaml.safe_load(Path("configs/matrix.yaml").read_text())
    assert "benign_control" in cfg["matrix"]["prompt_categories"]
