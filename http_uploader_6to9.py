import os
import sys
import json
import re
import time
import requests
import mysql.connector
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = r"C:\Users\bhask\Desktop\Archive\New folder"
URL = "https://app-api.schools2ai.com/api/ainote"
ALL_FILES = []

def index_files():
    global ALL_FILES
    print("Indexing workspace files...")
    search_dirs = [
        r"C:\Users\bhask\Desktop\edu_content_system\final_pdf",
        r"C:\Users\bhask\Desktop\Study Materials",
        BASE_DIR
    ]
    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        print(f"Scanning directory: {sdir}")
        for root, dirs, files in os.walk(sdir):
            root_lower = root.lower()
            if "11th" in root_lower or "12th" in root_lower or "11" in root_lower or "12" in root_lower:
                continue
            for f in files:
                if f.lower().endswith('.pdf'):
                    ALL_FILES.append({
                        "path": os.path.join(root, f),
                        "filename": f,
                        "root_lower": root_lower
                    })
    print(f"Indexed {len(ALL_FILES)} PDF files.")

def normalize_name(name):
    # Replace all non-alphanumeric/non-Hindi characters with spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', ' ', name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    
    # Remove Hindi conjunctions/stopwords
    cleaned = re.sub(r'\b(और|एवं|तथा)\b', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Apply Hindi spelling-insensitive normalization
    cleaned = cleaned.replace('ी', 'ि')
    cleaned = cleaned.replace('ू', 'ु')
    cleaned = cleaned.replace('ं', '')
    cleaned = cleaned.replace('ँ', '')
    cleaned = cleaned.replace('श', 'स')
    cleaned = cleaned.replace('ष', 'स')
    cleaned = cleaned.replace('ज़', 'ज')
    cleaned = cleaned.replace('त्सी', 'ज')
    cleaned = cleaned.replace('ज़ी', 'ज')
    cleaned = cleaned.replace('ऋ', 'र')
    
    return cleaned

def find_pdf_for_6to9(class_str, subject, chapter_name, file_type, raw_chapter="", sub_subject=""):
    """
    Finds the appropriate PDF based on the class and whether we want notes or books.
    file_type: "notes" or "books"
    """
    clean_chap = normalize_name(chapter_name)
    
    is_dummy_sub = (not sub_subject) or sub_subject.strip().startswith('_')
    if sub_subject.lower() in ['textbooks', 'notes']:
        is_dummy_sub = True
    candidate_files = []
            
    for file_info in ALL_FILES:
        root_lower = file_info["root_lower"]
        f = file_info["filename"]
        path = file_info["path"]
        
        # Class filtering
        if class_str == "9":
            if "9" not in root_lower and "ninth" not in root_lower:
                continue
        elif class_str == "8":
            if "8" not in root_lower and "eighth" not in root_lower:
                continue
        elif class_str == "7":
            if "7" not in root_lower and "seventh" not in root_lower:
                continue
        elif class_str == "6":
            if "6" not in root_lower and "sixth" not in root_lower:
                continue
                
        # Subject filtering (with translation mismatch override for Social Studies / Social Science)
        subject_matched = False
        if subject.lower() in root_lower:
            subject_matched = True
        elif "final_pdf" in root_lower:
            # Under final_pdf, Mathematics and CT & AI / AI notes are all located under Class_* directories
            if subject.lower() in ["mathematics", "computational thinking and artificial intelligence", "ct and ai", "artificial intelligence", "ai"]:
                subject_matched = True
        else:
            sub_clean = re.sub(r'\(.*?\)', '', subject).strip().lower()
            if sub_clean in root_lower:
                subject_matched = True
            elif ('social' in subject.lower() or 'सामाजिक' in subject.lower()) and ('social' in root_lower or 'सामाजिक' in root_lower):
                subject_matched = True
                
        if not subject_matched:
            continue
                
        # Fix: If the subject is 'science' or 'विज्ञान (science)', it should not match 'social science' or 'सामाजिक विज्ञान'
        if ('science' in subject.lower() and 'social' not in subject.lower()) and 'social science' in root_lower:
            continue
        if ('विज्ञान' in subject.lower() and 'सामाजिक' not in subject.lower()) and 'सामाजिक विज्ञान' in root_lower:
            continue

        # Sub-subject matching logic to avoid cross-matching subfolders
        if not is_dummy_sub:
            parts = re.split(r'[\(\)/\|]', sub_subject)
            matched_sub = False
            for part in parts:
                part_clean = normalize_name(part)
                if not part_clean:
                    continue
                part_clean_no_digits = re.sub(r'^\d+\s*', '', part_clean).strip()
                if not part_clean_no_digits:
                    continue
                root_clean = normalize_name(root_lower)
                if part_clean_no_digits in root_clean:
                    matched_sub = True
                    break
            if not matched_sub:
                continue

        # Textbooks vs Notes logic for Class 9
        if class_str == "9":
            if file_type == "books" and "textbooks" not in root_lower:
                continue
            if file_type == "notes" and "textbooks" in root_lower:
                continue
        else:
            if file_type == "books":
                continue
        candidate_files.append((f, path))
        
    # Pass 1: Try to match by chapter name
    for f, path in candidate_files:
        clean_f = normalize_name(f)
        if (clean_chap and clean_chap in clean_f) or (chapter_name and chapter_name.lower() in f.lower()):
            return path
            
    # Pass 2: Match by chapter number at start
    if raw_chapter:
        chap_match = re.search(r'^(?:chapter|अध्याय)?\s*(\d+)\b', raw_chapter, re.IGNORECASE)
        if chap_match:
            chap_num = chap_match.group(1)
            for f, path in candidate_files:
                file_match = re.search(r'^(?:chapter|अध्याय)?\s*(\d+)\b', f, re.IGNORECASE)
                if file_match:
                    file_chap_num = file_match.group(1)
                    if chap_num == file_chap_num:
                        return path
                            
    return None

def get_uploaded_topics(language, class_num):
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor()
        query = f"SELECT topic FROM ai_notes_new WHERE language = '{language}' AND class = '{class_num}'"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return set([r[0].strip() for r in results])
    except Exception as e:
        print(f"⚠️ Could not fetch uploaded topics from DB: {e}")
        return set()

def upload_task(class_num, language, subject, chapter_name, content, notes_pdf, book_pdf):
    data = {
        "language": language,
        "board": "CBSE",
        "class": class_num,
        "subject": subject,
        "stream": "",
        "createdBy": "AI",
        "chapters": json.dumps([chapter_name], ensure_ascii=False),
        "short_notes": json.dumps([json.dumps(content, ensure_ascii=False)], ensure_ascii=False)
    }
    
    files = {}
    if notes_pdf:
        files["notes"] = (os.path.basename(notes_pdf), open(notes_pdf, "rb"), "application/pdf")
        data["noteChapterIndices"] = json.dumps([0])
        
    if class_num == "9" and book_pdf:
        files["books"] = (os.path.basename(book_pdf), open(book_pdf, "rb"), "application/pdf")
        data["bookChapterIndices"] = json.dumps([0])
        
    try:
        response = requests.post(URL, data=data, files=files, timeout=60)
        if response.status_code == 200:
            print(f"     ✅ Success: {class_num}th {subject} - {chapter_name}")
            return True, None
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)
    finally:
        for f in files.values():
            f[1].close()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--classes', nargs='+', default=["6", "7", "8", "9"])
    parser.add_argument('--threads', type=int, default=8)
    args = parser.parse_args()
    
    print(f"🚀 Starting High-Speed HTTP Bulk Uploader for Classes {args.classes} with {args.threads} threads...")
    
    index_files()
    
    # Load all keys to upload
    tasks = []
    for file in os.listdir(BASE_DIR):
        if file.startswith("rag_cache_Class_") and file.endswith(".json"):
            class_num = file.replace("rag_cache_Class_", "").split("th")[0]
            if class_num not in args.classes:
                continue
                
            parts = file.replace("rag_cache_Class_", "").replace(".json", "").split("_")
            language = parts[-1]
            
            filepath = os.path.join(BASE_DIR, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            print(f"Loading {file}...")
            uploaded_topics = get_uploaded_topics(language, class_num)
            
            for key, content in data.items():
                key_parts = key.split("||")
                subject = key_parts[0].strip()
                raw_chapter = key_parts[-1].strip()
                
                # Clean prefix and extract chapter name
                raw_chapter_clean = re.sub(r'^Copy\s+of\s+', '', raw_chapter, flags=re.IGNORECASE).strip()
                chapter_name = re.sub(r'^(?:Chapter\s*\d+\s*[:\-]?\s*)?\d*\.?\s*', '', raw_chapter_clean, flags=re.IGNORECASE).strip()
                
                if not chapter_name:
                    print(f"     ⚠️ Skipping empty chapter key '{key}'")
                    continue
                    
                sub_subject = ""
                if len(key_parts) > 2:
                    sub_subject = "||".join(key_parts[1:-1]).strip()
                    
                # Skip already uploaded
                already_uploaded = False
                for uploaded_topic in uploaded_topics:
                    if uploaded_topic.strip() == "": continue
                    if chapter_name.lower() in uploaded_topic.lower() or uploaded_topic.lower() in chapter_name.lower():
                        already_uploaded = True
                        break
                if already_uploaded:
                    continue
                    
                notes_pdf = find_pdf_for_6to9(class_num, subject, chapter_name, "notes", raw_chapter_clean, sub_subject)
                book_pdf = find_pdf_for_6to9(class_num, subject, chapter_name, "books", raw_chapter_clean, sub_subject)
                
                if not notes_pdf:
                    print(f"     ⚠️ Skipping {class_num}th {subject} - {chapter_name} (No Notes PDF found!)")
                    continue
                    
                tasks.append({
                    "class_num": class_num,
                    "language": language,
                    "subject": subject,
                    "chapter_name": chapter_name,
                    "content": content,
                    "notes_pdf": notes_pdf,
                    "book_pdf": book_pdf
                })

    print(f"\nTotal tasks loaded: {len(tasks)}")
    if not tasks:
        print("Nothing to upload. Exiting.")
        return
        
    start_time = time.time()
    
    # Run concurrent uploads
    success_count = 0
    fail_count = 0
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(
                upload_task, 
                t["class_num"], t["language"], t["subject"], t["chapter_name"], t["content"], t["notes_pdf"], t["book_pdf"]
            ): t for t in tasks
        }
        
        for future in as_completed(futures):
            t = futures[future]
            success, err = future.result()
            if success:
                success_count += 1
            else:
                fail_count += 1
                print(f"     ❌ Failed: {t['class_num']}th {t['subject']} - {t['chapter_name']}: {err}")
                
    elapsed = time.time() - start_time
    print(f"\n======================================")
    print(f"🏆 Bulk Upload Completed!")
    print(f"======================================")
    print(f"⏱️ Time elapsed: {elapsed:.1f} seconds")
    print(f"✅ Successful uploads: {success_count}")
    print(f"❌ Failed uploads: {fail_count}")

if __name__ == "__main__":
    main()
