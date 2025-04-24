# Graphical User Interface (GUI) (`app.py`)

This document outlines the structure and functionality of the LitOrganizer Graphical User Interface (GUI), implemented in `modules/gui/app.py` using the PyQt5 framework.

## Overview

The GUI provides an interactive way for users to select directories, configure processing options, start/stop the PDF renaming and keyword search processes, view logs, and analyze results statistics.

## Main Components

1.  **`MainWindow` Class:** This is the main application window class, inheriting from `QMainWindow`. It sets up the entire UI structure, manages interactions, and coordinates background processing.
2.  **`WorkerThread` Class:** Inherits from `QThread`. Handles the core PDF renaming/organization logic (`PDFProcessor`) in a separate background thread to prevent the GUI from freezing during long operations. It communicates with `MainWindow` using PyQt signals (`pyqtSignal`).
3.  **`SearchKeywordWorkerThread` Class:** Also inherits from `QThread`. Handles the keyword search process in a separate background thread. Communicates results and progress back to `MainWindow` via signals.
4.  **UI Elements:** Standard PyQt5 widgets like `QPushButton`, `QLineEdit`, `QCheckBox`, `QTabWidget`, `QListWidget`, `QTextEdit`, `QProgressBar`, `QTableWidget`, etc., are used to build the interface.
5.  **`SignalLogHandler` Class:** A custom `logging.Handler` that emits log records as PyQt signals, allowing logs generated in worker threads to be displayed in the GUI's log window (`QTextEdit`).

## UI Structure (`setup_ui`)

The `MainWindow.setup_ui()` method constructs the visual layout:

*   **Header:** Contains the LitOrganizer logo and BibexPy branding.
*   **Tabs (`QTabWidget`):** Organizes different functionalities:
    *   **Renamer - Organizer Tab:** The main tab for selecting directories, configuring renaming/categorization options, and starting/stopping the process. Includes panels for Results (`QListWidget`) and Processing Log (`QTextEdit`).
    *   **Search Keywords Tab:** For selecting a directory, entering keywords, setting search options (exact match, case sensitive, regex), starting/stopping the search, and viewing results in a `QTableWidget`.
    *   **API Settings Tab:** Allows users to view enabled APIs and configure optional email addresses or API keys (e.g., for Scopus).
    *   **General Statistics Tab:** Displays overall processing statistics like total files, success rate, performance metrics (time, speed), and API usage.
    *   **Publication Statistics Tab:** Shows detailed statistics based on categorization results, including distributions by author, journal, year, and subject.
*   **Styling:** Uses stylesheets for a consistent and modern appearance (colors, fonts, borders, shadows).

## Core Interactions and Workflow (Renamer/Organizer)

1.  **Directory Selection:** User selects the main PDF directory using `browse_directory()` (`QFileDialog`). Optionally selects a directory for problematic files.
2.  **Option Configuration:** User checks/unchecks options for backups, moving problematic files, reference creation, and categorization types.
3.  **Start Processing:** User clicks the "Start Processing" button (`start_processing()` method).
    *   Validates selected directory.
    *   Saves current settings (`save_settings()`).
    *   Records the start time.
    *   Creates a `WorkerThread` instance with the current configuration.
    *   Connects the thread's signals (`progress_update`, `file_processed`, `processing_complete`, `error_occurred`, `progress_percentage`) to corresponding methods (slots) in `MainWindow` (e.g., `log_message`, `update_file_status`, `processing_completed`, `handle_error`, `update_progress_percentage`).
    *   Disables the Start button, enables the Stop button, and updates the Start button text to show progress.
    *   Starts the `WorkerThread` (`worker_thread.start()`).
4.  **Background Processing (`WorkerThread.run`):**
    *   Sets up a `SignalLogHandler` to redirect logging output to the GUI.
    *   Creates a `PDFProcessor` instance, passing the logger.
    *   Patches the `PDFProcessor.process_file` method to emit `file_processed` and `progress_percentage` signals after each file.
    *   Calls `PDFProcessor.process_files()`.
    *   When complete, emits the `processing_complete` signal with final counts, including detailed categorization statistics.
5.  **GUI Updates (Slots):**
    *   `log_message(str)`: Appends messages from the worker thread (via `SignalLogHandler`) to the `log_text` widget.
    *   `update_file_status(str, bool)`: Adds an item to the `results_list` indicating the processing status of a file.
    *   `update_progress_percentage(int)`: Updates the text/style of the Start button to reflect the percentage progress.
    *   `processing_completed(int, int, int, dict, dict)`: Re-enables Start button, disables Stop button, logs completion, calls `update_statistics()`, and switches to the Statistics tab.
    *   `handle_error(str)`: Logs the error, re-enables Start button, and shows a critical message box.
6.  **Statistics Update (`update_statistics`):**
    *   Calculates success rate and performance metrics (total time, time per file, speed).
    *   Updates labels in the General Statistics tab.
    *   Analyzes log text to determine API usage distribution (this relies on specific log message formats).
    *   **Crucially:** Uses the `category_counts` and `categorized_file_counts` dictionaries (received directly from `processing_completed`) to populate the lists (Top Authors, Top Journals, Year Distribution, Subject Distribution) and summary counts in the Publication Statistics tab. This avoids parsing logs for categorization stats.
7.  **Stop Processing:** User clicks the "Stop" button (`stop_processing()` method).
    *   Sets a flag (`terminate_flag`) in the `WorkerThread`.
    *   Calls `worker_thread.terminate()` (which sets the flag) and `worker_thread.wait()`.
    *   The `WorkerThread.run` loop checks this flag and exits early if set.
    *   Updates button states.

### Flowchart: GUI Renamer/Organizer Workflow

```mermaid
flowchart TD
    A[User Selects Directory & Options] --> B[User Clicks Start];
    B --> C[MainWindow.start_processing];
    C --> D[Validate Input & Save Settings];
    D --> E[Create & Configure WorkerThread];
    E --> F[Connect WorkerThread Signals to MainWindow Slots];
    F --> G[Disable Start, Enable Stop, Update Button Text];
    G --> H[Start WorkerThread];
    
    subgraph WorkerThread
        I[run()] --> J[Setup SignalLogHandler];
        J --> K[Create PDFProcessor];
        K --> L[Patch process_file to emit signals];
        L --> M[Call PDFProcessor.process_files];
        M -- File Done --> N{Emit file_processed & progress_percentage signals};
        N --> M; // Loop through files
        M -- All Done --> O[Emit processing_complete signal with stats];
    end

    subgraph MainWindow Slots
        P[log_message] <== SignalLogHandler & WorkerThread.progress_update;
        Q[update_file_status] <== WorkerThread.file_processed;
        R[update_progress_percentage] <== WorkerThread.progress_percentage;
        S[processing_completed] <== WorkerThread.processing_complete;
        T[handle_error] <== WorkerThread.error_occurred;
    end

    H --> I;
    O --> S;
    S --> U[Update Statistics Tab];
    U --> V[Re-enable Start, Disable Stop];
    V --> W[End Processing Cycle];
    
    X[User Clicks Stop] --> Y[MainWindow.stop_processing];
    Y --> Z[Set terminate_flag in WorkerThread];
    Z --> ZA[Wait for WorkerThread to finish];
    ZA --> V; 
```

## Keyword Search Workflow

The keyword search follows a similar pattern using `SearchKeywordWorkerThread`:

1.  User selects directory, enters keyword, and configures search options on the "Search Keywords" tab.
2.  User clicks "Start Search" (`start_search_processing()`).
3.  A `SearchKeywordWorkerThread` is created and started.
4.  The thread iterates through PDFs, extracts text (using PyMuPDF/`fitz`), searches for the keyword/pattern based on options, and emits `result_found` signals for each match.
5.  `MainWindow.add_search_result` slot receives match details (DOI, filename, page, context sentences) and adds a row to the `search_results_table`.
6.  Progress and completion are handled similarly via signals and slots (`search_update_progress_percentage`, `search_processing_completed`).
7.  Results can be saved to Excel/Word (`save_search_results()`).

## Settings Management

*   **`load_settings` / `save_settings`:** Use `QSettings` to persist user choices (directories, checkbox states) between sessions.
*   **`load_api_settings` / `save_api_settings`:** Read from and write to `config/api_keys.json` to manage API configurations.

## Code Snippets

### `WorkerThread` Signal Definition
```python
class WorkerThread(QThread):
    # ...
    # Updated signal to include categorization statistics
    processing_complete = pyqtSignal(int, int, int, dict, dict)
    # ... other signals
```

### `MainWindow.processing_completed` Slot
```python
def processing_completed(self, processed, renamed, problematic, category_counts, categorized_file_counts):
    """
    Handle processing completion.
    Args:
        # ... (arg descriptions)
        category_counts (dict): Detailed counts for each category value.
        categorized_file_counts (dict): Total files categorized per type.
    """
    # ... (record end time, update buttons)
    
    # Update statistics tab - Pass categorization data directly
    self.update_statistics(processed, renamed, problematic, category_counts, categorized_file_counts)
    
    # Switch to statistics tab
    self.tabs.setCurrentIndex(3) 
    # ... (log completion)
```

### `MainWindow.update_statistics` (Partial - Using Direct Counts)
```python
def update_statistics(self, processed, renamed, problematic, category_counts, categorized_file_counts):
    # ... (update general & performance stats)

    # --- Update publication statistics --- 
    # Directly use the data passed from the worker thread instead of log parsing

    # Year distribution
    self.year_distribution_list.clear()
    year_stats = category_counts.get('year', {})
    total_categorized_by_year = categorized_file_counts.get('year', 0)
    if year_stats:
        for year, count in sorted(year_stats.items(), key=lambda x: x[0], reverse=True):
            percentage = round((count / total_categorized_by_year) * 100 if total_categorized_by_year > 0 else 0, 1)
            item = QListWidgetItem(f"{year}: {count} files ({percentage}%)")
            self.year_distribution_list.addItem(item)
    # ... (handle empty/disabled cases)

    # Author statistics (similar logic using category_counts['author'])
    self.top_authors_list.clear()
    # ...

    # Journal statistics (similar logic using category_counts['journal'])
    self.top_journals_list.clear()
    # ...

    # Subject statistics (similar logic using category_counts['subject'])
    self.subject_list.clear()
    # ...
```

The GUI provides a user-friendly layer on top of the core processing logic, leveraging threading for responsiveness and signals/slots for communication between the UI and background tasks. 