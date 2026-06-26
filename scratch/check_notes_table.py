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

# Get notes table structure
cursor.execute("DESCRIBE `notes`")
columns = [col[0] for col in cursor.fetchall()]
print(f"Columns in `notes`: {columns}")

# Get row count
cursor.execute("SELECT COUNT(*) FROM `notes`")
print(f"Total rows in `notes`: {cursor.fetchone()[0]}")

# Check for empty topics in `notes`
if 'topic' in columns:
    cursor.execute("SELECT COUNT(*) FROM `notes` WHERE topic IS NULL OR topic = '' OR topic = 'NULL'")
    print(f"Empty topics in `notes`: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT id, class, subject, topic, full_notes FROM `notes` WHERE topic IS NULL OR topic = '' OR topic = 'NULL' LIMIT 10")
    for r in cursor.fetchall():
        print(f"  ID: {r[0]} | Class: {r[1]} | Subject: {r[2]} | Topic: {repr(r[3])} | FullNotes: {r[4]}")
else:
    print("No 'topic' column in `notes`")

# Also search for '17801667' in `notes` table
for col in columns:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM `notes` WHERE `{col}` LIKE '%17801667%'")
        cnt = cursor.fetchone()[0]
        if cnt > 0:
            print(f"Found {cnt} occurrences of '17801667' in notes column `{col}`")
            cursor.execute(f"SELECT id, `{col}` FROM `notes` WHERE `{col}` LIKE '%17801667%' LIMIT 5")
            for r in cursor.fetchall():
                print(f"  ID: {r[0]} | `{col}`: {r[1]}")
    except Exception as e:
        pass

cursor.close()
conn.close()
