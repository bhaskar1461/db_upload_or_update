import os
import re
import sys
import shutil
from pathlib import Path
import requests

BASE_DIR = Path(r"c:\Users\bhask\Desktop\New folder")
SESSION = requests.Session()

FAILED_BOOKS = [
    {"code": "ihmh1", "dest": "Hindi/9th Class/गणित (Mathematics)/Textbooks", "ia_item": "ncert-ihmh1"},
    {"code": "ihsc1", "dest": "Hindi/9th Class/विज्ञान (Science)/Textbooks", "ia_item": "ncert-ihsc1"},
    {"code": "ihss1", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/इतिहास", "ia_item": "ncert-ihss1"},
    {"code": "ihss3", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/भूगोल", "ia_item": "ncert-ihss3"},
    {"code": "ihss4", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/राजनीति विज्ञान", "ia_item": "ncert-ihss4"},
    {"code": "ihss2", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/अर्थशास्त्र", "ia_item": "ncert-ihss2"}
]

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        
    for book in FAILED_BOOKS:
        dest_dir = BASE_DIR / book["dest"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        item_id = book["ia_item"]
        code = book["code"]
        
        print(f"\nProcessing {code} via Internet Archive ({item_id})")
        meta_url = f"https://archive.org/metadata/{item_id}/files"
        resp = SESSION.get(meta_url)
        if resp.status_code != 200:
            print("Failed to get IA metadata")
            continue
            
        files = resp.json().get("result", [])
        chapter_pdfs = [f for f in files if f.get("name", "").lower().endswith(".pdf") and not ("ps" in f["name"].lower() or "an" in f["name"].lower())]
        
        for f in chapter_pdfs:
            name = f["name"]
            m = re.match(rf"^{code}(\d+)\.pdf$", name, re.IGNORECASE)
            if not m:
                m2 = re.search(r"(\d+)\.pdf$", name, re.IGNORECASE)
                if not m2:
                    continue
                num = int(m2.group(1))
            else:
                num = int(m.group(1))
                
            # We don't have Hindi mappings for these since they weren't in notes, so we just use Chapter Num
            target_name = f"Chapter {num}.pdf"
            target_path = dest_dir / target_name
            
            url = f"https://archive.org/download/{item_id}/{name}"
            print(f"  Downloading {name} -> {target_name} ...", end="", flush=True)
            try:
                r = SESSION.get(url)
                if r.status_code == 200:
                    with open(target_path, "wb") as out:
                        out.write(r.content)
                    print(" OK")
                else:
                    print(f" Failed HTTP {r.status_code}")
            except Exception as e:
                print(f" Error: {e}")

if __name__ == "__main__":
    main()
