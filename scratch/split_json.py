import json
import os
import math

INPUT_FILE = r"C:\Users\bhask\Desktop\New folder\output\normalized\state_board_check_repaired_v2.json"
OUTPUT_DIR = r"C:\Users\bhask\Desktop\New folder\output\normalized\notion_parts"
CHUNK_SIZE = 250  # Number of entries per file

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    total_entries = len(data)
    num_chunks = math.ceil(total_entries / CHUNK_SIZE)
    
    print(f"Total entries: {total_entries}")
    print(f"Splitting into {num_chunks} files of up to {CHUNK_SIZE} entries each...")
    
    for i in range(num_chunks):
        start_idx = i * CHUNK_SIZE
        end_idx = start_idx + CHUNK_SIZE
        chunk = data[start_idx:end_idx]
        
        output_file = os.path.join(OUTPUT_DIR, f"state_board_part_{i+1:02d}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
            
        print(f"Created: {output_file} ({len(chunk)} entries)")

    print("\nAll files have been successfully split and are ready for Notion!")

if __name__ == '__main__':
    main()
