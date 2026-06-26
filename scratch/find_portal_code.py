import os
from pathlib import Path

def main():
    roots = [
        Path(r"c:\Users\bhask\Desktop"),
        Path(r"c:\Users\bhask")
    ]
    
    found = []
    for r in roots:
        print(f"Scanning {r}...")
        for child in r.iterdir():
            if child.is_dir() and not child.name.startswith(".") and child.name not in ["AppData", "Local Settings", "My Documents", "NetHood", "PrintHood", "Templates"]:
                # Check for common web folders
                if (child / "package.json").exists() or (child / "index.php").exists() or (child / "artisan").exists():
                    found.append(child)
                    
    print("\nFound web apps:")
    for f in found:
        print(f"  {f}")

if __name__ == "__main__":
    main()
