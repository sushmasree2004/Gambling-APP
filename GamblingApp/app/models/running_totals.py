"""
Tracks the live in-memory state of a running session.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class RunningTotals:
    current_bankroll:    Decimal
    current_stake:       Decimal          = Decimal("0")
    round_number:        int              = 0
    consecutive_wins:    int              = 0
    consecutive_losses:  int              = 0
    total_wins:          int              = 0
    total_losses:        int              = 0
    total_staked:        Decimal          = Decimal("0")
    total_payout:        Decimal          = Decimal("0")
    peak_bankroll:       Decimal          = Decimal("0")
    lowest_bankroll:     Decimal          = Decimal("0")
    max_win_streak:      int              = 0
    max_loss_streak:     int              = 0

    def __post_init__(self) -> None:
        self.peak_bankroll   = self.current_bankroll
        self.lowest_bankroll = self.current_bankroll

    @property
    def net_profit_loss(self) -> Decimal:
        return self.total_payout - self.total_staked

    @property
    def total_bets(self) -> int:
        return self.total_wins + self.total_losses

    @property
    def win_rate(self) -> float:
        if self.total_bets == 0:
            return 0.0
        return self.total_wins / self.total_bets

    def record_win(self, stake: Decimal, payout: Decimal) -> None:
        self.current_bankroll   += payout - stake
        self.total_staked       += stake
        self.total_payout       += payout
        self.total_wins         += 1
        self.consecutive_wins   += 1
        self.consecutive_losses  = 0
        self.round_number       += 1
        if self.consecutive_wins > self.max_win_streak:
            self.max_win_streak = self.consecutive_wins
        if self.current_bankroll > self.peak_bankroll:
            self.peak_bankroll = self.current_bankroll

    def record_loss(self, stake: Decimal) -> None:
        self.current_bankroll   -= stake
        self.total_staked       += stake
        self.total_losses       += 1
        self.consecutive_losses += 1
        self.consecutive_wins    = 0
        self.round_number       += 1
        if self.consecutive_losses > self.max_loss_streak:
            self.max_loss_streak = self.consecutive_losses
        if self.current_bankroll < self.lowest_bankroll:
            self.lowest_bankroll = self.current_bankroll

    def to_dict(self) -> dict:
        return {
            "current_bankroll":   float(self.current_bankroll),
            "current_stake":      float(self.current_stake),
            "round_number":       self.round_number,
            "consecutive_wins":   self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
            "total_wins":         self.total_wins,
            "total_losses":       self.total_losses,
            "total_staked":       float(self.total_staked),
            "total_payout":       float(self.total_payout),
            "net_profit_loss":    float(self.net_profit_loss),
            "win_rate":           self.win_rate,
            "peak_bankroll":      float(self.peak_bankroll),
            "lowest_bankroll":    float(self.lowest_bankroll),
        }
