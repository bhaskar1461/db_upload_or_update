import os
import json
import re

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
ALL_FILES = []

def index_files():
    global ALL_FILES
    print("Indexing workspace files...")
    for root, dirs, files in os.walk(BASE_DIR):
        root_lower = root.lower()
        if "11th" in root_lower or "12th" in root_lower or "11" in root_lower or "12" in root_lower:
            continue
        for f in files:
            if f.lower().endswith('.pdf'):
                ALL_FILES.append({
                    "path": os.path.join(root, f),
                    "filename": f,
                    "root_lower": root_lower
                })
    print(f"Indexed {len(ALL_FILES)} PDF files.")

def normalize_name(name):
    # Replace all non-alphanumeric/non-Hindi characters with spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\u0900-\u097F]', ' ', name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    
    # Remove Hindi conjunctions/stopwords
    cleaned = re.sub(r'\b(और|एवं|तथा)\b', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Apply Hindi spelling-insensitive normalization
    cleaned = cleaned.replace('ी', 'ि')
    cleaned = cleaned.replace('ू', 'ु')
    cleaned = cleaned.replace('ं', '')
    cleaned = cleaned.replace('ँ', '')
    cleaned = cleaned.replace('श', 'स')
    cleaned = cleaned.replace('ष', 'स')
    cleaned = cleaned.replace('ज़', 'ज')
    cleaned = cleaned.replace('त्सी', 'ज')
    cleaned = cleaned.replace('ज़ी', 'ज')
    cleaned = cleaned.replace('ऋ', 'र')
    
    return cleaned

def find_pdf_for_6to9(class_str, subject, chapter_name, file_type, raw_chapter="", sub_subject=""):
    """
    Finds the appropriate PDF based on the class and whether we want notes or books.
    file_type: "notes" or "books"
    """
    clean_chap = normalize_name(chapter_name)
    
    # Ignore textbooks/notes constraints for notes files
    is_dummy_sub = (not sub_subject) or sub_subject.strip().startswith('_')
    if file_type == "notes":
        if sub_subject.lower() in ['textbooks', 'notes']:
            is_dummy_sub = True
            
    candidate_files = []
    
    for file_info in ALL_FILES:
        root_lower = file_info["root_lower"]
        f = file_info["filename"]
        path = file_info["path"]
        
        # Class filtering
        if class_str == "9":
            if "9" not in root_lower and "ninth" not in root_lower:
                continue
        elif class_str == "8":
            if "8" not in root_lower and "eighth" not in root_lower:
                continue
        elif class_str == "7":
            if "7" not in root_lower and "seventh" not in root_lower:
                continue
        elif class_str == "6":
            if "6" not in root_lower and "sixth" not in root_lower:
                continue
                
        # Subject filtering (with translation mismatch override for Social Studies / Social Science)
        subject_matched = False
        if subject.lower() in root_lower:
            subject_matched = True
        else:
            sub_clean = re.sub(r'\(.*?\)', '', subject).strip().lower()
            if sub_clean in root_lower:
                subject_matched = True
            elif ('social' in subject.lower() or 'सामाजिक' in subject.lower()) and ('social' in root_lower or 'सामाजिक' in root_lower):
                subject_matched = True
                
        if not subject_matched:
            continue
                
        # Fix: If the subject is 'science' or 'विज्ञान (science)', it should not match 'social science' or 'सामाजिक विज्ञान'
        if ('science' in subject.lower() and 'social' not in subject.lower()) and 'social science' in root_lower:
            continue
        if ('विज्ञान' in subject.lower() and 'सामाजिक' not in subject.lower()) and 'सामाजिक विज्ञान' in root_lower:
            continue

        # Sub-subject matching logic to avoid cross-matching subfolders
        if not is_dummy_sub:
            parts = re.split(r'[\(\)/\|]', sub_subject)
            matched_sub = False
            for part in parts:
                part_clean = normalize_name(part)
                if not part_clean:
                    continue
                part_clean_no_digits = re.sub(r'^\d+\s*', '', part_clean).strip()
                if not part_clean_no_digits:
                    continue
                root_clean = normalize_name(root_lower)
                if part_clean_no_digits in root_clean:
                    matched_sub = True
                    break
            if not matched_sub:
                continue

        # Textbooks vs Notes logic for Class 9
        if class_str == "9":
            if file_type == "books" and "textbooks" not in root_lower:
                continue
            if file_type == "notes" and "textbooks" in root_lower:
                # We want notes, not textbooks
                continue
        else:
            # Classes 6, 7, 8 do NOT have textbooks, only notes.
            if file_type == "books":
                continue # Skip books entirely for 6-8

        candidate_files.append((f, path))
        
    # Pass 1: Try to match by chapter name
    for f, path in candidate_files:
        clean_f = normalize_name(f)
        if (clean_chap and clean_chap in clean_f) or (chapter_name and chapter_name.lower() in f.lower()):
            return path
            
    # Pass 2: Match by chapter number at start
    if raw_chapter:
        chap_match = re.search(r'^(?:chapter|अध्याय)?\s*(\d+)\b', raw_chapter, re.IGNORECASE)
        if chap_match:
            chap_num = chap_match.group(1)
            for f, path in candidate_files:
                file_match = re.search(r'^(?:chapter|अध्याय)?\s*(\d+)\b', f, re.IGNORECASE)
                if file_match:
                    file_chap_num = file_match.group(1)
                    if chap_num == file_chap_num:
                        return path
                            
    return None

def test_mapping_for_file(filepath):
    filename = os.path.basename(filepath)
    parts = filename.replace("rag_cache_Class_", "").replace(".json", "").split("_")
    class_num = parts[0].replace("th", "")
    language = parts[-1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    found_count = 0
    total_count = 0
    missing = []
    matches = []
    
    for key in data.keys():
        total_count += 1
        key_parts = key.split("||")
        subject = key_parts[0].strip()
        raw_chapter = key_parts[-1].strip()
        
        # Strip "Copy of" prefix
        raw_chapter_clean = re.sub(r'^Copy\s+of\s+', '', raw_chapter, flags=re.IGNORECASE).strip()
        chapter_name = re.sub(r'^(?:Chapter\s*\d+\s*[:\-]?\s*)?\d*\.?\s*', '', raw_chapter_clean, flags=re.IGNORECASE).strip()
        
        sub_subject = ""
        if len(key_parts) > 2:
            sub_subject = "||".join(key_parts[1:-1]).strip()
            
        pdf_path = find_pdf_for_6to9(class_num, subject, chapter_name, "notes", raw_chapter_clean, sub_subject)
        if pdf_path:
            found_count += 1
            matches.append((subject, raw_chapter, os.path.basename(pdf_path)))
        else:
            missing.append((subject, sub_subject, raw_chapter, chapter_name))
            
    print(f"\nFile: {filename}")
    print(f"  -> Found PDF for {found_count}/{total_count} keys ({found_count/total_count*100:.1f}%)")
    print("  -> First 10 mappings:")
    for idx, (sub, raw_c, pdf_file) in enumerate(matches[:10]):
        print(f"     {idx+1}. '{sub}' - '{raw_c}' ===> '{pdf_file}'")
    if missing:
        print("  -> Missing keys:")
        for idx, (sub, sub_sub, raw_c, c_name) in enumerate(missing[:15]):
            print(f"     {idx+1}. Subject='{sub}', SubSubject='{sub_sub}', Raw='{raw_c}', Clean='{c_name}'")

def main():
    index_files()
    for file in os.listdir(BASE_DIR):
        if file.startswith("rag_cache_Class_") and file.endswith(".json"):
            class_num = file.replace("rag_cache_Class_", "").split("th")[0]
            if class_num in ["6", "7", "8", "9"]:
                test_mapping_for_file(os.path.join(BASE_DIR, file))

if __name__ == "__main__":
    main()
