import urllib.request
import re

url = 'https://ainotes.schools2ai.com/assets/index-BKNv9IlF.js'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        js_code = response.read().decode('utf-8')
        
        # Find all string literals that look like API endpoints
        # Matching "/api/..." or ".../api/..."
        api_endpoints = re.findall(r'[\'\"\`]/[^\'\"\`]*api/[^\'\"\`]*[\'\"\`]', js_code)
        
        # Also look for full URLs containing schools2ai.com
        urls = re.findall(r'https?://[a-zA-Z0-9\-\_\.]*schools2ai\.com[^\'\"\`]*', js_code)
        
        print('Found endpoints containing API:')
        for e in set(api_endpoints): print(e)
        
        print('\nFound full URLs:')
        for u in set(urls): print(u)
except urllib.error.HTTPError as e:
    print('HTTPError:', e.code)
    # The file name might be different now, let's fetch the homepage to get the latest JS file name
    print("Fetching homepage to find the JS bundle name...")
    req_home = urllib.request.Request('https://ainotes.schools2ai.com/', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_home) as response_home:
        html = response_home.read().decode('utf-8')
        js_files = re.findall(r'src=[\'"](/assets/index-[^\'"]+\.js)[\'"]', html)
        if js_files:
            print("Found JS file:", js_files[0])
            js_url = 'https://ainotes.schools2ai.com' + js_files[0]
            req_js = urllib.request.Request(js_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_js) as response_js:
                js_code = response_js.read().decode('utf-8')
                api_endpoints = re.findall(r'[\'\"\`]/[^\'\"\`]*api/[^\'\"\`]*[\'\"\`]', js_code)
                urls = re.findall(r'https?://[a-zA-Z0-9\-\_\.]*schools2ai\.com[^\'\"\`]*', js_code)
                print('\nFound endpoints containing API:')
                for e in set(api_endpoints): print(e)
                print('\nFound full URLs:')
                for u in set(urls): print(u)
        else:
            print("Could not find JS file in homepage")
except Exception as e:
    print('Error:', e)
