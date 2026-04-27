"""
Represents a registered gambler / player.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class GamblerProfile:
    username:         str
    email:            str
    initial_bankroll: Decimal
    current_bankroll: Decimal
    id:               Optional[int]  = None
    created_at:       Optional[datetime] = None
    updated_at:       Optional[datetime] = None
    is_active:        bool            = True

    # ── Computed helpers ────────────────────────────────────────────────────
    @property
    def profit_loss(self) -> Decimal:
        return self.current_bankroll - self.initial_bankroll

    @property
    def roi_percent(self) -> Decimal:
        if self.initial_bankroll == 0:
            return Decimal("0")
        return (self.profit_loss / self.initial_bankroll * 100).quantize(Decimal("0.01"))

    # ── Serialisation ───────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "username":         self.username,
            "email":            self.email,
            "initial_bankroll": float(self.initial_bankroll),
            "current_bankroll": float(self.current_bankroll),
            "profit_loss":      float(self.profit_loss),
            "roi_percent":      float(self.roi_percent),
            "created_at":       str(self.created_at) if self.created_at else None,
            "is_active":        self.is_active,
        }

    def __str__(self) -> str:
        return (
            f"GamblerProfile(id={self.id}, username='{self.username}', "
            f"bankroll={self.current_bankroll:.2f})"
        )
