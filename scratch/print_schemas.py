import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def main():
    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    cursor = conn.cursor()
    
    for tbl in ['ai_notes', 'ai_notes_new', 'chapters', 'subjects']:
        print(f"\n=== SCHEMA FOR TABLE: {tbl} ===")
        cursor.execute(f"DESCRIBE {tbl}")
        for col in cursor.fetchall():
            print(f"  Field: {col[0]:<20} | Type: {col[1]:<20} | Null: {col[2]:<5} | Key: {col[3]}")
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
