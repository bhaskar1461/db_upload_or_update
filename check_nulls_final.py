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

cursor.execute("SELECT class, COUNT(*) FROM ai_notes_new WHERE class IN ('6', '7', '8') AND full_notes IS NULL GROUP BY class")
nulls = cursor.fetchall()

if not nulls:
    print('ZERO NULL rows found for Classes 6, 7, and 8! Everything is perfectly attached.')
else:
    for cls, count in nulls:
        print(f'Class {cls}: {count} NULL rows')

cursor.close()
conn.close()
