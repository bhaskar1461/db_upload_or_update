import os
import sys
import mysql.connector
import re
import json
from pathlib import Path
from datetime import datetime

# Enable UTF-8 console output for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent / ".env"
from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

# Check execution mode
DRY_RUN = "--execute" not in sys.argv

SUBJECT_RENAMES = {
    "भौतिकी (Physics)": "Physics",
    "Physics": "Physics",
    "रसायन विज्ञान (Chemistry)": "Chemistry",
    "Chemistry": "Chemistry",
    "गणित (Mathematics)": "Mathematics",
    "Mathematics": "Mathematics",
    "जीव विज्ञान (Biology)": "Biology",
    "Biology": "Biology",
    "अर्थशास्त्र (Economics)": "Economics",
    "Economics": "Economics",
    "लेखाशास्त्र (Accountancy)": "Accountancy",
    "Accountancy": "Accountancy",
    "व्यवसाय अध्ययन (Business Studies)": "Business Studies",
    "Business Studies": "Business Studies",
    "इतिहास (History)": "History",
    "इतिहास  (History)": "History",
    "History": "History",
    "भूगोल (Geography)": "Geography",
    "Geography": "Geography",
    "राजनीति विज्ञान (Political Science)": "Political Science",
    "Political Science": "Political Science",
    "समाजशास्त्र (Sociology)": "Sociology",
    "Sociology": "Sociology",
    "इंग्लिश (English)": "English",
    "English": "English",
    "हिन्दी (Hindi)": "Hindi",
    "Hindi": "Hindi",
    "शारीरिक शिक्षा (Physical Education)": "Physical Education",
    "Physical Education": "Physical Education",
    "गृह विज्ञान (Home science)": "Home Science",
    "Home Science": "Home Science",
}

# English subjects to be created for Class 11 and 12
NEW_ENGLISH_SUBJECTS = [
    # (class_val, subject_name, slug, language, stream_id)
    ("11", "English", "english", "english", 4),
    ("11", "Hindi", "hindi", "english", 4),
    ("12", "English", "english", "english", 4),
    ("12", "Hindi", "hindi", "english", 4),
]

# Mapping configurations for existing and new subjects where notes will be migrated
TARGETS_TO_MIGRATE = [
    # (class_val, old_subj, old_lang, new_subj, new_lang)
    ("11", "English", "English", "English", "english"),
    ("11", "English", "Hindi", "English", "hindi"),
    ("11", "Hindi", "Hindi", "Hindi", "hindi"),
    ("11", "Physical Education", "Hindi", "Physical Education", "hindi"),
    ("12", "English", "Hindi", "English", "hindi"),
    ("12", "Hindi", "Hindi", "Hindi", "hindi"),
    ("12", "Home Science", "Hindi", "Home Science", "hindi"),
    ("12", "Physical Education", "Hindi", "Physical Education", "hindi"),
]

def clean_topic_name(topic: str) -> str:
    """Strip chapter prefixes like '1. ', 'Chapter 1: ', and leading digits/whitespace."""
    # Remove leading numbering like "1 ", "10 ", "2. ", "03 - ", etc.
    cleaned = re.sub(r'^\d+[\s\.\-\_]+', '', topic).strip()
    # Remove chapter prefixes like "Chapter 1: " or "Ch 3 - "
    cleaned = re.sub(r'^(?:Chapter|Ch|Chp)\s*\d+[\s\.\-\_:]+', '', cleaned, flags=re.IGNORECASE).strip()
    return cleaned

def normalize_subject(subj: str) -> str:
    return SUBJECT_RENAMES.get(subj, subj).strip()

def build_full_notes_json(class_num: str, subject: str, topic: str, notes_text: str) -> str:
    """Generate structured full notes JSON, truncating it to fit varchar(255)."""
    full_notes = {
        "class": f"Class {class_num}",
        "subject": subject,
        "chapter_name": topic,
        "introduction": notes_text[:100].replace("\n", " "),
        "key_concepts": [{"topic": topic, "points": [notes_text[:100]]}],
        "important_exam_points": [],
        "quick_revision_facts": [],
    }
    return json.dumps(full_notes, ensure_ascii=False)[:255]

def main():
    mode_str = "DRY RUN (Previewing Changes)" if DRY_RUN else "LIVE MODE (Applying Changes)"
    print("=" * 80)
    print(f"  Class 11 & 12 Subject & Chapter Migration Tool  |  {mode_str}")
    print("=" * 80)

    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    
    # ── STEP 1: REGISTER MISSING ENGLISH MEDIUM SUBJECTS ──
    print("\n--- STEP 1: Registering & Linking Missing English Medium Subjects ---")
    for class_val, name, slug, lang, stream_id in NEW_ENGLISH_SUBJECTS:
        # Check if subject already exists for this class
        cursor.execute("""
            SELECT s.id FROM subjects s
            JOIN class_subjects cs ON cs.subject_id = s.id
            WHERE s.subject_name = %s AND s.language = %s AND cs.class_id = %s
        """, (name, lang, class_val))
        row = cursor.fetchone()
        
        if row:
            print(f"  [EXISTS] Class {class_val} {lang} Medium | Subject: '{name}' -> Subject ID: {row['id']}")
        else:
            if DRY_RUN:
                print(f"  [DRY RUN] Would register: Class {class_val} {lang} Medium | Subject: '{name}'")
            else:
                # Insert subject
                cursor.execute("""
                    INSERT INTO subjects (subject_name, slug, board, language, stream_id)
                    VALUES (%s, %s, 'CBSE', %s, %s)
                """, (name, slug, lang, stream_id))
                conn.commit()
                cursor.execute("SELECT LAST_INSERT_ID() as id")
                subj_id = cursor.fetchone()['id']
                print(f"  [INSERTED] Class {class_val} {lang} Medium | Subject: '{name}' -> ID: {subj_id}")
                
                # Link to class
                cursor.execute("""
                    INSERT IGNORE INTO class_subjects (class_id, subject_id)
                    VALUES (%s, %s)
                """, (class_val, subj_id))
                conn.commit()
                print(f"    [LINKED] Class {class_val} <-> Subject ID: {subj_id}")

    # ── STEP 2: SCAN TOPICS & MIGRATE NOTES ──
    print("\n--- STEP 2: Processing and Migrating Notes ---")
    now = datetime.now()
    
    total_chapters_created = 0
    total_notes_migrated = 0
    total_notes_linked = 0
    
    for class_val, old_subj, old_lang, target_subj_name, target_lang in TARGETS_TO_MIGRATE:
        print(f"\nTarget Class: {class_val} | Subject: {target_subj_name} ({target_lang} medium) | Source: {old_subj} ({old_lang})")
        
        # 1. Find correct subject ID in DB
        cursor.execute("""
            SELECT s.id FROM subjects s
            JOIN class_subjects cs ON cs.subject_id = s.id
            WHERE s.subject_name = %s AND s.language = %s AND cs.class_id = %s
        """, (target_subj_name, target_lang, class_val))
        subj_row = cursor.fetchone()
        
        if not subj_row:
            print(f"  ❌ ERROR: Target subject '{target_subj_name}' ({target_lang} medium) not found in subjects table for Class {class_val}!")
            continue
            
        subj_id = subj_row['id']
        print(f"  🎯 Found Target Subject ID: {subj_id}")
        
        # 2. Get distinct topics in old ai_notes for this target
        cursor.execute("""
            SELECT DISTINCT topic 
            FROM ai_notes
            WHERE class = %s AND LOWER(subject) = LOWER(%s) AND LOWER(language) = LOWER(%s)
              AND topic != 'UnknownTopic'
        """, (class_val, old_subj, old_lang))
        topics = [row['topic'] for row in cursor.fetchall()]
        print(f"  📂 Found {len(topics)} valid unique topics in old ai_notes.")
        
        for topic in topics:
            clean_topic = clean_topic_name(topic)
            
            # 3. Find or Create Chapter
            cursor.execute("""
                SELECT id FROM chapters
                WHERE subject_id = %s AND name = %s AND language = %s
            """, (subj_id, clean_topic, target_lang))
            ch_row = cursor.fetchone()
            
            if ch_row:
                ch_id = ch_row['id']
            else:
                if DRY_RUN:
                    print(f"    [DRY RUN] Would create Chapter: '{clean_topic}' for Subject ID {subj_id}")
                    ch_id = -1
                    total_chapters_created += 1
                else:
                    cursor.execute("""
                        INSERT INTO chapters (name, subject_id, language)
                        VALUES (%s, %s, %s)
                    """, (clean_topic, subj_id, target_lang))
                    conn.commit()
                    cursor.execute("SELECT LAST_INSERT_ID() as id")
                    ch_id = cursor.fetchone()['id']
                    print(f"    [CHAPTER CREATED] '{clean_topic}' -> Chapter ID: {ch_id}")
                    total_chapters_created += 1
            
            # 4. Fetch notes for this topic
            cursor.execute("""
                SELECT * FROM ai_notes
                WHERE class = %s AND LOWER(subject) = LOWER(%s) AND LOWER(language) = LOWER(%s)
                  AND topic = %s
            """, (class_val, old_subj, old_lang, topic))
            notes = cursor.fetchall()
            
            # Normalize target language string to title case (e.g. "English" or "Hindi") for ai_notes_new
            lang_title_case = target_lang.title()
            
            for note in notes:
                # Determine stream if empty/null
                stream_val = note['stream']
                if not stream_val or stream_val == '':
                    # Infer stream from target subject stream
                    cursor.execute("SELECT stream_id FROM subjects WHERE id = %s", (subj_id,))
                    s_id = cursor.fetchone()['stream_id']
                    stream_val = {1: "Science", 2: "Commerce", 3: "Humanities", 4: ""}.get(s_id, "")
                
                # Check if note already exists in ai_notes_new
                cursor.execute("""
                    SELECT id, chapter_id FROM ai_notes_new
                    WHERE class = %s AND subject = %s AND language = %s AND topic = %s AND stream = %s
                """, (class_val, target_subj_name, lang_title_case, clean_topic, stream_val))
                existing = cursor.fetchone()
                
                if existing:
                    # Note exists, link/update chapter_id if missing or different
                    if existing['chapter_id'] != ch_id:
                        if DRY_RUN:
                            print(f"      [DRY RUN] Would update Note ID {existing['id']} chapter_id -> {ch_id}")
                        else:
                            cursor.execute("""
                                UPDATE ai_notes_new 
                                SET chapter_id = %s, updated_at = %s 
                                WHERE id = %s
                            """, (ch_id, now, existing['id']))
                            conn.commit()
                        total_notes_linked += 1
                else:
                    # Note doesn't exist, migrate/insert new note
                    short_notes = note['short_notes']
                    full_notes_raw = note['full_notes']
                    book_url = note['book_url']
                    
                    # If full_notes in old table is empty, build a clean dummy JSON.
                    # If it has content (e.g., pdf file path), preserve it directly but truncate to 255 if needed.
                    if not full_notes_raw or full_notes_raw == '':
                        full_notes_to_save = build_full_notes_json(class_num=class_val, subject=target_subj_name, topic=clean_topic, notes_text=short_notes)
                    else:
                        full_notes_to_save = full_notes_raw[:255]
                        
                    book_url_to_save = book_url[:255] if book_url else None
                    
                    if DRY_RUN:
                        print(f"      [DRY RUN] Would insert new note: {clean_topic} for stream {stream_val}")
                    else:
                        cursor.execute("""
                            INSERT INTO ai_notes_new 
                            (language, board, stream, class, subject, topic, short_notes, full_notes, book_url, created_by, created_at, updated_at, chapter_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (lang_title_case, "CBSE", stream_val, class_val, target_subj_name, clean_topic, short_notes, full_notes_to_save, book_url_to_save, "AI", now, now, ch_id))
                        conn.commit()
                        print(f"      [MIGRATED] Note '{clean_topic}' inserted & linked to Chapter ID {ch_id}")
                    total_notes_migrated += 1

    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("  Execution Summary:")
    print(f"  Total chapters created: {total_chapters_created}")
    print(f"  Total notes newly migrated: {total_notes_migrated}")
    print(f"  Total existing notes updated/linked: {total_notes_linked}")
    print("=" * 80)
    if DRY_RUN:
        print("  DRY RUN completed. Run with `--execute` argument to apply actual database changes.")
    else:
        print("  LIVE EXECUTION completed. All changes committed to the database.")
    print("=" * 80)

if __name__ == "__main__":
    main()
