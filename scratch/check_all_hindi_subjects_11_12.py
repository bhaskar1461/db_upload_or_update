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
        
        print("=== UNIQUE SUBJECTS FOR CLASS 11 HINDI IN BOTH TABLES ===")
        cursor.execute("""
            SELECT subject, 'ai_notes_new' as tbl, COUNT(*) as cnt
            FROM ai_notes_new
            WHERE class = '11' AND language = 'Hindi'
            GROUP BY subject
            UNION
            SELECT subject, 'ai_notes' as tbl, COUNT(*) as cnt
            FROM ai_notes
            WHERE class = '11' AND language = 'Hindi'
            GROUP BY subject
            ORDER BY subject, tbl
        """)
        for r in cursor.fetchall():
            print(f"Subject: {r['subject']:<40s} | Table: {r['tbl']:<15s} | Count: {r['cnt']}")

        print("\n=== UNIQUE SUBJECTS FOR CLASS 12 HINDI IN BOTH TABLES ===")
        cursor.execute("""
            SELECT subject, 'ai_notes_new' as tbl, COUNT(*) as cnt
            FROM ai_notes_new
            WHERE class = '12' AND language = 'Hindi'
            GROUP BY subject
            UNION
            SELECT subject, 'ai_notes' as tbl, COUNT(*) as cnt
            FROM ai_notes
            WHERE class = '12' AND language = 'Hindi'
            GROUP BY subject
            ORDER BY subject, tbl
        """)
        for r in cursor.fetchall():
            print(f"Subject: {r['subject']:<40s} | Table: {r['tbl']:<15s} | Count: {r['cnt']}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
