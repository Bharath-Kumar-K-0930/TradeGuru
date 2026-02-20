import pytest
from decimal import Decimal
from bot.precision import round_step_size, round_tick_size

def test_round_step_size():
    # Round down 0.015 with step 0.01 -> 0.01
    assert round_step_size(Decimal("0.015"), Decimal("0.01")) == Decimal("0.01")
    # Exact match
    assert round_step_size(Decimal("0.01"), Decimal("0.01")) == Decimal("0.01")
    # Round down 0.019 -> 0.01
    assert round_step_size(Decimal("0.019"), Decimal("0.01")) == Decimal("0.01")

def test_round_tick_size():
    # Round nearest 45000.128 with tick 0.01 -> 45000.13
    assert round_tick_size(Decimal("45000.128"), Decimal("0.01")) == Decimal("45000.13")
    # Round nearest 45000.122 with tick 0.01 -> 45000.12
    assert round_tick_size(Decimal("45000.122"), Decimal("0.01")) == Decimal("45000.12")
