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

print("CHAPTERS TABLE SCHEMA:")
cursor.execute("DESCRIBE chapters")
for col in cursor.fetchall():
    print(f"  {col}")

print("\nSAMPLE CHAPTERS ROW:")
cursor.execute("SELECT * FROM chapters LIMIT 3")
for r in cursor.fetchall():
    print(f"  {r}")

print("\nAI_NOTES_NEW TABLE SCHEMA:")
cursor.execute("DESCRIBE ai_notes_new")
for col in cursor.fetchall():
    print(f"  {col}")

cursor.close()
conn.close()
