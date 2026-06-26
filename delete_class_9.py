import os
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def fix_db():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()
    
    query = "DELETE FROM ai_notes_new WHERE class = '9'"
    cursor.execute(query)
    
    deleted_rows = cursor.rowcount
    conn.commit()
    
    print(f"✅ Successfully deleted {deleted_rows} Class 9 rows from the database.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_db()
