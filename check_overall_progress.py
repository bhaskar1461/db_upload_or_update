import os
from pathlib import Path

school_root = Path(r"C:\Users\bhask\Desktop\Study Materials\data\school")
generated_root = Path(r"C:\Users\bhask\Desktop\Study Materials\data\generated_notes")

classes = [6, 7, 8, 9, 10]

print("=== OVERALL PROGRESS STATUS ===")
print(f"{'Class':<8} | {'Competitive PDFs':<18} | {'Generated Notes':<18} | {'Progress %':<10}")
print("-" * 65)

total_pdfs = 0
total_mds = 0

for c in classes:
    school_dir = school_root / f"class_{c}"
    generated_dir = generated_root / f"class_{c}"
    
    pdf_count = 0
    if school_dir.exists():
        for r, d, f in os.walk(school_dir):
            for file in f:
                if "(Competitive)" in r and file.endswith(".pdf"):
                    pdf_count += 1
                    
    md_count = 0
    if generated_dir.exists():
        for r, d, f in os.walk(generated_dir):
            for file in f:
                if file.endswith(".md"):
                    md_count += 1
                    
    pct = (md_count / pdf_count * 100) if pdf_count > 0 else 0.0
    print(f"Class {c:<2} | {pdf_count:<18} | {md_count:<18} | {pct:>8.1f}%")
    
    total_pdfs += pdf_count
    total_mds += md_count

print("-" * 65)
total_pct = (total_mds / total_pdfs * 100) if total_pdfs > 0 else 0.0
print(f"{'TOTAL':<8} | {total_pdfs:<18} | {total_mds:<18} | {total_pct:>8.1f}%")
