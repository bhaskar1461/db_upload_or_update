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
    cursor = conn.cursor()
    
    target_ids = (448, 449, 450)
    
    try:
        print(f"Starting deletion process for subject IDs {target_ids}...")
        
        for sid in target_ids:
            # 1. Delete class-subject link
            cursor.execute("DELETE FROM class_subjects WHERE subject_id = %s", (sid,))
            links_deleted = cursor.rowcount
            
            # 2. Delete subject
            cursor.execute("DELETE FROM subjects WHERE id = %s", (sid,))
            subjects_deleted = cursor.rowcount
            
            print(f"  Subject ID {sid}: Deleted {links_deleted} class links, {subjects_deleted} subject records.")
        
        conn.commit()
        print("\nAll deletions successfully committed to the database.")
    except Exception as e:
        conn.rollback()
        print(f"Error during deletion: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
