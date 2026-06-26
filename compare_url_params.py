import base64
import urllib.parse

old_key = "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFXVFhWM0M1M0pLTFhTS1lQJTJGMjAyNjA2MTclMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA2MTdUMDYzMjE3WiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFTCUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRndFYUNYVnpMV1ZoYzNRdE1TSklbase64_part_encoded_old=" # Let's read old key from the other env file
with open(r"C:\Users\bhask\Desktop\Archive\New folder\.env", "r") as f:
    for line in f:
        if "BEDROCK_API_KEY" in line:
            old_key = line.split("=", 1)[1].strip()

new_key = "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFXVFhWM0M1M0dKRlBSNFdaJTJGMjAyNjA2MjAlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA2MjBUMTI0MDQ0WiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFQTBhQ1hWekxXVmhjM1F0TVNKSE1FVUNJUUR1JTJCbXRobGxFazlaUUgya3J0eUpDcWd2b2JGcXRHR1IlMkJNMFN4cDV0JTJGMGNnSWdTaEJFYmdzcEZaN1hab2ZES2R6ZVZmN1hEWk5vOGJSaW5pT2wwTksxek5jcXNnTUkxdiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRkFSQUFHZ3cwTlRRM01EZ3pOamt5TnpBaURCOWx5c1Zua1h3azdrJTJGa0ZpcUdBJTJGS3IlMkJ1bzNmJTJGTnRkcmJZcm0zTGJ0M0RxS2dVY05zaFpzbWFBOFcyUmtaSVRwYXQlMkJHZUNJaWZQcFBFMGhHZW5CampqamdvOHNOSTlYaVJGSWFIeEQzSDZ6cG5JZktKJTJCTldwUVBWNWhpU0dtSWZoSmhSMExxWHJFb29KYTZYbmNkRUVuVlUlMkJmY2lXcHhlazJONnFrMDZSS200Z1F5SklVZ1NKdzFvOVdhd0c3WmtkWGExelFzdUJSdHAxbjNjMVNWSHFFZEwxOHFMeEVuVkY1b0NxU3lZdjJ5NnNuM281MWRNWjNxNGN3YVlkdVRMQ0xISXhBWk9qeExJaXNpV0hlNlRhYldPcER0SkolMkY4Yk9SblFiVGZqRUJoTW8lMkJYR1clMkJNTnclMkZCNzl0U3JvWFZDMGtXTXFQWEFWbVNZOTdPcGkzdFhtJTJGJTJGMTJDdmpqWjRuelNKWDFmZlRBVTlyVEFaYk94MUpGUFkwWnRyYUdsYjI4R0pZaFFtMUZxV2hsNmM5YW5ucFlOZERheHVLM2xDWjNaTklVZXdMQmRJZmgyYU01amdKWldDYjQ1b3dNWnhtbXZPODRYZnV2NjJhZ3FKcTZwVm1XVSUyQmIwc0VMOWowaGhKQkN4Qjh6TSUyQllJYUZTJTJCNmlOUEJVcXZFUzZ6RURGdFI3N0glMkJRdzk3UFBaY255aUFSRXBnWmRPc3NuekMxbE5yUkJqcmVBaSUyRm5RYVhvTG5PaUdoODJRTjh0MnlXTCUyRlglMkI5VUxqcjRRZ3lKWnpkSjFseXQ0dkg0NlFzZXRZTmVWQ3B5cGFMMUc5dDNXcU9VM1lEMTRKS1ZXSW9LWW9ETEc0JTJCYmk4JTJGY1dMSGVyeDJMTkFMSWJ2eiUyRjZ0VjZkRXJTSGJNZk9vejE1MUpmc3FreWFOR21CdERTTmpia1FhNWhGek12Zm01cWh0T1ElMkZ6Z3klMkJlUTlvRlJWME5Sb2ZjRFMzYlZUM0RGbkptcWJGdEJKSlh3eUNVRUpENnFiUEFKa3AyNDVuOE9hRlUlMkZwUEczcXkyJTJCciUyQmJWc2luMXdGeWVPTGxTcUFtZmRQZVVPS1ZhV0dhZ1VkdVV2ZGtlRzNKRmoxalBmUVNwZGlmRFplb08lMkI3eUR6VjU3Y2hBanR3Yzdld0p2UnZ3aUx1U2l3ekVBJTJCN2dxZwhoQURiTCUyQnUzTVVPNjNFMCUyRiUyQkJVVGttVFFIRFExUkhGVEk4T0Y2d2NCcWJaZ0ZRWlA5TWlYVHNIcUxkYTJoZEc2Y0tjSWx6ejBWUGIlMkJ5RDVabTJheXhubFBXNmlnaWlhcGhzb3UlMkZWdU9YQ1ZrYmpJbW05c3FqQzRqMUclMkJwdmxUWUpkVFZnQSZYLUFtei1TaWduYXR1cmU9ZGVhODVjNDE4YjMxYzI3N2JkZjVkNWUyNDE5OWIwY2VlOTdmNDQzOGUyOWI2MjNiMjkwY2FmM2UyYWZlOGZkMiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmVmVyc2lvbj0x"

def parse_key(key_str):
    bp = key_str.replace("bedrock-api-key-", "")
    bp_unquoted = urllib.parse.unquote(bp)
    missing_padding = len(bp_unquoted) % 4
    if missing_padding:
        bp_unquoted += '=' * (4 - missing_padding)
    dec = base64.b64decode(bp_unquoted).decode('latin1')
    
    # Decoded is like bedrock.amazonaws.com/?Action=CallWithBearerToken&...
    # Let's extract parameters
    url_part = dec.split("?", 1)[1]
    params = urllib.parse.parse_qs(url_part)
    # Simplify list values to single strings
    return {k: v[0] for k, v in params.items()}

old_params = parse_key(old_key)
new_params = parse_key(new_key)

print("=== PARAMETERS COMPARISON ===")
all_keys = set(old_params.keys()).union(new_params.keys())
for k in sorted(all_keys):
    old_val = old_params.get(k, "MISSING")
    new_val = new_params.get(k, "MISSING")
    if old_val != new_val:
        print(f"\nParameter: {k} (CHANGED)")
        print(f"  Old: {old_val[:120]} ... (len {len(old_val)})")
        print(f"  New: {new_val[:120]} ... (len {len(new_val)})")
    else:
        print(f"\nParameter: {k} (EQUAL)")
        print(f"  Value: {old_val[:120]} ...")
