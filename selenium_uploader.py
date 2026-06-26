import os
import json
import re
import time
import mysql.connector
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Hardcoded Paths
BASE_DIR = r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th"
NOTES_DIR = os.path.join(BASE_DIR, "11th &12th")
TEXTBOOK_DIR = os.path.join(BASE_DIR, "class 11 and 12 text book")
RAG_CACHE_DIR = r"C:\Users\bhask\Desktop\New folder"
TARGET_URL = "https://ainotes.schools2ai.com/bulk-upload"

# Change this to whichever JSON file you want to upload
CACHE_FILE_NAME = "rag_cache_Class_12th_Humanities_Hindi.json" 

def find_pdf(base_dir, class_str, stream, subject, chapter_name):
    # If a Commerce student has Maths, pull the book from the Science folder!
    if "Commerce" in stream and ("Maths" in subject or "गणित" in subject):
        stream = "Science"
        
    # If a Humanities student has Economics, pull the book from the Commerce folder!
    if "Humanities" in stream and ("Economics" in subject or "अर्थशास्त्र" in subject):
        stream = "Commerce"
        
    class_folder = f"Class {class_str}th"
    if stream:
        class_folder += f" {stream}"
    
    target_dir = None
    for root, dirs, files in os.walk(base_dir):
        if class_folder.lower() in root.lower() and subject.lower() in root.lower():
            target_dir = root
            break
            
    if not target_dir:
        return None
        
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.lower().endswith('.pdf'):
                clean_chap = re.sub(r'[^\w\s]', '', chapter_name).lower()
                clean_f = re.sub(r'[^\w\s]', '', f).lower()
                if clean_chap in clean_f or chapter_name.lower() in f.lower():
                    return os.path.join(root, f)
    return None

def setup_browser():
    print("\n🌐 Starting Invisible Chrome Browser...")
    chrome_options = Options()
    
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    
    # We spoof the user agent so Cloudflare thinks we are a normal user
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_uploaded_topics(language, class_num, stream):
    load_dotenv(os.path.join(RAG_CACHE_DIR, ".env"))
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor()
        query = f"SELECT topic FROM ai_notes_new WHERE language = '{language}' AND class = '{class_num}'"
        if stream:
            query += f" AND stream = '{stream}'"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return set([r[0].strip() for r in results])
    except Exception as e:
        print(f"⚠️ Could not fetch uploaded topics from DB: {e}")
        return set()

def main():
    print("🚀 Starting 100% Reliable Selenium Automation Script")
    
    filepath = os.path.join(RAG_CACHE_DIR, CACHE_FILE_NAME)
    if not os.path.exists(filepath):
        print(f"❌ Could not find cache file: {filepath}")
        return
        
    parts = CACHE_FILE_NAME.replace("rag_cache_Class_", "").replace(".json", "").split("_")
    class_num = parts[0].replace("th", "")
    stream = parts[1] if len(parts) > 2 else ""
    language = parts[-1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("🔍 Fetching already uploaded chapters from Database to resume safely...")
    uploaded_topics = get_uploaded_topics(language, class_num, stream)
    print(f"✅ Found {len(uploaded_topics)} chapters already uploaded in the database.")

    # 2. Start the Browser
    driver = setup_browser()
    driver.set_script_timeout(600) # 10 minutes for slow large PDF uploads
    
    try:
        print(f"\n🌍 Navigating to {TARGET_URL}...")
        driver.get(TARGET_URL)
        time.sleep(3) # Wait for page to fully render
        
        # Inject hidden file inputs into the DOM to attach real local PDFs
        driver.execute_script("""
            let form = document.createElement('form');
            form.id = 'backdoor_form';
            
            let notesInput = document.createElement('input');
            notesInput.type = 'file';
            notesInput.id = 'backdoor_notes';
            form.appendChild(notesInput);
            
            let booksInput = document.createElement('input');
            booksInput.type = 'file';
            booksInput.id = 'backdoor_books';
            form.appendChild(booksInput);
            
            document.body.appendChild(form);
        """)
        
        print("\n💉 Initializing Hidden Backdoor Uploader...")
        
        for key, content in data.items():
            key_parts = key.split("||")
            subject = key_parts[0].strip()
            raw_chapter = key_parts[-1].strip()
            chapter_name = re.sub(r'^\d+\.?\s*', '', raw_chapter).strip()
            
            # Check if this chapter is already in the database
            already_uploaded = False
            for uploaded_topic in uploaded_topics:
                if chapter_name.lower() in uploaded_topic.lower() or uploaded_topic.lower() in chapter_name.lower():
                    already_uploaded = True
                    break
                    
            if already_uploaded:
                print(f"\n  -> Skipping: {subject} - {chapter_name} (Already Uploaded in DB)")
                continue
                
            print(f"\n  -> Uploading: {subject} - {chapter_name}")
            
            notes_pdf = find_pdf(NOTES_DIR, class_num, stream, subject, chapter_name)
            book_pdf = find_pdf(TEXTBOOK_DIR, class_num, stream, subject, chapter_name)
            
            driver.execute_script("document.getElementById('backdoor_notes').value = '';")
            driver.execute_script("document.getElementById('backdoor_books').value = '';")
            
            if notes_pdf:
                driver.find_element(By.ID, 'backdoor_notes').send_keys(notes_pdf)
                print(f"     [Attached Notes PDF: {os.path.basename(notes_pdf)}]")
            
            if book_pdf:
                driver.find_element(By.ID, 'backdoor_books').send_keys(book_pdf)
                print(f"     [Attached Book PDF: {os.path.basename(book_pdf)}]")
                
            safe_content = json.dumps(content).replace("'", "\\'")

            js_script = f"""
            document.body.setAttribute('data-upload-status', 'pending');
            document.body.setAttribute('data-upload-result', '');
            
            async function uploadChapter() {{
                try {{
                    const formData = new FormData();
                    formData.append("language", "{language}");
                    formData.append("board", "CBSE");
                    formData.append("class", "{class_num}");
                    formData.append("subject", "{subject}");
                    formData.append("stream", "{stream}");
                    formData.append("createdBy", "AI");
                    formData.append("chapters", JSON.stringify(["{chapter_name}"]));
                    formData.append("short_notes", JSON.stringify([{json.dumps(content, ensure_ascii=False)}]));
                    
                    let notesFile = document.getElementById('backdoor_notes').files[0];
                    if (notesFile) {{
                        formData.append("notes", notesFile);
                        formData.append("noteChapterIndices", JSON.stringify([0]));
                    }}
                    
                    let booksFile = document.getElementById('backdoor_books').files[0];
                    if (booksFile) {{
                        formData.append("books", booksFile);
                        formData.append("bookChapterIndices", JSON.stringify([0]));
                    }}
                    
                    const response = await fetch("https://app-api.schools2ai.com/api/ainote", {{
                        method: "POST",
                        body: formData
                    }});
                    
                    if (response.ok) {{
                        document.body.setAttribute('data-upload-result', "SUCCESS: " + await response.text());
                    }} else {{
                        document.body.setAttribute('data-upload-result', "FAILED: " + response.status + " " + await response.text());
                    }}
                }} catch (error) {{
                    document.body.setAttribute('data-upload-result', "ERROR: " + error.toString());
                }} finally {{
                    document.body.setAttribute('data-upload-status', 'done');
                }}
            }}
            uploadChapter();
            """
            
            print("     [Javascript firing the request...]")
            driver.execute_script(js_script)
            
            result = ""
            while True:
                status = driver.execute_script("return document.body.getAttribute('data-upload-status');")
                if status == 'done':
                    result = driver.execute_script("return document.body.getAttribute('data-upload-result');")
                    break
                time.sleep(5)
            
            if "SUCCESS" in result:
                print("     ✅ Success! Uploaded successfully to S3 and Database.")
            else:
                print(f"     ❌ {result}")
                
            time.sleep(2)
            
    except Exception as e:
        print(f"\n❌ Browser Automation Error: {e}")
    finally:
        print("\n🛑 Closing Browser...")
        driver.quit()

if __name__ == "__main__":
    main()
