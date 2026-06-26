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
cursor.execute("UPDATE ai_notes_new SET topic = 'Extra Material / Worksheet' WHERE topic = 'Unknown Chapter'")
print(f"Updated {cursor.rowcount} Unknown Chapters.")
conn.commit()
cursor.close()
conn.close()
