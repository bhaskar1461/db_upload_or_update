import json
import os

ASSAM_PATH = r"C:\Users\bhask\Desktop\New folder\scratch\assam_complete.json"
ALL_STATES_PATH = r"C:\Users\bhask\Desktop\New folder\scratch\all_states_generated.json"
OUTPUT_PATH = r"C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired_v2.json"

def main():
    # Load Assam
    with open(ASSAM_PATH, 'r', encoding='utf-8') as f:
        assam_data = json.load(f)
    
    # Load all other states
    with open(ALL_STATES_PATH, 'r', encoding='utf-8') as f:
        other_states = json.load(f)
    
    # Merge
    merged = assam_data + other_states
    
    # Sort for consistency
    merged.sort(key=lambda x: (x.get('state', ''), x.get('class_name', ''), x.get('subject_name', '')))
    
    # Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully merged {len(assam_data)} Assam entries and {len(other_states)} other entries.")
    print(f"Total entries in final dataset: {len(merged)}")
    print(f"Saved to: {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
