import time
import psutil
import subprocess

print("⏳ Queue Manager started. Waiting for Class 12 Science to finish...")

while True:
    is_running = False
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                if any('selenium_uploader.py' in arg for arg in proc.info['cmdline']):
                    is_running = True
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if not is_running:
        break
    time.sleep(10)

print("✅ Science finished! Switching to Class 12th Commerce...")

with open('selenium_uploader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace whichever file it is currently on with Class 12 Commerce
import re
content = re.sub(r'CACHE_FILE_NAME = ".*"', 'CACHE_FILE_NAME = "rag_cache_Class_12th_Commerce_Hindi.json"', content)

with open('selenium_uploader.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("🚀 Starting Class 12th Commerce upload...")
subprocess.run([r"exam_notes_generator\.venv\Scripts\python.exe", "selenium_uploader.py"])
