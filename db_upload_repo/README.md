# DB Upload & Update: AI Notes Management

This repository contains the automation scripts designed to bulk process and upload educational material (Notes PDFs, Textbook PDFs, and Short Notes) to the `schools2ai` backend API. The scripts process the data in batches to ensure seamless handling and align files across different data sources.

## Overview of the Process

The end goal of the process was to perfectly align structured Short Notes (which were stored in JSON RAG cache files) with their corresponding full Notes PDFs, and then fetch, extract, match, and upload the official NCERT textbook PDFs to the platform backend.

Here is the step-by-step breakdown of how the whole process was accomplished:

### 1. Downloading Official NCERT Textbooks
The first challenge was fetching the official Class 11 and 12 textbook PDFs from the NCERT website.
- **Script:** `download_books.py`
- **What it did:** It navigated the NCERT directory structure (scraping subjects and their underlying chapters), downloaded the zip files containing the PDFs for each textbook in Hindi medium, and saved them logically organized by subject.

### 2. Extracting and Renaming the Textbooks
The textbooks came in zip files containing PDFs with arbitrary names (like `kebo101.pdf`, `kebo102.pdf`, etc.). These names did not match the actual chapter topics from the notes.
- **Script:** `unzip_and_rename.py`
- **What it did:** It unzipped each textbook folder and analyzed the RAG cache JSON file (which held the true names of each chapter). It then systematically renamed each PDF in the sequence (Chapter 1, Chapter 2, etc.) to precisely match the clean topic names (e.g., `1. मात्रक और मापन.pdf`) used by the existing notes so that both sets of files could be easily paired.

### 3. API Reverse Engineering and Verification
We needed to upload the `Short Notes`, `Notes PDFs`, and `Book PDFs` simultaneously. 
- Using testing scripts, we interacted directly with the frontend to discover the backend API endpoint (`/api/ainote/create`).
- We systematically determined the expected `multipart/form-data` structure:
  - The API required array items to be sent as JSON-stringified payloads (`chapters` and `short_notes`).
  - By brute-forcing multiple field name variations, we pinpointed that the API specifically expected the exact key `short_notes` (with an underscore) rather than camelCase.

### 4. The Main Upload Process
Once everything was aligned, we proceeded with uploading the massive dataset.
- **Script:** `upload_notes.py`
- **What it did:** It looped through all 22 subjects across three streams (Science, Commerce, Humanities).
  - It cleaned up the chapter names by parsing the RAG keys (extracting just the topic name and stripping out any prefix numbers or folder names).
  - It matched the topic name against the Notes directory and the Textbook directory to find the corresponding PDFs.
  - It compiled the form data and submitted the payload to the backend API.
- **Result:** It successfully uploaded subjects with standard chapter lengths.

### 5. Handling Server Limitations (Batch Uploading)
During the main upload, subjects with a very large number of chapters (e.g., English, Biology, and Hindi, which had upwards of 21–37 chapters) failed with a `500 Internal Error`. This was because the total number of files in the payload exceeded the backend server's `max_file_uploads` limit (usually defaulting to 20 files in environments like PHP).
- **Script:** `upload_failed_subjects.py`
- **What it did:** It isolated the 7 failed subjects and implemented a batching logic. It split the chapters into groups of 15 (ensuring the payload never exceeded 30 files per request) and successfully pushed the remaining data chunk by chunk into the backend database.

## Included Scripts

- **`download_books.py`**: Fetches the textbook ZIP files directly from the NCERT platform.
- **`unzip_and_rename.py`**: Extracts the PDFs from the ZIP archives and mathematically renames them to match the corresponding chapter names found in the RAG cache JSON data.
- **`upload_notes.py`**: The primary uploading engine that packages the Notes PDFs, Book PDFs, and Short Notes into `multipart/form-data` and pushes them to the `schools2ai` API.
- **`upload_failed_subjects.py`**: An advanced iteration of the uploader designed to break large subjects (more than 20 chapters) into smaller batches to circumvent server-side payload size and file count limits.

## Dependencies

- Python 3.x
- `httpx` (for making multipart API requests)
- `requests` (for scraping/downloading)
- `beautifulsoup4` (for scraping NCERT structure)

## Usage

Ensure the folder structures match the expected constants defined at the top of the scripts (e.g., `BASE_DIR`, `NOTES_DIR`, `TEXTBOOK_DIR`, `RAG_CACHE_DIR`). Then execute the scripts sequentially.
