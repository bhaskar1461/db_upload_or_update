import os

BASE_DIR = r"C:\Users\bhask\Desktop\New folder"
CLASS9_DIR = os.path.join(BASE_DIR, "Class 9")

search_topics = [
    "Slumber Did My Spirit Seal",
    "BEGGAR",
    "Kathmandu",
    "If I Were You",
]

print("Searching for textbooks for specific chapters:")
for topic in search_topics:
    found = False
    for root, dirs, files in os.walk(CLASS9_DIR):
        for f in files:
            if topic.lower() in f.lower():
                print(f"  Topic '{topic}' -> Found PDF: {os.path.join(root, f)}")
                found = True
    if not found:
        print(f"  Topic '{topic}' -> NO PDF found in Class 9!")
