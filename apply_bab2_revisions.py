# -*- coding: utf-8 -*-
"""
Script to apply comprehensive revisions to BAB 2 LANDASAN TEORI based on Claude's audit:
- 100% correct citations: Chang (arXiv:2305.00515), Cremel (Anais do XVII Computer on the Beach), Gultom (JICSA 2025)
- Preserves Chang 5x5 kernel fact and Cremel 24% edge detection fact
- Fixes GIL theory (NumPy releases GIL) & Cache theory (L2 private vs L3 shared, capacity misses, 12 MB threshold)
- Fixes Karp-Flatt (3 cases including decreasing e) & Statistics (P=2,4,8, Bonferroni, CLT n=30)
- Fixes A/A control paragraph (independent serial runs, noise floor)
- Fixes Table 2.1 (clean descriptive) & Table 2.2 (IPC bytes and arithmetic intensity columns)
- Fixes language: no 'di mana', '&' only in parens, no hyperbolic words, italicized foreign terms
- Updates both standalone Bab 2 (.docx & .md) and the master report (.docx in OneDrive & local)
"""

import sys
import os
import shutil
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

MASTER_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
MASTER_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
STANDALONE_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_2_LANDASAN_TEORI.docx"
STANDALONE_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_2_LANDASAN_TEORI.docx"
STANDALONE_MD_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_2_LANDASAN_TEORI.md"
STANDALONE_MD_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_2_LANDASAN_TEORI.md"

def set_open_table_borders(table):
    """Format table with open-table style (top border, header bottom, table bottom)."""
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
            text, italic, bold = item, False, False
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

def create_heading(doc, text, level=2, space_before=12, space_after=6):
    """Create a heading paragraph."""
    p = doc.add_paragraph(style=f'Heading {level}')
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(0)
    
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12) if level >= 2 else Pt(14)
    r.bold = True
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

def create_equation_table(doc, eq_text, eq_number_str):
    """Create borderless table for equations with center formula and right-aligned number."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.rows[0].cells[0].width = Cm(12.0)
    tbl.rows[0].cells[1].width = Cm(2.0)
    
    # Border none
    tblPr = tbl._element.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top', 'bottom', 'left', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    
    # Cell 0: Formula (Center)
    c0 = tbl.rows[0].cells[0]
    set_cell_margins(c0, top=40, bottom=40, left=40, right=40)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(3)
    p0.paragraph_format.space_after = Pt(3)
    p0.paragraph_format.line_spacing = 1.15
    p0.paragraph_format.first_line_indent = Cm(0)
    
    r0 = p0.add_run(eq_text)
    r0.font.name = 'Times New Roman'
    r0.font.size = Pt(11)
    r0.italic = True
    
    # Cell 1: Number (Right)
    c1 = tbl.rows[0].cells[1]
    set_cell_margins(c1, top=40, bottom=40, left=40, right=40)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.paragraph_format.space_before = Pt(3)
    p1.paragraph_format.space_after = Pt(3)
    p1.paragraph_format.line_spacing = 1.15
    p1.paragraph_format.first_line_indent = Cm(0)
    
    r1 = p1.add_run(eq_number_str)
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r1.bold = True
    
    return tbl

def format_cell_text(cell, runs_spec, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=Pt(9.0)):
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

def build_table_2_1_revised(doc):
    """Build revised descriptive Table 2.1 Perbandingan Penelitian Terdahulu."""
    headers = [
        "Peneliti dan Tahun",
        "Objek dan Beban Uji",
        "Platform dan Paradigma",
        "Skala / Dimensi Uji",
        "Metrik dan Temuan Utama"
    ]
    widths_cm = [2.5, 2.8, 2.8, 2.4, 3.5]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Chang et al. (2023)", False)],
            [("Operator Sobel multi-arah (kernel 5×5) untuk deteksi tepi", False)],
            [("Akselerasi GPU berbasis NVIDIA CUDA (", False), ("warp-level primitives", True), (")", False)],
            [("Citra resolusi tinggi standar", False)],
            [("Reduksi akses memori dan ", False), ("speedup", True), (" 6,7× s.d. 13,0× terhadap OpenCV-GPU; fokus pada akselerasi perangkat keras skala besar.", False)]
        ),
        (
            [("Vasile et al. (2024)", False)],
            [("Kajian literatur akselerator perangkat keras visi komputer", False)],
            [("Tinjauan arsitektur komputasi (GPU, FPGA, ASIC)", False)],
            [("Studi pustaka komprehensif", False)],
            [("Pemetaan komparatif throughput dan latensi antar-arsitektur; menegaskan tuntutan pemrosesan ", False), ("real-time", True), (" pada aliran data resolusi tinggi.", False)]
        ),
        (
            [("Cremel dan Arruda (2026)", False)],
            [("Filter prapemrosesan citra (", False), ("Blur, Sharpen, Edge detection, CLAHE, Denoise", True), (")", False)],
            [("CPU ", False), ("multi-core", True), (" berbasis OpenMP C/C++ (", False), ("shared memory threads", True), (")", False)],
            [("Variasi resolusi citra digital", False)],
            [("Penurunan efisiensi tajam seiring penambahan utas kerja (mencapai 24% pada 8 utas untuk deteksi tepi); keterbatasan lebar pita memori.", False)]
        ),
        (
            [("Ibrahim et al. (2021)", False)],
            [("Konvolusi filter ", False), ("Gaussian Blur 2D", True)],
            [("Komparasi CPU ", False), ("multi-core", True), (" dan GPU (Google Colab)", False)],
            [("Matriks citra kecil hingga besar", False)],
            [("Beban tambahan transfer memori mendominasi pada resolusi kecil; keuntungan paralel baru tercapai optimal pada matriks besar.", False)]
        ),
        (
            [("Gultom dan Sarumaha (2025)", False)],
            [("Beban komputasi numerik intensif (", False), ("CPU-bound loop", True), (")", False)],
            [("CPython: Sekuensial, ", False), ("Threading", True), (", dan ", False), ("Multiprocessing", True)],
            [("20 juta s.d. 120 juta iterasi numerik", False)],
            [("Multithreading dibatasi GIL (speedup ~1,05×); multiprocessing mencapai speedup 3,16× s.d. 3,55× pada 4 proses.", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    for c_idx, h_text in enumerate(headers):
        cell = tbl.rows[0].cells[c_idx]
        cell.width = Cm(widths_cm[c_idx])
        set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
        format_cell_text(cell, [(h_text, False)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.0))
        
    for r_idx, row_spec in enumerate(rows_data, 1):
        for c_idx, cell_runs in enumerate(row_spec):
            cell = tbl.rows[r_idx].cells[c_idx]
            cell.width = Cm(widths_cm[c_idx])
            set_cell_margins(cell, top=50, bottom=50, left=50, right=50)
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 3] else WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.5))
            
    return tbl

def build_table_2_2_revised(doc):
    """Build revised Table 2.2 with IPC payload bytes and theoretical arithmetic intensity."""
    headers = [
        "Nama Filter",
        "Dimensi Kernel",
        "Operasi Aritmatika per Piksel",
        "Bita IPC per Piksel",
        "Intensitas Aritmatika",
        "Karakteristik Komputasi"
    ]
    widths_cm = [2.2, 1.8, 2.8, 2.0, 2.2, 3.0]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Grayscale", True), ("\n(ITU-R BT.601)", False)],
            [("1 × 1\n(Titik)", False)],
            [("3 perkalian bobot,\n2 penjumlahan kanal\n(5 operasi/piksel)", False)],
            [("3 masuk + 1 keluar\n= 4 bita/piksel", False)],
            [("5 / 4\n= 1,25 op/bita", False)],
            [("Operasi titik linier;\nkecenderungan ", False), ("memory-bound", True), ("; intensitas kalkulasi rendah.", False)]
        ),
        (
            [("Gaussian Blur", True), ("\n3×3", False)],
            [("3 × 3\n(Spasial)", False)],
            [("9 perkalian koefisien,\n8 penjumlahan per kanal × 3 kanal = 51 operasi/piksel", False)],
            [("3 masuk + 3 keluar\n= 6 bita/piksel", False)],
            [("51 / 6\n= 8,50 op/bita", False)],
            [("Konvolusi simetris;\nbeban transfer data memori 3 kanal tinggi.", False)]
        ),
        (
            [("Sobel 3×3", True), ("\n(Gradien Gx dan Gy)", False)],
            [("2 × (3 × 3)\n(Diferensial)", False)],
            [("Hitungan tanpa tap nol:\n12 kali, 10 tambah, 2 kuadrat, 1 tambah, 1 akar\n(26 operasi/piksel)", False)],
            [("3 masuk + 1 keluar\n= 4 bita/piksel", False)],
            [("26 / 4\n= 6,50 op/bita", False)],
            [("Konvolusi ganda non-linier;\nkecenderungan ", False), ("compute-bound", True), ("; intensitas kalkulasi tinggi.", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    for c_idx, h_text in enumerate(headers):
        cell = tbl.rows[0].cells[c_idx]
        cell.width = Cm(widths_cm[c_idx])
        set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
        format_cell_text(cell, [(h_text, False)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(8.5))
        
    for r_idx, row_spec in enumerate(rows_data, 1):
        for c_idx, cell_runs in enumerate(row_spec):
            cell = tbl.rows[r_idx].cells[c_idx]
            cell.width = Cm(widths_cm[c_idx])
            set_cell_margins(cell, top=50, bottom=50, left=50, right=50)
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 3, 4] else WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.0))
            
    return tbl

REVISED_REFERENCES = [
    ("Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", [("Amdahl, G. M.", False), (" (1967). Validity of the single processor approach to achieving large scale computing capabilities. In ", False), ("Proceedings of the April 18–20, 1967, Spring Joint Computer Conference", True), (" (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", False)]),
    ("Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). Multi-directional Sobel operator kernel on GPUs. arXiv. https://doi.org/10.48550/arXiv.2305.00515", [("Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). ", False), ("Multi-directional Sobel operator kernel on GPUs", True), (". arXiv. https://doi.org/10.48550/arXiv.2305.00515", False)]),
    ("Cremel, G. D., & Arruda, L. F. M. (2026). High-performance parallel acceleration of image processing filters on multicore CPUs using OpenMP. Anais do XVII Computer on the Beach, 14–21. https://periodicos.univali.br/index.php/acotb/article/view/22235", [("Cremel, G. D., & Arruda, L. F. M. (2026). High-performance parallel acceleration of image processing filters on multicore CPUs using OpenMP. ", False), ("Anais do XVII Computer on the Beach", True), (", 14–21. https://periodicos.univali.br/index.php/acotb/article/view/22235", False)]),
    ("Gonzalez, R. C., & Woods, R. E. (2018). Digital image processing (4th ed.). Pearson.", [("Gonzalez, R. C., & Woods, R. E. (2018). ", False), ("Digital image processing", True), (" (4th ed.). Pearson.", False)]),
    ("Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. Journal of Informatics, Computer Science, Data Science and Artificial Intelligence, 3(2), 1–8.", [("Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. ", False), ("Journal of Informatics, Computer Science, Data Science and Artificial Intelligence", True), (", 3(2), 1–8.", False)]),
    ("Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021) (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179", [("Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In ", False), ("Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021)", True), (" (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179", False)]),
    ("Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.", [("Intel Corporation. (2023). ", False), ("13th Generation Intel Core processor family datasheet: Volume 1 of 2", True), (". Intel Corporation.", False)]),
    ("International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.", [("International Telecommunication Union. (2011). ", False), ("Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios", True), (" (Recommendation ITU-R BT.601-7). ITU.", False)]),
    ("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614", [("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. ", False), ("Communications of the ACM", True), (", 33(5), 539–543. https://doi.org/10.1145/78607.78614", False)]),
    ("Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.", [("Pacheco, P. S., & Malensek, M. (2022). ", False), ("An introduction to parallel programming", True), (" (2nd ed.). Morgan Kaufmann.", False)]),
    ("Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", [("Python Software Foundation. (n.d.-a). ", False), ("Global interpreter lock", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", False)]),
    ("Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", [("Python Software Foundation. (n.d.-b). ", False), ("multiprocessing — Process-based parallelism", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", False)]),
    ("Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.", [("Tanenbaum, A. S., & Bos, H. (2022). ", False), ("Modern operating systems", True), (" (5th ed.). Pearson.", False)]),
    ("Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. Journal of Imaging, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298", [("Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. ", False), ("Journal of Imaging", True), (", 10(12), Article 298. https://doi.org/10.3390/jimaging10120298", False)])
]

def generate_bab2_revised_elements(doc):
    """Generate all revised elements for Bab 2 as a list of paragraphs and tables."""
    elements = []
    
    # Heading 1
    p_h1 = create_heading(doc, "LANDASAN TEORI", level=1, space_before=18, space_after=12)
    elements.append(p_h1)
    
    # -------------------------------------------------------------
    # 2.1 Perbandingan Terhadap Penelitian Terdahulu
    # -------------------------------------------------------------
    elements.append(create_heading(doc, "Perbandingan Terhadap Penelitian Terdahulu", level=2))
    
    elements.append(create_para(doc, [
        ("Akselerasi proses komputasi pada visi komputer dan pengolahan citra digital telah menjadi fokus kajian intensif seiring dengan pesatnya pertumbuhan resolusi citra digital modern (Cremel & Arruda, 2026). Dalam menangani beban kalkulasi konvolusi matriks yang besar, sejumlah penelitian terdahulu mengarahkan implementasi pada unit pemrosesan grafis (GPU). Chang et al. (2023) meneliti implementasi operator Sobel multi-arah berbasis kernel 5×5 pada GPU menggunakan antarmuka NVIDIA CUDA, serta melaporkan bahwa pemanfaatan ", False),
        ("warp-level primitives", True),
        (" mampu mereduksi akses memori global secara signifikan dan menghasilkan rasio percepatan (", False),
        ("speedup", True),
        (") sebesar 6,7 hingga 13,0 kali lipat dibandingkan pustaka OpenCV-GPU standar. Dari sudut pandang arsitektur perangkat keras, Vasile et al. (2024) mengkaji akselerasi perangkat keras visi komputer dan menegaskan bahwa pemrosesan aliran data citra beresolusi tinggi menuntut pertimbangan ketat antara kapasitas komputasi (", False),
        ("throughput", True),
        (") dan latensi akses memori.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Pada ranah prosesor ", False),
        ("multi-core", True),
        (", eksplorasi komputasi paralel umumnya memanfaatkan model memori bersama (", False),
        ("shared memory", True),
        (") berbasis utas (", False),
        ("threading", True),
        ("). Cremel dan Arruda (2026) mengevaluasi akselerasi filter prapemrosesan citra digital menggunakan pustaka OpenMP pada bahasa C/C++. Temuan mereka menunjukkan bahwa rasio percepatan meningkat seiring membesarnya dimensi citra, namun efisiensi paralel mengalami degradasi tajam saat jumlah utas ditingkatkan hingga 8 utas, dengan efisiensi pada operasi deteksi tepi menurun hingga mencapai 24% akibat keterbatasan lebar pita memori (", False),
        ("memory-bound behavior", True),
        ("). Karakteristik tersebut sejalan dengan temuan Ibrahim et al. (2021) pada komparasi konvolusi Gaussian Blur 2D antara CPU ", False),
        ("multi-core", True),
        (" dan GPU, yang menyimpulkan bahwa beban tambahan (", False),
        ("overhead", True),
        (") transfer memori mendominasi durasi total pada matriks berukuran kecil hingga menengah, sehingga efisiensi pemrosesan paralel baru tercapai secara optimal pada matriks berdimensi besar.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Di sisi lain, implementasi komputasi paralel pada bahasa pemrograman Python menghadapi karakteristik arsitektur internal berupa ", False),
        ("Global Interpreter Lock", True),
        (" (GIL) pada implementasi referensi resmi CPython (Python Software Foundation, n.d.-a). Gultom dan Sarumaha (2025) mengevaluasi kinerja model sekuensial, ", False),
        ("multithreading", True),
        (", dan ", False),
        ("multiprocessing", True),
        (" pada beban komputasi numerik intensif (", False),
        ("CPU-bound", True),
        (") menggunakan Python pada prosesor ", False),
        ("multi-core", True),
        (". Hasil pengujian mereka menunjukkan bahwa ", False),
        ("multithreading", True),
        (" Python hanya menghasilkan rasio percepatan marjinal sekitar 1,05 kali lipat akibat restriksi GIL pada tingkat eksekusi ", False),
        ("bytecode", True),
        (" interpreter. Sebaliknya, modul ", False),
        ("multiprocessing", True),
        (" mampu melipatgandakan kinerja dengan capaian ", False),
        ("speedup", True),
        (" antara 3,16 hingga 3,55 kali lipat pada alokasi empat proses pekerja karena setiap proses memperoleh ruang memori (", False),
        ("address space", True),
        (") dan instansiasi interpreter yang independen (Gultom & Sarumaha, 2025; Tanenbaum & Bos, 2022).", False)
    ]))
    
    elements.append(create_table_title(doc, "Tabel 2.1 Perbandingan Penelitian Terdahulu Terkait Komputasi Paralel pada Pengolahan Citra"))
    elements.append(build_table_2_1_revised(doc))
    
    elements.append(create_para(doc, [
        ("Berdasarkan sintesis kajian pustaka pada Tabel 2.1, terdapat kesenjangan penelitian yang mendasar. Sebagian besar penelitian terdahulu berfokus pada model memori bersama berbasis C/C++ OpenMP (Cremel & Arruda, 2026) atau akselerasi GPU (Chang et al., 2023; Ibrahim et al., 2021), sedangkan studi multiprocessing Python (Gultom & Sarumaha, 2025) baru menguji beban iterasi sintetis murni. Belum ada penelitian yang secara sistematis membedah perilaku komputasi paralel multiprocessing Python pada pemrosesan citra multiresolusi bertingkat (512 hingga 4096 piksel) pada prosesor heterogen modern yang memadukan inti performa (P-Core) dan inti efisiensi (E-Core). Penelitian ini mengisi ruang tersebut dengan mengevaluasi tiga variasi algoritma filter spasial, memetakan kurva empiris terhadap batas teoretis Hukum Amdahl dan metrik Karp–Flatt, serta menerapkan kendali mutu pengukuran melalui protokol pengujian berselang-seling dan kontrol A/A.", False)
    ]))
    
    # -------------------------------------------------------------
    # 2.2 Pengolahan Citra Digital dan Operasi Filter Spasial
    # -------------------------------------------------------------
    elements.append(create_heading(doc, "Pengolahan Citra Digital dan Operasi Filter Spasial", level=2))
    
    elements.append(create_para(doc, [
        ("Pengolahan citra digital merupakan disiplin rekayasa komputer yang memanipulasi representasi visual diskret menggunakan algoritma komputasi terstruktur guna mengekstraksi informasi, meningkatkan kualitas visual, atau mempersiapkan data untuk analisis tingkat lanjut (Gonzalez & Woods, 2018). Dalam domain spasial, operasi filter citra bekerja secara langsung pada nilai intensitas piksel yang menyusun bidang matriks gambar.", False)
    ]))
    
    # 2.2.1 Representasi Citra Digital dan Operasi Konvolusi 2D
    elements.append(create_heading(doc, "Representasi Citra Digital dan Operasi Konvolusi 2D", level=3))
    
    elements.append(create_para(doc, [
        ("Secara matematis, citra digital monokromatik dimodelkan sebagai fungsi diskret intensitas dua dimensi ", False),
        ("I(x, y)", True),
        (", dengan ", False),
        ("x", True),
        (" dan ", False),
        ("y", True),
        (" menyatakan koordinat spasial pada bidang matriks, sedangkan nilainya merepresentasikan derajat keabuan (", False),
        ("gray level", True),
        (") piksel. Pada citra digital berwarna berformat RGB, representasi diperluas menjadi larik tiga dimensi berdimensi ", False),
        ("H × W × C", True),
        (", dengan ", False),
        ("H", True),
        (" menyatakan tinggi citra (jumlah baris), ", False),
        ("W", True),
        (" menyatakan lebar citra (jumlah kolom), dan ", False),
        ("C = 3", True),
        (" menyatakan komponen kanal warna primer merah (Red), hijau (Green), dan biru (Blue) (Gonzalez & Woods, 2018).", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Operasi filter spasial linier pada citra digital dieksekusi melalui pergeseran matriks bobot berukuran kecil yang disebut kernel konvolusi di atas bidang citra masukan. Nilai piksel luaran pada koordinat spasial ", False),
        ("(x, y)", True),
        (" dihitung sebagai penjumlahan berbobot dari perkalian elemen kernel terhadap nilai piksel ketetanggaannya. Mengacu pada perumusan baku pengolahan citra (Gonzalez & Woods, 2018), operasi konvolusi diskret dua dimensi (secara teknis dieksekusi sebagai korelasi silang tanpa pembalikan kernel) dinyatakan pada Persamaan (2.1):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "I_filter(x, y) = ∑_(i=-k)^k ∑_(j=-k)^k K(i, j) · I(x + i, y + j)",
        "(2.1)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq1_notes = [
        ("I_filter(x, y)", " : Nilai intensitas piksel luaran hasil pemfilteran pada koordinat spasial (x, y)."),
        ("I(x + i, y + j)", " : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (x + i, y + j)."),
        ("K(i, j)", " : Koefisien bobot matriks kernel konvolusi pada koordinat relatif (i, j)."),
        ("k", " : Radius spasial matriks kernel (pada kernel berdimensi 3 × 3, bernilai k = 1)."),
        ("i, j", " : Indeks pergeseran koordinat spasial kernel secara vertikal dan horizontal.")
    ]
    for sym, desc in p_eq1_notes:
        p_item = create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0))
        elements.append(p_item)
        
    elements.append(create_para(doc, [
        ("Bentuk formulasi pada Persamaan (2.1) secara teknis merupakan operasi korelasi silang (", False),
        ("cross-correlation", True),
        (") yang lazim disebut sebagai konvolusi dalam pustaka rekayasa visi komputer modern. Untuk kernel spasial simetris seperti Gaussian, hasil korelasi silang identik secara matematis dengan konvolusi sejati. Adapun pada operator diferensial seperti Sobel, korelasi silang hanya membalik tanda arah gradien tanpa mengubah nilai magnitudo gradien tepi yang dihasilkan.", False)
    ]))
    
    # 2.2.2 Karakteristik Algoritma Filter Spasial yang Diuji
    elements.append(create_heading(doc, "Karakteristik Algoritma Filter Spasial yang Diuji", level=3))
    
    elements.append(create_para(doc, [
        ("Penelitian ini menguji tiga algoritma filter spasial dengan karakteristik beban komputasi dan kebutuhan memori yang bertingkat secara sistematis:\n", False),
        ("1. Konversi Grayscale (Rekomendasi ITU-R BT.601-7): Merupakan operasi titik linier independen tanpa ketetanggaan spasial yang mentransformasikan tiga kanal warna RGB menjadi satu kanal luminansi monokromatik berbobot matematis: Y = 0,299R + 0,587G + 0,114B (International Telecommunication Union, 2011). Operasi ini membutuhkan 3 perkalian dan 2 penjumlahan per piksel dengan rasio komputasi terhadap volume data yang rendah (intensitas aritmatika 1,25 FLOP/bita).\n", False),
        ("2. Penghalusan Citra Gaussian Blur 3×3: Merupakan filter lolos-rendah (", False),
        ("low-pass filter", True),
        (") berbasis konvolusi spasial dua dimensi dengan radius k = 1 pada ketiga kanal warna RGB. Setiap piksel luaran dihitung dari konvolusi matriks kernel Gaussian diskret berbobot normalisasi 1/16, menghasilkan 51 operasi aritmatika per piksel dengan transfer data IPC sebesar 6 bita per piksel.\n", False),
        ("3. Deteksi Tepi Sobel 3×3: Merupakan filter diferensial spasial tingkat pertama yang menghitung aproksimasi gradien intensitas citra pada arah horizontal (Gx) dan vertikal (Gy). Menggunakan konvensi hitungan tanpa tap bernilai nol (mengeliminasi kolom tengah Gx dan baris tengah Gy), setiap koordinat piksel memerlukan 12 perkalian koefisien, 10 penjumlahan, 2 pemangkatan kuadrat, 1 penjumlahan kuadrat gradien, dan 1 kalkulasi akar kuadrat untuk menghasilkan magnitudo gradien (total 26 operasi aritmatika per piksel).", False)
    ]))
    
    elements.append(create_table_title(doc, "Tabel 2.2 Karakteristik Algoritma Filter Spasial yang Diuji"))
    elements.append(build_table_2_2_revised(doc))
    
    elements.append(create_para(doc, [
        ("Hierarki rancangan ketiga algoritma filter pada Tabel 2.2 memungkinkan pemetaan komparatif yang komprehensif, mulai dari operasi titik berintensitas aritmatika rendah dengan kecenderungan terikat memori (", False),
        ("memory-bound", True),
        ("), hingga operasi konvolusi diferensial non-linier yang membutuhkan instruksi aritmatika intensif dengan kecenderungan terikat komputasi (", False),
        ("compute-bound", True),
        (").", False)
    ]))
    
    # -------------------------------------------------------------
    # 2.3 Komputasi Paralel dan Multiprocessing Python
    # -------------------------------------------------------------
    elements.append(create_heading(doc, "Komputasi Paralel dan Multiprocessing Python", level=2))
    
    elements.append(create_para(doc, [
        ("Komputasi paralel adalah paradigma pemrosesan informasi yang membagi satu beban kalkulasi terpadu menjadi beberapa sub-tugas independen yang dieksekusi secara simultan pada unit pemrosesan fisik yang berbeda (Pacheco & Malensek, 2022). Tujuannya adalah mereduksi waktu eksekusi total dan meningkatkan efisiensi pemanfaatan sumber daya perangkat keras prosesor modern.", False)
    ]))
    
    # 2.3.1 Paradigma Data Parallelism dan Dekomposisi Domain Spasial
    elements.append(create_heading(doc, "Paradigma Data Parallelism dan Dekomposisi Domain Spasial", level=3))
    
    elements.append(create_para(doc, [
        ("Dalam taksonomi komputasi paralel, terdapat dua strategi pemecahan masalah utama: ", False),
        ("task parallelism", True),
        (" dan ", False),
        ("data parallelism", True),
        (" (Pacheco & Malensek, 2022). ", False),
        ("Task parallelism", True),
        (" mendistribusikan fungsi komputasi yang berbeda ke beberapa prosesor, sedangkan ", False),
        ("data parallelism", True),
        (" mendistribusikan elemen-elemen data berukuran besar ke beberapa unit pemrosesan yang menjalankan rantai instruksi algoritma yang serupa secara serentak. Pengolahan filter citra digital merupakan contoh representatif dari persoalan paralel mandiri (", False),
        ("embarrassingly parallel", True),
        ("), karena sebagian besar wilayah spasial citra dapat dihitung secara terpisah tanpa memerlukan sinkronisasi nilai perantara antar-pekerja (Cremel & Arruda, 2026).", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Dekomposisi domain spasial pada penelitian ini diterapkan melalui metode pembagian baris horizontal (", False),
        ("horizontal row partitioning", True),
        ("). Matriks citra berdimensi H × W × C dibagi secara merata sepanjang sumbu vertikal menjadi P potongan blok berdimensi (H/P) × W × C untuk didistribusikan ke P proses pekerja. Pada seluruh matriks uji yang dirancang, dimensi tinggi citra H (512, 1024, 2048, dan 4096 piksel) habis dibagi oleh jumlah proses pekerja P (1, 2, 4, dan 8 proses), sehingga pembagian beban kerja antar-proses pekerja bersifat seimbang sempurna tanpa adanya baris sisa yang dapat memicu ketimpangan beban kerja (", False),
        ("load imbalance", True),
        (").", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Tantangan utama dekomposisi spasial pada operasi konvolusi terletak pada ketergantungan data lokal di area tepi perbatasan blok. Piksel-piksel yang berada pada baris batas atas dan baris batas bawah potongan membutuhkan informasi intensitas piksel tetangga di luar area bloknya sejauh radius spasial k = 1. Untuk mengatasi ketergantungan ini, setiap blok potongan diperluas secara fisik dengan menambahkan k baris piksel tetangga di sisi atas dan bawah yang disebut sebagai baris batas (", False),
        ("boundary halo", True),
        ("). Potongan interior menerima satu baris batas atas dan satu baris batas bawah, menghasilkan potongan masukan berukuran ((H/P) + 2k) × W × C, sedangkan potongan tepi citra terluar hanya menerima penambahan baris batas pada satu sisi.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Mekanisme baris batas ini menjamin keamanan konkurensi data karena baris batas hanya dibaca secara mandiri oleh pekerja tanpa adanya operasi penulisan balik ke ruang memori proses lain, sehingga meniadakan potensi terjadinya kondisi balapan (", False),
        ("race condition", True),
        ("). Setelah komputasi filter selesai dieksekusi, setiap pekerja melakukan pemotongan pembuangan (", False),
        ("halo stripping", True),
        (") terhadap baris batas tersebut sebelum mengembalikan blok luaran ke proses utama, sehingga dimensi matriks hasil pemrosesan kembali tepat berukuran (H/P) × W untuk digabungkan kembali secara sekuensial melalui fungsi ", False),
        ("numpy.vstack()", True),
        (".", False)
    ]))
    
    # 2.3.2 Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC
    elements.append(create_heading(doc, "Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC", level=3))
    
    elements.append(create_para(doc, [
        ("CPython, implementasi referensi standar bahasa pemrograman Python, mengandalkan mekanisme manajemen memori berbasis pencacah referensi (", False),
        ("reference counting", True),
        ("). Untuk mencegah korupsi memori internal dan konflik alokasi objek saat beberapa utas berjalan serentak, CPython menerapkan ", False),
        ("Global Interpreter Lock", True),
        (" (GIL) (Python Software Foundation, n.d.-a; Tanenbaum & Bos, 2022). GIL adalah mekanisme kunci biner (", False),
        ("mutex", True),
        (") yang membatasi bahwa hanya satu utas yang diizinkan mengeksekusi ", False),
        ("bytecode", True),
        (" Python murni pada satu waktu. Akibatnya, pustaka ", False),
        ("threading", True),
        (" standar Python tidak mampu memanfaatkan kapasitas multi-core secara efektif pada beban kerja komputasi murni yang ditulis dalam bahasa Python (Gultom & Sarumaha, 2025). Perlu dicatat secara metodologis bahwa pustaka numerik berbasis C seperti NumPy secara internal melepas GIL (", False),
        ("releases the GIL", True),
        (") pada banyak operasi kalkulasi larik berukuran besar. Oleh karena itu, pemilihan paradigma multiprocessing dalam penelitian ini merupakan batasan ruang lingkup rancangan sistem untuk mengevaluasi isolasi proses independen dan beban koordinasi IPC, bukan pernyataan bahwa multithreading pasti gagal pada seluruh implementasi operasi berbasis NumPy.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Modul bawaan ", False),
        ("multiprocessing", True),
        (" pada Python dirancang untuk melangkahi restriksi GIL dengan menerapkan arsitektur konkurensi berbasis proses independen (Python Software Foundation, n.d.-b). Alih-alih membuat utas ringan di dalam ruang proses yang sama, modul ini meluncurkan proses sistem operasi baru yang terpisah. Masing-masing proses pekerja memiliki ruang alamat memori fisik independen (", False),
        ("isolated address space", True),
        (") dan instansiasi interpreter CPython mandiri (Tanenbaum & Bos, 2022). Pendekatan ini memungkinkan eksekusi instruksi komputasi berjalan secara paralel sesungguhnya (", False),
        ("true hardware parallelism", True),
        (") pada setiap inti prosesor fisik yang tersedia.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Namun demikian, isolasi ruang alamat memori pada arsitektur proses menimbulkan konsekuensi berupa beban tambahan komunikasi antar-proses (", False),
        ("inter-process communication / IPC", True),
        ("). Karena memori tidak dapat diakses secara langsung antar-proses, data larik citra masukan harus diubah ke dalam bentuk deretan bita melalui proses serialisasi (", False),
        ("pickling", True),
        ("), dikirimkan melalui saluran pipa (", False),
        ("pipes", True),
        (") atau antrean (", False),
        ("queues", True),
        (") sistem operasi, dan dide-serialisasi kembali (", False),
        ("unpickling", True),
        (") di ruang memori proses pekerja penerima. Beban penalti transmisi memori ini tumbuh sebanding dengan membesarnya dimensi data citra yang ditransfer dan menjadi komponen dominan dari beban tambahan paralel (", False),
        ("parallel overhead", True),
        (").", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Aspek kritis lain dalam ekosistem Python adalah model tata letak memori larik NumPy. Pustaka NumPy mengorganisasikan larik multidimensi dalam urutan berbasis baris (", False),
        ("row-major order", True),
        (") atau tata letak memori ", False),
        ("C-contiguous", True),
        (" (Pacheco & Malensek, 2022). Dalam representasi ini, elemen-elemen piksel pada baris horizontal yang sama menempati lokasi alamat memori fisik yang berurutan secara linier. Karakteristik ini memberikan keunggulan lokalitas spasial (", False),
        ("spatial locality", True),
        (") yang tinggi ketika dekomposisi data dilakukan melalui pemotongan baris horizontal, karena setiap proses pekerja menerima satu segmen blok memori yang kontinu tanpa fragmentasi pointer alamat.", False)
    ]))
    
    # 2.3.3 Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache
    elements.append(create_heading(doc, "Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache", level=3))
    
    elements.append(create_para(doc, [
        ("Evolusi arsitektur mikroprosesor modern telah bergeser dari peningkatan frekuensi kerja tunggal menuju integrasi banyak inti prosesor (", False),
        ("multi-core architecture", True),
        (") pada satu keping silikon (Pacheco & Malensek, 2022). Pada generasi prosesor Intel Core ke-13 (nama sandi Raptor Lake-H), diterapkan mikroarsitektur hibrida (", False),
        ("hybrid architecture", True),
        (") yang memadukan dua kategori mikroarsitektur inti komputasi dengan karakteristik daya dan instruksi per siklus (IPC) yang berbeda (Intel Corporation, 2023):\n", False),
        ("1. Performance-Cores (P-Cores, arsitektur turunan Golden Cove pada prosesor Core i5-13420H): Didesain untuk mengeksekusi beban kerja komputasi sekuensial dan latensi rendah dengan frekuensi turbo hingga 4,6 GHz serta mendukung Simultaneous Multithreading (SMT / Hyper-Threading 2 threads per inti fisik).\n", False),
        ("2. Efficient-Cores (E-Cores, arsitektur Gracemont): Didesain untuk memaksimalkan efisiensi energi dan keluaran beban kerja throughput tinggi multi-proses dengan frekuensi turbo hingga 3,4 GHz tanpa SMT (1 thread per inti fisik).", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Penjadwalan alokasi proses pada mikroprosesor hibrida didukung oleh mekanisme umpan balik perangkat keras (", False),
        ("Intel Thread Director", True),
        (") yang secara dinamis memantau karakteristik instruksi eksekusi proses dan memberikan rekomendasi penjadwalan kepada sistem operasi (Intel Corporation, 2023).", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Di samping diferensiasi inti komputasi, hierarki subsistem memori prosesor memainkan peran penentu dalam membatasi atau mengoptimalkan laju aliran data komputasi konvolusi matriks:\n", False),
        ("1. Cache Level 1 (L1): Terdiri atas 80 KB per P-Core dan 96 KB per E-Core dengan latensi akses tercepat (1 hingga 2 siklus clock prosesor).\n", False),
        ("2. Cache Level 2 (L2): Bersifat privat berkapasitas 1,25 MB per P-Core serta 2 MB terbagi bersama (shared) per kluster empat E-Core (Intel Corporation, 2023).\n", False),
        ("3. Cache Level 3 (L3 / Intel Smart Cache): Berkapasitas 12 MB yang terbagi secara bersama (shared cache) untuk seluruh inti prosesor.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Interaksi antara volume data matriks citra dan kapasitas hierarki memori cache memunculkan fenomena performa yang tidak linier. Pada matriks citra berdimensi kecil (512 × 512 piksel berukuran sekitar 768 KB), data citra masukan beserta potongan bloknya termuat secara utuh di dalam 12 MB L3 Cache bersama. Efek percepatan superlinear yang teramati pada operasi intensif seperti Sobel 512 dipengaruhi oleh kapasitas L2 Cache privat (1,25 MB per P-Core), sehingga setiap proses pekerja menerima irisan blok sekitar 192 KB yang termuat penuh di dalam L2 Cache privatnya, menghasilkan tingkat keberhasilan akses (", False),
        ("cache hit rate", True),
        (") yang tinggi dan meniadakan penalti latensi bus memori utama. Sebaliknya, pada citra beresolusi 2048 × 2048 piksel (volume data RGB mentah mencapai ~12,58 MB) dan 4096 × 4096 piksel (~48 MB), ukuran data melampaui kapasitas 12 MB L3 Cache bersama. Kondisi ini memicu kegagalan pemuatan kapasitas (", False),
        ("capacity misses", True),
        (") dan memaksa prosesor melakukan transfer data berulang ke memori utama (RAM DDR5 5200 MT/s), sehingga batas performa komputasi bergeser menuju saturasi lebar pita memori (", False),
        ("DRAM bandwidth saturation", True),
        (").", False)
    ]))
    
    # -------------------------------------------------------------
    # 2.4 Metrik Evaluasi Kinerja dan Model Skalabilitas
    # -------------------------------------------------------------
    elements.append(create_heading(doc, "Metrik Evaluasi Kinerja dan Model Skalabilitas", level=2))
    
    elements.append(create_para(doc, [
        ("Untuk mengukur, menganalisis, dan memvalidasi efektivitas komputasi paralel secara kuantitatif, digunakan serangkaian parameter kinerja baku dan model matematis skalabilitas yang terstandarisasi dalam literatur rekayasa komputasi paralel.", False)
    ]))
    
    # 2.4.1 Metrik Kinerja Dasar: Waktu Eksekusi, Speedup, Efisiensi, dan Overhead Paralel
    elements.append(create_heading(doc, "Metrik Kinerja Dasar: Waktu Eksekusi, Speedup, Efisiensi, dan Overhead Paralel", level=3))
    
    elements.append(create_para(doc, [
        ("Evaluasi kinerja komputasi bertumpu pada perbandingan durasi waktu pemrosesan antara varian program serial murni satu inti prosesor (", False),
        ("T_serial", True),
        (") terhadap durasi pemrosesan pada arsitektur paralel dengan alokasi ", False),
        ("P", True),
        (" proses pekerja (", False),
        ("T_paralel", True),
        (").", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Rasio percepatan (", False),
        ("speedup", True),
        (") mengukur seberapa banyak kelipatan percepatan komputasi yang dihasilkan oleh sistem paralel dibandingkan eksekusi serial pada kondisi data yang identik (Pacheco & Malensek, 2022). Mengacu pada formulasi standar, rasio percepatan ", False),
        ("S", True),
        (" dirumuskan pada Persamaan (2.2):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "S = T_serial / T_paralel",
        "(2.2)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq2_notes = [
        ("S", " : Nilai rasio percepatan (speedup) komputasi (rasio tanpa satuan)."),
        ("T_serial", " : Waktu eksekusi pemrosesan citra pada skrip serial murni (detik)."),
        ("T_paralel", " : Waktu eksekusi pemrosesan citra secara paralel pada alokasi P proses pekerja (detik).")
    ]
    for sym, desc in p_eq2_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Efisiensi paralel (", False),
        ("parallel efficiency", True),
        (") mengukur fraksi pemanfaatan kapasitas komputasi dari setiap unit proses pekerja yang dialokasikan dalam eksekusi paralel (Pacheco & Malensek, 2022). Efisiensi paralel ", False),
        ("E", True),
        (" dirumuskan pada Persamaan (2.3):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "E = (S / P) × 100% = (T_serial / (P · T_paralel)) × 100%",
        "(2.3)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq3_notes = [
        ("E", " : Persentase efisiensi komputasi paralel (%)."),
        ("S", " : Nilai rasio percepatan yang diperoleh dari Persamaan (2.2)."),
        ("P", " : Jumlah proses pekerja yang dialokasikan dalam eksekusi paralel.")
    ]
    for sym, desc in p_eq3_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Beban tambahan paralel (", False),
        ("parallel overhead", True),
        (") merepresentasikan selisih waktu antara durasi eksekusi paralel aktual terhadap waktu eksekusi paralel ideal tanpa biaya koordinasi (Pacheco & Malensek, 2022). Formulasi beban tambahan paralel ", False),
        ("T_overhead", True),
        (" dinyatakan pada Persamaan (2.4):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "T_overhead = T_paralel - (T_serial / P)",
        "(2.4)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq4_notes = [
        ("T_overhead", " : Durasi beban tambahan sistem paralel akibat koordinasi sistem (detik)."),
        ("T_paralel", " : Waktu eksekusi paralel aktual yang terukur (detik)."),
        ("T_serial / P", " : Waktu eksekusi paralel ideal secara teoretis tanpa penalti koordinasi (detik)."),
        ("T_serial", " : Waktu eksekusi serial baseline (detik)."),
        ("P", " : Jumlah proses pekerja yang dialokasikan.")
    ]
    for sym, desc in p_eq4_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Parameter ", False),
        ("T_overhead", True),
        (" mencakup spektrum biaya koordinasi sistem, termasuk latensi transmisi pipa IPC, serialisasi dan deserialisasi objek data (", False),
        ("pickling/unpickling", True),
        ("), replikasi baris batas (", False),
        ("boundary halo", True),
        ("), penggabungan kembali matriks luaran (", False),
        ("numpy.vstack", True),
        ("), ketimpangan beban kerja (", False),
        ("load imbalance", True),
        ("), serta kontensi lebar pita memori utama. Parameter ", False),
        ("T_overhead", True),
        (" secara empiris dapat bernilai negatif apabila terjadi akselerasi superlinear yang dipicu oleh efisiensi pemanfaatan L2 Cache privat pada blok data berdimensi kecil.", False)
    ]))
    
    # 2.4.2 Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp–Flatt
    elements.append(create_heading(doc, "Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp–Flatt", level=3))
    
    elements.append(create_para(doc, [
        ("Batas percepatan maksimum suatu sistem komputasi paralel pada ukuran masalah konstan (", False),
        ("strong scaling", True),
        (") dibatasi oleh fraksi kode yang harus dieksekusi secara sekuensial, sebagaimana dirumuskan dalam Hukum Amdahl (Amdahl, 1967). Rasio percepatan teoretis Amdahl ", False),
        ("S_Amdahl", True),
        (" dinyatakan pada Persamaan (2.5):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "S_Amdahl = 1 / ((1 - f) + (f / P))",
        "(2.5)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq5_notes = [
        ("S_Amdahl", " : Percepatan teoretis maksimum pada alokasi P proses pekerja."),
        ("f", " : Fraksi beban komputasi yang dapat diparalelkan (0 ≤ f ≤ 1)."),
        ("(1 - f)", " : Fraksi serial efektif yang tidak mengalami paralelisasi."),
        ("P", " : Jumlah proses pekerja yang dialokasikan.")
    ]
    for sym, desc in p_eq5_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Ketika alokasi prosesor ditingkatkan menuju tak hingga (P → ∞), rasio percepatan teoretis Amdahl mendekati batas asimtotik ", False),
        ("S_max = 1 / (1 - f)", True),
        (". Formulasi ini menunjukkan bahwa keberadaan komponen sekuensial sekecil apa pun membatasi percepatan maksimum secara asimtotik.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Hukum Amdahl mengasumsikan bahwa fraksi serial bersifat konstan dan mengabaikan beban koordinasi komunikasi antar-proses. Untuk memeriksa apakah keterbatasan skalabilitas empiris bersumber dari keterbatasan sekuensial murni ataukah dipicu oleh membengkaknya beban tambahan koordinasi paralel, Karp dan Flatt (1990) merumuskan metrik fraksi serial eksperimental (", False),
        ("experimentally determined serial fraction", True),
        (") ", False),
        ("e", True),
        (" pada Persamaan (2.6):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "e = ((1 / S) - (1 / P)) / (1 - (1 / P))",
        "(2.6)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq6_notes = [
        ("e", " : Fraksi serial eksperimental (metrik Karp–Flatt)."),
        ("S", " : Rasio percepatan empiris yang terukur pada alokasi P proses pekerja."),
        ("P", " : Jumlah proses pekerja yang dialokasikan (P > 1).")
    ]
    for sym, desc in p_eq6_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Metrik Karp–Flatt memberikan tiga indikasi diagnostik perilaku sistem komputasi paralel seiring penambahan proses pekerja P:\n", False),
        ("1. Jika nilai e meningkat secara konsisten seiring bertambahnya P, hal ini mengindikasikan bahwa keterbatasan skalabilitas terutama dipicu oleh pembengkakan beban tambahan koordinasi paralel (overhead IPC, kontensi memori, dan latensi sinkronisasi).\n", False),
        ("2. Jika nilai e relatif konstan terhadap P, hal ini mengindikasikan bahwa pembatas skalabilitas didominasi oleh fraksi kode sekuensial inheren algoritma atau beban koordinasi tetap. Perlu dicatat bahwa metrik ini tidak memisahkan fraksi sekuensial inheren dari biaya tetap komunikasi IPC.\n", False),
        ("3. Jika nilai e menurun seiring bertambahnya P, hal ini mengindikasikan adanya efek superlinearitas lokalitas memori cache privat (karena pembagian data membuat setiap sub-blok termuat penuh dalam cache berkecepatan tinggi) atau performa baseline serial yang mengalami degradasi penalti akses memori.", False)
    ]))
    
    # 2.4.3 Analisis Statistik Pengukuran dan Evaluasi Batas Derau Sistem (Kontrol A/A)
    elements.append(create_heading(doc, "Analisis Statistik Pengukuran dan Evaluasi Batas Derau Sistem (Kontrol A/A)", level=3))
    
    elements.append(create_para(doc, [
        ("Akurasi pengukuran kinerja pada sistem komputer riil dipengaruhi oleh fluktuasi derau interupsi sistem operasi, penjadwalan latar belakang, dan dinamika termal perangkat keras (Pacheco & Malensek, 2022). Untuk meredam bias derau temporal, seluruh kombinasi perlakuan dieksekusi sebanyak 30 kali repetisi terkontrol yang dijalankan secara berselang-seling (", False),
        ("interleaved execution", True),
        (") antara pengukuran serial dan paralel.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Data durasi waktu eksekusi pada sistem komputer umumnya memiliki distribusi yang menjulur ke kanan (", False),
        ("right-skewed distribution", True),
        (") akibat adanya nilai pencilan (", False),
        ("outliers", True),
        (") berkala dari interupsi sistem. Oleh karena itu, representasi pemusatan data mengutamakan statistik non-parametrik yang tangguh terhadap pencilan (", False),
        ("robust statistics", True),
        ("), yaitu nilai median dan rentang antarkuartil (IQR, [", False),
        ("Q25 - Q75", True),
        ("]), sedangkan nilai rerata sampel (", False),
        ("x̄", True),
        (") dan simpangan baku (", False),
        ("s", True),
        (") tetap dilaporkan sebagai parameter penunjang.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Untuk memberikan estimasi presisi statistik pada nilai rerata parameter kinerja, dihitung selang kepercayaan 95% (", False),
        ("confidence interval", True),
        (") menggunakan distribusi t-Student. Penerapan distribusi t-Student pada data komputasi didasarkan pada Teorema Limit Pusat (", False),
        ("Central Limit Theorem / CLT", True),
        (") untuk ukuran sampel n = 30 repetisi, didukung oleh verifikasi independensi observasi melalui estimasi koefisien autokorelasi lag-1 yang mendekati nol (ρ1 ≈ 0). Formulasi selang kepercayaan 95% dinyatakan pada Persamaan (2.7):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "CI_95% = x̄ ± t_(n-1, α/2) · (s / √n)",
        "(2.7)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq7_notes = [
        ("CI_95%", " : Selang kepercayaan 95% (confidence interval) nilai rerata populasi."),
        ("x̄", " : Nilai rerata sampel dari n = 30 repetisi pengujian."),
        ("s", " : Simpangan baku sampel."),
        ("n", " : Ukuran sampel repetisi pengujian (n = 30, derajat kebebasan df = n - 1 = 29)."),
        ("t_(n-1, α/2)", " : Nilai kritis distribusi t-Student pada tingkat signifikansi α = 0,05 (t_(29; 0,025) = 2,04523).")
    ]
    for sym, desc in p_eq7_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Pengujian signifikansi perbedaan performa antar-alokasi proses pekerja paralel riil dievaluasi melalui uji hipotesis non-parametrik Kruskal–Wallis untuk variasi alokasi P = 2, 4, dan 8 proses pekerja, serta uji Mann–Whitney U untuk perbandingan dua kelompok perlakuan independen dengan taraf signifikansi α = 0,05. Pada analisis komparasi berpasangan ganda (", False),
        ("multiple pairwise comparisons", True),
        ("), diterapkan koreksi signifikansi (seperti koreksi Holm atau Bonferroni) guna menjaga laju kesalahan keluarga perlakuan (", False),
        ("family-wise error rate", True),
        (").", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Sebagai instrumen kendali mutu pengukuran, dijalankan kontrol A/A pada alokasi P = 1, yaitu dua pengukuran serial independen yang disisipkan secara berselang-seling pada protokol pengujian yang sama. Karena kedua pengukuran mengeksekusi instruksi kode yang identik pada unit pemrosesan yang sama, nilai rasio percepatan S teoretis bernilai 1,00. Simpangan nilai S empiris dari 1,00 difungsikan sebagai estimasi batas derau sistem (", False),
        ("system noise floor", True),
        (") dan memverifikasi ketiadaan bias urutan (", False),
        ("order effect", True),
        ("). Pengujian kontrol A/A ini tidak mengukur biaya struktural komunikasi IPC.", False)
    ]))
    
    return elements

def update_standalone_documents():
    print("=== Updating Standalone BAB 2 Documents ===")
    doc = docx.Document()
    
    # Set page margins 4-3-3-3 cm
    sections = doc.sections
    for s in sections:
        s.top_margin = Cm(4.0)
        s.left_margin = Cm(4.0)
        s.bottom_margin = Cm(3.0)
        s.right_margin = Cm(3.0)
        
    elements = generate_bab2_revised_elements(doc)
    
    # Add References
    p_ref_h = create_heading(doc, "DAFTAR PUSTAKA (RUJUKAN BAB 2)", level=1, space_before=24, space_after=12)
    
    for plain_text, runs_spec in REVISED_REFERENCES:
        p_ref = doc.add_paragraph(style='Normal')
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.5
        p_ref.paragraph_format.left_indent = Cm(1.27)
        p_ref.paragraph_format.first_line_indent = Cm(-1.27)
        
        for text, italic in runs_spec:
            r = p_ref.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.italic = italic
            
    print(f"Saving standalone docx to: {STANDALONE_DOCX_LOCAL}")
    doc.save(STANDALONE_DOCX_LOCAL)
    
    try:
        shutil.copy2(STANDALONE_DOCX_LOCAL, STANDALONE_DOCX_ONEDRIVE)
        print("Standalone docx copied to OneDrive successfully!")
    except Exception as e:
        print("Notice on OneDrive copy:", e)
        
    # Generate revised Markdown
    print("Generating revised Markdown...")
    md_lines = ["# BAB 2 LANDASAN TEORI\n"]
    doc_for_md = docx.Document(STANDALONE_DOCX_LOCAL)
    for child in doc_for_md.element.body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(child, doc_for_md)
            txt = p.text.strip()
            style = p.style.name
            if style.startswith('Heading 1'):
                if 'LANDASAN TEORI' in txt:
                    continue
                else:
                    md_lines.append(f"\n# {txt}\n")
            elif style.startswith('Heading 2'):
                md_lines.append(f"\n## {txt}\n")
            elif style.startswith('Heading 3'):
                md_lines.append(f"\n### {txt}\n")
            elif style == 'List Paragraph':
                md_lines.append(f"* {txt}")
            elif txt:
                md_lines.append(f"{txt}\n")
        elif tag == 'tbl':
            tbl = docx.table.Table(child, doc_for_md)
            if len(tbl.rows) == 1 and len(tbl.columns) == 2:
                eq_text = tbl.rows[0].cells[0].text.strip()
                eq_num = tbl.rows[0].cells[1].text.strip()
                md_lines.append(f"\n$$\n{eq_text} \\quad {eq_num}\n$$\n")
            else:
                md_lines.append("\n")
                header_cells = [c.text.strip().replace('\n', ' ') for c in tbl.rows[0].cells]
                md_lines.append("| " + " | ".join(header_cells) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(header_cells)) + " |")
                for r in tbl.rows[1:]:
                    row_cells = [c.text.strip().replace('\n', '<br>') for c in r.cells]
                    md_lines.append("| " + " | ".join(row_cells) + " |")
                md_lines.append("\n")
                
    md_content = "\n".join(md_lines)
    with open(STANDALONE_MD_LOCAL, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Saved revised Markdown to: {STANDALONE_MD_LOCAL}")
    
    try:
        shutil.copy2(STANDALONE_MD_LOCAL, STANDALONE_MD_ONEDRIVE)
        print("Standalone markdown copied to OneDrive successfully!")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

def update_master_document():
    print("\n=== Updating Master Document with Revised Bab 2 ===")
    doc = docx.Document(MASTER_DOCX_LOCAL)
    body = doc.element.body
    elements = list(body)
    
    start_idx = None
    end_idx = None
    
    for i, el in enumerate(elements):
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, doc)
            txt = p.text.strip()
            if p.style.name.startswith('Heading 1') and 'LANDASAN TEORI' in txt:
                start_idx = i
            elif p.style.name.startswith('Heading 1') and 'METODOLOGI PENELITIAN' in txt:
                end_idx = i
                break
                
    assert start_idx is not None and end_idx is not None, f"Could not find Bab 2 bounds: {start_idx}, {end_idx}"
    print(f"Found Bab 2 bounds in master docx: start={start_idx}, end={end_idx}")
    
    target_p_before = elements[end_idx]
    
    # Generate new elements in a scratch document to get their XML
    scratch_doc = docx.Document()
    revised_elements = generate_bab2_revised_elements(scratch_doc)
    
    # Insert new elements before target_p_before
    for item in revised_elements:
        target_p_before.addprevious(item._element)
        
    # Now remove the old Bab 2 elements from start_idx to end_idx - 1
    # We remove them from elements list
    for i in range(start_idx, end_idx):
        body.remove(elements[i])
        
    print(f"Old Bab 2 elements ({end_idx - start_idx} elements) removed and replaced.")
    
    print(f"Saving updated master docx to: {MASTER_DOCX_LOCAL}")
    doc.save(MASTER_DOCX_LOCAL)
    print("Master local save successful!")
    
    try:
        print(f"Saving updated master docx to OneDrive: {MASTER_DOCX_ONEDRIVE}")
        shutil.copy2(MASTER_DOCX_LOCAL, MASTER_DOCX_ONEDRIVE)
        print("Master OneDrive copy successful!")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

if __name__ == '__main__':
    update_standalone_documents()
    update_master_document()
