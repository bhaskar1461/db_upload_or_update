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
        
        print("=== CHECK HOW CLASS 9 HINDI NOTES ARE STRUCTURED ===")
        cursor.execute("SELECT COUNT(*) FROM ai_notes WHERE class = '9' AND language = 'Hindi'")
        print(f"ai_notes count for Class 9 (Hindi): {cursor.fetchone()['COUNT(*)']}")
        
        cursor.execute("SELECT COUNT(*) FROM ai_notes_new WHERE class = '9' AND language = 'Hindi'")
        print(f"ai_notes_new count for Class 9 (Hindi): {cursor.fetchone()['COUNT(*)']}")

        print("\n=== SAMPLE CHAPTERS FOR CLASS 9 HINDI SUBJECTS ===")
        cursor.execute("""
            SELECT c.id, c.name, s.subject_name, s.id as subject_id, c.language
            FROM chapters c
            JOIN subjects s ON c.subject_id = s.id
            JOIN class_subjects cs ON s.id = cs.subject_id
            WHERE cs.class_id = 9 AND s.language = 'hindi'
            LIMIT 10
        """)
        for r in cursor.fetchall():
            print(f"Chapter ID: {r['id']} | Chapter Name: {r['name']} | Subject: {r['subject_name']} (ID: {r['subject_id']}) | Language: {r['language']}")

        print("\n=== ARE THERE ANY chapter_id MAPPINGS IN ai_notes_new FOR CLASS 9 HINDI? ===")
        cursor.execute("""
            SELECT chapter_id, COUNT(*)
            FROM ai_notes_new
            WHERE class = '9' AND language = 'Hindi'
            GROUP BY chapter_id
        """)
        for r in cursor.fetchall():
            print(f"chapter_id: {r['chapter_id']} | Count: {r['COUNT(*)']}")

        print("\n=== STRUCTURE OF CHAPTERS FOR HINDI IN GENERAL ===")
        cursor.execute("SELECT language, COUNT(*) FROM chapters GROUP BY language")
        for r in cursor.fetchall():
            print(f"Language in chapters: {r['language']} | Count: {r['COUNT(*)']}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
