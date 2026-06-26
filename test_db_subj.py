import os
import sys
import mysql.connector
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env')
db = mysql.connector.connect(
    host=os.getenv('DB_HOST','127.0.0.1'),
    user=os.getenv('DB_USER','root'),
    password=os.getenv('DB_PASSWORD',''),
    database=os.getenv('DB_NAME','u826463665_student')
)
cursor = db.cursor()
cursor.execute("SELECT DISTINCT class, subject FROM ai_notes WHERE class IN ('6', '11') LIMIT 20")
rows = cursor.fetchall()
for r in rows:
    print(f"Class: {r[0]}, Subject: {r[1]}")
