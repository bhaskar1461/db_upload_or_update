import os
import re
import sys
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def clean_topic_name(topic):
    # Removes "1. ", "Chapter 1: ", "Chapter 12 - ", etc.
    return re.sub(r'^(?:(?:Chapter|Ch)\s*\d+\s*[:\-]\s*|\d+\.\s*)', '', topic, flags=re.IGNORECASE).strip()

def main():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, topic FROM ai_notes")
        rows = cursor.fetchall()
        
        updated = 0
        for row_id, topic in rows:
            if not topic: continue
            cleaned = clean_topic_name(topic)
            if cleaned != topic:
                try:
                    cursor.execute("UPDATE ai_notes SET topic = %s WHERE id = %s", (cleaned, row_id))
                    updated += 1
                    print(f"Updated: '{topic}' -> '{cleaned}'")
                except Exception as e:
                    print(f"Error updating id {row_id}: {e}")
                    
        conn.commit()
        cursor.close()
        conn.close()
        print(f"\nSuccessfully cleaned {updated} topics in the database.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
