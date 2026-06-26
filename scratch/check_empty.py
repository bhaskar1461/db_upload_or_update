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

# Check tables in database
cursor.execute("SHOW TABLES")
tables = [t[0] for t in cursor.fetchall()]
print(f"Tables in DB: {tables}")

for table in ['ai_notes', 'ai_notes_new']:
    if table in tables:
        print(f"\nChecking table: {table}")
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  Total records: {cursor.fetchone()[0]}")
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE topic IS NULL OR topic = '' OR topic = 'NULL'")
        print(f"  Empty/NULL topics count: {cursor.fetchone()[0]}")
        
        cursor.execute(f"SELECT id, class, subject, topic, short_notes, full_notes, book_url FROM {table} WHERE topic IS NULL OR topic = '' OR topic = 'NULL' LIMIT 5")
        rows = cursor.fetchall()
        for r in rows:
            print(f"    ID: {r[0]} | Class: {r[1]} | Subject: {r[2]} | Topic: '{r[3]}' | ShortNotes (first 40 chars): {r[4][:40] if r[4] else 'None'} | FullNotes: {r[5]} | BookURL: {r[6]}")

        # Check book_url count for class 9
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE class = '9'")
        total_c9 = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE class = '9' AND (book_url IS NULL OR book_url = '' OR book_url = 'NULL')")
        empty_book_c9 = cursor.fetchone()[0]
        print(f"  Class 9 total: {total_c9}, Class 9 with empty book_url: {empty_book_c9}")
        
        if total_c9 > 0:
            cursor.execute(f"SELECT id, subject, topic, book_url FROM {table} WHERE class = '9' LIMIT 5")
            c9_rows = cursor.fetchall()
            print("  Sample Class 9 records:")
            for r in c9_rows:
                print(f"    ID: {r[0]} | Subject: {r[1]} | Topic: {r[2]} | BookURL: {r[3]}")

cursor.close()
conn.close()
