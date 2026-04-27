"""
Manages the lifecycle of a BettingSession: start, pause, resume, stop.
Also evaluates stop-conditions after each round.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional

from app.models.betting_preferences import BettingPreferences
from app.models.betting_session import BettingSession
from app.models.pause_record import PauseRecord
from app.models.running_totals import RunningTotals
from app.models.session_enums import SessionStatus
from app.models.win_loss_statistics import WinLossStatistics
from app.repository.gambler_repository import GamblerRepository
from app.repository.stake_repository import StakeRepository
from app.services.win_loss_calculator import WinLossCalculator
from app.validation.exceptions import (
    GamblerNotFoundError,
    SessionAlreadyActiveError,
    SessionAlreadyPausedError,
    SessionError,
    SessionNotActiveError,
    SessionNotFoundError,
)

logger = logging.getLogger(__name__)


class GameSessionManager:
    def __init__(self) -> None:
        self._gambler_repo = GamblerRepository()
        self._stake_repo   = StakeRepository()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start_session(self, gambler_id: int, session_name: str,
                      preferences: BettingPreferences) -> BettingSession:
        gambler = self._gambler_repo.get_gambler_by_id(gambler_id)
        if not gambler:
            raise GamblerNotFoundError(gambler_id)

        existing = self._gambler_repo.get_active_session(gambler_id)
        if existing:
            raise SessionAlreadyActiveError()

        session = BettingSession(
            gambler_id   = gambler_id,
            session_name = session_name or f"Session for {gambler.username}",
            preferences  = preferences,
        )
        saved = self._gambler_repo.create_session(session)

        # Initialise stats row
        stats = WinLossStatistics(
            session_id   = saved.id,
            gambler_id   = gambler_id,
            peak_bankroll   = gambler.current_bankroll,
            lowest_bankroll = gambler.current_bankroll,
        )
        self._gambler_repo.create_win_loss_stats(stats)
        logger.info("Session %s started for gambler %s", saved.id, gambler_id)
        return saved

    def pause_session(self, session_id: int, reason: str = "") -> bool:
        session = self._get_or_raise(session_id)
        if session.status == SessionStatus.PAUSED:
            raise SessionAlreadyPausedError()
        if not session.is_active:
            raise SessionNotActiveError()
        self._gambler_repo.update_session_status(session_id, SessionStatus.PAUSED)
        self._stake_repo.create_pause_record(PauseRecord(session_id=session_id, reason=reason))
        logger.info("Session %s paused.", session_id)
        return True

    def resume_session(self, session_id: int) -> bool:
        session = self._get_or_raise(session_id)
        if session.status != SessionStatus.PAUSED:
            raise SessionError("Session is not paused.")
        self._gambler_repo.update_session_status(session_id, SessionStatus.ACTIVE)
        self._stake_repo.resume_pause_record(session_id)
        logger.info("Session %s resumed.", session_id)
        return True

    def end_session(self, session_id: int,
                    totals: RunningTotals,
                    status: SessionStatus = SessionStatus.COMPLETED) -> WinLossStatistics:
        session = self._get_or_raise(session_id)
        self._gambler_repo.update_session_status(session_id, status)

        # Persist final stats
        stats = WinLossCalculator.from_running_totals(
            totals, session_id, session.gambler_id
        )
        existing = self._gambler_repo.get_stats_by_session(session_id)
        if existing:
            stats.id = existing.id
            self._gambler_repo.update_win_loss_stats(stats)
        else:
            self._gambler_repo.create_win_loss_stats(stats)

        # Sync gambler's bankroll
        self._gambler_repo.update_bankroll(session.gambler_id, totals.current_bankroll)
        logger.info("Session %s ended with status %s.", session_id, status.value)
        return stats

    # ── Stop-condition evaluation ─────────────────────────────────────────────

    @staticmethod
    def should_stop(totals: RunningTotals, session: BettingSession) -> tuple[bool, str]:
        """
        Returns (should_stop: bool, reason: str).
        """
        p = session.preferences.session_parameters

        # Bankrupt
        if totals.current_bankroll <= Decimal("0"):
            return True, "Bankrupt – bankroll reached zero."

        # Stop-loss
        if (p.stop_loss_threshold is not None
                and totals.current_bankroll <= p.stop_loss_threshold):
            return True, f"Stop-loss triggered at {totals.current_bankroll:.2f}."

        # Take-profit
        if (p.take_profit_threshold is not None
                and totals.current_bankroll >= p.take_profit_threshold):
            return True, f"Take-profit triggered at {totals.current_bankroll:.2f}."

        # Max rounds
        if (p.max_rounds is not None
                and totals.round_number >= p.max_rounds):
            return True, f"Max rounds ({p.max_rounds}) reached."

        return False, ""

    # ── Queries ──────────────────────────────────────────────────────────────

    def get_session(self, session_id: int) -> BettingSession:
        return self._get_or_raise(session_id)

    def get_active_session(self, gambler_id: int) -> Optional[BettingSession]:
        return self._gambler_repo.get_active_session(gambler_id)

    def get_all_sessions(self, gambler_id: int):
        return self._gambler_repo.get_sessions_by_gambler(gambler_id)

    def get_stats(self, session_id: int) -> Optional[WinLossStatistics]:
        return self._gambler_repo.get_stats_by_session(session_id)

    # ── Private ──────────────────────────────────────────────────────────────
    def _get_or_raise(self, session_id: int) -> BettingSession:
        session = self._gambler_repo.get_session_by_id(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        return session
