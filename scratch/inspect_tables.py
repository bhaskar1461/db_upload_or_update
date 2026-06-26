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
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables in database:")
    for t in tables:
        print(f"- {t[0]}")
        
    for t in tables:
        t_name = t[0]
        if "ai_notes" in t_name:
            cursor.execute(f"SELECT COUNT(*) FROM {t_name}")
            cnt = cursor.fetchone()[0]
            print(f"Table {t_name} row count: {cnt}")
            
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
