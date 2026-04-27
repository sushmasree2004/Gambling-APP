"""
Random Outcome: bet a random amount uniformly drawn from [min_stake, max_stake].
"""
import random
from decimal import Decimal

from app.models.running_totals import RunningTotals
from app.models.session_enums import StrategyType
from app.models.stake_boundary import StakeBoundary
from app.strategies.base_strategy import BaseStrategy


class RandomOutcomeStrategy(BaseStrategy):
    strategy_type = StrategyType.RANDOM_OUTCOME

    def next_stake(self, totals: RunningTotals) -> Decimal:
        lo = float(self.boundary.min_stake)
        hi = float(self.boundary.max_stake)
        stake = Decimal(str(round(random.uniform(lo, hi), 2)))
        return self.apply_boundary(stake)
