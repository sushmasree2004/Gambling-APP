from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class WinLossStatistics:
    session_id:          int
    gambler_id:          int
    total_bets:          int     = 0
    total_wins:          int     = 0
    total_losses:        int     = 0
    total_staked:        Decimal = Decimal("0")
    total_payout:        Decimal = Decimal("0")
    net_profit_loss:     Decimal = Decimal("0")
    win_rate:            Decimal = Decimal("0")
    max_win_streak:      int     = 0
    max_loss_streak:     int     = 0
    current_win_streak:  int     = 0
    current_loss_streak: int     = 0
    peak_bankroll:       Decimal = Decimal("0")
    lowest_bankroll:     Decimal = Decimal("0")
    id:                  Optional[int] = None

    def roi_percent(self, initial_bankroll: Decimal) -> Decimal:
        if initial_bankroll == 0:
            return Decimal("0")
        return (self.net_profit_loss / initial_bankroll * 100).quantize(Decimal("0.01"))

    def to_dict(self) -> dict:
        return {
            "id":                  self.id,
            "session_id":          self.session_id,
            "gambler_id":          self.gambler_id,
            "total_bets":          self.total_bets,
            "total_wins":          self.total_wins,
            "total_losses":        self.total_losses,
            "total_staked":        float(self.total_staked),
            "total_payout":        float(self.total_payout),
            "net_profit_loss":     float(self.net_profit_loss),
            "win_rate":            float(self.win_rate),
            "max_win_streak":      self.max_win_streak,
            "max_loss_streak":     self.max_loss_streak,
            "current_win_streak":  self.current_win_streak,
            "current_loss_streak": self.current_loss_streak,
            "peak_bankroll":       float(self.peak_bankroll),
            "lowest_bankroll":     float(self.lowest_bankroll),
        }
