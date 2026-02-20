from decimal import Decimal
from typing import Dict
from .exceptions import ValidationError, PrecisionError
import logging

class OrderValidator:
    """Methods for validating order parameters against exchange rules."""
    
    @staticmethod
    def validate_symbol(symbol: str) -> None:
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("Symbol must be a non-empty string.")
        if not symbol.isupper():
            raise ValidationError(f"Symbol {symbol} is not valid. Must be uppercase.")
            
    @staticmethod
    def validate_side(side: str) -> None:
        if side not in ["BUY", "SELL"]:
            raise ValidationError(f"Invalid side: {side}. Must be BUY or SELL.")

    @staticmethod
    def validate_type(order_type: str) -> None:
        if order_type not in ["MARKET", "LIMIT"]:
            raise ValidationError(f"Invalid type: {order_type}. Must be MARKET or LIMIT.")

    @staticmethod
    def validate_quantity(quantity: Decimal, step_size: Decimal, min_qty: Decimal) -> None:
        """
        Validates quantity against exchange filters.
        """
        if quantity <= 0:
            raise ValidationError(f"Quantity must be positive. Got: {quantity}")
            
        if quantity < min_qty:
            raise ValidationError(f"Quantity {quantity} is less than minimum required {min_qty}.")

        # Check step size (modulo check with tolerance for float errors)
        # Using Decimal: (quantity % step_size) should be 0
        if step_size > 0:
            remainder = quantity % step_size
            if remainder > Decimal("1e-10") and (step_size - remainder) > Decimal("1e-10"):
                 raise PrecisionError(f"Quantity {quantity} is not a multiple of step size {step_size}.")

    @staticmethod
    def validate_price(price: Decimal, tick_size: Decimal) -> None:
        """
        Validates price against exchange filters.
        """
        if price <= 0:
            raise ValidationError(f"Price must be positive. Got: {price}")
            
        if tick_size > 0:
            remainder = price % tick_size
            if remainder > Decimal("1e-10") and (tick_size - remainder) > Decimal("1e-10"):
                 raise PrecisionError(f"Price {price} is not a valid tick size multiple of {tick_size}.")

    @staticmethod
    def validate_symbol_status(exchange_info: Dict, symbol: str) -> Dict:
        """
        Checks if symbol exists and is trading. Returns the symbol info dict.
        """
        target = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)
        
        if not target:
             raise ValidationError(f"Symbol {symbol} not found on exchange.")
             
        if target['status'] != "TRADING":
             raise ValidationError(f"Symbol {symbol} is currently {target['status']}, not TRADING.")
             
        return target
