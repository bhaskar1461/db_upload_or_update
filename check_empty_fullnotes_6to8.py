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

for cls in ['6', '7', '8']:
    cursor.execute("SELECT id, subject, topic FROM ai_notes_new WHERE class = %s AND (full_notes IS NULL OR full_notes = '')", (cls,))
    rows = cursor.fetchall()
    print(f"\n=== Class {cls}: {len(rows)} empty full_notes ===")
    for r in rows:
        print(f"  ID={r[0]}  {r[1]} - {r[2]}")

cursor.close()
conn.close()
