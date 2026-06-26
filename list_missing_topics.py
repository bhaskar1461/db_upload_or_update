import os
import mysql.connector
from dotenv import load_dotenv
import re

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()
cursor.execute("SELECT class, subject, short_notes FROM ai_notes_new WHERE topic IS NULL OR topic = ''")
rows = cursor.fetchall()

empty_map = {}
for c, s, notes in rows:
    key = f"Class {c} {s}"
    if key not in empty_map: empty_map[key] = []
    if notes:
        match = re.search(r"Chapter:\s*(.+?)(?:\r?\n|$)", notes)
        if match:
            empty_map[key].append(match.group(1).strip())

for k, v in empty_map.items():
    print(f"{k}: {len(v)} missing -> {v}")

cursor.close()
conn.close()
