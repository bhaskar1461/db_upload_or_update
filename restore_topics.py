import os
import re
import mysql.connector
import PyPDF2
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

ids = [2591, 2599, 2637, 2647, 2657, 2661, 2679, 2697, 2702, 2706, 2707, 2710, 2711, 2714, 2718, 2725, 2729, 2735, 2743, 2746, 2747, 2751, 2755, 2759, 2762, 2763, 2766, 2767, 2770, 2774, 2777, 2785, 2793, 2811, 2814, 2834, 2844, 2864, 2925, 2989, 3005, 3009, 3013, 3016, 3020, 3024, 3028, 3032, 3034, 3038, 3042, 3046, 3050, 3053, 3057, 3061, 3065, 3068, 3071, 3141, 3145, 3148, 3151, 3155, 3159, 3162, 3164, 3166, 3169, 3172, 3191, 3197, 3200, 3205, 3207, 3210, 3213, 3244, 3276, 3387, 3399, 3403, 3414, 3416, 3417, 3427, 3430, 3513, 3523, 3533, 3539, 3556, 3564, 3624, 3633, 3635, 3639, 3643, 3645, 3647, 3651, 3665, 3674, 3716, 3848, 3879, 4033, 4287, 4288, 4289, 4290, 4291, 4292, 4293, 4294, 4295, 4296, 4297, 4298, 4299, 4300, 4301, 4302, 4303, 4304, 4305, 4306, 4307, 4309, 4310, 4311, 4312, 4313, 4314, 4315, 4316, 4317, 4318, 4319, 4320, 4321, 4322, 4323, 4324, 4325, 4326, 4327, 4328, 4329, 4330, 4331, 4332, 4333, 4334, 4335, 4336, 4337]

placeholders = ','.join(['%s'] * len(ids))
cursor.execute(f"SELECT id, short_notes FROM ai_notes_new WHERE id IN ({placeholders})", ids)
rows = cursor.fetchall()
updates = 0

for row_id, notes in rows:
    # Example notes:
    # "# Class 6th Social Science / 1. History - Chapter: Chapter 6: Kingdoms Kings and an Early Republic  ## 1. Introduction"
    # "# Class 7th विज्ञान (Science) / Textbooks - Chapter: Chapter 13  ## 1. Introduction"
    
    match = re.search(r"^#\s*(.*?)\s*-\s*Chapter:\s*(.*?)\s*##", notes, re.DOTALL)
    if match:
        path_info = match.group(1).strip() # "Class 6th Social Science / 1. History"
        chapter_info = match.group(2).strip() # "Chapter 6: Kingdoms Kings..." or "Chapter 13"
        
        # Check if the title is already available in chapter_info
        if ":" in chapter_info:
            parts = chapter_info.split(":", 1)
            title = parts[1].strip()
            # If the title is not empty, use it directly!
            if len(title) > 2:
                cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (title, row_id))
                updates += 1
                continue
        
        # If we reach here, it means chapter_info is just "Chapter 13" with no title
        chapter_match = re.search(r"(\d+)", chapter_info)
        if chapter_match:
            chapter_num = chapter_match.group(1)
            
            # Reconstruct the exact folder path!
            # path_info is "Class 7th विज्ञान (Science) / Textbooks"
            # It maps to "C:\Users\bhask\Desktop\New folder\...lang...\Class 7th\विज्ञान (Science)\Textbooks\Chapter 13.pdf"
            path_parts = path_info.split(" / ")
            
            found_pdf = None
            # Search EXACTLY for this path structure to avoid matching the wrong subject
            for root, dirs, files in os.walk(BASE_DIR):
                normalized_root = root.replace("\\", "/")
                # Check if all path parts are in this root
                if all(part in normalized_root for part in path_parts):
                    if f"Chapter {chapter_num}.pdf" in files:
                        found_pdf = os.path.join(root, f"Chapter {chapter_num}.pdf")
                        break
                    elif f"{chapter_num}.pdf" in files:
                        found_pdf = os.path.join(root, f"{chapter_num}.pdf")
                        break
            
            if found_pdf:
                try:
                    with open(found_pdf, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        if len(reader.pages) > 0:
                            pdf_text = reader.pages[0].extract_text()
                            lines = [line.strip() for line in pdf_text.split('\n') if len(line.strip()) > 3]
                            
                            title = f"Chapter {chapter_num}"
                            for line in lines:
                                if not re.match(r'^\d+$', line) and 'chapter' not in line.lower() and 'class' not in line.lower() and 'subject' not in line.lower():
                                    title = line
                                    break
                            
                            if len(title) > 60:
                                title = title[:57] + '...'
                                
                            cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (title, row_id))
                            updates += 1
                except Exception as e:
                    pass

print(f"Restored and accurately named {updates} rows.")
conn.commit()
cursor.close()
conn.close()
