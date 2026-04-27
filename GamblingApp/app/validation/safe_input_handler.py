"""
SafeInputHandler – wraps input() with validation loops so the UI
layer never crashes on bad user input.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Callable, List, Optional, Tuple, TypeVar

from app.validation.input_validator import InputValidator

T = TypeVar("T")
_MAX_RETRIES = 5


class SafeInputHandler:
    """Helper for robust terminal input collection."""

    @staticmethod
    def _prompt_loop(prompt: str,
                     validator: Callable[[str], Tuple[bool, T, str]],
                     retries: int = _MAX_RETRIES) -> Optional[T]:
        for _ in range(retries):
            raw = input(prompt).strip()
            ok, value, msg = validator(raw)
            if ok:
                return value
            print(f"  ✗ {msg}")
        print("  Too many invalid attempts.")
        return None

    # ── Public helpers ───────────────────────────────────────────────────────
    @classmethod
    def get_decimal(cls, prompt: str,
                    min_val: Decimal = Decimal("0.01"),
                    max_val: Decimal = Decimal("10000000")) -> Optional[Decimal]:
        def _validate(raw: str):
            result = InputValidator.validate_positive_decimal(raw)
            if not result.is_valid:
                return False, None, result.first_error()
            v: Decimal = result.value
            if v < min_val or v > max_val:
                return False, None, f"Value must be between {min_val} and {max_val}."
            return True, v, ""
        return cls._prompt_loop(prompt, _validate)

    @classmethod
    def get_int(cls, prompt: str,
                min_val: int = 1, max_val: int = 1_000_000) -> Optional[int]:
        def _validate(raw: str):
            result = InputValidator.validate_positive_int(raw, min_val=min_val, max_val=max_val)
            if not result.is_valid:
                return False, None, result.first_error()
            return True, result.value, ""
        return cls._prompt_loop(prompt, _validate)

    @classmethod
    def get_float_range(cls, prompt: str,
                        min_val: float = 0.0, max_val: float = 1.0) -> Optional[float]:
        def _validate(raw: str):
            try:
                v = float(raw.strip())
            except ValueError:
                return False, None, "Please enter a valid number."
            if not min_val <= v <= max_val:
                return False, None, f"Must be between {min_val} and {max_val}."
            return True, v, ""
        return cls._prompt_loop(prompt, _validate)

    @classmethod
    def get_string(cls, prompt: str,
                   min_len: int = 1, max_len: int = 255) -> Optional[str]:
        def _validate(raw: str):
            if len(raw) < min_len:
                return False, None, f"Must be at least {min_len} characters."
            if len(raw) > max_len:
                return False, None, f"Must be at most {max_len} characters."
            return True, raw, ""
        return cls._prompt_loop(prompt, _validate)

    @classmethod
    def get_username(cls, prompt: str = "Username: ") -> Optional[str]:
        def _validate(raw: str):
            result = InputValidator.validate_username(raw)
            if not result.is_valid:
                return False, None, result.first_error()
            return True, result.value, ""
        return cls._prompt_loop(prompt, _validate)

    @classmethod
    def get_email(cls, prompt: str = "Email: ") -> Optional[str]:
        def _validate(raw: str):
            result = InputValidator.validate_email(raw)
            if not result.is_valid:
                return False, None, result.first_error()
            return True, result.value, ""
        return cls._prompt_loop(prompt, _validate)

    @classmethod
    def get_choice(cls, prompt: str, choices: List[str]) -> Optional[str]:
        choices_lower = [c.lower() for c in choices]
        def _validate(raw: str):
            v = raw.strip().lower()
            if v not in choices_lower:
                return False, None, f"Please enter one of: {', '.join(choices)}"
            return True, choices[choices_lower.index(v)], ""
        return cls._prompt_loop(prompt, _validate)

    @classmethod
    def get_yes_no(cls, prompt: str) -> bool:
        result = cls.get_choice(prompt + " [y/n]: ", ["y", "n"])
        return result == "y"

    @classmethod
    def get_menu_choice(cls, prompt: str, valid_range: range) -> Optional[int]:
        def _validate(raw: str):
            try:
                v = int(raw.strip())
            except ValueError:
                return False, None, "Please enter a number."
            if v not in valid_range:
                return False, None, f"Please enter a number between {valid_range.start} and {valid_range.stop - 1}."
            return True, v, ""
        return cls._prompt_loop(prompt, _validate)
