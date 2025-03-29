import logging
from typing import Optional, Dict, Any
import os


def configure_logging(level=logging.INFO, log_file: Optional[str] = None, format_string: Optional[str] = None):
    """Configure standardized logging for the SDK.

    Args:
        level: The logging level (default: logging.INFO).
        log_file: Optional path to a log file. If provided, logs will be written to this file.
        format_string: Optional custom format string for log messages.

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger("deepexec")
    logger.setLevel(level)
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()
    
    # Default format string
    if not format_string:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        try:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to set up file logging to {log_file}: {str(e)}")
    
    # Suppress third-party library logs
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    return logger


def get_logger(name: Optional[str] = None):
    """Get a logger instance with the specified name.
    
    If no name is provided, returns the main deepexec logger.
    If the logger doesn't exist, it will be created with default settings.
    
    Args:
        name: Optional name for the logger (will be prefixed with 'deepexec.').
        
    Returns:
        A logger instance.
    """
    if name:
        logger_name = f"deepexec.{name}"
    else:
        logger_name = "deepexec"
        
    logger = logging.getLogger(logger_name)
    
    # If this is a new logger and the main logger is configured, inherit its level
    if not logger.handlers and logger_name != "deepexec":
        main_logger = logging.getLogger("deepexec")
        if main_logger.level != logging.NOTSET:
            logger.setLevel(main_logger.level)
    
    return logger


def log_request(logger, method: str, url: str, headers: Optional[Dict[str, Any]] = None, data: Any = None):
    """Log an outgoing request with appropriate masking of sensitive information.
    
    Args:
        logger: The logger instance to use.
        method: The HTTP method (GET, POST, etc.).
        url: The request URL.
        headers: Optional request headers.
        data: Optional request data.
    """
    if logger.level > logging.DEBUG:
        return
    
    # Mask sensitive information in headers
    masked_headers = {}
    if headers:
        for key, value in headers.items():
            if key.lower() in ["authorization", "x-deepseek-key", "x-e2b-key", "api-key"]:
                masked_headers[key] = "****"
            else:
                masked_headers[key] = value
    
    # Log the request
    logger.debug(f"Request: {method} {url}")
    logger.debug(f"Headers: {masked_headers}")
    
    # Only log data at trace level (more verbose than debug)
    if logger.level <= 5:  # TRACE level (custom)
        logger.log(5, f"Data: {data}")


def log_response(logger, status_code: int, headers: Optional[Dict[str, Any]] = None, data: Any = None):
    """Log an incoming response.
    
    Args:
        logger: The logger instance to use.
        status_code: The HTTP status code.
        headers: Optional response headers.
        data: Optional response data.
    """
    if logger.level > logging.DEBUG:
        return
    
    # Log the response
    logger.debug(f"Response: {status_code}")
    
    if headers and logger.level <= logging.DEBUG:
        logger.debug(f"Headers: {headers}")
    
    # Only log data at trace level
    if data is not None and logger.level <= 5:  # TRACE level
        logger.log(5, f"Data: {data}")
