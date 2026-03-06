from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .config import load_config
from .data_models import ResponseRecord
from .experiment_matrix import build_matrix
from .llm_clients.base import ClientRegistry
from .prompts.loader import load_prompt_suite
from .transforms.base import apply_transform
from .util.ids import new_run_id
from .util.jsonl import write_jsonl
from .util.time import utc_now
from .util.snapshots import write_snapshot, write_metadata
from .analysis.heuristics import heuristic_bundle
from .analysis.unsafe_detector import unsafe_score
from .analysis.anomaly import anomaly_score
from .analysis.pii import pii_score
from .util.hashing import file_sha256


class Runner:
    """Experiment orchestrator scaffold. Actual model calls should be implemented by users."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def run(
        self,
        base_config_path: Path,
        matrix_path: Path,
        models_path: Path,
        providers_path: Path,
        execute: bool = False,
        limit: int | None = None,
        sample: int | None = None,
        output_dir: Path | None = None,
        seed: int = 42,
    ) -> str:
        config = load_config(base_config_path)
        matrix_cfg = self._load_yaml(matrix_path)
        models_cfg = self._load_yaml(models_path)
        providers_cfg = self._load_yaml(providers_path)

        run_id = new_run_id()
        prompt_suite = load_prompt_suite(Path(config["paths"]["prompt_suite"]))
        client_registry = ClientRegistry.from_configs(models_cfg["models"], providers_cfg["providers"])

        responses: list[dict[str, Any]] = []
        transform_log: list[dict[str, Any]] = []
        request_log: list[dict[str, Any]] = []
        artifact_index: dict[str, str] = {}

        cells_iter = list(build_matrix(matrix_cfg))
        if sample:
            import random

            rng = random.Random(seed)
            cells_iter = rng.sample(cells_iter, min(sample, len(cells_iter)))
        if limit:
            cells_iter = cells_iter[:limit]

        for cell in cells_iter:
            model_config = client_registry.get_model_config(cell.model_id)
            client = client_registry.get_client(cell.model_id)

            prompts = prompt_suite.by_category(cell.prompt_category)
            for prompt in prompts:
                transformed_prompt, transform_meta = apply_transform(cell.transform, prompt.text)

                # Build generation parameters once for call and logging
                gen_params = {
                    "temperature": cell.temperature,
                    "max_tokens": cell.max_tokens,
                    **model_config.generation_parameters,
                    "transform": cell.transform,
                    "transform_meta": transform_meta,
                }

                # NOTE: Actual LLM invocation is stubbed unless execute=True and env allows network.
                result = client.generate(
                    transformed_prompt,
                    {k: v for k, v in gen_params.items() if k not in {"transform", "transform_meta"}},  # exclude transform info from API params
                    execute=execute,
                )
                generated_text = result.text
                heuristics = heuristic_bundle(generated_text)
                unsafe = unsafe_score(generated_text)
                anomaly = anomaly_score(generated_text)
                pii = pii_score(generated_text)

                record = ResponseRecord(
                    run_id=run_id,
                    model_id=cell.model_id,
                    provider_id=model_config.provider_id,
                    prompt_id=prompt.prompt_id,
                    category=prompt.category,
                    trial_index=cell.trial_index,
                    generation_parameters=gen_params,
                    timestamp=utc_now(),
                    raw_response_text=generated_text,
                    refusal_heuristic=heuristics.refusal,
                    safety_prefix_heuristic=heuristics.safety_prefix,
                    response_length=heuristics.length,
                    latency_ms=result.latency_ms,
                    unsafe_matches=unsafe.matches,
                    unsafe_score=unsafe.score,
                    anomaly_score=anomaly.score,
                    pii_score=pii.score,
                    model_name=model_config.model_name,
                    prompt_text=prompt.text,
                )
                responses.append(record.model_dump(mode="json"))
                transform_log.append(
                    {
                        "run_id": run_id,
                        "prompt_id": prompt.prompt_id,
                        "transform": cell.transform,
                        "meta": transform_meta,
                    }
                )
                request_log.append(
                    {
                        "run_id": run_id,
                        "model_id": cell.model_id,
                        "provider_id": model_config.provider_id,
                        "prompt_id": prompt.prompt_id,
                        "category": prompt.category,
                        "trial_index": cell.trial_index,
                        "transform": cell.transform,
                        "transformed_prompt": transformed_prompt,
                    }
                )

        out_dir = Path(output_dir or config["run"]["output_dir"]) / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        write_jsonl(out_dir / "responses.jsonl", responses)

        # Snapshots for reproducibility
        prompt_src = Path(config["paths"]["prompt_suite"])
        write_snapshot(out_dir / "config_snapshot.yaml", base_config_path.read_text())
        write_snapshot(out_dir / "prompt_snapshot.yaml", prompt_src.read_text())
        write_snapshot(out_dir / "providers_snapshot.yaml", providers_path.read_text())
        write_snapshot(out_dir / "models_snapshot.yaml", models_path.read_text())
        write_jsonl(out_dir / "transform_log.jsonl", transform_log)
        write_jsonl(out_dir / "request_log.jsonl", request_log)
        metadata = {
            "run_id": run_id,
            "created_at": utc_now().isoformat(),
            "matrix_path": str(matrix_path),
            "models_path": str(models_path),
            "providers_path": str(providers_path),
            "prompt_suite_path": str(prompt_src),
            "heuristics": {
                "refusal": "pattern_count",
                "safety_prefix": "pattern_count",
                "unsafe": "pattern_count",
            },
            "execute": execute,
        }
        write_metadata(out_dir / "metadata.json", metadata)
        (out_dir / "labels.jsonl").touch(exist_ok=True)
        (out_dir / "summary_metrics.csv").write_text("metric,value\n", encoding="utf-8")
        (out_dir / "summary.md").write_text("# Summary\n\nPending metrics.\n", encoding="utf-8")
        artifact_index = {
            "config_snapshot": str(out_dir / "config_snapshot.yaml"),
            "prompt_snapshot": str(out_dir / "prompt_snapshot.yaml"),
            "providers_snapshot": str(out_dir / "providers_snapshot.yaml"),
            "models_snapshot": str(out_dir / "models_snapshot.yaml"),
            "responses": str(out_dir / "responses.jsonl"),
            "transform_log": str(out_dir / "transform_log.jsonl"),
            "request_log": str(out_dir / "request_log.jsonl"),
            "labels": str(out_dir / "labels.jsonl"),
            "summary_csv": str(out_dir / "summary_metrics.csv"),
            "summary_md": str(out_dir / "summary.md"),
            "summary_html": str(out_dir / "summary.html"),
            "metadata": str(out_dir / "metadata.json"),
        }
        # add hashes where files exist
        indexed_with_hashes = {
            name: {"path": path, "sha256": file_sha256(Path(path)) if Path(path).exists() else None}
            for name, path in artifact_index.items()
        }
        write_snapshot(out_dir / "artifact_index.json", json.dumps(indexed_with_hashes, indent=2))

        return run_id

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        import yaml

        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
