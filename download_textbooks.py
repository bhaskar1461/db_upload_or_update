#!/usr/bin/env python3
"""
Download NCERT Textbooks (Class 6-9) from Internet Archive and fallback sources.
Saves PDFs organized by Class/Subject with descriptive filenames.
Generates a comprehensive log file of all download attempts.
"""

import os
import re
import sys
import json
import time
import datetime
import traceback

try:
    import requests
except ImportError:
    print("ERROR: 'requests' module not found. Install with: pip install requests")
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================
BASE_DIR = os.path.join(r"c:\Users\bhask\Desktop\New folder", "Textbooks")
LOG_FILE = os.path.join(r"c:\Users\bhask\Desktop\New folder", "textbook_download_log.txt")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# =============================================================================
# Textbook Definitions
# Each entry has a list of "sources" tried in order (first success wins).
# Source types:
#   archive  - Internet Archive item; uses metadata API to find PDF
#   direct   - Direct PDF URL
#   ncert    - Try NCERT official site pattern: ncert.nic.in/textbook/pdf/{code}ps.pdf
#   scrape   - Scrape an HTML page for embedded PDF links
# =============================================================================
TEXTBOOKS = [
    # =========================================================================
    # CLASS 6  (10 books — all Internet Archive)
    # =========================================================================
    {
        "class": 6, "subject": "English", "title": "Honeysuckle",
        "sources": [
            {"type": "archive", "item_id": "honeysuckle-textbook-english-class-6-2006-ncert"},
        ]
    },
    {
        "class": 6, "subject": "English", "title": "A Pact with the Sun",
        "sources": [
            {"type": "archive", "item_id": "ncert-fepw1"},
        ]
    },
    {
        "class": 6, "subject": "Hindi", "title": "Vasant",
        "sources": [
            {"type": "archive", "item_id": "ncert-fhvs1"},
        ]
    },
    {
        "class": 6, "subject": "Hindi", "title": "Durva",
        "sources": [
            {"type": "archive", "item_id": "ncert-fhdv1"},
        ]
    },
    {
        "class": 6, "subject": "Maths", "title": "Mathematics",
        "sources": [
            {"type": "archive", "item_id": "ncert-femh1"},
        ]
    },
    {
        "class": 6, "subject": "Science", "title": "Science",
        "sources": [
            {"type": "archive", "item_id": "ncert-fesc1"},
        ]
    },
    {
        "class": 6, "subject": "Social Science", "title": "Our Pasts - I (History)",
        "sources": [
            {"type": "archive", "item_id": "ncert-fess1"},
        ]
    },
    {
        "class": 6, "subject": "Social Science", "title": "The Earth Our Habitat (Geography)",
        "sources": [
            {"type": "archive", "item_id": "ncert-fess2"},
        ]
    },
    {
        "class": 6, "subject": "Social Science", "title": "Social and Political Life - I (Civics)",
        "sources": [
            {"type": "archive", "item_id": "ncert-fess3"},
        ]
    },
    {
        "class": 6, "subject": "Sanskrit", "title": "Ruchira - Prathamo Bhag",
        "sources": [
            {"type": "archive", "item_id": "ncert-fhsk1"},
        ]
    },

    # =========================================================================
    # CLASS 7  (11 books)
    # =========================================================================
    {
        "class": 7, "subject": "English", "title": "Honeycomb",
        "sources": [
            {"type": "archive", "item_id": "ncert-gehc1"},
        ]
    },
    {
        "class": 7, "subject": "English", "title": "An Alien Hand",
        "sources": [
            {"type": "archive", "item_id": "ncert-geah1"},
        ]
    },
    {
        "class": 7, "subject": "Hindi", "title": "Vasant - II",
        "sources": [
            {"type": "archive", "item_id": "ncert-ghvs1"},
        ]
    },
    {
        "class": 7, "subject": "Hindi", "title": "Durva - II",
        "sources": [
            # Try guessed IA item first (consistent naming convention)
            {"type": "archive", "item_id": "ncert-ghdv1"},
            # NCERT direct
            {"type": "ncert", "code": "ghdv1"},
            # Scrape Vedantu hub
            {"type": "scrape", "url": "https://www.vedantu.com/ncert-books/ncert-books-class-7-hindi-durva"},
        ]
    },
    {
        "class": 7, "subject": "Hindi", "title": "Bal Mahabharat Katha",
        "sources": [
            {"type": "archive", "item_id": "ncert-ghmb1"},
        ]
    },
    {
        "class": 7, "subject": "Maths", "title": "Mathematics",
        "sources": [
            {"type": "archive", "item_id": "NCERT_MathVII_2007"},
        ]
    },
    {
        "class": 7, "subject": "Science", "title": "Science",
        "sources": [
            {"type": "archive", "item_id": "sciencetextbookf0000bync"},
        ]
    },
    {
        "class": 7, "subject": "Social Science", "title": "Our Pasts - II (History)",
        "sources": [
            {"type": "archive", "item_id": "ncert-gess1"},
        ]
    },
    {
        "class": 7, "subject": "Social Science", "title": "Our Environment (Geography)",
        "sources": [
            {"type": "archive", "item_id": "ncert-gess2"},
        ]
    },
    {
        "class": 7, "subject": "Social Science", "title": "Social and Political Life - II (Civics)",
        "sources": [
            {"type": "archive", "item_id": "ncert-gess3"},
        ]
    },
    {
        "class": 7, "subject": "Sanskrit", "title": "Ruchira - II",
        "sources": [
            {"type": "archive", "item_id": "ncert-ghsk1"},
        ]
    },

    # =========================================================================
    # CLASS 8  (10 books)
    # =========================================================================
    {
        "class": 8, "subject": "English", "title": "Honeydew",
        "sources": [
            {"type": "archive", "item_id": "ncert-hehd1"},
        ]
    },
    {
        "class": 8, "subject": "English", "title": "It So Happened",
        "sources": [
            # Try guessed IA item first
            {"type": "archive", "item_id": "ncert-heih1"},
            # NCERT direct
            {"type": "ncert", "code": "heih1"},
            # Scrape BYJU'S
            {"type": "scrape", "url": "https://byjus.com/ncert-books-class-8-english/"},
        ]
    },
    {
        "class": 8, "subject": "Hindi", "title": "Vasant - III",
        "sources": [
            {"type": "archive", "item_id": "ncert-hhvs1"},
        ]
    },
    {
        "class": 8, "subject": "Hindi", "title": "Durva - III",
        "sources": [
            {"type": "archive", "item_id": "ncert-hhdv1"},
        ]
    },
    {
        "class": 8, "subject": "Maths", "title": "Mathematics",
        "sources": [
            {"type": "archive", "item_id": "ncert-hemh1"},
        ]
    },
    {
        "class": 8, "subject": "Science", "title": "Science",
        "sources": [
            {"type": "archive", "item_id": "ncert-hesc1"},
        ]
    },
    {
        "class": 8, "subject": "Social Science", "title": "Our Pasts - III (History)",
        "sources": [
            {"type": "archive", "item_id": "ncert-hess2"},
        ]
    },
    {
        "class": 8, "subject": "Social Science", "title": "Resources and Development (Geography)",
        "sources": [
            {"type": "archive", "item_id": "ncert-hhss4"},
            {"type": "ncert", "code": "hess4"},
        ]
    },
    {
        "class": 8, "subject": "Social Science", "title": "Social and Political Life - III (Civics)",
        "sources": [
            {"type": "archive", "item_id": "ncert-hess3"},
        ]
    },
    {
        "class": 8, "subject": "Sanskrit", "title": "Ruchira - III",
        "sources": [
            {"type": "archive", "item_id": "ruchira-bhag-3"},
        ]
    },

    # =========================================================================
    # CLASS 9  (12 books)
    # =========================================================================
    {
        "class": 9, "subject": "English", "title": "Beehive",
        "sources": [
            {"type": "archive", "item_id": "ncert-iebe1"},
        ]
    },
    {
        "class": 9, "subject": "English", "title": "Moments",
        "sources": [
            {"type": "archive", "item_id": "ncert-iemo1"},
        ]
    },
    {
        "class": 9, "subject": "English", "title": "Words and Expressions - I",
        "sources": [
            {"type": "archive", "item_id": "ncert-iewe1"},
        ]
    },
    {
        "class": 9, "subject": "Hindi", "title": "Kshitij - I",
        "sources": [
            {"type": "archive", "item_id": "ncert-ihks1"},
        ]
    },
    {
        "class": 9, "subject": "Hindi", "title": "Kritika - I",
        "sources": [
            {"type": "archive", "item_id": "ncert-ihkr1"},
        ]
    },
    {
        "class": 9, "subject": "Maths", "title": "Mathematics",
        "sources": [
            # Try NCERT direct first (most reliable for Class 9)
            {"type": "ncert", "code": "iemh1"},
            # Try guessed IA item
            {"type": "archive", "item_id": "ncert-iemh1"},
            # Scrape BYJU'S
            {"type": "scrape", "url": "https://byjus.com/cbse/class-9-math-book/"},
        ]
    },
    {
        "class": 9, "subject": "Science", "title": "Science",
        "sources": [
            {"type": "ncert", "code": "iesc1"},
            {"type": "archive", "item_id": "ncert-iesc1"},
            {"type": "scrape", "url": "https://byjus.com/ncert-science-book-class-9/"},
        ]
    },
    {
        "class": 9, "subject": "Social Science",
        "title": "India and the Contemporary World - I (History)",
        "sources": [
            # NCERT direct (user provided pattern)
            {"type": "direct", "url": "https://ncert.nic.in/textbook/pdf/iess1ps.pdf"},
            {"type": "archive", "item_id": "NCERT-Class-9-History"},
            {"type": "archive", "item_id": "ncert-iess1"},
        ]
    },
    {
        "class": 9, "subject": "Social Science",
        "title": "Contemporary India - I (Geography)",
        "sources": [
            {"type": "ncert", "code": "iess3"},
            {"type": "archive", "item_id": "ncert-iess3"},
            {"type": "scrape", "url": "https://byjus.com/ncert-book-class-9-social-science-geography/"},
        ]
    },
    {
        "class": 9, "subject": "Social Science", "title": "Democratic Politics - I (Civics)",
        "sources": [
            {"type": "archive", "item_id": "ncert-iess4"},
        ]
    },
    {
        "class": 9, "subject": "Social Science", "title": "Economics",
        "sources": [
            # User confirmed this direct URL works
            {"type": "direct", "url": "https://ncert.nic.in/textbook/pdf/iess2ps.pdf"},
            {"type": "archive", "item_id": "ncert-iess2"},
        ]
    },
    {
        "class": 9, "subject": "Sanskrit", "title": "Shemushi - Prathamo Bhag",
        "sources": [
            {"type": "archive", "item_id": "ncert-ihsh1"},
        ]
    },

    # =========================================================================
    # CLASS 6 (Hindi Medium)
    # =========================================================================
    {
        "class": 6, "subject": "Maths_Hindi", "title": "Ganit",
        "sources": [{"type": "archive", "item_id": "ncert-fhmh1"}, {"type": "ncert", "code": "fhmh1"}]
    },
    {
        "class": 6, "subject": "Science_Hindi", "title": "Vigyan",
        "sources": [{"type": "archive", "item_id": "ncert-fhsc1"}, {"type": "ncert", "code": "fhsc1"}]
    },
    {
        "class": 6, "subject": "Social_Science_History_Hindi", "title": "Hamare Atit - I",
        "sources": [{"type": "archive", "item_id": "ncert-fhss1"}, {"type": "ncert", "code": "fhss1"}]
    },
    {
        "class": 6, "subject": "Social_Science_Geography_Hindi", "title": "Prithvi Hamara Avas",
        "sources": [{"type": "archive", "item_id": "ncert-fhss2"}, {"type": "ncert", "code": "fhss2"}]
    },
    {
        "class": 6, "subject": "Social_Science_Civics_Hindi", "title": "Samajik Evam Rajnitik Jeevan - I",
        "sources": [{"type": "archive", "item_id": "ncert-fhss3"}, {"type": "ncert", "code": "fhss3"}]
    },

    # =========================================================================
    # CLASS 7 (Hindi Medium)
    # =========================================================================
    {
        "class": 7, "subject": "Maths_Hindi", "title": "Ganit",
        "sources": [{"type": "archive", "item_id": "ncert-ghmh1"}, {"type": "ncert", "code": "ghmh1"}]
    },
    {
        "class": 7, "subject": "Science_Hindi", "title": "Vigyan",
        "sources": [{"type": "archive", "item_id": "ncert-ghsc1"}, {"type": "ncert", "code": "ghsc1"}]
    },
    {
        "class": 7, "subject": "Social_Science_History_Hindi", "title": "Hamare Atit - II",
        "sources": [{"type": "archive", "item_id": "ncert-ghss1"}, {"type": "ncert", "code": "ghss1"}]
    },
    {
        "class": 7, "subject": "Social_Science_Geography_Hindi", "title": "Hamara Paryavaran",
        "sources": [{"type": "archive", "item_id": "ncert-ghss2"}, {"type": "ncert", "code": "ghss2"}]
    },
    {
        "class": 7, "subject": "Social_Science_Civics_Hindi", "title": "Samajik Evam Rajnitik Jeevan - II",
        "sources": [{"type": "archive", "item_id": "ncert-ghss3"}, {"type": "ncert", "code": "ghss3"}]
    },

    # =========================================================================
    # CLASS 8 (Hindi Medium)
    # =========================================================================
    {
        "class": 8, "subject": "Maths_Hindi", "title": "Ganit",
        "sources": [{"type": "archive", "item_id": "ncert-hhmh1"}, {"type": "ncert", "code": "hhmh1"}]
    },
    {
        "class": 8, "subject": "Science_Hindi", "title": "Vigyan",
        "sources": [{"type": "archive", "item_id": "ncert-hhsc1"}, {"type": "ncert", "code": "hhsc1"}]
    },
    {
        "class": 8, "subject": "Social_Science_History_Hindi", "title": "Hamare Atit - III",
        "sources": [{"type": "archive", "item_id": "ncert-hhss1"}, {"type": "ncert", "code": "hhss1"}]
    },
    {
        "class": 8, "subject": "Social_Science_Geography_Hindi", "title": "Sansadhan Avam Vikas",
        "sources": [{"type": "archive", "item_id": "ncert-hhss4"}, {"type": "ncert", "code": "hhss4"}]
    },
    {
        "class": 8, "subject": "Social_Science_Civics_Hindi", "title": "Samajik Evam Rajnitik Jeevan - III",
        "sources": [{"type": "archive", "item_id": "ncert-hhss3"}, {"type": "ncert", "code": "hhss3"}]
    },

    # =========================================================================
    # CLASS 9 (Hindi Medium)
    # =========================================================================
    {
        "class": 9, "subject": "Maths_Hindi", "title": "Ganit",
        "sources": [{"type": "archive", "item_id": "ncert-ihmh1"}, {"type": "ncert", "code": "ihmh1"}]
    },
    {
        "class": 9, "subject": "Science_Hindi", "title": "Vigyan",
        "sources": [{"type": "archive", "item_id": "ncert-ihsc1"}, {"type": "ncert", "code": "ihsc1"}]
    },
    {
        "class": 9, "subject": "Social_Science_History_Hindi", "title": "Bharat Aur Samkalin Vishwa - I",
        "sources": [{"type": "archive", "item_id": "ncert-ihss1"}, {"type": "ncert", "code": "ihss1"}]
    },
    {
        "class": 9, "subject": "Social_Science_Geography_Hindi", "title": "Samkalin Bharat - I",
        "sources": [{"type": "archive", "item_id": "ncert-ihss3"}, {"type": "ncert", "code": "ihss3"}]
    },
    {
        "class": 9, "subject": "Social_Science_Civics_Hindi", "title": "Loktantrik Rajniti - I",
        "sources": [{"type": "archive", "item_id": "ncert-ihss4"}, {"type": "ncert", "code": "ihss4"}]
    },
    {
        "class": 9, "subject": "Social_Science_Economics_Hindi", "title": "Arthashastra",
        "sources": [{"type": "archive", "item_id": "ncert-ihss2"}, {"type": "ncert", "code": "ihss2"}]
    }
]


# =============================================================================
# Download Helpers
# =============================================================================

def get_ia_pdf_url(item_id):
    """
    Query Internet Archive metadata API to find the best PDF download URL.
    Returns (pdf_url, pdf_size) or (None, 0).
    """
    meta_url = f"https://archive.org/metadata/{item_id}/files"
    for attempt in range(3):
        try:
            resp = SESSION.get(meta_url, timeout=30)
            if resp.status_code == 404:
                return None, 0
            if resp.status_code != 200:
                time.sleep(2 ** attempt)
                continue

            data = resp.json()
            files = data.get("result", [])
            if not files:
                return None, 0

            # Filter PDF files
            pdf_files = [
                f for f in files
                if f.get("name", "").lower().endswith(".pdf")
                and f.get("format", "").upper() != "METADATA"
            ]

            if not pdf_files:
                return None, 0

            # Priority: files with "ps" in name (page scans = full book)
            ps_files = [f for f in pdf_files if "ps" in f["name"].lower()]
            if ps_files:
                best = max(ps_files, key=lambda f: int(f.get("size", "0")))
            else:
                # Fall back to largest PDF
                best = max(pdf_files, key=lambda f: int(f.get("size", "0")))

            name = best["name"]
            size = int(best.get("size", "0"))
            url = f"https://archive.org/download/{item_id}/{requests.utils.quote(name)}"
            return url, size

        except Exception:
            if attempt < 2:
                time.sleep(2 ** attempt)
    return None, 0


def download_file(url, dest_path):
    """
    Stream-download a file. Returns file size in bytes, or 0 on failure.
    """
    for attempt in range(3):
        try:
            resp = SESSION.get(url, stream=True, timeout=180, allow_redirects=True)
            if resp.status_code != 200:
                print(f"      HTTP {resp.status_code}")
                time.sleep(2 ** attempt)
                continue

            content_type = resp.headers.get("content-type", "")
            # Reject HTML responses masquerading as PDF downloads
            if "text/html" in content_type and "pdf" not in content_type:
                print(f"      Got HTML instead of PDF, skipping")
                return 0

            total = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = (downloaded / total) * 100
                            mb = downloaded / (1024 * 1024)
                            print(f"\r      {mb:.1f} MB ({pct:.0f}%)", end="", flush=True)
                        else:
                            mb = downloaded / (1024 * 1024)
                            print(f"\r      {mb:.1f} MB", end="", flush=True)

            print()  # newline after progress

            # Verify: must be >10KB and start with PDF magic bytes
            if downloaded < 10240:
                print(f"      File too small ({downloaded} bytes), discarding")
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                return 0

            with open(dest_path, "rb") as f:
                magic = f.read(5)
            if magic != b"%PDF-":
                print(f"      Not a valid PDF (magic: {magic!r}), discarding")
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                return 0

            return downloaded

        except Exception as e:
            print(f"      Error: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            if attempt < 2:
                time.sleep(2 ** attempt)

    return 0


def try_scrape_pdf(url, dest_path):
    """
    Scrape an HTML page for PDF links, download the best match.
    Returns file size or 0.
    """
    try:
        resp = SESSION.get(url, timeout=30)
        if resp.status_code != 200:
            print(f"      Scrape failed: HTTP {resp.status_code}")
            return 0

        # Find all PDF links
        pdf_links = re.findall(
            r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
            resp.text, re.IGNORECASE
        )

        if not pdf_links:
            print(f"      No PDF links found on page")
            return 0

        # Filter for NCERT-related PDFs (prefer these)
        ncert_pdfs = [l for l in pdf_links if any(
            kw in l.lower() for kw in ["ncert", "textbook", "chapter", "book"]
        )]

        candidates = ncert_pdfs if ncert_pdfs else pdf_links

        # Try to find a full-book PDF (has "ps" or "full" or is biggest)
        full_book = [l for l in candidates if "ps" in l.lower() or "full" in l.lower()]
        if full_book:
            candidates = full_book

        # Make URLs absolute
        from urllib.parse import urljoin
        candidates = [urljoin(url, c) for c in candidates]

        # Remove duplicates
        seen = set()
        unique = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                unique.append(c)

        print(f"      Found {len(unique)} PDF link(s), trying first...")

        for pdf_url in unique[:3]:  # Try up to 3
            print(f"      Trying: {pdf_url[:100]}...")
            size = download_file(pdf_url, dest_path)
            if size > 0:
                return size

        return 0

    except Exception as e:
        print(f"      Scrape error: {e}")
        return 0


# =============================================================================
# Main Download Logic
# =============================================================================

def download_textbook(book):
    """
    Attempt to download a single textbook. Tries sources in priority order.
    Returns a log entry dict.
    """
    cls = book["class"]
    subject = book["subject"]
    title = book["title"]
    sources = book["sources"]

    folder_mapping = {
        "Maths_Hindi": "गणित (Maths)",
        "Science_Hindi": "विज्ञान (Science)",
        "Social_Science_History_Hindi": "सामाजिक विज्ञान (Social Science)",
        "Social_Science_Geography_Hindi": "सामाजिक विज्ञान (Social Science)",
        "Social_Science_Civics_Hindi": "सामाजिक विज्ञान (Social Science)",
        "Social_Science_Economics_Hindi": "सामाजिक विज्ञान (Social Science)",
    }
    
    # Use mapped subject if available
    folder_name = folder_mapping.get(subject, subject)

    # Prepare destination
    dest_dir = os.path.join(BASE_DIR, f"Class {cls}", folder_name)
    os.makedirs(dest_dir, exist_ok=True)

    # Clean title for filename (remove chars illegal in Windows filenames)
    safe_title = re.sub(r'[<>:"/\\|?*]', '-', title)
    dest_path = os.path.join(dest_dir, f"{safe_title}.pdf")

    entry = {
        "class": cls,
        "subject": subject,
        "title": title,
        "status": "FAILED",
        "source_used": "",
        "url": "",
        "file_size": 0,
        "save_path": dest_path,
        "error": "",
    }

    # Skip if already downloaded
    if os.path.exists(dest_path):
        size = os.path.getsize(dest_path)
        if size > 10240:
            entry["status"] = "SKIPPED_EXISTS"
            entry["file_size"] = size
            print(f"  SKIP  (already exists, {size/1024/1024:.1f} MB)")
            return entry

    # Try each source in order
    for i, source in enumerate(sources, 1):
        src_type = source["type"]
        print(f"  [{i}/{len(sources)}] Trying: {src_type}", end="")

        try:
            if src_type == "archive":
                item_id = source["item_id"]
                print(f" ({item_id})")
                pdf_url, expected_size = get_ia_pdf_url(item_id)
                if pdf_url:
                    print(f"      Found PDF: {pdf_url}")
                    size = download_file(pdf_url, dest_path)
                    if size > 0:
                        entry.update({
                            "status": "SUCCESS",
                            "source_used": f"archive:{item_id}",
                            "url": pdf_url,
                            "file_size": size,
                        })
                        print(f"  ==> SUCCESS: {size/1024/1024:.1f} MB")
                        return entry
                else:
                    print(f"      No PDF found in IA item")

            elif src_type == "direct":
                url = source["url"]
                print(f" ({url})")
                size = download_file(url, dest_path)
                if size > 0:
                    entry.update({
                        "status": "SUCCESS",
                        "source_used": f"direct",
                        "url": url,
                        "file_size": size,
                    })
                    print(f"  ==> SUCCESS: {size/1024/1024:.1f} MB")
                    return entry

            elif src_type == "ncert":
                code = source["code"]
                url = f"https://ncert.nic.in/textbook/pdf/{code}ps.pdf"
                print(f" ({url})")
                size = download_file(url, dest_path)
                if size > 0:
                    entry.update({
                        "status": "SUCCESS",
                        "source_used": f"ncert:{code}",
                        "url": url,
                        "file_size": size,
                    })
                    print(f"  ==> SUCCESS: {size/1024/1024:.1f} MB")
                    return entry

            elif src_type == "scrape":
                url = source["url"]
                print(f" ({url})")
                size = try_scrape_pdf(url, dest_path)
                if size > 0:
                    entry.update({
                        "status": "SUCCESS",
                        "source_used": f"scrape:{url}",
                        "url": url,
                        "file_size": size,
                    })
                    print(f"  ==> SUCCESS: {size/1024/1024:.1f} MB")
                    return entry

        except Exception as e:
            print(f"      Exception: {e}")
            entry["error"] = str(e)
            if os.path.exists(dest_path):
                os.remove(dest_path)

    # All sources exhausted
    entry["status"] = "FAILED"
    print(f"  ==> FAILED: Could not download from any source")
    return entry


def write_log(log_entries, elapsed_seconds):
    """Write a comprehensive log file."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("NCERT TEXTBOOK DOWNLOAD LOG\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Elapsed:   {elapsed_seconds:.0f} seconds\n")
        f.write("=" * 80 + "\n\n")

        # Summary
        total = len(log_entries)
        success = sum(1 for e in log_entries if e["status"] == "SUCCESS")
        skipped = sum(1 for e in log_entries if e["status"] == "SKIPPED_EXISTS")
        failed = sum(1 for e in log_entries if e["status"] == "FAILED")
        total_size = sum(e["file_size"] for e in log_entries if e["status"] in ("SUCCESS", "SKIPPED_EXISTS"))

        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total textbooks:     {total}\n")
        f.write(f"Successfully saved:  {success}\n")
        f.write(f"Skipped (existed):   {skipped}\n")
        f.write(f"Failed:              {failed}\n")
        f.write(f"Total size:          {total_size/1024/1024:.1f} MB\n")
        f.write("\n")

        # Group by class
        for cls in [6, 7, 8, 9]:
            class_entries = [e for e in log_entries if e["class"] == cls]
            if not class_entries:
                continue

            f.write("=" * 80 + "\n")
            f.write(f"CLASS {cls}\n")
            f.write("=" * 80 + "\n")

            for e in class_entries:
                status_icon = {
                    "SUCCESS": "OK",
                    "SKIPPED_EXISTS": "SKIP",
                    "FAILED": "FAIL",
                }.get(e["status"], "??")

                f.write(f"\n  [{status_icon}] {e['subject']} — {e['title']}\n")
                if e["status"] in ("SUCCESS", "SKIPPED_EXISTS"):
                    f.write(f"        Size:   {e['file_size']/1024/1024:.1f} MB\n")
                    f.write(f"        Path:   {e['save_path']}\n")
                    if e.get("url"):
                        f.write(f"        URL:    {e['url']}\n")
                    if e.get("source_used"):
                        f.write(f"        Source: {e['source_used']}\n")
                else:
                    f.write(f"        Status: FAILED — could not download from any source\n")
                    if e.get("error"):
                        f.write(f"        Error:  {e['error']}\n")

            f.write("\n")

        # Failed list at the end for quick reference
        failed_entries = [e for e in log_entries if e["status"] == "FAILED"]
        if failed_entries:
            f.write("\n" + "=" * 80 + "\n")
            f.write("FAILED DOWNLOADS (QUICK REFERENCE)\n")
            f.write("=" * 80 + "\n")
            for e in failed_entries:
                f.write(f"  Class {e['class']} | {e['subject']} | {e['title']}\n")

    print(f"\nLog written to: {LOG_FILE}")


def main():
    print("=" * 70)
    print("  NCERT Textbook Downloader — Class 6 to 9")
    print(f"  Save directory: {BASE_DIR}")
    print(f"  Total textbooks: {len(TEXTBOOKS)}")
    print("=" * 70)

    os.makedirs(BASE_DIR, exist_ok=True)

    log_entries = []
    start_time = time.time()

    for i, book in enumerate(TEXTBOOKS, 1):
        cls = book["class"]
        title = book["title"]
        subject = book["subject"]

        print(f"\n[{i}/{len(TEXTBOOKS)}] Class {cls} | {subject} | {title}")
        print("-" * 60)

        entry = download_textbook(book)
        log_entries.append(entry)

        # Small delay between downloads to be polite
        if entry["status"] == "SUCCESS":
            time.sleep(1)

    elapsed = time.time() - start_time

    # Write log
    write_log(log_entries, elapsed)

    # Print final summary
    success = sum(1 for e in log_entries if e["status"] == "SUCCESS")
    skipped = sum(1 for e in log_entries if e["status"] == "SKIPPED_EXISTS")
    failed = sum(1 for e in log_entries if e["status"] == "FAILED")

    print("\n" + "=" * 70)
    print(f"  DONE in {elapsed:.0f}s")
    print(f"  Success: {success} | Skipped: {skipped} | Failed: {failed}")
    print("=" * 70)

    if failed > 0:
        print("\n  Failed books:")
        for e in log_entries:
            if e["status"] == "FAILED":
                print(f"    - Class {e['class']} | {e['subject']} | {e['title']}")


if __name__ == "__main__":
    main()
