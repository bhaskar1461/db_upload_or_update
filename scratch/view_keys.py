import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"

for file in os.listdir(BASE_DIR):
    if file.startswith("rag_cache_Class_") and file.endswith(".json"):
        class_num = file.replace("rag_cache_Class_", "").split("th")[0]
        if class_num in ["6", "7", "8", "9"]:
            filepath = os.path.join(BASE_DIR, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            science_keys = [k for k in data.keys() if 'science' in k.lower() or 'विज्ञान' in k.lower()]
            if science_keys:
                print(f"\nFile: {file} (Class {class_num})")
                print(f"  Science keys count: {len(science_keys)}")
                for k in science_keys[:15]:
                    print(f"    '{k}'")
