from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import concurrent.futures
import threading
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from fpdf import FPDF

from core.config import config
from core.generator import generate_notes
from core.pdf_exporter import BOLD_FONT_CANDIDATES, FONT_CANDIDATES, _pick_font
from core.pdf_loader import extract_pdf_pages
from core.rag_store import collection_stats, delete_collection, index_pages
from core.text_utils import clean_text, safe_filename


# ── Tee stdout to a fixed log file so the dashboard can read it ──
class _Tee:
    """Write to both the original stdout and a log file."""
    def __init__(self, log_path: Path):
        self._stdout = sys.stdout
        self._log = open(log_path, "w", encoding="utf-8", buffering=1)  # line-buffered

    def write(self, data):
        self._stdout.write(data)
        try:
            self._log.write(data)
            self._log.flush()
        except Exception:
            pass

    def flush(self):
        self._stdout.flush()
        try:
            self._log.flush()
        except Exception:
            pass

    def reconfigure(self, **kwargs):
        """Forward reconfigure to the underlying stdout."""
        if hasattr(self._stdout, 'reconfigure'):
            self._stdout.reconfigure(**kwargs)

    @property
    def encoding(self):
        return getattr(self._stdout, 'encoding', 'utf-8')

_LOG_FILE = Path(r"C:\Users\bhask\Desktop\Archive\New folder") / "batch_generation.log"
sys.stdout = _Tee(_LOG_FILE)

BASE_DIR = Path(r"C:\Users\bhask\Desktop\Archive\New folder")

STUDY_MATERIALS_DIR = Path(r"C:\Users\bhask\Desktop\Study Materials")

ENGLISH_MEDIUM = {
    "6th": STUDY_MATERIALS_DIR / "data" / "school" / "class_6",
    "7th": STUDY_MATERIALS_DIR / "data" / "school" / "class_7",
    "8th": STUDY_MATERIALS_DIR / "data" / "school" / "class_8",
    "9th": STUDY_MATERIALS_DIR / "data" / "school" / "class_9",
    "11th_Science": BASE_DIR / "English" / "11th & 12th" / "11th Science",
    "11th_Commerce": BASE_DIR / "English" / "11th & 12th" / "11th Commerce",
    "12th_Science": BASE_DIR / "English" / "11th & 12th" / "12th Science",
    "12th_Commerce": BASE_DIR / "English" / "11th & 12th" / "12th Commerce",
}

HINDI_MEDIUM = {
    "6th": BASE_DIR / "Hindi" / "Class 6th",
    "7th": BASE_DIR / "Hindi" / "Class 7th",
    "8th": BASE_DIR / "Hindi" / "Class 8th",
    "9th": BASE_DIR / "Hindi" / "9th Class",
    "10th": Path(r"C:\Users\bhask\Desktop\Study Materials\Class 10\Hindi"),
    "11th_Science": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 11th Science"),
    "11th_Commerce": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 11th Commerce"),
    "11th_Humanities": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 11th Humanities"),
    "12th_Science": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 12th Science"),
    "12th_Commerce": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 12th Commerce"),
    "12th_Humanities": Path(r"C:\Users\bhask\Desktop\notes_textbooks_Hindi_meduim_11th and 12th\11th &12th\Class 12th Humanities"),
}



@dataclass(frozen=True)
class Chapter:
    subject: str
    subcategory: str
    subject_key: str
    name: str
    path: Path


def clean_chapter_name(path: Path) -> str:
    name = re.sub(r"_create$", "", path.stem, flags=re.IGNORECASE)
    # Strip download watermark suffixes like "_1600_pdf.gdrive.vip"
    name = re.sub(r"[-_]*\d*[-_]*pdf\.gdrive\.vip$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[-_]*\d+[-_]*pdf\.gdrive.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[-_\s]*\d+\s*pdf[.\s]*gdrive[.\s]*vip$", "", name, flags=re.IGNORECASE)
    name = name.replace("_", " ")
    name = re.sub(r"\s+", " ", name).strip()
    name = re.sub(r"[-\s]+$", "", name)  # strip trailing dashes
    name = re.sub(r"^(Chapter|Ch|CH)\s*[-_.]\s*", "Chapter ", name, flags=re.IGNORECASE)
    name = re.sub(r"^(Chapter|Ch|CH)\s+(\d+)\s+", r"Chapter \2: ", name, flags=re.IGNORECASE)
    return name


def sort_key(value: str) -> tuple[int, str]:
    match = re.search(r"(\d+)", value)
    return (int(match.group(1)) if match else 999, value.lower())


def has_pdfs(folder: Path) -> bool:
    return folder.is_dir() and any(folder.rglob("*.pdf"))


def dedupe_pdfs(files: list[Path]) -> list[Path]:
    seen: dict[str, Path] = {}
    for file in files:
        stem = re.sub(r"_create$", "", file.stem, flags=re.IGNORECASE)
        current = seen.get(stem)
        if current is None or "_create" not in file.stem.lower():
            seen[stem] = file
    return sorted(seen.values(), key=lambda path: sort_key(path.name))


def collect_chapters(class_dir: Path) -> OrderedDict[str, OrderedDict[str, list[Chapter]]]:
    subjects: OrderedDict[str, OrderedDict[str, list[Chapter]]] = OrderedDict()
    if not class_dir.exists():
        return subjects

    for subject_dir in sorted((p for p in class_dir.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        subject_name = subject_dir.name
        if subject_name.lower() in ["notes", "generated_notes", "textbooks"]:
            continue
        subcats: OrderedDict[str, list[Chapter]] = OrderedDict()

        # Always collect root-level PDFs first (fixes missing math chapters)
        root_pdfs = [f for f in subject_dir.iterdir() if f.is_file() and f.suffix.lower() == ".pdf" and "notes" not in str(f.parent).lower()]
        if root_pdfs:
            chapters = [
                Chapter(subject_name, "_main", subject_name, clean_chapter_name(file), file)
                for file in dedupe_pdfs(root_pdfs)
            ]
            if chapters:
                subcats["_main"] = chapters

        # Then collect subfolder PDFs
        child_pdf_dirs = [
            p for p in sorted(subject_dir.iterdir(), key=lambda x: x.name.lower())
            if has_pdfs(p) and p.name.lower() == "notes"
        ]
        for sub_dir in child_pdf_dirs:
            pdf_files = [f for f in sub_dir.rglob("*.pdf")]
            chapters = [
                Chapter(subject_name, sub_dir.name, f"{subject_name} / {sub_dir.name}", clean_chapter_name(file), file)
                for file in dedupe_pdfs(pdf_files)
            ]
            if chapters:
                subcats[sub_dir.name] = chapters

        if subcats:
            subjects[subject_name] = subcats
    return subjects


class CombinedNotesPDF(FPDF):
    def __init__(self, title: str):
        super().__init__(format="A4")
        self.title = title
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(15, 14, 15)

    def header(self) -> None:
        if self.page_no() <= 1:
            return
        self.set_font("Body", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 7, self.title, align="R", new_x="LMARGIN", new_y="NEXT")

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("Body", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"Page {self.page_no()}", align="C", new_x="LMARGIN", new_y="NEXT")


def add_fonts(pdf: FPDF) -> None:
    regular_deva = Path(__file__).parent / "core" / "NotoSansDevanagari-Regular.ttf"
    bold_deva = Path(__file__).parent / "core" / "NotoSansDevanagari-Bold.ttf"
    
    # Primary font: Arial (handles English/Latin)
    pdf.add_font("Body", "", "C:/Windows/Fonts/arial.ttf")
    pdf.add_font("Body", "B", "C:/Windows/Fonts/arialbd.ttf")
    
    # Fallback font: NotoSansDevanagari (handles Hindi/Devanagari)
    pdf.add_font("Devanagari", "", str(regular_deva))
    pdf.add_font("Devanagari", "B", str(bold_deva))
    pdf.set_fallback_fonts(["Devanagari"])


def write_line(pdf: FPDF, text: str, size: float = 10, bold: bool = False, color: tuple[int, int, int] = (45, 45, 45)) -> None:
    text = clean_text(text).replace("\x00", " ")
    pdf.set_font("Body", "B" if bold else "", size)
    pdf.set_text_color(*color)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, max(5, size * 0.55), text, new_x="LMARGIN", new_y="NEXT")


def render_markdown(pdf: FPDF, markdown: str) -> None:
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            pdf.ln(2)
            continue
        if line.startswith("# "):
            write_line(pdf, line[2:], 16, True, (20, 60, 95))
            pdf.ln(1)
        elif line.startswith("## "):
            write_line(pdf, line[3:], 13, True, (35, 80, 120))
        elif line.startswith("### "):
            write_line(pdf, line[4:], 11, True, (35, 35, 35))
        elif line.startswith(("- ", "* ")):
            write_line(pdf, "- " + line[2:], 9.5, False)
        else:
            line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
            line = re.sub(r"\*([^*]+)\*", r"\1", line)
            write_line(pdf, line, 9.5, False)


def cache_key(chapter: Chapter) -> str:
    return f"{chapter.subject}||{chapter.subcategory}||{chapter.name}"


def build_combined_pdf(class_name: str, medium: str, subjects: OrderedDict[str, OrderedDict[str, list[Chapter]]], processed: dict[str, str]) -> Path:
    output_path = config.output_dir / f"RAG_Class_{class_name}_{medium}_Medium_Exam_Notes.pdf"
    config.output_dir.mkdir(parents=True, exist_ok=True)

    title = f"Class {class_name} - {medium} Medium RAG Exam Notes"
    pdf = CombinedNotesPDF(title)
    pdf.set_text_shaping(True)
    add_fonts(pdf)

    pdf.add_page()
    pdf.ln(45)
    write_line(pdf, f"Class {class_name}", 26, True, (20, 60, 95))
    write_line(pdf, f"{medium} Medium", 18, True, (35, 80, 120))
    pdf.ln(8)
    write_line(pdf, "Local RAG Exam Notes", 13, False, (80, 80, 80))
    write_line(pdf, "Generated with Ollama, ChromaDB, and sentence-transformers", 10, False, (120, 120, 120))

    pdf.add_page()
    write_line(pdf, "Table of Contents", 18, True, (20, 60, 95))
    for subject, subcats in subjects.items():
        pdf.ln(2)
        write_line(pdf, subject, 12, True, (35, 80, 120))
        for subcat, chapters in subcats.items():
            if subcat != "_main":
                write_line(pdf, f"  {subcat}", 10.5, True, (70, 95, 130))
            for chapter in chapters:
                write_line(pdf, f"    - {chapter.name}", 8.5, False, (80, 80, 80))

    for subject, subcats in subjects.items():
        pdf.add_page()
        write_line(pdf, subject, 22, True, (20, 60, 95))
        for subcat, chapters in subcats.items():
            if subcat != "_main":
                pdf.add_page()
                write_line(pdf, subcat, 16, True, (35, 80, 120))
            for chapter in chapters:
                notes = processed.get(cache_key(chapter))
                if notes:
                    pdf.add_page()
                    render_markdown(pdf, notes)

    pdf.output(output_path)
    return output_path


def load_cache(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_cache(path: Path, data: dict[str, str]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def process_class(class_name: str, class_dir: Path, medium: str, args: argparse.Namespace) -> Path | None:
    print(f"\n{'=' * 70}")
    print(f"RAG batch: Class {class_name} - {medium} Medium")
    print(f"Source: {class_dir}")
    print(f"{'=' * 70}")

    subjects = collect_chapters(class_dir)
    total = sum(len(chapters) for subcats in subjects.values() for chapters in subcats.values())
    if total == 0:
        print("No PDFs found.")
        return None

    print(f"Found {len(subjects)} subjects, {total} PDF chapters.")
    collection_name = f"rag_{safe_filename(class_name)}_{safe_filename(medium)}".lower()
    if args.reindex:
        delete_collection(collection_name)

    stats = collection_stats(collection_name)
    if args.reindex or stats["chunks"] == 0:
        print(f"Indexing PDFs into Chroma collection '{collection_name}'...")
        indexed_total = 0
        done = 0
        for subcats in subjects.values():
            for chapters in subcats.values():
                for chapter in chapters:
                    done += 1
                    print(f"  [{done}/{total}] Index {chapter.subject_key} > {chapter.name[:70]}...", flush=True)
                    pages = extract_pdf_pages(chapter.path, subject=chapter.subject_key, unit=chapter.name, root=class_dir)
                    indexed_total += index_pages(pages, collection_name, args.chunk_size, args.chunk_overlap)
        print(f"Indexed {indexed_total} chunks.")
    else:
        print(f"Using existing Chroma collection '{collection_name}' with {stats['chunks']} chunks.")

    cache_file = BASE_DIR / f"rag_cache_Class_{class_name}_{medium}.json"
    processed = load_cache(cache_file)
    done = 0
    cache_lock = threading.Lock()

    def process_chapter(chapter: Chapter) -> None:
        nonlocal done
        key = cache_key(chapter)
        if key in processed:
            with cache_lock:
                done += 1
                print(f"  [{done}/{total}] SKIP cached: {chapter.subject_key} > {chapter.name[:60]}")
            return

        with cache_lock:
            done += 1
            print(f"  [{done}/{total}] Generate: {chapter.subject_key} > {chapter.name[:60]}...", flush=True)

        try:
            notes, _chunks = generate_notes(
                subject=chapter.subject_key,
                unit=chapter.name,
                mode=args.mode,
                collection_name=collection_name,
                top_k=args.top_k,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                context_length=args.context_length,
                class_name=class_name,
                extra_instruction=(
                    "Write all formulas in plain text only. "
                    "NEVER use $ signs or LaTeX notation. "
                    "Use Unicode symbols: x², √x, ×, ÷, ±, ≥, ≤ instead."
                ),
                is_hindi_medium=(medium.lower() == "hindi"),
            )
            with cache_lock:
                processed[key] = notes
                save_cache(cache_file, processed)
                print(f"      OK: {chapter.name[:40]}")
        except Exception as exc:
            with cache_lock:
                print(f"      FAILED: {chapter.name[:40]} - {exc}")
        time.sleep(args.pause)

    all_chapters = [
        chapter 
        for subcats in subjects.values() 
        for chapters in subcats.values() 
        for chapter in chapters
    ]

    if getattr(args, 'workers', 1) > 1:
        print(f"Starting ThreadPoolExecutor with {args.workers} workers...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            # We use a list to consume the iterator and wait for all to finish
            list(executor.map(process_chapter, all_chapters))
    else:
        for chapter in all_chapters:
            process_chapter(chapter)

    print("Building combined PDF...")
    output = build_combined_pdf(class_name, medium, subjects, processed)
    print(f"Saved: {output}")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automatic all-PDF batch generator using the local RAG pipeline.")
    parser.add_argument("--classes", nargs="+", default=["6th", "7th", "8th"])
    parser.add_argument("--mediums", nargs="+", default=["English", "Hindi"])
    parser.add_argument("--mode", default="Quick Revision")
    parser.add_argument("--top-k", type=int, default=int(os.getenv("RAG_BATCH_TOP_K", "8")))
    parser.add_argument("--max-tokens", type=int, default=int(os.getenv("RAG_BATCH_MAX_TOKENS", "2000")))
    parser.add_argument("--context-length", type=int, default=int(os.getenv("RAG_BATCH_CONTEXT_LENGTH", "8192")))
    parser.add_argument("--temperature", type=float, default=float(os.getenv("RAG_BATCH_TEMPERATURE", "0.2")))
    parser.add_argument("--chunk-size", type=int, default=int(os.getenv("RAG_BATCH_CHUNK_SIZE", "1100")))
    parser.add_argument("--chunk-overlap", type=int, default=int(os.getenv("RAG_BATCH_CHUNK_OVERLAP", "160")))
    parser.add_argument("--pause", type=float, default=float(os.getenv("RAG_BATCH_PAUSE", "0.1")))
    parser.add_argument("--workers", type=int, default=int(os.getenv("RAG_BATCH_WORKERS", "2")))
    parser.add_argument("--reindex", action="store_true")
    return parser.parse_args()


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    results: list[Path] = []
    for medium in args.mediums:
        source_map = ENGLISH_MEDIUM if medium.lower() == "english" else HINDI_MEDIUM
        for class_name in args.classes:
            if class_name not in source_map:
                print(f"Skipping {class_name} for {medium}: no source folder configured.")
                continue
            result = process_class(class_name, source_map[class_name], medium, args)
            if result:
                results.append(result)

    print("\nDone.")
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
