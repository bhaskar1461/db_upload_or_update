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
    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    cursor = conn.cursor()
    
    try:
        print("Starting deletion process for subject ID 443...")
        
        # 1. Delete notes in ai_notes_new
        cursor.execute("SELECT id FROM chapters WHERE subject_id = 443")
        ch_ids = [row[0] for row in cursor.fetchall()]
        
        notes_deleted = 0
        if ch_ids:
            format_strings = ','.join(['%s'] * len(ch_ids))
            cursor.execute(f"DELETE FROM ai_notes_new WHERE chapter_id IN ({format_strings})", tuple(ch_ids))
            notes_deleted = cursor.rowcount
            print(f"  Deleted {notes_deleted} notes from ai_notes_new.")
        else:
            print("  No chapters found, so no notes to delete from ai_notes_new.")
            
        # 2. Delete chapters
        cursor.execute("DELETE FROM chapters WHERE subject_id = 443")
        chapters_deleted = cursor.rowcount
        print(f"  Deleted {chapters_deleted} chapters from chapters table.")
        
        # 3. Delete class-subject link
        cursor.execute("DELETE FROM class_subjects WHERE subject_id = 443")
        links_deleted = cursor.rowcount
        print(f"  Deleted {links_deleted} links from class_subjects table.")
        
        # 4. Delete subject
        cursor.execute("DELETE FROM subjects WHERE id = 443")
        subjects_deleted = cursor.rowcount
        print(f"  Deleted {subjects_deleted} subject from subjects table.")
        
        conn.commit()
        print("\nAll changes successfully committed to the database.")
    except Exception as e:
        conn.rollback()
        print(f"Error during deletion (changes rolled back): {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
