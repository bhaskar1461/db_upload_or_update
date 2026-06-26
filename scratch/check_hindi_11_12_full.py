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

# Get all Class 11/12 Hindi subject IDs
cursor.execute("""
    SELECT cs.class_id, s.id as subject_id, s.subject_name, s.language, s.board, s.stream_id
    FROM class_subjects cs
    JOIN subjects s ON cs.subject_id = s.id
    WHERE cs.class_id IN (11, 12) AND s.language = 'hindi'
    ORDER BY cs.class_id, s.subject_name
""")
hindi_subjects = cursor.fetchall()

print("CLASS 11/12 HINDI SUBJECTS - CHAPTERS & NOTES STATUS")
print("=" * 120)

for subj in hindi_subjects:
    sid = subj['subject_id']
    cursor.execute("""
        SELECT c.id, c.name, c.language,
               (SELECT COUNT(*) FROM ai_notes_new WHERE chapter_id = c.id) as note_count
        FROM chapters c
        WHERE c.subject_id = %s
        ORDER BY c.id
    """, (sid,))
    chapters = cursor.fetchall()
    
    total_notes = sum(ch['note_count'] for ch in chapters)
    
    status = "✅" if chapters else "❌ NO CHAPTERS"
    notes_status = f"({total_notes} notes)" if total_notes > 0 else "(0 notes)"
    
    print(f"\nClass {subj['class_id']} | {subj['subject_name']:<25} | ID={sid} | "
          f"board={subj['board']} | stream={subj['stream_id']} | "
          f"{len(chapters)} chapters {notes_status} {status}")
    
    if chapters:
        for ch in chapters[:5]:  # Show first 5
            note_flag = f" [{ch['note_count']} notes]" if ch['note_count'] > 0 else ""
            print(f"    [{ch['id']:>5}] {ch['name'][:60]:<60} lang={ch['language']}{note_flag}")
        if len(chapters) > 5:
            print(f"    ... and {len(chapters) - 5} more chapters")

# Also check ai_notes_new directly for Class 11/12 Hindi
print("\n\n" + "=" * 120)
print("AI_NOTES_NEW TABLE - Class 11/12 Hindi entries (direct check)")
print("=" * 120)
cursor.execute("""
    SELECT `class`, subject, language, COUNT(*) as cnt
    FROM ai_notes_new
    WHERE `class` IN ('11', '12') AND language = 'hindi'
    GROUP BY `class`, subject, language
    ORDER BY `class`, subject
""")
notes = cursor.fetchall()
if notes:
    for n in notes:
        print(f"  class={n['class']}, subject={n['subject']:<30}, lang={n['language']}, count={n['cnt']}")
else:
    print("  NO entries found for Class 11/12 Hindi in ai_notes_new!")

# Check ai_notes (old table) too
print("\n\nAI_NOTES TABLE (old) - Class 11/12 Hindi entries")
print("=" * 120)
try:
    cursor.execute("""
        SELECT `class`, subject, language, COUNT(*) as cnt
        FROM ai_notes
        WHERE `class` IN ('11', '12') AND language = 'hindi'
        GROUP BY `class`, subject, language
        ORDER BY `class`, subject
    """)
    notes_old = cursor.fetchall()
    if notes_old:
        for n in notes_old:
            print(f"  class={n['class']}, subject={n['subject']:<30}, lang={n['language']}, count={n['cnt']}")
    else:
        print("  NO entries found for Class 11/12 Hindi in ai_notes!")
except Exception as e:
    print(f"  Error: {e}")

cursor.close()
conn.close()
