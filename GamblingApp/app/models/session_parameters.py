"""
Stop-condition parameters for a betting session.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class SessionParameters:
    stop_loss_threshold:   Optional[Decimal] = None  # stop if bankroll drops below this
    take_profit_threshold: Optional[Decimal] = None  # stop if bankroll rises above this
    max_rounds:            Optional[int]      = None  # stop after this many rounds

    def to_dict(self) -> dict:
        return {
            "stop_loss_threshold":   float(self.stop_loss_threshold) if self.stop_loss_threshold else None,
            "take_profit_threshold": float(self.take_profit_threshold) if self.take_profit_threshold else None,
            "max_rounds":            self.max_rounds,
        }
