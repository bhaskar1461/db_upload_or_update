import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

# Mode flags
DRY_RUN = "--execute" not in sys.argv

# Define subjects to map for Class 11 and Class 12
# format: (subject_name, slug, stream_id)
CORE_SUBJECTS = [
    ("Physics", "physics", 1),
    ("Chemistry", "chemistry", 1),
    ("Mathematics", "mathematics", 1),
    ("Biology", "biology", 1),
    ("Accountancy", "accountancy", 2),
    ("Business Studies", "business-studies", 2),
    ("Economics", "economics", 2),
    ("History", "history", 3),
    ("Geography", "geography", 3),
    ("Political Science", "political-science", 3), # Class 11 only in English, but let's check
    ("Sociology", "sociology", 3),
]

ELECTIVE_SUBJECTS = [
    ("English", "english", 4),
    ("Hindi", "hindi", 4),
    ("Physical Education", "physical-education", 4),
    ("Home Science", "home-science", 3),
]

# Subject name normalisation map for ai_notes and ai_notes_new
SUBJECT_RENAMES = {
    # Physics
    "भौतिकी (Physics)": "Physics",
    "Physics": "Physics",
    
    # Chemistry
    "रसायन विज्ञान (Chemistry)": "Chemistry",
    "Chemistry": "Chemistry",
    
    # Mathematics
    "गणित (Mathematics)": "Mathematics",
    "Mathematics": "Mathematics",
    
    # Biology
    "जीव विज्ञान (Biology)": "Biology",
    "Biology": "Biology",
    
    # Economics
    "अर्थशास्त्र (Economics)": "Economics",
    "Economics": "Economics",
    
    # Accountancy
    "लेखाशास्त्र (Accountancy)": "Accountancy",
    "Accountancy": "Accountancy",
    
    # Business Studies
    "व्यवसाय अध्ययन (Business Studies)": "Business Studies",
    "Business Studies": "Business Studies",
    
    # History
    "इतिहास (History)": "History",
    "इतिहास  (History)": "History", # with double spaces
    "History": "History",
    
    # Geography
    "भूगोल (Geography)": "Geography",
    "Geography": "Geography",
    
    # Political Science
    "राजनीति विज्ञान (Political Science)": "Political Science",
    "Political Science": "Political Science",
    
    # Sociology
    "समाजशास्त्र (Sociology)": "Sociology",
    "Sociology": "Sociology",
    
    # Electives
    "इंग्लिश (English)": "English",
    "English": "English",
    "हिन्दी (Hindi)": "Hindi",
    "Hindi": "Hindi",
    "शारीरिक शिक्षा (Physical Education)": "Physical Education",
    "Physical Education": "Physical Education",
    "गृह विज्ञान (Home science)": "Home Science",
    "Home Science": "Home Science",
}

# Mapping English subject_id to new Hindi subject_id
english_to_hindi_subj_map = {}

def esc(s: str) -> str:
    return s.replace("'", "\\'")

def main():
    mode_str = "DRY RUN (Previewing changes)" if DRY_RUN else "LIVE (Applying changes)"
    print("=" * 80)
    print(f"  Class 11 & 12 Hindi Medium Database Fixer  |  {mode_str}")
    print("=" * 80)

    try:
        conn = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        print("Connected to DB successfully.")

        # --- STEP 1: Process and Create Hindi Subjects ---
        print("\n--- STEP 1: Registering & Mapping Hindi Subjects ---")
        
        # We will check each core and elective subject for Class 11 and Class 12
        classes = [11, 12]
        
        for class_val in classes:
            # Determine which subjects apply to this class
            # Political Science only for 11, Home Science only for 12 in the notes, but let's map what's appropriate.
            subjects_to_process = CORE_SUBJECTS + ELECTIVE_SUBJECTS
            if class_val == 12:
                # We saw Political Science doesn't exist for 12, but let's keep it clean
                subjects_to_process = [s for s in subjects_to_process if s[0] != "Political Science"]
            if class_val == 11:
                # Home Science doesn't exist for 11
                subjects_to_process = [s for s in subjects_to_process if s[0] != "Home Science"]
                
            for subj_name, slug, stream_id in subjects_to_process:
                # 1. Check if the English counterpart exists to find its ID (for chapter re-linking)
                cursor.execute("""
                    SELECT s.id FROM subjects s
                    JOIN class_subjects cs ON cs.subject_id = s.id
                    WHERE s.subject_name = %s AND s.language = 'english' AND cs.class_id = %s
                """, (subj_name, class_val))
                en_subj_row = cursor.fetchone()
                en_subj_id = en_subj_row['id'] if en_subj_row else None
                
                # 2. Check if the Hindi subject already exists and is linked
                cursor.execute("""
                    SELECT s.id FROM subjects s
                    JOIN class_subjects cs ON cs.subject_id = s.id
                    WHERE s.subject_name = %s AND s.language = 'hindi' AND cs.class_id = %s
                """, (subj_name, class_val))
                hi_subj_row = cursor.fetchone()
                
                if hi_subj_row:
                    hi_subj_id = hi_subj_row['id']
                    print(f"  [EXISTS] Class {class_val} | Subject: '{subj_name}' (Hindi) -> ID: {hi_subj_id}")
                else:
                    if DRY_RUN:
                        print(f"  [DRY RUN] Would INSERT subject: Class {class_val} | '{subj_name}' (Hindi)")
                        hi_subj_id = -1
                    else:
                        # Insert new subject
                        cursor.execute("""
                            INSERT INTO subjects (subject_name, slug, board, language, stream_id)
                            VALUES (%s, %s, 'CBSE', 'hindi', %s)
                        """, (subj_name, slug, stream_id))
                        conn.commit()
                        cursor.execute("SELECT LAST_INSERT_ID() as id")
                        hi_subj_id = cursor.fetchone()['id']
                        print(f"  [INSERTED] Class {class_val} | Subject: '{subj_name}' (Hindi) -> ID: {hi_subj_id}")
                        
                        # Link to class in class_subjects
                        cursor.execute("""
                            INSERT IGNORE INTO class_subjects (class_id, subject_id)
                            VALUES (%s, %s)
                        """, (class_val, hi_subj_id))
                        conn.commit()
                        print(f"    [LINKED] Class {class_val} <-> Subject ID {hi_subj_id}")
                
                if en_subj_id and hi_subj_id != -1:
                    english_to_hindi_subj_map[(class_val, en_subj_id)] = hi_subj_id

        # --- STEP 2: Re-link chapters ---
        print("\n--- STEP 2: Re-linking Hindi Chapters to Hindi Subjects ---")
        
        # We will loop through the english_to_hindi_subj_map
        total_chapters_relinked = 0
        
        for (class_val, en_subj_id), hi_subj_id in english_to_hindi_subj_map.items():
            # Find chapters with language = 'hindi' pointing to en_subj_id
            cursor.execute("""
                SELECT COUNT(*) as count FROM chapters
                WHERE subject_id = %s AND language = 'hindi'
            """, (en_subj_id,))
            ch_count = cursor.fetchone()['count']
            
            if ch_count == 0:
                continue
                
            print(f"  Class {class_val} | Moving {ch_count} chapters from English Subj ID {en_subj_id} -> Hindi Subj ID {hi_subj_id}")
            
            if DRY_RUN:
                print(f"    [DRY RUN] Would execute: UPDATE chapters SET subject_id = {hi_subj_id} WHERE subject_id = {en_subj_id} AND language = 'hindi'")
                total_chapters_relinked += ch_count
            else:
                cursor.execute("""
                    UPDATE chapters
                    SET subject_id = %s
                    WHERE subject_id = %s AND language = 'hindi'
                """, (hi_subj_id, en_subj_id))
                conn.commit()
                affected = cursor.rowcount
                print(f"    [DONE] Updated {affected} chapters.")
                total_chapters_relinked += affected

        print(f"  Total chapters re-linked: {total_chapters_relinked}")

        # --- STEP 3: Normalize subject names in ai_notes_new ---
        print("\n--- STEP 3: Normalizing Subject Names in ai_notes_new ---")
        
        total_notes_new_updated = 0
        
        for old_name, new_name in SUBJECT_RENAMES.items():
            if old_name == new_name:
                continue
                
            cursor.execute("""
                SELECT COUNT(*) as count FROM ai_notes_new
                WHERE class IN ('11', '12') AND language = 'Hindi' AND subject = %s
            """, (old_name,))
            count = cursor.fetchone()['count']
            
            if count == 0:
                continue
                
            print(f"  '{old_name}' -> '{new_name}' ({count} notes)")
            
            if DRY_RUN:
                print(f"    [DRY RUN] Would execute: UPDATE ai_notes_new SET subject = '{new_name}' WHERE class IN ('11', '12') AND language = 'Hindi' AND subject = '{old_name}'")
                total_notes_new_updated += count
            else:
                cursor.execute("""
                    UPDATE ai_notes_new
                    SET subject = %s
                    WHERE class IN ('11', '12') AND language = 'Hindi' AND subject = %s
                """, (new_name, old_name))
                conn.commit()
                affected = cursor.rowcount
                print(f"    [DONE] Updated {affected} notes.")
                total_notes_new_updated += affected
                
        print(f"  Total notes in ai_notes_new updated: {total_notes_new_updated}")

        # --- STEP 4: Normalize subject names in ai_notes ---
        print("\n--- STEP 4: Normalizing Subject Names in ai_notes ---")
        
        total_notes_updated = 0
        
        for old_name, new_name in SUBJECT_RENAMES.items():
            if old_name == new_name:
                continue
                
            cursor.execute("""
                SELECT COUNT(*) as count FROM ai_notes
                WHERE class IN ('11', '12') AND language = 'Hindi' AND subject = %s
            """, (old_name,))
            count = cursor.fetchone()['count']
            
            if count == 0:
                continue
                
            print(f"  '{old_name}' -> '{new_name}' ({count} notes)")
            
            if DRY_RUN:
                print(f"    [DRY RUN] Would execute: UPDATE ai_notes SET subject = '{new_name}' WHERE class IN ('11', '12') AND language = 'Hindi' AND subject = '{old_name}'")
                total_notes_updated += count
            else:
                cursor.execute("""
                    UPDATE ai_notes
                    SET subject = %s
                    WHERE class IN ('11', '12') AND language = 'Hindi' AND subject = %s
                """, (new_name, old_name))
                conn.commit()
                affected = cursor.rowcount
                print(f"    [DONE] Updated {affected} notes.")
                total_notes_updated += affected
                
        print(f"  Total notes in ai_notes updated: {total_notes_updated}")

        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        if DRY_RUN:
            print("  DRY RUN complete. Run with --execute to apply changes.")
        else:
            print("  LIVE EXECUTION complete. All changes successfully committed.")
        print("=" * 80)

    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
