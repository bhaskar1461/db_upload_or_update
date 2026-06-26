import json, os

entries = []

# --- NCERT textbook name maps ---
ncert_names_6 = {"Hindi": "Vasant Bhag I", "English": "Honeysuckle", "Sanskrit": "Ruchira Bhag I",
                  "Mathematics": "Mathematics", "Science": "Science", "Social Science": ""}
ncert_names_7 = {"Hindi": "Vasant Bhag II", "English": "Honeycomb", "Sanskrit": "Ruchira Bhag II",
                  "Mathematics": "Mathematics", "Science": "Science", "Social Science": ""}
ncert_names_8 = {"Hindi": "Vasant Bhag III", "English": "Honeydew", "Sanskrit": "Ruchira Bhag III",
                  "Mathematics": "Mathematics", "Science": "Science", "Social Science": ""}
ncert_names_9 = {"Hindi": "Kshitij Bhag I", "English": "Beehive",
                  "Mathematics": "Mathematics", "Science": "Science", "Social Science": ""}
ncert_names_10 = {"Hindi": "Kshitij Bhag II", "English": "First Flight",
                   "Mathematics": "Mathematics", "Science": "Science", "Social Science": ""}
ncert_by_class = {6: ncert_names_6, 7: ncert_names_7, 8: ncert_names_8, 9: ncert_names_9, 10: ncert_names_10}

def make_entry(state, board, cls, subj, uses_ncert, usage_type, is_ncert, tname,
               publisher, medium, dl_link, source, conf, notes=""):
    return {
        "state": state,
        "board_name": board,
        "class_name": f"Class {cls}",
        "subject_name": subj,
        "uses_ncert": uses_ncert,
        "usage_type": usage_type,
        "is_ncert_book": is_ncert,
        "textbook_name": tname,
        "publisher": publisher,
        "medium": medium,
        "official_download_link": dl_link,
        "academic_year": "2025-26",
        "pdf_available": True,
        "source_website": source,
        "notes": notes,
        "repaired_fields": [],
        "confidence_score": conf,
        "verification_status": "PARTIALLY_VERIFIED"
    }

# ===================== PUNJAB =====================
PJ_BOARD = "Punjab School Education Board (PSEB)"
PJ_PUB = "PSEB"
PJ_SRC = "https://www.pseb.ac.in"
PJ_DL = "https://www.pseb.ac.in"
PJ_MED = "Punjabi"
PJ_CONF = 75

# Classes 1-5
for cls in range(1, 6):
    for subj in ["Punjabi", "English", "Mathematics", "EVS"]:
        entries.append(make_entry("Punjab", PJ_BOARD, cls, subj, False, "none", False, "",
                                  PJ_PUB, PJ_MED, PJ_DL, PJ_SRC, PJ_CONF))

# Classes 6-8
for cls in range(6, 9):
    for subj in ["Punjabi", "English", "Hindi", "Mathematics", "Science", "Social Science"]:
        entries.append(make_entry("Punjab", PJ_BOARD, cls, subj, False, "none", False, "",
                                  PJ_PUB, PJ_MED, PJ_DL, PJ_SRC, PJ_CONF))

# Classes 9-10
for cls in range(9, 11):
    for subj in ["Punjabi", "English", "Hindi", "Mathematics", "Science", "Social Science"]:
        entries.append(make_entry("Punjab", PJ_BOARD, cls, subj, False, "none", False, "",
                                  PJ_PUB, PJ_MED, PJ_DL, PJ_SRC, PJ_CONF))

# ===================== HARYANA =====================
HR_BOARD = "Board of School Education Haryana (BSEH)"
HR_PUB = "SCERT Haryana"
HR_SRC = "https://bseh.org.in"
HR_DL = "https://scertharyana.gov.in"
HR_MED = "Hindi"
HR_CONF = 80

# Classes 1-5 (own curriculum)
for cls in range(1, 6):
    for subj in ["Hindi", "English", "Mathematics", "EVS"]:
        entries.append(make_entry("Haryana", HR_BOARD, cls, subj, False, "none", False, "",
                                  HR_PUB, HR_MED, HR_DL, HR_SRC, HR_CONF))

# Classes 6-8 (own curriculum)
for cls in range(6, 9):
    for subj in ["Hindi", "English", "Sanskrit", "Mathematics", "Science", "Social Science"]:
        entries.append(make_entry("Haryana", HR_BOARD, cls, subj, False, "none", False, "",
                                  HR_PUB, HR_MED, HR_DL, HR_SRC, HR_CONF))

# Classes 9-10 (NCERT adopted)
for cls in [9, 10]:
    nmap = ncert_by_class[cls]
    for subj in ["Hindi", "English", "Mathematics", "Science", "Social Science"]:
        tname = nmap.get(subj, "")
        note = "NCERT textbook adopted by Haryana for this class and subject"
        if subj == "Social Science":
            note = "NCERT textbook adopted by Haryana; Social Science comprises multiple NCERT books (History, Geography, Political Science, Economics)"
        entries.append(make_entry("Haryana", HR_BOARD, cls, subj, True, "full", True, tname,
                                  "NCERT", HR_MED, HR_DL, HR_SRC, HR_CONF, note))

# ===================== HIMACHAL PRADESH =====================
HP_BOARD = "Himachal Pradesh Board of School Education (HPBOSE)"
HP_PUB = "HPBOSE"
HP_SRC = "https://hpbose.org"
HP_DL = "https://hpbose.org"
HP_MED = "Hindi"
HP_CONF = 75

# Classes 1-5 (own curriculum)
for cls in range(1, 6):
    for subj in ["Hindi", "English", "Mathematics", "EVS"]:
        entries.append(make_entry("Himachal Pradesh", HP_BOARD, cls, subj, False, "none", False, "",
                                  HP_PUB, HP_MED, HP_DL, HP_SRC, HP_CONF))

# Classes 6-8 (own curriculum)
for cls in range(6, 9):
    for subj in ["Hindi", "English", "Sanskrit", "Mathematics", "Science", "Social Science"]:
        entries.append(make_entry("Himachal Pradesh", HP_BOARD, cls, subj, False, "none", False, "",
                                  HP_PUB, HP_MED, HP_DL, HP_SRC, HP_CONF))

# Classes 9-10 (NCERT adopted)
for cls in [9, 10]:
    nmap = ncert_by_class[cls]
    for subj in ["Hindi", "English", "Mathematics", "Science", "Social Science"]:
        tname = nmap.get(subj, "")
        note = "NCERT textbook adopted by Himachal Pradesh for this class and subject"
        if subj == "Social Science":
            note = "NCERT textbook adopted by HP; Social Science comprises multiple NCERT books (History, Geography, Political Science, Economics)"
        entries.append(make_entry("Himachal Pradesh", HP_BOARD, cls, subj, True, "full", True, tname,
                                  "NCERT", HP_MED, HP_DL, HP_SRC, HP_CONF, note))

# ===================== UTTARAKHAND =====================
UK_BOARD = "Uttarakhand Board of School Education (UBSE)"
UK_PUB = "UBSE / SCERT Uttarakhand"
UK_SRC = "https://ubse.uk.gov.in"
UK_DL = "https://ubse.uk.gov.in"
UK_MED = "Hindi"
UK_CONF = 75

# Classes 1-5 (partial NCERT)
for cls in range(1, 6):
    for subj in ["Hindi", "English", "Mathematics", "EVS"]:
        entries.append(make_entry("Uttarakhand", UK_BOARD, cls, subj, True, "partial", False, "",
                                  UK_PUB, UK_MED, UK_DL, UK_SRC, UK_CONF,
                                  "Uttarakhand partially adopts NCERT curriculum for primary classes"))

# Classes 6-8 (full NCERT)
for cls in range(6, 9):
    nmap = ncert_by_class[cls]
    for subj in ["Hindi", "English", "Sanskrit", "Mathematics", "Science", "Social Science"]:
        tname = nmap.get(subj, "")
        note = "NCERT textbook adopted by Uttarakhand"
        if subj == "Social Science":
            note = "NCERT textbook adopted by Uttarakhand; Social Science comprises multiple NCERT books"
        entries.append(make_entry("Uttarakhand", UK_BOARD, cls, subj, True, "full", True, tname,
                                  "NCERT", UK_MED, UK_DL, UK_SRC, UK_CONF, note))

# Classes 9-10 (full NCERT)
for cls in [9, 10]:
    nmap = ncert_by_class[cls]
    for subj in ["Hindi", "English", "Mathematics", "Science", "Social Science"]:
        tname = nmap.get(subj, "")
        note = "NCERT textbook adopted by Uttarakhand"
        if subj == "Social Science":
            note = "NCERT textbook adopted by Uttarakhand; Social Science comprises multiple NCERT books"
        entries.append(make_entry("Uttarakhand", UK_BOARD, cls, subj, True, "full", True, tname,
                                  "NCERT", UK_MED, UK_DL, UK_SRC, UK_CONF, note))

# Write output
out_path = os.path.join(os.path.dirname(__file__), "north_states_complete.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

# Summary
from collections import Counter
state_counts = Counter(e["state"] for e in entries)
print(f"Total entries: {len(entries)}")
for st, cnt in state_counts.items():
    print(f"  {st}: {cnt}")
print(f"Written to: {out_path}")
