import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Centralized configuration for the trading bot."""
    
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
    
    # Defaults
    BASE_URL = "https://testnet.binancefuture.com"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE = "logs/trading.log"
    TIMEOUT = 10  # Seconds for API requests
    RETRY_COUNT = 3
    RETRY_DELAY = 1  # Base retry delay (exponential backoff)
    
    @classmethod
    def validate(cls):
        """Ensures critical configuration exists."""
        if not cls.BINANCE_API_KEY or not cls.BINANCE_SECRET_KEY:
            raise ValueError("Missing Binance API credentials in .env file.")

# Validate on import (fails fast)
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    sys.exit(1)
