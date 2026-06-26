import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

# Fix Windows terminal printing for Hindi text
sys.stdout.reconfigure(encoding='utf-8')

# Load database credentials from .env
env_path = Path(__file__).parent.parent / ".env"
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
        cursor = conn.cursor(dictionary=True)
        
        print("\n--- Listing unique class and language combinations in ai_notes ---")
        cursor.execute("SELECT class, language, COUNT(*) as count FROM ai_notes GROUP BY class, language ORDER BY class, language")
        for row in cursor.fetchall():
            print(f"Class: {row['class']} | Language: {row['language']} | Count: {row['count']}")

        print("\n--- Listing unique class and language combinations in ai_notes_new ---")
        cursor.execute("SELECT class, language, COUNT(*) as count FROM ai_notes_new GROUP BY class, language ORDER BY class, language")
        for row in cursor.fetchall():
            print(f"Class: {row['class']} | Language: {row['language']} | Count: {row['count']}")

        print("\n--- Listing Class 11 and 12 Hindi entries in ai_notes ---")
        cursor.execute("""
            SELECT class, subject, stream, COUNT(*) as count 
            FROM ai_notes 
            WHERE class IN ('11', '12') AND language = 'Hindi'
            GROUP BY class, subject, stream
            ORDER BY class, subject
        """)
        for row in cursor.fetchall():
            print(f"Class: {row['class']} | Subject: {row['subject']} | Stream: {row['stream']} | Count: {row['count']}")

        print("\n--- Check subjects table for Hindi medium subjects of Class 11 & 12 ---")
        cursor.execute("""
            SELECT s.id, s.subject_name, s.slug, s.language, s.stream_id, cs.class_id
            FROM subjects s
            LEFT JOIN class_subjects cs ON s.id = cs.subject_id
            WHERE cs.class_id IN (11, 12) AND s.language = 'Hindi'
        """)
        subjects = cursor.fetchall()
        print(f"Found {len(subjects)} subjects in subjects table for Class 11/12 (Hindi):")
        for s in subjects:
            print(f"  Class: {s['class_id']} | ID: {s['id']} | Name: {s['subject_name']} | Slug: {s['slug']} | Language: {s['language']} | Stream ID: {s['stream_id']}")

        print("\n--- Check general subjects table overview ---")
        cursor.execute("SELECT language, COUNT(*) as count FROM subjects GROUP BY language")
        for row in cursor.fetchall():
            print(f"Language: {row['language']} | Subject Count: {row['count']}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
