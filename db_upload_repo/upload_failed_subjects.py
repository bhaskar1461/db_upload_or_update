"""Upload the remaining subjects that failed due to file limits by batching them."""
import httpx
import json
import os
import re
import time
import sys

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

def load_rag_cache(rag_file):
    with open(rag_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    subjects = {}
    for key, value in data.items():
        parts = key.split("||")
        subject = parts[0]
        chapter_name = parts[-1]
        chapter_name = re.sub(r'^\d+\.?\s*', '', chapter_name).strip()
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append({
            "chapter_name": chapter_name,
            "short_notes": value,
            "rag_key": key
        })
    return subjects

def find_pdf(base_dir, class_num, stream, subject, topic):
    class_dir = f"Class {class_num}th {stream}"
    subject_dir = os.path.join(base_dir, class_dir, subject)
    if not os.path.isdir(subject_dir):
        return None
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf') and f[:-4] == topic:
                return os.path.join(root, f)
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf') and topic in f[:-4]:
                return os.path.join(root, f)
    return None

def upload_subject_batch(class_num, stream, subject, chapters):
    chapter_names = []
    short_notes_list = []
    notes_files = []
    book_files = []
    for ch in chapters:
        topic = ch["chapter_name"]
        chapter_names.append(topic)
        short_notes_list.append(ch.get("short_notes", ""))
        
        notes_pdf = find_pdf(NOTES_DIR, class_num, stream, subject, topic)
        if notes_pdf:
            notes_files.append(("notes", (os.path.basename(notes_pdf), open(notes_pdf, 'rb'), "application/pdf")))
        else:
            notes_files.append(("notes", ("empty.pdf", b"", "application/pdf")))
            
        book_pdf = find_pdf(TEXTBOOK_DIR, class_num, stream, subject, topic)
        if book_pdf:
            book_files.append(("books", (os.path.basename(book_pdf), open(book_pdf, 'rb'), "application/pdf")))
        else:
            book_files.append(("books", ("empty.pdf", b"", "application/pdf")))
            
    data = {
        "language": "Hindi",
        "board": "CBSE",
        "class": str(class_num),
        "subject": subject,
        "stream": stream,
        "createdBy": "AI",
        "chapters": json.dumps(chapter_names, ensure_ascii=False),
        "short_notes": json.dumps(short_notes_list, ensure_ascii=False),
    }
    
    files = notes_files + book_files
    try:
        with httpx.Client(verify=False, timeout=120) as client:
            resp = client.post(API_URL, data=data, files=files, headers=HEADERS)
            result = resp.json()
            if result.get("success"):
                print(f"    ✓ Batch success ({len(chapters)} chapters)")
                return True
            else:
                print(f"    ✗ Batch failed: {result.get('message')}")
                return False
    except Exception as e:
        print(f"    ✗ Batch error: {e}")
        return False
    finally:
        for _, (_, f, _) in notes_files + book_files:
            if hasattr(f, 'close'): f.close()

def main():
    rag_files = {
        "Science": os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Science_Hindi.json"),
        "Commerce": os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Commerce_Hindi.json"),
        "Humanities": os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Humanities_Hindi.json"),
    }
    
    # These subjects failed because they have >= 21 chapters, likely hitting a file limit (40+ files)
    failed_subjects = {
        "Science": ["इंग्लिश (English)", "जीव विज्ञान (Biology)", "हिन्दी (Hindi)"],
        "Commerce": ["इंग्लिश (English)", "हिन्दी (Hindi)"],
        "Humanities": ["इंग्लिश (English)", "हिन्दी (Hindi)"]
    }
    
    for stream, subjects_to_run in failed_subjects.items():
        rag_file = rag_files[stream]
        subjects = load_rag_cache(rag_file)
        
        for subject in subjects_to_run:
            if subject not in subjects:
                continue
                
            chapters = subjects[subject]
            print(f"\nUploading: {stream} | {subject} ({len(chapters)} total chapters)")
            
            # Batch into 15 chapters max per request
            batch_size = 15
            for i in range(0, len(chapters), batch_size):
                batch = chapters[i:i+batch_size]
                print(f"  -> Batch {i//batch_size + 1}: {len(batch)} chapters")
                upload_subject_batch(11, stream, subject, batch)
                time.sleep(2)

if __name__ == "__main__":
    main()
