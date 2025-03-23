"""
Logging configuration module.
"""
import logging
import os
import sys
from typing import Optional


def setup_logger(log_level: Optional[str] = None) -> None:
    """
    Set up the logger for the application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout),]
    )

    # Set lower log level for some third-party libraries
    logging.getLogger('web3').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)