from __future__ import annotations

from pathlib import Path

import typer

from ..data_models import LabelRecord, LabelType, ResponseRecord
from ..util.jsonl import read_jsonl, write_jsonl
from .prelabel import suggest_label

app = typer.Typer(add_completion=False, no_args_is_help=True)


def _prompt_label(response: ResponseRecord) -> LabelType:
    typer.echo(f"\nPrompt {response.prompt_id} ({response.category}) -> {response.model_id}")
    typer.echo(f"Response: {response.raw_response_text}\n")
    suggested = suggest_label(response)
    choice = typer.prompt(
        f"Label [r=REFUSAL / p=PARTIAL / u=UNSAFE] (suggested: {suggested})", default="r"
    )
    mapping = {"r": "REFUSAL", "p": "PARTIAL_COMPLIANCE", "u": "UNSAFE_COMPLIANCE"}
    return mapping.get(choice.lower(), suggested)  # type: ignore[return-value]


@app.command()
def label(
    responses_path: Path = typer.Argument(..., help="Path to responses.jsonl"),
    output_path: Path = typer.Option(..., help="Where to write labels.jsonl"),
    labeler: str = typer.Option("human", help="Labeler identifier"),
) -> None:
    responses = [ResponseRecord(**r) for r in read_jsonl(responses_path)]
    labeled: list[LabelRecord] = []
    for resp in responses:
        label_value = _prompt_label(resp)
        labeled.append(LabelRecord(**resp.model_dump(), label=label_value, labeler=labeler))

    write_jsonl(output_path, [l.model_dump() for l in labeled])
    typer.echo(f"Wrote {len(labeled)} labels to {output_path}")


if __name__ == "__main__":
    app()
