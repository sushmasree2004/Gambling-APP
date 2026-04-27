"""
Aggregate that bundles a BettingSession with its live state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.models.bet import Bet
from app.models.betting_session import BettingSession
from app.models.gambler_profile import GamblerProfile
from app.models.running_totals import RunningTotals
from app.models.win_loss_statistics import WinLossStatistics


@dataclass
class GamingSession:
    session:       BettingSession
    gambler:       GamblerProfile
    running_totals: RunningTotals         = field(default_factory=lambda: RunningTotals(Decimal("0")))
    bets:          List[Bet]             = field(default_factory=list)
    statistics:    Optional[WinLossStatistics] = None

    def add_bet(self, bet: Bet) -> None:
        self.bets.append(bet)

    def latest_bet(self) -> Optional[Bet]:
        return self.bets[-1] if self.bets else None


# Circular import guard
from decimal import Decimal  # noqa: E402
