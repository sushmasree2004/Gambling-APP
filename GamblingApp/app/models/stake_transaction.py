from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.transaction_type import TransactionType


@dataclass
class StakeTransaction:
    gambler_id:       int
    transaction_type: TransactionType
    amount:           Decimal
    balance_before:   Decimal
    balance_after:    Decimal
    id:               Optional[int]     = None
    session_id:       Optional[int]     = None
    description:      Optional[str]     = None
    created_at:       Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "gambler_id":       self.gambler_id,
            "session_id":       self.session_id,
            "transaction_type": self.transaction_type.value,
            "amount":           float(self.amount),
            "balance_before":   float(self.balance_before),
            "balance_after":    float(self.balance_after),
            "description":      self.description,
            "created_at":       str(self.created_at) if self.created_at else None,
        }
