from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PauseRecord:
    session_id: int
    id:         Optional[int]     = None
    paused_at:  Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    reason:     Optional[str]      = None

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "session_id": self.session_id,
            "paused_at":  str(self.paused_at)  if self.paused_at  else None,
            "resumed_at": str(self.resumed_at) if self.resumed_at else None,
            "reason":     self.reason,
        }
