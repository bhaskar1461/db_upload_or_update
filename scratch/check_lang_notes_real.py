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
        
        print("=== CHECKING FOR REAL LANGUAGE/PE/HOME SCIENCE NOTES FOR CLASS 11/12 HINDI IN ai_notes ===")
        cursor.execute("""
            SELECT class, subject, topic, LEFT(short_notes, 100) as snippet
            FROM ai_notes
            WHERE class IN ('11', '12') 
              AND language = 'Hindi'
              AND (subject LIKE '%इंग्लिश%' OR subject LIKE '%English%' 
                OR subject LIKE '%हिन्दी%' OR subject LIKE '%Hindi%' 
                OR subject LIKE '%शारीरिक%' OR subject LIKE '%Physical%' 
                OR subject LIKE '%गृह%' OR subject LIKE '%Home%')
              AND topic != 'UnknownTopic'
            LIMIT 20
        """)
        rows = cursor.fetchall()
        print(f"Found {len(rows)} real notes:")
        for r in rows:
            print(f"Class: {r['class']} | Subject: {r['subject']} | Topic: {r['topic']} | Snippet: {r['snippet']}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
