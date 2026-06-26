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

for table in ['ai_notes', 'ai_notes_new']:
    cursor.execute(f"DESCRIBE `{table}`")
    cols = cursor.fetchall()
    print(f"\nTable: {table}")
    for col in cols:
        print(f"  Column: {col[0]} | Type: {col[1]} | Nullable: {col[2]} | Key: {col[3]} | Default: {col[4]}")
        
cursor.close()
conn.close()
