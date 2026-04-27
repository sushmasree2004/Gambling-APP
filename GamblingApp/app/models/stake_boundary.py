"""
Defines the minimum and maximum allowed stake for a session.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class StakeBoundary:
    min_stake: Decimal
    max_stake: Decimal

    def __post_init__(self) -> None:
        if self.min_stake <= 0:
            raise ValueError("min_stake must be positive.")
        if self.max_stake < self.min_stake:
            raise ValueError("max_stake must be >= min_stake.")

    def clamp(self, amount: Decimal) -> Decimal:
        """Clamp *amount* to [min_stake, max_stake]."""
        return max(self.min_stake, min(self.max_stake, amount))

    def is_within(self, amount: Decimal) -> bool:
        return self.min_stake <= amount <= self.max_stake

    def to_dict(self) -> dict:
        return {"min_stake": float(self.min_stake), "max_stake": float(self.max_stake)}
