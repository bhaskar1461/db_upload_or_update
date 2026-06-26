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
cursor.execute("SELECT short_notes FROM ai_notes_new WHERE class='7' AND subject='Sanskrit' AND topic = '' LIMIT 2")
rows = cursor.fetchall()
for r in rows:
    print(r[0][:200].strip())
    print("---")
cursor.close()
conn.close()
