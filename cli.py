import argparse
import logging
import sys
import traceback
from decimal import Decimal

from bot.orders import OrderManager
from bot.logging_config import setup_logging
from bot.exceptions import ValidationError, APIRequestError, NetworkError, PrecisionError

def main():
    # 1. Setup Logging (JSON to file)
    logger = setup_logging()

    # 2. Parse Arguments
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot (USDT-M) v2",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("--symbol", required=True, type=str, help="Trading pair (e.g., BTCUSDT)")
    parser.add_argument("--side", required=True, type=str, choices=["BUY", "SELL"], help="Order side: BUY or SELL")
    parser.add_argument("--type", required=True, type=str, choices=["MARKET", "LIMIT"], help="Order type: MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument("--price", type=float, help="Limit price (Required for LIMIT orders)")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    # 3. Validation & Confirmation Loop
    try:
        manager = OrderManager()
        
        # Basic pre-check before fetching metadata
        if args.quantity <= 0:
             print("Error: Quantity must be positive.")
             sys.exit(1)

        # 4. Print Summary
        print("\nOrder Summary")
        print("=" * 30)
        print(f"Symbol:   {args.symbol}")
        print(f"Side:     {args.side}")
        print(f"Type:     {args.type}")
        print(f"Quantity: {args.quantity}")
        if args.type == "LIMIT":
            if args.price is None:
                print("Error: --price is required for LIMIT orders.")
                sys.exit(1)
            print(f"Price:    {args.price}")
        print("-" * 30)

        # 5. Confirmation
        if not args.yes:
            confirm = input("Confirm order? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Order cancelled by user.")
                sys.exit(0)

        print("\nSending order to Binance Futures Testnet...")
        
        # 6. Execution
        response = manager.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price
        )
        
        # 7. Success Output
        print("\nOrder Placed Successfully")
        print("=" * 30)
        print(f"Order ID:      {response.order_id}")
        print(f"Status:        {response.status}")
        print(f"Executed Qty:  {response.executed_qty}")
        print(f"Avg Price:     {response.avg_price}")
        print("=" * 30)
        
        sys.exit(0)

    except ValidationError as e:
        print(f"\n[Validation Error] {e}")
        logger.warning(f"Validation failed: {e}", extra={"failed_args": vars(args)})
        sys.exit(1)

    except PrecisionError as e:
        print(f"\n[Precision Error] {e}")
        logger.warning(f"Precision error: {e}")
        sys.exit(1)

    except APIRequestError as e:
        print(f"\n[API Error] {e}")
        # Logged internally with stack trace
        sys.exit(1)

    except NetworkError as e:
        print(f"\n[Network Error] {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)

    except Exception as e:
        print(f"\n[Unexpected Error] An internal error occurred. See logs for details.")
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
