from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class OrderResponse:
    """Normalized response schema for orders."""
    order_id: int
    client_order_id: str
    symbol: str
    side: str
    order_type: str
    executed_qty: Decimal
    avg_price: Decimal
    orig_qty: Decimal
    status: str
    
    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "client_order_id": self.client_order_id,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "executed_qty": str(self.executed_qty),
            "avg_price": str(self.avg_price),
            "orig_qty": str(self.orig_qty),
            "status": self.status
        }
