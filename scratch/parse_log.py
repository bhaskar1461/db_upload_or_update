import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

LOG_PATH = r"C:\Users\bhask\Desktop\New folder\batch_generation.log" # Wait, wait! The log path we want is:
# C:\Users\bhask\.gemini\antigravity\brain\00c506b5-f4eb-4019-b3ea-165e8b5903f0\.system_generated\tasks\task-2325.log
LOG_PATH = r"C:\Users\bhask\.gemini\antigravity\brain\00c506b5-f4eb-4019-b3ea-165e8b5903f0\.system_generated\tasks\task-2325.log"

if os.path.exists(LOG_PATH):
    with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    print(f"Total lines in log: {len(lines)}")
    
    print("\nChecking for 'Failed' or '❌' lines:")
    failed_lines = [l.strip() for l in lines if 'failed' in l.lower() or '❌' in l]
    print(f"Found {len(failed_lines)} failed lines. First 10:")
    for l in failed_lines[:10]:
        print(f"  {l}")
        
    print("\nChecking for 'Skipping' or '⚠️' lines:")
    skipping_lines = [l.strip() for l in lines if 'skipping' in l.lower() or '⚠️' in l]
    print(f"Found {len(skipping_lines)} skipping lines. First 10:")
    for l in skipping_lines[:10]:
        print(f"  {l}")

    print("\nChecking for empty chapter name or empty string matches:")
    empty_matches = [l.strip() for l in lines if "''" in l or '""' in l or 'empty' in l.lower()]
    print(f"Found {len(empty_matches)} lines with empty quotes/empty. First 10:")
    for l in empty_matches[:10]:
        print(f"  {l}")
        
    print("\nChecking for patterns containing 178016 in the log:")
    pattern_matches = [l.strip() for l in lines if '178016' in l]
    print(f"Found {len(pattern_matches)} lines. First 10:")
    for l in pattern_matches[:10]:
        print(f"  {l}")
else:
    print(f"Log path does not exist: {LOG_PATH}")
