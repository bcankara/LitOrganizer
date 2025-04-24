# Core PDF Processing (`PDFProcessor`)

This document details the core logic for processing PDF files, primarily handled by the `PDFProcessor` class located in `modules/core/pdf_renamer.py`.

## Overview

The `PDFProcessor` class orchestrates the entire workflow of analyzing a PDF file, extracting its metadata, renaming it based on citation standards, optionally creating backups, categorizing it, and handling any errors encountered during the process.

## Initialization (`__init__`)

When a `PDFProcessor` instance is created, it takes several configuration options:

*   `directory`: The target directory containing PDFs.
*   `use_ocr`: Whether to use OCR for text extraction.
*   `create_references`: Whether to generate reference files.
*   `create_backups`: Whether to back up original files.
*   `move_problematic`: Whether to move unprocessable files to a separate folder.
*   `problematic_dir`: The specific folder for unprocessable files (defaults to `[directory]/Unnamed Article`).
*   `categorize_options`: A dictionary specifying which categories (journal, author, year, subject) to use for creating subfolders.
*   `max_workers`: Number of threads for parallel processing.
*   `logger`: A logger instance for recording events.

During initialization, it sets up necessary directories (`backups`, `Categorized Article`, `Named Article`) and initializes counters for statistics (`processed_count`, `renamed_count`, `problematic_count`, `category_counts`, `categorized_file_count`).

## Main Processing Loop (`process_files`)

This method drives the processing for all PDF files in the specified directory.

1.  **Find PDFs:** It scans the `directory` for all files ending with `.pdf`.
2.  **Reset Counters:** Resets statistics counters before starting.
3.  **Parallel Execution:** It uses `concurrent.futures.ThreadPoolExecutor` to process multiple PDF files in parallel (up to `max_workers`).
4.  **Submit Jobs:** Each PDF file is submitted to the thread pool, calling the `process_file` method for each.
5.  **Collect Results:** As each job completes, it updates the `processed_count`, `renamed_count`, and `problematic_count` based on the success or failure of `process_file`.
6.  **Error Handling:** Catches exceptions that might occur within worker threads.
7.  **Summary Logging:** Logs a summary of the processing results.
8.  **Reference Writing:** If `create_references` is enabled, it calls `write_references_file()`.

### Flowchart: `process_files`

```mermaid
flowchart TD
    A[Start process_files] --> B[Find all *.pdf files in directory];
    B --> C{Any PDFs Found?};
    C -- No --> D[Log Warning & Exit];
    C -- Yes --> E[Reset Statistics Counters];
    E --> F[Initialize ThreadPoolExecutor];
    F --> G[For each PDF file];
    G --> H{Submit process_file(pdf) to Executor};
    H --> G;
    H -- All Submitted --> I[Wait for jobs to complete];
    I --> J{Process Result of completed job};
    J --> K{Successful?};
    K -- Yes --> L[Increment renamed_count];
    K -- No --> M[Increment problematic_count];
    L --> N[Increment processed_count];
    M --> N;
    N --> I;  // Check next completed job
    I -- All Complete --> O[Log Summary Statistics];
    O --> P{Create References Enabled?};
    P -- Yes --> Q[Call write_references_file];
    P -- No --> R[End];
    Q --> R;
    D --> R;
```

## Single File Processing (`process_file`)

This method contains the detailed logic for processing a single PDF file. It returns `True` if the file is successfully renamed and potentially categorized, and `False` otherwise (marking it as problematic).

1.  **Log Start:** Records the start of processing for the file.
2.  **Extract DOI:** Calls `pdf_extractor.extract_doi()` to find a DOI within the PDF content or metadata. Handles potential `PDFReadError`, `PDFEncryptedError`, and other extraction exceptions.
3.  **DOI Check:** If no DOI is found, logs a warning and returns `False` (moves to problematic if enabled).
4.  **Fetch Metadata:** Calls `pdf_extractor.get_metadata_from_multiple_sources()` with the found DOI. This utility function queries APIs like CrossRef, DataCite, etc. Handles potential network/API errors.
5.  **Metadata Check:** Calls `pdf_extractor.has_sufficient_metadata()` to ensure essential fields (like title, author, year) are present. If not sufficient, logs a warning and returns `False`.
6.  **Format Citation & Filename:** 
    *   Calls `self.format_citation()` (which uses `reference_formatter.create_apa7_citation`) to create a short citation string (e.g., "(Author, Year)").
    *   Calls `self.format_filename()` to combine the citation and title into a sanitized base filename.
7.  **Create Backup:** If `create_backups` is enabled, copies the original file to the `backup_dir`.
8.  **Move to "Named Article":** 
    *   Constructs the target path in the `Named Article` directory using the new filename.
    *   Handles potential filename collisions by appending a counter (`_1`, `_2`, etc.).
    *   Uses `shutil.move()` to move the original file to the `Named Article` directory with its new name. This is the primary rename step.
    *   Handles potential `OSError`, `IOError`, `PermissionError` during the move.
    *   If the move fails, the file is considered problematic, and the method returns `False`.
9.  **Categorization:** If the move to "Named Article" was successful and categorization options are enabled, it calls `self.categorize_file()` with the path of the file *in the Named Article directory* and its metadata.
10. **Add Reference:** If the move to "Named Article" was successful and `create_references` is enabled, calls `reference_formatter.create_apa7_reference()` and appends the result to the `self.references` list.
11. **Return Status:** Returns `True` if the move to "Named Article" succeeded, `False` otherwise.
12. **General Error Handling:** A top-level `try...except` block catches any other unexpected errors during the process.

### Flowchart: `process_file`

```mermaid
flowchart TD
    A[Start process_file(file_path)] --> B{Extract DOI};
    B -- Error --> Z[Log Error & Return False];
    B -- Success --> C{DOI Found?};
    C -- No --> D[Log Warning & Move to Problematic?];
    D --> Z;
    C -- Yes --> E{Fetch Metadata from APIs};
    E -- Error --> Z;
    E -- Success --> F{Metadata Found & Sufficient?};
    F -- No --> G[Log Warning & Move to Problematic?];
    G --> Z;
    F -- Yes --> H[Format Citation (APA7)];
    H --> I[Format Filename (Sanitized)];
    I --> J{Create Backup Enabled?};
    J -- Yes --> K[Copy Original to Backup Dir];
    J -- No --> L[Move Original to "Named Article" Dir w/ New Name];
    K --> L;
    L -- Error --> Z;
    L -- Success --> M{Categorization Enabled?};
    M -- Yes --> N[Call categorize_file(new_path, metadata)];
    M -- No --> O{Create References Enabled?};
    N --> O;
    O -- Yes --> P[Create & Append Reference Entry];
    O -- No --> Q[Return True];
    P --> Q;
```

## Categorization (`categorize_file`)

This method is called after a file has been successfully renamed and moved to the "Named Article" directory.

1.  **Check Options:** Returns immediately if no categorization options are enabled.
2.  **Ensure Directory:** Ensures the base `Categorized Article` directory exists.
3.  **Extract Category Values:** Gets relevant values (journal, author surname, year, first subject) from the metadata based on enabled options and sanitizes them for use as folder names.
4.  **Copy to Subfolders:** For each valid category value found:
    *   Constructs the target subfolder path (e.g., `Categorized Article/by_journal/Nature`).
    *   Ensures the subfolder exists.
    *   Constructs the destination file path within the subfolder.
    *   Uses `shutil.copy2()` to copy the file *from the Named Article directory* to the category subfolder.
    *   Handles potential file system errors during the copy.
5.  **Update Statistics:** Increments the specific category counter (e.g., `self.category_counts['journal']['Nature']`) and the total category type counter (e.g., `self.categorized_file_count['journal']`).
6.  **Category References:** If `create_references` is enabled, calls `_create_reference_files()` to generate reference files specific to that category subfolder.
7.  **Return Status:** Returns `True` if at least one file copy to a category folder was successful.

## Reference Writing (`write_references_file`, `_create_reference_files`)

*   `write_references_file`: Orchestrates the creation of reference files. It calls `_create_reference_files` for the main directory and then iterates through enabled categories, groups references by category value (journal name, author name, etc.), and calls `_create_reference_files` for each specific category subfolder.
*   `_create_reference_files`: Creates `references.xlsx` (using pandas if available) and `references.txt` in a specified directory, containing the provided list of references. Includes DOI, Author, Filename, and Bibliography (APA7) information.

## Error Handling (`_move_to_problematic`)

This helper function is called internally when `move_problematic` is enabled and an error occurs that prevents successful renaming (e.g., missing DOI, insufficient metadata, file system error during move).

1.  **Check Enabled:** Returns if `move_problematic` is `False`.
2.  **Ensure Directory:** Ensures the `problematic_dir` exists.
3.  **Construct Path:** Creates a target path in the problematic directory, often prefixing the original filename with an error tag (e.g., `ERROR_Missing_DOI_...`).
4.  **Copy & Delete:** Copies the original file to the problematic directory using `shutil.copy2()` and then attempts to delete the original file using `file_path.unlink()`. This ensures the original isn't lost if the deletion fails.
5.  **Log:** Logs the action and any errors during the move/delete process.

## Code Snippets

### `PDFProcessor.__init__` (Partial)
```python
class PDFProcessor:
    # ... (imports)
    def __init__(
        self,
        directory: Union[str, Path] = "pdf",
        # ... other args
        categorize_options: Optional[Dict[str, bool]] = None,
        max_workers: int = 4,
        logger: Optional[logging.Logger] = None
    ):
        # ... (setup paths)
        self.categorize_options = categorize_options or {}
        
        # Stats counters
        self.processed_count = 0
        self.renamed_count = 0
        self.problematic_count = 0

        # Categorization statistics dictionaries
        self.category_counts = {
            'journal': {},
            'author': {},
            'year': {},
            'subject': {}
        }
        self.categorized_file_count = {
            'journal': 0,
            'author': 0,
            'year': 0,
            'subject': 0
        }
        # ... (ensure directories)
```

### `PDFProcessor.categorize_file` (Partial - Statistics Update)
```python
def categorize_file(self, source_file_path: Path, metadata: Dict[str, Any], target_filename: str) -> bool:
    # ... (check options, get category values)
    for category_type, folder_name in category_values.items():
        if not folder_name: continue
        try:
            # ... (ensure folders, construct paths)
            destination_path = category_target_folder / target_filename
            shutil.copy2(source_file_path, destination_path)
            self.logger.info(f"Successfully categorized (copied) to 'by_{category_type}': {destination_path}")
            
            # --- Update categorization statistics --- 
            self.category_counts[category_type][folder_name] = self.category_counts[category_type].get(folder_name, 0) + 1
            self.categorized_file_count[category_type] += 1
            # --- End update --- 
            
            at_least_one_category_created = True
            # ... (create references)
        except Exception as e:
            # ... (log error)
    # ... (return status)
```

This class forms the backbone of the application's renaming and organization capabilities. 