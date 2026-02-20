import pytest
from decimal import Decimal
from bot.validators import OrderValidator
from bot.exceptions import ValidationError, PrecisionError

def test_validate_symbol():
    OrderValidator.validate_symbol("BTCUSDT")
    with pytest.raises(ValidationError):
        OrderValidator.validate_symbol("btc")
    with pytest.raises(ValidationError):
        OrderValidator.validate_symbol("")

def test_validate_side():
    OrderValidator.validate_side("BUY")
    OrderValidator.validate_side("SELL")
    with pytest.raises(ValidationError):
        OrderValidator.validate_side("HOLD")

def test_validate_quantity():
    # Valid quantity (multiple of step size)
    OrderValidator.validate_quantity(Decimal("0.01"), Decimal("0.001"), Decimal("0.001"))
    
    # Below min qty
    with pytest.raises(ValidationError):
        OrderValidator.validate_quantity(Decimal("0.0001"), Decimal("0.001"), Decimal("0.001"))
        
    # Invalid step size
    with pytest.raises(PrecisionError):
        OrderValidator.validate_quantity(Decimal("0.015"), Decimal("0.01"), Decimal("0.001"))

def test_validate_price():
    # Valid price (multiple of tick size)
    OrderValidator.validate_price(Decimal("45000.50"), Decimal("0.50"))
    
    # Invalid tick size
    with pytest.raises(PrecisionError):
        OrderValidator.validate_price(Decimal("45000.25"), Decimal("0.50"))
