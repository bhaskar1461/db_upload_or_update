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

print("Searching for any tables with empty/NULL fields that look like the screenshot...")
for table in tables:
    try:
        cursor.execute(f"DESCRIBE `{table}`")
        cols = [c[0] for c in cursor.fetchall()]
        
        # Check if table has 'full_notes' or similar column
        has_full_notes = 'full_notes' in cols or any('note' in c.lower() for c in cols)
        has_topic = 'topic' in cols or any('chap' in c.lower() or 'title' in c.lower() for c in cols)
        
        if 'class' in cols and (has_full_notes or has_topic):
            # Count total
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            total = cursor.fetchone()[0]
            
            # Count where topic/chapter is empty
            topic_col = 'topic' if 'topic' in cols else [c for c in cols if 'chap' in c.lower() or 'title' in c.lower() or 'name' in c.lower()][0]
            
            cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE `{topic_col}` IS NULL OR `{topic_col}` = '' OR `{topic_col}` = 'NULL'")
            empty_cnt = cursor.fetchone()[0]
            
            print(f"Table `{table}` (total rows: {total}) | Column `{topic_col}` empty/NULL: {empty_cnt}")
            if empty_cnt > 0:
                # print some rows
                cursor.execute(f"SELECT id, class, `{topic_col}` FROM `{table}` WHERE `{topic_col}` IS NULL OR `{topic_col}` = '' OR `{topic_col}` = 'NULL' LIMIT 5")
                for r in cursor.fetchall():
                    print(f"  Row: {r}")
    except Exception as e:
        # print(f"Error checking {table}: {e}")
        pass

cursor.close()
conn.close()
