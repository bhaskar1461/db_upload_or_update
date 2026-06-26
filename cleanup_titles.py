import os
import re
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
load_dotenv(os.path.join(BASE_DIR, ".env"))

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
)
cursor = conn.cursor()

# Get all topics
cursor.execute("SELECT id, topic FROM ai_notes_new")
rows = cursor.fetchall()

updates = 0
for row_id, topic in rows:
    if not topic: continue
    
    new_topic = topic
    
    # Fix repeated words like LIGHTLIGHT
    if len(new_topic) > 4 and new_topic[:len(new_topic)//2] == new_topic[len(new_topic)//2:]:
        new_topic = new_topic[:len(new_topic)//2]
    
    # Fix repeated phrases like MICROORGANISMS  : FRIEND AND FOE MICROORGANISMS  : FRIEND...
    match = re.match(r"^(.+?)\s+\1", new_topic)
    if match:
        new_topic = match.group(1)
        
    # Remove trailing numbers like Heat3 or Motion and Time9 if the name is mostly english
    if re.search(r'[a-zA-Z]', new_topic):
        new_topic = re.sub(r'\d+$', '', new_topic).strip()
    
    # Title case ALL CAPS strings
    if new_topic.isupper():
        new_topic = new_topic.title()
        
    # Remove weird prefixes
    new_topic = new_topic.replace('SCIENCE 142', '').replace('SCIENCE 156', '').replace('LIGHT 123', '')
    
    # Clean up trailing spaces or punctuation
    new_topic = new_topic.strip()
    if new_topic.endswith('...'):
        new_topic = new_topic[:-3].strip()
        
    if new_topic != topic:
        cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (new_title, row_id))
        updates += 1

print(f"Cleaned up {updates} messy titles.")
conn.commit()
cursor.close()
conn.close()
