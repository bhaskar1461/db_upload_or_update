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
        
        query = """
        SELECT class, subject, topic, language, count(distinct short_notes) as notes, count(*) as total_rows 
        FROM ai_notes_new 
        GROUP BY 1,2,3,4 
        ORDER BY 1,2,3,4
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"Analyzing all {len(rows)} groups...\n")
        
        duplicates_by_lang = []
        notes_mismatch = []
        
        for r in rows:
            if r['total_rows'] > 1:
                duplicates_by_lang.append(r)
            if r['notes'] != r['total_rows']:
                notes_mismatch.append(r)
                
        if duplicates_by_lang:
            print(f"❌ Found {len(duplicates_by_lang)} groups with total_rows > 1 (Duplicates under Class, Subject, Topic, Language):")
            for r in duplicates_by_lang[:10]:
                print(f"   - Class: {r['class']} | Subject: {r['subject']} | Topic: {r['topic']} | Lang: {r['language']} | Total Rows: {r['total_rows']}")
            if len(duplicates_by_lang) > 10:
                print(f"   ... and {len(duplicates_by_lang) - 10} more.")
        else:
            print("✅ Zero duplicates found under Class, Subject, Topic, Language grouping (total_rows is 1 for all groups)!")
            
        if notes_mismatch:
            print(f"\n⚠️  Found {len(notes_mismatch)} groups where distinct short_notes count != total_rows:")
            for r in notes_mismatch[:10]:
                print(f"   - Class: {r['class']} | Subject: {r['subject']} | Topic: {r['topic']} | Lang: {r['language']} | Distinct Notes: {r['notes']} | Total Rows: {r['total_rows']}")
            if len(notes_mismatch) > 10:
                print(f"   ... and {len(notes_mismatch) - 10} more.")
        else:
            print("✅ Every group's distinct short_notes matches its row count (no identical short_notes shared across rows or null variations within group).")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
