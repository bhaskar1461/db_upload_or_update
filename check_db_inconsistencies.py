import os
import re
import sys
from collections import defaultdict
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "u826463665_student")

REQUIRED_HEADINGS = [
    "## 1. Introduction",
    "## 2. Key Concepts",
    "## 3. Important Formulas",
    "## 4. Important Exam Points",
    "## 5. Quick Summary",
]

def main():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM ai_notes")
        rows = cursor.fetchall()
        
        inconsistencies = defaultdict(list)
        
        # Check for duplicates
        seen = {}
        for row in rows:
            key = (row['class'], row['subject'], row['topic'], row['language'])
            if key in seen:
                inconsistencies['duplicates'].append(f"Class {row['class']} | {row['subject']} | {row['topic']} ({row['language']})")
            seen[key] = True

            # Check 1: Missing or incomplete notes
            if not row['short_notes'] or len(row['short_notes'].strip()) < 50:
                inconsistencies['too_short_notes'].append(f"ID {row['id']} | {row['class']} | {row['subject']} | {row['topic']}")
            else:
                missing_headings = [h for h in REQUIRED_HEADINGS if h not in row['short_notes']]
                if missing_headings:
                    inconsistencies['missing_headings'].append(f"ID {row['id']} | {row['topic']} (Missing: {', '.join(missing_headings)})")

            # Check 2: Topic names still containing 'Chapter' or numbers at the start
            topic = row['topic']
            if topic and re.search(r'^(?:Chapter|Ch|\d+\.)', topic, re.IGNORECASE):
                inconsistencies['unclean_topics'].append(f"ID {row['id']} | '{topic}'")
                
            # Check 3: Topic names containing '-' or '_' that might need cleaning or 'Outdated'
            if topic and ('Outdated' in topic or '||' in topic):
                inconsistencies['strange_topics'].append(f"ID {row['id']} | '{topic}'")

            # Check 4: Streams not properly assigned for 11/12
            class_num = str(row['class'])
            if class_num in ['11', '12'] and not row['stream']:
                inconsistencies['missing_stream_11_12'].append(f"ID {row['id']} | {row['subject']} | {row['topic']}")
            
            # Check 5: Streams assigned for 6-8 (should be NULL)
            if class_num in ['6', '7', '8'] and row['stream']:
                inconsistencies['stream_in_middle_school'].append(f"ID {row['id']} | {row['subject']} | stream: {row['stream']}")
                
            # Check 6: Unknown subjects
            if row['subject'] == 'Unknown' or not row['subject']:
                inconsistencies['unknown_subjects'].append(f"ID {row['id']} | {row['topic']}")

        print(f"--- Database Inconsistency Report (Total rows: {len(rows)}) ---\n")
        
        for category, items in inconsistencies.items():
            print(f"[{category.upper()}] - {len(items)} found:")
            for item in items[:15]: # Show up to 15 examples per category
                print(f"  - {item}")
            if len(items) > 15:
                print(f"  ... and {len(items) - 15} more.")
            print()
            
        if not inconsistencies:
            print("No inconsistencies found! Database is perfectly clean.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()
