import sys
sys.stdout.reconfigure(encoding='utf-8')

log_file = 'exam_notes_generator/logs/all_exam_generation.log'
try:
    with open(log_file, 'r', encoding='utf-16') as f:
        lines = f.readlines()
        
    generated = 0
    total = 0
    classes = set()
    current_class = ""
    for line in lines:
        if "Found" in line and "topics for" in line:
            # Found 42 topics for Class 11th_Commerce
            pass # just info
        if "Successfully generated notes for" in line:
            generated += 1
            if "Class 12th" in line:
                current_class = "12th"
        if "Finished all exam PDF generation" in line:
            print("Generation is already FINISHED.")
            
    print(f"Total topics generated across all classes so far: {generated}")
    print("Last 10 lines of the log:")
    for line in lines[-10:]:
        print(line.strip())
        
except Exception as e:
    print(f"Error: {e}")
