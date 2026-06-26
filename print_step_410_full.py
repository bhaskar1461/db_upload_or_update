from pathlib import Path
import json

transcript_path = Path(r"C:\Users\bhask\.gemini\antigravity-ide\brain\f28215d8-3ae0-4fae-8157-0ab59bacc76b\.system_generated\logs\transcript.jsonl")

if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx == 410:
                data = json.loads(line)
                for k, v in data.items():
                    print(f"{k}: {str(v)[:500]}")
                break
else:
    print("Not found")
