import os
import sys

sys.path.append(r"c:\Users\bhask\Desktop\Archive\New folder\exam_notes_generator")
from core.llm_client import generate_with_llm

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(r"C:\Users\bhask\Desktop\Study Materials\.env"), override=True)

# Set BEDROCK_API_KEY from AWS_BEARER_TOKEN_BEDROCK
os.environ["BEDROCK_API_KEY"] = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
os.environ["BEDROCK_REGION"] = "us-east-1"
os.environ["BEDROCK_MODEL"] = "deepseek.v3.2"

try:
    print(f"\n--- Trying Model: {os.environ['BEDROCK_MODEL']} ---")
    res = generate_with_llm("You are a helpful assistant.", "Say hello world.", 0.1, 10, 1024)
    print("SUCCESS! Output:", res.encode('ascii', errors='replace').decode('ascii'))
except Exception as e:
    print("FAILED:", str(e))
