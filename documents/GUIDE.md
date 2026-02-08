# LitOrganizer User Guide

> **LitOrganizer v2.0.0** — Academic PDF Management Platform  
> Last updated: February 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Naming Pipeline](#2-naming-pipeline)
3. [Gemini AI Integration](#3-gemini-ai-integration)
4. [Keyword Search](#4-keyword-search)
5. [Output Structure](#5-output-structure)
6. [API Reference](#6-api-reference)

---

## 1. Overview

LitOrganizer is an automated academic PDF management tool that **extracts metadata** from scientific publications and **renames** them in standardized **APA 7th edition** citation format:

```
(Author, Year) - Title of the Paper.pdf
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Automated Naming** | DOI extraction, multi-API metadata retrieval, and AI-powered fallback |
| **AI-Powered** | Google Gemini Flash integration for intelligent metadata extraction |
| **Full-Text Search** | Keyword search across entire PDF collections with regex support |

### Quick Start

1. **Select Folder** — Native file picker or built-in browser
2. **Configure** — Backup, OCR, categorization options
3. **Process** — Real-time progress tracking
4. **Review** — Statistics and organized files

### Processing Options

| Option | Description | Default |
|--------|-------------|---------|
| Create Backups | Copies originals to `backups/` before renaming | ON |
| Create References | Generates APA7 bibliography in Excel + Text format | OFF |
| Move Unnamed | Moves unprocessable files to `Unnamed Article/` | OFF |
| Use OCR | Optical character recognition for scanned PDFs | OFF |

---

## 2. Naming Pipeline

LitOrganizer employs a **multi-stage pipeline** to maximize naming success rate:

```
PDF File
│
├─ Stage 1: DOI Extraction
│   DOI is searched via regex from PDF content
│   │
│   ├─ DOI Found ─────────────────┐
│   │                             │
│   │   Stage 2a: API Metadata    │
│   │   Crossref, OpenAlex, etc.  │
│   │   ✅ → Named Article/       │
│   │                             │
│   └─ DOI Not Found ─────────────┤
│                                 │
│       Stage 2b: Gemini AI       │
│       AI extracts title,        │
│       authors, year             │
│       │                         │
│       └─ Stage 3: Validation    │
│          Crossref title match   │
│          │                      │
│          ├─ ≥80% Match          │
│          │  ✅ → Named Article/ │
│          │                      │
│          └─ <80% Match          │
│             ✅ → AI_Named_Content/
│
└─ All Methods Failed
   ❌ → Unnamed Article/
```

### Confidence Levels

| Level | Folder | Description |
|-------|--------|-------------|
| 🟢 **HIGH** | Named Article/ | DOI found and verified via API, or Crossref title match ≥80% |
| 🟡 **MEDIUM** | AI_Named_Content/ | No DOI, no Crossref match, but Gemini AI successfully extracted metadata |
| 🔴 **FAILED** | Unnamed Article/ | No naming method succeeded. File may be encrypted or not academic |

---

## 3. Gemini AI Integration

An advanced system that uses **Google Gemini Flash 2.0** AI to automatically extract title, author, and year information from PDFs where DOI could not be found.

### How It Works

1. **Text Extraction** — Text is extracted from the first 2 pages using `pdfplumber`
2. **AI Analysis** — Text is sent to Gemini Flash API. AI understands academic structure and extracts metadata
3. **Validation** — AI result is validated via Crossref API. If no match, the file is named using AI data

### AI Response Format

```json
{
  "title": "The Role of Openness and Cultural Intelligence...",
  "authors": ["Bukovec", "Erksenc", "Burcdo"],
  "year": "2024"
}
```

### Setup

| Setting | Details |
|---------|---------|
| **API Key** | Get a free key at [Google AI Studio](https://aistudio.google.com/apikey) |
| **Free Tier** | 15 requests/minute, 1,500 requests/day |
| **Model** | `gemini-2.0-flash` |
| **Activation** | Settings → AI-Powered Extraction → Toggle ON + paste API Key |

> ⚠️ **Note:** If Gemini AI is disabled or no API key is provided, files without DOI will be moved directly to `Unnamed Article/`.

---

## 4. Keyword Search

Search for specific keywords across your entire PDF collection.

### Search Modes

| Mode | Description | Example |
|------|-------------|---------|
| Standard | Case-insensitive, partial match | `education` → Education, EDUCATION |
| Exact Match | Word boundary detection | `education` ≠ educational |
| Case Sensitive | Exact case matching | `DNA` ≠ dna, Dna |
| Regex | Regular expression patterns | `p\s*[<>=]\s*0\.\d+` |

### Regex Examples

| Purpose | Pattern |
|---------|---------|
| p-value Search | `p\s*[<>=]\s*0\.\d+` |
| Multiple Terms | `\b(COVID\|SARS-CoV-2)\b` |
| Figure References | `(?:Fig\|Figure)\s*\d+` |
| Year Pattern | `(19\|20)\d{2}` |

### Export Options

| Format | Description |
|--------|-------------|
| **.xlsx** (Excel) | DOI, filename, page, context, and matched text. Ideal for data analysis |
| **.docx** (Word) | Formatted document with highlighted keywords. Ideal for reports |

> 💡 **Tip:** Keyword search and PDF processing can run simultaneously. Track progress for both tasks from the bottom panel.

---

## 5. Output Structure

After processing, your PDF directory will be organized:

```
your_pdf_folder/
├── Named Article/           # DOI verified + Crossref title match
├── AI_Named_Content/        # Gemini AI metadata (no Crossref match)
├── Unnamed Article/         # No method succeeded
├── Categorized Article/     # Journal / Author / Year / Subject
├── backups/                 # Original file copies
└── exports/                 # Search export files (.xlsx, .docx)
```

| Folder | Confidence | Description |
|--------|------------|-------------|
| Named | High | DOI or Crossref validated |
| AI Named | Medium | Gemini AI extraction |
| Unnamed | Failed | Naming unsuccessful |
| Categorized | — | Metadata-based grouping |

---

## 6. API Reference

LitOrganizer queries multiple academic APIs to retrieve metadata.

| API | Purpose | Cost | Key Required |
|-----|---------|------|--------------|
| **Google Gemini** | AI-powered metadata extraction (DOI fallback) | Free | Yes |
| **Crossref** | Primary DOI metadata + title search validation | Free | No |
| **OpenAlex** | Scholarly works database, citations, concepts | Free | No |
| **Semantic Scholar** | AI-powered academic search engine | Free | Optional |
| **DataCite** | DOI registration and metadata for datasets | Free | No |
| **Europe PMC** | Biomedical and life sciences literature | Free | No |
| **Scopus** | Elsevier abstract and citation database | Institutional | Yes |
| **Unpaywall** | Open access availability checker | Free | Email |

All APIs can be configured from the **Settings** page.

---

<div align="center">

**[← Back to README](../README.md)**

</div>
