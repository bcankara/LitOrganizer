<div align="center">
  <img src="resources/logo_v2.svg" alt="LitOrganizer Logo" width="200">
  <br>
  <h3>V2 - Automated Academic PDF Organization with AI</h3>
  
  [![Version](https://img.shields.io/badge/Version-2.0.0-blue.svg)]()
  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
  [![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
  [![Gemini AI](https://img.shields.io/badge/Gemini_AI-Flash_2.0-blueviolet.svg)](https://ai.google.dev/)
  [![Socket.IO](https://img.shields.io/badge/Socket.IO-Realtime-orange.svg)](https://socket.io/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
  [![GitHub stars](https://img.shields.io/github/stars/bcankara/LitOrganizer.svg)](https://github.com/bcankara/LitOrganizer/stargazers)
  [![GitHub issues](https://img.shields.io/github/issues/bcankara/LitOrganizer.svg)](https://github.com/bcankara/LitOrganizer/issues)

  <br>

  > **Published in [SoftwareX (Elsevier)](https://doi.org/10.1016/j.softx.2025.102198) · SCI-E**
  > <br>An open-source tool for automated academic PDF organization using DOI extraction, multi-API metadata retrieval, and AI-powered naming.
</div>

## 📚 Citation

<div align="center">

[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.softx.2025.102198-blue?style=for-the-badge&logo=doi&logoColor=white)](https://doi.org/10.1016/j.softx.2025.102198)
[![Journal](https://img.shields.io/badge/SoftwareX-Elsevier-orange?style=for-the-badge&logo=elsevier&logoColor=white)](https://www.sciencedirect.com/journal/softwarex)
[![Indexed](https://img.shields.io/badge/Indexed-SCI--E-green?style=for-the-badge)](https://mjl.clarivate.com/)

</div>

<br>

If you use **LitOrganizer** in your research, please cite our paper:

<table>
<tr>
<td>

### 📄 APA 7th Edition

> Şahin, A., Kara, B. C., & Dirsehan, T. (2025). LitOrganizer: Automating the process of data extraction and organization for scientific literature reviews. *SoftwareX*, *30*, 102198. https://doi.org/10.1016/j.softx.2025.102198

</td>
</tr>
</table>

<details>
<summary><b>📋 BibTeX</b> (click to expand)</summary>

```bibtex
@article{sahin2025litorganizer,
  title     = {LitOrganizer: Automating the process of data extraction and 
               organization for scientific literature reviews},
  author    = {Şahin, Alperen and Kara, Burak Can and Dirsehan, Taşkın},
  journal   = {SoftwareX},
  volume    = {30},
  pages     = {102198},
  year      = {2025},
  publisher = {Elsevier},
  doi       = {10.1016/j.softx.2025.102198},
  url       = {https://doi.org/10.1016/j.softx.2025.102198}
}
```

</details>

<details>
<summary><b>📋 RIS</b> (click to expand)</summary>

```ris
TY  - JOUR
T1  - LitOrganizer: Automating the process of data extraction and organization for scientific literature reviews
AU  - Şahin, Alperen
AU  - Kara, Burak Can
AU  - Dirsehan, Taşkın
JO  - SoftwareX
VL  - 30
SP  - 102198
PY  - 2025
PB  - Elsevier
DO  - 10.1016/j.softx.2025.102198
UR  - https://doi.org/10.1016/j.softx.2025.102198
ER  - 
```

</details>

---

LitOrganizer is a powerful tool designed for researchers, academics, and students to organize their PDF literature collections automatically. It extracts metadata from academic papers using DOI lookup, multi-API validation, and **Google Gemini AI** as an intelligent fallback — then renames files according to citation standards, categorizes them into a logical directory structure, and provides powerful search capabilities through a modern, real-time web interface.

<div align="center" style="margin: 25px auto; max-width: 850px;">
  <table style="margin: 0 auto; border-collapse: separate; border-spacing: 15px;">
    <tr>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_01.png" alt="Process Page" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">Process Page</p>
      </td>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_04.png" alt="General Statistic" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">General Statistic</p>
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_03.png" alt="Rename Results" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">Rename Results</p>
      </td>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_02.png" alt="Term Search" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">Term Search</p>
      </td>
    </tr>
  </table>
</div>

---

## Naming Pipeline

LitOrganizer uses a multi-stage pipeline to extract metadata and name your PDF files:

```
PDF File
  │
  ├─ Stage 1: DOI Extraction
  │   Extract DOI from PDF text → Query academic APIs (Crossref, OpenAlex, etc.)
  │   ✅ Success → Named Article/
  │
  ├─ Stage 2: Gemini AI (Optional)
  │   Send first page text to Google Gemini Flash 2.0
  │   AI extracts title, authors, year → Validate via Crossref
  │   ✅ Success → Named Article/ (default) or AI Named Content/ (if separate folder enabled)
  │
  └─ Stage 3: Unresolved
      No metadata found
      → Unnamed Article/
```

### Output Directory Structure

```
your_pdf_folder/
  Named Article/          # Successfully named (DOI + API or Gemini AI validated)
  AI Named Content/       # Gemini AI named (only if "Separate AI Folder" option enabled)
  Unnamed Article/        # No naming method succeeded
  backups/                # Original file backups (if enabled)
```

---

## Features

### Automatic Organization
- **Smart Metadata Extraction**: Extracts DOIs and retrieves complete metadata from multiple academic APIs (Crossref, OpenAlex, DataCite, Europe PMC, Semantic Scholar, Scopus, Unpaywall)
- **Gemini AI Fallback**: When DOI extraction fails, sends the first page text to Google Gemini Flash 2.0 for AI-powered title/author extraction — configurable in Settings
- **Citation-based Renaming**: Renames PDF files using APA7 format — `(Author, Year) - Title.pdf`
- **Intelligent Categorization**: Organizes PDFs into folders by journal, author, year, or subject
- **Backup System**: Creates backups of all original files before renaming
- **Reference List Generation**: Creates a comprehensive bibliography of all processed papers

### Google Gemini AI Integration
- **AI-Powered Metadata Extraction**: Uses Google Gemini Flash 2.0 to extract title, authors, and year from PDF content
- **Real-time Status Panel**: Inline Gemini AI results panel on the processing page showing connection status, active queries, and extracted metadata
- **Configurable Placement**: AI-named files go to `Named Article/` by default, or a separate `AI Named Content/` folder if preferred
- **Optional Feature**: Enable/disable in Settings with your own Google AI Studio API key

### Advanced Search
- **Full-text Search**: Quickly find information across your entire PDF collection
- **Context Display**: View search results with surrounding text for better understanding
- **Flexible Options**: Exact match, case sensitivity, regular expressions
- **Export Results**: Save search results to Word and Excel files with highlighted matches

### Comprehensive Statistics
- **Performance Metrics**: Visual representation of processing speed and efficiency
- **Accuracy Analysis**: Detailed breakdown of metadata quality and DOI detection rates
- **Publication Analytics**: Distribution of papers by author, journal, year, and subject
- **Error Diagnostics**: Identification of problematic files with detailed error analysis

### Real-time Web Interface
- **WebSocket Communication**: Live progress updates without page refresh
- **Circular Progress Rings**: Animated, mobile-style progress indicators
- **Native OS Folder Picker**: Select directories using the system dialog — no path typing needed
- **Quick Access Shortcuts**: One-click access to Desktop, Documents, Downloads, and drives in the manual browser
- **Persistent State**: Processing status survives page navigation
- **Global Activity Panel**: Persistent bottom panel with progress rings and compact log output across all pages
- **Completion Modal**: Summary statistics after processing with "Open Folder" and "View Statistics" buttons
- **Built-in Usage Guide**: Comprehensive guide page with pipeline documentation and API reference

---

## Quick Start

The easiest way to run LitOrganizer is using the provided launcher scripts. They will automatically:
- Check for Python 3.10+ installation
- Create a virtual environment (`.venv`)
- Install all required dependencies
- Launch the web application on `http://localhost:5000`

### Windows

1. **Download** or clone the repository
2. **Double-click** `start_litorganizer.bat`
3. Open your browser to `http://localhost:5000`

### macOS

```bash
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer
chmod +x start_litorganizer.sh "Start LitOrganizer.command"
```

**Option A:** Double-click `Start LitOrganizer.command` in Finder
**Option B:** Run `./start_litorganizer.sh` in Terminal

> If downloaded as ZIP, remove quarantine first: `xattr -cr .`

### Linux

```bash
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer
chmod +x start_litorganizer.sh
./start_litorganizer.sh
```

---

## Manual Installation

```bash
# Clone repository
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer

# Create virtual environment
python3 -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python litorganizer.py
```

### Command Line Mode

```bash
python litorganizer.py -d /path/to/pdfs --create-references
```

Run `python litorganizer.py --help` for all available options.

---

## Usage

1. Launch the application — it opens a web server at `http://localhost:5000`
2. Navigate to the **Process** page
3. Click **Select PDF Folder** to open the native OS file dialog (or click "Browse Manually" for the built-in browser with quick access shortcuts)
4. Configure options (categorization, OCR, backup, separate AI folder, etc.)
5. Click **Start Processing** and watch real-time progress via circular progress rings and the Gemini AI panel
6. When complete, a summary modal shows results with "Open Folder" and "View Statistics" buttons

### Gemini AI Setup

1. Go to the **Settings** page
2. In the "AI-Powered Extraction" section, toggle **Google Gemini Flash** on
3. Enter your API key from [Google AI Studio](https://aistudio.google.com/apikey)
4. Save settings — Gemini AI will now be used as a fallback when DOI extraction fails

---

## Configuration

API settings for metadata retrieval can be configured on the **Settings** page or by editing `config/api_keys.json`.

| API | Default | Requires |
|-----|---------|----------|
| Crossref | Enabled | — |
| OpenAlex | Enabled | Email |
| DataCite | Enabled | — |
| Europe PMC | Enabled | — |
| Semantic Scholar | Enabled | — |
| Scopus | Disabled | API Key |
| Unpaywall | Disabled | Email |
| **Google Gemini AI** | **Disabled** | **API Key** |

---

## Technical Details

<div align="center">
  <table>
    <tr>
      <td align="center"><img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"/><br>Python</td>
      <td align="center"><img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg"/><br>Flask</td>
      <td align="center"><img width="40" src="https://socket.io/images/logo.svg"/><br>Socket.IO</td>
      <td align="center"><img width="50" src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Tailwind_CSS_Logo.svg"/><br>Tailwind CSS</td>
      <td align="center"><img width="50" src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/PDF_file_icon.svg/833px-PDF_file_icon.svg.png"/><br>PDF Processing</td>
    </tr>
  </table>
</div>

**Backend:**
- **Flask** + **Flask-SocketIO**: Web framework with real-time WebSocket communication
- **PyMuPDF** & **pdfplumber**: PDF text extraction
- **Google Gemini Flash 2.0 API**: AI-powered metadata extraction (REST API via `requests`)
- **requests**: API communication with academic metadata providers
- **pandas** & **openpyxl**: Excel file generation
- **python-docx**: Word document creation

**Frontend:**
- **Tailwind CSS**: Utility-first CSS framework
- **Socket.IO Client**: Real-time bidirectional communication
- **SVG Progress Rings**: Animated circular progress indicators
- **Native OS File Dialog**: System-level folder picker via tkinter backend

---

## Roadmap

- [x] Modern web interface with real-time updates (v2.0)
- [x] DOI Fallback with Crossref title search (v2.0)
- [x] Google Gemini AI integration for metadata extraction (v2.0)
- [x] Native OS folder picker (v2.0)
- [x] Usage guide page (v2.0)
- [ ] Batch Export in BibTeX/RIS format
- [ ] Docker Support
- [ ] Dark Mode

---

## Changelog

### v2.0.0 — AI-Powered Web Application

> **Major Release:** LitOrganizer has been completely redesigned from a PyQt5 desktop application to a modern Flask + Socket.IO web application with Google Gemini AI integration.

#### Added

- **Google Gemini AI Integration**: AI-powered metadata extraction using Gemini Flash 2.0 as an intelligent fallback when DOI extraction fails. Sends first-page text to the AI, extracts title/authors/year, and validates via Crossref. Configurable in Settings with API key management.
- **Inline Gemini AI Panel**: Real-time results panel on the processing page showing connection status, active queries, extracted metadata (title, authors, year), and a counter of AI-processed files.
- **Separate AI Folder Option**: Checkbox in processing options to place Gemini AI-named files in a dedicated `AI Named Content/` folder instead of the default `Named Article/`.
- **Modern Web Interface**: Clean, responsive UI built with Tailwind CSS and an academic-inspired design system.
- **Real-time Updates**: WebSocket-powered live progress tracking with circular progress rings for both PDF processing and keyword search.
- **Native OS Folder Picker**: Select PDF directories using the native operating system file dialog (primary method) with a built-in directory browser as an alternative.
- **Quick Access Shortcuts**: The manual browse modal includes one-click shortcuts to Desktop, Documents, Downloads, and all available drives.
- **DOI Fallback Pipeline**: Multi-stage metadata extraction: DOI → Gemini AI → Crossref title validation → categorized output.
- **Global Activity Panel**: A persistent bottom panel visible across all pages showing circular progress indicators and a compact log output.
- **Completion Modal**: Detailed summary after processing (processed/renamed/unnamed counts, success rate) with "Open Folder" and "View Statistics" buttons.
- **State Persistence**: Processing progress, file statuses, and statistics survive page navigation with loading overlay during state restoration.
- **Usage Guide Page**: Comprehensive documentation page with naming pipeline flowchart, Gemini AI setup instructions, output folder structure, and API reference.
- **Search Export Modal**: Post-search export dialog for saving results to Word/Excel.
- **Search Warning Modal**: Confirmation dialog when starting a new search while previous results exist.
- **Published SCI-E Banner**: Header banner linking to the SoftwareX publication.
- **Full English Localization**: All UI text, log messages, and code comments translated to English.

#### Fixed

- **Backup System**: Resolved an issue where original PDF files were not being backed up before renaming — `shutil.copy2` was incorrectly scoped inside a conditional check.
- **Open Folder Button**: The completion modal now correctly opens the output directory using platform-appropriate commands. Fixed cross-platform path separator issue.
- **Statistics Persistence**: File processing statistics and the completion modal persist across page navigation.
- **Real-time Counter Updates**: Processing statistics (Processed, Renamed, Unnamed) update in real-time during PDF processing.
- **Progress Ring Synchronization**: Search and processing progress rings stay synchronized between the bottom panel and page-level indicators.

#### Changed

- **Architecture**: Complete migration from PyQt5 desktop GUI to Flask + Socket.IO web application.
- **Naming Pipeline**: Default Gemini AI-named files now go to `Named Article/` (previously `AI_Named_Content/`), with an optional separate folder setting.
- **Directory Selection**: "Select Folder" button with native OS dialog replaces the old drag-and-drop zone.
- **Logo**: Updated to `logo_v2.svg`.
- **Launcher Scripts**: Modernized — removed PyQt5 references, added Flask/pdfplumber dependency checks, simplified banners.
- **Python Requirement**: Broadened from 3.11 to 3.10+.

#### Removed

- **PyQt5 Desktop GUI**: The legacy PyQt5-based graphical interface has been completely removed. LitOrganizer is now exclusively a web application.
- **`modules/gui/` Directory**: All desktop GUI code deleted.
- **`--gui` CLI Argument**: Removed from the argument parser.
- **Drag & Drop Directory Selection**: Removed due to browser security limitations preventing full system path access.
- **Heuristic Content Extraction**: The regex-based title/author extraction has been replaced by Google Gemini AI.

### v1.x — Desktop Application (Legacy)

- PyQt5-based desktop GUI with tabbed interface
- Basic progress bar
- Local-only operation

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/bcankara/LitOrganizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bcankara/LitOrganizer/discussions)

---

<div align="center">
  <a href="https://github.com/bcankara/LitOrganizer/stargazers">
    <img src="https://img.shields.io/github/stars/bcankara/LitOrganizer?style=social" alt="Stars">
  </a>
  <a href="https://github.com/bcankara/LitOrganizer/fork">
    <img src="https://img.shields.io/github/forks/bcankara/LitOrganizer?style=social" alt="Forks">
  </a>
  <br><br>
  <p>Made with care for the academic community</p>
</div>
