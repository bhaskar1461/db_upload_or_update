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
cursor.execute("DELETE FROM ai_notes_new WHERE class = '6' AND full_notes IS NULL")
print(f"Deleted {cursor.rowcount} NULL rows from Class 6.")
conn.commit()
cursor.close()
conn.close()
