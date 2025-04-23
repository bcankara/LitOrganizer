# LitOrganizer

A powerful tool for organizing academic PDF literature by extracting citation information, renaming files, and searching through PDF content.

![LitOrganizer](resources/icon_windows.png)

## Features

### Main Features
- **Automatic Organization**: Rename PDF files based on citation information extracted from DOI metadata
- **Citation Formatting**: Use APA7 format for file naming and references
- **Directory Structure Creation**: Optionally categorize files by journal, author, year, or subject
- **Reference List Generation**: Create Excel file with complete citations for all processed PDFs
- **Backup Protection**: Create backups of original files before renaming

### Advanced Search Capabilities
- **Full-text Search**: Search for keywords across all PDFs in a directory
- **Context Display**: View the keyword with surrounding sentences
- **Search Options**: Use exact match, case sensitivity, or regular expressions
- **Export Results**: Save search results to Word and Excel files with highlighted matches

## Installation

### Requirements
- Python 3.8 or later
- Required Python packages (see `requirements.txt`)
- For OCR functionality: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

### Installation Steps

1. Clone or download this repository:
   ```
   git clone https://github.com/yourusername/litorganizer.git
   cd litorganizer
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. (Optional) For OCR functionality, install Tesseract OCR:
   - Windows: Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

## Usage

### GUI Mode

Run the application without arguments to start in GUI mode:
```
python litorganizer.py
```

The GUI provides two main tabs:
1. **Main**: For organizing PDFs using DOI metadata
2. **Search Keywords**: For searching text within PDFs

#### Main Tab
1. Select a directory containing PDFs
2. (Optional) Configure categorization options
3. Click "Start Processing" to begin

#### Search Keywords Tab
1. Select a directory containing PDFs
2. Enter a keyword to search for
3. (Optional) Configure search options:
   - **Exact Match**: Only match complete words
   - **Case Sensitive**: Match exact letter case
   - **Use Regex**: Use regular expressions for pattern matching
4. Click "Start Search" to begin
5. View results and save to Word/Excel if desired

### Command Line Mode

Basic usage:
```
python litorganizer.py -d /path/to/pdfs
```

Additional options:
```
python litorganizer.py --help
```

## Configuration

API settings for DOI metadata retrieval can be configured in the API Settings tab or by editing `config/api_config.json`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with PyQt5 for the user interface
- Uses pdfplumber and PyMuPDF for PDF text extraction
- Integrated with the Crossref API for metadata retrieval 