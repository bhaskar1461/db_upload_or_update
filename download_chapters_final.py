import os
import re
import sys
import glob
import json
import zipfile
import shutil
import traceback
from urllib.parse import urljoin
from pathlib import Path

try:
    import requests
except ImportError:
    print("Please pip install requests")
    sys.exit(1)

BASE_DIR = Path(r"c:\Users\bhask\Desktop\New folder")
SCRATCH_DIR = BASE_DIR / "scratch_downloads"
SCRATCH_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def parse_chapter_name(filename):
    """Extract chapter number and title from filename."""
    name = os.path.splitext(filename)[0]
    
    # Matches Chapter_1_Something, 1. Something, 01 Something
    m = re.match(r'^(?:Chapter\s*[-_]?\s*)?(\d+)[_\s\.\-]+(.*)$', name, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        title = m.group(2).strip(" _-.")
        return num, title
    
    return None, name

def scan_directory_for_mapping(base_search_dir):
    """Scan directory and return mapping dict: chapter_num -> full original filename (without ext)"""
    mapping = {}
    if not os.path.exists(base_search_dir):
        return mapping
        
    files = glob.glob(os.path.join(base_search_dir, "**", "*.*"), recursive=True)
    
    for f in files:
        if not (f.endswith('.docx') or f.endswith('.pdf')):
            continue
        # Skip Textbooks directory to avoid scanning already processed files or duplicates
        if "Textbooks" in f:
            continue
            
        filename = os.path.basename(f)
        num, title = parse_chapter_name(filename)
        
        if num is not None:
            # We want to keep the exact original filename layout, just replacing extension
            original_stem = os.path.splitext(filename)[0]
            mapping[num] = original_stem
            
    return mapping

def download_file(url, dest_path):
    print(f"  Downloading {url} ...")
    try:
        resp = SESSION.get(url, stream=True, timeout=120)
        if resp.status_code != 200:
            print(f"  Failed HTTP {resp.status_code}")
            return False
            
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(65536):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"\r  {downloaded/1024/1024:.1f} MB ({pct:.0f}%)", end="")
        print()
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Mapping configuration
# Structure: code -> {"search_dir": "relative/path", "dest_dir": "relative/path/Textbooks"}
BOOKS = [
    # CLASS 6 ENGLISH MEDIUM
    {"code": "fehs1", "search": "English/6th class/English/English", "dest": "English/6th class/English/Textbooks/Honeysuckle"},
    {"code": "fepw1", "search": "English/6th class/English/English", "dest": "English/6th class/English/Textbooks/A Pact With The Sun"},
    {"code": "fhvs1", "search": "English/6th class/Hindi", "dest": "English/6th class/Hindi/Textbooks/Vasant"},
    {"code": "fhdv1", "search": "English/6th class/Hindi", "dest": "English/6th class/Hindi/Textbooks/Durva"},
    {"code": "femh1", "search": "English/6th class/Maths", "dest": "English/6th class/Maths/Textbooks"},
    {"code": "fesc1", "search": "English/6th class/Science", "dest": "English/6th class/Science/Textbooks"},
    {"code": "fess1", "search": "English/6th class/Social Science/1. History", "dest": "English/6th class/Social Science/Textbooks/History"},
    {"code": "fess2", "search": "English/6th class/Social Science/2. Geography", "dest": "English/6th class/Social Science/Textbooks/Geography"},
    {"code": "fess3", "search": "English/6th class/Social Science/3. Civics", "dest": "English/6th class/Social Science/Textbooks/Civics"},
    {"code": "fhsk1", "search": "English/6th class/Sanskrit", "dest": "English/6th class/Sanskrit/Textbooks/Ruchira"},

    # CLASS 6 HINDI MEDIUM
    {"code": "fhmh1", "search": "Hindi/Class 6th/गणित (Maths)", "dest": "Hindi/Class 6th/गणित (Maths)/Textbooks"},
    {"code": "fhsc1", "search": "Hindi/Class 6th/विज्ञान (Science)", "dest": "Hindi/Class 6th/विज्ञान (Science)/Textbooks"},
    {"code": "fhss1", "search": "Hindi/Class 6th/सामाजिक विज्ञान (Social Science)/इतिहास (History)", "dest": "Hindi/Class 6th/सामाजिक विज्ञान (Social Science)/Textbooks/इतिहास"},
    {"code": "fhss2", "search": "Hindi/Class 6th/सामाजिक विज्ञान (Social Science)/भूगोल (Geography)", "dest": "Hindi/Class 6th/सामाजिक विज्ञान (Social Science)/Textbooks/भूगोल"},
    {"code": "fhss3", "search": "Hindi/Class 6th/सामाजिक विज्ञान (Social Science)/राजनीति विज्ञान (Political Science)", "dest": "Hindi/Class 6th/सामाजिक विज्ञान (Social Science)/Textbooks/राजनीति विज्ञान"},

    # CLASS 7 ENGLISH MEDIUM
    {"code": "gehc1", "search": "English/7th class/English/English", "dest": "English/7th class/English/Textbooks/Honeycomb"},
    {"code": "geah1", "search": "English/7th class/English/English", "dest": "English/7th class/English/Textbooks/An Alien Hand"},
    {"code": "ghvs1", "search": "English/7th class/Hindi", "dest": "English/7th class/Hindi/Textbooks/Vasant"},
    {"code": "ghdv1", "search": "English/7th class/Hindi", "dest": "English/7th class/Hindi/Textbooks/Durva"},
    {"code": "gemh1", "search": "English/7th class/Maths", "dest": "English/7th class/Maths/Textbooks"},
    {"code": "gesc1", "search": "English/7th class/science", "dest": "English/7th class/science/Textbooks"},
    {"code": "gess1", "search": "English/7th class/Social Science/1. History", "dest": "English/7th class/Social Science/Textbooks/History"},
    {"code": "gess2", "search": "English/7th class/Social Science/2. Geography Done", "dest": "English/7th class/Social Science/Textbooks/Geography"},
    {"code": "gess3", "search": "English/7th class/Social Science/3. Civics Done", "dest": "English/7th class/Social Science/Textbooks/Civics"},
    {"code": "ghsk1", "search": "English/7th class/Sanskrit", "dest": "English/7th class/Sanskrit/Textbooks/Ruchira"},

    # CLASS 7 HINDI MEDIUM
    {"code": "ghmh1", "search": "Hindi/Class 7th/गणित (Maths)", "dest": "Hindi/Class 7th/गणित (Maths)/Textbooks"},
    {"code": "ghsc1", "search": "Hindi/Class 7th/विज्ञान (Science)", "dest": "Hindi/Class 7th/विज्ञान (Science)/Textbooks"},
    {"code": "ghss1", "search": "Hindi/Class 7th/सामाजिक विज्ञान (Social Science)/इतिहास (History)", "dest": "Hindi/Class 7th/सामाजिक विज्ञान (Social Science)/Textbooks/इतिहास"},
    {"code": "ghss2", "search": "Hindi/Class 7th/सामाजिक विज्ञान (Social Science)/भूगोल (Geography)", "dest": "Hindi/Class 7th/सामाजिक विज्ञान (Social Science)/Textbooks/भूगोल"},
    {"code": "ghss3", "search": "Hindi/Class 7th/सामाजिक विज्ञान (Social Science)/राजनीति विज्ञान (Political Science)", "dest": "Hindi/Class 7th/सामाजिक विज्ञान (Social Science)/Textbooks/राजनीति विज्ञान"},

    # CLASS 8 ENGLISH MEDIUM
    {"code": "hehd1", "search": "English/8th class/English", "dest": "English/8th class/English/Textbooks/Honeydew"},
    {"code": "heih1", "search": "English/8th class/English", "dest": "English/8th class/English/Textbooks/It So Happened"},
    {"code": "hhvs1", "search": "English/8th class/हिंदी (Hindi)", "dest": "English/8th class/हिंदी (Hindi)/Textbooks/Vasant"},
    {"code": "hhdv1", "search": "English/8th class/हिंदी (Hindi)", "dest": "English/8th class/हिंदी (Hindi)/Textbooks/Durva"},
    {"code": "hemh1", "search": "English/8th class/Maths", "dest": "English/8th class/Maths/Textbooks"},
    {"code": "hesc1", "search": "English/8th class/science", "dest": "English/8th class/science/Textbooks"},
    {"code": "hess1", "search": "English/8th class/Social Science/History", "dest": "English/8th class/Social Science/Textbooks/History_1"},
    {"code": "hess2", "search": "English/8th class/Social Science/History", "dest": "English/8th class/Social Science/Textbooks/History_2"},
    {"code": "hess4", "search": "English/8th class/Social Science/Geography", "dest": "English/8th class/Social Science/Textbooks/Geography"},
    {"code": "hess3", "search": "English/8th class/Social Science/Civics", "dest": "English/8th class/Social Science/Textbooks/Civics"},

    # CLASS 8 HINDI MEDIUM
    {"code": "hhmh1", "search": "Hindi/Class 8th/गणित (Maths)", "dest": "Hindi/Class 8th/गणित (Maths)/Textbooks"},
    {"code": "hhsc1", "search": "Hindi/Class 8th/विज्ञान (Science)", "dest": "Hindi/Class 8th/विज्ञान (Science)/Textbooks"},
    {"code": "hhss1", "search": "Hindi/Class 8th/सामाजिक विज्ञान (Social Science)/इतिहास (History)", "dest": "Hindi/Class 8th/सामाजिक विज्ञान (Social Science)/Textbooks/इतिहास"},
    {"code": "hhss4", "search": "Hindi/Class 8th/सामाजिक विज्ञान (Social Science)/भूगोल (Geography)", "dest": "Hindi/Class 8th/सामाजिक विज्ञान (Social Science)/Textbooks/भूगोल"},
    {"code": "hhss3", "search": "Hindi/Class 8th/सामाजिक विज्ञान (Social Science)/राजनीति विज्ञान (Political Science)", "dest": "Hindi/Class 8th/सामाजिक विज्ञान (Social Science)/Textbooks/राजनीति विज्ञान"},

    # CLASS 9 MISSING
    {"code": "iewe1", "search": "Class 9/English", "dest": "Class 9/English/Textbooks/Words and Expressions"},
    {"code": "ihsh1", "search": "Class 9/Sanskrit", "dest": "Class 9/Sanskrit/Textbooks/Shemushi"},
    {"code": "ihmh1", "search": "Hindi/9th Class/गणित (Mathematics)", "dest": "Hindi/9th Class/गणित (Mathematics)/Textbooks"},
    {"code": "ihsc1", "search": "Hindi/9th Class/विज्ञान (Science)", "dest": "Hindi/9th Class/विज्ञान (Science)/Textbooks"},
    {"code": "ihss1", "search": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/इतिहास (History)", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/इतिहास"},
    {"code": "ihss3", "search": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/भूगोल (Geography)", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/भूगोल"},
    {"code": "ihss4", "search": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/राजनीति विज्ञान (Political Science)", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/राजनीति विज्ञान"},
    {"code": "ihss2", "search": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/अर्थशास्त्र (Economics)", "dest": "Hindi/9th Class/सामाजिक अध्ययन (Social Studies)/Textbooks/अर्थशास्त्र"}
]

def extract_and_rename(zip_path, book):
    search_dir = BASE_DIR / book["search"]
    dest_dir = BASE_DIR / book["dest"]
    code = book["code"]
    
    # Pre-compute mapping from the search dir
    mapping = scan_directory_for_mapping(str(search_dir))
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"  Mapping found {len(mapping)} chapters in notes. Extracting PDFs...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for info in zip_ref.infolist():
            filename = info.filename
            if not filename.lower().endswith(".pdf"):
                continue
            # Ignore Prelims (ps) and Answers (an)
            if "ps" in filename.lower() or "an" in filename.lower():
                continue
            
            # Match the chapter number from the NCERT convention: e.g. fesc101.pdf
            # It starts with the code, then digits
            m = re.match(rf"^{code}(\d+)\.pdf$", filename, re.IGNORECASE)
            if not m:
                # Sometimes NCERT includes other random PDFs, just try to extract any digits
                m2 = re.search(r"(\d+)\.pdf$", filename, re.IGNORECASE)
                if not m2:
                    continue
                num = int(m2.group(1))
            else:
                num = int(m.group(1))
            
            # Extract
            extracted_path = SCRATCH_DIR / filename
            zip_ref.extract(info, SCRATCH_DIR)
            
            # Decide target name
            if num in mapping:
                target_name = f"{mapping[num]}.pdf"
            else:
                target_name = f"Chapter {num}.pdf"
                
            final_path = dest_dir / target_name
            
            # Move and overwrite if exists
            if final_path.exists():
                final_path.unlink()
            shutil.move(str(extracted_path), str(final_path))
            print(f"    -> {target_name}")

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        
    for book in BOOKS:
        code = book["code"]
        print(f"\nProcessing {code} -> {book['dest']}")
        url = f"https://ncert.nic.in/textbook/pdf/{code}dd.zip"
        zip_path = SCRATCH_DIR / f"{code}dd.zip"
        
        if not zip_path.exists():
            success = download_file(url, zip_path)
            if not success:
                print(f"  [ERROR] Could not download ZIP for {code}")
                continue
                
        # Extract and rename
        try:
            extract_and_rename(zip_path, book)
        except Exception as e:
            print(f"  [ERROR] Processing {code}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
