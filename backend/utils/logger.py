import logging
import os
from logging.handlers import RotatingFileHandler
from flask import has_request_context, g
from pythonjsonlogger import jsonlogger

class RequestIDFilter(logging.Filter):
    """Injects the request_id into the log record if available."""
    def filter(self, record):
        if has_request_context() and hasattr(g, 'request_id'):
            record.request_id = g.request_id
        else:
            record.request_id = "-"
        return True

def get_logger(module_name: str) -> logging.Logger:
    """
    Creates and returns a configured logger instance.
    Logs are written to both console and a rotating file in JSON format.
    """
    logger = logging.getLogger(module_name)
    
    # If logger already has handlers, return it to avoid duplicate logs
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Ensure logs directory exists (relative to the project root, this file is in app/utils/)
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "mdrp.log")

    # Format: timestamp | log level | [module] | [req-id] | message
    format_str = "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
    formatter = jsonlogger.JsonFormatter(format_str)

    req_id_filter = RequestIDFilter()
    
    # Rotating file handler (5 MB max, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(req_id_filter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(req_id_filter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
