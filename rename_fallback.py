import os
import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\bhask\Desktop\New folder\Hindi\9th Class")

def rename_smartly():
    # Walk all Textbooks folders
    for tb_dir in BASE_DIR.rglob("Textbooks"):
        if not tb_dir.is_dir(): continue
        
        # Look for PDF files inside this Textbooks dir or its subdirectories
        for pdf_path in tb_dir.rglob("Chapter *.pdf"):
            m = re.match(r"Chapter (\d+)\.pdf", pdf_path.name, re.IGNORECASE)
            if not m:
                continue
            chapter_num = int(m.group(1))
            
            # Search the entire Subject folder for a matching .docx or .pdf note
            # Find the top level Subject folder (parent of Textbooks or grandparent)
            subject_dir = tb_dir
            while subject_dir.parent != BASE_DIR:
                subject_dir = subject_dir.parent
                if subject_dir.parent == BASE_DIR:
                    break
            
            target_name = None
            # Recursively find any .docx or .pdf that matches the chapter number
            for note_file in subject_dir.rglob("*.*"):
                if "Textbooks" in note_file.parts:
                    continue # Skip our own textbook files
                if note_file.is_file() and note_file.suffix in [".docx", ".pdf"]:
                    nm = re.match(r"^(?:Chapter\s*)?0?" + str(chapter_num) + r"[\s\.\-_]+(.+)\.(docx|pdf)$", note_file.name, re.IGNORECASE)
                    if nm:
                        target_name = note_file.stem
                        break
            
            if target_name:
                new_pdf_path = pdf_path.parent / f"{target_name}.pdf"
                print(f"Renaming: {pdf_path.name} -> {new_pdf_path.name}")
                try:
                    pdf_path.rename(new_pdf_path)
                except Exception as e:
                    print(f"Failed to rename {pdf_path.name}: {e}")
            else:
                print(f"Could not find matching note name for {pdf_path.name} in {subject_dir}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    rename_smartly()
