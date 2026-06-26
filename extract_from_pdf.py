import os
import sys
import re
import mysql.connector
import PyPDF2
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
sys.path.append(os.path.join(BASE_DIR, "exam_notes_generator"))
from core.llm_client import LLMClient

load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

# Get the rows we previously updated to generic names
cursor.execute("SELECT id, class, subject, short_notes FROM ai_notes_new WHERE topic IN ('Hindi Grammar (हिंदी व्याकरण)', 'Mixed Compilation (मिश्रित संकलन)', 'Extra Material / Worksheet', 'Mixed Compilation', 'Unknown Chapter')")
rows = cursor.fetchall()
updates = 0

llm = LLMClient()

def find_pdf_path(cls, subj, chapter_num):
    # Try to find 'Chapter {chapter_num}.pdf' or '{chapter_num}.pdf' in a path containing cls and subj
    # E.g. '8th class', 'हिंदी (Hindi)', 'Chapter 13.pdf'
    cls_str = str(cls)
    search_names = [f"Chapter {chapter_num}.pdf", f"{chapter_num}.pdf"]
    
    for root, dirs, files in os.walk(BASE_DIR):
        if 'Textbooks' in root:
            # Check if class and subj match loosely
            if (cls_str in root or f"{cls_str}th" in root) and (subj.split(' ')[0] in root or 'science' in root.lower() if 'science' in subj.lower() else True):
                for f in files:
                    if f in search_names:
                        return os.path.join(root, f)
    return None

for row_id, cls, subj, notes in rows:
    # Extract chapter num from notes
    match = re.search(r"Chapter:\s*Chapter\s*(\d+)", notes, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"Chapter:\s*(\d+)", notes, flags=re.IGNORECASE)
    
    if match:
        chapter_num = match.group(1)
        pdf_path = find_pdf_path(cls, subj, chapter_num)
        
        if pdf_path and os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    if len(reader.pages) > 0:
                        pdf_text = reader.pages[0].extract_text()[:800]
                        
                        prompt = f"""
                        Extract the actual chapter title from the following text extracted from the first page of a textbook PDF.
                        IMPORTANT: The text might be in Kruti Dev font (Hindi typed with English keys, e.g. "ckt vkSj lk¡i" means "बाज और साँप"). If it looks like gibberish English, translate the Kruti Dev to actual Hindi.
                        Return ONLY the Chapter Title in a clean format (e.g. "Baaj aur Saanp (बाज और साँप)" or "Light"). Do not include any other text or quotes.

                        Text:
                        {pdf_text}
                        """
                        
                        new_title = llm.generate_with_llm(prompt).strip()
                        # Clean up any potential markdown quotes
                        new_title = new_title.replace('**', '').replace('"', '').replace("'", "")
                        
                        cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (new_title, row_id))
                        print(f"ID {row_id} mapped from PDF -> {new_title}")
                        updates += 1
            except Exception as e:
                print(f"Failed to read {pdf_path}: {e}")
        else:
            print(f"Could not find PDF for Class {cls} Subject {subj} Ch {chapter_num}")

print(f"\nFixed {updates} titles using direct PDF extraction.")
conn.commit()
cursor.close()
conn.close()
