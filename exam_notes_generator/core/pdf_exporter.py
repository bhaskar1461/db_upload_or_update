from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from .config import config
from .logger import get_logger
from .text_utils import safe_filename


logger = get_logger(__name__)


FONT_CANDIDATES = [
    Path(__file__).parent / "NotoSansDevanagari-Regular.ttf",
    Path("C:/Windows/Fonts/NotoSans-Regular.ttf"),
    Path("C:/Windows/Fonts/Nirmala.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
]

BOLD_FONT_CANDIDATES = [
    Path(__file__).parent / "NotoSansDevanagari-Bold.ttf",
    Path("C:/Windows/Fonts/NotoSans-Bold.ttf"),
    Path("C:/Windows/Fonts/NirmalaB.ttf"),
    Path("C:/Windows/Fonts/arialbd.ttf"),
    Path("C:/Windows/Fonts/segoeuib.ttf"),
]


class NotesPDF(FPDF):
    def header(self) -> None:
        self.set_font("Body", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Generated Exam Notes", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Body", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _pick_font(candidates: list[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No usable Windows Unicode font found.")


def _safe_line(line: str) -> str:
    return line.replace("\x00", " ").encode("utf-8", errors="replace").decode("utf-8")


def export_notes_to_pdf(notes: str, subject: str, unit: str) -> Path:
    """Render markdown-like notes to a Unicode PDF with safe page wrapping."""

    config.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.output_dir / f"{safe_filename(subject)}__{safe_filename(unit)}.pdf"

    regular_deva = Path(__file__).parent / "NotoSansDevanagari-Regular.ttf"
    bold_deva = Path(__file__).parent / "NotoSansDevanagari-Bold.ttf"

    pdf = NotesPDF(format="A4")
    pdf.set_text_shaping(True)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(16, 14, 16)
    
    # Primary font: Arial (handles English/Latin)
    pdf.add_font("Body", "", "C:/Windows/Fonts/arial.ttf")
    pdf.add_font("Body", "B", "C:/Windows/Fonts/arialbd.ttf")
    
    # Fallback font: NotoSansDevanagari (handles Hindi/Devanagari)
    pdf.add_font("Devanagari", "", str(regular_deva))
    pdf.add_font("Devanagari", "B", str(bold_deva))
    pdf.set_fallback_fonts(["Devanagari"])
    pdf.add_page()

    for raw_line in notes.splitlines():
        line = _safe_line(raw_line.rstrip())
        stripped = line.strip()

        if not stripped:
            pdf.ln(4)
            continue

        if stripped.startswith("# "):
            pdf.set_font("Body", "B", 18)
            pdf.set_text_color(20, 60, 95)
            pdf.multi_cell(0, 10, stripped[2:].strip())
            pdf.ln(2)
        elif stripped.startswith("## "):
            pdf.set_font("Body", "B", 15)
            pdf.set_text_color(35, 80, 120)
            pdf.ln(2)
            pdf.multi_cell(0, 8, stripped[3:].strip())
        elif stripped.startswith("### "):
            pdf.set_font("Body", "B", 12)
            pdf.set_text_color(30, 30, 30)
            pdf.ln(1)
            pdf.multi_cell(0, 7, stripped[4:].strip())
        elif stripped.startswith(("- ", "* ")):
            pdf.set_font("Body", "", 10.5)
            pdf.set_text_color(35, 35, 35)
            pdf.multi_cell(0, 6, f"- {stripped[2:].strip()}")
        else:
            pdf.set_font("Body", "", 10.5)
            pdf.set_text_color(35, 35, 35)
            pdf.multi_cell(0, 6, stripped)

    pdf.output(output_path)
    logger.info("Exported PDF: %s", output_path)
    return output_path
