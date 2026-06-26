import os
import sys
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def main():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, class, subject, topic, stream FROM ai_notes_new WHERE full_notes IS NULL OR TRIM(full_notes) = '' OR LOWER(full_notes) = 'none'")
        rows = cursor.fetchall()
        
        print("Records missing full_notes:")
        for r in rows:
            print(f" - ID: {r['id']} | Class: {r['class']} | Subject: {r['subject']} | Topic: {r['topic']} | Stream: {r['stream']}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
