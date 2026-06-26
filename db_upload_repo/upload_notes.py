"""
Full uploader for Class 11 Hindi Medium notes to ainotes.schools2ai.com

API Spec:
- POST https://app-api.schools2ai.com/api/ainote/create
- multipart/form-data
- Fields: language, board, class, subject, stream, createdBy
- chapters (JSON string[]), shortNotes (JSON string[])
- Files: "notes" (Full Notes PDF), "books" (Book PDF)
"""

import httpx
import json
import os
import re
import time
import sys
import traceback

# ========== CONFIGURATION ==========
API_URL = "https://app-api.schools2ai.com/api/ainote/create"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://ainotes.schools2ai.com",
    "Referer": "https://ainotes.schools2ai.com/"
}

BASE_DIR = r"c:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th"
NOTES_DIR = os.path.join(BASE_DIR, "11th &12th")
TEXTBOOK_DIR = os.path.join(BASE_DIR, "class 11 and 12 text book")
RAG_CACHE_DIR = r"C:\Users\bhask\Desktop\rag_chache_files_class 11&12th"

# Fixed form values
LANGUAGE = "Hindi"
BOARD = "CBSE"
CREATED_BY = "AI"

# ========== RAG CACHE KEY FORMAT ==========
# Keys look like: "भौतिकी (Physics)||1. मात्रक और मापन"
# Or multi-level: "इंग्लिश (English)||1. Passage||Discursive Passage"
# We need to map: Subject -> list of (chapter_name, short_notes_content)

def load_rag_cache(rag_file):
    """Load RAG cache and organize by subject"""
    with open(rag_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    subjects = {}
    for key, value in data.items():
        parts = key.split("||")
        subject = parts[0]
        # Use only the last part as the topic name (skip folder names like _main, Outdated Chapters, etc.)
        chapter_name = parts[-1]
        # Strip leading chapter numbers like "1. ", "14. ", "1 " etc.
        chapter_name = re.sub(r'^\d+\.?\s*', '', chapter_name).strip()
        
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append({
            "chapter_name": chapter_name,
            "short_notes": value,
            "rag_key": key
        })
    
    return subjects

def find_notes_pdf(notes_base, class_num, stream, subject, chapter_name):
    """Find the notes PDF file for a given chapter.
    
    Notes structure: 11th &12th/Class {class}th {stream}/{subject}/[sub-subject/]{chapter_name}.pdf
    """
    class_dir = f"Class {class_num}th {stream}"
    subject_dir = os.path.join(notes_base, class_dir, subject)
    
    if not os.path.isdir(subject_dir):
        return None
    
    # Direct match: look for {chapter_name}.pdf in subject dir and subdirs
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf'):
                name = f[:-4]  # Remove .pdf
                if name == chapter_name:
                    return os.path.join(root, f)
    
    # Partial match: chapter_name might be from RAG key like "3. Long Composition / Articles"
    # Try matching the last part
    last_part = chapter_name.split(" / ")[-1] if " / " in chapter_name else chapter_name
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf'):
                name = f[:-4]
                if name == last_part or last_part in name:
                    return os.path.join(root, f)
    
    return None

def find_textbook_pdf(textbook_base, class_num, stream, subject, chapter_name):
    """Find the textbook PDF for a given chapter.
    
    Textbook structure: class 11 and 12 text book/Class {class}th {stream}/{subject}/[sub-dirs/]{chapter_name}.pdf
    """
    class_dir = f"Class {class_num}th {stream}"
    subject_dir = os.path.join(textbook_base, class_dir, subject)
    
    if not os.path.isdir(subject_dir):
        return None
    
    # Direct match
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf'):
                name = f[:-4]
                if name == chapter_name:
                    return os.path.join(root, f)
    
    # Partial match on last part
    last_part = chapter_name.split(" / ")[-1] if " / " in chapter_name else chapter_name
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf'):
                name = f[:-4]
                if name == last_part or last_part in name:
                    return os.path.join(root, f)
    
    return None

def upload_subject(class_num, stream, subject, chapters, dry_run=False):
    """Upload all chapters for a subject in a single API call."""
    
    chapter_names = []
    short_notes_list = []
    notes_files = []
    book_files = []
    
    for ch in chapters:
        chapter_name = ch["chapter_name"]
        chapter_names.append(chapter_name)
        short_notes_list.append(ch.get("short_notes", ""))
        
        # Find notes PDF
        notes_pdf = find_notes_pdf(NOTES_DIR, class_num, stream, subject, chapter_name)
        if notes_pdf:
            notes_files.append(("notes", (os.path.basename(notes_pdf), open(notes_pdf, 'rb'), "application/pdf")))
        else:
            # Send empty placeholder so indexing stays aligned
            notes_files.append(("notes", ("empty.pdf", b"", "application/pdf")))
        
        # Find textbook PDF
        book_pdf = find_textbook_pdf(TEXTBOOK_DIR, class_num, stream, subject, chapter_name)
        if book_pdf:
            book_files.append(("books", (os.path.basename(book_pdf), open(book_pdf, 'rb'), "application/pdf")))
        else:
            book_files.append(("books", ("empty.pdf", b"", "application/pdf")))
    
    data = {
        "language": LANGUAGE,
        "board": BOARD,
        "class": str(class_num),
        "subject": subject,
        "stream": stream,
        "createdBy": CREATED_BY,
        "chapters": json.dumps(chapter_names, ensure_ascii=False),
        "short_notes": json.dumps(short_notes_list, ensure_ascii=False),
    }
    
    files = notes_files + book_files
    
    print(f"\n{'='*60}")
    print(f"Uploading: Class {class_num} | {stream} | {subject}")
    print(f"Chapters: {len(chapter_names)}")
    for i, cn in enumerate(chapter_names):
        n_pdf = "✓" if notes_files[i][1][1] != b"" else "✗"
        b_pdf = "✓" if book_files[i][1][1] != b"" else "✗"
        print(f"  {i+1}. {cn} [Notes:{n_pdf}] [Book:{b_pdf}]")
    
    if dry_run:
        print("  [DRY RUN - not uploading]")
        # Close any opened files
        for _, (_, f, _) in notes_files + book_files:
            if hasattr(f, 'close'):
                f.close()
        return True
    
    try:
        with httpx.Client(verify=False, timeout=120) as client:
            resp = client.post(API_URL, data=data, files=files, headers=HEADERS)
            result = resp.json()
            
            if result.get("success"):
                print(f"  ✓ SUCCESS! Uploaded {len(result.get('results', []))} chapters")
                for r in result.get("results", []):
                    nk = "✓" if r.get("noteKey") else "✗"
                    bk = "✓" if r.get("bookKey") else "✗"
                    print(f"    ID:{r.get('id')} | {r.get('topic')} | Notes:{nk} Book:{bk}")
                return True
            else:
                print(f"  ✗ FAILED: {result.get('message', 'Unknown error')}")
                return False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        traceback.print_exc()
        return False
    finally:
        # Close opened files
        for _, (_, f, _) in notes_files + book_files:
            if hasattr(f, 'close'):
                f.close()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry"
    
    # Map stream names to RAG cache files for Class 11
    rag_files = {
        "Science": os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Science_Hindi.json"),
        "Commerce": os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Commerce_Hindi.json"),
        "Humanities": os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Humanities_Hindi.json"),
    }
    
    total_subjects = 0
    total_chapters = 0
    total_success = 0
    
    for stream, rag_file in rag_files.items():
        if not os.path.exists(rag_file):
            print(f"Skipping {stream}: RAG cache not found")
            continue
        
        subjects = load_rag_cache(rag_file)
        print(f"\n{'#'*60}")
        print(f"# Stream: {stream} ({len(subjects)} subjects)")
        print(f"{'#'*60}")
        
        for subject, chapters in sorted(subjects.items()):
            total_subjects += 1
            total_chapters += len(chapters)
            
            success = upload_subject(
                class_num=11,
                stream=stream,
                subject=subject,
                chapters=chapters,
                dry_run=(mode == "dry")
            )
            
            if success:
                total_success += 1
            
            if mode != "dry":
                time.sleep(2)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {total_success}/{total_subjects} subjects uploaded | {total_chapters} total chapters")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
