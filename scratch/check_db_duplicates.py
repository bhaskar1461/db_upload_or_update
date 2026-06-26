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

# Find duplicates in ai_notes_new
query = """
    SELECT class, subject, topic, language, COUNT(*) as cnt, MIN(id) as min_id, MAX(id) as max_id
    FROM ai_notes_new
    GROUP BY class, subject, topic, language
    HAVING cnt > 1
"""
cursor.execute(query)
rows = cursor.fetchall()
print(f"Found {len(rows)} duplicated keys in ai_notes_new.")
for r in rows[:20]:
    print(f"  Class: {r[0]} | Subject: {r[1]} | Topic: {r[2]} | Lang: {r[3]} | Count: {r[4]} | IDs: {r[5]} to {r[6]}")

cursor.close()
conn.close()
