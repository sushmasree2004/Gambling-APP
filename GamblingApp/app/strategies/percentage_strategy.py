"""
Percentage (Kelly-inspired): bet a fixed percentage of the current bankroll.
"""
from decimal import Decimal

from app.models.running_totals import RunningTotals
from app.models.session_enums import StrategyType
from app.models.stake_boundary import StakeBoundary
from app.strategies.base_strategy import BaseStrategy


class PercentageStrategy(BaseStrategy):
    strategy_type = StrategyType.PERCENTAGE

    def __init__(self, base_stake: Decimal, boundary: StakeBoundary,
                 percentage: Decimal = Decimal("0.05")) -> None:
        """
        Args:
            percentage: fraction of bankroll to bet, e.g. 0.05 = 5 %.
        """
        super().__init__(base_stake, boundary)
        self.percentage = percentage

    def next_stake(self, totals: RunningTotals) -> Decimal:
        bankroll = totals.current_bankroll
        if bankroll <= Decimal("0"):
            return self.boundary.min_stake
        stake = (bankroll * self.percentage).quantize(Decimal("0.01"))
        return self.apply_boundary(stake)
