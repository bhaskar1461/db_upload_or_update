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
        
        print("=== CLASS 9 HINDI NOTES IN ai_notes_new ===")
        cursor.execute("""
            SELECT n.id, n.subject, n.topic, n.chapter_id, c.name as chapter_name, c.subject_id, s.subject_name, s.language as subject_language
            FROM ai_notes_new n
            LEFT JOIN chapters c ON n.chapter_id = c.id
            LEFT JOIN subjects s ON c.subject_id = s.id
            WHERE n.class = '9' AND n.language = 'Hindi'
            LIMIT 10
        """)
        for r in cursor.fetchall():
            print(f"Note ID: {r['id']} | Note Subj: {r['subject']} | Topic: {r['topic']} | Ch ID: {r['chapter_id']} | Ch Name: {r['chapter_name']} | Subj ID: {r['subject_id']} | Subj Name: {r['subject_name']} | Subj Lang: {r['subject_language']}")

        print("\n=== CLASS 9 HINDI NOTES IN ai_notes ===")
        cursor.execute("""
            SELECT id, subject, topic, stream
            FROM ai_notes
            WHERE class = '9' AND language = 'Hindi'
            LIMIT 10
        """)
        for r in cursor.fetchall():
            print(f"Note ID: {r['id']} | Subject: {r['subject']} | Topic: {r['topic']} | Stream: {r['stream']}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
