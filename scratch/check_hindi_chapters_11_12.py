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
        
        print("=== HINDI CHAPTERS UNDER ENGLISH SUBJECTS FOR CLASS 11/12 ===")
        cursor.execute("""
            SELECT s.id as subject_id, s.subject_name, cs.class_id, s.stream_id,
                   COUNT(CASE WHEN c.language = 'english' THEN 1 END) as en_chapters,
                   COUNT(CASE WHEN c.language = 'hindi' THEN 1 END) as hi_chapters
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            LEFT JOIN chapters c ON c.subject_id = s.id
            WHERE cs.class_id IN (11, 12) AND s.language = 'english'
            GROUP BY s.id, s.subject_name, cs.class_id, s.stream_id
            ORDER BY cs.class_id, s.subject_name
        """)
        for r in cursor.fetchall():
            print(f"Class: {r['class_id']:<2} | Subj ID: {r['subject_id']:>3d} | Name: {r['subject_name']:<25s} | Stream: {r['stream_id']} | English Chapters: {r['en_chapters']:>2d} | Hindi Chapters: {r['hi_chapters']:>2d}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
