import os
import sys
import json
import re
import mysql.connector
from dotenv import load_dotenv
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def clean_str(s):
    """Strip all punctuation, underscores, numbers, and normalize."""
    s = re.sub(r'^\d+[\.\)\-\s]*', '', s)  # strip leading number
    s = s.replace('.pdf', '').replace('.PDF', '')
    s = re.sub(r'[^\w\s]', ' ', s)  # punctuation -> space
    s = re.sub(r'_', ' ', s)  # underscores -> space
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def index_all_local_pdfs():
    print("Indexing all local PDF files on disk...")
    local_files = defaultdict(list)
    for root, dirs, files in os.walk(BASE_DIR):
        root_lower = root.lower()
        if "11th" in root_lower or "12th" in root_lower or "11" in root_lower or "12" in root_lower:
            continue
        for f in files:
            if f.lower().endswith('.pdf'):
                path = os.path.join(root, f)
                filename_clean = clean_str(f)
                local_files[filename_clean].append({
                    "path": path,
                    "filename": f,
                    "root": root
                })
    print(f"Indexed {sum(len(v) for v in local_files.values())} local PDFs.")
    return local_files

import time

def main():
    retries = 5
    conn = None
    for attempt in range(retries):
        try:
            print(f"Connecting to database (Attempt {attempt+1}/{retries})...")
            conn = mysql.connector.connect(
                host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
                user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
            )
            print("Successfully connected!")
            break
        except mysql.connector.Error as err:
            print(f"Connection failed: {err}")
            if attempt < retries - 1:
                time.sleep(3)
            else:
                print("All connection attempts failed. Exiting.")
                sys.exit(1)
                
    cursor = conn.cursor(dictionary=True)

    print("================================================================================")
    # 1. Fetch all rows for Classes 6, 7, 8, 9 from ai_notes_new
    print("Fetching all records for Classes 6, 7, 8, and 9 from ai_notes_new...")
    cursor.execute("SELECT * FROM ai_notes_new WHERE class IN ('6', '7', '8', '9')")
    rows = cursor.fetchall()
    print(f"Loaded {len(rows)} records.")
    print("================================================================================\n")

    # Metrics collections
    duplicates = []
    empty_topics = []
    generic_topics = []
    json_parse_errors = []
    invalid_short_notes_schema = []
    missing_full_notes = []
    missing_book_url = []
    grammar_missing_books = 0
    literature_missing_books = []
    
    seen = {}
    
    for r in rows:
        row_id = r['id']
        class_num = r['class']
        subject = r['subject']
        topic = r['topic']
        lang = r['language']
        short_notes = r['short_notes']
        full_notes = r['full_notes']
        book_url = r['book_url']

        # Check A: Duplicates check
        key = (class_num, subject.lower(), topic.lower(), lang.lower())
        if key in seen:
            duplicates.append(f"ID {row_id} is a duplicate of ID {seen[key]} | Class {class_num} | Subj: {subject} | Topic: '{topic}' | Lang: {lang}")
        else:
            seen[key] = row_id

        # Check B: Empty/NULL Topics
        if not topic or topic.strip() == "":
            empty_topics.append(row_id)
        elif re.search(r'^(?:Chapter|Ch|\d+\.)$', topic.strip(), re.IGNORECASE):
            generic_topics.append(f"ID {row_id} | Class {class_num} | Subj: {subject} | Topic: '{topic}'")

        # Check C: JSON validation of short_notes
        if not short_notes:
            invalid_short_notes_schema.append(f"ID {row_id} | Empty short_notes field")
        else:
            try:
                # The API stores it as JSON stringified array of stringified JSON objects
                # e.g., json.loads(short_notes) -> [json_content_string]
                data = json.loads(short_notes)
                if not isinstance(data, list):
                    invalid_short_notes_schema.append(f"ID {row_id} | short_notes is not a JSON list")
                elif len(data) == 0:
                    invalid_short_notes_schema.append(f"ID {row_id} | short_notes is an empty JSON list")
                else:
                    content_str = data[0]
                    # Sometimes it is double stringified
                    if isinstance(content_str, str):
                        try:
                            # Try to parse the inner string to see if it is valid JSON
                            inner = json.loads(content_str)
                        except Exception:
                            # It could be raw markdown string, which is also fine but let's check
                            if len(content_str) < 100:
                                invalid_short_notes_schema.append(f"ID {row_id} | short_notes content is too short (< 100 chars)")
                    else:
                        invalid_short_notes_schema.append(f"ID {row_id} | inner short_notes element is not a string")
            except Exception as ex:
                json_parse_errors.append(f"ID {row_id} | JSON decode error: {ex}")

        # Check D: Full Notes mapping validation
        if not full_notes or full_notes.strip() == "" or full_notes.lower() == "none":
            missing_full_notes.append(f"ID {row_id} | Class {class_num} | Subj: {subject} | Topic: '{topic}'")

        # Check E: Book URL mapping validation
        if not book_url or book_url.strip() == "" or book_url.lower() == "none":
            missing_book_url.append(row_id)
            if "grammar" in subject.lower() or "writing" in subject.lower() or "व्याकरण" in subject.lower():
                grammar_missing_books += 1
            else:
                literature_missing_books.append(f"ID {row_id} | Class {class_num} | Subj: {subject} | Topic: '{topic}'")

    # Output Sanity Check Report
    print("--------------------------------------------------------------------------------")
    print("📊 DATABASE SANITY CHECK & CONSISTENCY REPORT")
    print("--------------------------------------------------------------------------------")
    print(f"Total records checked: {len(rows)}")
    print(f"Unique keys found:     {len(seen)}")
    print(f"Duplicate records:     {len(duplicates)}")
    print(f"Empty/NULL topics:     {len(empty_topics)}")
    print(f"Generic topics:        {len(generic_topics)}")
    print(f"JSON parse errors:     {len(json_parse_errors)}")
    print(f"Invalid short_notes:   {len(invalid_short_notes_schema)}")
    print(f"Missing full_notes:    {len(missing_full_notes)}")
    print(f"Missing book_url:      {len(missing_book_url)} (Grammar: {grammar_missing_books}, Lit/Science/Maths: {len(literature_missing_books)})")
    print("--------------------------------------------------------------------------------\n")

    if duplicates:
        print("❌ DUPLICATES (Sample of 10):")
        for d in duplicates[:10]:
            print(f"  {d}")
        print()

    if empty_topics:
        print(f"❌ EMPTY/NULL TOPICS ({len(empty_topics)} found):")
        print(f"  IDs: {empty_topics}")
        print()

    if generic_topics:
        print("❌ GENERIC TOPICS (Sample of 10):")
        for gt in generic_topics[:10]:
            print(f"  {gt}")
        print()

    if json_parse_errors:
        print("❌ JSON PARSE ERRORS (Sample of 10):")
        for je in json_parse_errors[:10]:
            print(f"  {je}")
        print()

    if invalid_short_notes_schema:
        print("❌ INVALID SHORT_NOTES (Sample of 10):")
        for iv in invalid_short_notes_schema[:10]:
            print(f"  {iv}")
        print()

    if missing_full_notes:
        print("❌ MISSING FULL NOTES (Sample of 15):")
        for mf in missing_full_notes[:15]:
            print(f"  {mf}")
        print()

    if literature_missing_books:
        print("ℹ️ LITERATURE/SCIENCE/MATHS CHAPTERS MISSING TEXTBOOKS (Sample of 15):")
        for lm in literature_missing_books[:15]:
            print(f"  {lm}")
        print()

    # 2. Re-verify S3 paths matches local files where full_notes exists
    print("================================================================================")
    print("🔍 VERIFYING FILE-PATH LINKAGE (Checking if DB paths match files on disk)")
    print("================================================================================")
    local_pdfs = index_all_local_pdfs()
    
    broken_full_notes_links = 0
    broken_book_links = 0
    verified_links = 0

    for r in rows:
        full_notes = r['full_notes']
        book_url = r['book_url']
        topic = r['topic']
        
        # Verify full_notes
        if full_notes and full_notes.lower() != 'none':
            # Extract clean filename from S3 key (e.g. Notes/CBSE/English/Class7/science/Light-1780167121964.pdf -> Light)
            fn_basename = os.path.basename(full_notes)
            # Remove timestamp part: Light-1780167121964.pdf -> Light.pdf
            fn_clean = re.sub(r'-\d+\.pdf$', '', fn_basename, flags=re.IGNORECASE)
            fn_clean_normalized = clean_str(fn_clean)
            
            # Find if this file exists in our local indexed PDFs
            if fn_clean_normalized in local_pdfs:
                verified_links += 1
            else:
                # Try word overlap
                matched = False
                for loc_fn in local_pdfs.keys():
                    loc_words = set(loc_fn.split())
                    db_words = set(fn_clean_normalized.split())
                    if len(loc_words) > 1 and len(db_words) > 1:
                        overlap = loc_words & db_words
                        if len(overlap) >= min(len(loc_words), len(db_words)) * 0.7:
                            matched = True
                            break
                if matched:
                    verified_links += 1
                else:
                    broken_full_notes_links += 1
                    if broken_full_notes_links <= 10:
                        print(f"  ❌ Broken full_notes path: {full_notes} (Cleaned: '{fn_clean_normalized}' does not match any local PDF)")

        # Verify book_url
        if book_url and book_url.lower() != 'none':
            bk_basename = os.path.basename(book_url)
            bk_clean = re.sub(r'-\d+\.pdf$', '', bk_basename, flags=re.IGNORECASE)
            bk_clean_normalized = clean_str(bk_clean)
            
            if bk_clean_normalized in local_pdfs:
                verified_links += 1
            else:
                matched = False
                for loc_fn in local_pdfs.keys():
                    loc_words = set(loc_fn.split())
                    db_words = set(bk_clean_normalized.split())
                    if len(loc_words) > 1 and len(db_words) > 1:
                        overlap = loc_words & db_words
                        if len(overlap) >= min(len(loc_words), len(db_words)) * 0.7:
                            matched = True
                            break
                if matched:
                    verified_links += 1
                else:
                    broken_book_links += 1
                    if broken_book_links <= 10:
                        print(f"  ❌ Broken book_url path: {book_url} (Cleaned: '{bk_clean_normalized}' does not match any local PDF)")

    print("--------------------------------------------------------------------------------")
    print(f"Verified Database-to-Disk PDF Matches: {verified_links}")
    print(f"Broken full_notes links:               {broken_full_notes_links}")
    print(f"Broken book_url links:                 {broken_book_links}")
    print("--------------------------------------------------------------------------------\n")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
