import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

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
        print(f"Connecting to database {DB_NAME} at {DB_HOST}...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM ai_notes")
        total = cursor.fetchone()[0]
        print(f"\nTotal notes in database: {total}")
        
        if total > 0:
            print("\nBreakdown by Class, Language, and Subject:")
            print("-" * 50)
            query = """
                SELECT class, language, subject, COUNT(*) as topic_count
                FROM ai_notes
                GROUP BY class, language, subject
                ORDER BY class, language, subject
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                class_id, lang, subj, count = row
                print(f"Class {class_id} ({lang}) - {subj}: {count} topics")
                
            print("\nSample of latest 5 topics:")
            print("-" * 50)
            cursor.execute("SELECT class, language, subject, topic FROM ai_notes ORDER BY id DESC LIMIT 5")
            latest = cursor.fetchall()
            for row in latest:
                class_id, lang, subj, topic = row
                print(f"- Class {class_id} ({lang}): {subj} -> {topic}")
                
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
