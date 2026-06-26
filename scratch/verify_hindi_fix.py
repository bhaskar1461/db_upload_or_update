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
        cursor = conn.cursor(dictionary=True, buffered=True)
        print("=== VERIFYING DATABASE FIX FOR CLASS 11 & 12 HINDI MEDIUM ===")

        # 1. Check if Hindi subjects are mapped to class 11 and 12 in subjects and class_subjects table
        print("\n1. Verification: Hindi Subjects for Class 11 and 12 in DB:")
        print("-" * 60)
        cursor.execute("""
            SELECT cs.class_id, s.id, s.subject_name, s.language, s.stream_id
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            WHERE cs.class_id IN (11, 12) AND s.language = 'hindi'
            ORDER BY cs.class_id, s.subject_name
        """)
        hi_subjs = cursor.fetchall()
        print(f"Total Hindi subjects found for Class 11/12: {len(hi_subjs)}")
        for s in hi_subjs:
            print(f"  Class: {s['class_id']} | Subj ID: {s['id']:>3d} | Name: {s['subject_name']:<20s} | Stream: {s['stream_id']}")

        # 2. Check if Hindi chapters point to these subjects
        print("\n2. Verification: Chapters Count per Hindi Subject:")
        print("-" * 60)
        cursor.execute("""
            SELECT cs.class_id, s.id as subject_id, s.subject_name, COUNT(c.id) as chapters_count
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            LEFT JOIN chapters c ON c.subject_id = s.id AND c.language = 'hindi'
            WHERE cs.class_id IN (11, 12) AND s.language = 'hindi'
            GROUP BY cs.class_id, s.id, s.subject_name
            ORDER BY cs.class_id, s.subject_name
        """)
        for r in cursor.fetchall():
            print(f"  Class: {r['class_id']} | Subj ID: {r['subject_id']:>3d} | Name: {r['subject_name']:<20s} | Hindi Chapters: {r['chapters_count']}")

        # 3. Check for any remaining Hindi chapters under English subjects for Class 11/12
        print("\n3. Verification: Hindi Chapters remaining under English subjects for Class 11/12:")
        print("-" * 60)
        cursor.execute("""
            SELECT s.id as subject_id, s.subject_name, cs.class_id, COUNT(c.id) as hi_chapters
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            JOIN chapters c ON c.subject_id = s.id
            WHERE cs.class_id IN (11, 12) AND s.language = 'english' AND c.language = 'hindi'
            GROUP BY s.id, s.subject_name, cs.class_id
        """)
        leftover = cursor.fetchall()
        if leftover:
            for r in leftover:
                print(f"  Class: {r['class_id']} | Subj ID: {r['subject_id']:>3d} | Name: {r['subject_name']} | Leftover Hindi Chapters: {r['hi_chapters']}")
        else:
            print("  [SUCCESS] No leftover Hindi chapters found under English subjects!")

        # 4. Check subject names in ai_notes_new
        print("\n4. Verification: Unique subject names in ai_notes_new for Class 11/12 Hindi:")
        print("-" * 60)
        cursor.execute("""
            SELECT class, subject, COUNT(*) as cnt
            FROM ai_notes_new
            WHERE class IN ('11', '12') AND language = 'Hindi'
            GROUP BY class, subject
            ORDER BY class, subject
        """)
        for r in cursor.fetchall():
            print(f"  Class {r['class']} | Subject: '{r['subject']}' | Count: {r['cnt']}")

        # 5. Check subject names in ai_notes
        print("\n5. Verification: Unique subject names in ai_notes for Class 11/12 Hindi:")
        print("-" * 60)
        cursor.execute("""
            SELECT class, subject, COUNT(*) as cnt
            FROM ai_notes
            WHERE class IN ('11', '12') AND language = 'Hindi'
            GROUP BY class, subject
            ORDER BY class, subject
        """)
        for r in cursor.fetchall():
            print(f"  Class {r['class']} | Subject: '{r['subject']}' | Count: {r['cnt']}")

        # 6. Verify if we can successfully query subjects + chapters + notes for Class 11 Mathematics Hindi
        print("\n6. Verification: Mock Frontend Query (Class 11 Mathematics - Hindi):")
        print("-" * 60)
        # Find the subject ID
        cursor.execute("""
            SELECT s.id FROM subjects s
            JOIN class_subjects cs ON cs.subject_id = s.id
            WHERE cs.class_id = 11 AND s.subject_name = 'Mathematics' AND s.language = 'hindi'
        """)
        math_subj = cursor.fetchone()
        if math_subj:
            math_subj_id = math_subj['id']
            print(f"  Found Subject ID: {math_subj_id}")
            # Get chapters
            cursor.execute("""
                SELECT id, name FROM chapters
                WHERE subject_id = %s AND language = 'hindi'
            """, (math_subj_id,))
            chapters = cursor.fetchall()
            print(f"  Found {len(chapters)} Hindi chapters:")
            for ch in chapters[:3]:
                # Get notes for chapter
                cursor.execute("""
                    SELECT id, topic FROM ai_notes_new
                    WHERE chapter_id = %s
                """, (ch['id'],))
                note = cursor.fetchone()
                note_id = note['id'] if note else "None"
                note_topic = note['topic'] if note else "N/A"
                print(f"    - Chapter ID: {ch['id']} | Name: {ch['name']} | Note ID: {note_id} | Topic: {note_topic}")
        else:
            print("  [ERROR] Class 11 Hindi Mathematics subject not found!")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    main()
