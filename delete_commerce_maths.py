import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(r'C:\Users\bhask\Desktop\New folder\.env')

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

query = "DELETE FROM ai_notes_new WHERE class = '11' AND stream = 'Commerce' AND subject LIKE '%Maths%'"
cursor.execute(query)
conn.commit()

print(f'\n---> DELETED {cursor.rowcount} COMMERCE MATHS ROWS!')

cursor.close()
conn.close()
