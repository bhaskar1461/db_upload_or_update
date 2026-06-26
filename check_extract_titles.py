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

# Get the rows we just mapped (we can filter by the topics we mapped)
cursor.execute("SELECT id, class, subject, topic, short_notes FROM ai_notes_new WHERE id IN (2747, 2735, 3005, 3050) LIMIT 10")
rows = cursor.fetchall()
for r in rows:
    row_id, cls, subj, topic, notes = r
    print(f"ID: {row_id} | Class: {cls} | Subject: {subj} | Current Name: {topic}")
    print(notes[:400].replace('\n', ' '))
    print("-" * 80)

cursor.close()
conn.close()
