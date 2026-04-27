"""
Repository for Gamblers, BettingSessions, and WinLossStatistics.
All DB interaction is here – services never touch the cursor directly.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List, Optional

import mysql.connector

from app.config.db_config import DatabaseConfig
from app.models.betting_preferences import BettingPreferences
from app.models.betting_session import BettingSession
from app.models.gambler_profile import GamblerProfile
from app.models.odds_config import OddsConfig
from app.models.session_enums import GameType, SessionStatus, StrategyType
from app.models.session_parameters import SessionParameters
from app.models.stake_boundary import StakeBoundary
from app.models.win_loss_statistics import WinLossStatistics
from app.validation.exceptions import DatabaseError, DuplicateRecordError, GamblerNotFoundError, SessionNotFoundError

logger = logging.getLogger(__name__)


class GamblerRepository:
    """CRUD operations for gamblers, sessions, and win/loss stats."""

    # ── Internal helper ──────────────────────────────────────────────────────
    @staticmethod
    def _conn():
        return DatabaseConfig.get_connection()

    # ================================================================
    # GAMBLERS
    # ================================================================

    def create_gambler(self, gambler: GamblerProfile) -> GamblerProfile:
        sql = """
            INSERT INTO gamblers (username, email, initial_bankroll, current_bankroll)
            VALUES (%s, %s, %s, %s)
        """
        conn = self._conn()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                gambler.username,
                gambler.email,
                float(gambler.initial_bankroll),
                float(gambler.current_bankroll),
            ))
            conn.commit()
            gambler.id = cursor.lastrowid
            logger.info("Created gambler id=%s username=%s", gambler.id, gambler.username)
            return gambler
        except mysql.connector.IntegrityError as exc:
            conn.rollback()
            raise DuplicateRecordError("Gambler", "username/email", gambler.username) from exc
        except mysql.connector.Error as exc:
            conn.rollback()
            raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def get_gambler_by_id(self, gambler_id: int) -> Optional[GamblerProfile]:
        sql = "SELECT id, username, email, initial_bankroll, current_bankroll, created_at, is_active FROM gamblers WHERE id = %s"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (gambler_id,))
            row = cursor.fetchone()
            return self._row_to_gambler(row) if row else None
        finally:
            cursor.close(); conn.close()

    def get_gambler_by_username(self, username: str) -> Optional[GamblerProfile]:
        sql = "SELECT id, username, email, initial_bankroll, current_bankroll, created_at, is_active FROM gamblers WHERE username = %s"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            return self._row_to_gambler(row) if row else None
        finally:
            cursor.close(); conn.close()

    def get_all_gamblers(self) -> List[GamblerProfile]:
        sql = "SELECT id, username, email, initial_bankroll, current_bankroll, created_at, is_active FROM gamblers WHERE is_active = TRUE ORDER BY created_at DESC"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            return [self._row_to_gambler(r) for r in cursor.fetchall()]
        finally:
            cursor.close(); conn.close()

    def update_bankroll(self, gambler_id: int, new_bankroll: Decimal) -> bool:
        sql = "UPDATE gamblers SET current_bankroll = %s WHERE id = %s"
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (float(new_bankroll), gambler_id))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def deactivate_gambler(self, gambler_id: int) -> bool:
        sql = "UPDATE gamblers SET is_active = FALSE WHERE id = %s"
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (gambler_id,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    @staticmethod
    def _row_to_gambler(row: dict) -> GamblerProfile:
        return GamblerProfile(
            id               = row["id"],
            username         = row["username"],
            email            = row["email"],
            initial_bankroll = Decimal(str(row["initial_bankroll"])),
            current_bankroll = Decimal(str(row["current_bankroll"])),
            created_at       = row["created_at"],
            is_active        = bool(row["is_active"]),
        )

    # ================================================================
    # BETTING SESSIONS
    # ================================================================

    def create_session(self, session: BettingSession) -> BettingSession:
        p = session.preferences
        sql = """
            INSERT INTO betting_sessions
              (gambler_id, session_name, strategy_type, initial_stake,
               min_stake, max_stake, stop_loss_threshold,
               take_profit_threshold, max_rounds,
               win_probability, payout_multiplier, strategy_param)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                session.gambler_id,
                session.session_name,
                p.strategy_type.value,
                float(p.initial_stake),
                float(p.stake_boundary.min_stake),
                float(p.stake_boundary.max_stake),
                float(p.session_parameters.stop_loss_threshold)   if p.session_parameters.stop_loss_threshold   else None,
                float(p.session_parameters.take_profit_threshold) if p.session_parameters.take_profit_threshold else None,
                p.session_parameters.max_rounds,
                p.odds_config.win_probability,
                float(p.odds_config.payout_multiplier),
                float(p.strategy_param) if p.strategy_param else None,
            ))
            conn.commit()
            session.id = cursor.lastrowid
            logger.info("Created session id=%s for gambler=%s", session.id, session.gambler_id)
            return session
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def get_session_by_id(self, session_id: int) -> Optional[BettingSession]:
        sql = "SELECT * FROM betting_sessions WHERE id = %s"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (session_id,))
            row = cursor.fetchone()
            return self._row_to_session(row) if row else None
        finally:
            cursor.close(); conn.close()

    def get_sessions_by_gambler(self, gambler_id: int) -> List[BettingSession]:
        sql = "SELECT * FROM betting_sessions WHERE gambler_id = %s ORDER BY started_at DESC"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (gambler_id,))
            return [self._row_to_session(r) for r in cursor.fetchall()]
        finally:
            cursor.close(); conn.close()

    def get_active_session(self, gambler_id: int) -> Optional[BettingSession]:
        sql = "SELECT * FROM betting_sessions WHERE gambler_id = %s AND status IN ('ACTIVE','PAUSED') LIMIT 1"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (gambler_id,))
            row = cursor.fetchone()
            return self._row_to_session(row) if row else None
        finally:
            cursor.close(); conn.close()

    def update_session_status(self, session_id: int, status: SessionStatus) -> bool:
        if status in (SessionStatus.STOPPED, SessionStatus.COMPLETED):
            sql = "UPDATE betting_sessions SET status = %s, ended_at = NOW() WHERE id = %s"
        else:
            sql = "UPDATE betting_sessions SET status = %s WHERE id = %s"
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (status.value, session_id))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    @staticmethod
    def _row_to_session(row: dict) -> BettingSession:
        sp = SessionParameters(
            stop_loss_threshold   = Decimal(str(row["stop_loss_threshold"]))   if row["stop_loss_threshold"]   else None,
            take_profit_threshold = Decimal(str(row["take_profit_threshold"])) if row["take_profit_threshold"] else None,
            max_rounds            = row["max_rounds"],
        )
        sb  = StakeBoundary(Decimal(str(row["min_stake"])), Decimal(str(row["max_stake"])))
        oc  = OddsConfig(
            win_probability   = float(row["win_probability"]),
            payout_multiplier = Decimal(str(row["payout_multiplier"])),
        )
        pref = BettingPreferences(
            strategy_type      = StrategyType(row["strategy_type"]),
            initial_stake      = Decimal(str(row["initial_stake"])),
            stake_boundary     = sb,
            session_parameters = sp,
            odds_config        = oc,
            strategy_param     = Decimal(str(row["strategy_param"])) if row.get("strategy_param") else None,
        )
        return BettingSession(
            id           = row["id"],
            gambler_id   = row["gambler_id"],
            session_name = row["session_name"] or "",
            preferences  = pref,
            status       = SessionStatus(row["status"]),
            started_at   = row["started_at"],
            ended_at     = row["ended_at"],
        )

    # ================================================================
    # WIN / LOSS STATISTICS
    # ================================================================

    def create_win_loss_stats(self, stats: WinLossStatistics) -> WinLossStatistics:
        sql = """
            INSERT INTO win_loss_statistics
              (session_id, gambler_id, total_bets, total_wins, total_losses,
               total_staked, total_payout, net_profit_loss, win_rate,
               max_win_streak, max_loss_streak,
               current_win_streak, current_loss_streak,
               peak_bankroll, lowest_bankroll)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                stats.session_id, stats.gambler_id,
                stats.total_bets, stats.total_wins, stats.total_losses,
                float(stats.total_staked), float(stats.total_payout),
                float(stats.net_profit_loss), float(stats.win_rate),
                stats.max_win_streak, stats.max_loss_streak,
                stats.current_win_streak, stats.current_loss_streak,
                float(stats.peak_bankroll), float(stats.lowest_bankroll),
            ))
            conn.commit()
            stats.id = cursor.lastrowid
            return stats
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def update_win_loss_stats(self, stats: WinLossStatistics) -> bool:
        sql = """
            UPDATE win_loss_statistics SET
              total_bets=%s, total_wins=%s, total_losses=%s,
              total_staked=%s, total_payout=%s, net_profit_loss=%s,
              win_rate=%s, max_win_streak=%s, max_loss_streak=%s,
              current_win_streak=%s, current_loss_streak=%s,
              peak_bankroll=%s, lowest_bankroll=%s
            WHERE session_id=%s
        """
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                stats.total_bets, stats.total_wins, stats.total_losses,
                float(stats.total_staked), float(stats.total_payout),
                float(stats.net_profit_loss), float(stats.win_rate),
                stats.max_win_streak, stats.max_loss_streak,
                stats.current_win_streak, stats.current_loss_streak,
                float(stats.peak_bankroll), float(stats.lowest_bankroll),
                stats.session_id,
            ))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def get_stats_by_session(self, session_id: int) -> Optional[WinLossStatistics]:
        sql = "SELECT * FROM win_loss_statistics WHERE session_id = %s"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return WinLossStatistics(
                id                  = row["id"],
                session_id          = row["session_id"],
                gambler_id          = row["gambler_id"],
                total_bets          = row["total_bets"],
                total_wins          = row["total_wins"],
                total_losses        = row["total_losses"],
                total_staked        = Decimal(str(row["total_staked"])),
                total_payout        = Decimal(str(row["total_payout"])),
                net_profit_loss     = Decimal(str(row["net_profit_loss"])),
                win_rate            = Decimal(str(row["win_rate"])),
                max_win_streak      = row["max_win_streak"],
                max_loss_streak     = row["max_loss_streak"],
                current_win_streak  = row["current_win_streak"],
                current_loss_streak = row["current_loss_streak"],
                peak_bankroll       = Decimal(str(row["peak_bankroll"])),
                lowest_bankroll     = Decimal(str(row["lowest_bankroll"])),
            )
        finally:
            cursor.close(); conn.close()
