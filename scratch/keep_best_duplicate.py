import os
import sys
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

def has_content(val):
    if not val:
        return False
    # If it's a string containing just 'None', 'null' etc, or very short.
    val_str = str(val).strip().lower()
    if val_str in ['none', 'null', '', 'na', 'n/a']:
        return False
    if len(val_str) < 5:
        return False
    return True

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

        for d in duplicates:
            c = d['class']
            s = d['subject']
            t = d['topic']
            stream = d['stream']
            
            if stream is None:
                q = "SELECT id, short_notes, full_notes, book_url FROM ai_notes_new WHERE class=%s AND subject=%s AND topic=%s AND stream IS NULL"
                cursor.execute(q, (c, s, t))
            else:
                q = "SELECT id, short_notes, full_notes, book_url FROM ai_notes_new WHERE class=%s AND subject=%s AND topic=%s AND stream=%s"
                cursor.execute(q, (c, s, t, stream))
                
            rows = cursor.fetchall()
            if len(rows) < 2:
                continue
                
            # Score each row
            # Priority:
            # 1. Number of populated important fields (full_notes + book_url) [max 2]
            # 2. Length of short_notes
            # 3. Higher ID (as tie breaker)
            
            scored_rows = []
            for row in rows:
                fn_score = 1 if has_content(row['full_notes']) else 0
                bu_score = 1 if has_content(row['book_url']) else 0
                sn = row['short_notes']
                sn_len = len(sn) if sn else 0
                
                score_tuple = (fn_score + bu_score, sn_len, row['id'])
                scored_rows.append((score_tuple, row['id']))
                
            # Sort descending by score_tuple
            scored_rows.sort(key=lambda x: x[0], reverse=True)
            
            best_row_id = scored_rows[0][1]
            best_score = scored_rows[0][0]
            
            # Delete all except the best one
            ids_to_delete = [r[1] for r in scored_rows[1:]]
            
            if ids_to_delete:
                delete_q = f"DELETE FROM ai_notes_new WHERE id IN ({','.join(['%s']*len(ids_to_delete))})"
                cursor.execute(delete_q, tuple(ids_to_delete))
                conn.commit()
                deleted_count += len(ids_to_delete)
                print(f"Kept ID {best_row_id} (Full/Book Score: {best_score[0]}, SN Len: {best_score[1]}) | Deleted {len(ids_to_delete)} row(s) for Class {c} | {s} | {t}")
                
        print(f"\nDone! Deleted a total of {deleted_count} redundant rows based on new priority rules.")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
