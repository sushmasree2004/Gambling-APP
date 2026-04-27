"""
Represents an active or historical betting session.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.models.betting_preferences import BettingPreferences
from app.models.session_enums import SessionStatus


@dataclass
class BettingSession:
    gambler_id:   int
    session_name: str
    preferences:  BettingPreferences
    id:           Optional[int]          = None
    status:       SessionStatus          = SessionStatus.ACTIVE
    started_at:   Optional[datetime]     = None
    ended_at:     Optional[datetime]     = None

    @property
    def is_active(self) -> bool:
        return self.status == SessionStatus.ACTIVE

    @property
    def is_paused(self) -> bool:
        return self.status == SessionStatus.PAUSED

    def duration_seconds(self) -> Optional[float]:
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "gambler_id":   self.gambler_id,
            "session_name": self.session_name,
            "preferences":  self.preferences.to_dict(),
            "status":       self.status.value,
            "started_at":   str(self.started_at) if self.started_at else None,
            "ended_at":     str(self.ended_at)   if self.ended_at   else None,
        }
