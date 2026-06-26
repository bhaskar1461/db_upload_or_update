import sys
sys.stdout.reconfigure(encoding='utf-8')
from fpdf import FPDF
from pathlib import Path

# Test with arial
pdf = FPDF(format='A4')
pdf.set_text_shaping(True)
pdf.add_font('Body', '', 'C:/Windows/Fonts/arial.ttf')
pdf.add_page()
pdf.set_font('Body', '', 16)
pdf.multi_cell(0, 10, 'हिंदी (Hindi) - परिमेय संख्याएं')
pdf.ln()
pdf.multi_cell(0, 7, 'यह एक टेस्ट है। गणित के सूत्र: Area = l x b')
pdf.output('test_arial.pdf')
print('test_arial.pdf created')
