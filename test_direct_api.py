import json
import os
import requests

# Test data for one chapter
url = "https://app-api.schools2ai.com/api/ainote"

notes_path = r"C:\Users\bhask\Desktop\New folder\English\6th class\Science\Science\Biology\1. Food Where Does It Come From.pdf"

content = {"Introduction": "This is a direct API upload test."}

data = {
    "language": "English",
    "board": "CBSE",
    "class": "6",
    "subject": "Science",
    "stream": "",
    "createdBy": "AI",
    "chapters": json.dumps(["Food Where Does It Come From"]),
    # The server expects an array containing a single JSON string
    "short_notes": json.dumps([json.dumps(content)])
}

files = {
    "notes": (os.path.basename(notes_path), open(notes_path, "rb"), "application/pdf")
}
data["noteChapterIndices"] = json.dumps([0])

print("Sending POST request directly to API...")
try:
    response = requests.post(url, data=data, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
finally:
    files["notes"][1].close()
