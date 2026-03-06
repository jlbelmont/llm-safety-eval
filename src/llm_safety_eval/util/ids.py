from __future__ import annotations

import uuid


def new_run_id() -> str:
    """Generate a short unique run identifier."""

    return uuid.uuid4().hex[:12]
