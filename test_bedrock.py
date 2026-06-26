"""Test the best reasoning models available on this Bedrock account."""
import os
import json
import urllib.request
import time

API_KEY = os.getenv("BEDROCK_API_KEY", "YOUR_BEDROCK_API_KEY_HERE")

# Best reasoning models from the list, ranked by capability
best_models = [
    "deepseek.v3.2",           # DeepSeek V3.2 - Top-tier reasoning
    "deepseek.v3.1",           # DeepSeek V3.1 - Excellent reasoning
    "mistral.mistral-large-3-675b-instruct",  # 675B param - massive
    "qwen.qwen3-235b-a22b-2507",  # Qwen3 235B - very strong
    "moonshotai.kimi-k2-thinking", # Kimi K2 Thinking - reasoning focused
    "openai.gpt-oss-120b",     # GPT OSS 120B
]

prompt = "You are an exam revision assistant. Generate 3 bullet points about photosynthesis for a Class 8 Science exam. Keep it concise."

for model in best_models:
    print(f"\nTesting: {model}")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert exam revision assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.2,
    }).encode("utf-8")
    
    req = urllib.request.Request(
        "https://bedrock-mantle.ap-south-1.api.aws/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    try:
        start = time.time()
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            elapsed = time.time() - start
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            print(f"  TIME: {elapsed:.1f}s")
            print(f"  TOKENS: {usage}")
            print(f"  OUTPUT:\n{content[:300]}")
            print(f"  --- PASSED ---")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"  HTTP {e.code}: {body[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
