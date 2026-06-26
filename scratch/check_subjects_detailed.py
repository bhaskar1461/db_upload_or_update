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
    
    print("=== SEARCHING SUBJECTS TABLE ===")
    cursor.execute("""
        SELECT * FROM subjects 
        WHERE subject_name LIKE '%English%' 
           OR subject_name LIKE '%Hindi%' 
           OR subject_name LIKE '%Physical Education%' 
           OR subject_name LIKE '%Home Science%'
           OR subject_name LIKE '%Home science%'
        ORDER BY subject_name, language
    """)
    for r in cursor.fetchall():
        print(f"ID: {r['id']:<4} | Name: {r['subject_name']:<30} | Lang: {r['language']:<10} | Board: {r['board']:<10} | Stream: {r['stream_id']}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
