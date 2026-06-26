from __future__ import annotations

import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize extracted PDF text without destroying formulas or Unicode content."""

    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def safe_filename(value: str, fallback: str = "exam_notes") -> str:
    """Return a Windows-safe filename while preserving readable subject names."""

    value = clean_text(value) or fallback
    value = re.sub(r'[<>:"/\\|?*]+', "_", value)
    value = re.sub(r"\s+", "_", value).strip("._ ")
    return value[:120] or fallback


def estimate_tokens(text: str) -> int:
    """Fast rough token estimate for progress and batching decisions."""

    return max(1, len(text) // 4)
