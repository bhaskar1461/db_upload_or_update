import os
import json
from curl_cffi import requests
from pathlib import Path

API_URL = "https://app-api.schools2ai.com/api/ainote"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.5",
    "origin": "https://ainotes.schools2ai.com",
    "priority": "u=1, i",
    "referer": "https://ainotes.schools2ai.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

cache_path = Path(r"C:\Users\bhask\Desktop\Archive\New folder\rag_cache_Class_6th_English.json")
with open(cache_path, 'r', encoding='utf-8') as f:
    cache_data = json.load(f)

# Find "Chapter 01. Patterns in Mathematics"
notes_content = None
for k, v in cache_data.items():
    if "Patterns in Mathematics" in k:
        notes_content = v
        break

if not notes_content:
    print("Could not find chapter in cache!")
    exit(1)

notes_pdf = r"C:\Users\bhask\Desktop\Study Materials\Class 6\Mathematics\Notes\Chapter 01. Patterns in Mathematics.pdf"
print(f"Notes PDF path: {notes_pdf} (Exists: {os.path.exists(notes_pdf)})")

data_payload = {
    "language": "English",
    "board": "CBSE",
    "class": "6",
    "subject": "Mathematics",
    "stream": "",
    "createdBy": "AI",
    "chapters": json.dumps(["Patterns in Mathematics"]),
    "short_notes": json.dumps([notes_content]),
}

# Scenario 1: Only notes PDF, no books PDF
print("\n--- Test Scenario 1: Only notes PDF ---")
multipart_data = {}
for k, v in data_payload.items():
    multipart_data[k] = str(v)

with open(notes_pdf, 'rb') as f:
    multipart_data["notes"] = (os.path.basename(notes_pdf), f.read(), "application/pdf")
multipart_data["noteChapterIndices"] = json.dumps([0])

import traceback

try:
    resp = requests.post(API_URL, multipart=multipart_data, headers=HEADERS, impersonate="chrome110", timeout=60)
    print("Status Code:", resp.status_code)
    print("Response:", resp.text[:300])
except Exception as e:
    print("Error:")
    traceback.print_exc()

# Scenario 2: Notes PDF + Empty books PDF
print("\n--- Test Scenario 2: Notes PDF + Empty books PDF ---")
multipart_data = {}
for k, v in data_payload.items():
    multipart_data[k] = str(v)

with open(notes_pdf, 'rb') as f:
    multipart_data["notes"] = (os.path.basename(notes_pdf), f.read(), "application/pdf")
multipart_data["noteChapterIndices"] = json.dumps([0])

multipart_data["books"] = ("empty.pdf", b"", "application/pdf")

try:
    resp = requests.post(API_URL, multipart=multipart_data, headers=HEADERS, impersonate="chrome110", timeout=60)
    print("Status Code:", resp.status_code)
    print("Response:", resp.text[:300])
except Exception as e:
    print("Error:", e)
