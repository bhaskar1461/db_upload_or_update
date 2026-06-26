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

# ---- EXACT DUPLICATES ----
print("=" * 100)
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

# ---- NEAR-DUPLICATES ----
print("\n" + "=" * 100)
print("NEAR-DUPLICATES (same subject_name + language, more than 1 entry)")
print("=" * 100)
cursor.execute("""
    SELECT subject_name, language, 
           COUNT(*) as cnt, GROUP_CONCAT(id ORDER BY id) as ids,
           GROUP_CONCAT(DISTINCT stream_id ORDER BY stream_id) as stream_ids,
           GROUP_CONCAT(DISTINCT board ORDER BY board) as boards
    FROM subjects
    GROUP BY subject_name, language
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC, subject_name
""")
near_dups = cursor.fetchall()
if near_dups:
    print(f"Found {len(near_dups)} groups with same name+language:\n")
    for d in near_dups:
        print(f"  name={d['subject_name']:<35}, lang={d['language']:<8}, count={d['cnt']}, "
              f"stream_ids=[{d['stream_ids']}], boards=[{d['boards']}], IDs=[{d['ids']}]")
else:
    print("No near-duplicates found.")

# ---- CLASS 10 DUPLICATES (from what I saw earlier) ----
print("\n" + "=" * 100)
print("CLASS 10 SUBJECTS (checking duplicates there)")
print("=" * 100)
cursor.execute("""
    SELECT cs.class_id, s.id as subject_id, s.subject_name, s.language, s.stream_id,
           s.slug, s.board
    FROM class_subjects cs
    JOIN subjects s ON cs.subject_id = s.id
    WHERE cs.class_id = 10
    ORDER BY s.subject_name, s.language
""")
for r in cursor.fetchall():
    print(f"  class={r['class_id']}, subj_id={r['subject_id']}, name={r['subject_name']:<35}, "
          f"lang={r['language']:<8}, stream={r['stream_id']}, slug={r['slug']}")

# ---- CLASS_SUBJECTS duplicates ----
print("\n" + "=" * 100)
print("CLASS_SUBJECTS DUPLICATES (same class_id + subject_id)")
print("=" * 100)
cursor.execute("""
    SELECT class_id, subject_id, COUNT(*) as cnt
    FROM class_subjects
    GROUP BY class_id, subject_id
    HAVING COUNT(*) > 1
""")
cs_dups = cursor.fetchall()
if cs_dups:
    print(f"Found {len(cs_dups)} duplicate class_subject mappings:")
    for d in cs_dups:
        print(f"  class_id={d['class_id']}, subject_id={d['subject_id']}, count={d['cnt']}")
else:
    print("No duplicate class_subjects mappings found.")

# ---- Duplicate subjects linked to same class ----
print("\n" + "=" * 100)
print("DUPLICATE SUBJECT NAMES PER CLASS (same class, same name+lang, different subject IDs)")
print("=" * 100)
cursor.execute("""
    SELECT cs.class_id, s.subject_name, s.language, s.stream_id,
           COUNT(*) as cnt, GROUP_CONCAT(s.id ORDER BY s.id) as subject_ids
    FROM class_subjects cs
    JOIN subjects s ON cs.subject_id = s.id
    GROUP BY cs.class_id, s.subject_name, s.language, s.stream_id
    HAVING COUNT(*) > 1
    ORDER BY cs.class_id, s.subject_name
""")
class_dups = cursor.fetchall()
if class_dups:
    print(f"Found {len(class_dups)} cases of duplicate subject names within a class:\n")
    for d in class_dups:
        print(f"  class={d['class_id']}, name={d['subject_name']:<35}, lang={d['language']:<8}, "
              f"stream={d['stream_id']}, count={d['cnt']}, subject_ids=[{d['subject_ids']}]")
else:
    print("No duplicate subject names within the same class.")

cursor.close()
conn.close()
