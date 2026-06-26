import sys
sys.stdout.reconfigure(encoding='utf-8')
from fpdf import FPDF
from pathlib import Path

font_path = Path(r'C:\Users\bhask\Desktop\New folder\exam_notes_generator\core\NotoSansDevanagari-Regular.ttf')
bold_path = Path(r'C:\Users\bhask\Desktop\New folder\exam_notes_generator\core\NotoSansDevanagari-Bold.ttf')

# Test WITH text_shaping
pdf = FPDF(format='A4')
pdf.set_text_shaping(True)
pdf.add_font('Body', '', str(font_path))
pdf.add_font('Body', 'B', str(bold_path))
pdf.add_page()
pdf.set_font('Body', 'B', 16)
pdf.multi_cell(0, 10, 'हिंदी (Hindi) - परिमेय संख्याएं')
pdf.ln()
pdf.set_font('Body', '', 12)
pdf.multi_cell(0, 7, 'यह एक टेस्ट है। गणित के सूत्र: Area = l x b')
pdf.output('test_shaping_on.pdf')
print('test_shaping_on.pdf created')

# Test WITHOUT text_shaping
pdf2 = FPDF(format='A4')
pdf2.add_font('Body', '', str(font_path))
pdf2.add_font('Body', 'B', str(bold_path))
pdf2.add_page()
pdf2.set_font('Body', 'B', 16)
pdf2.multi_cell(0, 10, 'हिंदी (Hindi) - परिमेय संख्याएं')
pdf2.ln()
pdf2.set_font('Body', '', 12)
pdf2.multi_cell(0, 7, 'यह एक टेस्ट है। गणित के सूत्र: Area = l x b')
pdf2.output('test_shaping_off.pdf')
print('test_shaping_off.pdf created')
