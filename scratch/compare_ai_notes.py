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
    
    print("=== AI_NOTES (OLD) DISTINCT SUBJECTS, LANGUAGES, STREAMS FOR CLASS 11 ===")
    cursor.execute("""
        SELECT subject, language, COALESCE(stream, '') as stream, COUNT(*) as cnt
        FROM ai_notes
        WHERE class = '11'
        GROUP BY subject, language, stream
        ORDER BY language, subject
    """)
    for r in cursor.fetchall():
        print(f"Sub: {r['subject']:<30} | Lang: {r['language']:<10} | Stream: {r['stream']:<15} | Count: {r['cnt']}")

    print("\n=== AI_NOTES (OLD) DISTINCT SUBJECTS, LANGUAGES, STREAMS FOR CLASS 12 ===")
    cursor.execute("""
        SELECT subject, language, COALESCE(stream, '') as stream, COUNT(*) as cnt
        FROM ai_notes
        WHERE class = '12'
        GROUP BY subject, language, stream
        ORDER BY language, subject
    """)
    for r in cursor.fetchall():
        print(f"Sub: {r['subject']:<30} | Lang: {r['language']:<10} | Stream: {r['stream']:<15} | Count: {r['cnt']}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
