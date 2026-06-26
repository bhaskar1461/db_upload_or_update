import os
import sys
import json
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

from upload_to_db import get_english_subject_type

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env')

db = mysql.connector.connect(
    host=os.getenv('DB_HOST','127.0.0.1'),
    user=os.getenv('DB_USER','root'),
    password=os.getenv('DB_PASSWORD',''),
    database=os.getenv('DB_NAME','u826463665_student')
)
cursor = db.cursor()

BASE_DIR = Path(__file__).parent
cache_files = list(BASE_DIR.glob('rag_cache_Class_11th_*.json'))

total_updated = 0

for cache_file in cache_files:
    parts = cache_file.stem.split('_')
    # parts: ['rag', 'cache', 'Class', '11th', 'Commerce', 'Hindi']
    if len(parts) >= 6:
        stream = parts[4]
    else:
        continue

    try:
        data = json.loads(cache_file.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Error reading {cache_file.name}: {e}")
        continue
        
    for key in data.keys():
        key_parts = key.split("||")
        if len(key_parts) == 3:
            subject, subcat, topic = key_parts
        elif len(key_parts) == 2:
            subject, topic = key_parts
        else:
            topic = key
            subject = "Unknown"

        # Apply same cleaning logic as upload
        clean_topic = topic
        if ". " in clean_topic[:5]:
            clean_topic = clean_topic.split(". ", 1)[1]

        subject = get_english_subject_type('11th', subject, clean_topic)

        update_query = """
            UPDATE ai_notes 
            SET stream = %s 
            WHERE class = '11' AND subject = %s AND topic = %s
        """
        try:
            cursor.execute(update_query, (stream, subject, topic))
            if cursor.rowcount > 0:
                total_updated += cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error updating {topic}: {err}")

db.commit()
cursor.close()
db.close()

print(f"Done! Successfully updated the stream column for {total_updated} rows.")
