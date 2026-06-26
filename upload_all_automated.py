import os
import json
import re
import time
import requests

API_URL = "https://app-api.schools2ai.com/api/ainote"

# These are the exact headers your browser used, which will bypass Cloudflare 
# since you are running this from your own trusted IP address!
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

def find_pdf(base_dir, class_str, stream, subject, chapter_name):
    """Finds a PDF file by searching for the chapter name in the filename."""
    # Handle different class formatting
    class_folder = f"Class {class_str}th"
    if stream:
        class_folder += f" {stream}"
    
    # Check if directory exists
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
                # Check if chapter name or number is in the filename
                # Clean chapter name for comparison
                clean_chap = re.sub(r'[^\w\s]', '', chapter_name).lower()
                clean_f = re.sub(r'[^\w\s]', '', f).lower()
                if clean_chap in clean_f or chapter_name.lower() in f.lower():
                    return os.path.join(root, f)
    return None

def process_cache_file(filepath):
    print(f"\nProcessing: {os.path.basename(filepath)}")
    
    # Extract metadata from filename (e.g. rag_cache_Class_11th_Science_Hindi.json)
    filename = os.path.basename(filepath)
    parts = filename.replace("rag_cache_Class_", "").replace(".json", "").split("_")
    
    class_num = parts[0].replace("th", "")
    stream = parts[1] if len(parts) > 2 else ""
    language = parts[-1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for key, content in data.items():
        try:
            # Key format: Subject||_main||Chapter Name
            key_parts = key.split("||")
            subject = key_parts[0].strip()
            raw_chapter = key_parts[-1].strip()
            
            # Clean chapter name
            chapter_name = re.sub(r'^\d+\.?\s*', '', raw_chapter).strip()
            
            print(f"  -> Uploading: {subject} - {chapter_name}")
            
            notes_pdf = find_pdf(NOTES_DIR, class_num, stream, subject, chapter_name)
            book_pdf = find_pdf(TEXTBOOK_DIR, class_num, stream, subject, chapter_name)
            
            files = []
            files_to_close = []
            
            if notes_pdf:
                f_obj = open(notes_pdf, 'rb')
                files_to_close.append(f_obj)
                files.append(("notes", (os.path.basename(notes_pdf), f_obj, "application/pdf")))
            else:
                files.append(("notes", ("empty.pdf", b"", "application/pdf")))
                
            if book_pdf:
                f_obj = open(book_pdf, 'rb')
                files_to_close.append(f_obj)
                files.append(("books", (os.path.basename(book_pdf), f_obj, "application/pdf")))
            else:
                files.append(("books", ("empty.pdf", b"", "application/pdf")))
                
            data_payload = {
                "language": language,
                "board": "CBSE",
                "class": class_num,
                "subject": subject,
                "stream": stream,
                "createdBy": "AI",
                "chapters": json.dumps([chapter_name], ensure_ascii=False),
                "short_notes": json.dumps([content], ensure_ascii=False),
            }
            
            # Send Request
            response = requests.post(API_URL, data=data_payload, files=files, headers=HEADERS, timeout=60)
            
            if response.status_code == 200:
                print("     ✅ Success!")
            else:
                print(f"     ❌ Failed: {response.status_code} - {response.text}")
                
            # Cleanup
            for f_obj in files_to_close:
                f_obj.close()
                
            # Small delay to prevent rate-limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"     ⚠️ Error uploading {key}: {str(e)}")

def main():
    print("🚀 Starting Automated API Bulk Upload...")
    
    # Install requests if missing
    try:
        import requests
    except ImportError:
        os.system("pip install requests")
        import requests

    for file in os.listdir(RAG_CACHE_DIR):
        if file.startswith("rag_cache_") and file.endswith(".json"):
            filepath = os.path.join(RAG_CACHE_DIR, file)
            process_cache_file(filepath)

if __name__ == "__main__":
    main()
