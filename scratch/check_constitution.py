import os
import sys
import mysql.connector
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

cursor.execute("SELECT id, subject, topic, full_notes, book_url FROM ai_notes_new WHERE class = '9' AND topic LIKE '%संविधान%'")
rows = cursor.fetchall()
print(f"Found {len(rows)} records containing 'संविधान':")
for r in rows:
    print(f"  ID: {r[0]} | Subject: {r[1]} | Topic: {r[2]} | FullNotes: {r[3]} | BookURL: {r[4]}")

cursor.close()
conn.close()
