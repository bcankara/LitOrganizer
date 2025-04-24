# LitOrganizer Project Documentation

Welcome to the official documentation for the LitOrganizer project. This documentation aims to provide a comprehensive understanding of the project's architecture, functionalities, core algorithms, and usage.

## Purpose

The goal of this documentation is to serve as a reference for:

*   **Users:** Understanding how to use the application (both GUI and CLI).
*   **Developers:** Understanding the codebase, architecture, and how to contribute or modify the project.
*   **Maintainers:** Keeping track of the project's components and logic.

## Documentation Structure

This documentation is organized into several files:

*   **`README.md`**: (This file) Provides an overview of the documentation and the project.
*   **`main_flow.md`**: Describes the main application entry point (`litorganizer.py`), argument parsing, and the choice between CLI and GUI execution. Includes a high-level flowchart.
*   **`pdf_processing.md`**: Details the core PDF processing logic found in `modules/core/pdf_renamer.py`. Covers DOI extraction, metadata fetching, file renaming, backup creation, error handling, and categorization. Includes flowcharts and code snippets.
*   **`gui.md`**: Explains the structure and workflow of the Graphical User Interface (`modules/gui/app.py`). Covers UI components, user interactions, background processing with `QThread`, and statistics display. Includes flowcharts and code snippets.
*   **`keyword_search.md`**: Describes the keyword search functionality, including text extraction, search algorithms, and result presentation. Includes flowcharts and code snippets.
*   **`utils.md`**: Briefly covers the utility modules used throughout the project (e.g., metadata extraction helpers, file utilities, reference formatting).

## Project Overview

LitOrganizer is a tool designed to help users organize their academic literature (PDF files) efficiently. Its main features include:

1.  **Automatic Renaming:** Extracts Digital Object Identifiers (DOIs) from PDFs, fetches metadata from various online sources (CrossRef, DataCite, etc.), and renames files based on a standardized citation format (e.g., APA7).
2.  **Categorization:** Optionally categorizes the renamed files into subfolders based on metadata like journal, author, year, or subject.
3.  **Backup:** Creates backups of original files before renaming or moving them.
4.  **Error Handling:** Moves files that cannot be processed (e.g., missing DOI, insufficient metadata, encrypted PDFs) to a separate "Unnamed Article" directory.
5.  **Reference Generation:** Creates `.txt` and `.xlsx` files containing bibliographic references (APA7 format) for the processed articles.
6.  **Keyword Search:** Allows users to search for specific keywords within the text content of PDF files in a selected directory.
7.  **User Interfaces:** Offers both a command-line interface (CLI) for batch processing and a graphical user interface (GUI) built with PyQt5 for interactive use.
8.  **API Management:** Allows configuration of API usage, including optional email addresses for better rate limits and API keys for services like Scopus.

Navigate through the files listed above to explore specific aspects of the project in detail. 