import os
import glob
from PyPDF2 import PdfReader

def main():
    base_dir = r"c:\Users\bhask\Desktop\New folder\Textbooks"
    pdf_files = glob.glob(os.path.join(base_dir, "**", "*.pdf"), recursive=True)
    
    print(f"Found {len(pdf_files)} PDFs. Checking page counts...\n")
    print(f"{'Pages':<8} | {'Size (MB)':<10} | {'Book'}")
    print("-" * 80)
    
    suspicious = []

    for pdf_path in pdf_files:
        try:
            size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            
            rel_path = os.path.relpath(pdf_path, base_dir)
            print(f"{num_pages:<8} | {size_mb:<10.1f} | {rel_path}")
            
            # If a book has fewer than 50 pages, it might be just a chapter or incomplete
            if num_pages < 50:
                suspicious.append((rel_path, num_pages, size_mb))
                
        except Exception as e:
            rel_path = os.path.relpath(pdf_path, base_dir)
            print(f"{'ERROR':<8} | {'-':<10} | {rel_path} ({e})")
            suspicious.append((rel_path, "ERROR", 0))

    if suspicious:
        print("\n" + "="*80)
        print("⚠️ POTENTIALLY INCOMPLETE BOOKS (< 50 pages or error)")
        print("="*80)
        for s in suspicious:
            print(f"{s[1]} pages | {s[0]}")
    else:
        print("\nAll books appear to be full-length textbooks (50+ pages).")

if __name__ == "__main__":
    main()
