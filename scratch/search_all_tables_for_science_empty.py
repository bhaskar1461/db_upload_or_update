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

for table in tables:
    try:
        cursor.execute(f"DESCRIBE `{table}`")
        cols = [c[0] for c in cursor.fetchall()]
        if 'subject' in cols and 'class' in cols:
            # Let's search for science and class 6-9
            cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE class IN ('6', '7', '8', '9') AND (subject LIKE '%science%' OR subject LIKE '%Science%')")
            cnt = cursor.fetchone()[0]
            if cnt > 0:
                print(f"Table `{table}` has {cnt} rows matching class 6-9 and subject science")
                # Now find if any has empty/NULL topic or similar column
                topic_col = 'topic' if 'topic' in cols else (cols[5] if len(cols) > 5 else cols[0])
                cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE class IN ('6', '7', '8', '9') AND (subject LIKE '%science%' OR subject LIKE '%Science%') AND (`{topic_col}` IS NULL OR `{topic_col}` = '' OR `{topic_col}` = 'NULL')")
                empty_cnt = cursor.fetchone()[0]
                print(f"  Empty '{topic_col}' column count: {empty_cnt}")
                if empty_cnt > 0:
                    cursor.execute(f"SELECT id, class, subject, `{topic_col}` FROM `{table}` WHERE class IN ('6', '7', '8', '9') AND (subject LIKE '%science%' OR subject LIKE '%Science%') AND (`{topic_col}` IS NULL OR `{topic_col}` = '' OR `{topic_col}` = 'NULL') LIMIT 5")
                    for r in cursor.fetchall():
                        print(f"    Row: {r}")
    except Exception as e:
        print(f"Error checking table {table}: {e}")

cursor.close()
conn.close()
