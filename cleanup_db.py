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

# Delete all AI generated entries to start completely fresh
cursor.execute("DELETE FROM ai_notes WHERE generated_by = 'AI'")
affected = cursor.rowcount
conn.commit()

print(f"Successfully deleted {affected} AI-generated entries from the database.")
cursor.close()
conn.close()
