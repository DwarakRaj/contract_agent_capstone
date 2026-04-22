import logging
import json
import contextvars
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables early for logging config
load_dotenv()

# ContextVar to store the correlation ID for the current async flow
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("correlation_id", default="")

def set_correlation_id(correlation_id: str):
    """Set the correlation ID for the current context."""
    correlation_id_var.set(correlation_id)

class JsonFormatter(logging.Formatter):
    """
    A unified standard JSON formatter that automatically injects the active correlation_id
    from contextvars, adhering to structured logging best practices.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_record["correlation_id"] = correlation_id
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging(level: Optional[int] = None):
    """
    Configure the root Python logger to use our JSON Formatter.
    This centralized configuration should be called on app startup.
    Level can be overridden by LOG_LEVEL environment variable.
    """
    if level is None:
        # Get level from environment or default to INFO
        env_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        level = level_map.get(env_level, logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    
    # Configure the root logger exactly once to avoid duplicate logs
    logging.root.setLevel(level)
    # Remove existing handlers to ensure we only have our JSON formatter
    logging.root.handlers = [handler]
    
    # Also silence uvicorn loggers to match the desired level
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uv_logger = logging.getLogger(logger_name)
        uv_logger.setLevel(level)
        uv_logger.propagate = True # Ensure they propagate to root handler

def get_logger(name: str) -> logging.Logger:
    """
    Get a pre-configured logger instance.
    This serves as the single entry point for creating loggers codebase-wide
    (DRY principle).
    """
    return logging.getLogger(name)

# Ensure logging is setup globally as soon as this utility is imported
setup_logging()
