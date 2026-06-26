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

# ---- EXACT DUPLICATES only ----
print("EXACT DUPLICATES (same subject_name + slug + board + language + stream_id)")
print("=" * 100)
cursor.execute("""
    SELECT subject_name, slug, board, language, stream_id, 
           COUNT(*) as cnt, GROUP_CONCAT(id ORDER BY id) as ids
    FROM subjects
    GROUP BY subject_name, slug, board, language, stream_id
    HAVING COUNT(*) > 1
    ORDER BY subject_name, language, stream_id
""")
exact_dups = cursor.fetchall()
if exact_dups:
    print(f"Found {len(exact_dups)} duplicate groups:\n")
    for d in exact_dups:
        print(f"  name={d['subject_name']:<35}, slug={d['slug']:<35}, board={d['board']:<6}, "
              f"lang={d['language']:<8}, stream_id={d['stream_id']}, count={d['cnt']}, IDs=[{d['ids']}]")
else:
    print("No exact duplicates found.")

# ---- Check which duplicate IDs have chapters linked ----
print("\n\nCHAPTERS LINKED TO DUPLICATE SUBJECT IDS")
print("=" * 100)

# Class 10 duplicates
dup_pairs = [
    (10, "English", [140, 165]),
    (10, "Hindi", [142, 166]),
    (10, "Mathematics", [33, 144]),
    (10, "Science", [32, 145]),
    (10, "Social Science", [146, 164]),
    (5, "Mathematics", [1, 88]),
]

for cls, name, ids in dup_pairs:
    print(f"\n  Class {cls} - {name} (subject IDs: {ids}):")
    for sid in ids:
        cursor.execute("SELECT COUNT(*) as cnt FROM chapters WHERE subject_id = %s", (sid,))
        ch_count = cursor.fetchone()['cnt']
        cursor.execute("SELECT COUNT(*) as cnt FROM ai_notes_new WHERE chapter_id IN (SELECT id FROM chapters WHERE subject_id = %s)", (sid,))
        note_count = cursor.fetchone()['cnt']
        print(f"    Subject ID {sid}: {ch_count} chapters, {note_count} notes")

cursor.close()
conn.close()
