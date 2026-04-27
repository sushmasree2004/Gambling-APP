"""
Weighted Probability: scale the stake based on the configured win probability.

Higher win probability  → bet closer to max_stake.
Lower  win probability  → bet closer to min_stake.
At exactly 50 % probability → bet the base_stake.
"""
from decimal import Decimal

from app.models.running_totals import RunningTotals
from app.models.session_enums import StrategyType
from app.models.stake_boundary import StakeBoundary
from app.strategies.base_strategy import BaseStrategy


class WeightedProbabilityStrategy(BaseStrategy):
    strategy_type = StrategyType.WEIGHTED_PROBABILITY

    def __init__(self, base_stake: Decimal, boundary: StakeBoundary,
                 win_probability: float = 0.50) -> None:
        super().__init__(base_stake, boundary)
        self.win_probability = max(0.01, min(0.99, win_probability))

    def next_stake(self, totals: RunningTotals) -> Decimal:
        """
        Linear interpolation:
          p=0.01  → min_stake
          p=0.50  → base_stake
          p=0.99  → max_stake
        """
        p   = Decimal(str(self.win_probability))
        lo  = self.boundary.min_stake
        hi  = self.boundary.max_stake
        mid = self.base_stake

        if p <= Decimal("0.50"):
            # interpolate between lo and mid
            t = (p - Decimal("0.01")) / (Decimal("0.50") - Decimal("0.01"))
            stake = lo + t * (mid - lo)
        else:
            # interpolate between mid and hi
            t = (p - Decimal("0.50")) / (Decimal("0.99") - Decimal("0.50"))
            stake = mid + t * (hi - mid)

        stake = stake.quantize(Decimal("0.01"))
        return self.apply_boundary(stake)
