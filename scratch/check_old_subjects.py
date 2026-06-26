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
        
        print("=== UNIQUE CLASSES/SUBJECTS IN ai_notes FOR HINDI LANGUAGE ===")
        cursor.execute("""
            SELECT class, subject, COUNT(*) as count
            FROM ai_notes
            WHERE language = 'Hindi' AND class IN ('11', '12')
            GROUP BY class, subject
            ORDER BY class, subject
        """)
        for r in cursor.fetchall():
            print(f"Class: {r['class']} | Subject: {r['subject']} | Count: {r['count']}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
