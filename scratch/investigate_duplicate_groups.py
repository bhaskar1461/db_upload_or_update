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
        
        # We'll investigate 'Class: 11 | Subject: गणित (Mathematics) | Topic: त्रिकोणमीतीय फलन | Lang: Hindi'
        query = """
        SELECT id, class, subject, topic, language, stream, short_notes, full_notes, book_url
        FROM ai_notes_new
        WHERE class = '11' AND subject = 'गणित (Mathematics)' AND topic = 'त्रिकोणमीतीय फलन' AND language = 'Hindi'
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print("Investigating group:")
        print("Class 11 | गणित (Mathematics) | त्रिकोणमीतीय फलन | Hindi\n")
        for r in rows:
            print(f" - ID: {r['id']}")
            print(f"   Stream: {r['stream']}")
            print(f"   Language: {r['language']}")
            print(f"   short_notes length: {len(r['short_notes']) if r['short_notes'] else 0}")
            print(f"   full_notes length: {len(r['full_notes']) if r['full_notes'] else 0}")
            print(f"   book_url: {r['book_url']}")
            print()
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
