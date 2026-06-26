import requests
r = requests.post("http://localhost:11434/api/generate", json={
    "model": "qwen2.5:7b",
    "prompt": "Write 3 sentences about the solar system.",
    "stream": False,
    "options": {"num_ctx": 16384}
})
d = r.json()
count = d.get("eval_count", 0)
dur = d.get("eval_duration", 1)
tps = count / (dur / 1e9)
print(f"Generated: {count} tokens")
print(f"Speed: {tps:.1f} tokens/sec")
print(f"Total time: {d.get('total_duration', 0) / 1e9:.1f}s")
