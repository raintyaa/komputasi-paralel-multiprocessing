import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc_path = Path("d:/Rakha/File Kuliah/Semester 5/Komputasi Paralel/UTS/Laporan_Akhir_Komparasi_Kinerja_Paralel.docx")

doc = Document()

# -------------------------------------------------------------
# 1. SETUP PAGE PROPERTIES: A4, MARGIN 4-3-3-3 CM
# -------------------------------------------------------------
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(3.0)
    section.left_margin = Cm(4.0)
    section.right_margin = Cm(3.0)

# -------------------------------------------------------------
# 2. CONFIGURE STYLES
# -------------------------------------------------------------
# A. Normal Style
normal_style = doc.styles['Normal']
normal_font = normal_style.font
normal_font.name = 'Times New Roman'
normal_font.size = Pt(12)
normal_font.color.rgb = RGBColor(0, 0, 0)
normal_p_format = normal_style.paragraph_format
normal_p_format.line_spacing = 1.5
normal_p_format.space_before = Pt(0)
normal_p_format.space_after = Pt(0)
normal_p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# B. Heading 1: BAB X JUDUL BAB (Times New Roman 12 pt, Bold, Center)
h1_style = doc.styles['Heading 1']
h1_font = h1_style.font
h1_font.name = 'Times New Roman'
h1_font.size = Pt(12)
h1_font.bold = True
h1_font.color.rgb = RGBColor(0, 0, 0)
h1_p_format = h1_style.paragraph_format
h1_p_format.line_spacing = 1.5
h1_p_format.space_before = Pt(12)
h1_p_format.space_after = Pt(6)
h1_p_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
h1_p_format.first_line_indent = Cm(0)

# C. Heading 2: X.Y Subbab (Times New Roman 12 pt, Bold, Left)
h2_style = doc.styles['Heading 2']
h2_font = h2_style.font
h2_font.name = 'Times New Roman'
h2_font.size = Pt(12)
h2_font.bold = True
h2_font.color.rgb = RGBColor(0, 0, 0)
h2_p_format = h2_style.paragraph_format
h2_p_format.line_spacing = 1.5
h2_p_format.space_before = Pt(12)
h2_p_format.space_after = Pt(4)
h2_p_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
h2_p_format.first_line_indent = Cm(0)

# D. Heading 3: X.Y.Z Anak Subbab (Times New Roman 12 pt, Bold, Left)
h3_style = doc.styles['Heading 3']
h3_font = h3_style.font
h3_font.name = 'Times New Roman'
h3_font.size = Pt(12)
h3_font.bold = True
h3_font.color.rgb = RGBColor(0, 0, 0)
h3_p_format = h3_style.paragraph_format
h3_p_format.line_spacing = 1.5
h3_p_format.space_before = Pt(6)
h3_p_format.space_after = Pt(2)
h3_p_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
h3_p_format.first_line_indent = Cm(0)

# Helper function to add body paragraph with first-line indent 1.27 cm
def add_body_p(text=""):
    p = doc.add_paragraph()
    p.style = 'Normal'
    p.paragraph_format.first_line_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if text:
        p.add_run(text)
    return p

# Helper function to add centered bold title (for front matter like KATA PENGANTAR, DAFTAR ISI)
def add_front_title(text):
    p = doc.add_paragraph()
    p.style = 'Normal'
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    return p

# Helper function to add caption for table (top, center)
def add_table_caption(table_num, title_text):
    p = doc.add_paragraph()
    p.style = 'Normal'
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(f"Tabel {table_num}. {title_text}")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    return p

# Helper function to add caption for image (bottom, center)
def add_image_caption(img_num, title_text):
    p = doc.add_paragraph()
    p.style = 'Normal'
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(f"Gambar {img_num}. {title_text}")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    return p

print("Setup completed. Building document outline...")
