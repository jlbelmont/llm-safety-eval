from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)
