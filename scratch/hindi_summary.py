import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor(dictionary=True)

# Quick summary of which Hindi 11/12 subjects have NO chapters
cursor.execute("""
    SELECT cs.class_id, s.id as subject_id, s.subject_name, s.language, s.stream_id,
           (SELECT COUNT(*) FROM chapters WHERE subject_id = s.id) as chapter_count,
           (SELECT COUNT(*) FROM ai_notes_new WHERE chapter_id IN 
               (SELECT id FROM chapters WHERE subject_id = s.id)) as note_count
    FROM class_subjects cs
    JOIN subjects s ON cs.subject_id = s.id
    WHERE cs.class_id IN (11, 12) AND s.language = 'hindi'
    ORDER BY cs.class_id, s.subject_name
""")

print("SUMMARY: Class 11/12 Hindi Subjects - Chapters & Notes Status")
print("=" * 110)
print(f"{'Class':<6} {'Subject':<30} {'ID':<6} {'Stream':<8} {'Chapters':<10} {'Notes':<8} {'Status'}")
print("-" * 110)

missing_chapters = []
for r in cursor.fetchall():
    status = "✅" if r['chapter_count'] > 0 else "❌ MISSING CHAPTERS"
    if r['chapter_count'] == 0:
        missing_chapters.append(r)
    print(f"{r['class_id']:<6} {r['subject_name']:<30} {r['subject_id']:<6} {r['stream_id']:<8} "
          f"{r['chapter_count']:<10} {r['note_count']:<8} {status}")

if missing_chapters:
    print(f"\n\n⚠️  {len(missing_chapters)} SUBJECTS HAVE NO CHAPTERS:")
    for m in missing_chapters:
        print(f"  Class {m['class_id']} - {m['subject_name']} (ID={m['subject_id']})")
    
    # Check if ai_notes (old table) has data for these
    print("\n  Checking ai_notes (old table) for these subjects...")
    for m in missing_chapters:
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM ai_notes
            WHERE `class` = %s AND subject = %s AND language = 'Hindi'
        """, (str(m['class_id']), m['subject_name']))
        old_count = cursor.fetchone()['cnt']
        print(f"    Class {m['class_id']} - {m['subject_name']}: {old_count} notes in ai_notes (old)")

# Check case sensitivity issue
print("\n\nCASE SENSITIVITY CHECK (language column)")
print("=" * 110)
cursor.execute("SELECT DISTINCT language FROM subjects ORDER BY language")
print("Subjects table languages:", [r['language'] for r in cursor.fetchall()])

cursor.execute("SELECT DISTINCT language FROM ai_notes_new ORDER BY language")
print("ai_notes_new languages:", [r['language'] for r in cursor.fetchall()])

cursor.execute("SELECT DISTINCT language FROM ai_notes ORDER BY language")
print("ai_notes languages:", [r['language'] for r in cursor.fetchall()])

cursor.execute("SELECT DISTINCT language FROM chapters ORDER BY language")
print("chapters languages:", [r['language'] for r in cursor.fetchall()])

cursor.close()
conn.close()
