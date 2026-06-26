"""
Fix all badly-named PDFs across Classes 6-8 (non-textbook only).
Handles two patterns:
  1. Chapter_X_Name_With_Underscores.pdf  ->  X. Name With Underscores.pdf
  2. Chapter - X Name_With_Underscores.pdf -> X. Name With Underscores.pdf  
  3. Ch_X_Name.pdf -> X. Name.pdf
"""
import os
import re

BASE = r"C:\Users\bhask\Desktop\New folder\English"

renamed = 0
for cls_folder in ['6th class', '7th class', '8th class']:
    path = os.path.join(BASE, cls_folder)
    if not os.path.exists(path):
        continue
    
    for root, dirs, files in os.walk(path):
        # Skip Textbooks folders - we don't touch those
        if 'Textbooks' in root or 'Textbook' in root:
            continue
        
        for f in files:
            if not f.endswith('.pdf'):
                continue
            
            old_path = os.path.join(root, f)
            new_name = None
            
            # Pattern 1: Chapter_X_Name.pdf
            m = re.match(r'^Chapter_(\d+)_(.+)\.pdf$', f)
            if m:
                num = m.group(1)
                rest = m.group(2).replace('_', ' ').strip()
                new_name = f"{num}. {rest}.pdf"
            
            # Pattern 2: Chapter - X Name_With_Underscores.pdf
            if not new_name:
                m = re.match(r'^Chapter\s*-\s*(\d+)\s+(.+)\.pdf$', f)
                if m:
                    num = m.group(1)
                    rest = m.group(2).replace('_', ' ').strip()
                    new_name = f"{num}. {rest}.pdf"
            
            # Pattern 3: Ch_X_Name.pdf
            if not new_name:
                m = re.match(r'^Ch_(\d+)_(.+)\.pdf$', f)
                if m:
                    num = m.group(1)
                    rest = m.group(2).replace('_', ' ').strip()
                    new_name = f"{num}. {rest}.pdf"
            
            if new_name and new_name != f:
                new_path = os.path.join(root, new_name)
                if os.path.exists(new_path):
                    print(f"  [SKIP - already exists] {f} -> {new_name}")
                    continue
                os.rename(old_path, new_path)
                print(f"  [{cls_folder}] {f}  ->  {new_name}")
                renamed += 1

print(f"\n✅ Total files renamed: {renamed}")
