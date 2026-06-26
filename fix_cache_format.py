import json
import glob
import os
import sys

# Ensure generator can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "exam_notes_generator"))

from core.generator import enforce_required_headings, REQUIRED_HEADINGS

def fix_format():
    cache_files = glob.glob("rag_cache_Class_*.json")
    total_fixed = 0

    for file_path in cache_files:
        filename = os.path.basename(file_path)
        # Parse filename e.g. rag_cache_Class_6th_English.json
        # rag_cache_Class_11th_Commerce_Hindi.json
        parts = filename.replace("rag_cache_Class_", "").replace(".json", "").split("_")
        
        medium = parts[-1] # English or Hindi
        class_name = "_".join(parts[:-1]) # e.g. 6th, or 11th_Commerce
        is_hindi = (medium.lower() == "hindi")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            fixed = False
            for key, content in data.items():
                missing_headings = [h for h in REQUIRED_HEADINGS if h not in content]
                
                if missing_headings:
                    # Key format: subject||subcategory||unit
                    key_parts = key.split("||")
                    subject = key_parts[0] if len(key_parts) > 0 else "Unknown"
                    unit = key_parts[-1] if len(key_parts) > 0 else "Unknown"
                    
                    new_content = enforce_required_headings(
                        text=content,
                        class_name=class_name,
                        subject=subject,
                        unit=unit,
                        is_hindi_medium=is_hindi
                    )
                    
                    data[key] = new_content
                    fixed = True
                    total_fixed += 1
            
            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Fixed formatting in: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"\nTotal chapters fixed: {total_fixed}")

if __name__ == "__main__":
    fix_format()
