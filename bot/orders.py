from decimal import Decimal
from typing import Dict, Optional, Tuple
from .client import BinanceFuturesClient
from .validators import OrderValidator
from .precision import round_step_size, round_tick_size
from .validators import ValidationError, PrecisionError
from .exceptions import APIRequestError, NetworkError
from .schemas import OrderResponse
import logging

logger = logging.getLogger("trading_bot")

class OrderManager:
    """Orchestrates order placement, validation, and execution."""
    
    def __init__(self, client: Optional[BinanceFuturesClient] = None):
        self.client = client or BinanceFuturesClient()
        self.exchange_info = None

    def _get_symbol_info(self, symbol: str) -> Dict:
        """Fetch and cache symbol metadata."""
        if not self.exchange_info:
            self.exchange_info = self.client.get_exchange_info()
            
        target_symbol = next((s for s in self.exchange_info['symbols'] if s['symbol'] == symbol), None)
        
        if not target_symbol:
            raise ValidationError(f"Symbol {symbol} not found on Binance Futures.")
            
        if target_symbol['status'] != 'TRADING':
            raise ValidationError(f"Symbol {symbol} is currently {target_symbol['status']}.")
            
        return target_symbol

    def _get_filter(self, symbol_info: Dict, filter_type: str) -> Dict:
        """Helper to extract specific filter from symbol info."""
        return next((f for f in symbol_info['filters'] if f['filterType'] == filter_type), {})

    def _normalize_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> Tuple[Dict, str]:
        """
        Normalizes inputs, validates against exchange rules, and prepares API parameters.
        Returns: (api_params, symbol_base_asset)
        """
        # Validate critical inputs (Basic)
        OrderValidator.validate_symbol(symbol)
        OrderValidator.validate_side(side)
        OrderValidator.validate_type(order_type)

        # Fetch exchange metadata
        symbol_info = self._get_symbol_info(symbol)
        base_asset = symbol_info['baseAsset']
        quote_asset = symbol_info['quoteAsset']

        # Extract filters
        lot_size = self._get_filter(symbol_info, 'LOT_SIZE')
        price_filter = self._get_filter(symbol_info, 'PRICE_FILTER')
        min_notional = self._get_filter(symbol_info, 'MIN_NOTIONAL') # Usually relevant but tricky to pre-calc without index price

        step_size = Decimal(lot_size.get('stepSize', '0'))
        min_qty = Decimal(lot_size.get('minQty', '0'))
        tick_size = Decimal(price_filter.get('tickSize', '0'))

        # Prepare Quantity
        qty_dec = Decimal(str(quantity))
        
        # Round quantity
        try:
            qty_rounded = round_step_size(qty_dec, step_size)
            logger.debug(f"Input Qty: {qty_dec}, Step: {step_size} -> Rounded: {qty_rounded}")
        except PrecisionError as e:
            raise ValidationError(f"Quantity rounding failed: {e}")

        # Validate Quantity
        if qty_rounded < min_qty:
             raise ValidationError(f"Quantity {qty_rounded} is below minimum {min_qty}.")
             
        # Prepare Price
        price_rounded = None
        if order_type == 'LIMIT':
            if price is None:
                raise ValidationError("Price is required for LIMIT orders.")
            
            price_dec = Decimal(str(price))
            
            try:
                price_rounded = round_tick_size(price_dec, tick_size)
                logger.debug(f"Input Price: {price_dec}, Tick: {tick_size} -> Rounded: {price_rounded}")
            except PrecisionError as e:
                raise ValidationError(f"Price rounding failed: {e}")
                
            if price_rounded <= 0:
                raise ValidationError(f"Price must be positive.")

        # Construct payload
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": "{:f}".format(qty_rounded.normalize()), # Format as string safely
        }

        if order_type == 'LIMIT':
            params["price"] = "{:f}".format(price_rounded.normalize())
            params["timeInForce"] = "GTC"
            
        return params, base_asset

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> OrderResponse:
        """
        Public method to execute trade with full validation cycle.
        """
        logger.info(f"Initiating order flow: {symbol} {side} {quantity} {order_type} @ {price}")
        
        # 1. Validation & Normalization
        api_params, _ = self._normalize_order(symbol, side, order_type, quantity, price)
        
        # 2. Execution (Client Layer)
        raw_response = self.client.create_order(api_params)
        
        # 3. Response Normalization
        return OrderResponse(
            order_id=raw_response.get('orderId'),
            client_order_id=raw_response.get('clientOrderId'),
            symbol=raw_response.get('symbol'),
            side=raw_response.get('side'),
            order_type=raw_response.get('type'),
            executed_qty=Decimal(raw_response.get('executedQty', '0')),
            avg_price=Decimal(raw_response.get('avgPrice', '0')),
            orig_qty=Decimal(raw_response.get('origQty', '0')),
            status=raw_response.get('status')
        )
