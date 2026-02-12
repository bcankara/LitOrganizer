<div align="center">

  <img src="resources/logo_v2.svg" alt="LitOrganizer Logo" width="480">

  <br>

  **Automated Academic PDF Organization & Search — Powered by AI**

  <br>

  [![Version](https://img.shields.io/badge/Version-2.0.0-0969da?style=for-the-badge)](https://github.com/bcankara/LitOrganizer/releases)
  [![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
  [![License: MIT](https://img.shields.io/badge/License-MIT-97ca00?style=for-the-badge)](https://opensource.org/licenses/MIT)
  [![Platform](https://img.shields.io/badge/Platform-Win%20%7C%20Mac%20%7C%20Linux-555?style=for-the-badge)]()

  <br>

  [![DOI](https://img.shields.io/badge/DOI-10.1016/j.softx.2025.102198-blue?style=flat-square&logo=doi&logoColor=white)](https://doi.org/10.1016/j.softx.2025.102198)
  [![SoftwareX](https://img.shields.io/badge/SoftwareX-Elsevier-orange?style=flat-square)](https://www.sciencedirect.com/journal/softwarex)
  [![SCI-E](https://img.shields.io/badge/Indexed-SCI--E-success?style=flat-square)](https://mjl.clarivate.com/)
  [![GitHub stars](https://img.shields.io/github/stars/bcankara/LitOrganizer?style=flat-square)](https://github.com/bcankara/LitOrganizer/stargazers)
  [![GitHub issues](https://img.shields.io/github/issues/bcankara/LitOrganizer?style=flat-square)](https://github.com/bcankara/LitOrganizer/issues)

  <br>

  <sub>Published in <a href="https://doi.org/10.1016/j.softx.2025.102198"><b>SoftwareX (Elsevier)</b></a> · Science Citation Index Expanded (SCI-E)</sub>

</div>

<br>

<p align="center">
  <a href="#-key-features">Features</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#-naming-pipeline">Pipeline</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-documentation">Docs</a> •
  <a href="#-citation">Citation</a>
</p>

---

> LitOrganizer is an open-source tool for researchers, academics, and students to **automatically organize PDF literature collections**. It extracts metadata via DOI lookup, queries multiple academic APIs, and leverages **Google Gemini AI** as an intelligent fallback — then renames files using citation standards, categorizes them into a logical directory structure, and provides **full-text search** through a modern, real-time web interface.

---

## ✨ Key Features

<table>
  <tr>
    <td width="50%" valign="top">

### 🔍 Smart Metadata Extraction
- DOI detection from PDF text
- 7+ academic APIs (Crossref, OpenAlex, DataCite, Europe PMC, Semantic Scholar, Scopus, Unpaywall)
- **Gemini AI** fallback for papers without DOIs

</td>
    <td width="50%" valign="top">

### 📝 Citation-Based Renaming
- APA 7th edition format: `(Author, Year) - Title.pdf`
- Automatic folder categorization (journal, author, year, subject)
- Backup system for original files

</td>
  </tr>
  <tr>
    <td width="50%" valign="top">

### 🔎 Advanced Full-Text Search
- Search across entire PDF collections
- Regex & exact match support
- Export results to **Word** / **Excel** with highlights

</td>
    <td width="50%" valign="top">

### 📊 Real-Time Web Interface
- WebSocket live progress with animated rings
- Native OS folder picker
- Comprehensive statistics & analytics dashboard

</td>
  </tr>
  <tr>
    <td width="50%" valign="top">

### 🤖 Google Gemini AI Integration
- Extracts title, authors & year from PDF content
- Real-time AI status panel during processing
- Configurable placement of AI-named files

</td>
    <td width="50%" valign="top">

### 📋 Reference Generation
- Auto-generated bibliography of all processed papers
- Publication analytics by author, journal & year
- Detailed error diagnostics for problematic files

</td>
  </tr>
</table>

---

## 📸 Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="resources/screenshots/SS_01.png" alt="Process Page" width="420">
        <br><sub><b>Processing Page</b> — Real-time progress with AI panel</sub>
      </td>
      <td align="center">
        <img src="resources/screenshots/SS_04.png" alt="Statistics" width="420">
        <br><sub><b>Statistics Dashboard</b> — Comprehensive analytics</sub>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="resources/screenshots/SS_03.png" alt="Results" width="420">
        <br><sub><b>Rename Results</b> — Detailed file processing log</sub>
      </td>
      <td align="center">
        <img src="resources/screenshots/SS_02.png" alt="Searcher" width="420">
        <br><sub><b>Searcher</b> — Full-text search with export</sub>
      </td>
    </tr>
  </table>
</div>

---

## 🔬 Naming Pipeline

LitOrganizer uses a multi-stage pipeline to extract metadata and name your PDF files:

```mermaid
flowchart LR
    A["📄 PDF File"] --> B{"DOI Found?"}
    B -- Yes --> C["🔗 Query Academic APIs"]
    C --> D["✅ Named Article/"]
    B -- No --> E{"Gemini AI\nEnabled?"}
    E -- Yes --> F["🤖 AI Extraction\n(Title, Authors, Year)"]
    F --> G{"Validated via\nCrossref?"}
    G -- Yes --> D
    G -- No --> H["📁 AI Named Content/\n(if separate folder)"]
    E -- No --> I["❓ Unnamed Article/"]
    G -- Fail --> I
```

### Output Directory Structure

```
your_pdf_folder/
├── Named Article/          # DOI + API verified or Gemini AI validated
├── AI Named Content/       # Gemini AI named (optional separate folder)
├── Unnamed Article/        # No metadata found
└── backups/                # Original file backups (if enabled)
```

---

## 🚀 Quick Start

The launcher scripts handle everything automatically — Python check, virtual environment, dependencies, and server startup.

<details open>
<summary><b>🪟 Windows</b></summary>

1. **Download** or clone the repository  
2. **Double-click** `start_litorganizer.bat`  
3. Open `http://localhost:5000` in your browser

</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer
chmod +x start_litorganizer.sh "Start LitOrganizer.command"
```

**Option A:** Double-click `Start LitOrganizer.command` in Finder  
**Option B:** Run `./start_litorganizer.sh` in Terminal

> **Note:** If downloaded as ZIP, remove quarantine first: `xattr -cr .`

</details>

<details>
<summary><b>🐧 Linux</b></summary>

```bash
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer
chmod +x start_litorganizer.sh
./start_litorganizer.sh
```

</details>

### Manual Installation

```bash
# Clone & setup
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# Install & run
pip install -r requirements.txt
python litorganizer.py
```

<details>
<summary><b>Command Line Mode</b></summary>

```bash
python litorganizer.py -d /path/to/pdfs --create-references
```

Run `python litorganizer.py --help` for all available options.

</details>

---

## 📖 Documentation

For detailed usage instructions, see the **[User Guide](documents/GUIDE.md)** which covers:

- 🔄 Naming pipeline and confidence levels
- 🤖 Gemini AI setup and configuration
- 🔎 Keyword search with regex examples
- 📁 Output folder structure
- ⚙️ API reference and configuration

> 💡 **In-App Guide**: After launching, click **Guide** in the navigation menu for interactive documentation.

---

## ⚙️ Configuration

API settings can be managed on the **Settings** page or by editing `config/api_keys.json`.

| API | Status | Requires |
|:----|:------:|:--------:|
| Crossref | ✅ Enabled | — |
| OpenAlex | ✅ Enabled | Email |
| DataCite | ✅ Enabled | — |
| Europe PMC | ✅ Enabled | — |
| Semantic Scholar | ✅ Enabled | — |
| Scopus | ⬚ Disabled | API Key |
| Unpaywall | ⬚ Disabled | Email |
| **Google Gemini AI** | **⬚ Disabled** | **API Key** |

<details>
<summary><b>🤖 Gemini AI Setup</b></summary>

1. Go to the **Settings** page  
2. Toggle **Google Gemini Flash** on  
3. Enter your API key from [Google AI Studio](https://aistudio.google.com/apikey)  
4. Save — Gemini AI will be used as a fallback when DOI extraction fails

</details>

---

## 🛠️ Tech Stack

<div align="center">
  <table>
    <tr>
      <td align="center" width="100"><img width="48" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"/><br><sub><b>Python</b></sub></td>
      <td align="center" width="100"><img width="48" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg"/><br><sub><b>Flask</b></sub></td>
      <td align="center" width="100"><img width="36" src="https://socket.io/images/logo.svg"/><br><sub><b>Socket.IO</b></sub></td>
      <td align="center" width="100"><img width="48" src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Tailwind_CSS_Logo.svg"/><br><sub><b>Tailwind CSS</b></sub></td>
      <td align="center" width="100"><img width="48" src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/PDF_file_icon.svg/833px-PDF_file_icon.svg.png"/><br><sub><b>PDF Tools</b></sub></td>
    </tr>
  </table>
</div>

| Layer | Technologies |
|:------|:-------------|
| **Backend** | Flask · Flask-SocketIO · PyMuPDF · pdfplumber · Google Gemini Flash 2.0 API |
| **Frontend** | Tailwind CSS · Socket.IO Client · SVG Progress Rings · Native OS Dialog |
| **Data** | pandas · openpyxl · python-docx · requests |

---

## 🗺️ Roadmap

- [x] Modern web interface with real-time updates
- [x] DOI fallback with Crossref title search
- [x] Google Gemini AI integration
- [x] Native OS folder picker
- [x] Built-in usage guide
- [ ] Batch export in BibTeX / RIS format
- [ ] Docker support
- [ ] Dark mode

---

## 📄 Citation

If you use **LitOrganizer** in your research, please cite:

> Şahin, A., Kara, B. C., & Dirsehan, T. (2025). LitOrganizer: Automating the process of data extraction and organization for scientific literature reviews. *SoftwareX*, *30*, 102198. https://doi.org/10.1016/j.softx.2025.102198

<details>
<summary><b>BibTeX</b></summary>

```bibtex
@article{sahin2025litorganizer,
  title     = {LitOrganizer: Automating the process of data extraction and organization for scientific literature reviews},
  author    = {Şahin, Alperen and Kara, Burak Can and Dirsehan, Taşkın},
  journal   = {SoftwareX},
  volume    = {30},
  pages     = {102198},
  year      = {2025},
  publisher = {Elsevier},
  doi       = {10.1016/j.softx.2025.102198}
}
```

</details>

---

## 📋 Changelog

<details>
<summary><b>v2.0.0 — AI-Powered Web Application (Latest)</b></summary>

> **Major Release:** Complete redesign from PyQt5 desktop app to Flask + Socket.IO web application with Google Gemini AI integration.

#### ✅ Added
- Google Gemini AI integration with real-time status panel
- Modern web interface with Tailwind CSS
- WebSocket-powered live progress tracking with circular progress rings
- Native OS folder picker with quick access shortcuts
- Multi-stage DOI fallback pipeline
- Global activity panel & completion modal
- Comprehensive usage guide page
- Search export to Word/Excel with highlights

#### 🔧 Fixed
- Backup system file copy scope issue
- Cross-platform path separator in "Open Folder"
- Statistics persistence across page navigation
- Progress ring synchronization

#### 🔄 Changed
- Architecture: PyQt5 → Flask + Socket.IO
- Default AI-named files go to `Named Article/` (configurable)
- Native OS dialog replaces drag-and-drop zone
- Python requirement broadened to 3.10+

#### 🗑️ Removed
- PyQt5 desktop GUI & `modules/gui/` directory
- `--gui` CLI argument
- Drag & drop directory selection
- Heuristic regex-based content extraction

</details>

<details>
<summary><b>v1.x — Desktop Application (Legacy)</b></summary>

- PyQt5-based desktop GUI with tabbed interface
- Basic progress bar
- Local-only operation

</details>

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

```
1. Fork the repository
2. Create your feature branch    →  git checkout -b feature/AmazingFeature
3. Commit your changes           →  git commit -m 'Add AmazingFeature'
4. Push to the branch            →  git push origin feature/AmazingFeature
5. Open a Pull Request
```

---

## 📬 Contact & Support

<div align="center">

[![Issues](https://img.shields.io/badge/Report%20Bug-GitHub%20Issues-red?style=for-the-badge&logo=github)](https://github.com/bcankara/LitOrganizer/issues)
[![Discussions](https://img.shields.io/badge/Ask%20Question-GitHub%20Discussions-blue?style=for-the-badge&logo=github)](https://github.com/bcankara/LitOrganizer/discussions)

</div>

---

<div align="center">
  <a href="https://github.com/bcankara/LitOrganizer/stargazers">
    <img src="https://img.shields.io/github/stars/bcankara/LitOrganizer?style=social" alt="Stars">
  </a>
  &nbsp;
  <a href="https://github.com/bcankara/LitOrganizer/fork">
    <img src="https://img.shields.io/github/forks/bcankara/LitOrganizer?style=social" alt="Forks">
  </a>
  <br><br>
  <sub>Made with ❤️ for the academic community</sub>
</div>
