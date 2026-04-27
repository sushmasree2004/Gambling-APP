"""
Repository for Bets, StakeTransactions, GameRecords, and PauseRecords.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List, Optional

import mysql.connector

from app.config.db_config import DatabaseConfig
from app.models.bet import Bet
from app.models.game_record import GameRecord
from app.models.game_result import GameResult
from app.models.pause_record import PauseRecord
from app.models.session_enums import GameType
from app.models.stake_transaction import StakeTransaction
from app.models.transaction_type import TransactionType
from app.validation.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class StakeRepository:

    @staticmethod
    def _conn():
        return DatabaseConfig.get_connection()

    # ================================================================
    # BETS
    # ================================================================

    def create_bet(self, bet: Bet) -> Bet:
        sql = """
            INSERT INTO bets
              (session_id, gambler_id, round_number, stake_amount,
               game_result, payout, profit_loss, bankroll_after, strategy_next_stake)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                bet.session_id, bet.gambler_id, bet.round_number,
                float(bet.stake_amount), bet.game_result.value,
                float(bet.payout), float(bet.profit_loss),
                float(bet.bankroll_after),
                float(bet.strategy_next_stake) if bet.strategy_next_stake else None,
            ))
            conn.commit()
            bet.id = cursor.lastrowid
            return bet
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def get_bets_by_session(self, session_id: int) -> List[Bet]:
        sql = "SELECT * FROM bets WHERE session_id = %s ORDER BY round_number"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (session_id,))
            return [self._row_to_bet(r) for r in cursor.fetchall()]
        finally:
            cursor.close(); conn.close()

    def get_bet_count(self, session_id: int) -> int:
        sql = "SELECT COUNT(*) AS cnt FROM bets WHERE session_id = %s"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (session_id,))
            return cursor.fetchone()["cnt"]
        finally:
            cursor.close(); conn.close()

    @staticmethod
    def _row_to_bet(row: dict) -> Bet:
        return Bet(
            id                  = row["id"],
            session_id          = row["session_id"],
            gambler_id          = row["gambler_id"],
            round_number        = row["round_number"],
            stake_amount        = Decimal(str(row["stake_amount"])),
            game_result         = GameResult(row["game_result"]),
            payout              = Decimal(str(row["payout"])),
            profit_loss         = Decimal(str(row["profit_loss"])),
            bankroll_after      = Decimal(str(row["bankroll_after"])),
            strategy_next_stake = Decimal(str(row["strategy_next_stake"])) if row["strategy_next_stake"] else None,
            created_at          = row["created_at"],
        )

    # ================================================================
    # STAKE TRANSACTIONS
    # ================================================================

    def create_transaction(self, tx: StakeTransaction) -> StakeTransaction:
        sql = """
            INSERT INTO stake_transactions
              (gambler_id, session_id, transaction_type, amount,
               balance_before, balance_after, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                tx.gambler_id, tx.session_id, tx.transaction_type.value,
                float(tx.amount), float(tx.balance_before),
                float(tx.balance_after), tx.description,
            ))
            conn.commit()
            tx.id = cursor.lastrowid
            return tx
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def get_transactions_by_gambler(self, gambler_id: int) -> List[StakeTransaction]:
        sql = "SELECT * FROM stake_transactions WHERE gambler_id = %s ORDER BY created_at DESC"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (gambler_id,))
            return [self._row_to_tx(r) for r in cursor.fetchall()]
        finally:
            cursor.close(); conn.close()

    def get_transactions_by_session(self, session_id: int) -> List[StakeTransaction]:
        sql = "SELECT * FROM stake_transactions WHERE session_id = %s ORDER BY created_at"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (session_id,))
            return [self._row_to_tx(r) for r in cursor.fetchall()]
        finally:
            cursor.close(); conn.close()

    @staticmethod
    def _row_to_tx(row: dict) -> StakeTransaction:
        return StakeTransaction(
            id               = row["id"],
            gambler_id       = row["gambler_id"],
            session_id       = row["session_id"],
            transaction_type = TransactionType(row["transaction_type"]),
            amount           = Decimal(str(row["amount"])),
            balance_before   = Decimal(str(row["balance_before"])),
            balance_after    = Decimal(str(row["balance_after"])),
            description      = row["description"],
            created_at       = row["created_at"],
        )

    # ================================================================
    # GAME RECORDS
    # ================================================================

    def create_game_record(self, record: GameRecord) -> GameRecord:
        sql = """
            INSERT INTO game_records
              (session_id, bet_id, round_number, game_type,
               outcome, win_probability, random_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (
                record.session_id, record.bet_id, record.round_number,
                record.game_type.value, record.outcome.value,
                record.win_probability, record.random_value,
            ))
            conn.commit()
            record.id = cursor.lastrowid
            return record
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def get_game_records_by_session(self, session_id: int) -> List[GameRecord]:
        sql = "SELECT * FROM game_records WHERE session_id = %s ORDER BY round_number"
        conn = self._conn(); cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, (session_id,))
            return [self._row_to_record(r) for r in cursor.fetchall()]
        finally:
            cursor.close(); conn.close()

    @staticmethod
    def _row_to_record(row: dict) -> GameRecord:
        return GameRecord(
            id              = row["id"],
            session_id      = row["session_id"],
            bet_id          = row["bet_id"],
            round_number    = row["round_number"],
            game_type       = GameType(row["game_type"]),
            outcome         = GameResult(row["outcome"]),
            win_probability = float(row["win_probability"]) if row["win_probability"] else None,
            random_value    = float(row["random_value"])    if row["random_value"]    else None,
            created_at      = row["created_at"],
        )

    # ================================================================
    # PAUSE RECORDS
    # ================================================================

    def create_pause_record(self, record: PauseRecord) -> PauseRecord:
        sql = "INSERT INTO pause_records (session_id, reason) VALUES (%s, %s)"
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (record.session_id, record.reason))
            conn.commit()
            record.id = cursor.lastrowid
            return record
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()

    def resume_pause_record(self, session_id: int) -> bool:
        sql = "UPDATE pause_records SET resumed_at = NOW() WHERE session_id = %s AND resumed_at IS NULL"
        conn = self._conn(); cursor = conn.cursor()
        try:
            cursor.execute(sql, (session_id,))
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as exc:
            conn.rollback(); raise DatabaseError(str(exc)) from exc
        finally:
            cursor.close(); conn.close()
