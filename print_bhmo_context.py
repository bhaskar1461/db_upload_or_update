from pathlib import Path
import json

transcript_path = Path(r"C:\Users\bhask\.gemini\antigravity-ide\brain\f28215d8-3ae0-4fae-8157-0ab59bacc76b\.system_generated\logs\transcript.jsonl")

if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if "BhMo%2BgW" in line and "BhMo%2BXGW" in line:
                data = json.loads(line)
                print(f"Line {idx}:")
                # Look for tool_calls or content
                for k, v in data.items():
                    val_str = str(v)
                    if len(val_str) > 1000:
                        # Print occurrences of BhMo
                        print(f"  {k} (length {len(val_str)})")
                        pos = val_str.find("BhMo")
                        while pos != -1:
                            print(f"    Occurrence: ...{val_str[pos-30:pos+30]}...")
                            pos = val_str.find("BhMo", pos+1)
                    else:
                        print(f"  {k}: {val_str}")
else:
    print("Not found")
