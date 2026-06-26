with open('selenium_uploader_6to9.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'if chapter_name.lower() in uploaded_topic.lower() or uploaded_topic.lower() in chapter_name.lower():' in line:
        new_lines.append('            if uploaded_topic.strip() == "": continue\n')
        new_lines.append(line)
    else:
        new_lines.append(line)

with open('selenium_uploader_6to9.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Now recreate the math one based on the fixed 6to9 script
new_math_lines = []
for line in new_lines:
    new_math_lines.append(line)
    if 'subject = key_parts[0].strip()' in line:
        new_math_lines.append('        if "math" not in subject.lower():\n')
        new_math_lines.append('            continue\n')

with open('selenium_uploader_math.py', 'w', encoding='utf-8') as f:
    f.writelines(new_math_lines)

print("Fixed the empty string bug in both uploaders.")
