"""
Full custom exception hierarchy for GamblingApp.
"""


# ── Root ────────────────────────────────────────────────────────────────────
class GamblingAppError(Exception):
    """Base for all application errors."""
    def __init__(self, message: str = "An application error occurred.") -> None:
        super().__init__(message)
        self.message = message


# ── Database ─────────────────────────────────────────────────────────────────
class DatabaseError(GamblingAppError):
    """Raised on any database-layer failure."""


class DatabaseConnectionError(DatabaseError):
    """Cannot connect to MySQL."""


class RecordNotFoundError(DatabaseError):
    """Expected row was missing."""
    def __init__(self, entity: str, identifier) -> None:
        super().__init__(f"{entity} with identifier '{identifier}' not found.")
        self.entity     = entity
        self.identifier = identifier


class DuplicateRecordError(DatabaseError):
    """Unique-constraint violation."""
    def __init__(self, entity: str, field: str, value) -> None:
        super().__init__(f"{entity} with {field}='{value}' already exists.")


# ── Validation ───────────────────────────────────────────────────────────────
class ValidationError(GamblingAppError):
    """Input failed validation."""
    def __init__(self, message: str, field: str = "") -> None:
        prefix = f"[{field}] " if field else ""
        super().__init__(f"{prefix}{message}")
        self.field = field


class InvalidAmountError(ValidationError):
    pass


class InvalidStakeError(ValidationError):
    pass


class InvalidProbabilityError(ValidationError):
    pass


# ── Business logic ────────────────────────────────────────────────────────────
class InsufficientFundsError(GamblingAppError):
    def __init__(self, available, required) -> None:
        super().__init__(
            f"Insufficient funds: available={available:.2f}, required={required:.2f}."
        )
        self.available = available
        self.required  = required


class GamblerNotFoundError(RecordNotFoundError):
    def __init__(self, identifier) -> None:
        super().__init__("Gambler", identifier)


class SessionNotFoundError(RecordNotFoundError):
    def __init__(self, session_id: int) -> None:
        super().__init__("BettingSession", session_id)


class SessionError(GamblingAppError):
    """General session lifecycle error."""


class SessionAlreadyActiveError(SessionError):
    def __init__(self) -> None:
        super().__init__("A session is already active for this gambler.")


class SessionNotActiveError(SessionError):
    def __init__(self) -> None:
        super().__init__("No active session found.")


class SessionAlreadyPausedError(SessionError):
    def __init__(self) -> None:
        super().__init__("Session is already paused.")


# ── Strategy ──────────────────────────────────────────────────────────────────
class StrategyError(GamblingAppError):
    """Strategy calculation errors."""


class BoundaryViolationError(StrategyError):
    def __init__(self, stake, boundary) -> None:
        super().__init__(
            f"Stake {stake} violates boundary [{boundary.min_stake}, {boundary.max_stake}]."
        )
