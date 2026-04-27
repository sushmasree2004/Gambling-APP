"""
Renders post-session summary tables.
"""
from __future__ import annotations

from typing import List

from app.models.bet import Bet
from app.models.betting_session import BettingSession
from app.models.gambler_profile import GamblerProfile
from app.models.win_loss_statistics import WinLossStatistics
from app.utils.validators import banner, format_currency, format_percentage, mini_banner


class SessionSummary:

    @staticmethod
    def print_full(session: BettingSession,
                   gambler: GamblerProfile,
                   stats: WinLossStatistics,
                   bets: List[Bet]) -> None:
        print(banner(f"SESSION SUMMARY  –  {session.session_name}"))

        # Basic info
        print(mini_banner("Session Info"))
        print(f"  Session ID  : {session.id}")
        print(f"  Gambler     : {gambler.username}")
        print(f"  Strategy    : {session.preferences.strategy_type.value}")
        print(f"  Status      : {session.status.value}")
        if session.started_at:
            print(f"  Started     : {session.started_at}")
        if session.ended_at:
            print(f"  Ended       : {session.ended_at}")

        # Statistics
        print(mini_banner("Betting Statistics"))
        print(f"  Total Rounds   : {stats.total_bets}")
        print(f"  Wins           : {stats.total_wins}   ({format_percentage(float(stats.win_rate))})")
        print(f"  Losses         : {stats.total_losses}")
        print(f"  Total Staked   : {format_currency(stats.total_staked)}")
        print(f"  Total Payout   : {format_currency(stats.total_payout)}")
        sign = "+" if stats.net_profit_loss >= 0 else ""
        print(f"  Net P/L        : {sign}{format_currency(stats.net_profit_loss)}")
        print(f"  Peak Bankroll  : {format_currency(stats.peak_bankroll)}")
        print(f"  Lowest Bankroll: {format_currency(stats.lowest_bankroll)}")
        print(f"  Max Win Streak : {stats.max_win_streak}")
        print(f"  Max Loss Streak: {stats.max_loss_streak}")
        roi = stats.roi_percent(gambler.initial_bankroll)
        print(f"  ROI            : {roi:+.2f}%")

        # Bet history (last 20)
        if bets:
            print(mini_banner(f"Last {min(20, len(bets))} Rounds"))
            header = f"  {'#':>4}  {'Stake':>10}  {'Result':<6}  {'P/L':>10}  {'Bankroll':>12}"
            print(header)
            print(f"  {'─'*54}")
            for bet in bets[-20:]:
                pl_sign = "+" if bet.profit_loss >= 0 else ""
                print(
                    f"  {bet.round_number:>4}  "
                    f"{format_currency(bet.stake_amount):>10}  "
                    f"{bet.game_result.value:<6}  "
                    f"{pl_sign}{format_currency(bet.profit_loss):>10}  "
                    f"{format_currency(bet.bankroll_after):>12}"
                )

        print(banner("END OF SUMMARY"))

    @staticmethod
    def print_brief(session: BettingSession, stats: WinLossStatistics) -> None:
        sign = "+" if stats.net_profit_loss >= 0 else ""
        print(
            f"  [{session.id}] {session.session_name:<25} "
            f"Rounds:{stats.total_bets:<6} "
            f"W/L:{stats.total_wins}/{stats.total_losses}  "
            f"P/L:{sign}{format_currency(stats.net_profit_loss)}"
        )
