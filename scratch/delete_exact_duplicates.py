import os
import sys
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

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
        
        # Get duplicate groups
        query = """
        SELECT class, subject, topic, stream, COUNT(*) as cnt
        FROM ai_notes_new
        GROUP BY class, subject, topic, stream
        HAVING cnt > 1
        """
        cursor.execute(query)
        duplicates = cursor.fetchall()
        
        deleted_count = 0
        skipped_count = 0

        for d in duplicates:
            c = d['class']
            s = d['subject']
            t = d['topic']
            stream = d['stream']
            
            if stream is None:
                q = "SELECT id, short_notes, full_notes, book_url FROM ai_notes_new WHERE class=%s AND subject=%s AND topic=%s AND stream IS NULL ORDER BY id ASC"
                cursor.execute(q, (c, s, t))
            else:
                q = "SELECT id, short_notes, full_notes, book_url FROM ai_notes_new WHERE class=%s AND subject=%s AND topic=%s AND stream=%s ORDER BY id ASC"
                cursor.execute(q, (c, s, t, stream))
                
            rows = cursor.fetchall()
            if len(rows) < 2:
                continue
                
            # Compare all rows against the first one
            first_row = rows[0]
            is_identical = True
            
            for row in rows[1:]:
                # We consider them identical if short_notes, full_notes, and book_url match
                if (row['short_notes'] != first_row['short_notes'] or 
                    row['full_notes'] != first_row['full_notes'] or 
                    row['book_url'] != first_row['book_url']):
                    is_identical = False
                    break
                    
            if is_identical:
                # Delete all except the first one
                ids_to_delete = [row['id'] for row in rows[1:]]
                delete_q = f"DELETE FROM ai_notes_new WHERE id IN ({','.join(['%s']*len(ids_to_delete))})"
                cursor.execute(delete_q, tuple(ids_to_delete))
                conn.commit()
                deleted_count += len(ids_to_delete)
                print(f"Deleted {len(ids_to_delete)} exact duplicates for Class {c} | {s} | {t}")
            else:
                skipped_count += 1
                print(f"Skipped Class {c} | {s} | {t} - data is NOT identical among duplicates")
                
        print(f"\nDone! Deleted {deleted_count} redundant rows. Skipped {skipped_count} groups with non-identical data.")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
