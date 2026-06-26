import os
import re
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

cursor.execute("SELECT id, short_notes FROM ai_notes_new WHERE topic IS NULL OR topic = ''")
rows = cursor.fetchall()
updates = 0

for row_id, notes in rows:
    if not notes: continue
    
    # Extract "Chapter: X" from the first line
    # e.g. "# Class 8th science / Textbooks - Chapter: Chapter 2"
    match = re.search(r"Chapter:\s*(.+?)(?:\r?\n|$)", notes)
    if match:
        new_topic = match.group(1).strip()
        cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (new_topic, row_id))
        updates += 1
        print(f"Updated ID {row_id} topic to '{new_topic}'")

print(f"\nFixed {updates} empty topics.")
conn.commit()
cursor.close()
conn.close()
