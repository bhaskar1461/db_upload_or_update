import os
import sys
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
sys.path.append(BASE_DIR)
from core.llm_client import LLMClient

load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

# Get the 73 rows that we messed up (we can find them by checking the short_notes for 'Chapter: Chapter \d+')
cursor.execute("SELECT id, short_notes FROM ai_notes_new WHERE short_notes LIKE '%Chapter: Chapter %'")
rows = cursor.fetchall()
updates = 0

llm = LLMClient()

for row_id, notes in rows:
    if not notes: continue
    
    # Extract the introduction
    intro = notes[:800]
    
    prompt = f"""
    Read the following Introduction from a generated note.
    Based on the actual content described in the introduction, provide a short, accurate Title (max 5 words) for this chapter.
    If it's about Hindi Grammar (Upsarg, etc.), title it 'Hindi Grammar (हिंदी व्याकरण)' or similar.
    If it's a mix of subjects, title it 'Mixed Compilation'.
    Return ONLY the Title, nothing else. No quotes.

    Introduction:
    {intro}
    """
    
    try:
        new_title = llm.generate_with_llm(prompt).strip()
        cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (new_title, row_id))
        updates += 1
        print(f"ID {row_id} -> {new_title}")
    except Exception as e:
        print(f"Error on {row_id}: {e}")

print(f"\nSuccessfully generated {updates} real titles using AI.")
conn.commit()
cursor.close()
conn.close()
