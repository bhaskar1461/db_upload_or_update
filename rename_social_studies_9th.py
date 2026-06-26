import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\bhask\Desktop\New folder\Hindi\9th Class\सामाजिक अध्ययन (Social Studies)\Textbooks")

MAPPING = {
    "अर्थशास्त्र": {
        "Chapter 1.pdf": "1. पालमपुर गाँव की कहानी.pdf",
        "Chapter 2.pdf": "2. संसाधन के रूप में लोग.pdf",
        "Chapter 3.pdf": "3. निर्धनता - एक चुनौती.pdf",
        "Chapter 4.pdf": "4. भारत में खाद्य सुरक्षा.pdf"
    },
    "भूगोल": {
        "Chapter 1.pdf": "1. भारत - आकार और स्थिति.pdf",
        "Chapter 2.pdf": "2. भारत का भौतिक स्वरूप.pdf",
        "Chapter 3.pdf": "3. अपवाह.pdf",
        "Chapter 4.pdf": "4. जलवायु.pdf",
        "Chapter 5.pdf": "5. प्राकृतिक वनस्पति तथा वन्य प्राणी.pdf",
        "Chapter 6.pdf": "6. जनसंख्या.pdf"
    },
    "इतिहास": {
        "Chapter 1.pdf": "1. फ्रांसीसी क्रांति.pdf",
        "Chapter 2.pdf": "2. यूरोप में समाजवाद एवं रूसी क्रांति.pdf",
        "Chapter 3.pdf": "3. नात्सीवाद और हिटलर का उदय.pdf",
        "Chapter 4.pdf": "4. वन्य समाज एवं उपनिवेशवाद.pdf",
        "Chapter 5.pdf": "5. आधुनिक विश्व में चरवाहे.pdf"
    },
    "राजनीति विज्ञान": {
        "Chapter 1.pdf": "1. लोकतंत्र क्या और लोकतंत्र क्यों.pdf",
        "Chapter 2.pdf": "2. संविधान निर्माण.pdf",
        "Chapter 3.pdf": "3. चुनावी राजनीति.pdf",
        "Chapter 4.pdf": "4. संस्थाओं का कामकाज.pdf",
        "Chapter 5.pdf": "5. लोकतांत्रिक अधिकार.pdf"
    }
}

def rename_social_studies():
    for subcat, chapters in MAPPING.items():
        subcat_dir = BASE_DIR / subcat
        if not subcat_dir.exists():
            continue
        for old_name, new_name in chapters.items():
            old_path = subcat_dir / old_name
            new_path = subcat_dir / new_name
            if old_path.exists():
                old_path.rename(new_path)
                print(f"Renamed {old_path.name} to {new_path.name}")
            else:
                print(f"Missing {old_path}")
                
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    rename_social_studies()
