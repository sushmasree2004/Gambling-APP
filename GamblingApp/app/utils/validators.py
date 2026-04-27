"""
Standalone utility functions used across layers.
"""
from __future__ import annotations

from decimal import Decimal


def format_currency(amount: Decimal | float, symbol: str = "$") -> str:
    return f"{symbol}{float(amount):,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    return f"{value * 100:.{decimals}f}%"


def clamp_decimal(value: Decimal, lo: Decimal, hi: Decimal) -> Decimal:
    return max(lo, min(hi, value))


def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default


def truncate_to_cents(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def banner(title: str, width: int = 60, char: str = "=") -> str:
    line = char * width
    padded = title.center(width)
    return f"\n{line}\n{padded}\n{line}"


def mini_banner(title: str, width: int = 60, char: str = "-") -> str:
    return f"\n{char * width}\n  {title}\n{char * width}"
