"""
Stateless input validation functions; return ValidationResult objects.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from app.models.stake_boundary import StakeBoundary
from app.validation.validation_config import ValidationConfig
from app.validation.validation_error_type import ValidationErrorType
from app.validation.validation_result import ValidationResult

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class InputValidator:
    cfg = ValidationConfig()

    # ── Money / bankroll ────────────────────────────────────────────────────
    @staticmethod
    def validate_bankroll(raw: str) -> ValidationResult:
        result = ValidationResult()
        try:
            amount = Decimal(raw.strip())
        except InvalidOperation:
            result.add_error(ValidationErrorType.INVALID_AMOUNT,
                             "Bankroll must be a valid number.", "bankroll")
            return result
        if amount < ValidationConfig.MIN_BANKROLL:
            result.add_error(ValidationErrorType.INVALID_AMOUNT,
                             f"Bankroll must be at least {ValidationConfig.MIN_BANKROLL}.", "bankroll")
        elif amount > ValidationConfig.MAX_BANKROLL:
            result.add_error(ValidationErrorType.INVALID_AMOUNT,
                             f"Bankroll may not exceed {ValidationConfig.MAX_BANKROLL}.", "bankroll")
        else:
            result.value = amount
        return result

    @staticmethod
    def validate_stake(raw: str, boundary: Optional[StakeBoundary] = None) -> ValidationResult:
        result = ValidationResult()
        try:
            amount = Decimal(raw.strip())
        except InvalidOperation:
            result.add_error(ValidationErrorType.INVALID_STAKE,
                             "Stake must be a valid number.", "stake")
            return result
        if amount < ValidationConfig.MIN_STAKE:
            result.add_error(ValidationErrorType.INVALID_STAKE,
                             f"Stake must be at least {ValidationConfig.MIN_STAKE}.", "stake")
            return result
        if boundary and not boundary.is_within(amount):
            result.add_error(ValidationErrorType.BOUNDARY_VIOLATION,
                             f"Stake must be in [{boundary.min_stake}, {boundary.max_stake}].", "stake")
            return result
        result.value = amount
        return result

    @staticmethod
    def validate_positive_decimal(raw: str, field: str = "value") -> ValidationResult:
        result = ValidationResult()
        try:
            v = Decimal(raw.strip())
        except InvalidOperation:
            result.add_error(ValidationErrorType.INVALID_AMOUNT,
                             f"{field} must be a valid number.", field)
            return result
        if v <= 0:
            result.add_error(ValidationErrorType.INVALID_AMOUNT,
                             f"{field} must be positive.", field)
            return result
        result.value = v
        return result

    # ── String fields ───────────────────────────────────────────────────────
    @staticmethod
    def validate_username(raw: str) -> ValidationResult:
        result = ValidationResult()
        username = raw.strip()
        if len(username) < ValidationConfig.MIN_USERNAME_LEN:
            result.add_error(ValidationErrorType.INVALID_USERNAME,
                             f"Username must be at least {ValidationConfig.MIN_USERNAME_LEN} characters.", "username")
        elif len(username) > ValidationConfig.MAX_USERNAME_LEN:
            result.add_error(ValidationErrorType.INVALID_USERNAME,
                             f"Username must be at most {ValidationConfig.MAX_USERNAME_LEN} characters.", "username")
        elif not re.match(r"^[A-Za-z0-9_.-]+$", username):
            result.add_error(ValidationErrorType.INVALID_USERNAME,
                             "Username may only contain letters, digits, _, ., -", "username")
        else:
            result.value = username
        return result

    @staticmethod
    def validate_email(raw: str) -> ValidationResult:
        result = ValidationResult()
        email = raw.strip().lower()
        if not _EMAIL_PATTERN.match(email):
            result.add_error(ValidationErrorType.INVALID_EMAIL,
                             "Please enter a valid email address.", "email")
        elif len(email) > ValidationConfig.MAX_EMAIL_LEN:
            result.add_error(ValidationErrorType.INVALID_EMAIL,
                             f"Email must not exceed {ValidationConfig.MAX_EMAIL_LEN} characters.", "email")
        else:
            result.value = email
        return result

    # ── Numeric ranges ───────────────────────────────────────────────────────
    @staticmethod
    def validate_probability(raw: str) -> ValidationResult:
        result = ValidationResult()
        try:
            p = float(raw.strip())
        except ValueError:
            result.add_error(ValidationErrorType.INVALID_PROBABILITY,
                             "Probability must be a number.", "probability")
            return result
        lo, hi = ValidationConfig.MIN_PROBABILITY, ValidationConfig.MAX_PROBABILITY
        if not lo <= p <= hi:
            result.add_error(ValidationErrorType.INVALID_PROBABILITY,
                             f"Probability must be between {lo} and {hi}.", "probability")
            return result
        result.value = p
        return result

    @staticmethod
    def validate_positive_int(raw: str, field: str = "value",
                              min_val: int = 1, max_val: int = 1_000_000) -> ValidationResult:
        result = ValidationResult()
        try:
            v = int(raw.strip())
        except ValueError:
            result.add_error(ValidationErrorType.INVALID_RANGE,
                             f"{field} must be an integer.", field)
            return result
        if not min_val <= v <= max_val:
            result.add_error(ValidationErrorType.INVALID_RANGE,
                             f"{field} must be between {min_val} and {max_val}.", field)
            return result
        result.value = v
        return result
