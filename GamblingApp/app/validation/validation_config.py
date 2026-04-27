from decimal import Decimal


class ValidationConfig:
    # Bankroll
    MIN_BANKROLL: Decimal = Decimal("1.00")
    MAX_BANKROLL: Decimal = Decimal("10_000_000.00")

    # Stake
    MIN_STAKE: Decimal = Decimal("0.01")
    MAX_STAKE: Decimal = Decimal("1_000_000.00")

    # Probability
    MIN_PROBABILITY: float = 0.01
    MAX_PROBABILITY: float = 0.99

    # Payout multiplier
    MIN_PAYOUT: Decimal = Decimal("1.01")
    MAX_PAYOUT: Decimal = Decimal("1000.00")

    # Percentage strategy
    MIN_PERCENTAGE: Decimal = Decimal("0.001")   # 0.1 %
    MAX_PERCENTAGE: Decimal = Decimal("1.000")   # 100 %

    # Rounds
    MIN_ROUNDS: int = 1
    MAX_ROUNDS: int = 100_000

    # Username
    MIN_USERNAME_LEN: int = 3
    MAX_USERNAME_LEN: int = 100

    # Email
    MIN_EMAIL_LEN: int = 6
    MAX_EMAIL_LEN: int = 255

    # Session name
    MAX_SESSION_NAME_LEN: int = 255
