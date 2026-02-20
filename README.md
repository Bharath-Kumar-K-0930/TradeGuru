# Binance Futures Testnet Trading Bot (USDT-M) v2

**PRODUCTION GRADE - V2 ULTIMATE MASTER EDITION**

A professional-grade, specialized CLI trading bot for Binance Futures Testnet (USDT-M). This bot is engineered with strict clean architecture, robust error handling, precision math, and enterprise-grade logging.

## 🚀 Key Features v2

- **Exchange Metadata Validation**: Automatically fetches `minQty`, `stepSize`, and `tickSize` to ensure orders are valid before hitting the API.
- **Precision Handling**: Uses `Decimal` for all financial calculations. Auto-rounds inputs to the exchange's required precision.
- **Resilient Networking**: Implements exponential backoff retries for 5xx errors and network timeouts.
- **Time Synchronization**: Automatically syncs local time with Binance server time to prevent `-1021` errors.
- **Structured JSON Logging**: All logs are emitted in JSON format for easy ingestion by log aggregators (e.g., Splunk, ELK).
- **Secure Configuration**: Strict environment variable validation and secret handling.
- **Interactive CLI**: Confirmation prompts and normalized output tables.

## 🛠️ Architecture

The system follows a strict layered architecture:

1.  **CLI Layer** (`cli.py`): Handles user input, prints formatted output, catches top-level exceptions.
2.  **Service Layer** (`bot/orders.py`): Orchestrates validation, normalization, and execution logic.
3.  **Validation Layer** (`bot/validators.py`, `bot/precision.py`): Enforces exchange rules and math correctness.
4.  **Client Layer** (`bot/client.py`): Wraps `python-binance`, handles retries, auth, and raw API communication.
5.  **Configuration** (`bot/config.py`): Centralized config loading and validation.

## ⚙️ How the System Works

When you run a command (e.g., placing a limit order), the system executes the following pipeline:

1.  **Initialization**:
    *   Loads environment variables (`.env`).
    *   Initializes the Binance Client and synchronizes local time with the server to prevent timestamp errors.
    *   Sets up structured JSON logging.

2.  **Input Validation**:
    *   CLI arguments are parsed and basic checks are run (e.g., is quantity positive?).
    *   **Exchange Sync**: The bot fetches real-time metadata for the requested symbol (e.g., `BTCUSDT`) to get the exact `tickSize` (price precision) and `stepSize` (quantity precision).

3.  **Normalization & Math**:
    *   **Smart Rounding**: Inputs are automatically rounded to the exchange's strict requirements using `Decimal` arithmetic.
        *   *Example*: If you input `0.0025 BTC` but the step size is `0.001`, the bot rounds it to `0.002` (DOWN) to avoid rejection.
        *   *Example*: Use input price `25000.123` -> rounded to `25000.10` (if tick is `0.10`).

4.  **Execution**:
    *   The standardized payload is sent to Binance.
    *   **Retry Logic**: If the network fails or the API returns a 5xx error, the bot waits (exponential backoff) and retries automatically.

5.  **Feedback**:
    *   Success: Prints a summary table and the Order ID.
    *   Failure: Prints a user-friendly error message while logging the full stack trace to `logs/trading.log`.

## 📦 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Binance Futures Testnet Account

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:

```ini
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET_KEY=your_testnet_secret
LOG_LEVEL=INFO
```

## 💻 Operational Workflow

1.  **Configure**: Ensure your `.env` file has the correct Testnet API keys.
2.  **Run Command**: Execute the `cli.py` script with your desired parameters (see examples below).
3.  **Confirm**: Review the "Order Summary" displayed in the terminal. Type `y` to proceed (or use `--yes` to skip).
4.  **Verify**:
    *   **Terminal**: See the "Order Placed Successfully" message with the Order ID.
    *   **Logs**: Check `logs/trading.log` for the detailed JSON record of the event.

### Usage Examples

### Place Market Order
Buy 0.01 BTC at market price:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place Limit Order
Sell 0.5 ETH at $2500:

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 2500
```

### Running Tests
Run the unit test suite:
```bash
pytest
```

## 🔍 Logging
Logs are written to `logs/trading.log` in JSON format:

```json
{"timestamp": "2023-10-27 10:00:00,000", "level": "INFO", "event": "order_success", "module": "client", "orderId": 123456}
```

## 🛡️ Security
- **No Secrets in Logs**: API keys are never logged.
- **No Stack Traces**: Users see clean error messages; developers see stack traces in `logs/trading.log`.
- **Testnet Forced**: The client is hardcoded to use `testnet=True`.

## ⚠️ Limitations
- **Testnet Only**: Do not use with mainnet keys without code modification.
- **USDT-M Only**: Designed specifically for USDT-Margined Futures.
