"""
This module provides common numeric type definitions, constants and functions.
"""

__all__ = ["Numeric", "MaxPrecision", "MaxPrecisionQuantizer", "ZERO", "ONE", "HUNDRED", "CENT", "make_quantizer"]

from decimal import Decimal
from typing import Union

#: Defines a type alias for acceptable numeric values.
Numeric = Union[Decimal, int, float]

#: Defines the decimal constant for 0.
ZERO = Decimal("0")

#: Defines the decimal constant for 0.01.
CENT = Decimal("0.01")

#: Defines the decimal constant for 1.
ONE = Decimal("1")

#: Defines the decimal constant for 100.
HUNDRED = Decimal("100")


def make_quantizer(precision: int) -> Decimal:
    """
    Creates a quantifier as per the given precision.
    """
    return Decimal(f"0.{''.join(['0' * precision])}")


#: Defines the maximum precision of the monetary values and operations.
MaxPrecision: int = 12

#: Defines the maximum precision quantifier.
MaxPrecisionQuantizer: Decimal = make_quantizer(MaxPrecision)
