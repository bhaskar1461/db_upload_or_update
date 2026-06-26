import httpx
import urllib.parse

url = "https://bedrock-mantle.us-east-1.api.aws/v1/chat/completions"
payload = {
    "model": "deepseek.v3.2",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello"}
    ],
    "max_tokens": 10
}

key_encoded = "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFXVFhWM0M1M0dKRlBSNFdaJTJGMjAyNjA2MjAlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA2MjBUMTI0MDQ0WiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFQTBhQ1hWekxXVmhjM1F0TVNKSE1FVUNJUUR1JTJCbXRobGxFazlaUUgya3J0eUpDcWd2b2JGcXRHR1IlMkJNMFN4cDV0JTJGMGNnSWdTaEJFYmdzcEZaN1hab2ZES2R6ZVZmN1hEWk5vOGJSaW5pT2wwTksxek5jcXNnTUkxdiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRkFSQUFHZ3cwTlRRM01EZ3pOamt5TnpBaURCOWx5c1Zua1h3azdrJTJGa0ZpcUdBJTJGS3IlMkJ1bzNmJTJGTnRkcmJZcm0zTGJ0M0RxS2dVY05zaFpzbWFBOFcyUmtaSVRwYXQlMkJHZUNJaWZQcFBFMGhHZW5CampqamdvOHNOSTlYaVJGSWFIeEQzSDZ6cG5JZktKJTJCTldwUVBWNWhpU0dtSWZoSmhSMExxWHJFb29KYTZYbmNkRUVuVlUlMkJmY2lXcHhlazJONnFrMDZSS200Z1F5SklVZ1NKdzFvOVdhd0c3WmtkWGExelFzdUJSdHAxbjNjMVNWSHFFZEwxOHFMeEVuVkY1b0NxU3lZdjJ5NnNuM281MWRNWjNxNGN3YVlkdVRMQ0xISXhBWk9qeExJaXNpV0hlNlRhYldPcER0SkolMkY4Yk9SblFiVGZqRUJoTW8lMkJYR1clMkJNTnclMkZCNzl0U3JvWFZDMGtXTXFQWEFWbVNZOTdPcGkzdFhtJTJGJTJGMTJDdmpqWjRuelNKWDFmZlRBVTlyVEFaYk94MUpGUFkwWnRyYUdsYjI4R0pZaFFtMUZxV2hsNmM5YW5ucFlOZERheHVLM2xDWjNaTklVZXdMQmRJZmgyYU01amdKWldDYjQ1b3dNWnhtbXZPODRYZnV2NjJhZ3FKcTZwVm1XVSUyQmIwc0VMOWowaGhKQkN4Qjh6TSUyQllJYUZTJTJCNmlOUEJVcXZFUzZ6RURGdFI3N0glMkJRdzk3UFBaY255aUFSRXBnWmRPc3NuekMxbE5yUkJqcmVBaSUyRm5RYVhvTG5PaUdoODJRTjh0MnlXTCUyRlglMkI5VUxqcjRRZ3lKWnpkSjFseXQ0dkg0NlFzZXRZTmVWQ3B5cGFMMUc5dDNXcU9VM1lEMTRKS1ZXSW9LWW9ETEc0JTJCYmk4JTJGY1dMSGVyeDJMTkFMSWJ2eiUyRjZ0VjZkRXJTSGJNZk9vejE1MUpmc3FreWFOR21CdERTTmpia1FhNWhGek12Zm01cWh0T1ElMkZ6Z3klMkJlUTlvRlJWME5Sb2ZjRFMzYlZUM0RGbkptcWJGdEJKSlh3eUNVRUpENnFiUEFJa3AyNDVuOE9hRlUlMkZwUEczcXkyJTJCciUyQmJWc2luMXdcvTllPTGxTcUFtZmRQZVVPS1ZhV0dhZ1VkdVV2ZGtlRzNKRmoxalBmUVNwZGlmRFplb08lMkI3eUR6VjU3Y2hBanR3Yzdld0p2UnZ3aUx1U2l3ekVBJTJCN2dxZwhoQURiTCUyQnUzTVVPNjNFMCUyRiUyQkJVVGttVFFIRFExUkhGVEk4T0Y2d2NCcWJaZ0ZRWlA5TWlYVHNIcUxkYTJoZEc2Y0tjSWx6ejBWUGIlMkJ5RDVabTJheXhubFBXNmlnaWlhcGhzb3UlMkZWdU9YQ1ZrYmpJbW05c3FqQzRqMUclMkJwdmxUWUpkVFZnQSZYLUFtei1TaWduYXR1cmU9ZGVhODVjNDE4YjMxYzI3N2JkZjVkNWUyNDE5OWIwY2VlOTdmNDQzOGUyOWI2MjNiMjkwY2FmM2UyYWZlOGZkMiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmVmVyc2lvbj0x"

# We unquote the base64 part
base64_part_encoded = key_encoded.replace("bedrock-api-key-", "")
base64_part_unquoted = urllib.parse.unquote(base64_part_encoded)
key_unquoted = f"bedrock-api-key-{base64_part_unquoted}"

def test(tok, desc):
    print(f"\nTesting: {desc}")
    headers = {
        "Authorization": f"Bearer {tok}",
        "Content-Type": "application/json",
        "Host": "bedrock.amazonaws.com"
    }
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=10)
        print("  Status:", response.status_code)
        print("  Body:", response.text)
    except Exception as e:
        print("  Error:", e)

test(key_encoded, "Encoded key (as-is)")
test(key_unquoted, "Unquoted key (with + and /)")
