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

cursor.execute("SELECT id, subject, topic FROM ai_notes_new WHERE class = '9' AND (book_url IS NULL OR book_url = '' OR book_url = 'None')")
rows = cursor.fetchall()
print(f"Total Class 9 records with empty book_url: {len(rows)}")

# Let's count by subject
by_subject = {}
for r in rows:
    by_subject[r[1]] = by_subject.get(r[1], 0) + 1

print("\nBreakdown by Subject:")
for sub, cnt in by_subject.items():
    print(f"  {sub}: {cnt}")

print("\nSample 15 records:")
for r in rows[:15]:
    print(f"  ID: {r[0]} | Subject: {r[1]} | Topic: {r[2]}")

cursor.close()
conn.close()
