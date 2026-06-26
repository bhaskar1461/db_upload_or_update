SYSTEM_PROMPT = """You are an expert exam notes generator.

Your task is to convert textbook/PDF content into COMPREHENSIVE, CLEAN, EXAM-ORIENTED revision notes.

IMPORTANT GOALS:
* Include ALL important information from the chapter - do not skip anything useful for exams.
* Cover every key concept, definition, theorem, law, rule, character, event, theme, and moral.
* Generate thorough student-friendly notes that a student can rely on for last-minute revision.
* Provide VERY DETAILED, EXTENSIVE, and COMPREHENSIVE explanations. Do NOT summarize too briefly.
* Write long, exhaustive notes with a high word count for every concept.
* Do not hallucinate facts or formulas - use only the supplied context.
* Use bullets more than paragraphs.
* Include important dates, names, places, examples, and numerical values from the text.

STRICT FORMAT:
Generate exactly one markdown title and exactly these five markdown section headings:

# Class [Class] [Subject] - Chapter: [Chapter Name]

## 1. Introduction
## 2. Key Concepts
## 3. Important Formulas
## 4. Important Exam Points
## 5. Quick Summary

HEADING RULES:
* Keep the five section headings in English exactly as written above.
* Do not translate the section headings.
* Do not add extra markdown headings.
* Do not use Hindi heading words such as Parichay, Mukhya Avdharna, Sutra, Pariksha Bindoo, or Saaransh.

LANGUAGE RULES:
* If Hindi medium is requested, write explanatory content in Hindi Devanagari.
* EXCEPTION: If the subject is "English" (language/literature), ALWAYS write the notes in English regardless of medium. English subject notes must be in English even for Hindi medium students.
* Keep English words for examples, grammar terms, names, formulas, or quoted textbook phrases.
* If English medium is requested, write the content in English.

FORMULA EXTRACTION RULES:
* Extract important formulas, equations, statistical relationships, economic formulas, scientific laws, and numerical expressions from ALL subjects whenever applicable.
* Do NOT assume only Mathematics and Science chapters contain formulas. Social Science and Economics may contain GDP, growth rate, population density, trade balance formulas etc.
* Extract formulas even if they appear inside explanations or paragraphs.
* Write all formulas in plain text only. Never use LaTeX.
* If you need a fraction, write numerator / denominator. For square root, write sqrt(x).
* Keep formulas clean and separated as bullet points.
* Preserve formulas exactly as found in the source material.
* If a chapter genuinely contains no formulas or numerical relationships, write: None.
* For literature/language chapters, write: Not applicable (prose/poetry chapter).
"""


HINDI_MEDIUM_RULE = """CRITICAL HINDI-MEDIUM OUTPUT RULE:
The five markdown section headings must remain in English exactly:
## 1. Introduction
## 2. Key Concepts
## 3. Important Formulas
## 4. Important Exam Points
## 5. Quick Summary

Write the content under those headings in Hindi Devanagari.
Do not translate the five section headings into Hindi.
Do not add extra markdown headings.
"""


def get_system_prompt(
    subject: str,
    is_hindi_subject: bool = False,
    is_hindi_medium: bool = False,
) -> str:
    """Return the system prompt. Compatible with generator.py call signature."""

    is_english_subject = "english" in subject.lower()

    if is_english_subject:
        # English subject notes should ALWAYS be in English, even for Hindi medium
        lang_note = (
            "English subject mode. Write ALL notes in English. "
            "Focus on themes, characters, morals, literary devices, important quotes, and grammar rules. "
            "This applies even if the student is Hindi medium - English subject notes must be in English."
        )
    elif is_hindi_medium or is_hindi_subject:
        lang_note = (
            "Hindi-medium mode. Keep the required markdown headings in English exactly. "
            "Write all explanatory content in Hindi Devanagari."
        )
    else:
        lang_note = "English-medium mode. Write explanatory content in English."
    return f"{SYSTEM_PROMPT}\n\nSubject: {subject} | Language: {lang_note}"


def get_user_prompt(
    class_name: str,
    subject: str,
    chapter_name: str,
    context: str,
    mode: str = "Quick Revision",
    is_hindi_medium: bool = False,
) -> str:
    """Return the user prompt for a specific chapter."""

    lang = "Hindi" if is_hindi_medium else "English"
    hindi_rule = f"\n\n{HINDI_MEDIUM_RULE}" if is_hindi_medium else ""
    return (
        f"Generate EXTREMELY DETAILED and COMPREHENSIVE exam revision notes for:\n"
        f"Class: {class_name} | Subject: {subject} | Chapter: {chapter_name} | Language: {lang}\n"
        f"Mode: {mode}\n\n"
        f"Use ONLY the following textbook content:\n\n{context}"
        f"{hindi_rule}"
    )


def build_user_prompt(
    class_name: str,
    subject: str,
    unit: str,
    mode: str,
    context: str,
    extra_instruction: str = "",
    is_hindi_medium: bool = False,
) -> str:
    """Build user prompt compatible with generator.py call signature."""

    lang = "Hindi" if is_hindi_medium else "English"
    extra = f"\n\nAdditional instructions: {extra_instruction}" if extra_instruction else ""
    hindi_rule = f"\n\n{HINDI_MEDIUM_RULE}" if is_hindi_medium else ""
    return (
        f"Generate EXTREMELY DETAILED and COMPREHENSIVE exam revision notes for:\n"
        f"Class: {class_name} | Subject: {subject} | Chapter: {unit} | Language: {lang}\n"
        f"Mode: {mode}\n\n"
        f"Mandatory output skeleton:\n"
        f"# Class {class_name} {subject} - Chapter: {unit}\n"
        f"## 1. Introduction\n"
        f"## 2. Key Concepts\n"
        f"## 3. Important Formulas\n"
        f"## 4. Important Exam Points\n"
        f"## 5. Quick Summary\n\n"
        f"Use ONLY the following textbook content:\n\n{context}"
        f"{extra}"
        f"{hindi_rule}"
    )
