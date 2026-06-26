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
        cur.execute("""
            SELECT s.id, s.subject_name, s.slug, s.stream_id, cs.class_id 
            FROM subjects s
            JOIN class_subjects cs ON cs.subject_id = s.id
            WHERE s.subject_name LIKE '%(Competitive)%'
            ORDER BY cs.class_id, s.id
        """)
        rows = cur.fetchall()
        for r in rows:
            print(f"Class: {r['class_id']:<2} | ID: {r['id']:<4} | Name: {r['subject_name']:<30} | Stream ID: {r['stream_id']}")
    conn.close()
except Exception as e:
    print("Error:", e)
