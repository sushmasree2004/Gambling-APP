"""
Represents a single bet placed during a session.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.game_result import GameResult


@dataclass
class Bet:
    session_id:          int
    gambler_id:          int
    round_number:        int
    stake_amount:        Decimal
    game_result:         GameResult
    payout:              Decimal
    profit_loss:         Decimal
    bankroll_after:      Decimal
    id:                  Optional[int]     = None
    strategy_next_stake: Optional[Decimal] = None
    created_at:          Optional[datetime] = None

    @property
    def is_win(self) -> bool:
        return self.game_result == GameResult.WIN

    def to_dict(self) -> dict:
        return {
            "id":                  self.id,
            "session_id":          self.session_id,
            "gambler_id":          self.gambler_id,
            "round_number":        self.round_number,
            "stake_amount":        float(self.stake_amount),
            "game_result":         self.game_result.value,
            "payout":              float(self.payout),
            "profit_loss":         float(self.profit_loss),
            "bankroll_after":      float(self.bankroll_after),
            "strategy_next_stake": float(self.strategy_next_stake) if self.strategy_next_stake else None,
            "created_at":          str(self.created_at) if self.created_at else None,
        }
