import base64
import urllib.parse

token_with_xgw = "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUFXVFhWM0M1M0dKRlBSNFdaJTJGMjAyNjA2MjAlMkZ1cy1lYXN0LTElMkZiZWRyb2NrJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNjA2MjBUMTI0MDQ0WiZYLUFtei1FeHBpcmVzPTQzMjAwJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFQTBhQ1hWekxXVmhjM1F0TVNKSE1FVUNJUUR1JTJCbXRobGxFazlaUUgya3J0eUpDcWd2b2JGcXRHR1IlMkJNMFN4cDV0JTJGMGNnSWdTaEJFYmdzcEZaN1hab2ZES2R6ZVZmN1hEWk5vOGJSaW5pT2wwTksxek5jcXNnTUkxdiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRkFSQUFHZ3cwTlRRM01EZ3pOamt5TnpBaURCOWx5c1Zua1h3azdrJTJGa0ZpcUdBJTJGS3IlMkJ1bzNmJTJGTnRkcmJZcm0zTGJ0M0RxS2dVY05zaFpzbWFBOFcyUmtaSVRwYXQlMkJHZUNJaWZQcFBFMGhHZW5CampqamdvOHNOSTlYaVJGSWFIeEQzSDZ6cG5JZktKJTJCTldwUVBWNWhpU0dtSWZoSmhSMExxWHJFb29KYTZYbmNkRUVuVlUlMkJmY2lXcHhlazJONnFrMDZSS200Z1F5SklVZ1NKdzFvOVdhd0c3WmtkWGExelFzdUJSdHAxbjNjMVNWSHFFZEwxOHFMeEVuVkY1b0NxU3lZdjJ5NnNuM281MWRNWjNxNGN3YVlkdVRMQ0xISXhBWk9qeExJaXNpV0hlNlRhYldPcER0SkolMkY4Yk9SblFiVGZqRUJoTW8lMkJYR1clMkJNTnclMkZCNzl0U3JvWFZDMGtXTXFQWEFWbVNZOTdPcGkzdFhtJTJGJTJGMTJDdmpqWjRuelNKWDFmZlRBVTlyVEFaYk94MUpGUFkwWnRyYUdsYjI4R0pZaFFtMUZxV2hsNmM5YW5ucFlOZERheHVLM2xDWjNaTklVZXdMQmRJZmgyYU01amdKWldDYjQ1b3dNWnhtbXZPODRYZnV2NjJhZ3FKcTZwVm1XVSUyQmIwc0VMOWowaGhKQkN4Qjh6TSUyQllJYUZTJTJCNmlOUEJVcXZFUzZ6RURGdFI3N0glMkJRdzk3UFBaY255aUFSRXBnWmRPc3NuekMxbE5yUkJqcmVBaSUyRm5RYVhvTG5PaUdoODJRTjh0MnlXTCUyRlglMkI5VUxqcjRRZ3lKWnpkSjFseXQ0dkg0NlFzZXRZTmVWQ3B5cGFMMUc5dDNXcU9VM1lEMTRKS1ZXSW9LWW9ETEc0JTJCYmk4JTJGY1dMSGVyeDJMTkFMSWJ2eiUyRjZ0VjZkRXJTSGJNZk9vejE1MUpmc3FreWFOR21CdERTTmpia1FhNWhGek12Zm01cWh0T1ElMkZ6Z3klMkJlUTlvRlJWME5Sb2ZjRFMzYlZUM0RGbkptcWJGdEJKSlh3eUNVRUpENnFiUEFKa3AyNDVuOE9hRlUlMkZwUEczcXkyJTJCciUyQmJWc2luMXdGeWVPTGxTcUFtZmRQZVVPS1ZhV0dhZ1VkdVV2ZGtlRzNKRmoxalBmUVNwZGlmRFplb08lMkI3eUR6VjU3Y2hBanR3Yzdld0p2UnZ3aUx1U2l3ekVBJTJCN2dxZwhoQURiTCUyQnUzTVVPNjNFMCUyRiUyQkJVVGttVFFIRFExUkhGVEk4T0Y2d2NCcWJaZ0ZRWlA5TWlYVHNIcUxkYTJoZEc2Y0tjSWx6ejBWUGIlMkJ5RDVabTJheXhubFBXNmlnaWlhcGhzb3UlMkZWdU9YQ1ZrYmpJbW05c3FqQzRqMUclMkJwdmxUWUpkVFZnQSZYLUFtei1TaWduYXR1cmU9ZGVhODVjNDE4YjMxYzI3N2JkZjVkNWUyNDE5OWIwY2VlOTdmNDQzOGUyOWI2MjNiMjkwY2FmM2UyYWZlOGZkMiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmVmVyc2lvbj0x"

token_with_gw = token_with_xgw.replace("BhMo%2BXGW", "BhMo%2BgW")

def decode_token(tok):
    base64_part = tok.replace("bedrock-api-key-", "")
    # Add padding if needed
    missing_padding = len(base64_part) % 4
    if missing_padding:
        base64_part += '=' * (4 - missing_padding)
    try:
        decoded_bytes = base64.b64decode(base64_part)
        # Decode as latin1 to preserve all byte values without throwing
        decoded_str = decoded_bytes.decode('latin1')
        return decoded_str
    except Exception as e:
        return f"ERROR: {e}"

dec_xgw = decode_token(token_with_xgw)
dec_gw = decode_token(token_with_gw)

print("XGW decoded length:", len(dec_xgw))
print("gW decoded length:", len(dec_gw))

# Let's find the difference
if len(dec_xgw) == len(dec_gw):
    diffs = []
    for i, (c1, c2) in enumerate(zip(dec_xgw, dec_gw)):
        if c1 != c2:
            diffs.append((i, c1, c2))
    print("Differences:")
    for diff in diffs:
        idx, c1, c2 = diff
        print(f"  Index {idx}: {repr(c1)} vs {repr(c2)}")
        # Print surrounding context
        print(f"    Context XGW: {repr(dec_xgw[max(0, idx-30):idx+30])}")
        print(f"    Context gW:  {repr(dec_gw[max(0, idx-30):idx+30])}")
else:
    print("Lengths are different!")
