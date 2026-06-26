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

for cls in ['6', '7', '8', '9']:
    cursor.execute(f"SELECT subject, COUNT(*) FROM ai_notes_new WHERE class='{cls}' AND subject LIKE '%Hindi%' GROUP BY subject")
    rows = cursor.fetchall()
    print(f'Class {cls} Hindi Subjects:')
    for r in rows:
        print('  ', r)

cursor.close()
conn.close()
