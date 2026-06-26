<p align="center">
  <h1 align="center">Schools2AI — Educational Content Pipeline</h1>
  <p align="center">
    <em>Automated textbook processing, AI-powered study notes generation, and scalable content delivery for CBSE Classes 6–12.</em>
  </p>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white">
  <img alt="ChromaDB" src="https://img.shields.io/badge/ChromaDB-0.5+-FFD700?logo=data:image/png;base64,&logoColor=black">
  <img alt="AWS Bedrock" src="https://img.shields.io/badge/AWS_Bedrock-DeepSeek_v3.2-FF9900?logo=amazonaws&logoColor=white">
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-Hostinger-4479A1?logo=mysql&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-Proprietary-red">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [System 1 — Exam Notes Generator (RAG Pipeline)](#system-1--exam-notes-generator-rag-pipeline)
- [System 2 — Full Notes Generator & Upload Pipeline](#system-2--full-notes-generator--upload-pipeline)
- [System 3 — Textbook Downloader](#system-3--textbook-downloader)
- [System 4 — Database Sync & Upload](#system-4--database-sync--upload)
- [System 5 — Monitoring Dashboard](#system-5--monitoring-dashboard)
- [System 6 — Puter Bridge (Free LLM Proxy)](#system-6--puter-bridge-free-llm-proxy)
- [Content Coverage Matrix](#content-coverage-matrix)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Batch Processing Scripts](#batch-processing-scripts)
- [Contributing](#contributing)

---

## Overview

**Schools2AI** is a production-grade content automation pipeline that transforms raw educational PDFs (NCERT textbooks, coaching notes, previous year question papers) into structured, exam-oriented revision notes. The system processes content across **two mediums** (English and Hindi), **seven class levels** (6th through 12th), and **three academic streams** (Science, Commerce, Humanities) — covering approximately **500+ chapters** in total.

### What It Does

1. **Downloads** official NCERT textbooks and supplementary notes from Internet Archive, NCERT's website, and fallback scraping sources.
2. **Extracts** text from PDFs using PyMuPDF (handles OCR-resistant documents and corrupted pages gracefully).
3. **Chunks & embeds** text into a ChromaDB vector store using `sentence-transformers/all-MiniLM-L6-v2`.
4. **Generates** comprehensive exam-oriented notes using a multi-provider LLM backend (AWS Bedrock DeepSeek v3.2, Groq Llama 3.3 70B, or local Ollama).
5. **Exports** notes as professional Unicode PDFs with Devanagari font support.
6. **Uploads** generated notes to a Hostinger-hosted MySQL database via direct SQL or REST API, mapped to subjects, chapters, and medium.

### Key Technical Highlights

- **Multi-provider LLM failover**: Bedrock → Groq → Ollama (local), selected automatically.
- **Concurrent generation**: ThreadPoolExecutor with configurable worker count for parallel chapter processing.
- **JSON cache layer**: All generated notes are cached as `rag_cache_Class_*.json` files, enabling resume-on-failure and incremental generation.
- **Hindi/Devanagari-first design**: Full Unicode PDF rendering pipeline with NotoSansDevanagari font fallback chain.
- **English subject intelligence**: Automatic classification of English chapters into Prose, Poem, and Supplementary categories using a curated mapping table.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Schools2AI Pipeline                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │  Textbook     │    │  PDF Extraction   │    │  RAG Vector      │  │
│  │  Downloader   │───▶│  (PyMuPDF/fitz)   │───▶│  Store (Chroma)  │  │
│  │              │    │                   │    │                   │  │
│  │ Internet     │    │ • Page-level OCR  │    │ • MiniLM-L6-v2   │  │
│  │ Archive +    │    │ • Unicode norm    │    │ • Cosine HNSW     │  │
│  │ NCERT Direct │    │ • Corrupt skip    │    │ • Subject filter  │  │
│  └──────────────┘    └──────────────────┘    └────────┬──────────┘  │
│                                                        │             │
│                           ┌────────────────────────────┘             │
│                           ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │              LLM Notes Generation Engine                  │       │
│  │                                                           │       │
│  │  Priority: AWS Bedrock (DeepSeek v3.2 671B)              │       │
│  │         → Groq Cloud (Llama 3.3 70B)                     │       │
│  │         → Local Ollama (Qwen 2.5 7B)                     │       │
│  │                                                           │       │
│  │  Features:                                                │       │
│  │  • Structured 5-section markdown output                   │       │
│  │  • Hindi-medium heading enforcement + retry               │       │
│  │  • LaTeX → Unicode symbol conversion                      │       │
│  │  • PYQ-aware retrieval weighting                          │       │
│  └──────────────────────┬───────────────────────────────────┘       │
│                          │                                           │
│              ┌───────────┴───────────┐                               │
│              ▼                       ▼                               │
│  ┌──────────────────┐   ┌──────────────────────┐                    │
│  │  PDF Export       │   │  JSON Cache Files     │                   │
│  │  (fpdf2 + Noto)   │   │  rag_cache_Class_*    │                   │
│  │                   │   │  .json                │                   │
│  └──────────────────┘   └──────────┬─────────────┘                  │
│                                     │                                │
│                                     ▼                                │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │            Database Upload Layer                          │       │
│  │                                                           │       │
│  │  • sync_to_db.py  → ai_notes table (legacy)              │       │
│  │  • upload_hindi_11_12.py → ai_notes_new table             │       │
│  │  • http_uploader_6to9.py → REST API + PDF attachment      │       │
│  │  • selenium_uploader.py → Browser-automated bulk upload   │       │
│  │  • migrate_11_12_notes.py → Cross-table migration         │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                     │                                │
│                                     ▼                                │
│                     ┌──────────────────────────┐                     │
│                     │  Hostinger MySQL          │                     │
│                     │  u826463665_student       │                     │
│                     │                           │                     │
│                     │  Tables:                  │                     │
│                     │  • ai_notes (legacy)      │                     │
│                     │  • ai_notes_new (active)  │                     │
│                     │  • subjects               │                     │
│                     │  • chapters               │                     │
│                     └──────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## System 1 — Exam Notes Generator (RAG Pipeline)

> **Location**: `exam_notes_generator/`

The core RAG (Retrieval-Augmented Generation) system. This is the primary production pipeline.

### Core Modules (`exam_notes_generator/core/`)

| Module | Purpose |
|---|---|
| `config.py` | Central `AppConfig` dataclass with all paths, model names, chunk sizes, and generation defaults. Auto-creates required directories on import. |
| `generator.py` | Orchestrates the full generation flow: semantic retrieval → context packing → LLM generation → LaTeX stripping → heading enforcement. Contains the `strip_latex()` function that converts LaTeX macros to Unicode symbols (e.g., `\alpha` → `α`). |
| `llm_client.py` | Multi-provider LLM client with automatic failover. Priority: Bedrock → Groq → Ollama. Supports comma-separated API key rotation for rate-limit balancing. |
| `pdf_loader.py` | PDF text extraction engine using PyMuPDF (`fitz`). Defines the `ExtractedPage` dataclass. Detects PYQ (Previous Year Questions) files by filename keywords. Infers subject and unit from folder hierarchy. |
| `pdf_exporter.py` | Renders markdown notes to A4 PDF with full Unicode support. Uses Arial as primary font with NotoSansDevanagari as fallback for Hindi content. Handles `#`, `##`, `###`, bullets, and body text with distinct styling. |
| `prompts.py` | Contains the system prompt, Hindi-medium rules, and two prompt builders (`get_user_prompt` for simple use, `build_user_prompt` for the batch pipeline). Enforces the 5-section output format. |
| `rag_store.py` | ChromaDB vector store management. `LocalEmbeddingFunction` wraps sentence-transformers. Handles chunking via LangChain's `RecursiveCharacterTextSplitter`, batch upserts (256 per batch), and filtered semantic retrieval by subject/unit. |
| `text_utils.py` | Text normalization utilities: NFKC Unicode normalization, whitespace collapse, safe filename generation, and rough token estimation. |
| `logger.py` | Rotating file logger (2MB max, 5 backups) with concurrent console output. |

### Entry Points

| Script | Description |
|---|---|
| `app.py` | **Streamlit web UI**. Two tabs: (1) Ingest PDFs (upload or folder scan) → chunk → embed into ChromaDB. (2) Generate Notes with mode selection (Full Exam Notes, Quick Revision, Long Answer, Cheat Sheet, Question Bank). |
| `rag_batch_generate.py` | **CLI batch generator**. Processes entire class directories automatically. Collects chapters from filesystem, indexes into ChromaDB, generates notes via LLM, caches to JSON, and compiles a combined PDF per class+medium. Supports multi-threaded generation. |

### Fonts

The `core/` directory ships two embedded font files:
- `NotoSansDevanagari-Regular.ttf` — For Hindi body text rendering
- `NotoSansDevanagari-Bold.ttf` — For Hindi heading rendering

---

## System 2 — Full Notes Generator & Upload Pipeline

> **Location**: Root-level scripts

### `generate_exam_pdfs.py`

The **original** notes generation system (pre-RAG). Uses direct OpenAI GPT-4o-mini or the shared `llm_client` to process PDF/DOCX content and generate structured exam notes. Supports English and Hindi medium for Classes 6–8 and 11–12.

Key differences from the RAG pipeline:
- Extracts text directly from PDFs/DOCX without vector indexing
- Uses OpenAI client directly (before the multi-provider system was built)
- Outputs per-class combined PDFs to `Generated_Exam_PDFs/`

### Upload Scripts

| Script | Target | Method | Coverage |
|---|---|---|---|
| `sync_to_db.py` | `ai_notes` table | Direct MySQL upsert | Classes 6–9, all mediums |
| `upload_hindi_11_12.py` | `ai_notes_new` table | Direct MySQL insert/update | Classes 11–12, Hindi medium |
| `http_uploader_6to9.py` | REST API (`app-api.schools2ai.com`) | HTTP POST with PDF attachments | Classes 6–9, both mediums |
| `selenium_uploader.py` | Bulk upload page (`ainotes.schools2ai.com`) | Browser automation (Selenium + ChromeDriver) | Classes 11–12, Hindi medium |
| `selenium_uploader_6to9.py` | Bulk upload page | Browser automation | Classes 6–9 |
| `selenium_uploader_math.py` | Bulk upload page | Browser automation (Math-specific) | Math subjects |
| `migrate_11_12_notes.py` | `ai_notes_new` table | Cross-table migration with subject normalization | Classes 11–12, both mediums |

---

## System 3 — Textbook Downloader

> **Location**: `download_textbooks.py`

An automated NCERT textbook acquisition system covering **43+ textbooks** across Classes 6–9 in both English and Hindi medium.

### Download Source Priority

1. **Internet Archive** — Queries the IA metadata API to find the largest PDF in an item.
2. **NCERT Direct** — Downloads from `ncert.nic.in/textbook/pdf/{code}ps.pdf`.
3. **Scrape** — Parses educational websites (Vedantu, BYJU'S) for embedded PDF links.
4. **Direct URL** — User-confirmed static download URLs.

### Features

- Automatic retry with exponential backoff (3 attempts per source)
- PDF validation: checks file size (>10KB) and PDF magic bytes (`%PDF-`)
- Skip-if-exists logic to support incremental downloads
- Comprehensive log file generation with per-book status tracking
- Hindi medium folder mapping (e.g., `Maths_Hindi` → `गणित (Maths)`)

### Supplementary Download Scripts

| Script | Purpose |
|---|---|
| `download_chapters_final.py` | Chapter-level PDF download with more granular control |
| `download_fallback_class9.py` | Fallback download logic specific to Class 9 |
| `auto_start_class9.py` | Automated startup script for Class 9 processing |

---

## System 4 — Database Sync & Upload

> **Location**: Root-level scripts + `db_upload_repo/`

### `sync_to_db.py` (Root)

The primary database synchronization script. Reads from `rag_cache_Class_*.json` cache files and upserts into the `ai_notes` table.

**Key logic:**
1. Parses class, stream, and language from the cache filename (e.g., `rag_cache_Class_11th_Science_Hindi.json`)
2. Splits the cache key (`subject||subcategory||topic`) to extract metadata
3. Cleans topic names by stripping "Chapter 1:", "Ch. 2 -" prefixes
4. Uses `english_mapper.py` to reclassify English chapters into Prose/Poem/Supplementary
5. Performs upsert: UPDATE if row exists, INSERT if new

### `english_mapper.py`

A curated classification table for English subject chapters across Classes 6–8. Maps chapter names (by fuzzy matching) to their category:

- **Prose**: "Who Did Patrick's Homework", "The Tsunami", etc.
- **Poem**: "A House, A Home", "The Kite", etc.
- **Supplementary**: "A Tale of Two Birds", "The Selfish Giant", etc.

### `db_upload_repo/`

A standalone Git repository containing sanitized versions of the sync scripts for deployment. Contains its own README, `.env` configuration, and three scripts: `sync_to_db.py`, `upload_to_db.py` (insert-only), and `update_db_notes.py` (update-only).

---

## System 5 — Monitoring Dashboard

> **Location**: `monitor_dashboard.py`

A **Streamlit-based real-time monitoring dashboard** (955 lines) that tracks the progress of batch note generation. Features:

- Live progress bars per class/medium showing chapters completed vs total
- Cache file analysis with per-subject breakdown
- System resource monitoring via `psutil` (CPU, RAM)
- Log file tailing from `batch_generation.log`
- Batch process launcher with configurable parameters

### Native Monitor (`monitor.cpp` / `monitor.exe`)

A compiled C++ Windows console application that provides a lightweight, zero-dependency alternative to the Streamlit dashboard. Uses the Windows API for CPU monitoring and `nlohmann/json` for parsing cache files. Displays ANSI-colored terminal output with real-time progress tracking.

---

## System 6 — Puter Bridge (Free LLM Proxy)

> **Location**: `puter_bridge/`

A Node.js Express server that proxies OpenAI-compatible API calls to the Puter.js free AI API. This enables using `gpt-5.4-nano` at zero cost during development/testing.

**Endpoint**: `POST http://localhost:3141/v1/chat/completions`

The Python `OpenAI` client connects to this local endpoint with `api_key="ollama"`, making it a drop-in replacement for any OpenAI-compatible backend.

---

## Content Coverage Matrix

| Class | English Medium | Hindi Medium | Streams |
|---|---|---|---|
| 6th | ✅ All subjects | ✅ All subjects | — |
| 7th | ✅ All subjects | ✅ All subjects | — |
| 8th | ✅ All subjects | ✅ All subjects | — |
| 9th | ✅ All subjects | ✅ All subjects | — |
| 10th | — | ✅ Partial | — |
| 11th | ✅ Science, Commerce | ✅ Science, Commerce, Humanities | Science, Commerce, Humanities |
| 12th | ✅ Science, Commerce | ✅ Science, Commerce, Humanities | Science, Commerce, Humanities |

**Subjects covered**: English (Prose/Poem/Supplementary), Hindi, Mathematics, Science, Social Science (History/Geography/Civics/Economics), Sanskrit, Physics, Chemistry, Biology, Accountancy, Business Studies, Economics, Political Science, Sociology, Home Science, Physical Education.

---

## Database Schema

### `ai_notes` (Legacy Table)

```sql
CREATE TABLE ai_notes (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    language     VARCHAR(10),        -- 'English' or 'Hindi'
    board        VARCHAR(20),        -- 'CBSE'
    class        VARCHAR(5),         -- '6', '7', ..., '12'
    subject      VARCHAR(100),       -- 'Physics', 'English (Prose)', etc.
    topic        VARCHAR(255),       -- Chapter/topic name
    short_notes  LONGTEXT,           -- Markdown-formatted notes
    full_notes   TEXT,               -- Full notes URL or content
    book_url     TEXT,               -- S3/CDN URL to original book PDF
    generated_by VARCHAR(20),        -- 'AI'
    stream       VARCHAR(30),        -- 'Science', 'Commerce', 'Humanities', NULL
    created_at   DATETIME,
    updated_at   DATETIME
);
```

### `ai_notes_new` (Active Table)

```sql
CREATE TABLE ai_notes_new (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    language     VARCHAR(10),
    board        VARCHAR(20),
    stream       VARCHAR(30),
    class        VARCHAR(5),
    subject      VARCHAR(100),
    topic        VARCHAR(255),
    short_notes  LONGTEXT,
    full_notes   VARCHAR(255),       -- Structured JSON or URL
    created_by   VARCHAR(20),
    created_at   DATETIME,
    updated_at   DATETIME
);
```

### Related Tables

- **`subjects`** — Subject registry with `id`, `class`, `subject_name`, `stream`, `medium`
- **`chapters`** — Chapter-to-subject mapping with `id`, `subject_id`, `chapter_name`, `chapter_number`

---

## Project Structure

```
Schools2AI/
│
├── exam_notes_generator/          # System 1: Core RAG pipeline
│   ├── core/                      # Core Python package
│   │   ├── __init__.py
│   │   ├── config.py              # AppConfig dataclass
│   │   ├── generator.py           # Notes generation orchestrator
│   │   ├── llm_client.py          # Multi-provider LLM client
│   │   ├── pdf_exporter.py        # Markdown → PDF renderer
│   │   ├── pdf_loader.py          # PDF text extraction
│   │   ├── prompts.py             # System/user prompt templates
│   │   ├── rag_store.py           # ChromaDB vector store
│   │   ├── text_utils.py          # Text normalization utilities
│   │   ├── logger.py              # Rotating file logger
│   │   ├── NotoSansDevanagari-Regular.ttf
│   │   └── NotoSansDevanagari-Bold.ttf
│   ├── app.py                     # Streamlit web UI
│   ├── rag_batch_generate.py      # CLI batch generator
│   ├── proxima_prompt.json        # Reference prompt template
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment template
│   └── data/                      # ChromaDB + uploads (gitignored)
│
├── db_upload_repo/                # System 4: Standalone DB sync (Git repo)
│   ├── sync_to_db.py
│   ├── upload_to_db.py
│   ├── update_db_notes.py
│   └── README.md
│
├── puter_bridge/                  # System 6: Free LLM proxy
│   ├── server.js
│   └── package.json
│
├── English/                       # English medium PDFs (6th–12th)
│   ├── 6th class/
│   ├── 7th class/
│   ├── 8th class/
│   ├── Class 9th/
│   └── 11th & 12th/
│
├── Hindi/                         # Hindi medium PDFs (6th–9th)
│   ├── Class 6th/
│   ├── Class 7th/
│   ├── Class 8th/
│   └── 9th Class/
│
├── Generated_Exam_PDFs/           # Output: Combined exam notes PDFs
├── Textbooks/                     # Downloaded NCERT textbooks
│
├── rag_cache_Class_*.json         # Generated notes cache files
│
├── .env                           # Environment variables (DB + Bedrock)
├── sync_to_db.py                  # DB sync with English mapping
├── english_mapper.py              # English chapter classifier
├── download_textbooks.py          # NCERT textbook downloader
├── generate_exam_pdfs.py          # Legacy notes generator
├── upload_hindi_11_12.py          # Hindi 11/12 uploader
├── http_uploader_6to9.py          # REST API uploader
├── selenium_uploader.py           # Browser-based uploader
├── monitor_dashboard.py           # Streamlit monitoring UI
├── monitor.cpp                    # Native C++ monitoring tool
├── migrate_11_12_notes.py         # Cross-table migration script
│
├── run_bedrock_6to9.bat           # Batch: Bedrock 6-9 English
├── run_rag_batch_class_11_12_hindi.bat  # Batch: Ollama 11-12 Hindi
├── run_rag_batch_class_12th.bat         # Batch: Class 12 English
└── run_all_exam_pdfs_ollama.bat         # Batch: All classes Ollama
```

---

## Setup & Installation

### Prerequisites

- **Python 3.13+** (Windows)
- **MySQL 8.0+** (Hostinger remote or local)
- **Node.js 18+** (only for Puter Bridge)
- **Ollama** (optional, for local LLM inference)

### Step 1: Clone and Install Dependencies

```powershell
cd "C:\Users\bhask\Desktop\Archive\New folder"

# Create virtual environment
cd exam_notes_generator
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# Additional root-level dependencies
pip install mysql-connector-python python-dotenv requests selenium webdriver-manager psutil PyPDF2 python-docx
```

### Step 2: Configure Environment

```powershell
# Copy and edit the environment file
Copy-Item .env.example .env
notepad .env
```

Required variables in `.env`:

```env
# Database (Hostinger MySQL)
DB_HOST=auth-db1645.hstgr.io
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=u826463665_student

# LLM Provider (choose one)
BEDROCK_API_KEY=your_bedrock_key
BEDROCK_REGION=us-east-1
BEDROCK_MODEL=deepseek.v3.2

# OR Groq
GROQ_API_KEY=your_groq_key

# OR Ollama (default fallback)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen2.5:7b
```

### Step 3: Install Ollama (Optional)

```powershell
# Download from https://ollama.com/download
ollama pull qwen2.5:7b

# Enable GPU acceleration
$env:OLLAMA_FLASH_ATTENTION="1"
ollama serve
```

### Step 4: Puter Bridge (Optional)

```powershell
cd puter_bridge
npm install
node server.js
# Runs at http://localhost:3141/v1
```

---

## Configuration

### LLM Provider Selection

The system automatically selects the best available provider:

| Priority | Provider | Model | Cost | Speed |
|---|---|---|---|---|
| 1st | AWS Bedrock | DeepSeek v3.2 (671B) | ~$0.002/1K tokens | Fast (cloud) |
| 2nd | Groq Cloud | Llama 3.3 70B | Free tier available | Very fast |
| 3rd | Local Ollama | Qwen 2.5 7B (Q4) | Free | Depends on GPU |

### Batch Generation Parameters

| Parameter | Default | Description |
|---|---|---|
| `--classes` | `6th 7th 8th` | Space-separated class identifiers |
| `--mediums` | `English Hindi` | `English`, `Hindi`, or both |
| `--mode` | `Quick Revision` | Generation mode |
| `--top-k` | `8` | Number of chunks to retrieve |
| `--max-tokens` | `2000` | Max LLM output tokens |
| `--context-length` | `8192` | LLM context window |
| `--temperature` | `0.2` | LLM sampling temperature |
| `--chunk-size` | `1100` | Text chunk size (characters) |
| `--chunk-overlap` | `160` | Overlap between chunks |
| `--workers` | `2` | Parallel generation threads |
| `--pause` | `0.1` | Delay between API calls (seconds) |
| `--reindex` | `false` | Force re-index ChromaDB |

---

## Usage Guide

### Interactive Mode (Streamlit)

```powershell
cd exam_notes_generator
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

1. Open `http://localhost:8501`
2. **Ingest PDFs** tab → Upload files or scan a local folder
3. **Generate Notes** tab → Select subject, chapter, and mode → Generate

### Batch Mode (CLI)

```powershell
# Generate English notes for Classes 6-9 using Bedrock
python exam_notes_generator\rag_batch_generate.py ^
    --classes 6th 7th 8th 9th ^
    --mediums English ^
    --workers 8 ^
    --max-tokens 4000

# Generate Hindi notes for Classes 11-12 using Ollama
python exam_notes_generator\rag_batch_generate.py ^
    --classes 11th_Science 11th_Commerce 12th_Science 12th_Commerce ^
    --mediums Hindi ^
    --workers 1 ^
    --context-length 16384
```

### Database Sync

```powershell
# Sync all cache files to the database
python sync_to_db.py

# Upload Hindi 11/12 to ai_notes_new
python upload_hindi_11_12.py

# Upload via REST API with PDF attachments
python http_uploader_6to9.py
```

### Download Textbooks

```powershell
python download_textbooks.py
# Outputs to: Textbooks/Class {6-9}/{Subject}/
# Log file: textbook_download_log.txt
```

---

## Batch Processing Scripts

Pre-configured `.bat` files for one-click execution:

| Script | What It Does |
|---|---|
| `run_bedrock_6to9.bat` | Classes 6–9, English medium, 8 workers, Bedrock DeepSeek v3.2 |
| `run_rag_batch_class_11_12_hindi.bat` | Classes 11–12, Hindi medium, Ollama, all 3 streams |
| `run_rag_batch_class_12th.bat` | Class 12 only, English medium |
| `run_rag_batch_exam_pdfs.bat` | Full exam PDF generation run |
| `run_all_exam_pdfs_ollama.bat` | All classes via local Ollama |
| `run_all_exam_pdfs_groq.bat` | All classes via Groq Cloud |

---

## Contributing

### Development Workflow

1. Source PDFs go into `English/` or `Hindi/` organized by class and subject.
2. Run the batch generator to produce `rag_cache_Class_*.json` files.
3. Review generated notes in the cache files.
4. Run `sync_to_db.py` or the appropriate uploader to push to production.
5. Monitor progress via `monitor_dashboard.py` or `monitor.exe`.

### Code Style

- Python 3.13 with `from __future__ import annotations`
- Type hints throughout
- `pathlib.Path` for all file operations
- `python-dotenv` for configuration
- UTF-8 encoding enforced on Windows via `sys.stdout.reconfigure()`

### Adding a New Class/Subject

1. Add PDF content to the appropriate `English/` or `Hindi/` directory
2. Add the path mapping in `rag_batch_generate.py` under `ENGLISH_MEDIUM` or `HINDI_MEDIUM`
3. If English subject, update `english_mapper.py` with the chapter classification
4. Run the batch generator with the new class identifier
5. Sync to database

---

<p align="center">
  <strong>Built for Schools2AI</strong> — Making quality education accessible through AI.
</p>
