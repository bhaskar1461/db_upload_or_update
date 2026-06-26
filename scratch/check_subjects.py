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
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        print("=== ALL HINDI SUBJECTS IN DB ===")
        cursor.execute("SELECT * FROM subjects WHERE LOWER(language) = 'hindi'")
        for row in cursor.fetchall():
            print(f"ID: {row['id']} | Name: {row['subject_name']} | Slug: {row['slug']} | Language: {row['language']} | Stream ID: {row['stream_id']}")

        print("\n=== CLASS SUBJECT MAPPINGS FOR HINDI SUBJECTS ===")
        cursor.execute("""
            SELECT cs.class_id, s.id as subject_id, s.subject_name, s.slug, s.language, s.stream_id
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            WHERE LOWER(s.language) = 'hindi'
            ORDER BY cs.class_id, s.id
        """)
        for row in cursor.fetchall():
            print(f"Class: {row['class_id']} | Subject ID: {row['subject_id']} | Name: {row['subject_name']} | Slug: {row['slug']} | Language: {row['language']} | Stream ID: {row['stream_id']}")

        print("\n=== CLASS SUBJECT MAPPINGS FOR CLASS 11 & 12 (ANY LANGUAGE) ===")
        cursor.execute("""
            SELECT cs.class_id, s.id as subject_id, s.subject_name, s.slug, s.language, s.stream_id
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            WHERE cs.class_id IN (11, 12)
            ORDER BY cs.class_id, s.language, s.id
        """)
        for row in cursor.fetchall():
            print(f"Class: {row['class_id']} | Lang: {row['language']} | Subject ID: {row['subject_id']} | Name: {row['subject_name']} | Slug: {row['slug']} | Stream ID: {row['stream_id']}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
