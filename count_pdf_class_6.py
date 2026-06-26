import os
from pathlib import Path

school_dir = Path(r"C:\Users\bhask\Desktop\Study Materials\data\school\class_6")
generated_dir = Path(r"C:\Users\bhask\Desktop\Study Materials\data\generated_notes\class_6")

pdf_count = 0
for r, d, f in os.walk(school_dir):
    for file in f:
        if "(Competitive)" in r and file.endswith(".pdf"):
            pdf_count += 1

md_count = 0
for r, d, f in os.walk(generated_dir):
    for file in f:
        if file.endswith(".md"):
            md_count += 1

print(f"Total competitive PDFs in Class 6: {pdf_count}")
print(f"Total competitive MD notes in Class 6: {md_count}")
