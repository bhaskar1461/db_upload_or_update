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
                database=DB_NAME, connect_timeout=5,
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception:
            continue
    raise RuntimeError("Could not connect to MariaDB")

try:
    conn = get_db()
    with conn.cursor() as cur:
        for table in ["ai_notes_new", "ai_notes", "chapters", "subjects", "class_subjects"]:
            print(f"\nSchema of Table: {table}")
            cur.execute(f"DESCRIBE {table}")
            columns = cur.fetchall()
            for col in columns:
                print(f"  {col['Field']}: {col['Type']}")
    conn.close()
except Exception as e:
    print("Error:", e)
