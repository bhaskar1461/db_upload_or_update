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

# Standardize to a single format
target_subject = "हिंदी (Hindi)"

cursor.execute("UPDATE ai_notes_new SET subject = %s WHERE subject IN ('Hindi', 'हिन्दी (Hindi)')", (target_subject,))
print(f"Updated {cursor.rowcount} rows to use consistent '{target_subject}' spelling.")

conn.commit()
cursor.close()
conn.close()
