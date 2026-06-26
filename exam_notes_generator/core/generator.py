from __future__ import annotations

import re

from .config import config
from .llm_client import generate_with_llm
from .prompts import get_system_prompt, build_user_prompt
from .rag_store import retrieve_chunks
from .text_utils import estimate_tokens


def strip_latex(text: str) -> str:
    """Remove LaTeX delimiters and convert common macros to plain Unicode."""
    # Remove display-math blocks $$...$$
    text = re.sub(r'\$\$(.+?)\$\$', r'\1', text, flags=re.DOTALL)
    # Remove inline-math blocks $...$
    text = re.sub(r'\$(.+?)\$', r'\1', text, flags=re.DOTALL)
    # Convert \frac{a}{b} → a / b
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 / \2', text)
    # Convert \sqrt{x} → √x
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√\1', text)
    # Common symbol macros
    replacements = {
        r'\times': '×', r'\div': '÷', r'\cdot': '·',
        r'\pm': '±', r'\geq': '≥', r'\leq': '≤',
        r'\neq': '≠', r'\approx': '≈', r'\infty': '∞',
        r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ',
        r'\delta': 'δ', r'\pi': 'π', r'\theta': 'θ',
        r'\lambda': 'λ', r'\mu': 'μ', r'\sigma': 'σ',
        r'\Rightarrow': '⇒', r'\rightarrow': '→',
        r'\ ': ' ',  # escaped space
    }
    for macro, symbol in replacements.items():
        text = text.replace(macro, symbol)
    # Remove any remaining lone backslash-commands like \text{}, \left, \right
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # Collapse accidental double spaces
    text = re.sub(r'  +', ' ', text)
    return text


MODE_GUIDANCE = {
    "Full Exam Notes": "Create balanced, complete exam notes with all required sections.",
    "Quick Revision": "Be very concise. Focus on last-day revision, definitions, formulas, and likely questions.",
    "Long Answer Mode": "Add answer frameworks, step-by-step explanations, diagrams to draw, and long-answer points.",
    "Cheat Sheet": "Make a dense one-page style sheet with formulas, keywords, mistakes, and mini examples.",
    "Question Bank": "Prioritize 2-mark, 5-mark, important questions, PYQ focus, and viva questions.",
}

REQUIRED_HEADINGS = [
    "## 1. Introduction",
    "## 2. Key Concepts",
    "## 3. Important Formulas",
    "## 4. Important Exam Points",
    "## 5. Quick Summary",
]

SECTION_HEADING_RE = re.compile(r"^\s*#{2,6}\s*([1-5])\.\s*.*$")
TITLE_HEADING_RE = re.compile(r"^\s*#(?!#)\s+.*$")


def has_required_headings(text: str) -> bool:
    return all(heading in text for heading in REQUIRED_HEADINGS)


def enforce_required_headings(
    text: str,
    class_name: str,
    subject: str,
    unit: str,
    is_hindi_medium: bool,
) -> str:
    """Normalize generated markdown so the saved notes/PDF use the fixed headings.

    Local models sometimes translate heading labels even when the prompt says not to.
    This keeps the model's content but rewrites numbered section headings to the
    required English labels before saving the cache or PDF.
    """

    title = f"# Class {class_name} {subject} - Chapter: {unit}"
    sections: dict[str, list[str]] = {heading: [] for heading in REQUIRED_HEADINGS}
    current_heading = REQUIRED_HEADINGS[0]

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue

        if TITLE_HEADING_RE.match(stripped):
            continue

        section_match = SECTION_HEADING_RE.match(stripped)
        if section_match:
            current_heading = REQUIRED_HEADINGS[int(section_match.group(1)) - 1]
            continue

        if stripped.startswith("#"):
            # Preserve useful text from any extra heading as normal content.
            plain_heading = stripped.lstrip("#").strip()
            if plain_heading:
                sections[current_heading].append(f"- {plain_heading}")
            continue

        sections[current_heading].append(line)

    missing_text = (
        "- \u0909\u092a\u0932\u092c\u094d\u0927 \u092a\u093e\u0920\u094d\u092f \u0938\u093e\u092e\u0917\u094d\u0930\u0940 \u092e\u0947\u0902 \u0938\u094d\u092a\u0937\u094d\u091f \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0928\u0939\u0940\u0902 \u092e\u093f\u0932\u0940\u0964"
        if is_hindi_medium
        else "- Not available in the provided context."
    )

    normalized: list[str] = [title]
    for heading in REQUIRED_HEADINGS:
        normalized.extend(["", heading])
        content = sections[heading]
        if content:
            normalized.extend(content)
        elif heading == "## 3. Important Formulas":
            normalized.append("None.")
        else:
            normalized.append(missing_text)

    return "\n".join(normalized).strip() + "\n"


def format_context(chunks: list[dict], max_context_tokens: int) -> str:
    """Pack retrieved chunks into a bounded context window."""

    parts: list[str] = []
    used_tokens = 0

    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        source = metadata.get("source", "unknown")
        page = metadata.get("page", "?")
        is_pyq = "yes" if metadata.get("is_pyq") else "no"
        text = chunk["text"]
        block = f"[Chunk {index} | Source: {source} | Page: {page} | PYQ: {is_pyq}]\n{text}"
        tokens = estimate_tokens(block)
        if used_tokens + tokens > max_context_tokens:
            break
        used_tokens += tokens
        parts.append(block)

    return "\n\n---\n\n".join(parts)


def generate_notes(
    subject: str,
    unit: str,
    mode: str,
    collection_name: str,
    top_k: int,
    temperature: float,
    max_tokens: int,
    context_length: int,
    class_name: str,
    extra_instruction: str = "",
    is_hindi_medium: bool = False,
) -> tuple[str, list[dict]]:
    """Retrieve relevant chunks and generate structured notes."""

    query = (
        f"{subject} {unit} exam notes formulas important questions PYQ "
        f"common mistakes viva quick revision problem solving"
    )
    chunks = retrieve_chunks(
        query=query,
        collection_name=collection_name,
        subject=subject if subject else None,
        unit=unit if unit else None,
        top_k=top_k,
    )

    if not chunks and unit:
        chunks = retrieve_chunks(query=query, collection_name=collection_name, subject=subject or None, top_k=top_k)
    if not chunks:
        chunks = retrieve_chunks(query=query, collection_name=collection_name, top_k=top_k)

    max_context_tokens = max(1200, context_length - max_tokens - 900)
    context = format_context(chunks, max_context_tokens=max_context_tokens)
    mode_instruction = MODE_GUIDANCE.get(mode, MODE_GUIDANCE["Full Exam Notes"])
    user_prompt = build_user_prompt(
        class_name=class_name,
        subject=subject,
        unit=unit,
        mode=mode,
        context=context,
        extra_instruction=f"{mode_instruction}\n{extra_instruction}",
        is_hindi_medium=is_hindi_medium,
    )
    notes = generate_with_llm(
        system_prompt=get_system_prompt(subject, "hindi" in subject.lower(), is_hindi_medium),
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        context_length=context_length,
    )
    if is_hindi_medium and not has_required_headings(notes):
        retry_prompt = (
            f"{user_prompt}\n\n"
            "Your previous response did not follow the mandatory format. "
            "Regenerate from scratch. Use EXACTLY these English headings and no other headings:\n"
            "# Class [Class] [Subject] - Chapter: [Chapter Name]\n"
            "## 1. Introduction\n"
            "## 2. Key Concepts\n"
            "## 3. Important Formulas\n"
            "## 4. Important Exam Points\n"
            "## 5. Quick Summary\n\n"
            "Write all content under these headings in Hindi Devanagari."
        )
        notes = generate_with_llm(
            system_prompt=get_system_prompt(subject, "hindi" in subject.lower(), is_hindi_medium),
            user_prompt=retry_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            context_length=context_length,
        )
    notes = strip_latex(notes)
    if is_hindi_medium:
        notes = enforce_required_headings(notes, class_name, subject, unit, is_hindi_medium=True)
    return notes, chunks
