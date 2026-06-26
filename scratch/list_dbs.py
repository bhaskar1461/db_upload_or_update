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

# Get all databases
cursor.execute("SHOW DATABASES")
dbs = [d[0] for d in cursor.fetchall()]
print(f"Databases: {dbs}")

for db in dbs:
    if db in ('information_schema', 'performance_schema', 'mysql', 'sys'):
        continue
    print(f"\nDatabase: {db}")
    # Switch to db
    cursor.execute(f"USE `{db}`")
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"  Tables: {tables}")
    for table in tables:
        # Check if table has a column full_notes
        try:
            cursor.execute(f"DESCRIBE `{table}`")
            cols = [c[0] for c in cursor.fetchall()]
            if 'full_notes' in cols:
                # Count total rows
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                total = cursor.fetchone()[0]
                # Count matching our screenshot filename pattern
                cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE full_notes LIKE '%17801667%'")
                match_cnt = cursor.fetchone()[0]
                # Count where topic is empty or null
                cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE topic IS NULL OR topic = '' OR topic = 'NULL'")
                empty_topic_cnt = cursor.fetchone()[0]
                print(f"    Table: {table} | Total: {total} | 17801667 Match: {match_cnt} | Empty Topic: {empty_topic_cnt}")
                if match_cnt > 0 or empty_topic_cnt > 0:
                    cursor.execute(f"SELECT id, class, subject, topic, full_notes FROM `{table}` WHERE topic IS NULL OR topic = '' OR topic = 'NULL' OR full_notes LIKE '%17801667%' LIMIT 5")
                    for r in cursor.fetchall():
                        print(f"      ID: {r[0]} | Class: {r[1]} | Subject: {r[2]} | Topic: {repr(r[3])} | FullNotes: {r[4]}")
        except Exception as e:
            print(f"    Error on {table}: {e}")

cursor.close()
conn.close()
