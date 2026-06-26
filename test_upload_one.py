from curl_cffi import requests
import json
import os
import re

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

BASE_DIR = r"c:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th"
NOTES_DIR = os.path.join(BASE_DIR, "11th &12th")
TEXTBOOK_DIR = os.path.join(BASE_DIR, "class 11 and 12 text book")
RAG_CACHE_DIR = r"C:\Users\bhask\Desktop\New folder"
RAG_FILE = os.path.join(RAG_CACHE_DIR, "rag_cache_Class_11th_Science_Hindi.json")

def find_notes_pdf(notes_base, class_num, stream, subject, chapter_name):
    class_dir = f"Class {class_num}th {stream}"
    subject_dir = os.path.join(notes_base, class_dir, subject)
    if not os.path.isdir(subject_dir): return None
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf') and chapter_name in f:
                return os.path.join(root, f)
    return None

def find_textbook_pdf(textbook_base, class_num, stream, subject, chapter_name):
    class_dir = f"Class {class_num}th {stream}"
    subject_dir = os.path.join(textbook_base, class_dir, subject)
    if not os.path.isdir(subject_dir): return None
    for root, dirs, files in os.walk(subject_dir):
        for f in files:
            if f.endswith('.pdf') and chapter_name in f:
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

notes_content = data[key_to_upload]
print(f"Testing Upload for: {key_to_upload}")

# Extract names
parts = key_to_upload.split("||")
subject = parts[0]
raw_chapter = parts[-1]
chapter_name = re.sub(r'^\d+\.?\s*', '', raw_chapter).strip()

notes_pdf = find_notes_pdf(NOTES_DIR, 11, "Science", subject, chapter_name)
book_pdf = find_textbook_pdf(TEXTBOOK_DIR, 11, "Science", subject, chapter_name)

print(f"Notes PDF Found: {notes_pdf}")
print(f"Book PDF Found: {book_pdf}")

data_payload = {
    "language": "Hindi",
    "board": "CBSE",
    "class": "11",
    "subject": subject,
    "stream": "Science",
    "createdBy": "AI",
    "chapters": json.dumps([chapter_name], ensure_ascii=False),
    "short_notes": json.dumps([notes_content], ensure_ascii=False),
}

# curl_cffi syntax for multipart
multipart_data = {}

for k, v in data_payload.items():
    multipart_data[k] = str(v)

if notes_pdf:
    with open(notes_pdf, 'rb') as f:
        multipart_data["notes"] = (os.path.basename(notes_pdf), f.read(), "application/pdf")
else:
    multipart_data["notes"] = ("empty.pdf", b"", "application/pdf")

if book_pdf:
    with open(book_pdf, 'rb') as f:
        multipart_data["books"] = (os.path.basename(book_pdf), f.read(), "application/pdf")
else:
    multipart_data["books"] = ("empty.pdf", b"", "application/pdf")

print("\n--- Sending request to API using curl_cffi ---")
try:
    resp = requests.post(API_URL, multipart=multipart_data, headers=HEADERS, impersonate="chrome110", timeout=60)
    print("Status Code:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)
