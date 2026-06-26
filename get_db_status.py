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
        # Get count of competitive notes class-wise
        cur.execute("""
            SELECT `class`, COUNT(*) as count 
            FROM ai_notes_new 
            WHERE `class` IN ('6', '7', '8', '9', '10') 
              AND subject LIKE '%(Competitive)%'
            GROUP BY `class`
            ORDER BY CAST(`class` AS UNSIGNED)
        """)
        rows_new = cur.fetchall()
        
        cur.execute("""
            SELECT `class`, COUNT(*) as count 
            FROM ai_notes 
            WHERE `class` IN ('6', '7', '8', '9', '10') 
              AND subject LIKE '%(Competitive)%'
            GROUP BY `class`
            ORDER BY CAST(`class` AS UNSIGNED)
        """)
        rows_old = cur.fetchall()

    conn.close()
    
    print("=== DATABASE COMPETITIVE NOTES COUNT ===")
    print("Table: ai_notes_new")
    total_new = 0
    for r in rows_new:
        print(f"  Class {r['class']}: {r['count']} notes")
        total_new += r['count']
    print(f"  Total: {total_new} notes")
    
    print("\nTable: ai_notes")
    total_old = 0
    for r in rows_old:
        print(f"  Class {r['class']}: {r['count']} notes")
        total_old += r['count']
    print(f"  Total: {total_old} notes")

except Exception as e:
    print("Error:", e)
