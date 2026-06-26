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
    cursor = conn.cursor(dictionary=True)
    
    print("=== SAMPLE CHAPTERS FOR PHYSICS CLASS 11 ENGLISH (ID: 45) ===")
    cursor.execute("SELECT * FROM chapters WHERE subject_id = 45 LIMIT 10")
    for r in cursor.fetchall():
        print(f"ID: {r['id']:<5} | Name: {r['name']:<50} | Lang: {r['language']}")
        
    print("\n=== SAMPLE CHAPTERS FOR PHYSICS CLASS 11 HINDI (ID: 419) ===")
    cursor.execute("SELECT * FROM chapters WHERE subject_id = 419 LIMIT 10")
    for r in cursor.fetchall():
        print(f"ID: {r['id']:<5} | Name: {r['name']:<50} | Lang: {r['language']}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
