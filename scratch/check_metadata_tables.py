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
        
        print("=== STREAMS ===")
        cursor.execute("SELECT * FROM streams")
        for r in cursor.fetchall():
            print(r)
            
        print("\n=== CLASSES ===")
        cursor.execute("SELECT * FROM classes")
        for r in cursor.fetchall():
            print(r)

        print("\n=== LANGUAGES ===")
        cursor.execute("SELECT * FROM languages")
        for r in cursor.fetchall():
            print(r)

        print("\n=== SAMPLE SUBJECTS ===")
        cursor.execute("SELECT * FROM subjects LIMIT 10")
        for r in cursor.fetchall():
            print(r)
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
