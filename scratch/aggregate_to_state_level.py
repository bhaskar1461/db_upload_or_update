import json
import csv
import os

INPUT_FILE = r"C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired_v2.json"
OUTPUT_FILE = r"C:\Users\bhask\Desktop\New folder\output\normalized\notion_state_level_import.csv"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Group by state
    states_data = {}
    
    for item in data:
        state = item.get("state", "")
        if state not in states_data:
            states_data[state] = {
                "board_names": set(),
                "class_names": set(),
                "uses_ncert": set(),
                "usage_types": set(),
                "portals": set(),
                "notes": set()
            }
        
        sd = states_data[state]
        if item.get("board_name"): sd["board_names"].add(item.get("board_name"))
        if item.get("class_name"): sd["class_names"].add(item.get("class_name"))
        sd["uses_ncert"].add(item.get("uses_ncert", False))
        if item.get("usage_type"): sd["usage_types"].add(item.get("usage_type"))
        if item.get("source_website"): sd["portals"].add(item.get("source_website"))
        if item.get("notes"): sd["notes"].add(item.get("notes"))
        
    rows = []
    for state, sd in states_data.items():
        # Sort classes numerically (e.g., "Class 1", "Class 2"...)
        classes = sorted(list(sd["class_names"]), key=lambda x: int(x.replace("Class ", "")) if "Class " in x else 0)
        
        # Uses NCERT: "Yes" if any class uses it, else "No"
        uses_ncert = "Yes" if True in sd["uses_ncert"] else "No"
        
        # Usage type: if multiple types or "partial", set to "partial"
        utypes = sd["usage_types"]
        if "partial" in utypes or len(utypes) > 1:
            usage_type = "partial"
        elif "full" in utypes:
            usage_type = "full"
        else:
            usage_type = "none"
            
        board_name = " / ".join(sorted(list(sd["board_names"])))
        portal = list(sd["portals"])[0] if sd["portals"] else ""
        
        # Combine unique notes
        notes = " | ".join(sorted(list(sd["notes"])))
        
        rows.append({
            "state": state,
            "board_name": board_name,
            "class_name": ", ".join(classes),
            "uses_ncert": uses_ncert,
            "usage_type": usage_type,
            "official_textbook_portal": portal,
            "notes": notes
        })

    fieldnames = [
        "state",
        "board_name",
        "class_name",
        "uses_ncert",
        "usage_type",
        "official_textbook_portal",
        "notes"
    ]

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by state name alphabetically
        rows = sorted(rows, key=lambda x: x["state"])
        for row in rows:
            writer.writerow(row)

    print(f"Aggregated {len(data)} textbook entries down to EXACTLY {len(rows)} State-level entries.")
    print(f"CSV saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
