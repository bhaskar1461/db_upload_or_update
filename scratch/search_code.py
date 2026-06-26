import os
from pathlib import Path

def main():
    root = Path(r"c:\Users\bhask\Desktop\Archive\New folder")
    terms = ["INSERT INTO subjects", "subjects", "class_subjects", "chapters"]
    
    for p in root.glob("**/*.py"):
        if "scratch" in p.parts or ".venv" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            content = p.read_text(encoding='utf-8')
            for term in terms:
                if term in content:
                    print(f"Found '{term}' in {p.relative_to(root)}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
