from pathlib import Path
import json

transcript_path = Path(r"C:\Users\bhask\.gemini\antigravity-ide\brain\f28215d8-3ae0-4fae-8157-0ab59bacc76b\.system_generated\logs\transcript.jsonl")

if transcript_path.exists():
    with open(transcript_path, "r", encoding="utf-8") as f:
        # Find the very last user input (which is the current prompt)
        user_inputs = []
        for line in f:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                user_inputs.append(data)
        
        if user_inputs:
            last_input = user_inputs[-1]
            content = last_input.get("content", "")
            print(f"Content length: {len(content)}")
            # Extract key
            idx = content.find("AWS_BEARER_TOKEN_BEDROCK=")
            if idx != -1:
                key_part = content[idx+len("AWS_BEARER_TOKEN_BEDROCK="):].strip()
                # Remove use this new key if present
                if "use this new key" in key_part:
                    key_part = key_part.split("use this new key")[0].strip()
                print("Key length in transcript:", len(key_part))
                print("Key starts with:", key_part[:100])
                print("Key ends with:", key_part[-100:])
                # Print hex representation of the first 20 chars
                print("First 20 chars hex:", key_part[:20].encode('utf-8').hex())
else:
    print("Not found")
