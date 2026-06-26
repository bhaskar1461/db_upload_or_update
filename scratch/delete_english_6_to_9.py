import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(r"C:\Users\bhask\Desktop\Archive\New folder\.env")
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def delete_english_notes():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # 1. Inspect before deletion
        print("Checking counts BEFORE deletion:")
        for table in ["ai_notes", "ai_notes_new"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE class IN ('6', '7', '8', '9') AND language = 'English'")
            cnt = cursor.fetchone()[0]
            print(f"- {table}: {cnt} English rows for Classes 6-9")

        print("\nProceeding with deletion...")
        
        # 2. Perform deletion on ai_notes
        cursor.execute("DELETE FROM ai_notes WHERE class IN ('6', '7', '8', '9') AND language = 'English'")
        deleted_ai_notes = cursor.rowcount
        
        # 3. Perform deletion on ai_notes_new
        cursor.execute("DELETE FROM ai_notes_new WHERE class IN ('6', '7', '8', '9') AND language = 'English'")
        deleted_ai_notes_new = cursor.rowcount
        
        conn.commit()
        
        print(f"\nSuccessfully deleted:")
        print(f"- {deleted_ai_notes} rows from ai_notes")
        print(f"- {deleted_ai_notes_new} rows from ai_notes_new")
        
        # 4. Inspect after deletion
        print("\nChecking counts AFTER deletion:")
        for table in ["ai_notes", "ai_notes_new"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE class IN ('6', '7', '8', '9') AND language = 'English'")
            cnt = cursor.fetchone()[0]
            print(f"- {table}: {cnt} English rows for Classes 6-9")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_english_notes()
