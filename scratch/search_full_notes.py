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

print("Querying ai_notes_new for Class 7/8 Science records:")
cursor.execute("SELECT id, class, subject, topic, full_notes, book_url FROM ai_notes_new WHERE class IN ('7', '8') AND subject LIKE '%science%' LIMIT 30")
for r in cursor.fetchall():
    print(f"  ID: {r[0]} | Class: {r[1]} | Subject: {r[2]} | Topic: {repr(r[3])} | FullNotes: {r[4]} | BookURL: {r[5]}")

cursor.close()
conn.close()
