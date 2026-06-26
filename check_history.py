import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = db.cursor()
cursor.execute("SELECT topic FROM ai_notes_new WHERE class = '12' AND stream = 'Humanities' AND language = 'Hindi' AND subject LIKE '%History%'")
rows = cursor.fetchall()
for r in rows:
    print(f"Chapter: {r[0]}")
