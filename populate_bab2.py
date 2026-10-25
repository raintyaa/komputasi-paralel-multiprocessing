# -*- coding: utf-8 -*-
"""
Script to populate BAB 2 LANDASAN TEORI in Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx
Strictly follows:
- academic-paper-builder SOP & UNTAN 2022 guidelines
- Open-format tables (Tabel 2.1 & Tabel 2.2)
- Borderless equation tables with right-aligned numbering (Persamaan 2.1 s.d. 2.7)
- Times New Roman, 12 pt body, 1.5 spacing, 1.0 cm first-line indent, justified
- Proper APA 7th citations and PUEBI / EYD V orthography
"""

import sys
import os
import docx
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DOC_PATH = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"

def set_open_table_borders(table):
    """Format table with open-table style (borders on top, header bottom, and table bottom only)."""
    tblPr = table._element.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    
    # Top border 1 pt
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '8')
    top.set(qn('w:space'), '0')
    top.set(qn('w:color'), '000000')
    tblBorders.append(top)
    
    # Bottom border 1 pt
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), '000000')
    tblBorders.append(bottom)
    
    # Left, right, insideH, insideV none
    for side in ['left', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
        
    tblPr.append(tblBorders)
    
    # Header row bottom border 0.75 pt
    for cell in table.rows[0].cells:
        tcPr = cell._element.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        b = OxmlElement('w:bottom')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '6')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), '000000')
        tcBorders.append(b)
        tcPr.append(tcBorders)

def set_borderless_table(table):
    """Format table with no borders (for equations)."""
    tblPr = table._element.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top', 'bottom', 'left', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
    tblPr.append(tblBorders)

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    """Set cell padding in dxa."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_para(doc, runs_spec, style='Normal', space_before=0, space_after=0, 
                line_spacing=1.5, first_line_indent=Cm(1.0), align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Create a formatted paragraph with rich runs."""
    p = doc.add_paragraph(style=style)
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.first_line_indent = first_line_indent
    
    for item in runs_spec:
        if isinstance(item, str):
            text = item
            italic = False
            bold = False
        elif len(item) == 2:
            text, italic = item
            bold = False
        else:
            text, italic, bold = item
            
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.italic = italic
        r.bold = bold
        
    return p

def create_table_title(doc, text):
    """Create table title paragraph."""
    p = doc.add_paragraph(style='Normal')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.first_line_indent = Cm(0)
    
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.bold = True
    return p

def create_equation_row(doc, formula_runs, eq_num_str):
    """Create a 1-row, 2-col borderless table for equations."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_borderless_table(tbl)
    
    # Set widths: col 0 = 12.2 cm, col 1 = 1.8 cm (sum = 14.0 cm)
    tbl.rows[0].cells[0].width = Cm(12.2)
    tbl.rows[0].cells[1].width = Cm(1.8)
    set_cell_margins(tbl.rows[0].cells[0], top=40, bottom=40, left=40, right=40)
    set_cell_margins(tbl.rows[0].cells[1], top=40, bottom=40, left=40, right=40)
    
    # Formula in cell 0
    p0 = tbl.rows[0].cells[0].paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(2)
    p0.paragraph_format.space_after = Pt(2)
    p0.paragraph_format.line_spacing = 1.15
    p0.paragraph_format.first_line_indent = Cm(0)
    for item in formula_runs:
        if isinstance(item, str):
            text, italic, bold = item, False, False
        elif len(item) == 2:
            text, italic = item
            bold = False
        else:
            text, italic, bold = item
        r = p0.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.italic = italic
        r.bold = bold
        
    # Eq number in cell 1
    p1 = tbl.rows[0].cells[1].paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.paragraph_format.space_before = Pt(2)
    p1.paragraph_format.space_after = Pt(2)
    p1.paragraph_format.line_spacing = 1.15
    p1.paragraph_format.first_line_indent = Cm(0)
    r1 = p1.add_run(eq_num_str)
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(12)
    r1.bold = False
    
    return tbl

def create_keterangan_block(doc, items):
    """Create 'Keterangan:' paragraph and numbered parameter explanations."""
    elements = []
    # Header 'Keterangan:'
    p_hdr = doc.add_paragraph(style='Normal')
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_hdr.paragraph_format.space_before = Pt(3)
    p_hdr.paragraph_format.space_after = Pt(2)
    p_hdr.paragraph_format.line_spacing = 1.15
    p_hdr.paragraph_format.first_line_indent = Cm(1.0)
    r = p_hdr.add_run("Keterangan:")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    elements.append(p_hdr)
    
    # Items
    for idx, runs in enumerate(items, 1):
        p_item = doc.add_paragraph(style='Normal')
        p_item.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_item.paragraph_format.space_before = Pt(1)
        p_item.paragraph_format.space_after = Pt(1)
        p_item.paragraph_format.line_spacing = 1.15
        p_item.paragraph_format.left_indent = Cm(1.0)
        p_item.paragraph_format.first_line_indent = Cm(-0.5)
        
        # Number prefix
        rn = p_item.add_run(f"{idx}. ")
        rn.font.name = 'Times New Roman'
        rn.font.size = Pt(11)
        
        for item in runs:
            if isinstance(item, str):
                text, italic, bold = item, False, False
            elif len(item) == 2:
                text, italic = item
                bold = False
            else:
                text, italic, bold = item
            r = p_item.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.italic = italic
            r.bold = bold
        elements.append(p_item)
        
    return elements

def format_cell_text(cell, runs_spec, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=Pt(9.5)):
    """Format cell paragraphs and runs."""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    p.paragraph_format.first_line_indent = Cm(0)
    for item in runs_spec:
        if isinstance(item, str):
            text, italic, r_bold = item, False, bold
        elif len(item) == 2:
            text, italic = item
            r_bold = bold
        else:
            text, italic, r_bold = item
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = font_size
        r.bold = r_bold
        r.italic = italic

def build_table_2_1(doc):
    """Build Table 2.1 Perbandingan Penelitian Terdahulu."""
    headers = [
        "Peneliti & Tahun",
        "Paradigma / Perangkat",
        "Filter yang Diuji",
        "Temuan Utama",
        "Posisi dan Perbedaan Penelitian Ini"
    ]
    widths_cm = [2.4, 2.3, 2.2, 3.8, 3.3]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Chang et al. (2023)", False)],
            [("Akselerasi GPU (NVIDIA CUDA)", False)],
            [("Sobel multi-arah kernel besar (5 × 5, 7 × 7)", False)],
            [("Akselerasi GPU menghasilkan ", False), ("speedup", True), (" 6,7× hingga 13,0× dibanding OpenCV-GPU standar; komputasi konvolusi turunan terbukti menjadi beban komputasi masif pada resolusi tinggi.", False)],
            [("Menguji arsitektur CPU ", False), ("multi-core", True), (" heterogen berbasis Python ", False), ("multiprocessing", True), ("; fokus mengevaluasi ", False), ("overhead", True), (" komunikasi IPC dan batas derau sistem.", False)]
        ),
        (
            [("Vasile et al. (2024)", False)],
            [("CPU ", False), ("Single-Core", True), (" vs ", False), ("Hardware Acceleration", True)],
            [("Konvolusi 2D spasial generik", False)],
            [("Pengolahan citra beresolusi tinggi secara ", False), ("real-time", True), (" menuntut efisiensi penanganan aliran data; arsitektur CPU serial konvensional tidak mampu memenuhi latensi target.", False)],
            [("Menerapkan dekomposisi data spasial pada CPU ", False), ("multi-core", True), (" untuk mengatasi keterbatasan CPU serial tanpa akselerator khusus (FPGA/ASIC).", False)]
        ),
        (
            [("Cremel & Arruda (2026)", False)],
            [("CPU ", False), ("Multi-Core", True), (" (OpenMP C/C++)", False)],
            [("Grayscale", True), (", ", False), ("Gaussian Blur", True), (", ", False), ("Sobel", True)],
            [(("Speedup", True)), (" dan efisiensi meningkat seiring dimensi citra, namun efisiensi menurun tajam pada 8 utas (efisiensi Sobel merosot hingga ~24%).", False)],
            [("Mengevaluasi ", False), ("multiprocessing", True), (" Python dengan ruang memori terpisah dan kendala GIL, dibandingkan model memori bersama OpenMP.", False)]
        ),
        (
            [("Ibrahim et al. (2021)", False)],
            [("CPU ", False), ("Multi-Core", True), (" & GPU", False)],
            [("Gaussian Blur 2D", False)],
            [("Peningkatan resolusi citra memperbesar skalabilitas paralel; ", False), ("overhead", True), (" transfer data mendominasi pada citra kecil hingga menengah.", False)],
            [("Meneliti rentang resolusi 512×512 hingga 4096×4096 px pada CPU hibrida modern serta mengukur ", False), ("overhead", True), (" IPC dan kontrol A/A secara kuantitatif.", False)]
        ),
        (
            [("Gultom & Sarumaha (2025)", False)],
            [("CPU ", False), ("Multi-Core", True), (" (Python CPython)", False)],
            [("Operasi citra ", False), ("CPU-bound", True)],
            [("Multithreading", True), (" Python dibatasi GIL (", False), ("speedup", True), (" hanya ~1,05×), sedangkan ", False), ("multiprocessing", True), (" mencapai ", False), ("speedup", True), (" 3,16–3,55× pada 4 proses.", False)],
            [("Memperluas evaluasi ke ", False), ("P", True), (" = 1, 2, 4, 8 proses pada prosesor hibrida P/E-Core, pencocokan Amdahl, Karp–Flatt, dan verifikasi bit-identik.", False)]
        ),
        (
            [("Penelitian Ini (2026)", True, True)],
            [("CPU ", True), ("Multi-Core", True), (" Hibrida (Python ", True), ("Multiprocessing", True), (")", True)],
            [("Grayscale", True), (", ", True), ("Gaussian Blur 3×3", True), (", ", True), ("Sobel 3×3", True)],
            [("Memetakan ", True), ("speedup", True), (", efisiensi, ", True), ("overhead", True), (" IPC, utilisasi CPU, kecocokan Amdahl, metrik Karp–Flatt, dan integritas bit-identik (Δmax = 0).", True)],
            [("Komparasi komprehensif pengaruh resolusi, jumlah pekerja, dan kompleksitas filter pada prosesor Intel Raptor Lake dengan hierarki 12 MB L3 ", True), ("Smart Cache", True), (".", True)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    # Headers
    for c_idx, h_text in enumerate(headers):
        cell = tbl.rows[0].cells[c_idx]
        cell.width = Cm(widths_cm[c_idx])
        set_cell_margins(cell, top=60, bottom=60, left=60, right=60)
        format_cell_text(cell, [(h_text, False)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.0))
        
    # Data rows
    for r_idx, row_spec in enumerate(rows_data, 1):
        for c_idx, cell_runs in enumerate(row_spec):
            cell = tbl.rows[r_idx].cells[c_idx]
            cell.width = Cm(widths_cm[c_idx])
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.5))
            
    return tbl

def build_table_2_2(doc):
    """Build Table 2.2 Karakteristik Algoritma Filter Spasial yang Diuji."""
    headers = [
        "Nama Filter",
        "Tipe Operasi Spasial",
        "Ukuran Kernel & Radius (k)",
        "Operasi Komputasi per Piksel",
        "Dimensi Kanal Masukan & Luaran",
        "Ketergantungan Baris Batas (Halo)"
    ]
    widths_cm = [2.2, 2.3, 2.0, 2.8, 2.4, 2.3]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Grayscale (ITU-R BT.601)", False)],
            [("Operasi Titik (", False), ("Point Operation", True), (")", False)],
            [("Tanpa kernel (", False), ("k", True), (" = 0)", False)],
            [("3 perkalian, 2 penjumlahan bobot luma (0,299", False), ("R", True), (" + 0,587", False), ("G", True), (" + 0,114", False), ("B", True), (")", False)],
            [("Masukan: ", False), ("H × W × 3", True), (" (uint8)\nLuaran: ", False), ("H × W", True), (" (uint8)", False)],
            [("Tidak memerlukan ", False), ("halo", True), (" (", False), ("k", True), (" = 0)", False)]
        ),
        (
            [("Gaussian Blur 3×3", False)],
            [("Konvolusi Linier Spasial (", False), ("Smoothing", True), (")", False)],
            [("Kernel 3 × 3 (", False), ("k", True), (" = 1)", False)],
            [("27 perkalian, 24 penjumlahan (9 perkalian dan 8 penjumlahan independen per kanal RGB)", False)],
            [("Masukan: ", False), ("H × W × 3", True), (" (uint8)\nLuaran: ", False), ("H × W × 3", True), (" (uint8)", False)],
            [("Memerlukan 1 baris ", False), ("halo", True), (" atas dan bawah (", False), ("k", True), (" = 1)", False)]
        ),
        (
            [("Sobel 3×3", False)],
            [("Diferensiasi Gradien (", False), ("Edge Detection", True), (")", False)],
            [("Dua kernel 3 × 3 (", False), ("Gx", True), (" & ", False), ("Gy", True), (", ", False), ("k", True), (" = 1)", False)],
            [("12 perkalian, 12 penjumlahan, 2 pemangkatan kuadrat, 1 penarikan akar kuadrat, dan pemotongan ", False), ("clipping", True), (" [0, 255]", False)],
            [("Masukan: ", False), ("H × W", True), (" Grayscale (uint8)\nLuaran: ", False), ("H × W", True), (" Peta Tepi (uint8)", False)],
            [("Memerlukan 1 baris ", False), ("halo", True), (" atas dan bawah (", False), ("k", True), (" = 1)", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    # Headers
    for c_idx, h_text in enumerate(headers):
        cell = tbl.rows[0].cells[c_idx]
        cell.width = Cm(widths_cm[c_idx])
        set_cell_margins(cell, top=60, bottom=60, left=60, right=60)
        format_cell_text(cell, [(h_text, False)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.0))
        
    # Data rows
    for r_idx, row_spec in enumerate(rows_data, 1):
        for c_idx, cell_runs in enumerate(row_spec):
            cell = tbl.rows[r_idx].cells[c_idx]
            cell.width = Cm(widths_cm[c_idx])
            set_cell_margins(cell, top=50, bottom=50, left=60, right=60)
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.5))
            
    return tbl

def populate_bab_2():
    print("Loading document...")
    doc = docx.Document(DOC_PATH)
    
    # Fix paragraph 58 in Bab 1 (replace Mean Blur 5x5 with Gaussian Blur 3x3)
    p58 = doc.paragraphs[58]
    if "mean blur" in p58.text.lower():
        print("Fixing paragraph 58 in Bab 1...")
        p58.clear()
        p58.paragraph_format.line_spacing = 1.0
        p58.paragraph_format.space_before = Pt(0)
        p58.paragraph_format.space_after = Pt(0)
        runs_spec_58 = [
            ("Bagaimana pengaruh variasi tingkat kompleksitas algoritma filter citra (", False),
            ("Grayscale", True),
            (", ", False),
            ("Gaussian Blur 3×3", True),
            (", dan ", False),
            ("Sobel 3×3", True),
            (") terhadap beban tambahan (", False),
            ("overhead", True),
            (") paralel dan utilisasi CPU?", False)
        ]
        for text, it in runs_spec_58:
            r = p58.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.italic = it
            
    # Locate headings in Bab 2
    h_map = {}
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if "Perbandingan Terhadap Penelitian Terdahulu" in text:
            h_map["2.1"] = p
        elif "Pengolahan Citra Digital dan Operasi Filter Spasial" in text:
            h_map["2.2"] = p
        elif "Representasi Citra Digital dan Operasi Konvolusi 2D" in text:
            h_map["2.2.1"] = p
        elif "Karakteristik Algoritma Filter Spasial yang Diuji" in text:
            h_map["2.2.2"] = p
        elif "Komputasi Paralel dan Multiprocessing Python" in text:
            h_map["2.3"] = p
        elif "Paradigma Data Parallelism dan Dekomposisi Domain Spasial" in text:
            h_map["2.3.1"] = p
        elif "Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC" in text:
            h_map["2.3.2"] = p
        elif "Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache" in text:
            h_map["2.3.3"] = p
        elif "Metrik Evaluasi Kinerja dan Model Skalabilitas" in text:
            h_map["2.4"] = p
        elif "Metrik Kinerja Dasar: Waktu Eksekusi, Speedup, Efisiensi, dan Overhead Paralel" in text:
            h_map["2.4.1"] = p
        elif "Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik" in text:
            h_map["2.4.2"] = p
            # Fix text to have proper en-dash
            p.text = "Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp–Flatt"
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(12)
                r.bold = True
        elif "Analisis Statistik Pengukuran dan Evaluasi Batas Derau Sistem (Kontrol A/A)" in text:
            h_map["2.4.3"] = p
        elif "METODOLOGI PENELITIAN" in text and p.style.name.startswith("Heading 1"):
            h_map["3.0"] = p
            
    print(f"Found {len(h_map)} target heading markers in Bab 2.")
    assert len(h_map) == 13, f"Expected 13 heading markers, found {len(h_map)}: {list(h_map.keys())}"

    # Helper to insert list of items before target element
    def insert_items_before(target_p, items_list):
        for item in items_list:
            target_p._element.addprevious(item._element)

    # -------------------------------------------------------------
    # SECTION 2.1: Perbandingan Terhadap Penelitian Terdahulu
    # -------------------------------------------------------------
    print("Building Section 2.1 items...")
    sec_2_1_items = []
    
    # Para 1: GPU & Hardware Acceleration
    p2_1_1 = create_para(doc, [
        ("Akselerasi proses komputasi pada visi komputer dan pengolahan citra digital telah menjadi fokus kajian intensif seiring dengan eksponensialnya pertumbuhan resolusi citra modern (Cremel & Arruda, 2026). Dalam menangani beban komputasi konvolusi matriks yang masif, berbagai penelitian terdahulu mengarahkan fokus implementasi pada unit pemrosesan grafis (GPU). Chang et al. (2023) meneliti penerapan operator Sobel multi-arah dengan ukuran kernel besar (5 × 5 dan 7 × 7) dan membuktikan bahwa akselerasi GPU berbasis CUDA mampu menghasilkan rasio percepatan (", False),
        ("speedup", True),
        (") sebesar 6,7 hingga 13,0 kali lipat dibandingkan pustaka OpenCV-GPU standar. Dari perspektif arsitektur perangkat keras, Vasile et al. (2024) menegaskan bahwa sistem visi komputer beresolusi tinggi menuntut penanganan aliran data (", False),
        ("data stream", True),
        (") secara ", False),
        ("real-time", True),
        (", di mana arsitektur CPU serial konvensional memiliki keterbatasan laten dalam memenuhi ambang batas waktu respons akibat ketergantungan memori dan keterbatasan instruksi per siklus.", False)
    ])
    sec_2_1_items.append(p2_1_1)
    
    # Para 2: Multi-core threading OpenMP & Gaussian Blur
    p2_1_2 = create_para(doc, [
        ("Pada ranah prosesor ", False),
        ("multi-core", True),
        (", eksplorasi komputasi paralel umumnya memanfaatkan model ", False),
        ("shared memory", True),
        (" berbasis utas (", False),
        ("threading", True),
        ("). Cremel dan Arruda (2026) mengevaluasi akselerasi filter spasial citra (", False),
        ("Grayscale", True),
        (", ", False),
        ("Gaussian Blur", True),
        (", dan ", False),
        ("Sobel", True),
        (") menggunakan pustaka OpenMP pada bahasa C/C++. Temuan mereka menunjukkan bahwa rasio percepatan dan efisiensi meningkat seiring dengan bertambahnya dimensi matriks citra, namun efisiensi paralel mengalami degradasi tajam saat jumlah utas ditingkatkan hingga 8 utas, di mana efisiensi pada deteksi tepi Sobel merosot hingga mencapai sekitar 24%. Ibrahim et al. (2021) turut memperkuat karakteristik tersebut melalui komparasi konvolusi Gaussian Blur 2D pada CPU ", False),
        ("multi-core", True),
        (" dan GPU, yang menyimpulkan bahwa beban tambahan (", False),
        ("overhead", True),
        (") transfer memori mendominasi waktu total pada matriks berukuran kecil hingga menengah, sehingga keuntungan komputasi paralel baru tercapai secara optimal pada matriks berdimensi besar.", False)
    ])
    sec_2_1_items.append(p2_1_2)
    
    # Para 3: Python GIL & Multiprocessing
    p2_1_3 = create_para(doc, [
        ("Di sisi lain, implementasi komputasi paralel pada bahasa pemrograman Python menghadapi kendala arsitektural yang unik berupa Global Interpreter Lock (GIL) pada rilis resmi CPython (Python Software Foundation, n.d.-a). Gultom dan Sarumaha (2025) membuktikan secara empiris bahwa GIL membatasi eksekusi instruksi Python hanya pada satu utas dalam satu waktu, sehingga paradigma ", False),
        ("multithreading", True),
        (" pada beban kerja intensif komputasi (", False),
        ("CPU-bound", True),
        (") hanya menghasilkan rasio percepatan marjinal sekitar 1,05 kali lipat. Sebaliknya, modul ", False),
        ("multiprocessing", True),
        (" mampu mendistribusikan beban komputasi secara efektif ke banyak inti prosesor fisik melalui alokasi ruang memori (", False),
        ("address space", True),
        (") dan interpreter independen, dengan pencapaian ", False),
        ("speedup", True),
        (" mencapai 3,16 hingga 3,55 kali lipat pada alokasi empat proses pekerja (Gultom & Sarumaha, 2025; Tanenbaum & Bos, 2022).", False)
    ])
    sec_2_1_items.append(p2_1_3)
    
    # Para 4: Research Gap & Posisi Penelitian
    p2_1_4 = create_para(doc, [
        ("Meskipun demikian, kajian pustaka terdahulu memperlihatkan adanya kesenjangan penelitian (", False),
        ("research gap", True),
        (") yang mendasar. Sebagian besar penelitian filter citra paralel pada CPU berbasis prosesor simetris seragam dengan model memori bersama OpenMP (Cremel & Arruda, 2026). Karakteristik skalabilitas modul ", False),
        ("multiprocessing", True),
        (" Python—yang melibatkan beban komunikasi antar-proses (", False),
        ("inter-process communication", True),
        (" / IPC), serialisasi objek matriks (", False),
        ("pickling", True),
        ("), replikasi baris batas (", False),
        ("boundary halo", True),
        ("), serta rekonstruksi citra—belum dievaluasi secara komprehensif pada arsitektur prosesor heterogen modern yang memadukan inti kinerja tinggi (", False),
        ("Performance-Core", True),
        (") dan inti hemat daya (", False),
        ("Efficient-Core", True),
        ("). Selain itu, pengujian terdahulu umumnya mengabaikan fluktuasi derau sistem operasi dan belum mengonfirmasi integritas bit-identik secara deterministik. Pada rancangan penelitian ini, evaluasi dilakukan secara mendalam terhadap tiga variasi filter spasial bertingkat pada rentang resolusi 512 × 512 hingga 4096 × 4096 piksel, memetakan metrik kinerja empiris terhadap batas teoretis Hukum Amdahl dan metrik Karp–Flatt, serta menerapkan pengujian kontrol A/A untuk mengukur ambang batas derau sistem (", False),
        ("system noise floor", True),
        (").", False)
    ])
    sec_2_1_items.append(p2_1_4)
    
    # Tabel 2.1 Title & Table
    t2_1_title = create_table_title(doc, "Tabel 2.1 Perbandingan Penelitian Terdahulu Terkait Akselerasi Pengolahan Citra Digital")
    sec_2_1_items.append(t2_1_title)
    t2_1_tbl = build_table_2_1(doc)
    sec_2_1_items.append(t2_1_tbl)
    
    # Para 5: Synthesis
    p2_1_5 = create_para(doc, [
        ("Berdasarkan sintesis pada Tabel 2.1, posisi penelitian ini adalah melengkapi pemahaman empiris mengenai efektivitas dan batasan skalabilitas komputasi paralel berbasis ", False),
        ("multiprocessing", True),
        (" Python pada prosesor ", False),
        ("multi-core", True),
        (" modern. Analisis difokuskan pada interaksi antara beban komputasi per piksel, beban transmisi data antar-proses, dan karakteristik hierarki memori ", False),
        ("cache", True),
        (" sistem.", False)
    ])
    sec_2_1_items.append(p2_1_5)
    
    # Insert before Heading 2.2
    insert_items_before(h_map["2.2"], sec_2_1_items)

    # -------------------------------------------------------------
    # SECTION 2.2: Bridge Paragraph before 2.2.1
    # -------------------------------------------------------------
    print("Building Section 2.2 Bridge items...")
    sec_2_2_items = []
    p2_2_bridge = create_para(doc, [
        ("Pengolahan citra digital merupakan disiplin rekayasa yang memanipulasi data piksel dalam format matriks diskret untuk berbagai tujuan, seperti perbaikan kualitas visual citra (", False),
        ("image enhancement", True),
        ("), penajaman kontras, penekanan derau (", False),
        ("noise reduction", True),
        ("), maupun ekstraksi fitur penting untuk analisis lebih lanjut (Gonzalez & Woods, 2018). Pada sistem visi komputer, operasi filter spasial memegang peranan krusial sebagai tahap prapemrosesan (", False),
        ("preprocessing", True),
        (") yang menentukan akurasi interpretasi visual tahap lanjut. Bagian ini menguraikan representasi matematis citra dan karakteristik operasi konvolusi spasial yang menjadi objek pengujian dalam penelitian ini.", False)
    ])
    sec_2_2_items.append(p2_2_bridge)
    insert_items_before(h_map["2.2.1"], sec_2_2_items)

    # -------------------------------------------------------------
    # SECTION 2.2.1: Representasi Citra Digital dan Operasi Konvolusi 2D
    # -------------------------------------------------------------
    print("Building Section 2.2.1 items...")
    sec_2_2_1_items = []
    
    p2_2_1_1 = create_para(doc, [
        ("Secara matematis, citra digital monokromatik dimodelkan sebagai fungsi intensitas spasial diskret dua dimensi ", False),
        ("I(x, y)", True),
        (", di mana ", False),
        ("x", True),
        (" dan ", False),
        ("y", True),
        (" merepresentasikan koordinat baris dan kolom spasial, sedangkan ", False),
        ("I(x, y)", True),
        (" menyatakan derajat keabuan (", False),
        ("gray level", True),
        (") piksel pada rentang nilai diskret [0, 255] untuk format 8-bit (Gonzalez & Woods, 2018). Pada citra berwarna berformat RGB (", False),
        ("Red, Green, Blue", True),
        ("), citra direpresentasikan sebagai tensor tiga dimensi berukuran ", False),
        ("H × W × C", True),
        (", dengan ", False),
        ("H", True),
        (" menyatakan tinggi citra (jumlah baris piksel), ", False),
        ("W", True),
        (" menyatakan lebar citra (jumlah kolom piksel), dan ", False),
        ("C = 3", True),
        (" menyatakan tiga kanal warna komponen dasar. Dalam lingkungan pemrograman Python menggunakan pustaka NumPy, matriks citra disimpan dalam memori utama dengan urutan berbasis baris (", False),
        ("row-major order", True),
        (" atau ", False),
        ("C-contiguous layout", True),
        ("). Pada tata letak ini, piksel-piksel yang berada pada baris horizontal yang sama dialokasikan pada alamat memori fisik yang berurutan. Karakteristik ini memaksimalkan lokalitas spasial (", False),
        ("spatial locality", True),
        (") perangkat keras, sehingga ketika CPU membaca suatu piksel, baris ", False),
        ("cache", True),
        (" (", False),
        ("cache line", True),
        (") berukuran 64 bita akan memuat piksel-piksel di sekitarnya secara bersamaan, yang secara signifikan meminimalkan terjadinya kegagalan pemanggilan data (", False),
        ("cache miss", True),
        (") (Pacheco & Malensek, 2022).", False)
    ])
    sec_2_2_1_items.append(p2_2_1_1)
    
    p2_2_1_2 = create_para(doc, [
        ("Operasi filter spasial linier pada citra digital dilakukan melalui operasi konvolusi diskret dua dimensi (atau korelasi silang diskret) dengan menggeser matriks bobot berukuran kecil yang disebut kernel konvolusi di atas matriks citra masukan (Vasile et al., 2024). Untuk matriks kernel ", False),
        ("K", True),
        (" berukuran ganjil (2", False),
        ("k", True),
        (" + 1) × (2", False),
        ("k", True),
        (" + 1) dengan radius spasial ", False),
        ("k", True),
        (", nilai intensitas piksel luaran ", False),
        ("I_filter(x, y)", True),
        (" dihitung melalui penjumlahan terbobot dari nilai piksel masukan pada area ketetanggaannya, sebagaimana dirumuskan pada Persamaan (2.1):", False)
    ])
    sec_2_2_1_items.append(p2_2_1_2)
    
    # Equation 2.1
    eq_2_1 = create_equation_row(doc, [
        ("I_filter(x, y) = ", True),
        ("∑", False),
        ("(i=-k to k) ", False),
        ("∑", False),
        ("(j=-k to k) ", False),
        ("I(x + i, y + j) · K(i, j)", True)
    ], "(2.1)")
    sec_2_2_1_items.append(eq_2_1)
    
    # Keterangan 2.1
    ket_2_1 = create_keterangan_block(doc, [
        [("I_filter(x, y)", True), (" : Nilai intensitas piksel luaran hasil pemfilteran pada koordinat spasial (", False), ("x, y", True), (").", False)],
        [("I(x + i, y + j)", True), (" : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (", False), ("x + i, y + j", True), (").", False)],
        [("K(i, j)", True), (" : Koefisien bobot matriks kernel konvolusi pada posisi relatif (", False), ("i, j", True), (").", False)],
        [("k", True), (" : Radius spasial matriks kernel (pada matriks kernel berukuran 3 × 3, bernilai ", False), ("k", True), (" = 1).", False)],
        [("i, j", True), (" : Indeks koordinat pergeseran spasial kernel secara vertikal dan horizontal.", False)]
    ])
    sec_2_2_1_items.extend(ket_2_1)
    
    # Boundary handling paragraph
    p2_2_1_3 = create_para(doc, [
        ("Ketika pusat matriks kernel berada pada baris atau kolom terluar citra (", False),
        ("x = 0, x = H - 1, y = 0", True),
        (", atau ", False),
        ("y = W - 1", True),
        ("), sebagian elemen kernel berada di luar batas fisik matriks citra. Untuk mengatasi kendala ini, diterapkan penanganan batas tepi citra (", False),
        ("boundary condition handling", True),
        ("). Pada rancangan penelitian ini, penanganan batas tepi menggunakan teknik replikasi tepi (", False),
        ("mode edge", True),
        ("), di mana nilai intensitas piksel terluar diduplikasi ke area imajiner di luar citra. Metode ini mencegah timbulnya artefak gelap di sepanjang tepi bingkai citra sekaligus menjamin determinisme hasil komputasi antara implementasi serial dan paralel. Secara teoritis, bentuk matematis pada Persamaan (2.1) merupakan korelasi silang diskret yang dalam domain pengolahan citra lazim diidentifikasi sebagai konvolusi spasial (Gonzalez & Woods, 2018). Pada matriks kernel simetris seperti Gaussian, hasil korelasi silang identik secara mutlak dengan konvolusi sejati. Sementara itu, pada operator Sobel yang bersifat anti-simetris, korelasi silang hanya membalikkan tanda aljabar gradien tanpa mengubah magnitudo gradien yang dihasilkan.", False)
    ])
    sec_2_2_1_items.append(p2_2_1_3)
    
    insert_items_before(h_map["2.2.2"], sec_2_2_1_items)

    # -------------------------------------------------------------
    # SECTION 2.2.2: Karakteristik Algoritma Filter Spasial yang Diuji
    # -------------------------------------------------------------
    print("Building Section 2.2.2 items...")
    sec_2_2_2_items = []
    
    p2_2_2_1 = create_para(doc, [
        ("Penelitian ini menguji tiga algoritma filter spasial dengan karakteristik beban komputasi bertingkat, yang merepresentasikan variasi intensitas kalkulasi matematis terhadap rasio transfer memori:", False)
    ])
    sec_2_2_2_items.append(p2_2_2_1)
    
    # Grayscale detail
    p2_2_2_gray = create_para(doc, [
        ("1. Konversi Grayscale (ITU-R BT.601): Merupakan operasi per-piksel murni (", False),
        ("point operation", True),
        (") yang mentransformasikan matriks citra RGB tiga kanal menjadi citra derajat keabuan satu kanal. Transformasi ini menghitung intensitas luma (", False),
        ("Y", True),
        (") berdasarkan standar persepsi visual manusia ITU-R BT.601: ", False),
        ("Y(x, y) = 0,299·R(x, y) + 0,587·G(x, y) + 0,114·B(x, y)", True),
        (". Operasi ini tidak memiliki ketergantungan terhadap piksel tetangga sama sekali (", False),
        ("k", True),
        (" = 0), sehingga kompleksitas komputasinya relatif rendah, yaitu hanya 3 perkalian skalar dan 2 penjumlahan per piksel. Tipe data masukan adalah matriks uint8 berdimensi ", False),
        ("H × W × 3", True),
        (", dan luaran berupa matriks uint8 berdimensi ", False),
        ("H × W", True),
        (".", False)
    ])
    sec_2_2_2_items.append(p2_2_2_gray)
    
    # Gaussian detail
    p2_2_2_gauss = create_para(doc, [
        ("2. Penghalusan Citra Gaussian Blur 3×3: Merupakan filter linier penghalus spasial (", False),
        ("low-pass smoothing filter", True),
        (") yang bertujuan mereduksi derau frekuensi tinggi dan menghaluskan variasi intensitas lokal. Kernel Gaussian berukuran 3 × 3 (", False),
        ("k", True),
        (" = 1) mengaproksimasi fungsi sebaran normal dua dimensi secara diskret dengan matriks bobot ", False),
        ("K_Gaussian = [[1, 2, 1], [2, 4, 2], [1, 2, 1]] / 16", True),
        (". Operasi konvolusi dilakukan secara terpisah pada masing-masing kanal warna RGB (", False),
        ("C", True),
        (" = 3). Setiap piksel luaran membutuhkan 9 perkalian bobot dan 8 penjumlahan per kanal, sehingga secara total melibatkan 27 perkalian dan 24 penjumlahan per piksel masukan RGB. Masukan dan luaran filter berdimensi ", False),
        ("H × W × 3", True),
        (" dengan tipe data uint8.", False)
    ])
    sec_2_2_2_items.append(p2_2_2_gauss)
    
    # Sobel detail
    p2_2_2_sobel = create_para(doc, [
        ("3. Deteksi Tepi Sobel 3×3: Merupakan filter diferensial non-linier berbasis operator gradien spasial turunan pertama (", False),
        ("first-order derivative", True),
        (") untuk menonjolkan batas kontur dan tepi objek. Perhitungan dilakukan pada citra representasi grayscale satu kanal menggunakan dua kernel konvolusi ortogonal berukuran 3 × 3 (", False),
        ("k", True),
        (" = 1), yaitu kernel gradien horizontal (", False),
        ("Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]", True),
        (") dan kernel gradien vertikal (", False),
        ("Gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]", True),
        ("). Setelah konvolusi kedua gradien selesai, magnitudo gradien total dihitung melalui formulasi modulus Euclidean: ", False),
        ("G(x, y) = √(Gx(x, y)² + Gy(x, y)²)", True),
        (". Nilai magnitudo kemudian dinormalisasi dan dipotong (", False),
        ("clipped", True),
        (") ke rentang [0, 255] dengan format data uint8 berdimensi ", False),
        ("H × W", True),
        (". Kompleksitas komputasi Sobel meliputi 12 operasi perkalian, 12 penjumlahan, 2 pemangkatan kuadrat, 1 penarikan akar kuadrat, serta operasi pemotongan rentang intensitas pada setiap piksel.", False)
    ])
    sec_2_2_2_items.append(p2_2_2_sobel)
    
    # Tabel 2.2
    t2_2_title = create_table_title(doc, "Tabel 2.2 Karakteristik Algoritma Filter Spasial yang Diuji")
    sec_2_2_2_items.append(t2_2_title)
    t2_2_tbl = build_table_2_2(doc)
    sec_2_2_2_items.append(t2_2_tbl)
    
    # Synthesis
    p2_2_2_post = create_para(doc, [
        ("Hierarki ketiga filter pada Tabel 2.2 memungkinkan evaluasi komparatif yang sistematis: Grayscale merepresentasikan beban komputasi terendah dengan ketergantungan memori tinggi (", False),
        ("memory-bandwidth bound", True),
        ("), Gaussian Blur merepresentasikan beban konvolusi kanal jamak dengan volume transfer data terbesar, sedangkan Sobel merepresentasikan beban kalkulasi matematis terberat (", False),
        ("compute-bound", True),
        (") dengan keterlibatan fungsi non-linier akar kuadrat.", False)
    ])
    sec_2_2_2_items.append(p2_2_2_post)
    
    insert_items_before(h_map["2.3"], sec_2_2_2_items)

    # -------------------------------------------------------------
    # SECTION 2.3: Bridge Paragraph before 2.3.1
    # -------------------------------------------------------------
    print("Building Section 2.3 Bridge items...")
    sec_2_3_items = []
    p2_3_bridge = create_para(doc, [
        ("Komputasi paralel adalah paradigma pemrosesan informasi di mana sejumlah instruksi atau kalkulasi dieksekusi secara simultan pada beberapa unit pemrosesan fisik untuk mempercepat penyelesaian suatu masalah komputasi (Pacheco & Malensek, 2022). Bagian ini membahas arsitektur dekomposisi data spasial, implementasi pada lingkungan eksekusi Python beserta mitigasi kendala arsitekturalnya, serta karakteristik arsitektur perangkat keras prosesor modern yang melandasinya.", False)
    ])
    sec_2_3_items.append(p2_3_bridge)
    insert_items_before(h_map["2.3.1"], sec_2_3_items)

    # -------------------------------------------------------------
    # SECTION 2.3.1: Paradigma Data Parallelism dan Dekomposisi Domain Spasial
    # -------------------------------------------------------------
    print("Building Section 2.3.1 items...")
    sec_2_3_1_items = []
    
    p2_3_1_1 = create_para(doc, [
        ("Dalam taksonomi komputasi paralel, terdapat dua strategi pemecahan masalah utama: ", False),
        ("task parallelism", True),
        (" dan ", False),
        ("data parallelism", True),
        (" (Pacheco & Malensek, 2022). ", False),
        ("Task parallelism", True),
        (" mendistribusikan fungsi atau tugas komputasi yang berbeda ke beberapa prosesor, sedangkan ", False),
        ("data parallelism", True),
        (" mendistribusikan elemen-elemen data berukuran besar ke beberapa unit pemrosesan yang masing-masing menjalankan instruksi komputasi yang serupa. Pengolahan filter citra digital merupakan contoh klasik dari permasalahan ", False),
        ("embarrassingly parallel", True),
        (", di mana setiap piksel atau wilayah spasial citra dapat diproses secara terisolasi tanpa memerlukan pertukaran status perantara antar-unit kerja (Cremel & Arruda, 2026).", False)
    ])
    sec_2_3_1_items.append(p2_3_1_1)
    
    p2_3_1_2 = create_para(doc, [
        ("Dekomposisi domain spasial pada penelitian ini diterapkan melalui strategi partisi baris horizontal (", False),
        ("horizontal row partitioning", True),
        ("). Matriks citra berdimensi tinggi ", False),
        ("H", True),
        (", lebar ", False),
        ("W", True),
        (", dan kanal ", False),
        ("C", True),
        (" dibagi secara merata di sepanjang sumbu vertikal (sumbu baris) ke dalam ", False),
        ("P", True),
        (" blok data terpisah. Setiap proses pekerja menerima sub-matriks berukuran ⌊", False),
        ("H/P", True),
        ("⌋ × ", False),
        ("W × C", True),
        (". Pemilihan partisi berbasis baris horizontal selaras dengan tata letak memori ", False),
        ("row-major", True),
        (" NumPy, di mana setiap blok irisan menempati blok memori yang berurutan secara fisik. Hal ini meminimalkan biaya rekonstruksi data matriks dibandingkan partisi berbasis kolom atau blok dua dimensi (", False),
        ("grid partition", True),
        (").", False)
    ])
    sec_2_3_1_items.append(p2_3_1_2)
    
    p2_3_1_3 = create_para(doc, [
        ("Tantangan utama dekomposisi spasial pada operasi konvolusi adalah ketergantungan data pada perbatasan partisi. Operasi konvolusi dengan kernel beradius ", False),
        ("k", True),
        (" = 1 menuntut ketersediaan piksel tetangga di atas dan di bawah baris terluar blok kerja. Untuk mengatasi hal ini tanpa sinkronisasi interaktif di tengah komputasi, dirancang mekanisme baris batas (", False),
        ("boundary halo", True),
        ("). Sebelum didistribusikan ke proses pekerja, setiap blok baris diperluas dengan menambahkan ", False),
        ("k", True),
        (" baris tetangga dari blok di sebelahnya. Untuk blok perantara, ditambahkan 1 baris ", False),
        ("halo", True),
        (" di sisi atas dan 1 baris ", False),
        ("halo", True),
        (" di sisi bawah. Khusus untuk blok teratas, perluasan hanya dilakukan pada sisi bawah, sedangkan blok terbawah hanya diperluas pada sisi atas. Pada operasi Grayscale yang bersifat titik, nilai ", False),
        ("k", True),
        (" = 0 sehingga tidak ada penambahan baris batas.", False)
    ])
    sec_2_3_1_items.append(p2_3_1_3)
    
    p2_3_1_4 = create_para(doc, [
        ("Mekanisme baris batas ini menjamin keamanan konkurensi data secara mutlak. Seluruh proses pekerja hanya membaca (", False),
        ("read-only", True),
        (") baris batas tersebut selama proses konvolusi lokal tanpa pernah menulis ulang ke memori bersama, sehingga risiko terjadinya kondisi balapan (", False),
        ("race condition", True),
        (") dapat dieliminasi secara inheren. Setelah operasi filter selesai dieksekusi, masing-masing proses pekerja memotong dan membuang (", False),
        ("discard", True),
        (") ", False),
        ("k", True),
        (" baris batas dari hasil keluarannya sebelum mengirimkan blok data akhir kembali ke proses utama (", False),
        ("master process", True),
        ("). Proses utama kemudian menggabungkan kembali seluruh blok secara berurutan menggunakan fungsi ", False),
        ("numpy.vstack", True),
        (", menghasilkan matriks citra utuh yang memiliki dimensi dan koordinat piksel yang presisi.", False)
    ])
    sec_2_3_1_items.append(p2_3_1_4)
    
    insert_items_before(h_map["2.3.2"], sec_2_3_1_items)

    # -------------------------------------------------------------
    # SECTION 2.3.2: Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC
    # -------------------------------------------------------------
    print("Building Section 2.3.2 items...")
    sec_2_3_2_items = []
    
    p2_3_2_1 = create_para(doc, [
        ("CPython, implementasi referensi standar bahasa Python, mengandalkan mekanisme manajemen memori berbasis pencacah referensi (", False),
        ("reference counting", True),
        ("). Untuk mencegah bahaya korupsi memori internal dan konflik alokasi objek saat beberapa utas berjalan serentak, CPython mengimplementasikan Global Interpreter Lock (GIL) (Python Software Foundation, n.d.-a; Tanenbaum & Bos, 2022). GIL adalah mekanisme kunci biner (", False),
        ("mutex", True),
        (") yang mewajibkan bahwa hanya satu utas yang diizinkan mengeksekusi ", False),
        ("bytecode", True),
        (" Python pada satu waktu, terlepas dari jumlah inti prosesor fisik yang tersedia pada perangkat keras. Konsekuensinya, pustaka ", False),
        ("threading", True),
        (" standar Python tidak mampu meningkatkan kinerja pada beban komputasi intensif (", False),
        ("CPU-bound", True),
        ("), sebagaimana dibuktikan oleh Gultom & Sarumaha (2025) yang mencatat rasio percepatan hanya 1,05 kali lipat.", False)
    ])
    sec_2_3_2_items.append(p2_3_2_1)
    
    p2_3_2_2 = create_para(doc, [
        ("Modul bawaan ", False),
        ("multiprocessing", True),
        (" pada Python dirancang khusus untuk mengatasi keterbatasan GIL dengan mengalihkan paradigma pemrograman dari tingkat utas (", False),
        ("multithreading", True),
        (") ke tingkat proses sistem operasi (", False),
        ("multiprocessing", True),
        (") (Python Software Foundation, n.d.-b). Alih-alih mengeksekusi beberapa utas di dalam satu interpreter, modul ", False),
        ("multiprocessing", True),
        (" menciptakan beberapa proses sistem operasi independen. Setiap proses pekerja memiliki ruang alamat memori virtual (", False),
        ("virtual address space", True),
        (") terisolasi, pencacah referensi privat, dan instansiasi interpreter CPython mandiri (Tanenbaum & Bos, 2022). Dengan arsitektur ini, setiap inti prosesor fisik dapat mengeksekusi proses pekerjanya masing-masing secara serentak tanpa saling terhalang oleh kunci interpreter, mewujudkan komputasi paralel sejati (", False),
        ("true parallelism", True),
        (").", False)
    ])
    sec_2_3_2_items.append(p2_3_2_2)
    
    p2_3_2_3 = create_para(doc, [
        ("Isolasi ruang alamat memori pada arsitektur proses terpisah membawa konsekuensi teknis berupa perlunya mekanisme komunikasi antar-proses (", False),
        ("inter-process communication", True),
        (" / IPC) untuk mendistribusikan data masukan dan menghimpun hasil luaran. Proses utama dan pekerja berkomunikasi melalui saluran pipa sistem operasi (", False),
        ("OS pipes", True),
        ("). Karena memori tidak dapat diakses secara langsung oleh proses lain, objek matriks NumPy harus diubah menjadi representasi aliran bita terurut (", False),
        ("byte streams", True),
        (") melalui proses serialisasi (", False),
        ("pickling", True),
        (") menggunakan protokol modul ", False),
        ("pickle", True),
        (", lalu dikirimkan melalui pipa IPC, dan direkonstruksi kembali melalui deserialisasi (", False),
        ("unpickling", True),
        (") di proses pekerja (Python Software Foundation, n.d.-b). Pada matriks citra beresolusi tinggi, volume data yang diserialisasi sangat masif (sebagai contoh, citra 4096 × 4096 piksel RGB memerlukan transfer data mentah sekitar 48 MB per arah transmisi). Durasi yang dihabiskan untuk serialisasi, transmisi pipa IPC, dan deserialisasi ini menjadi komponen utama dari beban tambahan paralel (", False),
        ("parallel overhead", True),
        ("), yang mengurangi efisiensi komputasi pada sistem paralel berbasis proses.", False)
    ])
    sec_2_3_2_items.append(p2_3_2_3)
    
    p2_3_2_4 = create_para(doc, [
        ("Aspek kritis lain dalam ekosistem Python adalah model inisialisasi proses pekerja pada sistem operasi Windows. Berbeda dengan sistem operasi berbasis POSIX (seperti Linux atau macOS) yang menyediakan panggilan sistem ", False),
        ("fork", True),
        (" untuk menyalin ruang memori proses induk secara efisien (", False),
        ("copy-on-write", True),
        ("), sistem operasi Windows hanya mendukung metode inisialisasi ", False),
        ("spawn", True),
        (" (Python Software Foundation, n.d.-b). Pada metode ", False),
        ("spawn", True),
        (", sistem operasi meluncurkan proses baru secara utuh dengan memuat ulang interpreter Python dari penyimpanan sekunder, mengalokasikan struktur proses baru, dan mengeksekusi ulang modul kode sumber dari awal. Mekanisme ini mewajibkan penyusunan skrip menggunakan blok proteksi ", False),
        ("if __name__ == '__main__':", True),
        (" guna mencegah rekursi pembuatan proses tak berhingga. Metode ", False),
        ("spawn", True),
        (" menimbulkan latensi inisialisasi yang cukup besar, berkisar antara 0,1 hingga 0,5 detik per proses. Untuk mencegah distorsi pengukuran waktu akibat latensi inisialisasi tersebut, penelitian ini menerapkan strategi ", False),
        ("pre-warmed worker pool", True),
        (" (", False),
        ("multiprocessing.Pool", True),
        ("), di mana kolam proses pekerja diinisialisasi dan distabilkan terlebih dahulu sebelum pengukuran waktu benchmarking dimulai.", False)
    ])
    sec_2_3_2_items.append(p2_3_2_4)
    
    insert_items_before(h_map["2.3.3"], sec_2_3_2_items)

    # -------------------------------------------------------------
    # SECTION 2.3.3: Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache
    # -------------------------------------------------------------
    print("Building Section 2.3.3 items...")
    sec_2_3_3_items = []
    
    p2_3_3_1 = create_para(doc, [
        ("Evolusi arsitektur mikroprosesor modern telah bergeser dari peningkatan frekuensi kerja tunggal (", False),
        ("clock scaling", True),
        (") menuju integrasi banyak inti pemrosesan fisik (", False),
        ("multi-core architecture", True),
        (") dalam satu keping silikon (Pacheco & Malensek, 2022). Inti fisik merepresentasikan unit eksekusi lengkap yang memiliki unit logika aritmatika (", False),
        ("arithmetic logic unit", True),
        (" / ALU), unit vektor SIMD, dan unit kendali instruksi tersendiri. Di atas inti fisik, prosesor modern sering mengimplementasikan teknologi ", False),
        ("Simultaneous Multithreading", True),
        (" (SMT atau Intel Hyper-Threading), yang menduplikasi register arsitektural untuk menyajikan dua prosesor logis per inti fisik. SMT meningkatkan ", False),
        ("throughput", True),
        (" pemrosesan saat terjadi penundaan memori (", False),
        ("memory stall", True),
        ("), namun pada komputasi intensif berbasis pemrosesan larik numerik penuh, penambahan beban melampaui jumlah inti fisik tidak memberikan percepatan linier karena unit kalkulasi fisik tetap dibagi bersama.", False)
    ])
    sec_2_3_3_items.append(p2_3_3_1)
    
    p2_3_3_2 = create_para(doc, [
        ("Perangkat keras uji yang digunakan dalam penelitian ini mengusung arsitektur heterogen hibrida kontemporer, yaitu prosesor Intel Core i5-13420H generasi ke-13 (nama sandi ", False),
        ("Raptor Lake", True),
        ("). Arsitektur hibrida ini mengombinasikan dua jenis mikroarsitektur inti prosesor yang memiliki karakteristik daya dan kinerja asimetris:\n", False),
        ("1. Performance-Cores (P-Cores, arsitektur Raptor Cove): Berjumlah 4 inti fisik yang dirancang khusus untuk beban kerja komputasi berat dengan latensi rendah. P-Core memiliki pipa instruksi lebar, kapasitas prediksi percabangan mendalam, frekuensi kerja dasar 2,1 GHz dengan dorongan turbo hingga 4,6 GHz, serta mendukung SMT (menghasilkan 8 utas logis).\n", False),
        ("2. Efficient-Cores (E-Cores, arsitektur Gracemont): Berjumlah 4 inti fisik yang dirancang dengan tapak silikon kompak dan konsumsi daya sangat rendah untuk menangani komputasi latar belakang dan pemrosesan multi-utas throughput tinggi. E-Core beroperasi pada frekuensi dasar 1,5 GHz dengan turbo hingga 3,4 GHz, dan tidak mendukung SMT (4 utas logis).\n", False),
        ("Secara keseluruhan, prosesor menyediakan 8 inti fisik dan 12 utas logis. Penjadwalan proses sepenuhnya dikendalikan oleh sistem operasi Windows 11 melalui kolaborasi dengan mikrokontroler perangkat keras Intel Thread Director.", False)
    ])
    sec_2_3_3_items.append(p2_3_3_2)
    
    p2_3_3_3 = create_para(doc, [
        ("Hierarki subsistem memori prosesor memainkan peran yang sangat menentukan dalam kinerja algoritma pengolahan citra. Prosesor Intel Core i5-13420H memiliki struktur hierarki ", False),
        ("cache", True),
        (" tiga tingkat:\n", False),
        ("1. Cache Level 1 (L1): Terdiri atas 80 KB per P-Core (48 KB L1-Data + 32 KB L1-Instruction) dan 96 KB per E-Core (32 KB L1-D + 64 KB L1-I), dengan latensi akses sekitar 1 nanodetik (ns).\n", False),
        ("2. Cache Level 2 (L2): Bersifat privat berkapasitas 1,25 MB per P-Core dan 2 MB terbagi (", False),
        ("shared", True),
        (") per kluster empat E-Core, dengan latensi akses sekitar 3–4 ns.\n", False),
        ("3. Cache Level 3 (L3 / Intel Smart Cache): Berkapasitas total 12 MB yang terbagi secara merata (", False),
        ("shared cache", True),
        (") untuk seluruh inti prosesor (baik P-Core maupun E-Core) dengan latensi sekitar 10–12 ns.\n", False),
        ("Di luar L3 cache, data harus diambil dari memori utama (DDR5 SDRAM pada kecepatan transfer 5200 MT/s) yang memiliki latensi jauh lebih tinggi, yaitu sekitar 60 hingga 80 ns.", False)
    ])
    sec_2_3_3_items.append(p2_3_3_3)
    
    p2_3_3_4 = create_para(doc, [
        ("Interaksi antara dimensi matriks citra dan kapasitas 12 MB L3 Smart Cache menjadi faktor penjelas fundamental terhadap perilaku percepatan paralel. Pada citra masukan berdimensi kecil, seperti 512 × 512 piksel berformat RGB (ukuran matriks mentah sekitar 768 KB), seluruh data citra beserta sub-matriks hasil partisi untuk seluruh proses pekerja dapat ditampung secara penuh di dalam 12 MB L3 Smart Cache. Kondisi ini menghasilkan tingkat keberhasilan temu data memori (", False),
        ("cache hit rate", True),
        (") yang sangat tinggi, mengurangi latensi akses secara drastis, dan memungkinkan pencapaian rasio percepatan yang sangat tinggi (bahkan mendekati atau melampaui batas linier pada komputasi intensif). Sebaliknya, pada citra berdimensi ultra-tinggi 4096 × 4096 piksel (ukuran matriks mentah sekitar 48 MB data RGB tak terkompresi), ukuran data melampaui kapasitas 12 MB L3 cache hingga empat kali lipat. Akibatnya, terjadi penggantian baris cache yang masif dan terus-menerus (", False),
        ("cache thrashing", True),
        ("), memaksa prosesor untuk mengambil data secara berulang dari RAM DDR5 melalui bus memori sistem. Perebutan lebar pita (", False),
        ("memory bandwidth contention", True),
        (") antar-inti prosesor pada citra berukuran masif ini menjadi pembatas utama skalabilitas komputasi paralel.", False)
    ])
    sec_2_3_3_items.append(p2_3_3_4)
    
    insert_items_before(h_map["2.4"], sec_2_3_3_items)

    # -------------------------------------------------------------
    # SECTION 2.4: Bridge Paragraph before 2.4.1
    # -------------------------------------------------------------
    print("Building Section 2.4 Bridge items...")
    sec_2_4_items = []
    p2_4_bridge = create_para(doc, [
        ("Untuk mengukur dan menganalisis efektivitas komputasi paralel secara objektif, diperlukan parameter kuantitatif yang terstandarisasi. Bagian ini merumuskan metrik kinerja empiris dasar, batas skalabilitas teoretis berdasarkan Hukum Amdahl dan metrik Karp–Flatt, serta kerangka analisis statistik dan metodologi evaluasi batas derau sistem (kontrol A/A) yang diterapkan dalam penelitian ini.", False)
    ])
    sec_2_4_items.append(p2_4_bridge)
    insert_items_before(h_map["2.4.1"], sec_2_4_items)

    # -------------------------------------------------------------
    # SECTION 2.4.1: Metrik Kinerja Dasar
    # -------------------------------------------------------------
    print("Building Section 2.4.1 items...")
    sec_2_4_1_items = []
    
    # Para 1: Waktu eksekusi
    p2_4_1_1 = create_para(doc, [
        ("Evaluasi kinerja komputasi bertumpu pada perbandingan durasi waktu eksekusi program. Waktu eksekusi diukur dalam satuan detik menggunakan fungsi pewaktu berpresisi tinggi berbasis monotonik ", False),
        ("time.perf_counter()", True),
        (" pada bahasa Python. Waktu eksekusi serial (", False),
        ("T_serial", True),
        (" atau ", False),
        ("Ts", True),
        (") merepresentasikan durasi pemrosesan citra pada skrip serial murni satu inti prosesor tanpa inisialisasi kolam pekerja. Sementara itu, waktu eksekusi paralel (", False),
        ("T_paralel", True),
        (" atau ", False),
        ("Tp", True),
        (") mencakup seluruh rentang waktu mulai dari pencatatan stempel waktu awal sebelum partisi matriks citra, pemotongan blok dan baris batas, transmisi data melalui pipa IPC, eksekusi filter serentak oleh kolam proses pekerja, pembuangan baris batas, transmisi balik, hingga rekonstruksi citra utuh selesai dilakukan melalui penggabungan vertikal.", False)
    ])
    sec_2_4_1_items.append(p2_4_1_1)
    
    # Para 2: Speedup
    p2_4_1_2 = create_para(doc, [
        ("Rasio percepatan (", False),
        ("speedup", True),
        (") mengukur seberapa banyak komputasi paralel mampu mempersingkat durasi pemrosesan dibandingkan eksekusi serial pada beban kerja yang identik (Pacheco & Malensek, 2022). Rasio percepatan (", False),
        ("S", True),
        (") dirumuskan pada Persamaan (2.2):", False)
    ])
    sec_2_4_1_items.append(p2_4_1_2)
    
    eq_2_2 = create_equation_row(doc, [
        ("S = T_serial / T_paralel", True)
    ], "(2.2)")
    sec_2_4_1_items.append(eq_2_2)
    
    ket_2_2 = create_keterangan_block(doc, [
        [("S", True), (" : Nilai rasio percepatan (", False), ("speedup", True), (") komputasi (rasio nirdimensi).", False)],
        [("T_serial", True), (" : Waktu eksekusi pemrosesan citra pada skrip serial murni satu inti prosesor tanpa inisialisasi kolam proses (detik).", False)],
        [("T_paralel", True), (" : Waktu eksekusi pemrosesan citra secara paralel pada alokasi ", False), ("P", True), (" proses pekerja (detik).", False)]
    ])
    sec_2_4_1_items.extend(ket_2_2)
    
    # Para 3: Efficiency
    p2_4_1_3 = create_para(doc, [
        ("Efisiensi paralel (", False),
        ("parallel efficiency", True),
        (") mengukur fraksi pemanfaatan daya komputasi dari setiap unit proses pekerja yang dialokasikan (Pacheco & Malensek, 2022). Pada kondisi ideal tanpa hambatan komunikasi, penambahan ", False),
        ("P", True),
        (" prosesor akan menghasilkan percepatan sebesar ", False),
        ("P", True),
        (" kali lipat dengan efisiensi 100%. Namun pada sistem riil, efisiensi selalu terdegradasi seiring peningkatan ", False),
        ("P", True),
        (". Efisiensi paralel (", False),
        ("E", True),
        (") dinyatakan dalam persentase sebagaimana dirumuskan pada Persamaan (2.3):", False)
    ])
    sec_2_4_1_items.append(p2_4_1_3)
    
    eq_2_3 = create_equation_row(doc, [
        ("E = (S / P) × 100% = (T_serial / (P · T_paralel)) × 100%", True)
    ], "(2.3)")
    sec_2_4_1_items.append(eq_2_3)
    
    ket_2_3 = create_keterangan_block(doc, [
        [("E", True), (" : Persentase efisiensi komputasi paralel (%).", False)],
        [("S", True), (" : Nilai rasio percepatan (", False), ("speedup", True), (") yang diperoleh dari Persamaan (2.2).", False)],
        [("P", True), (" : Jumlah proses pekerja (", False), ("worker processes", True), (") yang dialokasikan dalam eksekusi paralel.", False)]
    ])
    sec_2_4_1_items.extend(ket_2_3)
    
    # Para 4: Parallel Overhead
    p2_4_1_4 = create_para(doc, [
        ("Beban tambahan paralel (", False),
        ("parallel overhead", True),
        (") merepresentasikan penalti durasi waktu tambahan yang timbul akibat koordinasi sistem paralel di luar waktu komputasi pemrosesan citra murni (Pacheco & Malensek, 2022). Beban ini dihitung dari selisih antara waktu eksekusi paralel aktual (", False),
        ("T_paralel", True),
        (") dengan waktu eksekusi paralel ideal teoretis (", False),
        ("T_serial / P", True),
        ("), sebagaimana dirumuskan pada Persamaan (2.4):", False)
    ])
    sec_2_4_1_items.append(p2_4_1_4)
    
    eq_2_4 = create_equation_row(doc, [
        ("T_overhead = T_paralel - (T_serial / P)", True)
    ], "(2.4)")
    sec_2_4_1_items.append(eq_2_4)
    
    ket_2_4 = create_keterangan_block(doc, [
        [("T_overhead", True), (" : Durasi beban tambahan sistem paralel akibat komunikasi antar-proses (IPC), serialisasi matriks (", False), ("pickling", True), ("), replikasi baris batas (", False), ("halo", True), ("), dan rekonstruksi matriks citra (detik).", False)],
        [("T_paralel", True), (" : Waktu eksekusi paralel aktual yang terukur (detik).", False)],
        [("T_serial / P", True), (" : Waktu eksekusi paralel ideal secara teoretis tanpa beban koordinasi sistem (detik).", False)],
        [("T_serial", True), (" : Waktu eksekusi serial ", False), ("baseline", True), (" (detik).", False)],
        [("P", True), (" : Jumlah proses pekerja yang dialokasikan.", False)]
    ])
    sec_2_4_1_items.extend(ket_2_4)
    
    insert_items_before(h_map["2.4.2"], sec_2_4_1_items)

    # -------------------------------------------------------------
    # SECTION 2.4.2: Batas Skalabilitas Teoretis: Amdahl & Karp-Flatt
    # -------------------------------------------------------------
    print("Building Section 2.4.2 items...")
    sec_2_4_2_items = []
    
    # Amdahl Law
    p2_4_2_1 = create_para(doc, [
        ("Batas percepatan maksimum suatu sistem komputasi paralel secara klasik dimodelkan oleh Hukum Amdahl (Amdahl, 1967). Hukum Amdahl menyatakan bahwa rasio percepatan program paralel dibatasi secara fundamental oleh proporsi instruksi kode yang bersifat serial dan tidak dapat dibagi ke banyak prosesor (Pacheco & Malensek, 2022). Apabila suatu program memiliki fraksi beban kerja paralel sebesar ", False),
        ("f", True),
        (" (di mana 0 ≤ ", False),
        ("f", True),
        (" ≤ 1), maka batas rasio percepatan teoretis pada alokasi ", False),
        ("P", True),
        (" proses pekerja dirumuskan pada Persamaan (2.5):", False)
    ])
    sec_2_4_2_items.append(p2_4_2_1)
    
    eq_2_5 = create_equation_row(doc, [
        ("S_Amdahl = 1 / ((1 - f) + (f / P))", True)
    ], "(2.5)")
    sec_2_4_2_items.append(eq_2_5)
    
    ket_2_5 = create_keterangan_block(doc, [
        [("S_Amdahl", True), (" : Percepatan teoretis pada alokasi ", False), ("P", True), (" proses pekerja menurut model Amdahl.", False)],
        [("f", True), (" : Fraksi beban komputasi yang dapat diparalelkan secara sempurna (0 ≤ ", False), ("f", True), (" ≤ 1).", False)],
        [("(1 - f)", True), (" : Fraksi serial efektif yang tidak mengalami percepatan, mencakup bagian kode sekuensial program, beban koordinasi paralel (partisi, transmisi pipa IPC, baris batas, rekonstruksi), dan pengaruh disparitas arsitektur inti prosesor yang tidak setara (P-Core dan E-Core).", False)],
        [("P", True), (" : Jumlah proses pekerja yang dialokasikan.", False)]
    ])
    sec_2_4_2_items.extend(ket_2_5)
    
    p2_4_2_2 = create_para(doc, [
        ("Ketika jumlah prosesor ditingkatkan mendekati tak hingga (", False),
        ("P → ∞", True),
        ("), suku ", False),
        ("f / P", True),
        (" mendekati nol, sehingga batas percepatan asimtotik maksimum program dibatasi oleh 1 / (1 - ", False),
        ("f", True),
        ("). Hukum Amdahl klasik mengasumsikan bahwa seluruh prosesor bersifat homogen dan tidak memperhitungkan pembengkakan biaya koordinasi yang tumbuh seiring pertambahan prosesor. Dalam konteks sistem riil penelitian ini pada prosesor hibrida Intel Raptor Lake, fraksi serial (1 - ", False),
        ("f", True),
        (") diperlakukan sebagai fraksi serial efektif (", False),
        ("effective serial fraction", True),
        ("), yang menyerap seluruh penalti non-ideal sistem, termasuk transmisi IPC, serialisasi ", False),
        ("pickle", True),
        (", rekonstruksi ", False),
        ("vstack", True),
        (", serta asimetri kemampuan komputasi antara P-Core dan E-Core. Parameter fraksi paralel ", False),
        ("f", True),
        (" diestimasi per algoritma filter melalui regresi non-linier kuadrat terkecil (", False),
        ("non-linear least squares", True),
        (") terhadap data empiris Skenario B untuk ", False),
        ("P ∈ {2, 4, 8}", True),
        (" disertai estimasi selang kepercayaan 95% berbasis ", False),
        ("bootstrap", True),
        (".", False)
    ])
    sec_2_4_2_items.append(p2_4_2_2)
    
    # Karp-Flatt
    p2_4_2_3 = create_para(doc, [
        ("Untuk memeriksa apakah hambatan skalabilitas yang terjadi berakar dari keterbatasan inheren algoritma ataukah didominasi oleh inefisiensi arsitektur komunikasi sistem, diterapkan metrik Karp–Flatt (Karp & Flatt, 1990). Metrik Karp–Flatt mendefinisikan fraksi serial eksperimental (", False),
        ("e", True),
        (") secara independen dari estimasi parameter Amdahl, sebagaimana dirumuskan pada Persamaan (2.6):", False)
    ])
    sec_2_4_2_items.append(p2_4_2_3)
    
    eq_2_6 = create_equation_row(doc, [
        ("e = ((1 / S) - (1 / P)) / (1 - (1 / P))", True)
    ], "(2.6)")
    sec_2_4_2_items.append(eq_2_6)
    
    ket_2_6 = create_keterangan_block(doc, [
        [("e", True), (" : Fraksi serial eksperimental (", False), ("experimentally determined serial fraction", True), (").", False)],
        [("S", True), (" : Rasio percepatan empiris yang terukur pada alokasi ", False), ("P", True), (" proses pekerja.", False)],
        [("P", True), (" : Jumlah proses pekerja yang dialokasikan (", False), ("P", True), (" > 1).", False)]
    ])
    sec_2_4_2_items.extend(ket_2_6)
    
    p2_4_2_4 = create_para(doc, [
        ("Metrik Karp–Flatt memberikan alat diagnostik yang sangat kuat untuk mengidentifikasi perilaku sistem paralel:\n", False),
        ("1. Jika nilai fraksi serial eksperimental ", False),
        ("e", True),
        (" bernilai konstan seiring dengan penambahan alokasi proses pekerja ", False),
        ("P", True),
        (", maka keterbatasan skalabilitas program murni disebabkan oleh keberadaan bagian kode serial sekuensial yang konstan, sehingga sistem mematuhi asumsi model klasik Amdahl.\n", False),
        ("2. Jika nilai fraksi serial eksperimental ", False),
        ("e", True),
        (" meningkat secara monoton seiring penambahan ", False),
        ("P", True),
        (", hal tersebut membuktikan secara diagnostik bahwa pembatas utama skalabilitas bukanlah kode serial murni, melainkan diakibatkan oleh pembengkakan beban koordinasi paralel, latensi transmisi pipa IPC, biaya serialisasi matriks, atau saturasi lebar pita memori yang tumbuh sebanding dengan penambahan proses kerja.", False)
    ])
    sec_2_4_2_items.append(p2_4_2_4)
    
    insert_items_before(h_map["2.4.3"], sec_2_4_2_items)

    # -------------------------------------------------------------
    # SECTION 2.4.3: Analisis Statistik & Kontrol A/A
    # -------------------------------------------------------------
    print("Building Section 2.4.3 items...")
    sec_2_4_3_items = []
    
    p2_4_3_1 = create_para(doc, [
        ("Akurasi pengukuran kinerja pada sistem komputer modern sangat rentan terdistorsi oleh fluktuasi derau perangkat keras dan perangkat lunak, seperti fluktuasi suhu prosesor (", False),
        ("thermal throttling", True),
        (") serta interupsi aktivitas latar belakang sistem operasi (layanan sistem Windows, pembaruan otomatis, dan manajemen memori OS). Untuk mengisolasi faktor pengganggu tersebut, seluruh pengujian dalam penelitian ini dieksekusi melalui protokol 30 kali repetisi pengujian terkontrol yang dijalankan secara berselang-seling (", False),
        ("interleaved execution", True),
        (") antara skrip serial dan skrip paralel pada setiap tingkatan perlakuan. Dengan metode berselang-seling ini, setiap pasangan data serial dan paralel mengalami kondisi termal dan beban sistem latar belakang yang setara.", False)
    ])
    sec_2_4_3_items.append(p2_4_3_1)
    
    p2_4_3_2 = create_para(doc, [
        ("Data durasi waktu eksekusi pada sistem komputer riil memiliki karakteristik distribusi yang asimetris dengan kecenderungan menjulur ke kanan (", False),
        ("right-skewed distribution", True),
        ("), akibat munculnya beberapa nilai pencilan (", False),
        ("outliers", True),
        (") yang dipicu oleh lonjakan aktivitas proses latar belakang sistem operasi. Mengingat asumsi normalitas tidak selalu terpenuhi, analisis pemusatan data mengutamakan statistik non-parametrik yang tangguh terhadap pencilan (", False),
        ("robust statistics", True),
        ("), yaitu nilai median dan rentang antarkuartil (IQR, [", False),
        ("Q25 - Q75", True),
        ("]). Nilai rerata sampel (", False),
        ("x̄", True),
        (") dan simpangan baku sampel (", False),
        ("s", True),
        (") tetap dilaporkan sebagai parameter pelengkap.", False)
    ])
    sec_2_4_3_items.append(p2_4_3_2)
    
    # Equation 2.7 CI 95%
    p2_4_3_3 = create_para(doc, [
        ("Untuk memberikan estimasi kepastian statistik pada nilai rerata parameter kinerja, dihitung selang kepercayaan 95% (", False),
        ("confidence interval", True),
        (") menggunakan distribusi ", False),
        ("t", True),
        ("-Student untuk ukuran sampel ", False),
        ("n = 30", True),
        (", sebagaimana dirumuskan pada Persamaan (2.7):", False)
    ])
    sec_2_4_3_items.append(p2_4_3_3)
    
    eq_2_7 = create_equation_row(doc, [
        ("CI_95% = x̄ ± t_(n-1, α/2) · (s / √n)", True)
    ], "(2.7)")
    sec_2_4_3_items.append(eq_2_7)
    
    ket_2_7 = create_keterangan_block(doc, [
        [("CI_95%", True), (" : Selang kepercayaan 95% (", False), ("confidence interval", True), (") untuk nilai rerata parameter kinerja.", False)],
        [("x̄", True), (" : Rerata sampel dari ", False), ("n", True), (" = 30 repetisi pengujian.", False)],
        [("s", True), (" : Simpangan baku sampel.", False)],
        [("n", True), (" : Ukuran sampel pengujian (", False), ("n", True), (" = 30).", False)],
        [("t_(n-1, α/2)", True), (" : Nilai kritis distribusi ", False), ("t", True), ("-Student pada derajat kebebasan ", False), ("df = n - 1 = 29", True), (" dan tingkat signifikansi ", False), ("α = 0,05", True), (", bernilai ", False), ("t_(29, 0,025) = 2,04523", True), (".", False)]
    ])
    sec_2_4_3_items.extend(ket_2_7)
    
    p2_4_3_4 = create_para(doc, [
        ("Pengujian signifikansi perbedaan performa antar-perlakuan dievaluasi melalui uji hipotesis non-parametrik dengan taraf signifikansi ", False),
        ("α = 0,05", True),
        (". Uji Mann–Whitney ", False),
        ("U", True),
        (" digunakan untuk membandingkan signifikansi perbedaan antara dua kelompok independen, sedangkan uji Kruskal–Wallis digunakan untuk menguji variasi kinerja antar-alokasi proses pekerja (", False),
        ("P = 1, 2, 4, 8", True),
        ("). Suatu perbedaan perlakuan dinyatakan signifikan secara statistik apabila nilai signifikansi terhitung lebih kecil dari ambang batas (", False),
        ("p < 0,05", True),
        (").", False)
    ])
    sec_2_4_3_items.append(p2_4_3_4)
    
    p2_4_3_5 = create_para(doc, [
        ("Sebagai instrumen kendali mutu pengukuran, penelitian ini menyertakan rancangan pengujian kontrol A/A dengan alokasi satu proses pekerja (", False),
        ("P = 1", True),
        ("). Pada perlakuan kontrol A/A, skrip arsitektur paralel dieksekusi dengan satu pekerja (", False),
        ("T_paralel, P=1", True),
        (") lalu dikomparasikan secara langsung terhadap skrip serial murni (", False),
        ("T_serial", True),
        ("). Karena pada ", False),
        ("P = 1", True),
        (" tidak terjadi pembagian beban komputasi ke beberapa inti fisik prosesor, secara teoretis rasio percepatan yang dihasilkan harus bernilai mendekati satu (", False),
        ("S ≈ 1,00", True),
        ("). Nilai selisih ", False),
        ("T_overhead, P=1 = T_paralel, P=1 - T_serial", True),
        (" secara presisi merepresentasikan batas derau sistem (", False),
        ("system noise floor", True),
        (") dan biaya struktural inheren dari modul ", False),
        ("multiprocessing", True),
        (" Python (mekanisme transmisi pipa IPC dan serialisasi data matriks) tanpa campur tangan akselerasi perangkat keras. Metodologi kontrol A/A ini menjadi fondasi empiris yang memvalidasi bahwa seluruh peningkatan performa pada ", False),
        ("P = 2, 4,", True),
        (" dan 8 benar-benar bersumber dari akselerasi komputasi paralel dan bukan merupakan artefak derau pengukuran.", False)
    ])
    sec_2_4_3_items.append(p2_4_3_5)
    
    # Target insertion before Heading 3.0 (or blank paragraph before it)
    p_before_h3 = h_map["3.0"]
    insert_items_before(p_before_h3, sec_2_4_3_items)
    
    print("Saving modified document...")
    doc.save(DOC_PATH)
    print("Document successfully updated and saved!")

if __name__ == '__main__':
    populate_bab_2()
