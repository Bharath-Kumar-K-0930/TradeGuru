class ValidationError(Exception):
    """Raised when input validation or exchange constraints fail."""
    pass

class APIRequestError(Exception):
    """Raised when the Binance API returns an error (4xx, 5xx)."""
    pass

class NetworkError(Exception):
    """Raised when network connection fails or times out."""
    pass

class PrecisionError(Exception):
    """Raised when rounding or precision logic fails."""
    pass

class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass
