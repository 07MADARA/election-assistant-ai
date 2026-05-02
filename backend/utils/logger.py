import json
import logging
from typing import Any, Dict

class GCPJSONFormatter(logging.Formatter):
    """
    Custom logging formatter for Google Cloud Platform structured JSON logging.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def get_logger(name: str = "civicguide") -> logging.Logger:
    """
    Get a configured logger instance with the GCP JSON Formatter.
    
    Args:
        name (str): The name of the logger.
        
    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if the logger is already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(GCPJSONFormatter())
        logger.addHandler(handler)
        
    return logger
