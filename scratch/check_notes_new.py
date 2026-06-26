import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def main():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        print("=== CHECK ai_notes_new CLASS 11/12 HINDI chapter_id MAPPINGS ===")
        cursor.execute("""
            SELECT class, subject, topic, chapter_id
            FROM ai_notes_new
            WHERE class IN ('11', '12') AND language = 'Hindi'
            LIMIT 30
        """)
        for r in cursor.fetchall():
            print(f"Class: {r['class']} | Subject: {r['subject']} | Topic: {r['topic']} | Chapter ID: {r['chapter_id']}")

        print("\n=== ARE THERE ANY chapter_id MAPPINGS THAT ARE NULL? ===")
        cursor.execute("""
            SELECT class, language, COUNT(*) as null_count
            FROM ai_notes_new
            WHERE chapter_id IS NULL OR chapter_id = 0
            GROUP BY class, language
        """)
        for r in cursor.fetchall():
            print(f"Class: {r['class']} | Lang: {r['language']} | Null/Zero Chapter ID count: {r['null_count']}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
