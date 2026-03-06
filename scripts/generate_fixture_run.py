from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

def main(run_id: str = "fixture_run") -> None:
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    responses = [
        {
            "run_id": run_id,
            "model_id": "mock_safe",
            "provider_id": "mock",
            "prompt_id": "base_direct_01",
            "category": "baseline_direct",
            "trial_index": 0,
            "generation_parameters": {"temperature": 0.2, "max_tokens": 256, "transform": "none", "transform_meta": {}},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_response_text": "[mock response]",
            "refusal_heuristic": 0.5,
            "safety_prefix_heuristic": 0.1,
            "response_length": 15,
            "latency_ms": 0.0,
            "unsafe_matches": 0,
            "unsafe_score": 0.0,
        }
    ]
    labels = [
        {
            **responses[0],
            "label": "REFUSAL",
            "labeler": "fixture",
        }
    ]
    (run_dir / "responses.jsonl").write_text("\n".join(json.dumps(r) for r in responses), encoding="utf-8")
    (run_dir / "labels.jsonl").write_text("\n".join(json.dumps(l) for l in labels), encoding="utf-8")
    (run_dir / "summary_metrics.csv").write_text("metric,value\n", encoding="utf-8")
    (run_dir / "summary.md").write_text("# Summary\nFixture run.\n", encoding="utf-8")
    (run_dir / "summary.html").write_text("<html><body>Fixture</body></html>", encoding="utf-8")
    (run_dir / "config_snapshot.yaml").write_text(Path("configs/base.yaml").read_text(), encoding="utf-8")
    (run_dir / "prompt_snapshot.yaml").write_text(Path("prompts/prompt_suites.yaml").read_text(), encoding="utf-8")
    (run_dir / "providers_snapshot.yaml").write_text(Path("configs/providers.yaml").read_text(), encoding="utf-8")
    (run_dir / "models_snapshot.yaml").write_text(Path("configs/models.yaml").read_text(), encoding="utf-8")
    (run_dir / "transform_log.jsonl").write_text("{}", encoding="utf-8")
    (run_dir / "request_log.jsonl").write_text("{}", encoding="utf-8")
    metadata = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "fixture": True,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (run_dir / "artifact_index.json").write_text(json.dumps({"responses": str(run_dir / "responses.jsonl")}, indent=2), encoding="utf-8")
    (run_dir / "labels.jsonl").touch(exist_ok=True)


if __name__ == "__main__":
    main()
