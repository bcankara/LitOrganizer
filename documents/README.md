# LitOrganizer Project Documentation

Welcome to the official documentation for the LitOrganizer project. This documentation aims to provide a comprehensive understanding of the project's architecture, functionalities, core algorithms, and usage.

## Purpose

The goal of this documentation is to serve as a reference for:

*   **Users:** Understanding how to use the web application and CLI.
*   **Developers:** Understanding the codebase, architecture, and how to contribute or modify the project.
*   **Maintainers:** Keeping track of the project's components and logic.

## Documentation Structure

This documentation is organized into several files:

*   **`README.md`**: (This file) Provides an overview of the documentation and the project.
*   **`main_flow.md`**: Describes the main application entry point (`litorganizer.py`), argument parsing, and the choice between CLI and web execution. Includes a high-level flowchart.
*   **`pdf_processing.md`**: Details the core PDF processing logic found in `modules/core/pdf_renamer.py`. Covers DOI extraction, Gemini AI fallback, metadata fetching, file renaming, backup creation, error handling, and categorization. Includes flowcharts and code snippets.
*   **`keyword_search.md`**: Describes the keyword search functionality, including text extraction, search algorithms, and result presentation. Includes flowcharts and code snippets.
*   **`utils.md`**: Briefly covers the utility modules used throughout the project (e.g., metadata extraction helpers, file utilities, reference formatting).
*   **`Key_Algorithms_LitOrganizer.md`**: In-depth analysis of the key algorithms used in the project.

## Project Overview

LitOrganizer is a tool designed to help users organize their academic literature (PDF files) efficiently. Its main features include:

1.  **Automatic Renaming:** Extracts Digital Object Identifiers (DOIs) from PDFs, fetches metadata from various online sources (Crossref, OpenAlex, DataCite, etc.), and renames files based on a standardized citation format (APA7).
2.  **Gemini AI Fallback:** When DOI extraction fails, sends the first page text to Google Gemini Flash 2.0 for AI-powered title/author extraction and validates via Crossref.
3.  **Categorization:** Optionally categorizes the renamed files into subfolders based on metadata like journal, author, year, or subject.
4.  **Backup:** Creates backups of original files before renaming or moving them.
5.  **Error Handling:** Moves files that cannot be processed (e.g., missing DOI, insufficient metadata, encrypted PDFs) to a separate "Unnamed Article" directory.
6.  **Reference Generation:** Creates `.txt` and `.xlsx` files containing bibliographic references (APA7 format) for the processed articles.
7.  **Keyword Search:** Allows users to search for specific keywords within the text content of PDF files in a selected directory.
8.  **Web Interface:** Modern Flask + Socket.IO web application with real-time progress tracking, circular progress rings, native OS folder picker, and a persistent activity panel.
9.  **API Management:** Allows configuration of API usage including Gemini AI, Crossref, OpenAlex, Scopus, and more through the Settings page.

Navigate through the files listed above to explore specific aspects of the project in detail.
