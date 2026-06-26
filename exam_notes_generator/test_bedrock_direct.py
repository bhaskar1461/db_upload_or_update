import os
import httpx

user_raw_absk = os.getenv("BEDROCK_API_KEY", "YOUR_BEDROCK_API_KEY_HERE")
user_base64_only = "YOUR_BASE64_KEY_HERE"
decoded_key = "YOUR_DECODED_KEY_HERE"

url = "https://bedrock-mantle.us-east-1.api.aws/v1/chat/completions"
payload = {
    "model": "deepseek.v3.2",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello"}
    ],
    "max_tokens": 10
}

keys_to_test = {
    "User Raw ABSK string (starts with ABSKQ...)": user_raw_absk,
    "User Base64 string only (starts with Q...)": user_base64_only,
    "Decoded key string (starts with Bedrock...)": decoded_key
}

for desc, key in keys_to_test.items():
    print(f"\n--- Testing Key: {desc} ---")
    for host in [None, "bedrock.amazonaws.com", "bedrock-mantle.us-east-1.api.aws"]:
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        if host:
            headers["Host"] = host
            print(f"  Testing with Host: {host}")
        else:
            print("  Testing with default Host")
            
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=10)
            print("    Status:", response.status_code)
            print("    Body:", response.text)
        except Exception as e:
            print("    Error:", e)
