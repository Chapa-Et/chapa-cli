"""Tests for amount conversion (base unit to smallest unit, no float errors)."""

from decimal import Decimal

import pytest

from chapa_cli.amounts import from_smallest_unit, to_smallest_unit


def test_to_smallest_unit_etb():
    assert to_smallest_unit(10.50, "ETB") == 1050
    assert to_smallest_unit(10, "ETB") == 1000
    assert to_smallest_unit(0.01, "ETB") == 1


def test_to_smallest_unit_string():
    assert to_smallest_unit("19.99", "ETB") == 1999


def test_to_smallest_unit_decimal():
    assert to_smallest_unit(Decimal("10.50"), "ETB") == 1050


def test_to_smallest_unit_no_float_precision_error():
    # 0.1 + 0.2 in float is not exactly 0.3; Decimal avoids that
    assert to_smallest_unit(0.1 + 0.2, "ETB") == 30
    assert to_smallest_unit(Decimal("0.1") + Decimal("0.2"), "ETB") == 30


def test_from_smallest_unit():
    assert from_smallest_unit(1050, "ETB") == Decimal("10.50")
    assert from_smallest_unit(1999, "ETB") == Decimal("19.99")


def test_unknown_currency_defaults_to_2_decimals():
    assert to_smallest_unit(1.23, "XXX") == 123
    assert from_smallest_unit(123, "XXX") == Decimal("1.23")
