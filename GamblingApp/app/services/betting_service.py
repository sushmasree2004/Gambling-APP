"""
Business logic for placing bets and recording results.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List

from app.models.bet import Bet
from app.models.game_record import GameRecord
from app.models.game_result import GameResult
from app.models.stake_transaction import StakeTransaction
from app.models.transaction_type import TransactionType
from app.repository.stake_repository import StakeRepository
from app.validation.exceptions import InvalidStakeError

logger = logging.getLogger(__name__)


class BettingService:
    def __init__(self) -> None:
        self._repo = StakeRepository()

    # ── Core bet placement ───────────────────────────────────────────────────
    def place_bet(
        self,
        session_id:     int,
        gambler_id:     int,
        round_number:   int,
        stake_amount:   Decimal,
        game_result:    GameResult,
        payout_multiplier: Decimal,
        bankroll_before:   Decimal,
    ) -> Bet:
        """
        Persist a bet record.  Returns the saved Bet with DB-assigned id.
        """
        if stake_amount <= 0:
            raise InvalidStakeError("Stake amount must be positive.", "stake_amount")
        if stake_amount > bankroll_before:
            raise InvalidStakeError(
                f"Stake {stake_amount:.2f} exceeds bankroll {bankroll_before:.2f}.",
                "stake_amount",
            )

        payout      = self._calc_payout(stake_amount, game_result, payout_multiplier)
        profit_loss = payout - stake_amount if game_result == GameResult.WIN else -stake_amount
        bankroll_after = bankroll_before + profit_loss

        bet = Bet(
            session_id     = session_id,
            gambler_id     = gambler_id,
            round_number   = round_number,
            stake_amount   = stake_amount,
            game_result    = game_result,
            payout         = payout,
            profit_loss    = profit_loss,
            bankroll_after = bankroll_after,
        )
        saved = self._repo.create_bet(bet)
        logger.debug("Bet saved: round=%s result=%s stake=%s", round_number, game_result.value, stake_amount)
        return saved

    def record_game(
        self,
        session_id:      int,
        bet_id:          int,
        round_number:    int,
        outcome:         GameResult,
        win_probability: float,
        random_value:    float,
    ) -> GameRecord:
        record = GameRecord(
            session_id      = session_id,
            bet_id          = bet_id,
            round_number    = round_number,
            outcome         = outcome,
            win_probability = win_probability,
            random_value    = random_value,
        )
        return self._repo.create_game_record(record)

    def record_transaction(self, tx: StakeTransaction) -> StakeTransaction:
        return self._repo.create_transaction(tx)

    # ── Queries ──────────────────────────────────────────────────────────────
    def get_session_bets(self, session_id: int) -> List[Bet]:
        return self._repo.get_bets_by_session(session_id)

    def get_bet_count(self, session_id: int) -> int:
        return self._repo.get_bet_count(session_id)

    # ── Helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _calc_payout(stake: Decimal, result: GameResult,
                     multiplier: Decimal) -> Decimal:
        """WIN: payout = stake × multiplier. LOSS: payout = 0."""
        if result == GameResult.WIN:
            return (stake * multiplier).quantize(Decimal("0.01"))
        return Decimal("0")
