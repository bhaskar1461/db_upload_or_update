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
        
        # Check duplicates in ai_notes_new
        query = """
        SELECT class, subject, topic, stream, COUNT(*) as cnt
        FROM ai_notes_new
        GROUP BY class, subject, topic, stream
        HAVING cnt > 1
        ORDER BY cnt DESC
        """
        cursor.execute(query)
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("No duplicates found in ai_notes_new table based on class, subject, topic, stream.")
        else:
            print(f"Found {len(duplicates)} duplicate groups in ai_notes_new table:")
            for d in duplicates:
                print(f"Count: {d['cnt']} | Class: {d['class']} | Subject: {d['subject']} | Topic: {d['topic']} | Stream: {d['stream']}")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
