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

search_str = "1780166717451"

print(f"Searching for string '{search_str}' in all tables...")
for table in tables:
    try:
        cursor.execute(f"DESCRIBE `{table}`")
        columns = [col[0] for col in cursor.fetchall()]
        
        # We only search text/varchar/char columns or just search everything using CONCAT
        select_parts = []
        for col in columns:
            select_parts.append(f"IFNULL(CAST(`{col}` AS CHAR), '')")
        
        concat_query = f"SELECT * FROM `{table}` WHERE CONCAT({', '.join(select_parts)}) LIKE %s"
        cursor.execute(concat_query, (f"%{search_str}%",))
        rows = cursor.fetchall()
        if rows:
            print(f"\nFound match in table: {table} ({len(rows)} rows)")
            for r in rows:
                print(f"  Columns: {columns}")
                print(f"  Row: {r}")
    except Exception as e:
        print(f"Error searching table {table}: {e}")

cursor.close()
conn.close()
