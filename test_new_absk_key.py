import os
import sys

sys.path.append(r"c:\Users\bhask\Desktop\Archive\New folder\exam_notes_generator")
from core.llm_client import generate_with_llm

user_key = os.getenv("BEDROCK_API_KEY", "YOUR_BEDROCK_API_KEY_HERE")

def test_key(tok):
    print("\n--- Testing new ABSK key ---")
    os.environ["BEDROCK_API_KEY"] = tok
    os.environ["BEDROCK_REGION"] = "us-east-1"
    os.environ["BEDROCK_MODEL"] = "deepseek.v3.2"
    try:
        res = generate_with_llm("You are a helpful assistant.", "Say hello world.", 0.1, 10, 1024)
        print("SUCCESS! Output:", res.encode('ascii', errors='replace').decode('ascii'))
        return True
    except Exception as e:
        print("FAILED:", str(e))
        return False

test_key(user_key)
