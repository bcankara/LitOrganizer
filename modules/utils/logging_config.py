"""
Logging configuration utilities for LitOrganizer.

This module provides functions to set up and configure logging for the application,
including console and file logging with proper formatting.
"""

import logging
import sys
from pathlib import Path


def setup_logger(name='litorganizer', level=logging.INFO, log_file=None):
    """
    Set up and configure a logger.
    
    Args:
        name (str): Logger name
        level (int): Logging level
        log_file (str, optional): Log file path
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                 datefmt='%Y-%m-%d %H:%M:%S')
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 