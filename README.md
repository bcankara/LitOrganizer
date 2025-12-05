<div align="center">
  <img src="resources/logo.png" alt="LitOrganizer Logo" width="200">
  <br>
  <h3>Organize Your Academic Literature Efficiently</h3>
  
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
  [![PyQt5](https://img.shields.io/badge/PyQt5-5.15.9-green.svg)](https://pypi.org/project/PyQt5/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
  [![GitHub stars](https://img.shields.io/github/stars/bcankara/LitOrganizer.svg)](https://github.com/bcankara/LitOrganizer/stargazers)
  [![GitHub issues](https://img.shields.io/github/issues/bcankara/LitOrganizer.svg)](https://github.com/bcankara/LitOrganizer/issues)
</div>

LitOrganizer is a powerful tool designed for researchers, academics, and students to organize their PDF literature collections automatically. It extracts metadata from academic papers, renames files according to citation standards, categorizes them into a logical directory structure, and provides powerful search capabilities.

<div align="center" style="margin: 25px auto; max-width: 850px;">
  <table style="margin: 0 auto; border-collapse: separate; border-spacing: 15px;">
    <tr>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_01.png" alt="Main Tab" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">Main Organization Tab</p>
      </td>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_04.png" alt="Search Tab" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">Search Keywords Tab</p>
      </td>
    </tr>
    <tr>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_03.png" alt="General Statistics Tab" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">General Statistics Tab</p>
      </td>
      <td align="center" style="padding: 10px; background-color: #f8f9fa; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="resources/screenshots/SS_02.png" alt="Publication Statistics Tab" width="400" style="border-radius: 8px; max-width: 100%;">
        <p style="margin-top: 15px; font-weight: bold;">Publication Statistics Tab</p>
      </td>
    </tr>
  </table>
</div>

---

## ✨ Features

### 📚 Automatic Organization
- **Smart Metadata Extraction**: Automatically extracts DOIs and retrieves complete metadata from multiple academic APIs
- **Citation-based Renaming**: Renames PDF files using APA7 format (Author_Year) for easy identification
- **Intelligent Categorization**: Organizes PDFs into folders by journal, author, year, or subject
- **Reference List Generation**: Creates a comprehensive bibliography of all processed papers

### 🔍 Advanced Search Capabilities
- **Full-text Search**: Quickly find information across your entire PDF collection
- **Context Display**: View search results with surrounding text for better understanding
- **Flexible Search Options**: Use exact match, case sensitivity, or regular expressions
- **Export Results**: Save search results to Word and Excel files with highlighted matches

### 📊 Comprehensive Statistics
- **Performance Metrics**: Visual representation of processing speed and efficiency
- **Accuracy Analysis**: Detailed breakdown of metadata quality and DOI detection rates
- **Publication Analytics**: Distribution of papers by author, journal, year, and subject
- **Error Diagnostics**: Identification of problematic files with detailed error analysis

### 💻 User-Friendly Interface
- **Modern Design**: Clean, intuitive interface with Windows 11 design principles
- **Multi-tab Layout**: Separate tabs for organization, search, and statistics
- **Progress Tracking**: Real-time progress indicators and detailed logging
- **Customizable Options**: Flexible settings to adapt to your workflow

---

## 🚀 Quick Start (One-Click Launch)

The easiest way to run LitOrganizer is using the provided launcher scripts. They will automatically:
- ✅ Check for Python 3.11 installation
- ✅ Create a virtual environment (`.venv`)
- ✅ Install all required dependencies
- ✅ Launch the application

---

### 🪟 Windows

1. **Download** or clone the repository
2. **Double-click** `start_litorganizer.bat`
3. Follow the on-screen instructions

> If Python 3.11 is not installed, the script will show you how to install it.

---

### 🍎 macOS

#### First-Time Setup (Required)

macOS has security restrictions that prevent running downloaded scripts. Follow these steps:

**Step 1: Download the Repository**
```bash
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer
```

**Step 2: Make Scripts Executable**
```bash
chmod +x start_litorganizer.sh
chmod +x "Start LitOrganizer.command"
```

**Step 3: Remove Quarantine (if downloaded as ZIP)**
```bash
xattr -cr .
```

**Step 4: Run the Application**

You have two options:

**Option A: Double-click in Finder**
1. Open Finder and navigate to the LitOrganizer folder
2. Double-click `Start LitOrganizer.command`
3. If you see "cannot be opened because it is from an unidentified developer":
   - Right-click the file → Select "Open" → Click "Open" in the dialog
   - Or go to System Preferences → Security & Privacy → Click "Open Anyway"

**Option B: Run from Terminal**
```bash
./start_litorganizer.sh
```

#### Installing Python 3.11 on macOS

If Python 3.11 is not installed, the script will offer to install it. You can also install manually:

**Using Homebrew (Recommended):**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11
```

**Using pyenv:**
```bash
brew install pyenv
pyenv install 3.11.10
pyenv global 3.11.10
```

**Official Installer:**
Download from [python.org](https://www.python.org/downloads/release/python-31110/)

#### Troubleshooting macOS Issues

| Issue | Solution |
|-------|----------|
| "Permission denied" | Run `chmod +x start_litorganizer.sh` |
| "Operation not permitted" | Run `xattr -cr .` in the project folder |
| "Unidentified developer" | Right-click → Open → Open |
| App doesn't open | Check System Preferences → Security & Privacy |
| Python not found | Install via Homebrew: `brew install python@3.11` |

---

### 🐧 Linux

**Step 1: Clone and Navigate**
```bash
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer
```

**Step 2: Make Executable and Run**
```bash
chmod +x start_litorganizer.sh
./start_litorganizer.sh
```

#### Installing Python 3.11 on Linux

**Ubuntu/Debian:**
```bash
# For Ubuntu 22.04+
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

# For older Ubuntu versions
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

**Fedora:**
```bash
sudo dnf install python3.11
```

**Arch Linux:**
```bash
sudo pacman -S python
```

---

## 📦 Alternative Installation Methods

### Docker (Cross-Platform)

```bash
# Pull the image
docker pull bcankara/litorganizer:latest

# Windows
docker run -it --rm -e DISPLAY=host.docker.internal:0 -v %cd%/pdfs:/app/pdf bcankara/litorganizer

# Linux
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd)/pdfs:/app/pdf bcankara/litorganizer

# macOS (with XQuartz)
docker run -it --rm -e DISPLAY=host.docker.internal:0 -v $(pwd)/pdfs:/app/pdf bcankara/litorganizer
```

**Requirements:**
- [Docker](https://www.docker.com/get-started)
- X11 Server: [VcXsrv](https://sourceforge.net/projects/vcxsrv/) (Windows), [XQuartz](https://www.xquartz.org/) (macOS)

### Manual Installation

```bash
# Clone repository
git clone https://github.com/bcankara/LitOrganizer.git
cd LitOrganizer

# Create virtual environment
python3.11 -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python litorganizer.py
```

---

## 📖 Usage

### GUI Mode

Run without arguments to start the graphical interface:
```bash
python litorganizer.py
```

#### Main Tab
1. Select a directory containing PDFs using the "Browse" button
2. Configure categorization options (by journal, author, year, subject)
3. Click "Start Processing" to begin organizing your files
4. Monitor progress in the log window

#### Search Keywords Tab
1. Select a directory containing PDFs
2. Enter a keyword to search for
3. Configure search options:
   - **Exact Match**: Only match complete words
   - **Case Sensitive**: Match exact letter case
   - **Use Regex**: Use regular expressions for pattern matching
4. Click "Start Search" to begin
5. View results and save to Word/Excel if desired

### Command Line Mode

```bash
python litorganizer.py -d /path/to/pdfs --create-references
```

Run `python litorganizer.py --help` for all options.

---

## ⚙️ Configuration

API settings for DOI metadata retrieval can be configured in the API Settings tab or by editing `config/api_config.json`.

---

## 🛠️ Technical Details

<div align="center">
  <table>
    <tr>
      <td align="center"><img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg"/><br>Python</td>
      <td align="center"><img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/qt/qt-original.svg"/><br>PyQt5</td>
      <td align="center"><img width="50" src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/PDF_file_icon.svg/833px-PDF_file_icon.svg.png"/><br>PDF Processing</td>
      <td align="center"><img width="50" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg"/><br>Pandas</td>
    </tr>
  </table>
</div>

**Dependencies:**
- **PyQt5**: Graphical user interface
- **PyMuPDF & pdfplumber**: PDF text extraction
- **pandas & openpyxl**: Excel file generation
- **python-docx**: Word document creation
- **requests**: API communication

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📬 Contact & Support

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
  <p>Made with ❤️ for the academic community</p>
</div>
