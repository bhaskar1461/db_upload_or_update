import os
import sys
import mysql.connector
import subprocess
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def main():
    print("Connecting to database...")
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()
    
    # Check current Class 9 count
    cursor.execute("SELECT COUNT(*) FROM ai_notes_new WHERE class = '9'")
    current_cnt = cursor.fetchone()[0]
    print(f"Current Class 9 records in ai_notes_new: {current_cnt}")
    
    # Delete Class 9 records
    print("Deleting all Class 9 records in ai_notes_new...")
    cursor.execute("DELETE FROM ai_notes_new WHERE class = '9'")
    deleted = cursor.rowcount
    conn.commit()
    print(f"Deleted {deleted} records from database.")
    
    cursor.close()
    conn.close()
    
    # Run the uploader for class 9
    print("Launching http_uploader_6to9.py for Class 9...")
    cmd = [sys.executable, "http_uploader_6to9.py", "--classes", "9", "--threads", "8"]
    result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, encoding='utf-8')
    print("\nUploader stdout:")
    print(result.stdout)
    if result.stderr:
        print("\nUploader stderr:")
        print(result.stderr)
        
if __name__ == "__main__":
    main()
