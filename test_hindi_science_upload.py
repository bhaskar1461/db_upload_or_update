import os
import json
import re
from curl_cffi import requests
from curl_cffi import CurlMime

API_URL = "https://app-api.schools2ai.com/api/ainote"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.5",
    "origin": "https://ainotes.schools2ai.com",
    "priority": "u=1, i",
    "referer": "https://ainotes.schools2ai.com/",
    "sec-ch-ua": '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "sec-gpc": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

BASE_DIR = r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th"
NOTES_DIR = os.path.join(BASE_DIR, "11th &12th")
TEXTBOOK_DIR = os.path.join(BASE_DIR, "class 11 and 12 text book")
RAG_CACHE_DIR = r"C:\Users\bhask\Desktop\New folder"
RAG_FILE = os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Science_Hindi.json")

def find_pdf(base_dir, class_str, stream, subject, chapter_name):
    class_folder = f"Class {class_str}th"
    if stream:
        class_folder += f" {stream}"
    
    target_dir = None
    for root, dirs, files in os.walk(base_dir):
        if class_folder.lower() in root.lower() and subject.lower() in root.lower():
            target_dir = root
            break
            
    if not target_dir:
        return None
        
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.lower().endswith('.pdf'):
                clean_chap = re.sub(r'[^\w\s]', '', chapter_name).lower()
                clean_f = re.sub(r'[^\w\s]', '', f).lower()
                if clean_chap in clean_f or chapter_name.lower() in f.lower():
                    return os.path.join(root, f)
    return None

with open(RAG_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Pick the first physics chapter
key_to_upload = None
for k in data.keys():
    if "भौतिकी" in k:
        key_to_upload = k
        break

if not key_to_upload:
    print("Could not find a physics chapter!")
    exit(1)

content = data[key_to_upload]
key_parts = key_to_upload.split("||")
subject = key_parts[0].strip()
raw_chapter = key_parts[-1].strip()
chapter_name = re.sub(r'^\d+\.?\s*', '', raw_chapter).strip()

print(f"Testing Upload for: {subject} - {chapter_name}")

notes_pdf = find_pdf(NOTES_DIR, "11", "Science", subject, chapter_name)
book_pdf = find_pdf(TEXTBOOK_DIR, "11", "Science", subject, chapter_name)

print(f"Notes PDF: {notes_pdf}")
print(f"Book PDF: {book_pdf}")

mp = CurlMime()

if notes_pdf:
    mp.addpart(name="notes", content_type="application/pdf", filename=os.path.basename(notes_pdf), local_path=notes_pdf)
else:
    mp.addpart(name="notes", content_type="application/pdf", filename="empty.pdf", data=b"")

if book_pdf:
    mp.addpart(name="books", content_type="application/pdf", filename=os.path.basename(book_pdf), local_path=book_pdf)
else:
    mp.addpart(name="books", content_type="application/pdf", filename="empty.pdf", data=b"")

data_payload = {
    "language": "Hindi",
    "board": "CBSE",
    "class": "11",
    "subject": subject,
    "stream": "Science",
    "createdBy": "AI",
    "chapters": json.dumps([chapter_name], ensure_ascii=False),
    "short_notes": json.dumps([content], ensure_ascii=False),
}

print("\n--- Sending request to API via curl_cffi ---")
try:
    response = requests.post(API_URL, data=data_payload, multipart=mp, headers=HEADERS, impersonate="chrome110", timeout=60)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Error:", str(e))
finally:
    mp.close()
