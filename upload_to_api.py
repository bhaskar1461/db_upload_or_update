import json
import os
import sys
from pathlib import Path
import requests

# Fix Windows terminal printing for diverse character sets
sys.stdout.reconfigure(encoding='utf-8')

# --- API Configuration ---
# Replace this with the exact endpoint from the developers/documentation
API_URL = "https://ainotes.schools2ai.com/api/v1/notes/upload" 
API_TOKEN = "YOUR_API_TOKEN_HERE"  # Replace with your actual Bearer token or API key

def upload_chapter_to_api(class_name, language, subject, topic, markdown_notes, pdf_path):
    """
    Sends the short notes and the textbook PDF to the schools2ai API.
    """
    # Setup headers. (Do NOT set Content-Type manually when sending files)
    headers = {}
    if API_TOKEN and API_TOKEN != "YOUR_API_TOKEN_HERE":
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    # Setup the text data payload
    data_payload = {
        "class": class_name,
        "language": language,
        "subject": subject,
        "topic": topic,
        "short_notes": markdown_notes,
    }

    # Setup the file payload for the textbook PDF
    files = {}
    if pdf_path and pdf_path.exists():
        # The key 'textbook_pdf' should match whatever field name the API expects
        files['textbook_pdf'] = (pdf_path.name, open(pdf_path, 'rb'), 'application/pdf')
    else:
        print(f"  [Warning] PDF not found at {pdf_path}")

    # Make the POST request
    try:
        response = requests.post(API_URL, headers=headers, data=data_payload, files=files)
        
        if response.status_code in [200, 201]:
            print(f"  [SUCCESS] Uploaded: Class {class_name} {subject} - {topic}")
            return True
        else:
            print(f"  [FAILED] HTTP {response.status_code} for {topic}")
            print(f"  [Response] {response.text}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Network error for {topic}: {str(e)}")
        return False
        
    finally:
        # Ensure the file is closed if we opened it
        if 'textbook_pdf' in files:
            files['textbook_pdf'][1].close()


def find_pdf_for_topic(base_dir, language, class_name, subject, topic):
    """
    Attempts to locate the original PDF based on the directory structure.
    Adjust this logic to match exactly how your folders are structured.
    """
    # Example Path: C:\Users\bhask\Desktop\New folder\English\Class 9th\Grammar and Writing\Active and Passive Voice.pdf
    # This is a best-effort guess based on your workspace setup.
    medium_folder = "English" if language.lower() == "english" else "Hindi"
    class_folder = f"Class {class_name}th" if "9" in class_name else f"{class_name}th class"
    
    # We search recursively in the class folder for a PDF that matches the topic name
    search_dir = base_dir / medium_folder / class_folder
    if not search_dir.exists():
        # Fallback for folder naming inconsistencies
        search_dir = base_dir / medium_folder
    
    # Clean topic for matching (removing numbering)
    clean_topic = topic.split(". ", 1)[-1] if ". " in topic[:5] else topic
    
    if search_dir.exists():
        for pdf_file in search_dir.rglob("*.pdf"):
            # Check if the topic name is in the PDF file name
            if clean_topic.lower() in pdf_file.name.lower():
                return pdf_file
                
    return None


def main():
    BASE_DIR = Path(__file__).parent
    cache_files = list(BASE_DIR.glob('rag_cache_Class_*.json'))
    
    if not cache_files:
        print("No cache files found.", flush=True)
        return

    total_uploaded = 0

    for cache_file in cache_files:
        print(f"\nProcessing {cache_file.name}...")
        parts = cache_file.stem.split('_')
        if len(parts) >= 5:
            class_name = parts[3].lower().replace("th", "").strip() 
            language = parts[4] if len(parts) < 6 else parts[5]
        else:
            continue

        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"Error reading {cache_file.name}: {e}")
            continue

        for key, markdown_notes in data.items():
            key_parts = key.split("||")
            if len(key_parts) == 3:
                subject, subcat, topic = key_parts
            elif len(key_parts) == 2:
                subject, topic = key_parts
            else:
                topic = key
                subject = "General"

            # Clean up the topic name
            clean_topic = topic.split(". ", 1)[1] if ". " in topic[:5] else topic

            print(f"Preparing to upload: {clean_topic}")
            
            # 1. Locate the corresponding PDF
            pdf_path = find_pdf_for_topic(BASE_DIR, language, class_name, subject, topic)
            
            # 2. Upload to the API
            success = upload_chapter_to_api(
                class_name=class_name,
                language=language,
                subject=subject,
                topic=clean_topic,
                markdown_notes=markdown_notes,
                pdf_path=pdf_path
            )
            
            if success:
                total_uploaded += 1

    print(f"\nDone! Successfully uploaded {total_uploaded} records to the API.")

if __name__ == "__main__":
    main()
