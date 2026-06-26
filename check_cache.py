import json
import os
p = r"C:\Users\bhask\Desktop\New folder\rag_cache_Class_6th_English.json"
if os.path.exists(p):
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Chapters completed: {len(data)}")
else:
    print("No cache")
