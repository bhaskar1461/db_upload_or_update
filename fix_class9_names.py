"""
Fix all badly-named PDFs in Class 9.
Handles:
  1. Chapter_X_Name.pdf  ->  X. Name.pdf
  2. Chapter - X Name_With_Underscores.pdf -> X. Name With Underscores.pdf
  3. Chapter X Name.pdf -> X. Name.pdf
  4. Name_With_Underscores.pdf -> Name With Underscores.pdf (grammar files)
  5. Precis_Writing-.pdf -> Precis Writing.pdf (trailing dash)
"""
import os
import re

BASE = r"C:\Users\bhask\Desktop\New folder\English\Class 9th"
renamed = 0

for root, dirs, files in os.walk(BASE):
    # Skip Textbooks folders
    if 'Textbooks' in root or 'Textbook' in root:
        continue
    
    for f in files:
        if not f.endswith('.pdf'):
            continue
        
        old_path = os.path.join(root, f)
        new_name = None
        
        # Skip files that already have correct naming (X. Name.pdf or name_create.pdf)
        if re.match(r'^\d+\.\s', f):
            continue
        
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
        
        # Pattern 3: Chapter X Name.pdf
        if not new_name:
            m = re.match(r'^Chapter\s+(\d+)\s+(.+)\.pdf$', f)
            if m:
                num = m.group(1)
                rest = m.group(2).replace('_', ' ').strip()
                new_name = f"{num}. {rest}.pdf"
        
        # Pattern 4: Copy of Chapter - X Name.pdf
        if not new_name:
            m = re.match(r'^Copy of Chapter\s*-\s*(\d+)\s+(.+)\.pdf$', f)
            if m:
                num = m.group(1)
                rest = m.group(2).replace('_', ' ').strip()
                new_name = f"Copy of {num}. {rest}.pdf"
        
        # Pattern 5: Name_With_Underscores.pdf (grammar/writing files without chapter numbers)
        if not new_name and '_' in f and not f.endswith('_create.pdf'):
            rest = f.replace('.pdf', '').replace('_', ' ').strip()
            # Clean up double spaces and trailing dashes
            rest = re.sub(r'\s+', ' ', rest).rstrip('-').strip()
            new_name = f"{rest}.pdf"
        
        if new_name and new_name != f:
            # Clean up any double spaces
            new_name = re.sub(r'\s+', ' ', new_name)
            new_path = os.path.join(root, new_name)
            if os.path.exists(new_path):
                print(f"  [SKIP - exists] {f}")
                continue
            os.rename(old_path, new_path)
            print(f"  {f}  ->  {new_name}")
            renamed += 1

print(f"\n✅ Total files renamed: {renamed}")
