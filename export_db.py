import os
import sys
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

# Fix Windows terminal printing for Hindi text
sys.stdout.reconfigure(encoding='utf-8')

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def main():
    try:
        print(f"Connecting to database {DB_NAME}...")
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # We will fetch class, language, subject, topic, and short_notes
        query = """
            SELECT class, language, subject, topic, short_notes 
            FROM ai_notes 
            ORDER BY class ASC, language ASC, subject ASC, id ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        output_file = Path("database_export.md")
        
        print(f"Exporting {len(rows)} notes to {output_file.name}...")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Database Export: AI Notes\n\n")
            
            current_group = ""
            for row in rows:
                class_id, lang, subj, topic, short_notes = row
                
                # Group headers
                group_key = f"Class {class_id} - {lang} - {subj}"
                if group_key != current_group:
                    f.write(f"\n## {group_key}\n\n")
                    current_group = group_key
                    
                f.write(f"### Topic: {topic}\n\n")
                if short_notes:
                    f.write(f"{short_notes}\n\n")
                else:
                    f.write("*No short notes available.*\n\n")
                
                f.write("---\n\n")
                
        cursor.close()
        conn.close()
        
        print("Export completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
