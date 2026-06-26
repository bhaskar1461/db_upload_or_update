from pathlib import Path
import json

transcript_path = Path(r"C:\Users\bhask\.gemini\antigravity-ide\brain\f28215d8-3ae0-4fae-8157-0ab59bacc76b\.system_generated\logs\transcript.jsonl")

if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if "BhMo%2BgW" in line:
                data = json.loads(line)
                print(f"File Line {idx}: step_index={data.get('step_index')}, type={data.get('type')}, source={data.get('source')}")
                # Print the content or tool_calls
                content = data.get("content")
                if content:
                    print(f"  Content: {content[:1000]}")
                tc = data.get("tool_calls")
                if tc:
                    print(f"  Tool Calls: {str(tc)[:1000]}")
else:
    print("Not found")
