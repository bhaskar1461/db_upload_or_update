from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import fitz

from .config import config
from .logger import get_logger
from .text_utils import clean_text


logger = get_logger(__name__)


@dataclass
class ExtractedPage:
    text: str
    source: str
    page: int
    subject: str
    unit: str
    is_pyq: bool


def detect_pyq(path: Path) -> bool:
    name = path.name.lower()
    keywords = ["pyq", "previous", "paper", "question paper", "past paper", "model paper"]
    return any(keyword in name for keyword in keywords)


def infer_subject_unit(path: Path, root: Path | None = None) -> tuple[str, str]:
    """Infer subject and unit from folder names or the PDF filename."""

    try:
        relative = path.relative_to(root) if root else path
        parts = list(relative.parts)
    except ValueError:
        parts = list(path.parts)

    stem = path.stem
    if len(parts) >= 3:
        return parts[-3], path.stem
    if len(parts) >= 2:
        return parts[-2], stem
    return "General", stem


def discover_pdfs(folder: Path) -> list[Path]:
    """Find PDFs recursively in a folder."""

    if not folder.exists():
        return []
    return sorted(path for path in folder.rglob("*.pdf") if path.is_file())


def save_uploaded_pdfs(files: Iterable, subject: str) -> list[Path]:
    """Persist Streamlit uploads so Chroma metadata can point to stable file paths."""

    saved_paths: list[Path] = []
    subject_dir = config.uploads_dir / subject
    subject_dir.mkdir(parents=True, exist_ok=True)

    for uploaded_file in files:
        destination = subject_dir / Path(uploaded_file.name).name
        with destination.open("wb") as handle:
            shutil.copyfileobj(uploaded_file, handle)
        saved_paths.append(destination)

    return saved_paths


def extract_pdf_pages(path: Path, subject: str | None = None, unit: str | None = None, root: Path | None = None) -> list[ExtractedPage]:
    """Extract text page by page with robust handling for corrupted PDFs/pages."""

    inferred_subject, inferred_unit = infer_subject_unit(path, root)
    subject = subject or inferred_subject
    unit = unit or inferred_unit
    pages: list[ExtractedPage] = []

    try:
        with fitz.open(path) as document:
            for page_index in range(document.page_count):
                try:
                    page = document.load_page(page_index)
                    text = clean_text(page.get_text("text"))
                    if not text:
                        continue
                    pages.append(
                        ExtractedPage(
                            text=text,
                            source=str(path),
                            page=page_index + 1,
                            subject=subject,
                            unit=unit,
                            is_pyq=detect_pyq(path),
                        )
                    )
                except Exception as exc:
                    logger.warning("Skipped unreadable page %s in %s: %s", page_index + 1, path, exc)
    except Exception as exc:
        logger.error("Could not read PDF %s: %s", path, exc)

    return pages


def extract_many(paths: Iterable[Path], subject: str | None = None, root: Path | None = None) -> list[ExtractedPage]:
    """Extract pages from many PDFs, skipping unreadable files safely."""

    extracted: list[ExtractedPage] = []
    for path in paths:
        extracted.extend(extract_pdf_pages(path, subject=subject, root=root))
    return extracted
