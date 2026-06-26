import json
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

REQUIRED_HEADINGS = [
    "## 1. Introduction",
    "## 2. Key Concepts",
    "## 3. Important Formulas",
    "## 4. Important Exam Points",
    "## 5. Quick Summary",
]

def check_format():
    cache_files = glob.glob("rag_cache_Class_*.json")
    total_chapters = 0
    malformed_chapters = []

    for file_path in cache_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for key, content in data.items():
                total_chapters += 1
                missing_headings = [h for h in REQUIRED_HEADINGS if h not in content]
                
                if missing_headings:
                    malformed_chapters.append({
                        "file": file_path,
                        "key": key,
                        "missing": missing_headings
                    })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"--- Format Audit Results ---")
    print(f"Total cache files checked: {len(cache_files)}")
    print(f"Total chapters checked: {total_chapters}")
    print(f"Chapters failing format check: {len(malformed_chapters)}\n")
    
    if malformed_chapters:
        print("Detailed list of malformed chapters:")
        for idx, issue in enumerate(malformed_chapters[:50], 1): # show up to 50
            print(f" {idx}. File: {issue['file']}")
            print(f"    Topic: {issue['key']}")
            print(f"    Missing Headings: {issue['missing']}\n")
            
        if len(malformed_chapters) > 50:
            print(f"... and {len(malformed_chapters) - 50} more.")
    else:
        print("✅ SUCCESS: All chapters across all cache files perfectly follow the exact 5-heading format!")

if __name__ == "__main__":
    check_format()
