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
    
    # Delete On Killing a Tree
    query = "DELETE FROM ai_notes_new WHERE topic LIKE '%Killing a Tree%'"
    cursor.execute(query)
    
    print(f"Deleted {cursor.rowcount} rows.")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_db()
