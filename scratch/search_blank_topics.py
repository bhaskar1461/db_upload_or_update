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

print("All Class 7 science records in ai_notes:")
cursor.execute("SELECT id, topic, full_notes FROM ai_notes WHERE class = '7' AND subject = 'science'")
rows = cursor.fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(f"  ID: {r[0]} | Topic: {repr(r[1])} | FullNotes: {r[2]}")

cursor.close()
conn.close()
