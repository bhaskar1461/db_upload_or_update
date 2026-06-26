import json
import os
import sys
# Fix Windows terminal printing for Hindi text
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

from english_mapper import get_english_subject_type

# Load database credentials from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

# Map your class string directly to the grade numbers
CLASS_ID_MAP = {
    "6": "6",
    "7": "7",
    "8": "8",
    "6th": "6",
    "7th": "7",
    "8th": "8"
}

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        sys.exit(1)

def get_class_id(class_str: str) -> str:
    """Map string like '6th' to the admin_classes ID."""
    clean_str = class_str.lower().replace("th", "").strip()
    return str(CLASS_ID_MAP.get(clean_str, clean_str))

def main():
    BASE_DIR = Path(__file__).parent
    cache_files = list(BASE_DIR.glob('rag_cache_Class_*.json'))
    
    if not cache_files:
        print("No cache files found. Have you generated the notes yet?", flush=True)
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    total_inserted = 0
    total_updated = 0

    for cache_file in cache_files:
        parts = cache_file.stem.split('_')
        stream = None
        if len(parts) >= 5:
            class_name = parts[3] # '6th' or '11th'
            if len(parts) >= 6 and parts[4] in ['Commerce', 'Humanities', 'Science', 'Arts']:
                stream = parts[4]
                language = parts[5]
            else:
                language = parts[4]
        else:
            continue
            
        class_id = get_class_id(class_name)

        try:
            data = json.loads(cache_file.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"Error reading {cache_file.name}: {e}")
            continue

        for key, markdown_notes in data.items():
            # Example Key: 'English||English||1. A House, A Home'
            key_parts = key.split("||")
            if len(key_parts) == 3:
                subject, subcat, topic = key_parts
            elif len(key_parts) == 2:
                subject, topic = key_parts
            else:
                topic = key
                subject = "Unknown"

            import re
            # Remove prefix numbers like '1. ', 'Chapter 1: ', 'Chapter 12 - ' from topic
            clean_topic = re.sub(r'^(?:(?:Chapter|Ch)\s*\d+\s*[:\-]\s*|\d+\.\s*)', '', topic, flags=re.IGNORECASE).strip()

            # Re-map English subject based on topic name
            subject = get_english_subject_type(class_name, subject, clean_topic)

            # Leave URLs empty as requested
            full_notes_path = ""
            book_url_path = ""

            # Check if this note already exists to prevent duplicates
            check_query = """
                SELECT id FROM ai_notes 
                WHERE class = %s AND subject = %s AND topic = %s AND language = %s
            """
            cursor.execute(check_query, (class_id, subject, clean_topic, language))
            result = cursor.fetchone()

            if result:
                # Row exists: perform an UPDATE
                row_id = result[0]
                update_query = """
                    UPDATE ai_notes 
                    SET short_notes = %s, stream = %s, updated_at = NOW()
                    WHERE id = %s
                """
                try:
                    cursor.execute(update_query, (markdown_notes, stream, row_id))
                    total_updated += 1
                    print(f"Updated: {class_name} {subject} - {clean_topic}", flush=True)
                except mysql.connector.Error as err:
                    print(f"Error updating {clean_topic}: {err}", flush=True)

            else:
                # Row does NOT exist: perform an INSERT
                insert_query = """
                    INSERT INTO ai_notes 
                    (language, board, class, subject, topic, short_notes, full_notes, book_url, generated_by, stream, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    language,               # language
                    "CBSE",                 # board
                    class_id,               # class
                    subject,                # subject
                    clean_topic,            # topic
                    markdown_notes,         # short_notes (markdown text)
                    full_notes_path,        # full_notes
                    book_url_path,          # book_url
                    "AI",                   # generated_by
                    stream                  # stream
                )
                try:
                    cursor.execute(insert_query, values)
                    total_inserted += 1
                    print(f"Inserted: {class_name} {subject} - {clean_topic}", flush=True)
                except mysql.connector.Error as err:
                    print(f"Error inserting {clean_topic}: {err}", flush=True)

    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nDone! Successfully UPSERTED data.")
    print(f"Total New Records Inserted: {total_inserted}")
    print(f"Total Existing Records Updated: {total_updated}")

if __name__ == "__main__":
    main()
