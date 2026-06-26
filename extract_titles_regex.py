import os
import re
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

# Get the 73 rows we previously wrongly mapped
# We can find them because their short_notes start with '# Class Xth Subject / Textbooks - Chapter: Chapter Y'
cursor.execute("SELECT id, subject, short_notes FROM ai_notes_new WHERE short_notes LIKE '%Chapter: Chapter %'")
rows = cursor.fetchall()
updates = 0

for row_id, subject, notes in rows:
    if not notes: continue
    
    intro = notes[:600]
    new_title = "Unknown Chapter"
    
    # Check for Mixed compilations
    if "compilation" in intro.lower() or "multiple subjects" in intro.lower() or "विभिन्न विषयों" in intro:
        if "Hindi" in subject or "हिंदी" in subject:
            if "व्याकरण" in intro:
                new_title = "Hindi Grammar (हिंदी व्याकरण)"
            else:
                new_title = "Mixed Compilation (मिश्रित संकलन)"
        elif "Sanskrit" in subject:
            new_title = "Mixed Compilation"
        else:
            new_title = "Mixed Compilation"
    
    # Try to find a quoted chapter name
    # e.g., specifically the chapter "Pollution of Air and Water"
    match = re.search(r'chapter ["\']([^"\']+)["\']', intro, re.IGNORECASE)
    if match and "Mixed Compilation" not in new_title:
        new_title = match.group(1).title()
        
    cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (new_title, row_id))
    updates += 1
    print(f"ID {row_id} -> {new_title}")

print(f"\nFixed {updates} wrong titles.")
conn.commit()
cursor.close()
conn.close()
