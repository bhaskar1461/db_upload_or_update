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
    cursor = conn.cursor(dictionary=True)
    
    print("=== INSPECTING SUBJECT ID 443 ===")
    cursor.execute("SELECT * FROM subjects WHERE id = 443")
    subj = cursor.fetchone()
    if subj:
        print(f"Subject: {subj}")
    else:
        print("Subject ID 443 does not exist in subjects table.")
        
    cursor.execute("SELECT * FROM class_subjects WHERE subject_id = 443")
    class_links = cursor.fetchall()
    print(f"Class links in class_subjects: {class_links}")
    
    cursor.execute("SELECT id, name, language FROM chapters WHERE subject_id = 443")
    chapters = cursor.fetchall()
    print(f"Chapters count in chapters: {len(chapters)}")
    for ch in chapters[:5]:
        print(f"  Chapter ID: {ch['id']} | Name: {ch['name']}")
    if len(chapters) > 5:
        print(f"  ... and {len(chapters) - 5} more chapters")
        
    if chapters:
        ch_ids = [ch['id'] for ch in chapters]
        format_strings = ','.join(['%s'] * len(ch_ids))
        cursor.execute(f"SELECT COUNT(*) as count FROM ai_notes_new WHERE chapter_id IN ({format_strings})", tuple(ch_ids))
        notes_cnt = cursor.fetchone()['count']
        print(f"Linked notes in ai_notes_new: {notes_cnt}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
