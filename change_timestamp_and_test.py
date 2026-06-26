import base64
import os
import sys
import urllib.parse
import datetime

sys.path.append(r"c:\Users\bhask\Desktop\Archive\New folder\exam_notes_generator")
from core.llm_client import generate_with_llm

token_with_xgw = "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFXVFhWM0M1M0dKRlBSNFdaJTJGMjAyNjA2MjAlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA2MjBUMTI0MDQ0WiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFQTBhQ1hWekxXVmhjM1F0TVNKSE1FVUNJUUR1JTJCbXRobGxFazlaUUgya3J0eUpDcWd2b2JGcXRHR1IlMkJNMFN4cDV0JTJGMGNnSWdTaEJFYmdzcEZaN1hab2ZES2R6ZVZmN1hEWk5vOGJSaW5pT2wwTksxek5jcXNnTUkxdiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRkFSQUFHZ3cwTlRRM01EZ3pOamt5TnpBaURCOWx5c1Zua1h3azdrJTJGa0ZpcUdBJTJGS3IlMkJ1bzNmJTJGTnRkcmJZcm0zTGJ0M0RxS2dVY05zaFpzbWFBOFcyUmtaSVRwYXQlMkJHZUNJaWZQcFBFMGhHZW5CampqamdvOHNOSTlYaVJGSWFIeEQzSDZ6cG5JZktKJTJCTldwUVBWNWhpU0dtSWZoSmhSMExxWHJFb29KYTZYbmNkRUVuVlUlMkJmY2lXcHhlazJONnFrMDZSS200Z1F5SklVZ1NKdzFvOVdhd0c3WmtkWGExelFzdUJSdHAxbjNjMVNWSHFFZEwxOHFMeEVuVkY1b0NxU3lZdjJ5NnNuM281MWRNWjNxNGN3YVlkdVRMQ0xISXhBWk9qeExJaXNpV0hlNlRhYldPcER0SkolMkY4Yk9SblFiVGZqRUJoTW8lMkJYR1clMkJNTnclMkZCNzl0U3JvWFZDMGtXTXFQWEFWbVNZOTdPcGkzdFhtJTJGJTJGMTJDdmpqWjRuelNKWDFmZlRBVTlyVEFaYk94MUpGUFkwWnRyYUdsYjI4R0pZaFFtMUZxV2hsNmM5YW5ucFlOZERheHVLM2xDWjNaTklVZXdMQmRJZmgyYU01amdKWldDYjQ1b3dNWnhtbXZPODRYZnV2NjJhZ3FKcTZwVm1XVSUyQmIwc0VMOWowaGhKQkN4Qjh6TSUyQllJYUZTJTJCNmlOUEJVcXZFUzZ6RURGdFI3N0glMkJRdzk3UFBaY255aUFSRXBnWmRPc3NuekMxbE5yUkJqcmVBaSUyRm5RYVhvTG5PaUdoODJRTjh0MnlXTCUyRlglMkI5VUxqcjRRZ3lKWnpkSjFseXQ0dkg0NlFzZXRZTmVWQ3B5cGFMMUc5dDNXcU9VM1lEMTRKS1ZXSW9LWW9ETEc0JTJCYmk4JTJGY1dMSGVyeDJMTkFMSWJ2eiUyRjZ0VjZkRXJTSGJNZk9vejE1MUpmc3FreWFOR21CdERTTmpia1FhNWhGek12Zm01cWh0T1ElMkZ6Z3klMkJlUTlvRlJWME5Sb2ZjRFMzYlZUM0RGbkptcWJGdEJKSlh3eUNVRUpENnFiUEFJa3AyNDVuOE9hRlUlMkZwUEczcXkyJTJCciUyQmJWc2luMXdGeWVPTGxTcUFtZmRQZVVPS1ZhV0dhZ1VkdVV2ZGtlRzNKRmoxalBmUVNwZGlmRFplb08lMkI3eUR6VjU3Y2hBanR3Yzdld0p2UnZ3aUx1U2l3ekVBJTJCN2dxZwhoQURiTCUyQnUzTVVPNjNFMCUyRiUyQkJVVGttVFFIRFExUkhGVEk4T0Y2d2NCcWJaZ0ZRWlA5TWlYVHNIcUxkYTJoZEc2Y0tjSWx6ejBWUGIlMkJ5RDVabTJheXhubFBXNmlnaWlhcGhzb3UlMkZWdU9YQ1ZrYmpJbW05c3FqQzRqMUclMkJwdmxUWUpkVFZnQSZYLUFtei1TaWduYXR1cmU9ZGVhODVjNDE4YjMxYzI3N2JkZjVkNWUyNDE5OWIwY2VlOTdmNDQzOGUyOWI2MjNiMjkwY2FmM2UyYWZlOGZkMiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmVmVyc2lvbj0x"

# We unquote and decode the token
base64_part_encoded = token_with_xgw.replace("bedrock-api-key-", "")
base64_part_unquoted = urllib.parse.unquote(base64_part_encoded)
decoded_bytes = base64.b64decode(base64_part_unquoted)
decoded_str = decoded_bytes.decode('latin1')

# The token contains both XGW and date "20260620T124044Z"
# Let's replace the date with the current UTC timestamp
current_utc = datetime.datetime.now(datetime.timezone.utc)
new_date_str = current_utc.strftime("%Y%m%dT%H%M%SZ")
# Also format credentials date segment
new_cred_date = current_utc.strftime("%Y%m%d")

print(f"Replacing date in credentials with: {new_cred_date}")
print(f"Replacing date with: {new_date_str}")

# Perform replacement for date
corrected_decoded_str = decoded_str
corrected_decoded_str = corrected_decoded_str.replace("20260620T124044Z", new_date_str)
corrected_decoded_str = corrected_decoded_str.replace("/20260620/", f"/{new_cred_date}/")

# We also replace BhMo%2BXGW with BhMo%2BgW
if "BhMo%2BXGW" in corrected_decoded_str:
    corrected_decoded_str = corrected_decoded_str.replace("BhMo%2BXGW", "BhMo%2BgW")
    print("Replaced BhMo%2BXGW with BhMo%2BgW")

# 2. Encode back to base64
corrected_bytes = corrected_decoded_str.encode('latin1')
corrected_base64 = base64.b64encode(corrected_bytes).decode('ascii')

# Prepend bedrock-api-key-
corrected_token = f"bedrock-api-key-{corrected_base64}"

# Test the corrected token
print("\n--- Testing Corrected Token with Current Timestamp ---")
os.environ["BEDROCK_API_KEY"] = corrected_token
os.environ["BEDROCK_REGION"] = "us-east-1"
os.environ["BEDROCK_MODEL"] = "deepseek.v3.2"

try:
    res = generate_with_llm("You are a helpful assistant.", "Say hello world.", 0.1, 10, 1024)
    print("SUCCESS! Output:", res)
except Exception as e:
    print("FAILED:", str(e))
