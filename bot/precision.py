from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from .exceptions import PrecisionError

def round_step_size(quantity: Decimal, step_size: Decimal) -> Decimal:
    """
    Rounds quantity to the nearest step_size using ROUND_DOWN.
    Example: quantity=0.015, step_size=0.01 -> 0.01
    """
    try:
        # Avoid division by zero
        if step_size == 0:
            return quantity
            
        # Standardize using quantize
        # Round logic: Floor division approach (quantity // step_size) * step_size
        # But handling Decimals safely
        precision = step_size.normalize().as_tuple().exponent
        return quantity.quantize(Decimal(f"1e{precision}"), rounding=ROUND_DOWN)
    except Exception as e:
        raise PrecisionError(f"Failed to round quantity {quantity} with step_size {step_size}: {e}")

def round_tick_size(price: Decimal, tick_size: Decimal) -> Decimal:
    """
    Rounds price to the nearest tick_size using proper rounding.
    Example: price=45000.128, tick_size=0.01 -> 45000.13
    """
    try:
        if tick_size == 0:
            return price
            
        # Generally price rounding uses normal rounding, while quantity uses FLOOR
        precision = tick_size.normalize().as_tuple().exponent
        return price.quantize(Decimal(f"1e{precision}"), rounding=ROUND_HALF_UP)
    except Exception as e:
        raise PrecisionError(f"Failed to round price {price} with tick_size {tick_size}: {e}")
