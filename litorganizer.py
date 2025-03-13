#!/usr/bin/env python3
"""
LitOrganizer: Organize your academic literature quickly and efficiently

This tool helps rename academic PDF files using citation information from DOI metadata.
It extracts DOI from PDFs, queries Crossref API, and renames files using APA7 citation format.
"""

import argparse
import logging
import sys
from pathlib import Path

from modules.core.pdf_renamer import PDFProcessor
from modules.utils.logging_config import setup_logger
from modules.gui.app import launch_gui

__version__ = '1.0.0'


def process_command_line():
    """
    Process command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='LitOrganizer: Organize academic PDFs by extracting citation information',
        epilog='Note: When run without arguments, the program starts in GUI mode by default.'
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='pdf',
        help='Directory containing PDF files (default: pdf/) - Only used in command-line mode'
    )
    
    parser.add_argument(
        '--create-references',
        action='store_true',
        help='Create references.xlsx file with citations - Only used in command-line mode'
    )
    
    parser.add_argument(
        '--no-backups',
        action='store_true',
        help='Do not create backups of original files - Only used in command-line mode'
    )
    
    parser.add_argument(
        '--use-ocr',
        action='store_true',
        help='Use OCR for text extraction (requires pytesseract and pdf2image) - Only used in command-line mode'
    )
    
    parser.add_argument(
        '-g', '--gui',
        action='store_true',
        help='Launch graphical user interface (this is the default mode)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'LitOrganizer {__version__}'
    )
    
    return parser.parse_args()


def main():
    """
    Main entry point for the application.
    """
    args = process_command_line()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger('litorganizer', log_level)
    
    logger.debug(f"LitOrganizer v{__version__} starting...")
    
    # Default to GUI mode unless explicitly requested to run in command line mode
    if len(sys.argv) <= 1 or args.gui:
        # Launch GUI
        launch_gui(logger)
    else:
        # Command line mode
        try:
            processor = PDFProcessor(
                directory=args.directory,
                use_ocr=args.use_ocr,
                create_references=args.create_references,
                create_backups=not args.no_backups,
                move_problematic=True,  # Always move problematic files
                auto_analyze=False,  # Artık False olarak sabitlendi - Sadece DOI kullanılıyor
                logger=logger
            )
            
            # Process files
            result = processor.process_files()
            if not result:
                logger.error("Processing failed.")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Error processing files: {e}")
            if args.verbose:
                import traceback
                logger.debug(traceback.format_exc())
            sys.exit(1)


if __name__ == '__main__':
    main() 