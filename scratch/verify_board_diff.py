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

# Check board of each duplicate subject ID
print("BOARD INFO FOR DUPLICATE SUBJECT IDS")
print("=" * 100)
ids_to_check = [140, 165, 142, 166, 33, 144, 32, 145, 146, 164, 1, 88]
cursor.execute(f"SELECT * FROM subjects WHERE id IN ({','.join(str(i) for i in ids_to_check)})")
for r in cursor.fetchall():
    print(f"  ID={r['id']:>4}, name={r['subject_name']:<25}, board={r['board']:<6}, "
          f"lang={r['language']:<8}, stream_id={r['stream_id']}")

# The REAL question: what does the class_subjects mapping look like for these?
print("\n\nCLASS_SUBJECTS MAPPING FOR THESE IDS")
print("=" * 100)
cursor.execute(f"""
    SELECT cs.class_id, cs.subject_id, s.subject_name, s.board, s.language
    FROM class_subjects cs
    JOIN subjects s ON cs.subject_id = s.id
    WHERE cs.subject_id IN ({','.join(str(i) for i in ids_to_check)})
    ORDER BY cs.class_id, s.subject_name
""")
for r in cursor.fetchall():
    print(f"  class={r['class_id']}, subj_id={r['subject_id']}, name={r['subject_name']:<25}, "
          f"board={r['board']:<6}, lang={r['language']}")

# Now check: how many TOTAL exact same (name+slug+board+lang+stream_id) exist?
print("\n\nARE THE CLASS 10 DUPS REALLY SAME BOARD?")
print("=" * 100)
pairs = [(140, 165), (142, 166), (33, 144), (32, 145), (146, 164)]
for a, b in pairs:
    cursor.execute("SELECT * FROM subjects WHERE id IN (%s, %s)", (a, b))
    rows = cursor.fetchall()
    same_board = rows[0]['board'] == rows[1]['board']
    same_lang = rows[0]['language'] == rows[1]['language']
    same_stream = rows[0]['stream_id'] == rows[1]['stream_id']
    print(f"  IDs {a} vs {b}: name={rows[0]['subject_name']}")
    print(f"    Board: {rows[0]['board']} vs {rows[1]['board']} {'✅ SAME' if same_board else '❌ DIFFERENT'}")
    print(f"    Lang:  {rows[0]['language']} vs {rows[1]['language']} {'✅ SAME' if same_lang else '❌ DIFFERENT'}")
    print(f"    Stream:{rows[0]['stream_id']} vs {rows[1]['stream_id']} {'✅ SAME' if same_stream else '❌ DIFFERENT'}")

cursor.close()
conn.close()
