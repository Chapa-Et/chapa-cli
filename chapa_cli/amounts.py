"""Amount conversion: base currency unit to smallest unit.

Users provide amount in base unit (e.g. 10.50 ETB). This module converts
internally to smallest unit (integer) to avoid floating-point precision errors.
Conversion is consistent and documented per currency.
"""

from decimal import Decimal
from typing import Dict, Union

# Decimal places (minor units per 1 base unit) for supported currencies.
CURRENCY_MINOR_UNITS: Dict[str, int] = {
    "ETB": 2,
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
}


def to_smallest_unit(
    amount: Union[Decimal, float, str, int],
    currency: str = "ETB",
) -> int:
    """Convert amount from base currency unit to smallest unit (integer).

    Uses Decimal for exact arithmetic. No floating-point precision errors.
    Rounds half-up to nearest integer.

    Args:
        amount: Amount in base unit (e.g. 10.50 for 10.50 ETB).
        currency: Currency code (e.g. ETB). Default ETB (2 decimal places).

    Returns:
        Amount in smallest unit (e.g. 1050 for 10.50 ETB).

    Example:
        >>> to_smallest_unit(10.50, "ETB")
        1050
        >>> to_smallest_unit("19.99", "ETB")
        1999
    """
    decimals = CURRENCY_MINOR_UNITS.get(currency.upper(), 2)
    factor = 10**decimals
    d = Decimal(str(amount)).quantize(Decimal("0.01"))
    return int((d * factor).to_integral_value(rounding="ROUND_HALF_UP"))


def from_smallest_unit(
    amount_smallest: int,
    currency: str = "ETB",
) -> Decimal:
    """Convert amount from smallest unit to base unit (for display).

    Args:
        amount_smallest: Amount in smallest unit.
        currency: Currency code.

    Returns:
        Amount as Decimal in base unit.
    """
    decimals = CURRENCY_MINOR_UNITS.get(currency.upper(), 2)
    factor = 10**decimals
    return Decimal(amount_smallest) / factor
