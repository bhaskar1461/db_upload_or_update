import json, sys, glob
sys.stdout.reconfigure(encoding='utf-8')

for f in glob.glob('rag_cache_*.json'):
    data = json.loads(open(f, encoding='utf-8').read())
    for k, v in data.items():
        if 'math' in k.lower() or 'maths' in k.lower() or 'गणित' in k:
            print(f"FILE: {f}")
            print(f"KEY: {k}")
            print(f"NOTES: {v[:150]}")
            break
    else:
        continue
    break
