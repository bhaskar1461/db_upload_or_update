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
    """Map string like '6th' to the admin_classes ID like '11'."""
    clean_str = class_str.lower().replace("th", "").strip()
    return str(CLASS_ID_MAP.get(clean_str, clean_str))

def main():
    BASE_DIR = Path(__file__).parent
    cache_files = list(BASE_DIR.glob('rag_cache_Class_*.json'))
    
    if not cache_files:
        print("No cache files found.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    total_updated = 0
    total_skipped = 0
    skipped_details = []

    for cache_file in cache_files:
        parts = cache_file.stem.split('_')
        if len(parts) >= 5:
            class_name = parts[3]
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
            key_parts = key.split("||")
            if len(key_parts) == 3:
                subject, subcat, topic = key_parts
            elif len(key_parts) == 2:
                subject, topic = key_parts
            else:
                topic = key
                subject = "Unknown"

            clean_topic = topic
            if ". " in clean_topic[:5]:
                clean_topic = clean_topic.split(". ", 1)[1]

            # Re-map English subject based on topic name
            subject = get_english_subject_type(class_name, subject, clean_topic)

            # Check if this note already exists
            check_query = """
                SELECT id FROM ai_notes 
                WHERE class = %s AND subject = %s AND topic = %s AND language = %s
            """
            cursor.execute(check_query, (class_id, subject, topic, language))
            row = cursor.fetchone()

            if row:
                # Update existing record
                update_query = """
                    UPDATE ai_notes 
                    SET short_notes = %s, updated_at = NOW() 
                    WHERE id = %s
                """
                try:
                    cursor.execute(update_query, (markdown_notes, row[0]))
                    total_updated += 1
                    print(f"Updated: {class_name} {subject} - {topic}")
                except mysql.connector.Error as err:
                    print(f"Error updating {topic}: {err}")
            else:
                # You can choose to insert it if it doesn't exist, or just skip it
                skip_msg = f"{class_name} | {subject} | {topic}"
                print(f"Skipping: {skip_msg} (Not found in DB)")
                skipped_details.append(skip_msg)
                total_skipped += 1

    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nDone! Successfully updated {total_updated} notes in the database. Skipped {total_skipped} topics.")
    
    if skipped_details:
        skipped_file = BASE_DIR / "skipped_topics.txt"
        with open(skipped_file, "w", encoding="utf-8") as f:
            f.write("Topics skipped (not found in database):\n")
            f.write("-" * 40 + "\n")
            for item in skipped_details:
                f.write(f"- {item}\n")
        print(f"A detailed list of skipped topics has been saved to: {skipped_file.name}")

if __name__ == "__main__":
    main()
