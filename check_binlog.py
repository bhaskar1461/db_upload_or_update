import mysql.connector
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor(dictionary=True)
    
    print('--- Binary Log Status ---')
    cursor.execute("SHOW VARIABLES LIKE 'log_bin'")
    log_bin = cursor.fetchone()
    print(log_bin)
    
    if log_bin and log_bin.get('Value') == 'ON':
        try:
            cursor.execute('SHOW BINARY LOGS')
            logs = cursor.fetchall()
            print(f'Binary Logs available: {len(logs)}')
        except Exception as e:
            print(f'Cannot show binary logs: {e}')
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error connecting: {e}')
