import os
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

cursor.execute("SELECT id, class, subject, topic, short_notes FROM ai_notes_new WHERE topic IS NULL OR topic = '' LIMIT 20")
rows = cursor.fetchall()
print(f"Found {len(rows)} sample empty topics:")
for r in rows:
    print(f"ID: {r[0]} | Class: {r[1]} | Subject: {r[2]} | Topic: '{r[3]}' | ShortNotes (first 60 chars): {r[4][:60] if r[4] else 'NULL'}")

cursor.execute("SELECT COUNT(*) FROM ai_notes_new WHERE topic IS NULL OR topic = ''")
count = cursor.fetchone()[0]
print(f"\nTotal rows with empty topics: {count}")

cursor.close()
conn.close()
