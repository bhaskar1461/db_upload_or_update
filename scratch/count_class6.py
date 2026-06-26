import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(r"C:\Users\bhask\Desktop\Archive\New folder\.env")
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    for table in ["ai_notes", "ai_notes_new"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE class = '6' AND language = 'English'")
        cnt = cursor.fetchone()[0]
        print(f"Table {table}: {cnt} English Class 6 notes")
        
        if cnt > 0:
            cursor.execute(f"SELECT subject, topic FROM {table} WHERE class = '6' AND language = 'English' LIMIT 5")
            print("Sample notes:")
            for row in cursor.fetchall():
                print(f"  - {row[0]}: {row[1]}")
                
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
