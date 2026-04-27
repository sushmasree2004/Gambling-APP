"""
Calculates and updates WinLossStatistics from RunningTotals or a list of Bets.
"""
from __future__ import annotations

from decimal import Decimal
from typing import List

from app.models.bet import Bet
from app.models.game_result import GameResult
from app.models.running_totals import RunningTotals
from app.models.win_loss_statistics import WinLossStatistics


class WinLossCalculator:

    @staticmethod
    def from_running_totals(totals: RunningTotals,
                             session_id: int,
                             gambler_id: int) -> WinLossStatistics:
        """Build a WinLossStatistics snapshot from the live RunningTotals."""
        wr = Decimal(str(round(totals.win_rate, 6)))
        return WinLossStatistics(
            session_id          = session_id,
            gambler_id          = gambler_id,
            total_bets          = totals.total_bets,
            total_wins          = totals.total_wins,
            total_losses        = totals.total_losses,
            total_staked        = totals.total_staked,
            total_payout        = totals.total_payout,
            net_profit_loss     = totals.net_profit_loss,
            win_rate            = wr,
            max_win_streak      = totals.max_win_streak,
            max_loss_streak     = totals.max_loss_streak,
            current_win_streak  = totals.consecutive_wins,
            current_loss_streak = totals.consecutive_losses,
            peak_bankroll       = totals.peak_bankroll,
            lowest_bankroll     = totals.lowest_bankroll,
        )

    @staticmethod
    def from_bets(bets: List[Bet],
                  session_id: int,
                  gambler_id: int,
                  initial_bankroll: Decimal) -> WinLossStatistics:
        """Recalculate statistics from a historical list of Bet objects."""
        wins = losses = 0
        total_staked = total_payout = Decimal("0")
        cur_w = cur_l = max_w = max_l = 0
        peak = lowest = initial_bankroll

        for bet in bets:
            total_staked += bet.stake_amount
            if bet.game_result == GameResult.WIN:
                wins    += 1
                total_payout += bet.payout
                cur_w   += 1
                cur_l    = 0
                max_w    = max(max_w, cur_w)
            else:
                losses  += 1
                cur_l   += 1
                cur_w    = 0
                max_l    = max(max_l, cur_l)
            peak   = max(peak,   bet.bankroll_after)
            lowest = min(lowest, bet.bankroll_after)

        total = wins + losses
        wr = Decimal(str(round(wins / total, 6))) if total else Decimal("0")
        return WinLossStatistics(
            session_id          = session_id,
            gambler_id          = gambler_id,
            total_bets          = total,
            total_wins          = wins,
            total_losses        = losses,
            total_staked        = total_staked,
            total_payout        = total_payout,
            net_profit_loss     = total_payout - total_staked,
            win_rate            = wr,
            max_win_streak      = max_w,
            max_loss_streak     = max_l,
            current_win_streak  = cur_w,
            current_loss_streak = cur_l,
            peak_bankroll       = peak,
            lowest_bankroll     = lowest,
        )

    @staticmethod
    def roi_percent(stats: WinLossStatistics, initial_bankroll: Decimal) -> Decimal:
        if initial_bankroll == 0:
            return Decimal("0")
        return (stats.net_profit_loss / initial_bankroll * 100).quantize(Decimal("0.01"))
