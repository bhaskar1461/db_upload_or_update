import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(r'C:\Users\bhask\Desktop\New folder\.env')

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

query = "SELECT count(*) FROM ai_notes_new WHERE language = 'Hindi' AND class = '11' AND stream = 'Science'"
cursor.execute(query)
count = cursor.fetchone()[0]

print(f'\n---> TOTAL UPLOADED SO FAR: {count}')

cursor.close()
conn.close()
