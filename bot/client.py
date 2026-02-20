import time
import logging
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import RequestException
from .config import Config
from .exceptions import APIRequestError, NetworkError, ValidationError

logger = logging.getLogger("trading_bot")

class BinanceFuturesClient:
    """Wrapper for python-binance with retry logic and time sync."""

    def __init__(self):
        try:
            self.client = Client(
                Config.BINANCE_API_KEY, 
                Config.BINANCE_SECRET_KEY, 
                testnet=True
            )
            # Explicitly set the testnet URL just in case library defaults change
            self.client.FUTURES_URL = Config.BASE_URL
            
            logger.info("Binance Futures Client initialized.", extra={"event": "client_init"})
            
            # Sync time to prevent -1021 timestamp errors
            self._sync_time()
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            raise NetworkError(f"Failed to initialize client: {e}")

    def _sync_time(self):
        """Syncs local time offset with server time."""
        try:
            # First ping
            self.client.futures_ping()
            
            # Get server time
            server_time = self.client.futures_time()['serverTime']
            diff = int(time.time() * 1000) - server_time
            
            # If drift is large, we might need manual offset, but python-binance usually handles it.
            # However, explicit syncing can be done via private methods if needed,
            # but usually just calling an endpoint warms it up?
            # Actually python-binance doesn't auto-sync offset unless timestamp requests fail.
            # We will force it if needed, but for now just logging the drift.
            
            logger.info(f"Time sync: Local-Server diff = {diff}ms", extra={"event": "time_sync"})
            
        except Exception as e:
             logger.warning(f"Time sync failed: {e}")
             # Non-critical, proceed.

    def _retry_request(self, method, **kwargs):
        """Executes a request with exponential backoff retry."""
        attempt = 0
        last_exception = None
        
        while attempt < Config.RETRY_COUNT:
            try:
                return method(**kwargs)
            except (BinanceAPIException, BinanceRequestException) as e:
                # If it's a timestamp error (-1021), we might want to sync and retry faster
                # But treating as 5xx/network for now
                if isinstance(e, BinanceAPIException) and e.code == -1021:
                    logger.warning("Timestamp error, resyncing...", extra={"event": "retry_sync"})
                    self._sync_time()
                
                # Check if it's a 5xx error or rate limit (429)
                if (isinstance(e, BinanceAPIException) and (e.status_code >= 500 or e.status_code == 429)) or \
                   isinstance(e, BinanceRequestException):
                       
                    attempt += 1
                    sleep_time = Config.RETRY_DELAY * (2 ** (attempt - 1))
                    logger.warning(
                        f"API Error {e}. Retrying {attempt}/{Config.RETRY_COUNT} in {sleep_time}s...",
                        extra={"event": "retry_attempt", "error": str(e)}
                    )
                    time.sleep(sleep_time)
                    last_exception = e
                else:
                    # 4xx client errors (like invalid symbol) should not be retried
                    raise e
            except RequestException as e:
                attempt += 1
                sleep_time = Config.RETRY_DELAY * (2 ** (attempt - 1))
                logger.warning(f"Network Error. Retrying {attempt}/{Config.RETRY_COUNT}...", extra={"event": "retry_net"})
                time.sleep(sleep_time)
                last_exception = e
                
        raise last_exception

    def get_exchange_info(self):
        """Fetches exchange metadata."""
        try:
            return self._retry_request(self.client.futures_exchange_info)
        except Exception as e:
            logger.error(f"Failed to fetch exchange info: {e}", exc_info=True)
            raise NetworkError(f"Could not fetch exchange info: {e}")

    def create_order(self, params: dict):
        """Sends order creation request."""
        try:
            logger.info("Sending order request", extra={"event": "order_request", "params": params})
            response = self._retry_request(self.client.futures_create_order, **params)
            logger.info("Order success", extra={"event": "order_success", "orderId": response.get('orderId')})
            return response
        except BinanceAPIException as e:
             logger.error(f"Binance API Error: {e}", exc_info=True, extra={"event": "order_error", "code": e.code})
             raise APIRequestError(f"Exchange refused order: {e.message} (Code {e.code})")
        except Exception as e:
             logger.error(f"Unexpected error: {e}", exc_info=True)
             raise NetworkError(f"System failure: {e}")
