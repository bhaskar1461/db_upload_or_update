import time
import psutil
import subprocess
import os

print("⏳ Queue Manager started. Waiting for current upload to finish...")

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

print("✅ Current upload finished! Switching to Class 11th Humanities...")

with open('selenium_uploader.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('rag_cache_Class_11th_Commerce_Hindi.json', 'rag_cache_Class_11th_Humanities_Hindi.json')

with open('selenium_uploader.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("🚀 Starting Class 11th Humanities upload...")
subprocess.run([r"exam_notes_generator\.venv\Scripts\python.exe", "selenium_uploader.py"])
