"""
Represents the raw outcome of a single game round.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.models.game_result import GameResult
from app.models.session_enums import GameType


@dataclass
class OutcomeBase:
    result:          GameResult
    random_value:    float
    win_probability: float
    game_type:       GameType = GameType.COIN_FLIP

    @property
    def is_win(self) -> bool:
        return self.result == GameResult.WIN

    def __str__(self) -> str:
        icon = "✓ WIN" if self.is_win else "✗ LOSS"
        return (
            f"{icon}  (roll={self.random_value:.6f} vs "
            f"p_win={self.win_probability:.4f})"
        )
