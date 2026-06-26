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
    
    print("=== INSPECTING CLASS 11 HINDI (LANG: ENGLISH) UNKNOWN TOPIC NOTES ===")
    cursor.execute("""
        SELECT id, subject, topic, short_notes 
        FROM ai_notes 
        WHERE class = '11' AND subject = 'Hindi' AND language = 'English' AND topic = 'UnknownTopic'
        LIMIT 5
    """)
    for r in cursor.fetchall():
        print(f"ID: {r['id']} | Subject: {r['subject']} | Topic: {r['topic']}")
        print(f"Content Sample:\n{r['short_notes'][:400]}")
        print("-" * 60)
        
    print("\n=== INSPECTING CLASS 11 HINDI (LANG: HINDI) UNKNOWN TOPIC NOTES ===")
    cursor.execute("""
        SELECT id, subject, topic, short_notes 
        FROM ai_notes 
        WHERE class = '11' AND subject = 'Hindi' AND language = 'Hindi' AND topic = 'UnknownTopic'
        LIMIT 5
    """)
    for r in cursor.fetchall():
        print(f"ID: {r['id']} | Subject: {r['subject']} | Topic: {r['topic']}")
        print(f"Content Sample:\n{r['short_notes'][:400]}")
        print("-" * 60)
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
