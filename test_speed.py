import urllib.request
import json
import time

def check_speed():
    url = "http://localhost:11434/api/generate"
    # We ask it to write a short paragraph to test the GPU speed
    data = json.dumps({
        "model": "qwen2.5:7b",
        "prompt": "Write a 50 word summary of gravity.",
        "stream": False
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    print("Testing GPU token generation speed. Please wait a few seconds...")
    start_time = time.time()
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            
            # Ollama returns eval_duration in nanoseconds
            eval_duration_sec = result.get("eval_duration", 0) / 1e9
            eval_count = result.get("eval_count", 0)
            
            if eval_duration_sec > 0:
                tps = eval_count / eval_duration_sec
                print("\n=== GPU SPEED TEST RESULTS ===")
                print(f"Model used: {result.get('model')}")
                print(f"Tokens generated: {eval_count}")
                print(f"Time taken: {eval_duration_sec:.2f} seconds")
                print(f"Tokens Per Second: {tps:.2f} t/s")
                print("==============================\n")
            else:
                print("Could not calculate speed from the response.")
                
    except Exception as e:
        print(f"Error testing speed: {e}")
        print("Note: The batch generator might be heavily utilizing the GPU right now, causing the test request to timeout or fail.")

if __name__ == "__main__":
    check_speed()
