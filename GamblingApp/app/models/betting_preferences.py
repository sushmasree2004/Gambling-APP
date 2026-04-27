"""
All preferences that define how a betting session should run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from app.models.odds_config import OddsConfig
from app.models.session_enums import GameType, StrategyType
from app.models.session_parameters import SessionParameters
from app.models.stake_boundary import StakeBoundary


@dataclass
class BettingPreferences:
    strategy_type:      StrategyType
    initial_stake:      Decimal
    stake_boundary:     StakeBoundary
    session_parameters: SessionParameters
    odds_config:        OddsConfig          = field(default_factory=OddsConfig)
    game_type:          GameType            = GameType.COIN_FLIP
    strategy_param:     Optional[Decimal]   = None   # e.g. percentage for PercentageStrategy

    def to_dict(self) -> dict:
        return {
            "strategy_type":      self.strategy_type.value,
            "initial_stake":      float(self.initial_stake),
            "stake_boundary":     self.stake_boundary.to_dict(),
            "session_parameters": self.session_parameters.to_dict(),
            "odds_config":        self.odds_config.to_dict(),
            "game_type":          self.game_type.value,
            "strategy_param":     float(self.strategy_param) if self.strategy_param else None,
        }
