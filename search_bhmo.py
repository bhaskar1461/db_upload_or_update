from pathlib import Path
import json

transcript_path = Path(r"C:\Users\bhask\.gemini\antigravity-ide\brain\f28215d8-3ae0-4fae-8157-0ab59bacc76b\.system_generated\logs\transcript.jsonl")

if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            content = str(data)
            if "BhMo" in content:
                print(f"Step {idx}: Type={data.get('type')}, Source={data.get('source')}")
                if "BhMo%2BgW" in content:
                    print("  Contains BhMo%2BgW")
                if "BhMo%2BXGW" in content:
                    print("  Contains BhMo%2BXGW")
else:
    print("Not found")
