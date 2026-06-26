import os
import sys

# Fix console encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"

count = 0
for root, dirs, files in os.walk(BASE_DIR):
    for f in files:
        if f.lower().endswith('.pdf'):
            if "1780166" in f or "-" in f or f.startswith("-"):
                try:
                    print(f"Found: {os.path.join(root, f)}")
                except Exception as e:
                    print(f"Found (repr): {repr(os.path.join(root, f))}")
                count += 1
                if count >= 50:
                    break
    if count >= 50:
        break
print(f"Done. Found {count} files matching search criteria.")
