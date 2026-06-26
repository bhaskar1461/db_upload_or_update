import os
import sys
import re
import mysql.connector
from dotenv import load_dotenv
from collections import defaultdict

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def clean_str(s):
    """Strip punctuation, numbers, and normalize for comparison."""
    s = re.sub(r'^\d+[\.\)\-\s]*', '', s)  # strip leading number
    s = s.replace('.pdf', '').replace('.PDF', '')
    s = re.sub(r'[^\w\s]', ' ', s)  # punctuation -> space
    s = re.sub(r'_', ' ', s)  # underscores -> space
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def has_content(val):
    if not val:
        return False
    val_str = str(val).strip().lower()
    return val_str not in ['none', 'null', '', 'na', 'n/a']

def main():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 80)
        print("                DATABASE & STORAGE FULL SANITY CHECK REPORT")
        print("=" * 80)
        
        # -------------------------------------------------------------
        # CHECK 1: Row Count & Basic Stats
        # -------------------------------------------------------------
        print("\n[CHECK 1: Database Stats]")
        cursor.execute("SELECT COUNT(*) as count FROM ai_notes_new")
        total_rows = cursor.fetchone()['count']
        print(f"  - Total records in `ai_notes_new`: {total_rows}")
        
        # -------------------------------------------------------------
        # CHECK 2: Duplicates
        # -------------------------------------------------------------
        print("\n[CHECK 2: Duplicate Check]")
        dup_query = """
        SELECT class, subject, topic, stream, COUNT(*) as cnt
        FROM ai_notes_new
        GROUP BY class, subject, topic, stream
        HAVING cnt > 1
        """
        cursor.execute(dup_query)
        dups = cursor.fetchall()
        if dups:
            print(f"  ❌ Found {len(dups)} duplicate groups:")
            for d in dups:
                print(f"     - Count: {d['cnt']} | Class: {d['class']} | Subject: {d['subject']} | Topic: {d['topic']} | Stream: {d['stream']}")
        else:
            print("  ✅ Zero duplicates found based on Class, Subject, Topic, and Stream!")
            
        # -------------------------------------------------------------
        # CHECK 3: Null or Empty Columns
        # -------------------------------------------------------------
        print("\n[CHECK 3: Empty or Missing Content]")
        cursor.execute("SELECT id, class, subject, topic, short_notes, full_notes, book_url, stream FROM ai_notes_new")
        all_rows = cursor.fetchall()
        
        missing_short = []
        missing_full = []
        missing_url = []
        missing_topic = []
        
        for r in all_rows:
            if not has_content(r['topic']):
                missing_topic.append(r)
            if not has_content(r['short_notes']):
                missing_short.append(r)
            if not has_content(r['full_notes']):
                missing_full.append(r)
            if not has_content(r['book_url']):
                missing_url.append(r)
                
        if missing_topic:
            print(f"  ❌ {len(missing_topic)} records have MISSING or NULL Topic names! Examples (IDs): {[x['id'] for x in missing_topic[:5]]}")
        else:
            print("  ✅ All records have valid Topic names.")
            
        if missing_short:
            print(f"  ❌ {len(missing_short)} records have MISSING or NULL short_notes! Examples (IDs): {[x['id'] for x in missing_short[:5]]}")
        else:
            print("  ✅ All records have populated short_notes.")
            
        if missing_full:
            print(f"  ❌ {len(missing_full)} records have MISSING or NULL full_notes! (Normal for some non-uploaded items but check if expected). Total: {len(missing_full)}")
        else:
            print("  ✅ All records have populated full_notes.")
            
        if missing_url:
            print(f"  ⚠️  {len(missing_url)} records have MISSING or NULL book_url! Examples (IDs): {[x['id'] for x in missing_url[:5]]}")
        else:
            print("  ✅ All records have populated book_url.")
            
        # -------------------------------------------------------------
        # CHECK 4: Class-Stream Assignment Inconsistencies
        # -------------------------------------------------------------
        print("\n[CHECK 4: Stream Alignment Check]")
        stream_in_6to10 = []
        no_stream_in_11to12 = []
        
        for r in all_rows:
            cls_str = str(r['class']).strip()
            # Middle/High school classes 6-10 should NOT have a stream
            if cls_str in ['6', '7', '8', '9', '10'] and has_content(r['stream']):
                stream_in_6to10.append(r)
            # Senior secondary classes 11-12 MUST have a stream
            if cls_str in ['11', '12'] and not has_content(r['stream']):
                no_stream_in_11to12.append(r)
                
        if stream_in_6to10:
            print(f"  ❌ Found {len(stream_in_6to10)} middle/high school (6-10) records with a stream assigned! (Expected: NULL/None)")
            for r in stream_in_6to10[:5]:
                print(f"     - ID {r['id']} | Class {r['class']} | Subject {r['subject']} | Stream: {r['stream']}")
        else:
            print("  ✅ Classes 6 to 10 have no stream assigned (Correct).")
            
        if no_stream_in_11to12:
            print(f"  ❌ Found {len(no_stream_in_11to12)} senior secondary (11-12) records missing a stream assignment!")
            for r in no_stream_in_11to12[:5]:
                print(f"     - ID {r['id']} | Class {r['class']} | Subject {r['subject']}")
        else:
            print("  ✅ Classes 11 and 12 all have a stream assigned (Correct).")

        # -------------------------------------------------------------
        # CHECK 5: Subject Standardization Check
        # -------------------------------------------------------------
        print("\n[CHECK 5: Subject Naming Check]")
        cursor.execute("SELECT DISTINCT subject FROM ai_notes_new")
        subjects = [row['subject'] for row in cursor.fetchall()]
        
        maths_violations = [s for s in subjects if 'maths' in s.lower()]
        if maths_violations:
            print(f"  ❌ Found non-standard subject names containing 'Maths' instead of 'Mathematics': {maths_violations}")
        else:
            print("  ✅ Subject names are successfully standardized (no 'Maths' or 'गणित (Maths)' found).")

        # -------------------------------------------------------------
        # CHECK 6: Orphaned PDFs Check (Disk vs. DB)
        # -------------------------------------------------------------
        print("\n[CHECK 6: Disk vs. DB Orphans Check]")
        # Gather all cleaned topics from DB that have full notes attached
        db_topics = defaultdict(set)
        for r in all_rows:
            if has_content(r['topic']) and has_content(r['full_notes']):
                db_topics[str(r['class'])].add(clean_str(r['topic']))
                
        # Scan standard PDF folders
        disk_paths = [
            # (Class, Folder Path)
            ('6', os.path.join(BASE_DIR, "English", "6th class")),
            ('7', os.path.join(BASE_DIR, "English", "7th class")),
            ('8', os.path.join(BASE_DIR, "English", "8th class")),
            ('9', os.path.join(BASE_DIR, "English", "Class 9th")),
            ('11', os.path.join(BASE_DIR, "English", "11th & 12th")),
            ('12', os.path.join(BASE_DIR, "English", "11th & 12th")),
            ('6', os.path.join(BASE_DIR, "Hindi", "Class 6th")),
            ('7', os.path.join(BASE_DIR, "Hindi", "Class 7th")),
            ('8', os.path.join(BASE_DIR, "Hindi", "Class 8th")),
            ('9', os.path.join(BASE_DIR, "Hindi", "9th Class")),
        ]
        
        total_pdfs = 0
        orphans = []
        
        for cls, folder in disk_paths:
            if not os.path.exists(folder):
                continue
                
            attached_topics = db_topics[cls]
            
            for root, dirs, files in os.walk(folder):
                for f in files:
                    if not f.lower().endswith('.pdf'):
                        continue
                    
                    total_pdfs += 1
                    f_cleaned = clean_str(f)
                    if not f_cleaned or len(f_cleaned) < 3:
                        continue
                        
                    # Match logic: check substring or word overlap
                    matched = False
                    for t in attached_topics:
                        if t in f_cleaned or f_cleaned in t:
                            matched = True
                            break
                        t_words = set(t.split())
                        f_words = set(f_cleaned.split())
                        if len(t_words) > 1 and len(f_words) > 1:
                            overlap = t_words & f_words
                            # 60% overlap matches
                            if len(overlap) >= min(len(t_words), len(f_words)) * 0.6:
                                matched = True
                                break
                                
                    if not matched:
                        rel_path = os.path.relpath(os.path.join(root, f), BASE_DIR)
                        orphans.append((cls, f, rel_path, f_cleaned))
                        
        print(f"  - Scanned {total_pdfs} PDF textbooks/notes on disk.")
        if orphans:
            print(f"  ⚠️  Found {len(orphans)} PDFs on disk that do NOT appear to have a corresponding matching row with full notes in the DB:")
            # Group by class for clean reporting
            orphans_by_class = defaultdict(list)
            for cls, f, rel, cln in orphans:
                orphans_by_class[cls].append(rel)
                
            for cls, paths in orphans_by_class.items():
                print(f"     - Class {cls} ({len(paths)} files):")
                for path in paths[:5]:
                    print(f"       • {path}")
                if len(paths) > 5:
                    print(f"       • ... and {len(paths)-5} more.")
        else:
            print("  ✅ All scanned PDFs on disk match up with active notes in the database!")

        print("\n" + "=" * 80)
        print("                             SANITY CHECK COMPLETE")
        print("=" * 80)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
