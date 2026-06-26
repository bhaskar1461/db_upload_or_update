# Local AI Exam Notes Generator

This is a fully local/offline Streamlit app for generating exam-oriented notes from many PDFs using:

- Ollama with `qwen2.5:7b`
- OpenAI-compatible Ollama endpoint at `http://localhost:11434/v1`
- LangChain text chunking
- `sentence-transformers/all-MiniLM-L6-v2` embeddings
- ChromaDB persistent vector storage
- PyMuPDF PDF parsing
- fpdf2 Unicode PDF export

Generated PDFs are saved automatically into:

```text
Generated_Exam_PDFs/
```

## Project Structure

```text
exam_notes_generator/
  app.py
  requirements.txt
  .env.example
  README.md
  core/
    config.py
    generator.py
    logger.py
    ollama_client.py
    pdf_exporter.py
    pdf_loader.py
    prompts.py
    rag_store.py
    text_utils.py
  data/
    chroma_db/
    uploads/
  logs/
Generated_Exam_PDFs/
```

## Windows Setup

Open PowerShell in this folder:

```powershell
cd "C:\Users\bhask\Desktop\New folder\exam_notes_generator"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the Windows `py` launcher fails, use the direct Python install that is present on this machine:

```powershell
& "C:\Users\bhask\AppData\Local\Programs\Python\Python313\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Ollama from:

```text
https://ollama.com/download
```

Then pull the local model:

```powershell
ollama pull qwen2.5:7b
```

For RTX 3060 laptop GPUs, Ollama automatically uses GPU layers when the NVIDIA driver/CUDA runtime is available. Use a Q4 model to keep VRAM usage low:

```powershell
ollama run qwen2.5:7b
```

Optional environment variables:

```powershell
Copy-Item .env.example .env
notepad .env
```

## Enable Ollama Performance Options

Before launching Ollama, you can set:

```powershell
$env:OLLAMA_FLASH_ATTENTION="1"
$env:OLLAMA_CONTEXT_LENGTH="8192"
ollama serve
```

If Ollama is already running from the tray app, restart it after changing environment variables.

## Run The App

```powershell
cd "C:\Users\bhask\Desktop\New folder\exam_notes_generator"
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Open the URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## How To Use

1. Start Ollama and ensure `qwen2.5:7b` is installed.
2. Open the Streamlit app.
3. Go to **Ingest PDFs**.
4. Upload PDFs or enter a local folder path to scan recursively.
5. Click **Index**. The app extracts pages, chunks text, embeds chunks, and stores them in ChromaDB.
6. Go to **Generate Notes**.
7. Enter subject and unit/topic.
8. Choose a mode: full notes, quick revision, long answer, cheat sheet, or question bank.
9. Generate notes. A clean PDF is saved into `Generated_Exam_PDFs/`.

## Notes Format

The generated output follows:

```text
# Subject Name

## Unit Name

### 1. Chapter Overview
### 2. Key Concepts
### 3. Important Formulas
### 4. Problem Solving Methods
### 5. Important Questions
### 6. PYQ Focus
### 7. Common Mistakes
### 8. Quick Revision Sheet
### 9. Viva Questions
```

## Offline Behavior

The app runs offline after dependencies, model weights, and embedding model files are installed. The first run of `sentence-transformers` may download `all-MiniLM-L6-v2`. To make a machine fully offline, run the app once with internet access, then keep the Hugging Face cache.

## Large Collection Tips

- Use chunk size `1000-1400`, overlap `150-220`.
- Use top-k `8-15` for normal notes and `15-25` for broad units.
- Keep context at `8192` for 16 GB RAM unless you need wider retrieval.
- Index by subject to keep retrieval focused.
- Use `qwen2.5:7b` quantized through Ollama for low VRAM usage.

## Error Handling

- Corrupted PDFs are logged and skipped.
- Unreadable pages are skipped without stopping ingestion.
- Unicode output is normalized.
- PDF export uses Windows Unicode fonts when available.
- Logs are written to `exam_notes_generator/logs/app.log`.
