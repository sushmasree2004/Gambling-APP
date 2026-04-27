"""
SimpleGameEngine: drives a complete betting session round-by-round.
It is the orchestrator that uses all layers together.
"""
from __future__ import annotations

import random
import time
from decimal import Decimal
from typing import Optional, Tuple

from app.models.bet import Bet
from app.models.betting_session import BettingSession
from app.models.game_record import GameRecord
from app.models.game_result import GameResult
from app.models.gambler_profile import GamblerProfile
from app.models.running_totals import RunningTotals
from app.models.session_enums import SessionStatus
from app.models.stake_transaction import StakeTransaction
from app.models.transaction_type import TransactionType
from app.models.win_loss_statistics import WinLossStatistics
from app.services.betting_service import BettingService
from app.services.game_session_manager import GameSessionManager
from app.services.stake_management_service import StakeManagementService
from app.strategies.base_strategy import BaseStrategy
from app.strategies.outcome_base import OutcomeBase
from app.ui.game_status_display import GameStatusDisplay


class SimpleGameEngine:
    """
    Runs a betting session: generates outcomes, calls the strategy,
    persists each round, and enforces stop-conditions.
    """

    def __init__(self, delay_seconds: float = 0.0) -> None:
        self._betting_svc = BettingService()
        self._session_mgr = GameSessionManager()
        self._stake_svc   = StakeManagementService()
        self._display     = GameStatusDisplay()
        self._delay       = delay_seconds      # slow-mode for live demo

    # ── Public entry-point ───────────────────────────────────────────────────

    def run_session(
        self,
        session:   BettingSession,
        gambler:   GamblerProfile,
        strategy:  BaseStrategy,
        verbose:   bool = True,
    ) -> WinLossStatistics:
        """
        Runs every round until a stop-condition fires.
        Returns final WinLossStatistics.
        """
        totals = RunningTotals(current_bankroll=gambler.current_bankroll)
        strategy.reset()

        while True:
            # ── Calculate next stake ──────────────────────────────────────
            stake = strategy.next_stake(totals)

            # Cannot bet more than remaining bankroll
            stake = min(stake, totals.current_bankroll)
            if stake <= Decimal("0"):
                break

            totals.current_stake = stake
            round_num = totals.round_number + 1

            if verbose:
                self._display.round_header(round_num, strategy.__class__.__name__)
                self._display.show_bet_placed(float(stake), float(totals.current_bankroll))

            # ── Generate outcome ──────────────────────────────────────────
            outcome = self._generate_outcome(session.preferences.odds_config.win_probability)

            if verbose:
                self._display.show_outcome(
                    GameRecord(session_id=session.id, round_number=round_num,
                               outcome=outcome.result,
                               win_probability=outcome.win_probability,
                               random_value=outcome.random_value)
                )

            # ── Place bet & persist ───────────────────────────────────────
            bet = self._betting_svc.place_bet(
                session_id        = session.id,
                gambler_id        = gambler.id,
                round_number      = round_num,
                stake_amount      = stake,
                game_result       = outcome.result,
                payout_multiplier = session.preferences.odds_config.payout_multiplier,
                bankroll_before   = totals.current_bankroll,
            )

            # ── Record game log ───────────────────────────────────────────
            self._betting_svc.record_game(
                session_id      = session.id,
                bet_id          = bet.id,
                round_number    = round_num,
                outcome         = outcome.result,
                win_probability = outcome.win_probability,
                random_value    = outcome.random_value,
            )

            # ── Record financial transactions ─────────────────────────────
            bankroll_before = totals.current_bankroll
            if outcome.is_win:
                totals.record_win(stake, bet.payout)
                self._stake_svc.record_win(gambler.id, session.id,
                                           bet.payout, bankroll_before)
            else:
                totals.record_loss(stake)
                self._stake_svc.record_loss(gambler.id, session.id,
                                            stake, bankroll_before)

            # ── Update strategy with next-stake hint ──────────────────────
            next_hint = strategy.next_stake(totals)
            bet.strategy_next_stake = next_hint

            if verbose:
                self._display.show_bet_result(bet)
                self._display.show_running_totals(totals)

            # ── Evaluate stop-conditions ──────────────────────────────────
            stop, reason = GameSessionManager.should_stop(totals, session)
            if stop:
                if verbose:
                    self._display.show_stop_condition(reason)
                break

            if self._delay:
                time.sleep(self._delay)

        # ── Finalise session ──────────────────────────────────────────────
        final_stats = self._session_mgr.end_session(
            session.id, totals, status=SessionStatus.COMPLETED
        )
        return final_stats

    # ── Round-level helpers (also callable standalone) ────────────────────────

    @staticmethod
    def _generate_outcome(win_probability: float) -> OutcomeBase:
        rv     = random.random()
        result = GameResult.WIN if rv < win_probability else GameResult.LOSS
        return OutcomeBase(
            result          = result,
            random_value    = rv,
            win_probability = win_probability,
        )
