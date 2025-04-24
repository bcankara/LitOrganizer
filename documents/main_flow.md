# Main Application Flow (`litorganizer.py`)

This document describes the main entry point of the LitOrganizer application, handled by the `litorganizer.py` script. It covers command-line argument parsing and the logic that determines whether to launch the Graphical User Interface (GUI) or run in Command-Line Interface (CLI) mode.

## Entry Point: `main()` function

The execution starts in the `main()` function. Its primary responsibilities are:

1.  **Argument Parsing:** It calls `process_command_line()` to parse arguments provided by the user when running the script.
2.  **Logging Setup:** It configures the logging system based on the verbosity level specified by the user (e.g., `--verbose`).
3.  **Mode Selection:** Based on the parsed arguments (specifically `--gui`), it decides whether to launch the GUI or proceed with CLI processing.
4.  **Execution:** 
    *   If GUI mode is selected, it calls `launch_gui()` from `modules.gui.app`.
    *   If CLI mode is selected, it instantiates `PDFProcessor` from `modules.core.pdf_renamer` with the relevant options and calls its `process_files()` method.

## Command-Line Arguments (`process_command_line()`)

The `process_command_line()` function uses Python's `argparse` module to define and parse the command-line options available to the user. Key arguments include:

*   `-d`, `--directory`: Specifies the input directory containing PDF files (required for CLI mode).
*   `-g`, `--gui`: Launches the graphical user interface.
*   `-r`, `--references`: Enables the creation of reference files (`references.txt`, `references.xlsx`).
*   `--no-backups`: Disables the creation of backups for original files.
*   `--use-ocr`: Enables Optical Character Recognition (OCR) using Tesseract for text extraction (useful for image-based PDFs).
*   `--move-problematic`: Moves files that cannot be processed to a separate directory.
*   `--problematic-dir`: Specifies a custom directory for problematic files.
*   `--categorize-by-[journal|author|year|subject]`: Enables categorization into subfolders based on the specified metadata field.
*   `-v`, `--verbose`: Increases logging verbosity for debugging.
*   `--version`: Displays the application version and exits.

## High-Level Flowchart

```mermaid
flowchart TD
    A[Start litorganizer.py] --> B{Parse Command-Line Arguments};
    B --> C{GUI Mode Requested? (--gui)};
    C -- Yes --> D[Launch GUI (app.py)];
    C -- No --> E{Directory Specified? (-d)};
    E -- Yes --> F[Configure PDFProcessor based on Args];
    F --> G[Run PDFProcessor in CLI Mode];
    G --> H[Processing Complete];
    D --> H;
    E -- No --> I[Show Error / Help Message];
    I --> Z[End];
    H --> Z;
```

## Code Snippet: `main()` function

```python
# Example snippet from litorganizer.py

def main():
    """Main function to run the PDF Citation Tool."""
    args = process_command_line()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger('litorganizer')

    if args.gui:
        logger.info("Launching GUI mode...")
        try:
            from modules.gui.app import launch_gui
            launch_gui(logger)
        except ImportError:
            logger.error("GUI dependencies (PyQt5) not found. Please install them to use the GUI.")
            sys.exit(1)
        except Exception as e:
            logger.critical(f"Failed to launch GUI: {e}", exc_info=True)
            sys.exit(1)
    elif args.directory:
        logger.info(f"Starting CLI processing for directory: {args.directory}")
        # Setup categorization options from args
        categorize_options = {
            "by_journal": args.categorize_by_journal,
            "by_author": args.categorize_by_author,
            "by_year": args.categorize_by_year,
            "by_subject": args.categorize_by_subject
        }
        
        try:
            processor = PDFProcessor(
                directory=args.directory,
                use_ocr=args.use_ocr,
                create_references=args.references,
                create_backups=not args.no_backups,
                move_problematic=args.move_problematic,
                problematic_dir=args.problematic_dir,
                categorize_options=categorize_options, # Pass categorization flags
                logger=logger
            )
            processor.process_files()
        except FileNotFoundError as e:
            logger.error(f"Error: {e}. Please check if the directory exists.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during CLI processing: {e}", exc_info=True)
    else:
        logger.warning("No directory specified for CLI mode and GUI not requested. Use --gui or -d <directory>.")
        # Optionally print help here
        # parser.print_help() # Defined in process_command_line scope

if __name__ == "__main__":
    main() 