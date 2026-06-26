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
    
    cursor.execute("""
        SELECT s.id, s.subject_name, s.language, s.board, cs.class_id
        FROM subjects s
        LEFT JOIN class_subjects cs ON s.id = cs.subject_id
        WHERE s.subject_name LIKE '%English%'
        ORDER BY s.language, cs.class_id
    """)
    for r in cursor.fetchall():
        print(f"ID: {r['id']:<4} | Name: {r['subject_name']:<30} | Lang: {r['language']:<8} | Board: {r['board']:<6} | Class: {r['class_id']}")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
