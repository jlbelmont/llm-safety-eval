from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, Any


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    """Write iterable of dict records to JSONL."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield dict records from a JSONL file."""

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)
