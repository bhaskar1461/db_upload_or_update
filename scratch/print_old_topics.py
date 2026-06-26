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
    
    targets = [
        # (class_val, subject_name, language)
        ("11", "English", "English"),
        ("11", "Hindi", "English"),
        ("11", "English", "Hindi"),
        ("11", "Hindi", "Hindi"),
        ("11", "Physical Education", "Hindi"),
        ("12", "English", "Hindi"),
        ("12", "Hindi", "Hindi"),
        ("12", "Home Science", "Hindi"),
        ("12", "Physical Education", "Hindi"),
    ]
    
    for class_val, subject, language in targets:
        print(f"\n=======================================================")
        print(f"CLASS {class_val} | SUBJECT: {subject} | LANG: {language}")
        print(f"=======================================================")
        cursor.execute("""
            SELECT DISTINCT topic 
            FROM ai_notes 
            WHERE class = %s AND LOWER(subject) = LOWER(%s) AND LOWER(language) = LOWER(%s)
            ORDER BY topic
        """, (class_val, subject, language))
        topics = cursor.fetchall()
        print(f"Total topics: {len(topics)}")
        for idx, t in enumerate(topics[:15]):
            print(f"  {idx+1}. {t['topic']}")
        if len(topics) > 15:
            print(f"  ... and {len(topics) - 15} more topics")
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
