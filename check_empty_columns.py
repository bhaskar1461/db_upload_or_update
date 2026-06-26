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

# Check for empty short_notes
cursor.execute("SELECT class, COUNT(*) FROM ai_notes_new WHERE short_notes IS NULL OR short_notes = '' OR short_notes = '[]' GROUP BY class")
empty_short = cursor.fetchall()
print('Empty short_notes:', empty_short)

# Check for empty book_url
cursor.execute("SELECT class, COUNT(*) FROM ai_notes_new WHERE book_url IS NULL OR book_url = '' GROUP BY class")
empty_books = cursor.fetchall()
print('Empty book_url:', empty_books)

# Check for empty full_notes
cursor.execute("SELECT class, COUNT(*) FROM ai_notes_new WHERE full_notes IS NULL GROUP BY class")
empty_full = cursor.fetchall()
print('Empty full_notes:', empty_full)

cursor.close()
conn.close()
