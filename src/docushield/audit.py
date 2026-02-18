from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import AuditEvent


class AuditLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write_event(self, event: AuditEvent) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.__dict__, ensure_ascii=False) + "\n")

    def write_many(self, events: Iterable[AuditEvent]) -> None:
        for event in events:
            self.write_event(event)
