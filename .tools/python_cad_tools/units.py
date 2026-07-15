"""Small dimension-safe unit types; the geometry kernel boundary is millimetres."""

from __future__ import annotations

from dataclasses import dataclass
from typing import overload


@dataclass(frozen=True, slots=True, order=True)
class Length:
    mm: float

    def __post_init__(self) -> None:
        if not isinstance(self.mm, (int, float)):
            raise TypeError("Length requires a numeric millimetre value")

    @overload
    def __mul__(self, other: float) -> Length: ...

    @overload
    def __mul__(self, other: Length) -> Area: ...

    def __mul__(self, other: float | Length) -> Length | Area:
        if isinstance(other, Length):
            return Area(self.mm * other.mm)
        if isinstance(other, (int, float)):
            return Length(self.mm * other)
        return NotImplemented

    def __rmul__(self, other: float) -> Length:
        return Length(self.mm * other)

    @overload
    def __truediv__(self, other: float) -> Length: ...

    @overload
    def __truediv__(self, other: Length) -> float: ...

    def __truediv__(self, other: float | Length) -> Length | float:
        if isinstance(other, Length):
            return self.mm / other.mm
        if isinstance(other, (int, float)):
            return Length(self.mm / other)
        return NotImplemented

    def __add__(self, other: Length) -> Length:
        if not isinstance(other, Length):
            return NotImplemented
        return Length(self.mm + other.mm)

    def __sub__(self, other: Length) -> Length:
        if not isinstance(other, Length):
            return NotImplemented
        return Length(self.mm - other.mm)

    def __neg__(self) -> Length:
        return Length(-self.mm)

    def __abs__(self) -> Length:
        return Length(abs(self.mm))

    def __float__(self) -> float:
        raise TypeError("Use to_mm(length) for an explicit kernel conversion")


@dataclass(frozen=True, slots=True)
class Area:
    mm2: float

    @overload
    def __mul__(self, other: float) -> Area: ...

    @overload
    def __mul__(self, other: Length) -> Volume: ...

    def __mul__(self, other: float | Length) -> Area | Volume:
        if isinstance(other, Length):
            return Volume(self.mm2 * other.mm)
        if isinstance(other, (int, float)):
            return Area(self.mm2 * other)
        return NotImplemented

    def __rmul__(self, other: float) -> Area:
        return Area(self.mm2 * other)


@dataclass(frozen=True, slots=True)
class Volume:
    mm3: float

    def __mul__(self, other: float) -> Volume:
        if not isinstance(other, (int, float)):
            return NotImplemented
        return Volume(self.mm3 * other)

    __rmul__ = __mul__


MM = Length(1.0)
INCH = Length(25.4)
FOOT = 12 * INCH


def to_mm(value: Length) -> float:
    if not isinstance(value, Length):
        raise TypeError(f"Expected Length, got {type(value).__name__}")
    return float(value.mm)


def mm(value: float) -> Length:
    return value * MM


def inches(value: float) -> Length:
    return value * INCH


def feet(value: float) -> Length:
    return value * FOOT


def feet_inches(feet_value: float, inches_value: float = 0) -> Length:
    return feet_value * FOOT + inches_value * INCH


def square_feet(value: Area) -> float:
    if not isinstance(value, Area):
        raise TypeError("square_feet expects Area")
    return value.mm2 / (304.8**2)


def cubic_feet(value: Volume) -> float:
    if not isinstance(value, Volume):
        raise TypeError("cubic_feet expects Volume")
    return value.mm3 / (304.8**3)


def cubic_yards(value: Volume) -> float:
    if not isinstance(value, Volume):
        raise TypeError("cubic_yards expects Volume")
    return value.mm3 / (914.4**3)


def metres(value: Length) -> float:
    return to_mm(value) / 1000.0


def square_metres(value: Area) -> float:
    if not isinstance(value, Area):
        raise TypeError("square_metres expects Area")
    return value.mm2 / 1_000_000.0


def cubic_metres(value: Volume) -> float:
    if not isinstance(value, Volume):
        raise TypeError("cubic_metres expects Volume")
    return value.mm3 / 1_000_000_000.0


def format_feet_inches(length_mm: float, denominator: int = 16) -> str:
    total_inches = length_mm / 25.4
    feet_part = int(total_inches // 12)
    inches_part = total_inches - feet_part * 12
    rounded = round(inches_part * denominator) / denominator
    if rounded >= 12:
        feet_part += 1
        rounded = 0
    whole = int(rounded)
    fraction = rounded - whole
    if fraction:
        numerator = round(fraction * denominator)
        from math import gcd

        divisor = gcd(numerator, denominator)
        inch_text = f"{whole} {numerator // divisor}/{denominator // divisor}"
    else:
        inch_text = str(whole)
    return f"{feet_part}'-{inch_text}\""
