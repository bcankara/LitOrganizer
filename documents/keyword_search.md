# Keyword Search Functionality

This document describes the keyword search feature implemented in LitOrganizer, primarily handled by the `SearchKeywordWorkerThread` class within `modules/gui/app.py`.

## Overview

The keyword search allows users to search for specific text strings or regular expression patterns within the content of PDF files located in a chosen directory. The results display the context (surrounding sentences) of each match.

## Core Components

*   **`SearchKeywordWorkerThread`:** A `QThread` subclass responsible for performing the search in the background.
*   **PyMuPDF (`fitz`):** Used for efficient text extraction from PDF documents.
*   **Regular Expressions (`re`):** Used for pattern matching, especially when the "Use Regex" option is enabled.
*   **GUI Elements:** The "Search Keywords" tab in `MainWindow` provides the user interface for input (directory, keyword), options (exact match, case sensitive, regex), starting/stopping the search, and displaying results (`QTableWidget`).

## Workflow (`SearchKeywordWorkerThread.run`)

1.  **Initialization:** The thread is initialized with the target directory, keyword, search options (exact, case-sensitive, regex), and a logger.
2.  **Find PDFs:** Scans the target directory (including subdirectories) for `.pdf` files.
3.  **Parallel Processing:** Uses a `ThreadPoolExecutor` to process multiple PDFs concurrently.
4.  **Process Single PDF (`process_pdf` helper function):**
    *   **Extract DOI:** Attempts to extract the DOI from the PDF using `pdf_metadata_extractor.extract_doi`.
    *   **Extract Text:** Opens the PDF using `fitz.open()` and extracts text content page by page (`page.get_text("text")`). Handles potential errors during file opening.
    *   **Clean Text:** Removes null bytes and control characters from the extracted text.
    *   **Find Matches (`find_keyword_paragraphs` helper function):**
        *   Constructs the search pattern based on the `keyword` and the `exact_match`/`use_regex` options.
        *   Sets regex flags based on the `case_sensitive` option.
        *   Iterates through pages and sentences within each page.
        *   Uses `re.search()` to find occurrences of the pattern within each sentence.
        *   For each match found, it captures the preceding sentence, the matched sentence, and the following sentence.
        *   Emits the `result_found` signal, passing the DOI, filename, page number, keyword, and the context sentences.
    *   Emits `file_processed` signal indicating success or failure for the file.
    *   Includes periodic garbage collection (`gc.collect()`) to manage memory.
5.  **Progress & Completion:**
    *   Updates the overall progress by emitting the `progress_percentage` signal after each file is processed.
    *   Once all files are processed (or the process is terminated), emits the `processing_complete` signal with the total number of files processed and matches found.
6.  **Error Handling:** Catches exceptions during file processing or thread execution and emits `error_occurred` signals.
7.  **Termination:** Checks a `terminate_flag` regularly to allow the user to stop the search process prematurely.

### Flowchart: Keyword Search (`SearchKeywordWorkerThread.run`)

```mermaid
flowchart TD
    A[Start SearchKeywordWorkerThread.run] --> B[Find all *.pdf files in directory];
    B --> C{Any PDFs Found?};
    C -- No --> D[Log Error & Emit Complete(0,0)];
    C -- Yes --> E[Initialize ThreadPoolExecutor];
    E --> F[For each PDF file];
    F --> G{Submit process_pdf(pdf) to Executor};
    G --> F;
    G -- All Submitted --> H[Wait for jobs to complete];
    
    subgraph process_pdf(file_path)
        I[Extract DOI (Optional)] --> J[Open PDF with Fitz];
        J -- Error --> K[Emit file_processed(False)];
        J -- Success --> L[Extract Text per Page];
        L --> M[Clean Text];
        M --> N[Find Matches in Sentences (using re.search)];
        N -- Match Found --> O{Emit result_found signal (DOI, file, page, context)};
        O --> N; // Check next sentence/page
        N -- No More Matches --> P[Emit file_processed(True)];
    end

    H --> Q{Process Result/Update Progress};
    Q -- PDF Processed --> R[Increment processed_files count];
    R --> S[Emit progress_percentage signal];
    S --> H; // Check next completed job
    H -- All Complete --> T[Emit processing_complete(processed_count, found_matches)];
    T --> U[End];
    D --> U;
```

## GUI Interaction

*   The `MainWindow` collects search parameters from the UI elements on the "Search Keywords" tab.
*   It instantiates and starts the `SearchKeywordWorkerThread` when the "Start Search" button is clicked.
*   The `MainWindow.add_search_result` slot receives data from the `result_found` signal and populates the `search_results_table`.
*   Progress is displayed by updating the text/style of the "Start Search" button via the `search_update_progress_percentage` slot.
*   Completion and errors update the UI state (buttons, logging) via the `search_processing_completed` and `handle_error` slots.
*   The `save_search_results` method allows exporting the table data to `.xlsx` and `.docx` files.

## Code Snippets

### `SearchKeywordWorkerThread.run` (Partial - Finding Matches)
```python
def find_keyword_paragraphs(text_list, keyword, filename, doi=None):
    # ...
    # Prepare pattern based on search options
    if self.use_regex:
        keyword_pattern = keyword
    else:
        keyword_pattern = r'\b' + re.escape(keyword) + r'\b' if self.exact_match else re.escape(keyword)
    
    flags = 0 if self.case_sensitive else re.IGNORECASE
    
    for page_num, text in enumerate(text_list, start=1):
        # ... (check terminate_flag, clean text, split sentences)
        sentences = split_sentences(text)

        for i, sentence in enumerate(sentences):
            # ... (check terminate_flag)
            try:
                if re.search(keyword_pattern, sentence, flags):
                    prev_sentences = " ".join(sentences[max(i-1, 0):i]) if i > 0 else ""
                    next_sentences = " ".join(sentences[i+1:min(i+2, len(sentences))]) if i+1 < len(sentences) else ""
                    
                    # Signal the result found
                    self.result_found.emit(
                        doi or "",        # DOI
                        filename,         # PDF name
                        page_num,         # Page number
                        keyword,          # Keyword
                        prev_sentences,   # Previous sentence
                        sentence,         # Matched sentence
                        next_sentences    # Next sentence
                    )
                    self.found_matches += 1
            except Exception as e:
                # ... (log error)
                continue
    # ...
```

### `MainWindow.add_search_result` Slot
```python
def add_search_result(self, doi, filename, page_number, keyword, prev_sentence, matched_sentence, next_sentence, citation=None):
    """
    Add a search result to the results table.
    """
    # ... (normalize DOI if needed)
    row_position = self.search_results_table.rowCount()
    self.search_results_table.insertRow(row_position)
    
    self.search_results_table.setItem(row_position, 0, QTableWidgetItem(doi or ""))
    self.search_results_table.setItem(row_position, 1, QTableWidgetItem(filename))
    self.search_results_table.setItem(row_position, 2, QTableWidgetItem(str(page_number)))
    self.search_results_table.setItem(row_position, 3, QTableWidgetItem(keyword))
    self.search_results_table.setItem(row_position, 4, QTableWidgetItem(prev_sentence))
    self.search_results_table.setItem(row_position, 5, QTableWidgetItem(matched_sentence))
    self.search_results_table.setItem(row_position, 6, QTableWidgetItem(next_sentence))
```

This feature provides a powerful way to query the textual content of the user's PDF library directly within the application. 