"""
fix_latex_in_cache.py
─────────────────────
One-time post-processor: removes LaTeX $ signs and macros from all
rag_cache_*.json files in the project root WITHOUT re-generating notes.

Run once:  python fix_latex_in_cache.py
"""

import json
import re
import glob
import os
from pathlib import Path


# ── same strip_latex logic as generator.py ──────────────────────────────────

def strip_latex(text: str) -> str:
    """Remove LaTeX delimiters and convert common macros to plain Unicode."""
    if not isinstance(text, str):
        return text

    # Remove display-math blocks $$...$$
    text = re.sub(r'\$\$(.+?)\$\$', r'\1', text, flags=re.DOTALL)
    # Remove inline-math blocks $...$
    text = re.sub(r'\$(.+?)\$', r'\1', text, flags=re.DOTALL)
    # Convert \frac{a}{b} → a / b
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 / \2', text)
    # Convert \sqrt{x} → √x
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√\1', text)
    # \begin{array}...\end{array} — extract content rows
    text = re.sub(r'\\begin\{array\}.*?\\end\{array\}', '', text, flags=re.DOTALL)
    # Common symbol macros
    replacements = {
        r'\times':      '×',
        r'\div':        '÷',
        r'\cdot':       '·',
        r'\pm':         '±',
        r'\geq':        '≥',
        r'\leq':        '≤',
        r'\neq':        '≠',
        r'\approx':     '≈',
        r'\infty':      '∞',
        r'\alpha':      'α',
        r'\beta':       'β',
        r'\gamma':      'γ',
        r'\delta':      'δ',
        r'\pi':         'π',
        r'\theta':      'θ',
        r'\lambda':     'λ',
        r'\mu':         'μ',
        r'\sigma':      'σ',
        r'\Rightarrow': '⇒',
        r'\rightarrow': '→',
        r'\leftarrow':  '←',
        r'\leftrightarrow': '↔',
        r'\hline':      '',
        r'\\ ':         '\n',   # table row break
        r'\\':          '\n',
        r'\ ':          ' ',
    }
    for macro, symbol in replacements.items():
        text = text.replace(macro, symbol)

    # Remove remaining \command{content} → just content
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    # Remove bare \command
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # Remove lone $ signs that might be left over
    text = text.replace('$', '')
    # Collapse multiple spaces / blank lines
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── walk all cache files ─────────────────────────────────────────────────────

ROOT = Path(__file__).parent
cache_files = list(ROOT.glob("rag_cache_*.json"))

if not cache_files:
    print("No rag_cache_*.json files found. Exiting.")
    exit()

print(f"Found {len(cache_files)} cache file(s):\n")

total_fixed = 0

for cache_path in cache_files:
    print(f"  Processing: {cache_path.name} ...", end=" ", flush=True)

    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fixed_count = 0
    new_data = {}

    for key, value in data.items():
        if isinstance(value, str) and ('$' in value or '\\' in value):
            new_data[key] = strip_latex(value)
            fixed_count += 1
        else:
            new_data[key] = value

    # Write back only if something changed
    if fixed_count > 0:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"Fixed {fixed_count} entries [OK]")
    else:
        print("Nothing to fix [OK]")

    total_fixed += fixed_count

print(f"\nDone! Total entries cleaned: {total_fixed}")
print("Your existing cache files are now LaTeX-free — no re-generation needed.")
