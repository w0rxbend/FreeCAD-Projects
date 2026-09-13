"""Dimension validation at immutable parameter construction boundaries."""

from math import isfinite


def finite(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")


def positive(name: str, value: float) -> None:
    finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def nonnegative(name: str, value: float) -> None:
    finite(name, value)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
