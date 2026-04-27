"""
Fixed: always bet the base_stake regardless of history.
"""
from decimal import Decimal

from app.models.running_totals import RunningTotals
from app.models.session_enums import StrategyType
from app.models.stake_boundary import StakeBoundary
from app.strategies.base_strategy import BaseStrategy


class FixedStrategy(BaseStrategy):
    strategy_type = StrategyType.FIXED

    def next_stake(self, totals: RunningTotals) -> Decimal:
        return self.apply_boundary(self.base_stake)
