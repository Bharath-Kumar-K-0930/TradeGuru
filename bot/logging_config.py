import logging
import json
import os
import sys
from logging.handlers import RotatingFileHandler
from .config import Config

class JsonFormatter(logging.Formatter):
    """Formats log records as JSON strings."""
    
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "event": getattr(record, "event", "log_message"),
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage()
        }
        
        # Merge extra fields if present
        if hasattr(record, "extra_data"):
             log_record.update(record.extra_data)
             
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging():
    """Configures structured JSON logging."""
    
    log_dir = os.path.dirname(Config.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    logger = logging.getLogger("trading_bot")
    logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))
    
    # File Handler (JSON)
    file_handler = RotatingFileHandler(
        Config.LOG_FILE, 
        maxBytes=10*1024*1024, 
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(JsonFormatter())
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    logger.addHandler(file_handler)
    logger.propagate = False
    
    return logger
