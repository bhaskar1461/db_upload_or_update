import sys
sys.stdout.reconfigure(encoding='utf-8')
from fpdf import FPDF
from pathlib import Path

pdf = FPDF(format='A4')
pdf.set_text_shaping(True)

font_path = Path(r'C:\Users\bhask\Desktop\New folder\exam_notes_generator\core\NotoSansDevanagari-Regular.ttf')
bold_path = Path(r'C:\Users\bhask\Desktop\New folder\exam_notes_generator\core\NotoSansDevanagari-Bold.ttf')

# Add Arial as the primary font
pdf.add_font('Body', '', 'C:/Windows/Fonts/arial.ttf')
pdf.add_font('Body', 'B', 'C:/Windows/Fonts/arialbd.ttf')

# Add NotoSansDevanagari as a fallback font!
pdf.add_font('Devanagari', '', str(font_path))
pdf.add_font('Devanagari', 'B', str(bold_path))
pdf.set_fallback_fonts(['Devanagari'])

pdf.add_page()
pdf.set_font('Body', 'B', 16)
pdf.multi_cell(0, 10, 'हिंदी (Hindi) - परिमेय संख्याएं')
pdf.ln()
pdf.set_font('Body', '', 12)
pdf.multi_cell(0, 7, 'यह एक टेस्ट है। गणित के सूत्र: Area = l x b')
pdf.output('test_fallback.pdf')
print('test_fallback.pdf created')
