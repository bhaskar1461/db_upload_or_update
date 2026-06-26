import os
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(r"C:\Users\bhask\Desktop\Archive\New folder\.env")
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

def inspect_table(table_name):
    print(f"\n--- Inspecting {table_name} ---")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        if not cursor.fetchone():
            print(f"Table {table_name} does not exist.")
            return
            
        # Total counts for classes 6 to 9
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE class IN ('6', '7', '8', '9')")
        total = cursor.fetchone()[0]
        print(f"Total rows for classes 6-9: {total}")
        
        # Breakdown by class, language
        cursor.execute(f"""
            SELECT class, language, COUNT(*) 
            FROM {table_name} 
            WHERE class IN ('6', '7', '8', '9') 
            GROUP BY class, language
            ORDER BY class, language
        """)
        for row in cursor.fetchall():
            print(f"Class {row[0]} ({row[1]}): {row[2]} rows")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error inspecting {table_name}: {e}")

if __name__ == "__main__":
    inspect_table("ai_notes")
    inspect_table("ai_notes_new")
