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

cursor.execute("SELECT id, topic, short_notes FROM ai_notes_new WHERE short_notes LIKE '%Chapter 13%' AND subject = 'हिंदी (Hindi)' AND class = '8'")
for row in cursor.fetchall():
    print('ID:', row[0], 'Topic:', row[1])
    print(row[2][:500].replace('\n', ' '))
    print('---')

conn.close()
