import os

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
CLASS9_DIR = os.path.join(BASE_DIR, "Class 9")

for root, dirs, files in os.walk(CLASS9_DIR):
    for f in files:
        if 'toto' in f.lower() or 'adventures' in f.lower():
            print(f"Found: {os.path.join(root, f)}")
