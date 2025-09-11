import logging
import os
from datetime import datetime
# from config import LOGS_DIR
# Create logs directory if it doesn't exist

LOGS_DIR = "logs_directory"
os.makedirs(LOGS_DIR, exist_ok=True)
# Generate filename with timestamp
log_filename = os.path.join(
    LOGS_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")


def setup_logger(name):
    """
    Create a logger with the specified name that writes to both file and console
    """
    logger = logging.getLogger(name)
    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        # Create file handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Less verbose for console
        console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger


logger = setup_logger(__name__)
