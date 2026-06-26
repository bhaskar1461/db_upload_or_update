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

dup_pairs = [
    (10, "English", 140, 165),
    (10, "Hindi", 142, 166),
    (10, "Mathematics", 33, 144),
    (10, "Science", 32, 145),
    (10, "Social Science", 146, 164),
    (5, "Mathematics", 1, 88),
]

for cls, subj_name, id_a, id_b in dup_pairs:
    print(f"\n{'='*100}")
    print(f"Class {cls} - {subj_name}: Subject ID {id_a} vs {id_b}")
    print(f"{'='*100}")
    
    for sid in [id_a, id_b]:
        cursor.execute("""
            SELECT c.id, c.name, c.language,
                   (SELECT COUNT(*) FROM ai_notes_new WHERE chapter_id = c.id) as note_count
            FROM chapters c
            WHERE c.subject_id = %s
            ORDER BY c.id
        """, (sid,))
        chapters = cursor.fetchall()
        print(f"\n  Subject ID {sid}: {len(chapters)} chapters")
        for ch in chapters:
            note_flag = f" *** {ch['note_count']} NOTES ***" if ch['note_count'] > 0 else ""
            print(f"    [{ch['id']:>5}] {ch['name']:<60} lang={ch['language']}{note_flag}")
    
    # Check overlapping chapter names
    cursor.execute("""
        SELECT a.name, a.id as id_a, b.id as id_b
        FROM chapters a
        JOIN chapters b ON LOWER(TRIM(a.name)) = LOWER(TRIM(b.name))
        WHERE a.subject_id = %s AND b.subject_id = %s
    """, (id_a, id_b))
    overlaps = cursor.fetchall()
    if overlaps:
        print(f"\n  ⚠️  OVERLAPPING chapter names ({len(overlaps)}):")
        for o in overlaps:
            print(f"    - '{o['name']}' (IDs: {o['id_a']} vs {o['id_b']})")
    else:
        print(f"\n  ✅ No overlapping chapter names - chapters are completely separate")

cursor.close()
conn.close()
