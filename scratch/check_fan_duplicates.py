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

cursor.execute("SELECT id, class, subject, topic, language, created_at, full_notes FROM ai_notes_new WHERE topic LIKE '%Talking Fan%'")
rows = cursor.fetchall()
for r in rows:
    print(f"ID: {r[0]} | Class: {r[1]} | Subject: {r[2]} | Topic: {r[3]} | Lang: {r[4]} | CreatedAt: {r[5]} | FullNotes: {r[6]}")

cursor.close()
conn.close()
