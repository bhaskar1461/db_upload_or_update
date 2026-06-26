import os
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
sys.path.append(BASE_DIR)

CLASS9_DIR = os.path.join(BASE_DIR, "Class 9")

print("Checking PDF files under Class 9:")
all_c9_pdfs = []
for root, dirs, files in os.walk(CLASS9_DIR):
    for f in files:
        if f.lower().endswith('.pdf'):
            path = os.path.join(root, f)
            all_c9_pdfs.append(path)

print(f"Total PDFs in Class 9: {len(all_c9_pdfs)}")
notes_c9 = [p for p in all_c9_pdfs if 'notes' in p.lower()]
textbooks_c9 = [p for p in all_c9_pdfs if 'textbooks' in p.lower() or 'text book' in p.lower()]
print(f"Notes PDFs: {len(notes_c9)}")
print(f"Textbook PDFs: {len(textbooks_c9)}")

# Let's inspect rag_cache keys for Class 9 and try to match using the code logic
print("\nTesting Book PDF Matching for Class 9:")
from http_uploader_6to9 import ALL_FILES, index_files, find_pdf_for_6to9

# Initialize ALL_FILES
index_files()

for file in ["rag_cache_Class_9th_English.json", "rag_cache_Class_9th_Hindi.json"]:
    filepath = os.path.join(BASE_DIR, file)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"\nMatching file: {file}")
        for key in list(data.keys())[:15]:
            key_parts = key.split("||")
            subject = key_parts[0].strip()
            raw_chapter = key_parts[-1].strip()
            raw_chapter_clean = re.sub(r'^Copy\s+of\s+', '', raw_chapter, flags=re.IGNORECASE).strip()
            chapter_name = re.sub(r'^(?:Chapter\s*\d+\s*[:\-]?\s*)?\d*\.?\s*', '', raw_chapter_clean, flags=re.IGNORECASE).strip()
            
            sub_subject = ""
            if len(key_parts) > 2:
                sub_subject = "||".join(key_parts[1:-1]).strip()
                
            book_pdf = find_pdf_for_6to9("9", subject, chapter_name, "books", raw_chapter_clean, sub_subject)
            notes_pdf = find_pdf_for_6to9("9", subject, chapter_name, "notes", raw_chapter_clean, sub_subject)
            print(f"  Key: {key}")
            print(f"    Cleaned chapter: {chapter_name}")
            print(f"    Notes matched: {os.path.basename(notes_pdf) if notes_pdf else 'NONE'}")
            print(f"    Book matched: {os.path.basename(book_pdf) if book_pdf else 'NONE'}")
