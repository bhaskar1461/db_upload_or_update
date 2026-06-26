import urllib.request
import re

url = 'https://ainotes.schools2ai.com/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        scripts = re.findall(r'href=[\'\"](/assets/[^\'\"]+\.js)[\'\"]|src=[\'\"](/assets/[^\'\"]+\.js)[\'\"]', html)
        scripts = [s[0] or s[1] for s in scripts]
        for s in set(scripts):
            full_url = 'https://ainotes.schools2ai.com' + s
            print('Checking:', full_url)
            req_js = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(req_js) as js_resp:
                    js_code = js_resp.read().decode('utf-8')
                    # Search for any URL-like strings
                    urls = re.findall(r'[\'\"\`](https?://[a-zA-Z0-9\-\_\.]*schools2ai\.com[^\'\"\`]*)[\'\"\`]', js_code)
                    if urls:
                        print('  Found URLs:', set(urls))
                    
                    # Search for relative api endpoints
                    apis = re.findall(r'[\'\"\`](/[a-zA-Z0-9\-\_]+/api[a-zA-Z0-9\-\_/]*)[\'\"\`]|[\'\"\`](/api/[a-zA-Z0-9\-\_/]+)[\'\"\`]', js_code)
                    if apis:
                        api_list = [a[0] or a[1] for a in apis]
                        print('  Found relative APIs:', set(api_list))
                        
                    # Also look for any string containing 'app-api' or 'api/v1'
                    keywords = re.findall(r'[\'\"\`][^\'\"\`]*(app-api|api/v1|upload)[^\'\"\`]*[\'\"\`]', js_code, re.IGNORECASE)
                    if keywords:
                        print('  Found interesting strings:', set(keywords))
            except Exception as e:
                print('Error fetching', s, e)
except Exception as e:
    print('Error:', e)
