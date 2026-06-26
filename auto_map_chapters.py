import os
import glob
import re
import json

def parse_chapter_name(filename):
    """Extract chapter number and name from a filename like 'Chapter_1_Food_Where_Does_It_Come_From.docx' or '1. The Earth in the Solar System.pdf'"""
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Common patterns:
    # 1. Chapter_1_Something
    # 2. Chapter 1 Something
    # 3. Chapter - 1 Something
    # 4. 1. Something
    # 5. 1 Something
    
    # Match "Chapter" followed by optional delimiters and the number
    m = re.match(r'^(?:Chapter\s*[-_]?\s*)?(\d+)[_\s\.\-]+(.*)$', name, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        title = m.group(2).strip(" _-.")
        return num, title
    
    # Try just leading digits
    m = re.match(r'^(\d+)[_\s\.\-]+(.*)$', name)
    if m:
        num = int(m.group(1))
        title = m.group(2).strip(" _-.")
        return num, title
        
    return None, name

def scan_directory(base_dir):
    files = glob.glob(os.path.join(base_dir, "**", "*.*"), recursive=True)
    mapping = []
    
    for f in files:
        if not (f.endswith('.docx') or f.endswith('.pdf')):
            continue
            
        # Ignore things in Textbooks or Generated dirs
        if "Textbooks" in f or "Generated" in f or "Notes" not in f:
            # wait, sometimes notes are just in the folder directly
            if "Textbooks" in f or "Generated" in f:
                continue
                
        filename = os.path.basename(f)
        num, title = parse_chapter_name(filename)
        
        if num is not None:
            mapping.append({
                "path": f,
                "folder": os.path.dirname(f),
                "num": num,
                "title": title,
                "original": filename
            })
            
    return mapping

if __name__ == "__main__":
    base_dir = r"c:\Users\bhask\Desktop\New folder"
    m = scan_directory(base_dir)
    print(f"Found {len(m)} chapter files.")
    
    # Print a few to test
    for i in range(min(20, len(m))):
        print(f"Num: {m[i]['num']:<2} | Title: {m[i]['title']:<40} | Path: {m[i]['path']}")
