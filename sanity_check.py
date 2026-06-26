"""
Sanity Check: Find PDFs on disk that have NO matching row in the database.
This is the REVERSE approach - instead of checking DB nulls against files,
we check every file on disk against the DB to find orphaned PDFs.
"""
import os
import re
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def clean_str(s):
    """Strip all punctuation, underscores, numbers, and normalize."""
    s = re.sub(r'^\d+[\.\)\-\s]*', '', s)  # strip leading number
    s = s.replace('.pdf', '').replace('.PDF', '')
    s = re.sub(r'[^\w\s]', ' ', s)  # punctuation -> space
    s = re.sub(r'_', ' ', s)  # underscores -> space
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def run():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()

    # Get ALL rows for classes 6-8 (9 was wiped)
    cursor.execute("SELECT class, subject, topic, full_notes FROM ai_notes_new WHERE class IN ('6','7','8')")
    db_rows = cursor.fetchall()

    # Build a set of cleaned topic names per class
    db_topics_with_notes = {}  # {class: set of cleaned topics that HAVE notes}
    db_topics_without_notes = {}  # {class: set of cleaned topics that DON'T have notes}
    
    for cls, subj, topic, full_notes in db_rows:
        if not topic:
            continue
        key = f"{cls}"
        cleaned = clean_str(topic)
        if full_notes:
            db_topics_with_notes.setdefault(key, set()).add(cleaned)
        else:
            db_topics_without_notes.setdefault(key, set()).add(cleaned)

    # Now scan every PDF on disk for classes 6-8
    class_folders = {
        '6': os.path.join(BASE_DIR, "English", "6th class"),
        '7': os.path.join(BASE_DIR, "English", "7th class"),
        '8': os.path.join(BASE_DIR, "English", "8th class"),
    }

    print("=" * 80)
    print("SANITY CHECK: Finding PDFs on disk that are NOT in the database")
    print("=" * 80)

    total_orphans = 0

    for cls, folder in class_folders.items():
        if not os.path.exists(folder):
            print(f"\n[Class {cls}] Folder not found: {folder}")
            continue

        print(f"\n{'='*40}")
        print(f"CLASS {cls}")
        print(f"{'='*40}")

        attached_topics = db_topics_with_notes.get(cls, set())
        
        orphans = []
        for root, dirs, files in os.walk(folder):
            for f in files:
                if not f.lower().endswith('.pdf'):
                    continue
                
                f_cleaned = clean_str(f)
                if not f_cleaned or len(f_cleaned) < 3:
                    continue

                # Check if ANY db topic matches this file
                matched = False
                for t in attached_topics:
                    if t in f_cleaned or f_cleaned in t:
                        matched = True
                        break
                    # Also check word overlap
                    t_words = set(t.split())
                    f_words = set(f_cleaned.split())
                    if len(t_words) > 1 and len(f_words) > 1:
                        overlap = t_words & f_words
                        if len(overlap) >= min(len(t_words), len(f_words)) * 0.6:
                            matched = True
                            break

                if not matched:
                    rel_path = os.path.relpath(os.path.join(root, f), folder)
                    orphans.append((f, rel_path, f_cleaned))

        if orphans:
            print(f"  Found {len(orphans)} PDFs NOT matched to any DB row:")
            for fname, rel, cleaned in orphans:
                print(f"    ❌ {rel}")
                print(f"       cleaned: '{cleaned}'")
            total_orphans += len(orphans)
        else:
            print(f"  ✅ All PDFs on disk are matched to DB rows!")

    print(f"\n{'='*80}")
    print(f"TOTAL ORPHANED PDFs (on disk but not in DB): {total_orphans}")
    print(f"{'='*80}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run()
