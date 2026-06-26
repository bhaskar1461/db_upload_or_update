import os
from pathlib import Path

def main():
    p = Path(r"C:\Users\bhask\Desktop\New folder")
    if p.exists():
        print(f"Directory {p} exists.")
        print("Files inside:")
        for child in p.iterdir():
            if child.is_file() and 'rag_cache' in child.name:
                print(f"  {child.name} (size: {child.stat().st_size})")
    else:
        print(f"Directory {p} does not exist.")

if __name__ == "__main__":
    main()
