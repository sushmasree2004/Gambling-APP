"""
Abstract base class that every betting strategy must implement.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from app.models.running_totals import RunningTotals
from app.models.stake_boundary import StakeBoundary
from app.models.session_enums import StrategyType


class BaseStrategy(ABC):
    """
    All strategies expose a single method: ``next_stake()``.
    They receive the live RunningTotals so they can inspect history.
    """

    strategy_type: StrategyType  # must be set by subclass

    def __init__(self, base_stake: Decimal, boundary: StakeBoundary) -> None:
        self.base_stake = base_stake
        self.boundary   = boundary

    # ── Required override ────────────────────────────────────────────────────
    @abstractmethod
    def next_stake(self, totals: RunningTotals) -> Decimal:
        """Return the stake for the next round."""

    # ── Helpers available to subclasses ─────────────────────────────────────
    def apply_boundary(self, stake: Decimal) -> Decimal:
        return self.boundary.clamp(stake)

    def reset(self) -> None:
        """Reset internal state (call after session ends or session reset)."""

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"base={self.base_stake}, "
            f"min={self.boundary.min_stake}, "
            f"max={self.boundary.max_stake})"
        )
