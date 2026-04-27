"""
Renders current round status to the terminal.
"""
from __future__ import annotations

from app.models.bet import Bet
from app.models.betting_session import BettingSession
from app.models.game_record import GameRecord
from app.models.running_totals import RunningTotals
from app.utils.validators import format_currency, format_percentage, mini_banner


class GameStatusDisplay:

    @staticmethod
    def round_header(round_num: int, strategy_name: str) -> None:
        print(f"\n{'─'*60}")
        print(f"  ROUND {round_num:>4}  │  Strategy: {strategy_name}")
        print(f"{'─'*60}")

    @staticmethod
    def show_bet_placed(stake: float, bankroll_before: float) -> None:
        print(f"  Stake placed:    {format_currency(stake):>12}")
        print(f"  Bankroll before: {format_currency(bankroll_before):>12}")

    @staticmethod
    def show_outcome(record: GameRecord) -> None:
        icon = "✅  WIN" if record.outcome.value == "WIN" else "❌  LOSS"
        print(f"  Result:          {icon}")
        print(f"  Random roll:     {record.random_value:.6f}  (win if < {record.win_probability:.4f})")

    @staticmethod
    def show_bet_result(bet: Bet) -> None:
        pl_sign = "+" if bet.profit_loss >= 0 else ""
        print(f"  Payout:          {format_currency(bet.payout):>12}")
        print(f"  Profit / Loss:   {pl_sign}{format_currency(bet.profit_loss):>11}")
        print(f"  Bankroll after:  {format_currency(bet.bankroll_after):>12}")

    @staticmethod
    def show_running_totals(totals: RunningTotals) -> None:
        print(mini_banner("Running Totals"))
        print(f"  Bets: {totals.total_bets:<6}  Wins: {totals.total_wins:<6}  Losses: {totals.total_losses}")
        print(f"  Win rate: {format_percentage(totals.win_rate):<10}  Net P/L: {format_currency(totals.net_profit_loss)}")
        print(f"  Streak:   {'▲' * totals.consecutive_wins if totals.consecutive_wins else '▼' * totals.consecutive_losses}")

    @staticmethod
    def show_stop_condition(reason: str) -> None:
        print(f"\n  {'!'*60}")
        print(f"  🛑  SESSION ENDED: {reason}")
        print(f"  {'!'*60}")
