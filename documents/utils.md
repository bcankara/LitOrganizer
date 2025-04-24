# Utility Modules (`modules/utils/`)

This document provides a brief overview of the utility modules found in the `modules/utils/` directory. These modules contain reusable functions and classes that support the core processing and GUI functionalities.

## `pdf_metadata_extractor.py`

This is a crucial utility module responsible for extracting information from PDF files and fetching metadata from external APIs.

*   **`extract_doi(file_path, use_ocr)`:** Attempts to find a DOI string within the PDF content. It uses regular expressions and can optionally leverage OCR (Tesseract) via `pytesseract` if `use_ocr` is `True`.
*   **`get_metadata_from_crossref(doi, email)`:** Queries the CrossRef API using a DOI to retrieve bibliographic metadata.
*   **`get_metadata_from_datacite(doi)`:** Queries the DataCite API.
*   **`get_metadata_from_europepmc(doi)`:** Queries the Europe PMC API.
*   **`get_metadata_from_openaire(doi)`:** (Potentially, if implemented) Queries the OpenAIRE API.
*   **`get_metadata_from_scopus(doi, api_key)`:** Queries the Scopus API (requires an API key).
*   **`get_metadata_from_semantic_scholar(doi, api_key)`:** Queries the Semantic Scholar API (optionally uses API key).
*   **`get_metadata_from_unpaywall(doi, email)`:** Queries the Unpaywall API (optionally uses email).
*   **`get_metadata_from_openalex(doi, email)`:** Queries the OpenAlex API (optionally uses email).
*   **`get_metadata_from_multiple_sources(doi)`:** The main function used by `PDFProcessor`. It tries multiple APIs in a preferred order (defined within the function) until sufficient metadata is found. It loads API keys and email configurations from `config/api_keys.json`.
*   **`has_sufficient_metadata(metadata)`:** Checks if a retrieved metadata dictionary contains the essential fields (e.g., title, author, year) required for renaming.
*   **`extract_metadata_from_content(file_path)`:** (Currently less used in the main flow) Attempts to extract metadata directly from PDF text content using heuristics when API methods fail.
*   **`load_api_config()`:** Loads API keys and settings from the JSON configuration file.
*   **Error Classes:** Defines custom exceptions like `PDFReadError`, `PDFEncryptedError`, `MetadataAPIError`.

## `reference_formatter.py`

Contains functions to format bibliographic information according to specific citation styles.

*   **`create_apa7_citation(metadata)`:** Creates a short in-text citation string (e.g., "(Author, Year)") based on APA 7th edition style from the metadata dictionary.
*   **`create_apa7_reference(metadata)`:** Creates a full bibliographic reference string formatted according to APA 7th edition style.

## `file_utils.py`

Provides helper functions for file and directory operations.

*   **`ensure_dir(dir_path)`:** Checks if a directory exists, and creates it if it doesn't.
*   **`sanitize_filename(filename)`:** Removes or replaces characters that are invalid in filenames across different operating systems.
*   **`get_version()`:** Reads the project version from the `pyproject.toml` file.

These utility modules encapsulate specific functionalities, promoting code reuse and maintainability throughout the LitOrganizer project. 