import os
import json

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"

for file in os.listdir(BASE_DIR):
    if file.startswith("rag_cache_Class_") and file.endswith(".json"):
        filepath = os.path.join(BASE_DIR, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        matches = [k for k in data.keys() if 'talking fan' in k.lower()]
        if matches:
            print(f"File: {file}")
            for m in matches:
                print(f"  '{m}'")
