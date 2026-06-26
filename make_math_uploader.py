with open('selenium_uploader_6to9.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if 'subject = key_parts[0].strip()' in line:
        new_lines.append('        if "math" not in subject.lower():\n')
        new_lines.append('            continue\n')

with open('selenium_uploader_math.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
