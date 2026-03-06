from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import typer
import yaml

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _load(schema_path: Path, data_path: Path) -> tuple[dict, dict]:
    schema = json.loads(schema_path.read_text())
    data = yaml.safe_load(data_path.read_text()) or {}
    return schema, data


@app.command()
def check(
    base: Path = typer.Option(Path("configs/base.yaml")),
    providers: Path = typer.Option(Path("configs/providers.yaml")),
    models: Path = typer.Option(Path("configs/models.yaml")),
    matrix: Path = typer.Option(Path("configs/matrix.yaml")),
    prompts: Path = typer.Option(Path("prompts/prompt_suites.yaml")),
    schema_dir: Path = typer.Option(Path("configs/schema")),
) -> None:
    mappings = [
        ("base.schema.json", base),
        ("providers.schema.json", providers),
        ("models.schema.json", models),
        ("matrix.schema.json", matrix),
        ("prompts.schema.json", prompts),
    ]
    for schema_name, data_path in mappings:
        schema_path = schema_dir / schema_name
        schema, data = _load(schema_path, data_path)
        jsonschema.validate(instance=data, schema=schema)
        typer.echo(f"Validated {data_path} against {schema_name}")


if __name__ == "__main__":
    app()
