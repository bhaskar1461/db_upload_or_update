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
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
TARGET_URL = "https://ainotes.schools2ai.com/bulk-upload"

def find_pdf_for_6to9(class_str, subject, chapter_name, file_type):
    """
    Finds the appropriate PDF based on the class and whether we want notes or books.
    file_type: "notes" or "books"
    """
    clean_chap = re.sub(r'[^\w\s]', '', chapter_name).lower()
    
    # We will search the entire BASE_DIR for a matching file
    for root, dirs, files in os.walk(BASE_DIR):
        root_lower = root.lower()
        
        # Skip unrelated class folders
        if "11th" in root_lower or "12th" in root_lower or "11" in root_lower or "12" in root_lower:
            continue
            
        # Class filtering logic
        if class_str == "9":
            if "9" not in root_lower and "ninth" not in root_lower:
                continue
        elif class_str == "8":
            if "8" not in root_lower and "eighth" not in root_lower:
                continue
        elif class_str == "7":
            if "7" not in root_lower and "seventh" not in root_lower:
                continue
        elif class_str == "6":
            if "6" not in root_lower and "sixth" not in root_lower:
                continue
                
        # Subject filtering
        if subject.lower() not in root_lower:
            # specifically for Hindi mapping like 'सामाजिक अध्ययन (Social Studies)'
            sub_clean = re.sub(r'\(.*?\)', '', subject).strip().lower()
            if sub_clean not in root_lower:
                continue

        # Textbooks vs Notes logic for Class 9
        if class_str == "9":
            if file_type == "books" and "textbooks" not in root_lower:
                continue
            if file_type == "notes" and "textbooks" in root_lower:
                # We want notes, not textbooks
                continue
        else:
            # Classes 6, 7, 8 do NOT have textbooks, only notes.
            if file_type == "books":
                return None # Skip books entirely for 6-8

        for f in files:
            if f.lower().endswith('.pdf') or f.lower().endswith('.docx'):
                # Wait! We can only upload PDFs. If the notes are .docx, we have to find the matching .pdf
                if not f.lower().endswith('.pdf'):
                    continue
                    
                clean_f = re.sub(r'[^\w\s]', '', f).lower()
                clean_f = re.sub(r'\s+', ' ', clean_f).strip()
                clean_chap_norm = re.sub(r'\s+', ' ', clean_chap).strip()
                # Check if chapter name matches
                if clean_chap_norm in clean_f or chapter_name.lower() in f.lower():
                    return os.path.join(root, f)
                    
    return None

def setup_browser():
    print("\n🌐 Starting Invisible Chrome Browser...")
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_uploaded_topics(language, class_num):
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor()
        query = f"SELECT topic FROM ai_notes_new WHERE language = '{language}' AND class = '{class_num}'"
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return set([r[0].strip() for r in results])
    except Exception as e:
        print(f"⚠️ Could not fetch uploaded topics from DB: {e}")
        return set()

def upload_cache_file(driver, filepath):
    filename = os.path.basename(filepath)
    print(f"\n======================================")
    print(f"📦 Processing {filename}")
    print(f"======================================")
    
    # Extract metadata from filename (e.g. rag_cache_Class_9th_Hindi.json)
    parts = filename.replace("rag_cache_Class_", "").replace(".json", "").split("_")
    class_num = parts[0].replace("th", "")
    language = parts[-1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("🔍 Fetching already uploaded chapters from Database...")
    uploaded_topics = get_uploaded_topics(language, class_num)
    print(f"✅ Found {len(uploaded_topics)} chapters already uploaded in the database for Class {class_num}.")

    for key, content in data.items():
        key_parts = key.split("||")
        subject = key_parts[0].strip()
        if "math" not in subject.lower():
            continue
        raw_chapter = key_parts[-1].strip()
        # Aggressively strip "Chapter X:" and leading numbers
        chapter_name = re.sub(r'^(?:Chapter\s*\d+\s*[:\-]?\s*)?\d*\.?\s*', '', raw_chapter, flags=re.IGNORECASE).strip()
        
        already_uploaded = False
        for uploaded_topic in uploaded_topics:
            if uploaded_topic.strip() == "": continue
            if chapter_name.lower() in uploaded_topic.lower() or uploaded_topic.lower() in chapter_name.lower():
                already_uploaded = True
                break
                
        if already_uploaded:
            print(f"\n  -> Skipping: {subject} - {chapter_name} (Already Uploaded)")
            continue
            
        print(f"\n  -> Uploading: {subject} - {chapter_name}")
        
        notes_pdf = find_pdf_for_6to9(class_num, subject, chapter_name, "notes")
        book_pdf = find_pdf_for_6to9(class_num, subject, chapter_name, "books")
        
        driver.execute_script("document.getElementById('backdoor_notes').value = '';")
        driver.execute_script("document.getElementById('backdoor_books').value = '';")
        
        if notes_pdf:
            driver.find_element(By.ID, 'backdoor_notes').send_keys(notes_pdf)
            print(f"     [Attached Notes PDF: {os.path.basename(notes_pdf)}]")
        else:
            print(f"     [No Notes PDF found!]")
            
        if class_num == "9":
            if book_pdf:
                driver.find_element(By.ID, 'backdoor_books').send_keys(book_pdf)
                print(f"     [Attached Book PDF: {os.path.basename(book_pdf)}]")
            else:
                print(f"     [No Book PDF found!]")
        else:
            print(f"     [Class {class_num}: Skipping Book upload as requested]")
            
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
                formData.append("stream", "");
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
        
        driver.execute_script(js_script)
        
        result = ""
        while True:
            status = driver.execute_script("return document.body.getAttribute('data-upload-status');")
            if status == 'done':
                result = driver.execute_script("return document.body.getAttribute('data-upload-result');")
                break
            time.sleep(5)
        
        if "SUCCESS" in result:
            print("     ✅ Success!")
        else:
            print(f"     ❌ {result}")
            
        time.sleep(2)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--classes', nargs='+', default=["6", "7", "8", "9"])
    args = parser.parse_args()
    
    print(f"🚀 Starting Selenium Bulk Uploader for Classes {args.classes}...")
    
    # Find all cache files for the specified classes
    cache_files = []
    for file in os.listdir(BASE_DIR):
        if file.startswith("rag_cache_Class_") and file.endswith(".json"):
            class_num = file.replace("rag_cache_Class_", "").split("th")[0]
            if class_num in args.classes:
                cache_files.append(os.path.join(BASE_DIR, file))
                
    if not cache_files:
        print(f"❌ No cache files found for Classes {args.classes} yet!")
        return
        
    driver = setup_browser()
    driver.set_script_timeout(600)
    
    try:
        print(f"\n🌍 Navigating to {TARGET_URL}...")
        driver.get(TARGET_URL)
        time.sleep(3)
        
        driver.execute_script("""
            let form = document.createElement('form');
            form.id = 'backdoor_form';
            let notesInput = document.createElement('input'); notesInput.type = 'file'; notesInput.id = 'backdoor_notes'; form.appendChild(notesInput);
            let booksInput = document.createElement('input'); booksInput.type = 'file'; booksInput.id = 'backdoor_books'; form.appendChild(booksInput);
            document.body.appendChild(form);
        """)
        
        for filepath in cache_files:
            upload_cache_file(driver, filepath)
            
    except Exception as e:
        print(f"\n❌ Browser Automation Error: {e}")
    finally:
        print("\n🛑 Closing Browser...")
        driver.quit()

if __name__ == "__main__":
    import sys
    # We loop to wait for generation to finish.
    print("Waiting for generation process to complete completely before uploading...")
    
    # We check if generation is still active by looking for a running python process
    # But for safety, we assume if called directly, it will just run once.
    # We will let the AI Agent orchestrate when to call this.
    main()
