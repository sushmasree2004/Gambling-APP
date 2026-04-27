"""
Central location for all application-level enumerations.
"""
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE    = "ACTIVE"
    PAUSED    = "PAUSED"
    STOPPED   = "STOPPED"
    COMPLETED = "COMPLETED"


class StrategyType(str, Enum):
    MARTINGALE           = "MARTINGALE"
    FIBONACCI            = "FIBONACCI"
    FIXED                = "FIXED"
    PERCENTAGE           = "PERCENTAGE"
    RANDOM_OUTCOME       = "RANDOM_OUTCOME"
    WEIGHTED_PROBABILITY = "WEIGHTED_PROBABILITY"


class GameType(str, Enum):
    COIN_FLIP = "COIN_FLIP"
    DICE_ROLL = "DICE_ROLL"
    ROULETTE  = "ROULETTE"
