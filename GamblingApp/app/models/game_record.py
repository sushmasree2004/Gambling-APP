"""
Raw record of a single game round outcome (independent of money).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.models.game_result import GameResult
from app.models.session_enums import GameType


@dataclass
class GameRecord:
    session_id:      int
    round_number:    int
    outcome:         GameResult
    id:              Optional[int]     = None
    bet_id:          Optional[int]     = None
    game_type:       GameType          = GameType.COIN_FLIP
    win_probability: Optional[float]   = None
    random_value:    Optional[float]   = None
    created_at:      Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "session_id":      self.session_id,
            "round_number":    self.round_number,
            "game_type":       self.game_type.value,
            "outcome":         self.outcome.value,
            "win_probability": self.win_probability,
            "random_value":    self.random_value,
            "created_at":      str(self.created_at) if self.created_at else None,
        }
