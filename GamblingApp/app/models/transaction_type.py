from enum import Enum


class TransactionType(str, Enum):
    DEPOSIT    = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    BET        = "BET"
    WIN        = "WIN"
    LOSS       = "LOSS"
