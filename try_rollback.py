import mysql.connector
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

print('Executing ROLLBACK command...')
cursor.execute('ROLLBACK;')
conn.commit()

cursor.execute("SELECT COUNT(*) FROM ai_notes WHERE generated_by = 'AI'")
count = cursor.fetchone()[0]

print(f'Rows with generated_by="AI" currently in database: {count}')
cursor.close()
conn.close()
