#!/usr/bin/env python3
import json, re, unicodedata
from pathlib import Path

SECTION_ALIASES = {
    'introduction': 'Introduction',
    'key concepts': 'Key Concepts',
    'important formulas': 'Important Formulas',
    'important exam points': 'Important Exam Points',
    'quick summary': 'Quick Summary',
}

HEADER_RE = re.compile(r'^\s*#.*?\n+', re.S)
SECTION_RE = re.compile(
    r'(?:^|\n)\s*(?:##\s*)?(?:\*\*\s*)?(\d+)\.?\s*([A-Za-z][A-Za-z ]{2,40})(?:\*\*)?\s*[:\-]?\s*',
    re.M
)
KEY_SPLIT = '||'


def clean_text(s):
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'\u200b|\ufeff', '', s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def normalize_label(label):
    x = clean_text(str(label))
    x = x.replace('Grammer', 'Grammar')
    return re.sub(r'\s+', ' ', x).strip(' -_/')


def normalize_subject(label):
    x = normalize_label(label)
    mapping = {
        'इंग्लिश (English)': 'English',
        'English': 'English',
        'Hindi Hindi': 'Hindi',
        'Hindi': 'Hindi',
        'Maths': 'Mathematics',
        'maths': 'Mathematics',
        'science': 'Science',
        'Science': 'Science',
        'Social Science': 'Social Science',
    }
    return mapping.get(x, x)


def parse_key(key):
    parts = [normalize_label(p) for p in str(key).split(KEY_SPLIT)]
    if len(parts) >= 3:
        subject, book, topic = parts[0], parts[1], KEY_SPLIT.join(parts[2:])
    elif len(parts) == 2:
        subject, book, topic = parts[0], '', parts[1]
    else:
        subject, book, topic = '', '', parts[0]
    topic = normalize_label(topic)
    topic = re.sub(r'^(?:Chapter\s*)?\d+[.:\-)]*\s*', '', topic, flags=re.I).strip()
    return {
        'subject': normalize_subject(subject),
        'book': normalize_label(book),
        'topic': topic,
        'source_key': key,
    }


def strip_header(text):
    return HEADER_RE.sub('', text.strip(), count=1).strip()


def extract_sections(text):
    t = clean_text(strip_header(text))
    matches = list(SECTION_RE.finditer(t))
    sections = {}
    if matches:
        for i, m in enumerate(matches):
            title = normalize_label(m.group(2))
            title_std = SECTION_ALIASES.get(title.lower(), title)
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(t)
            sections[title_std] = clean_text(t[start:end])
    else:
        sections['Raw'] = t
    for sec in ['Introduction', 'Key Concepts', 'Important Formulas', 'Important Exam Points', 'Quick Summary']:
        sections.setdefault(sec, '')
    return sections


def normalize_entry(key, value):
    meta = parse_key(key)
    body = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    sections = extract_sections(body)
    return {
        'subject': meta['subject'],
        'book': meta['book'],
        'topic': meta['topic'],
        'content': {
            'Introduction': sections['Introduction'],
            'Key Concepts': sections['Key Concepts'],
            'Important Formulas': sections['Important Formulas'],
            'Important Exam Points': sections['Important Exam Points'],
            'Quick Summary': sections['Quick Summary'],
        },
        'source_key': meta['source_key'],
    }


def normalize_file(path_str):
    path = Path(path_str)
    data = json.loads(path.read_text(encoding='utf-8'))
    out = {
        'source_file': path.name,
        'metadata': {},
        'entries': []
    }
    for k, v in data.items():
        if k in ('summary', 'timestamp'):
            out['metadata'][k] = v
        else:
            out['entries'].append(normalize_entry(k, v))
    out['entries'].sort(key=lambda x: (x['subject'], x['book'], x['topic']))
    return out


def main():
    import sys
    if len(sys.argv) < 2:
        print('Usage: python normalize_rag_cache.py <file1.json> [file2.json ...]')
        raise SystemExit(1)
    outdir = Path('output/normalized')
    outdir.mkdir(parents=True, exist_ok=True)
    for p in sys.argv[1:]:
        norm = normalize_file(p)
        out_path = outdir / Path(p).name.replace('.json', '_normalized.json')
        out_path.write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Done: {out_path}")


if __name__ == '__main__':
    main()