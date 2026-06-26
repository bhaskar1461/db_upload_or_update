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
        
        print("=== CHECKING FOR HINDI CHAPTERS FOR LANGUAGES/PE/HOME SCIENCE ===")
        # Let's see what chapters exist with language = 'hindi' and what subject_ids they point to.
        # We can join with subjects table to see what those subjects are.
        cursor.execute("""
            SELECT s.id as subject_id, s.subject_name, s.language as subject_language,
                   c.name as chapter_name, c.language as chapter_language
            FROM chapters c
            JOIN subjects s ON c.subject_id = s.id
            WHERE c.language = 'hindi' 
              AND (s.subject_name LIKE '%English%' 
                OR s.subject_name LIKE '%Hindi%' 
                OR s.subject_name LIKE '%Physical Education%' 
                OR s.subject_name LIKE '%Home%')
            ORDER BY s.subject_name, c.name
        """)
        rows = cursor.fetchall()
        print(f"Found {len(rows)} chapters:")
        for r in rows[:30]:
            print(f"Subject: {r['subject_name']} (ID: {r['subject_id']}, Lang: {r['subject_language']}) | Chapter: {r['chapter_name']}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
