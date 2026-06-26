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
        SELECT COUNT(*) as total,
               SUM(CASE WHEN full_notes IS NULL OR full_notes = '' THEN 1 ELSE 0 END) as empty_full_notes
        FROM ai_notes
        WHERE class IN ('11', '12')
    """)
    res = cursor.fetchone()
    print(f"Class 11/12 in ai_notes: Total notes = {res['total']}, Empty full_notes = {res['empty_full_notes']}")
    
    cursor.execute("""
        SELECT id, subject, topic, full_notes 
        FROM ai_notes
        WHERE class IN ('11', '12') AND full_notes IS NOT NULL AND full_notes != ''
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print(f"Sample of non-empty full_notes:")
    for r in rows:
        print(f"  ID: {r['id']} | Subj: {r['subject']} | Topic: {r['topic']} | Full notes length: {len(r['full_notes'])}")
        print(f"  Snippet: {r['full_notes'][:200]}")
        print("-" * 60)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
