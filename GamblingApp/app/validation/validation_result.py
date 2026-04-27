from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from app.validation.validation_error_type import ValidationErrorType


@dataclass
class ValidationError:
    error_type: ValidationErrorType
    message:    str
    field:      str = ""

    def __str__(self) -> str:
        prefix = f"[{self.field}] " if self.field else ""
        return f"{prefix}{self.message}"


@dataclass
class ValidationResult:
    is_valid: bool                    = True
    errors:   List[ValidationError]   = field(default_factory=list)
    value:    Any                     = None

    def add_error(self, error_type: ValidationErrorType, message: str, field: str = "") -> None:
        self.errors.append(ValidationError(error_type, message, field))
        self.is_valid = False

    def error_messages(self) -> List[str]:
        return [str(e) for e in self.errors]

    def first_error(self) -> str:
        return str(self.errors[0]) if self.errors else ""

    def __bool__(self) -> bool:
        return self.is_valid
