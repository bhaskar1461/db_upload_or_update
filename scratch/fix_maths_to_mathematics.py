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
        cursor = conn.cursor()
        
        tables = ['ai_notes_new', 'ai_notes']
        
        for table in tables:
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if not cursor.fetchone():
                print(f"Table '{table}' does not exist, skipping.")
                continue
                
            # Perform updates
            print(f"Updating table '{table}':")
            
            # 1. 'Maths' -> 'Mathematics'
            cursor.execute(f"UPDATE {table} SET subject = 'Mathematics' WHERE subject = 'Maths'")
            rows_affected_1 = cursor.rowcount
            
            # 2. 'गणित (Maths)' -> 'गणित (Mathematics)'
            cursor.execute(f"UPDATE {table} SET subject = 'गणित (Mathematics)' WHERE subject = 'गणित (Maths)'")
            rows_affected_2 = cursor.rowcount
            
            conn.commit()
            
            print(f"  - 'Maths' -> 'Mathematics': {rows_affected_1} rows updated.")
            print(f"  - 'गणित (Maths)' -> 'गणित (Mathematics)': {rows_affected_2} rows updated.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
