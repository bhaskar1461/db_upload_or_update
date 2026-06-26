import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor(dictionary=True)

print("=" * 80)
print("SUBJECTS TABLE SCHEMA")
print("=" * 80)
cursor.execute("DESCRIBE subjects")
for col in cursor.fetchall():
    print(f"  {col}")

print("\n" + "=" * 80)
print("TOTAL ROW COUNT")
print("=" * 80)
cursor.execute("SELECT COUNT(*) as cnt FROM subjects")
print(f"  Total rows: {cursor.fetchone()['cnt']}")

print("\n" + "=" * 80)
print("FIRST 10 ROWS (raw)")
print("=" * 80)
cursor.execute("SELECT * FROM subjects LIMIT 10")
for r in cursor.fetchall():
    print(f"  {r}")

cursor.close()
conn.close()
