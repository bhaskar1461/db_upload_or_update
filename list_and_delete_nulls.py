import os, re, mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()
cursor.execute("SELECT id, class, subject, topic FROM ai_notes_new WHERE class IN ('6','7','8') AND full_notes IS NULL")
rows = cursor.fetchall()
print("Current NULL rows in Classes 6-8:")
for r in rows:
    print(r)
print("Total:", len(rows))

# Now delete them
cursor.execute("DELETE FROM ai_notes_new WHERE class IN ('6','7','8') AND full_notes IS NULL")
print(f"\nDeleted {cursor.rowcount} NULL rows.")
conn.commit()
cursor.close()
conn.close()
