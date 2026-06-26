import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(r'C:\Users\bhask\Desktop\New folder\.env')

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

query = "SELECT id, subject, topic FROM ai_notes_new WHERE language = 'Hindi' AND (subject LIKE '%English%' OR subject LIKE '%इंग्लिश%')"
cursor.execute(query)
results = cursor.fetchall()
print(f'Found {len(results)} Hindi-translated English records in the database.')

if results:
    print('Deleting them now...')
    delete_query = "DELETE FROM ai_notes_new WHERE language = 'Hindi' AND (subject LIKE '%English%' OR subject LIKE '%इंग्लिश%')"
    cursor.execute(delete_query)
    conn.commit()
    print('Deleted successfully.')

cursor.close()
conn.close()
