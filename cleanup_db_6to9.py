import os
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def clean_database():
    print("🧹 Connecting to Database...")
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()
    
    print("🗑️ Deleting all recently uploaded chapters for Classes 6, 7, 8, and 9...")
    query = "DELETE FROM ai_notes_new WHERE class IN ('6', '7', '8', '9')"
    cursor.execute(query)
    
    deleted_rows = cursor.rowcount
    conn.commit()
    
    print(f"✅ Successfully deleted {deleted_rows} rows from the database!")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    clean_database()
