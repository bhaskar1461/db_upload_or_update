"""
test_single_upload.py
─────────────────────
Inserts EXACTLY 1 row from rag_cache_Class_6th_Hindi.json into the DB.
Use this to verify schema/connection before running the full upload.
"""
import json, os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

import mysql.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = int(os.getenv("DB_PORT", "3306"))
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME     = os.getenv("DB_NAME")

print(f"Connecting to {DB_HOST}:{DB_PORT} / {DB_NAME} as {DB_USER}...")

try:
    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME
    )
    print("Connection OK\n")
except mysql.connector.Error as e:
    print(f"Connection FAILED: {e}")
    sys.exit(1)

cursor = conn.cursor()

# ── Check actual columns in the table ────────────────────────────────────────
print("Checking ai_notes table schema...")
cursor.execute("DESCRIBE ai_notes")
cols = cursor.fetchall()
col_names = [c[0] for c in cols]
print(f"Columns: {col_names}\n")

# ── Pick the FIRST entry from 6th Hindi cache ─────────────────────────────────
cache_file = Path(__file__).parent / "rag_cache_Class_6th_Hindi.json"
data = json.loads(cache_file.read_text(encoding='utf-8'))
first_key, first_notes = next(iter(data.items()))

key_parts = first_key.split("||")
subject = key_parts[0] if len(key_parts) >= 1 else "Unknown"
topic   = key_parts[2] if len(key_parts) == 3 else key_parts[-1]

print(f"Test record:")
print(f"  Class   : 6")
print(f"  Language: Hindi")
print(f"  Subject : {subject}")
print(f"  Topic   : {topic}")
print(f"  Notes   : {first_notes[:80]}...\n")

# ── Check for duplicate ───────────────────────────────────────────────────────
cursor.execute(
    "SELECT id FROM ai_notes WHERE class=%s AND subject=%s AND topic=%s AND language=%s",
    ("6", subject, topic, "Hindi")
)
existing = cursor.fetchone()
if existing:
    print(f"Record already exists (id={existing[0]}). Delete it first to test insert.")
    cursor.close(); conn.close()
    sys.exit(0)

# ── Insert 1 row ──────────────────────────────────────────────────────────────
insert_sql = """
    INSERT INTO ai_notes
    (language, board, class, subject, topic, short_notes, full_notes, book_url, generated_by, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
"""
values = ("Hindi", "CBSE", "6", subject, topic, first_notes, "", "", "AI")

try:
    cursor.execute(insert_sql, values)
    conn.commit()
    print(f"SUCCESS! 1 row inserted. New row ID: {cursor.lastrowid}")
    print("\nCheck your DB — if it looks good, run: python upload_to_db.py")
except mysql.connector.Error as e:
    print(f"INSERT FAILED: {e}")

cursor.close()
conn.close()
