import json
import os
import sys
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

# Fix Windows terminal printing for diverse character sets
sys.stdout.reconfigure(encoding='utf-8')

# Load database credentials from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "your_database_name")

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

def main():
    BASE_DIR = Path(__file__).parent
    cache_files = list(BASE_DIR.glob('rag_cache_Class_*.json'))
    
    if not cache_files:
        print("No cache files found.", flush=True)
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    total_inserted = 0
    total_updated = 0

    for cache_file in cache_files:
        parts = cache_file.stem.split('_')
        stream = None
        if len(parts) >= 5:
            class_name = parts[3].lower().replace("th", "").strip() 
            if len(parts) >= 6 and parts[4] in ['Commerce', 'Humanities', 'Science', 'Arts']:
                stream = parts[4]
                language = parts[5]
            else:
                language = parts[4]
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

            # Remove prefix numbers like '1. ' from topic if present
            clean_topic = topic
            if ". " in clean_topic[:5]:
                clean_topic = clean_topic.split(". ", 1)[1]
            else:
                clean_topic = topic

            # Check if this note already exists
            check_query = """
                SELECT id FROM ai_notes 
                WHERE class = %s AND subject = %s AND topic = %s AND language = %s
            """
            cursor.execute(check_query, (class_name, subject, topic, language))
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
                    print(f"Updated: Class {class_name} {subject} - {topic}", flush=True)
                except mysql.connector.Error as err:
                    print(f"Error updating {topic}: {err}", flush=True)

            else:
                # Row does NOT exist: perform an INSERT
                insert_query = """
                    INSERT INTO ai_notes 
                    (language, class, subject, topic, short_notes, stream, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    language,               
                    class_name,             
                    subject,                
                    topic,                  
                    markdown_notes,
                    stream
                )
                try:
                    cursor.execute(insert_query, values)
                    total_inserted += 1
                    print(f"Inserted: Class {class_name} {subject} - {topic}", flush=True)
                except mysql.connector.Error as err:
                    print(f"Error inserting {topic}: {err}", flush=True)

    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\nDone! Successfully UPSERTED data.")
    print(f"Total New Records Inserted: {total_inserted}")
    print(f"Total Existing Records Updated: {total_updated}")

if __name__ == "__main__":
    main()
