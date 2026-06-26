ENGLISH_MAPPING = {
    "6th": {
        "Prose": [
            "Who Did Patrick's Homework",
            "How the Dog Found Himself a New Master",
            "Taro's Reward",
            "An Indian-American Woman in Space: Kalpana Chawla",
            "A Different Kind of School",
            "Who I Am",
            "Fair Play",
            "A Game of Chance",
            "Desert Animals",
            "The Banyan Tree"
        ],
        "Poem": [
            "A House, A Home",
            "The Kite",
            "The Quarrel",
            "Beauty",
            "Where Do All the Teachers Go?",
            "The Wonderful Words",
            "Vocation",
            "What If"
        ],
        "Supplementary": [
            "A Tale of Two Birds",
            "The Friendly Mongoose",
            "The Shepherd's Treasure",
            "The Old-Clock Shop",
            "Tansen",
            "The Monkey and the Crocodile",
            "The Wonder Called Sleep",
            "A Pact with the Sun",
            "What Happened to the Reptiles",
            "A Strange Wrestling Match"
        ]
    },
    "7th": {
        "Prose": [
            "Three Questions",
            "A Gift of Chappals",
            "Gopal and the Hilsa Fish",
            "The Ashes That Made Trees Bloom",
            "Quality",
            "Expert Detectives",
            "The Invention of Vita-Wonk",
            "A Homage to Our Brave Soldiers"
        ],
        "Poem": [
            "The Squirrel",
            "The Rebel",
            "The Shed",
            "Chivvy",
            "Trees",
            "Mystery of the Talking Fan",
            "Dad and the Cat and the Tree",
            "Meadow Surprises",
            "Garden Snake"
        ],
        "Supplementary": [
            "The Tiny Teacher",
            "Bringing Up Kari",
            "Golu Grows a Nose",
            "Chandni",
            "The Bear Story",
            "A Tiger in the House",
            "An Alien Hand"
        ]
    },
    "8th": {
        "Prose": [
            "The Best Christmas Present in the World",
            "The Tsunami",
            "Glimpses of the Past",
            "Bepin Choudhury's Lapse of Memory",
            "The Summit Within",
            "This is Jody's Fawn",
            "A Visit to Cambridge",
            "A Short Monsoon Diary"
        ],
        "Poem": [
            "The Ant and the Cricket",
            "Geography Lesson",
            "Macavity: The Mystery Cat",
            "The Last Bargain",
            "The School Boy",
            "The Duck and the Kangaroo",
            "When I Set Out for Lyonnesse",
            "On the Grasshopper and Cricket"
        ],
        "Supplementary": [
            "How the Camel Got His Hump",
            "Children at Work",
            "The Selfish Giant",
            "The Treasure Within",
            "Princess September",
            "The Fight",
            "Jalebis",
            "Ancient Education System of India"
        ]
    }
}

import re

def normalize_text(text):
    # Remove all non-alphanumeric chars (keep spaces but replace with single space)
    # also remove common words like 'new', 'the', 'a', 'an' just to be safe if needed, 
    # but actually just removing punctuation and lowercasing is usually enough.
    text = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    return text

def get_english_subject_type(class_name, original_subject, clean_topic):
    if original_subject != "English":
        return original_subject
    
    cls_key = None
    if "6" in class_name: cls_key = "6th"
    elif "7" in class_name: cls_key = "7th"
    elif "8" in class_name: cls_key = "8th"
    
    if not cls_key:
        return original_subject
        
    mapping = ENGLISH_MAPPING.get(cls_key, {})
    
    # Try to find a match in the mapping
    topic_norm = normalize_text(clean_topic)
    if not topic_norm:
        return original_subject
        
    for prose in mapping.get("Prose", []):
        if normalize_text(prose) in topic_norm or topic_norm in normalize_text(prose):
            return "English (Prose)"
            
    for poem in mapping.get("Poem", []):
        if normalize_text(poem) in topic_norm or topic_norm in normalize_text(poem):
            return "English (Poem)"
            
    for supp in mapping.get("Supplementary", []):
        if normalize_text(supp) in topic_norm or topic_norm in normalize_text(supp):
            return "English (Supplementary)"
            
    return original_subject
