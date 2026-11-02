import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
import re, sys

sys.stdout.reconfigure(encoding='utf-8')

MASTER_PATH = 'UTS/Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx'
doc = docx.Document(MASTER_PATH)

print(f"Loaded master document: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")

# Helper: enforce Times New Roman on a run
def enforce_tnr(run, size_pt=12.0, bold=None, italic=None, color_rgb=RGBColor(0, 0, 0)):
    run.font.name = 'Times New Roman'
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color_rgb is not None:
        run.font.color.rgb = color_rgb
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    rFonts.set(qn('w:cs'), 'Times New Roman')

# Helper: enforce Consolas on a run
def enforce_consolas(run, size_pt=9.5, bold=False, italic=False, color_rgb=RGBColor(30, 30, 30)):
    run.font.name = 'Consolas'
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color_rgb
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:ascii'), 'Consolas')
    rFonts.set(qn('w:hAnsi'), 'Consolas')
    rFonts.set(qn('w:cs'), 'Consolas')

# Set default document Normal style
style_normal = doc.styles['Normal']
style_normal.font.name = 'Times New Roman'
style_normal.font.size = Pt(12)
style_normal.font.color.rgb = RGBColor(0, 0, 0)
rFonts_norm = style_normal._element.get_or_add_rPr().get_or_add_rFonts()
rFonts_norm.set(qn('w:ascii'), 'Times New Roman')
rFonts_norm.set(qn('w:hAnsi'), 'Times New Roman')
rFonts_norm.set(qn('w:cs'), 'Times New Roman')

print("Step 1: Normal style set to Times New Roman 12 pt.")

# ==============================================================================
# STEP 2: HARMONIZE PARAGRAPHS, HEADINGS, CAPTIONS, AND NOTES
# ==============================================================================
count_headings = 0
count_captions_table = 0
count_captions_fig = 0
count_captions_code = 0
count_notes = 0
count_body = 0

for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        # Drawing paragraph
        if len(p._element.xpath('.//w:drawing')) > 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
        continue

    style_name = p.style.name.lower()

    # A. Headings
    if 'heading 1' in style_name:
        count_headings += 1
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        for r in p.runs:
            enforce_tnr(r, size_pt=14.0, bold=True)
    elif 'heading 2' in style_name:
        count_headings += 1
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        for r in p.runs:
            enforce_tnr(r, size_pt=12.0, bold=True)
    elif 'heading 3' in style_name:
        count_headings += 1
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
            enforce_tnr(r, size_pt=12.0, bold=True)
    elif 'heading non-nomor' in style_name:
        count_headings += 1
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(10)
        for r in p.runs:
            enforce_tnr(r, size_pt=12.0, bold=True)

    # B. Table Captions (starts with 'Tabel ')
    elif txt.startswith('Tabel ') and any(f'Tabel {ch}.' in txt for ch in ['2', '3', '4', '5', '6']):
        count_captions_table += 1
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        for r in p.runs:
            enforce_tnr(r, size_pt=11.0, bold=True)

    # C. Figure Captions (starts with 'Gambar ')
    elif txt.startswith('Gambar ') and any(f'Gambar {ch}.' in txt for ch in ['1', '2', '3', '4', '5', '6']):
        count_captions_fig += 1
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(12)
        # Strip trailing dot if present
        if p.text.strip().endswith('.'):
            # check if last run has trailing dot
            last_run = p.runs[-1]
            if last_run.text.strip().endswith('.'):
                last_run.text = last_run.text.rstrip('.')
        for r in p.runs:
            enforce_tnr(r, size_pt=11.0, bold=True)

    # D. Code Program Captions (starts with 'Kode Program ')
    elif txt.startswith('Kode Program '):
        count_captions_code += 1
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        for r in p.runs:
            enforce_tnr(r, size_pt=11.0, bold=True)

    # E. Table Notes / Footnotes (starts with 'Keterangan:')
    elif txt.startswith('Keterangan:') and ('n = 30' in txt.lower() or 'p =' in txt.lower() or 'evaluasi' in txt.lower() or 'simbol' in txt.lower() or 'overhead' in txt.lower() or 'cpu' in txt.lower() or 'bootstrap' in txt.lower() or 'persamaan' in txt.lower()):
        count_notes += 1
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(12)
        for r in p.runs:
            enforce_tnr(r, size_pt=10.0, italic=True)

    # F. Standard Body Paragraphs
    else:
        count_body += 1
        if p.alignment != WD_ALIGN_PARAGRAPH.CENTER:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        for r in p.runs:
            # Check if this run is math or special
            if r.font.name != 'Cambria Math':
                enforce_tnr(r, size_pt=12.0)

print(f"Paragraphs harmonized: {count_headings} headings, {count_captions_table} table captions, {count_captions_fig} figure captions, {count_captions_code} code captions, {count_notes} table notes, {count_body} body paragraphs.")

# ==============================================================================
# STEP 3: HARMONIZE ALL TABLES AND THEIR CELLS
# ==============================================================================
# Categories of tables:
# 1. Equation tables (1 row, 2 cols, borders none): e.g. Table 1, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 17, 18, 19, 21
# 2. Code tables (1 row, 1 col, Consolas): Table 22, 23, 24, 25
# 3. Data tables: Table 0, 2, 9, 10, 11, 12, 20, 26, 27, 28, 29, 30, 31, 32, 33

for t_idx, t in enumerate(doc.tables):
    rows_cnt = len(t.rows)
    cols_cnt = len(t.columns)
    sample_txt = t.rows[0].cells[0].text.strip()
    
    # Category 2: Code blocks
    if rows_cnt == 1 and cols_cnt == 1:
        cell = t.rows[0].cells[0]
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                enforce_consolas(r, size_pt=9.5)
        continue
        
    # Category 1: Equation tables (1 or 2 rows, 2 cols, where second col is (X.X))
    if cols_cnt == 2 and (rows_cnt <= 2) and any(c.text.strip().startswith('(') and c.text.strip().endswith(')') for c in t.rows[0].cells):
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r in t.rows:
            p_eq = r.cells[0].paragraphs[0]
            p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_eq.paragraph_format.line_spacing = 1.0
            p_eq.paragraph_format.space_before = Pt(3)
            p_eq.paragraph_format.space_after = Pt(3)
            for run in p_eq.runs:
                if run.font.name != 'Cambria Math':
                    enforce_tnr(run, size_pt=11.0)
            p_num = r.cells[1].paragraphs[0]
            p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_num.paragraph_format.line_spacing = 1.0
            p_num.paragraph_format.space_before = Pt(3)
            p_num.paragraph_format.space_after = Pt(3)
            for run in p_num.runs:
                enforce_tnr(run, size_pt=11.0)
        continue

    # Category 3: Data tables
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Determine appropriate font size for table:
    # Large/wide tables (8 columns like Table 27, 28, 29, 30) -> 8.5 pt
    # Moderately wide tables (5-7 cols) -> 8.5 pt to 9.0 pt
    # Narrow tables (3-4 cols) -> 9.0 pt to 9.5 pt
    if cols_cnt >= 7:
        cell_font_size = 8.5
    elif cols_cnt >= 5:
        cell_font_size = 8.5
    else:
        cell_font_size = 9.0

    # Process all rows in data table
    for r_idx, row in enumerate(t.rows):
        is_header = (r_idx == 0)
        for c_idx, cell in enumerate(row.cells):
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                
                # Check if cell has text that should be centered vs left
                cell_txt = cell.text.strip()
                if is_header:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    # Decide alignment: if text looks numeric / code / status / resolution -> center
                    # If descriptive sentence / multiple words -> left or justify
                    if c_idx == 0 and len(cell_txt) <= 5: # e.g. "A1", "B1", "1", "No."
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    elif any(k in cell_txt.lower() for k in ['valid', 'px', '±', '–', '%']) and len(cell_txt) < 25:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    elif re.match(r'^[\d,\.\s\[\]\–\-\+]+$', cell_txt):
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    elif cell_txt in ['1', '2', '4', '8', '12', '16', '30', '90', '120', '360', '810', '0']:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    elif len(cell_txt) > 30:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    else:
                        # Default keep or center
                        if p.alignment != WD_ALIGN_PARAGRAPH.LEFT:
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                for r in p.runs:
                    bold_val = True if is_header else r.font.bold
                    enforce_tnr(r, size_pt=cell_font_size, bold=bold_val)

print("Step 3: All 34 tables and their cells fully harmonized.")

# Save document
doc.save(MASTER_PATH)
print(f"Harmonized document successfully saved to {MASTER_PATH}")
