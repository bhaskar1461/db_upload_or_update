import json
import csv
import os

INPUT_FILE = r"C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired_v2.json"
OUTPUT_FILE = r"C:\Users\bhask\Desktop\New folder\output\normalized\notion_board_classes_import.csv"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # We want unique rows since the schema doesn't include subject/textbook details
    unique_rows = {}
    for item in data:
        state = item.get("state", "")
        board_name = item.get("board_name", "")
        class_name = item.get("class_name", "")
        uses_ncert = item.get("uses_ncert", False)
        usage_type = item.get("usage_type", "")
        official_textbook_portal = item.get("source_website", "")
        notes = item.get("notes", "")

        # Create a unique key for deduplication
        key = (state, board_name, class_name)
        
        unique_rows[key] = {
            "state": state,
            "board_name": board_name,
            "class_name": class_name,
            "uses_ncert": "Yes" if uses_ncert else "No",  # Format nicely for checkbox
            "usage_type": usage_type,
            "official_textbook_portal": official_textbook_portal,
            "notes": notes
        }

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
        
        # Sort rows before writing
        sorted_rows = sorted(unique_rows.values(), key=lambda x: (x["state"], x["class_name"]))
        for row in sorted_rows:
            writer.writerow(row)

    print(f"Deduplicated from {len(data)} textbook entries to {len(unique_rows)} class-level entries.")
    print(f"CSV file formatted for Notion saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
