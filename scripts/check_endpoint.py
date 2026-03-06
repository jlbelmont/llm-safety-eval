from __future__ import annotations

from pathlib import Path

import httpx
import typer
import yaml

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def ping(providers_path: Path = typer.Argument(..., help="Path to providers.yaml")) -> None:
    providers = yaml.safe_load(providers_path.read_text())["providers"]
    for provider in providers:
        url = provider["base_url"]
        typer.echo(f"Checking {provider['provider_id']} at {url} ...")
        try:
            resp = httpx.get(url, timeout=3.0)
            typer.echo(f"  status: {resp.status_code}")
        except Exception as exc:  # pragma: no cover - network dependent
            typer.echo(f"  error: {exc}")


if __name__ == "__main__":
    app()
