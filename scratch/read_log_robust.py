import sys
import os

tasks_dir = r"C:\Users\bhask\.gemini\antigravity-ide\brain\85ab0f79-640d-43fa-8e41-000c7383a227\.system_generated\tasks"
if os.path.exists(tasks_dir):
    print("Files in tasks directory:")
    for f in os.listdir(tasks_dir):
        print(f"- {f}")
else:
    print("Tasks directory does not exist.")

