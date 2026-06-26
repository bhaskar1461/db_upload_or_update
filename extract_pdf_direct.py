import os
import sys
import re
import mysql.connector
import PyPDF2
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"

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

def find_pdf_path(cls, subj, chapter_num):
    cls_str = str(cls)
    search_names = [f"Chapter {chapter_num}.pdf", f"{chapter_num}.pdf"]
    
    for root, dirs, files in os.walk(BASE_DIR):
        if 'Textbooks' in root:
            if (cls_str in root or f"{cls_str}th" in root) and (subj.split(' ')[0] in root or 'science' in root.lower() if 'science' in subj.lower() else True):
                for f in files:
                    if f in search_names:
                        return os.path.join(root, f)
    return None

for row_id, cls, subj, notes in rows:
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
                        pdf_text = reader.pages[0].extract_text()
                        
                        # Find the first meaningful line
                        lines = [line.strip() for line in pdf_text.split('\n') if len(line.strip()) > 3]
                        
                        title = f"Chapter {chapter_num}"
                        
                        for line in lines:
                            # Skip lines that are just numbers or generic
                            if not re.match(r'^\d+$', line) and 'chapter' not in line.lower() and 'class' not in line.lower() and 'subject' not in line.lower():
                                title = line
                                break
                        
                        # Limit title length
                        if len(title) > 60:
                            title = title[:57] + '...'
                            
                        cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (title, row_id))
                        print(f"ID {row_id} mapped to -> {title}")
                        updates += 1
            except Exception as e:
                print(f"Failed to read {pdf_path}: {e}")

print(f"\nFixed {updates} titles using direct PDF text.")
conn.commit()
cursor.close()
conn.close()
