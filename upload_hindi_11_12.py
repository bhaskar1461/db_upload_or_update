"""
Upload Hindi Medium 11th & 12th notes to ai_notes_new table.
Reads from rag_cache_Class_*_Hindi.json files and inserts into Hostinger MySQL.
"""
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

import mysql.connector
from dotenv import load_dotenv

# ── Config ──
load_dotenv(Path(__file__).parent / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

BASE_DIR = Path(r"C:\Users\bhask\Desktop\New folder")

# Cache files to process: (file_path, class_number, stream)
HINDI_CACHES = [
    (BASE_DIR / "rag_cache_Class_11th_Science_Hindi.json",    "11", "Science"),
    (BASE_DIR / "rag_cache_Class_11th_Commerce_Hindi.json",   "11", "Commerce"),
    (BASE_DIR / "rag_cache_Class_12th_Science_Hindi.json",    "12", "Science"),
    (BASE_DIR / "rag_cache_Class_12th_Commerce_Hindi.json",   "12", "Commerce"),
]


def clean_notes(text: str) -> str:
    """Clean up notes text for DB storage."""
    # Remove LaTeX artifacts
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\$([^$]*)\$", r"\1", text)
    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_subject_name(raw: str) -> str:
    """Extract clean subject name from cache key like 'इंग्लिश (English)'."""
    # If it has parentheses with English name, extract that
    m = re.search(r"\(([^)]+)\)", raw)
    if m:
        return m.group(1).strip()
    # Strip leading numbers like "11th " prefix
    cleaned = re.sub(r"^\d+th\s+", "", raw)
    return cleaned.strip()


def connect_db():
    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn


def build_full_notes_json(class_num: str, subject: str, topic: str, notes_text: str) -> str:
    """Build a structured JSON string for the full_notes column matching existing format."""
    # Try to extract sections from the notes text
    sections = re.split(r"\n(?=#+\s|\*\*\d)", notes_text)
    
    key_concepts = []
    exam_points = []
    revision_facts = []
    intro = ""
    
    for section in sections:
        lines = [l.strip() for l in section.strip().split("\n") if l.strip()]
        if not lines:
            continue
        # First non-empty section becomes intro
        if not intro and not section.startswith("#"):
            intro = " ".join(lines[:3])
            continue
        
        # Extract bullet points
        points = [re.sub(r"^[-•*]\s*", "", l) for l in lines if l.startswith(("-", "•", "*")) and len(l) > 10]
        header = re.sub(r"^#+\s*", "", lines[0])
        
        if points:
            if "exam" in header.lower() or "important" in header.lower():
                exam_points.extend(points[:5])
            elif "revision" in header.lower() or "quick" in header.lower():
                revision_facts.extend(points[:5])
            else:
                key_concepts.append({"topic": header[:100], "points": points[:5]})
    
    if not intro:
        intro = notes_text[:200].replace("\n", " ")
    
    full_notes = {
        "class": f"Class {class_num}",
        "subject": subject,
        "chapter_name": topic,
        "introduction": intro[:500],
        "key_concepts": key_concepts[:6] if key_concepts else [{"topic": topic, "points": [notes_text[:300]]}],
        "important_exam_points": exam_points[:5] if exam_points else [],
        "quick_revision_facts": revision_facts[:5] if revision_facts else [],
    }
    return json.dumps(full_notes, ensure_ascii=False)


def upload_cache(conn, cache_path: Path, class_num: str, stream: str):
    """Upload a single cache file to the DB."""
    if not cache_path.exists():
        print(f"  ⏭ SKIP (not found): {cache_path.name}")
        return 0

    data = json.load(open(cache_path, "r", encoding="utf-8"))
    if not data:
        print(f"  ⏭ SKIP (empty): {cache_path.name}")
        return 0

    cur = conn.cursor()
    inserted = 0
    updated = 0
    skipped = 0
    now = datetime.now()

    for key, notes_text in data.items():
        parts = key.split("||")
        if len(parts) < 3:
            raw_subject = parts[0] if len(parts) >= 1 else "Unknown"
            topic = parts[-1]
        else:
            raw_subject = parts[0]
            topic = parts[2]

        subject = clean_subject_name(raw_subject)
        notes = clean_notes(notes_text)

        if not notes or len(notes) < 50:
            skipped += 1
            continue

        full_notes_json = build_full_notes_json(class_num, subject, topic, notes)

        # Check for existing entry
        cur.execute(
            "SELECT id, full_notes FROM ai_notes_new WHERE language = %s AND class = %s AND stream = %s AND subject = %s AND topic = %s",
            ("Hindi", class_num, stream, subject, topic)
        )
        existing = cur.fetchone()
        
        if existing:
            # Update full_notes if it's empty
            if not existing[1]:
                cur.execute(
                    "UPDATE ai_notes_new SET full_notes = %s, updated_at = %s WHERE id = %s",
                    (full_notes_json[:255], now, existing[0])
                )
                updated += 1
            else:
                skipped += 1
            continue

        # Insert new entry with both short_notes and full_notes
        cur.execute(
            """INSERT INTO ai_notes_new 
               (language, board, stream, class, subject, topic, short_notes, full_notes, created_by, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            ("Hindi", "CBSE", stream, class_num, subject, topic, notes, full_notes_json[:255], "AI", now, now)
        )
        inserted += 1

    conn.commit()
    cur.close()
    print(f"  ✅ {cache_path.name}: inserted {inserted}, updated {updated}, skipped {skipped}")
    return inserted


def main():
    print("=" * 60)
    print("Uploading Hindi Medium 11th & 12th to ai_notes_new")
    print("=" * 60)

    conn = connect_db()
    print(f"Connected to {DB_HOST}/{DB_NAME}\n")

    total = 0
    for cache_path, class_num, stream in HINDI_CACHES:
        print(f"Processing Class {class_num} {stream} Hindi...")
        count = upload_cache(conn, cache_path, class_num, stream)
        total += count

    print(f"\n{'=' * 60}")
    print(f"Total inserted: {total} Hindi chapters")

    # Show final counts
    cur = conn.cursor()
    cur.execute("SELECT class, stream, language, COUNT(1) FROM ai_notes_new GROUP BY class, stream, language ORDER BY class, stream, language")
    print(f"\nFinal DB state (ai_notes_new):")
    for r in cur.fetchall():
        print(f"  Class {r[0]} | {r[1]:10s} | {r[2]:8s} | {r[3]} entries")
    cur.close()

    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
