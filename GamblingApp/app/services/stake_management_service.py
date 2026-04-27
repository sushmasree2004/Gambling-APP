"""
Manages stake-level financial tracking:
records WIN/LOSS/BET transactions and syncs the gambler's bankroll.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List, Optional

from app.models.stake_transaction import StakeTransaction
from app.models.transaction_type import TransactionType
from app.repository.gambler_repository import GamblerRepository
from app.repository.stake_repository import StakeRepository

logger = logging.getLogger(__name__)


class StakeManagementService:
    def __init__(self) -> None:
        self._stake_repo   = StakeRepository()
        self._gambler_repo = GamblerRepository()

    # ── Per-round recording ──────────────────────────────────────────────────

    def record_bet(self, gambler_id: int, session_id: int,
                   stake_amount: Decimal, balance_before: Decimal) -> StakeTransaction:
        balance_after = balance_before - stake_amount
        return self._save(gambler_id, session_id, TransactionType.BET,
                          stake_amount, balance_before, balance_after,
                          f"Bet placed: {stake_amount:.2f}")

    def record_win(self, gambler_id: int, session_id: int,
                   payout: Decimal, balance_before: Decimal) -> StakeTransaction:
        balance_after = balance_before + payout
        self._gambler_repo.update_bankroll(gambler_id, balance_after)
        return self._save(gambler_id, session_id, TransactionType.WIN,
                          payout, balance_before, balance_after,
                          f"Win payout: {payout:.2f}")

    def record_loss(self, gambler_id: int, session_id: int,
                    stake_amount: Decimal, balance_before: Decimal) -> StakeTransaction:
        balance_after = balance_before - stake_amount
        self._gambler_repo.update_bankroll(gambler_id, balance_after)
        return self._save(gambler_id, session_id, TransactionType.LOSS,
                          stake_amount, balance_before, balance_after,
                          f"Loss: -{stake_amount:.2f}")

    def sync_bankroll(self, gambler_id: int, new_bankroll: Decimal) -> None:
        """Force-sync gambler's bankroll (e.g., after session ends)."""
        self._gambler_repo.update_bankroll(gambler_id, new_bankroll)

    # ── Queries ──────────────────────────────────────────────────────────────
    def get_history(self, gambler_id: int) -> List[StakeTransaction]:
        return self._stake_repo.get_transactions_by_gambler(gambler_id)

    def get_session_history(self, session_id: int) -> List[StakeTransaction]:
        return self._stake_repo.get_transactions_by_session(session_id)

    # ── Private ──────────────────────────────────────────────────────────────
    def _save(self, gambler_id, session_id, tx_type,
              amount, before, after, desc) -> StakeTransaction:
        tx = StakeTransaction(
            gambler_id       = gambler_id,
            session_id       = session_id,
            transaction_type = tx_type,
            amount           = amount,
            balance_before   = before,
            balance_after    = after,
            description      = desc,
        )
        return self._stake_repo.create_transaction(tx)
