"""
Business logic for gambler lifecycle: create, deposit, withdraw, retrieve.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List, Optional

from app.models.gambler_profile import GamblerProfile
from app.models.stake_transaction import StakeTransaction
from app.models.transaction_type import TransactionType
from app.repository.gambler_repository import GamblerRepository
from app.repository.stake_repository import StakeRepository
from app.validation.exceptions import (
    GamblerNotFoundError,
    InsufficientFundsError,
    InvalidAmountError,
)
from app.validation.input_validator import InputValidator

logger = logging.getLogger(__name__)


class GamblerService:
    def __init__(self) -> None:
        self._gamblers   = GamblerRepository()
        self._stake_repo = StakeRepository()

    # ── Create ───────────────────────────────────────────────────────────────
    def create_gambler(self, username: str, email: str,
                       initial_bankroll: Decimal) -> GamblerProfile:
        ur = InputValidator.validate_username(username)
        if not ur.is_valid:
            raise InvalidAmountError(ur.first_error(), "username")
        er = InputValidator.validate_email(email)
        if not er.is_valid:
            raise InvalidAmountError(er.first_error(), "email")
        br = InputValidator.validate_bankroll(str(initial_bankroll))
        if not br.is_valid:
            raise InvalidAmountError(br.first_error(), "initial_bankroll")

        profile = GamblerProfile(
            username         = username.strip(),
            email            = email.strip().lower(),
            initial_bankroll = initial_bankroll,
            current_bankroll = initial_bankroll,
        )
        created = self._gamblers.create_gambler(profile)

        # Record deposit transaction
        tx = StakeTransaction(
            gambler_id       = created.id,
            transaction_type = TransactionType.DEPOSIT,
            amount           = initial_bankroll,
            balance_before   = Decimal("0"),
            balance_after    = initial_bankroll,
            description      = "Initial bankroll deposit",
        )
        self._stake_repo.create_transaction(tx)
        logger.info("Gambler created: %s", created)
        return created

    # ── Retrieve ─────────────────────────────────────────────────────────────
    def get_gambler(self, gambler_id: int) -> GamblerProfile:
        g = self._gamblers.get_gambler_by_id(gambler_id)
        if not g:
            raise GamblerNotFoundError(gambler_id)
        return g

    def get_by_username(self, username: str) -> GamblerProfile:
        g = self._gamblers.get_gambler_by_username(username)
        if not g:
            raise GamblerNotFoundError(username)
        return g

    def list_all(self) -> List[GamblerProfile]:
        return self._gamblers.get_all_gamblers()

    # ── Financial operations ─────────────────────────────────────────────────
    def deposit(self, gambler_id: int, amount: Decimal,
                session_id: Optional[int] = None) -> GamblerProfile:
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive.", "amount")
        gambler = self.get_gambler(gambler_id)
        before  = gambler.current_bankroll
        after   = before + amount
        self._gamblers.update_bankroll(gambler_id, after)
        self._stake_repo.create_transaction(StakeTransaction(
            gambler_id       = gambler_id,
            session_id       = session_id,
            transaction_type = TransactionType.DEPOSIT,
            amount           = amount,
            balance_before   = before,
            balance_after    = after,
            description      = f"Deposit of {amount:.2f}",
        ))
        gambler.current_bankroll = after
        return gambler

    def withdraw(self, gambler_id: int, amount: Decimal,
                 session_id: Optional[int] = None) -> GamblerProfile:
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive.", "amount")
        gambler = self.get_gambler(gambler_id)
        if gambler.current_bankroll < amount:
            raise InsufficientFundsError(gambler.current_bankroll, amount)
        before = gambler.current_bankroll
        after  = before - amount
        self._gamblers.update_bankroll(gambler_id, after)
        self._stake_repo.create_transaction(StakeTransaction(
            gambler_id       = gambler_id,
            session_id       = session_id,
            transaction_type = TransactionType.WITHDRAWAL,
            amount           = amount,
            balance_before   = before,
            balance_after    = after,
            description      = f"Withdrawal of {amount:.2f}",
        ))
        gambler.current_bankroll = after
        return gambler

    def get_transaction_history(self, gambler_id: int):
        return self._stake_repo.get_transactions_by_gambler(gambler_id)
