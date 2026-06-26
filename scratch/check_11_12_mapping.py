import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

# Fix Windows terminal printing for Hindi/Unicode text
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
        
        print("=================================================================")
        print("1. SUBJECTS AND CHAPTERS FOR CLASS 11 & 12 (ENGLISH & HINDI)")
        print("=================================================================")
        
        cursor.execute("""
            SELECT s.id as subject_id, s.subject_name, s.slug, s.language, s.stream_id, cs.class_id,
                   (SELECT COUNT(*) FROM chapters ch WHERE ch.subject_id = s.id) as chapter_count
            FROM subjects s
            JOIN class_subjects cs ON s.id = cs.subject_id
            WHERE cs.class_id IN (11, 12) AND s.language IN ('hindi', 'english')
            ORDER BY cs.class_id, s.language, s.subject_name
        """)
        subjects = cursor.fetchall()
        print(f"Total subjects found: {len(subjects)}")
        for s in subjects:
            print(f"Class: {s['class_id']} | Lang: {s['language']:<7} | SubID: {s['subject_id']:<4} | Name: {s['subject_name']:<30} | Stream: {s['stream_id']} | Chapters: {s['chapter_count']}")
            
        print("\n=================================================================")
        print("2. ENTRIES IN AI_NOTES (OLD) FOR CLASS 11 & 12")
        print("=================================================================")
        
        cursor.execute("""
            SELECT class, subject, language, COALESCE(stream, '') as stream, COUNT(*) as cnt, COUNT(DISTINCT topic) as distinct_topics
            FROM ai_notes
            WHERE class IN ('11', '12')
            GROUP BY class, subject, language, stream
            ORDER BY class, language, subject
        """)
        old_notes = cursor.fetchall()
        for n in old_notes:
            stream_str = n['stream'] if n['stream'] else ''
            print(f"Class: {n['class']:<2} | Lang: {n['language']:<7} | Sub: {n['subject']:<30} | Stream: {stream_str:<10} | Rows: {n['cnt']:<5} | Unique Topics: {n['distinct_topics']}")

        print("\n=================================================================")
        print("3. ENTRIES IN AI_NOTES_NEW (NEW) FOR CLASS 11 & 12")
        print("=================================================================")
        
        cursor.execute("""
            SELECT class, subject, language, COALESCE(stream, '') as stream, COUNT(*) as cnt, COUNT(DISTINCT topic) as distinct_topics
            FROM ai_notes_new
            WHERE class IN ('11', '12')
            GROUP BY class, subject, language, stream
            ORDER BY class, language, subject
        """)
        new_notes = cursor.fetchall()
        for n in new_notes:
            stream_str = n['stream'] if n['stream'] else ''
            print(f"Class: {n['class']:<2} | Lang: {n['language']:<7} | Sub: {n['subject']:<30} | Stream: {stream_str:<10} | Rows: {n['cnt']:<5} | Unique Topics: {n['distinct_topics']}")

        cursor.close()
        conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
