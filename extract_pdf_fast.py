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

cursor.execute("SELECT id, class, subject, short_notes FROM ai_notes_new WHERE topic IN ('Hindi Grammar (हिंदी व्याकरण)', 'Mixed Compilation (मिश्रित संकलन)', 'Extra Material / Worksheet', 'Mixed Compilation', 'Unknown Chapter')")
rows = cursor.fetchall()
updates = 0

# Scan all PDFs ONCE
pdf_map = {} # path -> []
for root, dirs, files in os.walk(BASE_DIR):
    if 'Textbooks' in root:
        for f in files:
            if f.endswith('.pdf'):
                path = os.path.join(root, f)
                pdf_map[path] = f

def find_pdf_path_fast(cls, subj, chapter_num):
    cls_str = str(cls)
    search_names = [f"Chapter {chapter_num}.pdf", f"{chapter_num}.pdf"]
    
    for path, fname in pdf_map.items():
        if fname in search_names:
            if (cls_str in path or f"{cls_str}th" in path) and (subj.split(' ')[0] in path or 'science' in path.lower() if 'science' in subj.lower() else True):
                return path
    return None

for row_id, cls, subj, notes in rows:
    match = re.search(r"Chapter:\s*Chapter\s*(\d+)", notes, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"Chapter:\s*(\d+)", notes, flags=re.IGNORECASE)
    
    if match:
        chapter_num = match.group(1)
        pdf_path = find_pdf_path_fast(cls, subj, chapter_num)
        
        if pdf_path and os.path.exists(pdf_path):
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    if len(reader.pages) > 0:
                        pdf_text = reader.pages[0].extract_text()
                        lines = [line.strip() for line in pdf_text.split('\n') if len(line.strip()) > 3]
                        
                        title = f"Chapter {chapter_num}"
                        for line in lines:
                            if not re.match(r'^\d+$', line) and 'chapter' not in line.lower() and 'class' not in line.lower() and 'subject' not in line.lower():
                                title = line
                                break
                        
                        if len(title) > 60:
                            title = title[:57] + '...'
                            
                        cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (title, row_id))
                        print(f"ID {row_id} mapped -> {title}")
                        updates += 1
            except Exception as e:
                print(f"Failed to read {pdf_path}: {e}")

print(f"\nFixed {updates} titles.")
conn.commit()
cursor.close()
conn.close()
