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
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT cs.class_id, s.id, s.subject_name, s.language, s.board, s.stream_id
            FROM class_subjects cs
            JOIN subjects s ON cs.subject_id = s.id
            WHERE s.subject_name IN ('English', 'Hindi', 'Physical Education', 'Home science', 'Home Science')
            ORDER BY s.subject_name, cs.class_id, s.id
        """)
        for r in cursor.fetchall():
            print(f"Class: {r['class_id']:<2} | Subject ID: {r['id']:<4} | Name: {r['subject_name']:<30s} | Lang: {r['language']:<8s} | Board: {r['board']:<8s} | Stream ID: {r['stream_id']}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
