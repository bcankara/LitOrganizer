"""
File handling and general utility functions.

This module provides helper functions for file operations, path handling, 
directory creation, filename sanitization, and other common utility functions.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime


def setup_logger(debug=False):
    """
    Configure and return a logger for the application.
    
    Args:
        debug (bool): Whether to enable debug logging
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('pdf_citation_tool')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handler
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Create log directory if it doesn't exist
    log_dir = Path('logs')
    if not log_dir.exists():
        log_dir.mkdir(exist_ok=True)
    
    # Create file handler for logging to file
    log_file = log_dir / f"pdf_citation_tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Always log debug to file
    file_handler.setFormatter(formatter)
    
    # Add file handler to logger
    logger.addHandler(file_handler)
    
    return logger


def get_version():
    """
    Get the version of the application.
    
    Returns:
        str: Version string
    """
    try:
        from modules import __version__
        return __version__
    except ImportError:
        return "0.0.0"


def get_app_path():
    """
    Get the path where the application is running from.
    
    Returns:
        Path: Path to the application directory
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


def ensure_dir(directory):
    """
    Ensure that the specified directory exists.
    
    Args:
        directory (str or Path): Directory to ensure exists
        
    Returns:
        Path: Path object for the directory
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def sanitize_filename(filename):
    """
    Remove invalid characters from a filename.
    
    Args:
        filename (str): Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscore
    for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        filename = filename.replace(char, '_')
    
    # Replace multiple spaces with a single space
    filename = ' '.join(filename.split())
    
    # Limit length (Windows has a 260 character path limit)
    if len(filename) > 240:
        name, ext = os.path.splitext(filename)
        filename = name[:236 - len(ext)] + ext
    
    return filename 