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
    
    # 1. Get all Class 11/12 subjects
    cursor.execute("""
        SELECT cs.class_id, s.id as subject_id, s.subject_name, s.language, s.board, s.stream_id
        FROM class_subjects cs
        JOIN subjects s ON cs.subject_id = s.id
        WHERE cs.class_id IN (11, 12) AND s.language IN ('hindi', 'english')
        ORDER BY cs.class_id, s.language, s.subject_name
    """)
    subjects = cursor.fetchall()
    
    print("==========================================================================")
    print("CLASS 11/12 SUBJECTS & CHAPTERS & MAPPED NOTES STATUS")
    print("==========================================================================")
    for s in subjects:
        class_id = s['class_id']
        subj_id = s['subject_id']
        subj_name = s['subject_name']
        lang = s['language']
        
        # Check chapters count
        cursor.execute("SELECT COUNT(*) as cnt FROM chapters WHERE subject_id = %s", (subj_id,))
        ch_count = cursor.fetchone()['cnt']
        
        # Check notes in ai_notes_new matching this subject (case insensitive comparison for subject/language)
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM ai_notes_new 
            WHERE class = %s AND LOWER(subject) = LOWER(%s) AND LOWER(language) = LOWER(%s)
        """, (str(class_id), subj_name, lang))
        new_cnt = cursor.fetchone()['cnt']

        # Check notes in ai_notes (old) matching this subject
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM ai_notes 
            WHERE class = %s AND LOWER(subject) = LOWER(%s) AND LOWER(language) = LOWER(%s)
        """, (str(class_id), subj_name, lang))
        old_cnt = cursor.fetchone()['cnt']
        
        print(f"Class {class_id} | {lang:<7} | ID: {subj_id:<4} | Subj: {subj_name:<30} | Chs: {ch_count:<3} | NewNotes: {new_cnt:<4} | OldNotes: {old_cnt:<4}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
