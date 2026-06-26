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
        
        # Test if language column exists first to give a helpful message
        cursor.execute("DESCRIBE ai_notes_new")
        columns = [col['Field'] for col in cursor.fetchall()]
        print(f"Columns in ai_notes_new: {columns}\n")
        
        query = """
        SELECT class, subject, topic, language, count(distinct short_notes) as notes, count(*) as total_rows 
        FROM ai_notes_new 
        GROUP BY 1,2,3,4 
        ORDER BY 1,2,3,4
        """
        
        # Adjust query if 'language' is missing
        if 'language' not in columns:
            print("⚠️ 'language' column is missing from ai_notes_new! Let's check if 'stream' is used instead.")
            query = """
            SELECT class, subject, topic, stream as language, count(distinct short_notes) as notes, count(*) as total_rows 
            FROM ai_notes_new 
            GROUP BY 1,2,3,4 
            ORDER BY 1,2,3,4
            """
            
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"Query Results (showing first 30 rows of {len(rows)} total rows):")
        print("-" * 100)
        print(f"{'Class':<6} | {'Subject':<30} | {'Topic':<35} | {'Lang/Stream':<12} | {'Notes':<6} | {'Total':<6}")
        print("-" * 100)
        
        for r in rows[:30]:
            subject = str(r['subject'])[:28]
            topic = str(r['topic'])[:33]
            lang = str(r['language'])[:10] if r['language'] is not None else "None"
            print(f"{str(r['class']):<6} | {subject:<30} | {topic:<35} | {lang:<12} | {r['notes']:<6} | {r['total_rows']:<6}")
            
        if len(rows) > 30:
            print(f"\n... and {len(rows) - 30} more rows.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error running query: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
