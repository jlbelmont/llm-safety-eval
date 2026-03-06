from __future__ import annotations

from pathlib import Path
import typer
import yaml

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def main(prompt_suite: Path = typer.Argument(Path("prompts/prompt_suites.yaml"))) -> None:
    data = yaml.safe_load(prompt_suite.read_text()) or {}
    categories = data.get("categories", {})
    dup_ids = set()
    seen = set()
    empty = []
    for cat, payload in categories.items():
        prompts = payload.get("prompts", [])
        if not prompts:
            empty.append(cat)
        for p in prompts:
            pid = p.get("prompt_id")
            if pid in seen:
                dup_ids.add(pid)
            seen.add(pid)
            if not p.get("text"):
                empty.append(f"{cat}:{pid}")
    if dup_ids:
        typer.echo(f"Duplicate prompt_ids: {sorted(dup_ids)}", err=True)
    if empty:
        typer.echo(f"Empty prompts/categories: {empty}", err=True)
    if not dup_ids and not empty:
        typer.echo("Prompt suite OK")


if __name__ == "__main__":
    app()
