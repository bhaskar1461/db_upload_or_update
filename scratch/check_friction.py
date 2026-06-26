import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"

search_terms = ['friction', 'वचन', 'बचपन', 'ऐसे']

print("Searching workspace for files matching terms:")
for root, dirs, files in os.walk(BASE_DIR):
    for f in files:
        for term in search_terms:
            if term.lower() in f.lower():
                print(f"  Match for '{term}': {os.path.join(root, f)}")
