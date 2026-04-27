"""
Martingale: double the stake after every loss; reset to base_stake on a win.
"""
from decimal import Decimal

from app.models.running_totals import RunningTotals
from app.models.session_enums import StrategyType
from app.models.stake_boundary import StakeBoundary
from app.strategies.base_strategy import BaseStrategy


class MartingaleStrategy(BaseStrategy):
    strategy_type = StrategyType.MARTINGALE

    def __init__(self, base_stake: Decimal, boundary: StakeBoundary) -> None:
        super().__init__(base_stake, boundary)
        self._current_stake = base_stake

    def next_stake(self, totals: RunningTotals) -> Decimal:
        if totals.total_bets == 0:
            # First round
            self._current_stake = self.base_stake
        elif totals.consecutive_losses > 0:
            # Lost last round – double up
            self._current_stake = self._current_stake * Decimal("2")
        else:
            # Won last round – reset
            self._current_stake = self.base_stake

        return self.apply_boundary(self._current_stake)

    def reset(self) -> None:
        self._current_stake = self.base_stake
