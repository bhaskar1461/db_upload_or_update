import json
import csv
import os

INPUT_FILE = r"C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired_v2.json"
OUTPUT_FILE = r"C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired.csv"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if not data:
        print("No data found in JSON.")
        return

    # Extract all possible keys from the first few items to form the header
    keys = list(data[0].keys())

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        
        for item in data:
            # Handle list elements (like repaired_fields) by joining them into a string
            row = {}
            for k in keys:
                val = item.get(k, "")
                if isinstance(val, list):
                    row[k] = ", ".join(str(v) for v in val)
                else:
                    row[k] = val
            writer.writerow(row)

    print(f"Successfully converted {len(data)} entries to CSV.")
    print(f"CSV file saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
