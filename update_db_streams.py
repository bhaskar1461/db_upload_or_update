import os
import pymysql
from pathlib import Path
from dotenv import load_dotenv

# Load .env
dotenv_path = Path(r"C:\Users\bhask\Desktop\Study Materials\.env")
load_dotenv(dotenv_path)

DB_HOSTS = os.environ.get("MARIADB_HOST", "srv1645.hstgr.io").split(",")
DB_USER = os.environ.get("MARIADB_USER")
DB_PASSWORD = os.environ.get("MARIADB_PASSWORD")
DB_NAME = os.environ.get("MARIADB_DATABASE")

def get_db():
    for host in DB_HOSTS:
        host = host.strip()
        try:
            return pymysql.connect(
                host=host, user=DB_USER, password=DB_PASSWORD,
                database=DB_NAME, connect_timeout=5
            )
        except Exception:
            continue
    raise RuntimeError("Could not connect to MariaDB")

try:
    conn = get_db()
    print("Connected to DB successfully.")
    
    with conn.cursor() as cur:
        # Update ai_notes_new
        affected_new = cur.execute("""
            UPDATE ai_notes_new 
            SET stream = 'General' 
            WHERE `class` IN ('6', '7', '8', '9', '10') 
              AND subject LIKE '%(Competitive)%'
        """)
        print(f"Updated {affected_new} rows in ai_notes_new")
        
        # Update ai_notes
        affected_old = cur.execute("""
            UPDATE ai_notes 
            SET stream = 'General' 
            WHERE `class` IN ('6', '7', '8', '9', '10') 
              AND subject LIKE '%(Competitive)%'
        """)
        print(f"Updated {affected_old} rows in ai_notes")
        
    conn.commit()
    conn.close()
    print("Database updates committed successfully.")
except Exception as e:
    print("Error during update:", e)
