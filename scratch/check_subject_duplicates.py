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

# ---- 1. ALL subjects ----
print("=" * 100)
print("1. ALL 160 SUBJECTS (sorted by subject_name, language, stream_id)")
print("=" * 100)
cursor.execute("SELECT * FROM subjects ORDER BY subject_name, language, stream_id, id")
all_subjects = cursor.fetchall()
for r in all_subjects:
    print(f"  ID={r['id']:>4}, name={r['subject_name']:<40}, slug={r['slug']:<40}, "
          f"board={r['board']:<6}, lang={r['language']:<8}, stream_id={r['stream_id']}")

# ---- 2. Exact duplicates (same name+slug+board+language+stream_id) ----
print("\n" + "=" * 100)
print("2. EXACT DUPLICATES (same subject_name + slug + board + language + stream_id)")
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

# ---- 3. Near-duplicates (same name+language, different stream/board) ----
print("\n" + "=" * 100)
print("3. NEAR-DUPLICATES (same subject_name + language, potentially different stream/board)")
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

# ---- 4. Check streams table for context ----
print("\n" + "=" * 100)
print("4. STREAMS TABLE (to understand stream_id mapping)")
print("=" * 100)
cursor.execute("SELECT * FROM streams ORDER BY id")
for r in cursor.fetchall():
    print(f"  {r}")

# ---- 5. class_subjects table ----
print("\n" + "=" * 100)
print("5. CLASS_SUBJECTS TABLE SCHEMA + COUNT")
print("=" * 100)
cursor.execute("DESCRIBE class_subjects")
for col in cursor.fetchall():
    print(f"  {col}")
cursor.execute("SELECT COUNT(*) as cnt FROM class_subjects")
print(f"\n  Total rows: {cursor.fetchone()['cnt']}")

# ---- 6. Check which subject IDs are referenced in class_subjects ----
print("\n" + "=" * 100)
print("6. SUBJECTS REFERENCED IN CLASS_SUBJECTS (with class info)")
print("=" * 100)
cursor.execute("""
    SELECT cs.*, s.subject_name, s.language, s.stream_id
    FROM class_subjects cs
    JOIN subjects s ON cs.subject_id = s.id
    ORDER BY cs.class_id, s.subject_name
""")
cs_rows = cursor.fetchall()
print(f"Total class_subjects rows: {len(cs_rows)}\n")
for r in cs_rows:
    print(f"  class_id={r.get('class_id', 'N/A')}, subject_id={r.get('subject_id', 'N/A')}, "
          f"name={r.get('subject_name', 'N/A')}, lang={r.get('language', 'N/A')}, stream_id={r.get('stream_id', 'N/A')}")

# ---- 7. Orphan subjects (in subjects but not in class_subjects) ----
print("\n" + "=" * 100)
print("7. ORPHAN SUBJECTS (in subjects table but NOT linked in class_subjects)")
print("=" * 100)
cursor.execute("""
    SELECT s.*
    FROM subjects s
    LEFT JOIN class_subjects cs ON s.id = cs.subject_id
    WHERE cs.subject_id IS NULL
    ORDER BY s.id
""")
orphans = cursor.fetchall()
if orphans:
    print(f"Found {len(orphans)} orphan subjects:\n")
    for r in orphans:
        print(f"  ID={r['id']:>4}, name={r['subject_name']:<40}, lang={r['language']:<8}, "
              f"stream_id={r['stream_id']}, board={r['board']}")
else:
    print("No orphan subjects found.")

cursor.close()
conn.close()
