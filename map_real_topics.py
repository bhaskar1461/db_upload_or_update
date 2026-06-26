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

# Mappings of Class -> Subject -> Chapter Number -> Real Name
MAPPINGS = {
    "7": {
        "science": {
            "1": "Nutrition in Plants",
            "2": "Nutrition in Animals",
            "3": "Heat",
            "4": "Acids, Bases and Salts",
            "5": "Physical and Chemical Changes",
            "6": "Respiration in Organisms",
            "7": "Transportation in Animals and Plants",
            "8": "Reproduction in Plants",
            "9": "Motion and Time",
            "10": "Electric Current and its Effects",
            "11": "Light",
            "12": "Forests: Our Lifeline",
            "13": "Wastewater Story",
            "14": "Winds, Storms and Cyclones",
            "15": "Light",
            "16": "Water: A Precious Resource",
            "17": "Forests: Our Lifeline",
            "18": "Wastewater Story"
        },
        "Sanskrit": {
            "1": "Subhashitani",
            "2": "Durbuddhi Vinashyati",
            "3": "Swavalambanam",
            "4": "Pandita Ramabai",
            "5": "Sadacharah",
            "6": "Sankalpah Siddhidkayakah",
            "7": "Trivarnah Dhvajah",
            "8": "Ahamapi Vidyalayam Gamishyami",
            "9": "Vishvabandhutvam",
            "10": "Samavayo Hi Durjayah",
            "11": "Vidyadhanam",
            "12": "Amritam Samskritam",
            "13": "Lalanageetam",
            "14": "Ahahaa! Cha Evam Ma",
            "15": "Matulachandra"
        },
        "सामाजिक विज्ञान (Social Science)": {
            "1": "Environment",
            "2": "Inside Our Earth",
            "3": "Our Changing Earth",
            "4": "Air",
            "5": "Water",
            "6": "Human Environment Interactions",
            "7": "Life in the Deserts",
            "8": "Life in the Tropical and Subtropical Regions",
            "9": "Life in the Temperate Grasslands",
            "10": "New Kings and Kingdoms"
        }
    },
    "8": {
        "science": {
            "1": "Crop Production and Management",
            "2": "Microorganisms: Friend and Foe",
            "3": "Synthetic Fibres and Plastics",
            "4": "Materials: Metals and Non-Metals",
            "5": "Coal and Petroleum",
            "6": "Combustion and Flame",
            "7": "Conservation of Plants and Animals",
            "8": "Cell - Structure and Functions",
            "9": "Reproduction in Animals",
            "10": "Reaching the Age of Adolescence",
            "11": "Force and Pressure",
            "12": "Friction",
            "13": "Sound",
            "14": "Chemical Effects of Electric Current",
            "15": "Some Natural Phenomena",
            "16": "Light",
            "17": "Stars and the Solar System",
            "18": "Pollution of Air and Water"
        },
        "हिंदी (Hindi)": {
            "1": "Dhwani (ध्वनि)",
            "2": "Lakh ki Chudiyan (लाख की चूड़ियाँ)",
            "3": "Bus ki Yatra (बस की यात्रा)",
            "4": "Deewano ki Hasti (दीवानों की हस्ती)",
            "5": "Chitthiyon ki Anuthi Duniya (चिट्ठियों की अनूठी दुनिया)",
            "6": "Bhagwan ke Dakiye (भगवान के डाकिए)",
            "7": "Kya Nirash Hua Jaye (क्या निराश हुआ जाए)",
            "8": "Yeh Sabse Kathin Samay Nahi (यह सबसे कठिन समय नहीं)",
            "9": "Kabir ki Sakhiyan (कबीर की साखियाँ)",
            "10": "Kaamchor (कामचोर)",
            "11": "Jab Cinema ne Bolna Seekha (जब सिनेमा ने बोलना सीखा)",
            "12": "Sudama Charit (सुदामा चरित)",
            "13": "Jahan Pahiya Hai (जहाँ पहिया है)",
            "14": "Akbari Lota (अकबरी लोटा)",
            "15": "Sur ke Pad (सूर के पद)",
            "16": "Paani ki Kahani (पानी की कहानी)",
            "17": "Baaj aur Saanp (बाज और साँप)",
            "18": "Topi (टोपी)",
            "19": "Grammar / Other"
        },
        "सामाजिक विज्ञान (Social Science)": {
            "1": "The Indian Constitution",
            "2": "Understanding Secularism",
            "3": "Why Do We Need a Parliament?",
            "4": "Understanding Laws",
            "5": "Judiciary",
            "6": "Understanding Our Criminal Justice System",
            "7": "Understanding Marginalisation",
            "8": "Confronting Marginalisation",
            "9": "Public Facilities",
            "10": "Law and Social Justice"
        }
    },
    "9": {
        "सामाजिक अध्ययन (Social Studies)": {
            "6": "Population"
        }
    }
}

cursor.execute("SELECT id, class, subject, short_notes FROM ai_notes_new WHERE topic IS NULL OR topic = ''")
rows = cursor.fetchall()
updates = 0

for row_id, cls, subj, notes in rows:
    if not notes: continue
    
    # Extract "Chapter: Chapter X" from short_notes
    match = re.search(r"Chapter:\s*Chapter\s*(\d+)", notes, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"Chapter:\s*(\d+)", notes, flags=re.IGNORECASE)
        
    if match:
        chapter_num = match.group(1)
        
        # Look up the real name
        real_name = None
        if cls in MAPPINGS and subj in MAPPINGS[cls]:
            real_name = MAPPINGS[cls][subj].get(chapter_num)
            
        if not real_name:
            # Fallback if chapter number is not in map
            real_name = f"Chapter {chapter_num}"
            
        cursor.execute("UPDATE ai_notes_new SET topic = %s WHERE id = %s", (real_name, row_id))
        updates += 1
        print(f"Mapped ID {row_id} ({cls} {subj} Ch {chapter_num}) -> '{real_name}'")

print(f"\nFixed {updates} empty topics with real names.")
conn.commit()
cursor.close()
conn.close()
