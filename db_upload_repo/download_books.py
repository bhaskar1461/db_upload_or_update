import os
import urllib.request
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

base_dir = r"c:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\class 11 and 12 text book"
os.makedirs(base_dir, exist_ok=True)

subjects = ["mh", "ph", "ch", "bo", "ec", "ac", "bs", "hs", "gy", "ps", "sy", "hp", "pe", "st"]
parts = ["1", "2", "3"]

codes_to_try = []
for cls in ["k", "l"]:
    # Hindi medium subjects
    for sub in subjects:
        for part in parts:
            codes_to_try.append(f"{cls}h{sub}{part}")
    
    # English subjects
    if cls == "k":
        eng_books = ["hb", "sp", "ww"]
        hin_books = ["at", "vt", "nt", "tl"]
    else:
        eng_books = ["fl", "vt", "kl"]
        hin_books = ["at", "vt", "nt", "tl"]
        
    for eb in eng_books:
        codes_to_try.append(f"{cls}e{eb}1")
    for hb in hin_books:
        codes_to_try.append(f"{cls}h{hb}1")

print(f"Total codes to try: {len(codes_to_try)}")

def download_file(code):
    url = f"https://ncert.nic.in/textbook/pdf/{code}dd.zip"
    filepath = os.path.join(base_dir, f"{code}.zip")
    
    if os.path.exists(filepath):
        return True # already downloaded

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                if response.status != 200:
                    return False
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            time.sleep(2)
            continue
        except Exception as e:
            time.sleep(2)
            continue
            
        # If HEAD succeeds, download
        try:
            print(f"Downloading {code}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
                with open(filepath, "wb") as f:
                    f.write(response.read())
            print(f"Success: {code}")
            return True
        except Exception as e:
            print(f"Download failed for {code}: {e}")
            time.sleep(2)
            
    return False

success_count = 0
for code in codes_to_try:
    if download_file(code):
        success_count += 1

print(f"Finished. Downloaded {success_count} books.")
