import os
import sys
import re
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

from english_mapper import get_english_subject_type

# Fix Windows terminal printing for Hindi text
sys.stdout.reconfigure(encoding='utf-8')

# Load database credentials from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def main():
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = db.cursor()
        print("Connected to DB successfully.")

        # Get all English rows for classes 6, 7, 8
        cursor.execute("SELECT id, class, subject, topic FROM ai_notes WHERE class IN ('6', '7', '8') AND subject LIKE 'English%'")
        rows = cursor.fetchall()
        
        class_map = {
            '6': 'Class 6th',
            '7': 'Class 7th',
            '8': 'Class 8th'
        }
        
        updates = 0
        for row in rows:
            row_id, cls_num, subject, topic = row
            class_name = class_map[cls_num]
            
            # Clean topic prefix (e.g. "1. ", "Chapter 3: ")
            clean_topic = topic
            if ". " in clean_topic[:5]:
                clean_topic = clean_topic.split(". ", 1)[1]
            if clean_topic.startswith("Chapter "):
                parts = clean_topic.split(": ", 1)
                if len(parts) > 1:
                    clean_topic = parts[1]
                    
            # Try to map to Prose/Poem/Supplementary using our updated robust mapper
            new_subject = get_english_subject_type(class_name, "English", clean_topic)
            
            # Update row if topic name or subject changed
            if new_subject != subject or clean_topic != topic:
                # Skip Hindi math chapters that were miscategorized as English
                if new_subject == "English" and re.search(r'[\u0900-\u097F]', topic):
                    continue
                    
                print(f"Updating ID {row_id}: Subject '{subject}' -> '{new_subject}', Topic '{topic}' -> '{clean_topic}'")
                cursor.execute("UPDATE ai_notes SET subject = %s, topic = %s WHERE id = %s", (new_subject, clean_topic, row_id))
                updates += 1
                
        db.commit()
        print(f"Done! Updated {updates} records.")
        
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    main()
