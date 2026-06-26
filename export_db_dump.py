import os
import sys
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(dotenv_path=Path('.env'))
db = mysql.connector.connect(
    host=os.getenv('DB_HOST', '127.0.0.1'),
    port=os.getenv('DB_PORT', '3306'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'u826463665_student')
)
cursor = db.cursor()

# Get table schema dynamically
cursor.execute("SHOW CREATE TABLE ai_notes")
create_stmt = cursor.fetchone()[1]

cursor.execute('SELECT * FROM ai_notes')
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

with open('ai_notes_dump.sql', 'w', encoding='utf-8') as f:
    f.write('DROP TABLE IF EXISTS `ai_notes`;\n')
    f.write(create_stmt + ';\n\n')
    
    for row in rows:
        values = []
        for val in row:
            if val is None:
                values.append('NULL')
            elif isinstance(val, (int, float)):
                values.append(str(val))
            else:
                val_str = str(val).replace("'", "''").replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
                values.append(f"'{val_str}'")
        cols_str = ', '.join([f"`{c}`" for c in columns])
        val_str_joined = ', '.join(values)
        f.write(f'INSERT INTO `ai_notes` ({cols_str}) VALUES ({val_str_joined});\n')

print(f'Exported {len(rows)} rows to ai_notes_dump.sql')
