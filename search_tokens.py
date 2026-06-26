from pathlib import Path
import json

transcript_path = Path(r"C:\Users\bhask\.gemini\antigravity-ide\brain\f28215d8-3ae0-4fae-8157-0ab59bacc76b\.system_generated\logs\transcript.jsonl")

if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                content = data.get("content", "")
                if "AWS_BEARER_TOKEN_BEDROCK" in content:
                    print(f"Step {idx}: Length of content {len(content)}")
                    # Find start of token
                    s_idx = content.find("AWS_BEARER_TOKEN_BEDROCK=")
                    if s_idx != -1:
                        token_part = content[s_idx:s_idx+200]
                        print(f"  Token start: {token_part}")
else:
    print("Not found")
