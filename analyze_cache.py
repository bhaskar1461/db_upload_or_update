"""Analyze RAG cache quality and PDF content issues."""
import json
import os
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path(r"C:\Users\bhask\Desktop\New folder")

EXPECTED_HEADINGS = [
    "## 1. Introduction",
    "## 2. Key Concepts",
    "## 3. Important Formulas",
    "## 4. Important Exam Points",
    "## 5. Important Questions",
    "## 6. Quick Summary",
]

def analyze_cache(cache_file):
    if not cache_file.exists():
        print(f"  [NOT FOUND] {cache_file.name}")
        return
    
    with open(cache_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total = len(data)
    print(f"\n{'='*70}")
    print(f"  Cache: {cache_file.name}  ({total} entries)")
    print(f"{'='*70}")
    
    issues = {
        "missing_headings": [],
        "too_short": [],
        "has_latex": [],
        "wrong_format": [],
        "empty_sections": [],
    }
    
    heading_counts = Counter()
    
    for key, content in data.items():
        # Count headings
        headings = [l.strip() for l in content.split("\n") if l.strip().startswith("## ")]
        heading_counts[len(headings)] += 1
        
        # Check for expected 5-heading structure (sometimes 6 with Quick Summary)
        found_h2 = len(headings)
        if found_h2 < 4:
            issues["missing_headings"].append((key, found_h2, headings))
        
        # Check length
        if len(content) < 300:
            issues["too_short"].append((key, len(content)))
        
        # Check for LaTeX remnants
        latex_patterns = [r'\$[^$]+\$', r'\\frac\{', r'\\sqrt\{', r'\\times', r'\\cdot', r'\\text\{']
        for pat in latex_patterns:
            if re.search(pat, content):
                issues["has_latex"].append((key, pat))
                break
        
        # Check if content starts with expected format
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        if lines and not (lines[0].startswith("#") or lines[0].startswith("## ")):
            issues["wrong_format"].append((key, lines[0][:80]))
    
    print(f"\n  Heading count distribution:")
    for count, num in sorted(heading_counts.items()):
        marker = " <<<" if count < 4 else ""
        print(f"    {count} headings: {num} entries{marker}")
    
    print(f"\n  Quality Issues:")
    for issue_name, issue_list in issues.items():
        count = len(issue_list)
        status = "OK" if count == 0 else f"ISSUES ({count})"
        print(f"    {issue_name}: {status}")
        if count > 0 and count <= 5:
            for item in issue_list[:5]:
                print(f"      - {item}")
        elif count > 5:
            for item in issue_list[:3]:
                print(f"      - {item}")
            print(f"      ... and {count - 3} more")
    
    # Show a few sample entries with heading structure
    print(f"\n  Sample entries (first 3):")
    for i, (key, content) in enumerate(list(data.items())[:3]):
        headings = [l.strip() for l in content.split("\n") if l.strip().startswith("## ")]
        print(f"    [{i+1}] {key}")
        print(f"        Length: {len(content)} chars, Headings: {len(headings)}")
        for h in headings:
            print(f"          {h}")
    
    # Show a problematic entry if any
    if issues["missing_headings"]:
        key, count, headings = issues["missing_headings"][0]
        print(f"\n  === PROBLEM ENTRY (only {count} headings) ===")
        print(f"  Key: {key}")
        print(f"  Content preview:")
        print(f"  {data[key][:600]}")
        print(f"  ...")

def check_pdf_vs_cache(class_name, medium):
    """Check if the PDF was built from cache or raw text."""
    cache_file = BASE_DIR / f"rag_cache_Class_{class_name}_{medium}.json"
    pdf_file = BASE_DIR / "Generated_Exam_PDFs" / f"RAG_Class_{class_name}_{medium}_Medium_Exam_Notes.pdf"
    
    cache_count = 0
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            cache_count = len(json.load(f))
    
    pdf_size = 0
    if pdf_file.exists():
        pdf_size = pdf_file.stat().st_size / 1024
    
    print(f"  {class_name} {medium}: cache={cache_count} entries, PDF={pdf_size:.0f} KB")

# Analyze all cache files
print("=" * 70)
print("  PDF vs Cache Summary")
print("=" * 70)
for medium in ["English", "Hindi"]:
    for cls in ["6th", "7th", "8th"]:
        check_pdf_vs_cache(cls, medium)

# List all cache files
cache_files = sorted(BASE_DIR.glob("rag_cache_Class_*.json"))
print(f"\nFound {len(cache_files)} cache files:")
for cf in cache_files:
    size_kb = cf.stat().st_size / 1024
    print(f"  {cf.name}: {size_kb:.1f} KB")

# Deep analysis of each
for cf in cache_files:
    analyze_cache(cf)
