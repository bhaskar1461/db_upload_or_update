import json, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

import mysql.connector
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor()

# Load the maths chapter from Class 6th English
data = json.loads(open("rag_cache_Class_6th_English.json", encoding='utf-8').read())
key = "Maths||Maths||Chapter 2: Whole Numbers"
notes = data[key]

subject = "Maths"
topic   = "Chapter 2: Whole Numbers"
lang    = "English"
cls     = "6"

# Duplicate check
cursor.execute(
    "SELECT id FROM ai_notes WHERE class=%s AND subject=%s AND topic=%s AND language=%s",
    (cls, subject, topic, lang)
)
if cursor.fetchone():
    print("Already exists. Skipping.")
else:
    cursor.execute(
        """INSERT INTO ai_notes
           (language, board, class, subject, topic, short_notes, full_notes, book_url, generated_by, created_at, updated_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())""",
        (lang, "CBSE", cls, subject, topic, notes, "", "", "AI")
    )
    conn.commit()
    print(f"SUCCESS! Maths chapter inserted. Row ID: {cursor.lastrowid}")
    print(f"Topic: {topic}")
    print(f"Notes preview: {notes[:200]}")

cursor.close()
conn.close()
