import os
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

# Get all tables
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]

for table in ['ai_notes', 'ai_notes_new']:
    if table in tables:
        print(f"\nChecking table {table}:")
        # Let's check lengths
        cursor.execute(f"SELECT id, class, subject, topic, LENGTH(topic) FROM {table} WHERE LENGTH(TRIM(topic)) <= 3 OR topic IS NULL")
        rows = cursor.fetchall()
        print(f"  Found {len(rows)} topics with length <= 3 or NULL")
        for r in rows[:20]:
            print(f"    ID: {r[0]} | Class: {r[1]} | Subject: {r[2]} | Topic: {repr(r[3])} | Length: {r[4]}")
            
cursor.close()
conn.close()
