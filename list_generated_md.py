import os
from pathlib import Path
from datetime import datetime

generated_dir = Path(r"C:\Users\bhask\Desktop\Study Materials\data\generated_notes\class_6")

print("Generated competitive notes in Class 6:")
for r, d, f in os.walk(generated_dir):
    for file in f:
        if file.endswith(".md"):
            p = Path(r) / file
            mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {p.relative_to(generated_dir)} | Size: {p.stat().st_size} bytes | Modified: {mtime}")
