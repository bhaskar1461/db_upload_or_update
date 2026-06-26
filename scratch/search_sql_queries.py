import os
from pathlib import Path

def main():
    root = Path(r"c:\Users\bhask\Desktop\Study Materials")
    terms = ["SELECT", "subjects", "class_subjects", "chapters", "ai_notes"]
    
    for p in root.glob("**/*.py"):
        try:
            content = p.read_text(encoding='utf-8')
            for term in terms:
                if term in content and "db_service" in content:
                    # Print lines containing the term
                    lines = content.splitlines()
                    for i, l in enumerate(lines):
                        if any(t in l for t in ["SELECT", "FROM", "WHERE", "JOIN"]):
                            print(f"{p.name}:{i+1}: {l.strip()}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
