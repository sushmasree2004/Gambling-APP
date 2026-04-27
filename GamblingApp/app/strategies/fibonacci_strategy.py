"""
Fibonacci: advance one step in the Fibonacci sequence on each loss;
retreat two steps on a win; reset to position 0 on two or fewer consecutive wins.
"""
from decimal import Decimal
from typing import List

from app.models.running_totals import RunningTotals
from app.models.session_enums import StrategyType
from app.models.stake_boundary import StakeBoundary
from app.strategies.base_strategy import BaseStrategy

_FIB_LIMIT = 30  # pre-compute this many terms


def _generate_fibonacci(n: int) -> List[int]:
    seq = [1, 1]
    for _ in range(n - 2):
        seq.append(seq[-1] + seq[-2])
    return seq


class FibonacciStrategy(BaseStrategy):
    strategy_type = StrategyType.FIBONACCI

    def __init__(self, base_stake: Decimal, boundary: StakeBoundary) -> None:
        super().__init__(base_stake, boundary)
        self._sequence: List[int] = _generate_fibonacci(_FIB_LIMIT)
        self._position: int = 0

    def next_stake(self, totals: RunningTotals) -> Decimal:
        if totals.total_bets == 0:
            self._position = 0
        elif totals.consecutive_losses > 0:
            # Advance
            self._position = min(self._position + 1, len(self._sequence) - 1)
        else:
            # Win – retreat 2 steps
            self._position = max(0, self._position - 2)

        multiplier = Decimal(str(self._sequence[self._position]))
        stake = self.base_stake * multiplier
        return self.apply_boundary(stake)

    def reset(self) -> None:
        self._position = 0
