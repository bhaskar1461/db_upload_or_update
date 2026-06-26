import os
import sys
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

# Fix Windows terminal printing for Hindi/Unicode text
sys.stdout.reconfigure(encoding='utf-8')

# Load database credentials from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def main():
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = db.cursor()
        print("Connected to DB successfully.")

        # Define mapping of subjects to streams for Class 11
        subject_stream_map = {
            'Accountancy': 'Commerce',
            'Business Studies': 'Commerce',
            'Physics': 'Science',
            'Chemistry': 'Science',
            'Biology': 'Science',
            'Mathematics': 'Science'
        }

        total_updated = 0

        for subject, stream in subject_stream_map.items():
            print(f"Updating stream to '{stream}' for subject '{subject}' in Class 11 where stream is NULL...")
            
            # We match both English subject name and possible variations
            update_query = """
                UPDATE ai_notes 
                SET stream = %s 
                WHERE class = '11' 
                  AND (subject = %s OR subject LIKE %s)
                  AND stream IS NULL
            """
            like_pattern = f"%{subject}%"
            cursor.execute(update_query, (stream, subject, like_pattern))
            rows_affected = cursor.rowcount
            total_updated += rows_affected
            print(f"  -> Updated {rows_affected} rows.")

        db.commit()
        print(f"Done! Successfully updated a total of {total_updated} rows.")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    main()
