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

cursor.execute("SELECT id, short_notes FROM ai_notes_new WHERE class = '9' LIMIT 1")
r = cursor.fetchone()
if r:
    print(f"ID: {r[0]}")
    print(f"Raw type: {type(r[1])}")
    print(f"Raw value (first 300 chars):")
    print(r[1][:300])
    
cursor.close()
conn.close()
