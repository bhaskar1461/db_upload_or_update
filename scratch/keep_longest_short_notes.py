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

        for d in duplicates:
            c = d['class']
            s = d['subject']
            t = d['topic']
            stream = d['stream']
            
            if stream is None:
                q = "SELECT id, short_notes FROM ai_notes_new WHERE class=%s AND subject=%s AND topic=%s AND stream IS NULL"
                cursor.execute(q, (c, s, t))
            else:
                q = "SELECT id, short_notes FROM ai_notes_new WHERE class=%s AND subject=%s AND topic=%s AND stream=%s"
                cursor.execute(q, (c, s, t, stream))
                
            rows = cursor.fetchall()
            if len(rows) < 2:
                continue
                
            # Find the row with the longest short_notes
            longest_row_id = None
            max_len = -1
            
            for row in rows:
                sn = row['short_notes']
                sn_len = len(sn) if sn else 0
                
                # Tie-breaker: keep the higher ID if lengths are equal
                if sn_len > max_len or (sn_len == max_len and (longest_row_id is None or row['id'] > longest_row_id)):
                    max_len = sn_len
                    longest_row_id = row['id']
                    
            # Delete all except the longest one
            ids_to_delete = [row['id'] for row in rows if row['id'] != longest_row_id]
            
            if ids_to_delete:
                delete_q = f"DELETE FROM ai_notes_new WHERE id IN ({','.join(['%s']*len(ids_to_delete))})"
                cursor.execute(delete_q, tuple(ids_to_delete))
                conn.commit()
                deleted_count += len(ids_to_delete)
                print(f"Kept ID {longest_row_id} (len: {max_len}) | Deleted {len(ids_to_delete)} row(s) for Class {c} | {s} | {t}")
                
        print(f"\nDone! Deleted a total of {deleted_count} redundant rows.")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
