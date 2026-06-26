import os
import sys
import mysql.connector
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def main():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()

    print("Fetching duplicates from ai_notes_new...")
    # Find all groups with duplicates
    query = """
        SELECT class, subject, topic, language, COUNT(*) as cnt
        FROM ai_notes_new
        WHERE class IN ('6', '7', '8', '9')
        GROUP BY class, subject, topic, language
        HAVING cnt > 1
    """
    cursor.execute(query)
    dup_groups = cursor.fetchall()
    print(f"Found {len(dup_groups)} groups of duplicates.")

    deleted_total = 0
    for cls, subj, topic, lang, cnt in dup_groups:
        # Get all IDs in this group, ordered by ID
        select_query = """
            SELECT id FROM ai_notes_new
            WHERE class = %s AND subject = %s AND topic = %s AND language = %s
            ORDER BY id ASC
        """
        cursor.execute(select_query, (cls, subj, topic, lang))
        ids = [r[0] for r in cursor.fetchall()]
        
        # Keep the first ID, delete the rest
        keep_id = ids[0]
        delete_ids = ids[1:]
        
        delete_query = f"DELETE FROM ai_notes_new WHERE id IN ({', '.join(map(str, delete_ids))})"
        cursor.execute(delete_query)
        deleted_total += len(delete_ids)
        print(f"  Class {cls} | {subj} | '{topic}' ({lang}): Keeping ID {keep_id}, deleted IDs: {delete_ids}")

    conn.commit()
    print(f"\nSuccessfully cleaned up database! Deleted a total of {deleted_total} duplicate records.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
