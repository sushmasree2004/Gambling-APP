"""
Holds win-probability and payout multiplier for a game session.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class OddsConfig:
    win_probability:   float   = 0.50       # probability [0, 1]
    payout_multiplier: Decimal = Decimal("2.00")  # e.g. 2× means stake returned + stake profit
    house_edge:        float   = 0.00

    def expected_value(self, stake: Decimal) -> Decimal:
        """Expected value of a single bet."""
        win_amount  = stake * (self.payout_multiplier - 1)
        loss_amount = stake
        return (Decimal(str(self.win_probability)) * win_amount
                - Decimal(str(1 - self.win_probability)) * loss_amount)

    def to_dict(self) -> dict:
        return {
            "win_probability":   self.win_probability,
            "payout_multiplier": float(self.payout_multiplier),
            "house_edge":        self.house_edge,
        }
