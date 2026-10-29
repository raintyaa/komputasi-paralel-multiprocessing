# -*- coding: utf-8 -*-
"""
Script to apply comprehensive revisions to BAB 3 METODOLOGI PENELITIAN based on Claude's audit:
- Fixes experimental design: 21 unique parameter combinations across 27 block conditions (3 replicated).
- Identifies design as partial factorial per scenario (one factor varied per block).
- Fixes cross-referencing in Table 3.3 and text: P=4 in Scenario B corresponds to B3, B7, B11; Scenario C replicates A3, A7, A11 and B3, B7, B11.
- Fixes A/A control description: P=1 is pure serial vs serial to measure system noise floor & position bias; no IPC/pickle overhead.
- Separates execution count: 810 paired iterations (90 A/A control pairs + 720 parallel-serial pairs).
- Completes control variables (spawn, chunksize, boundary halo k=1, halo stripping, uint8 to float64, no core pinning, GC) and uncontrolled factors (thermal dynamics, OS background interrupts, Thread Director P/E-core scheduling).
- Replaces hyperbolic claims ("kedap bias", "validitas kokoh", "menjamin") with objective academic prose ("temporally proximate", "asimetri posisi").
- Removes contradiction in 3.2: eliminates gradient richness praise; confirms data-independent ALU workload.
- Adds specific master image metadata: img_01.png, 4096x4096x3 uint8, SHA-256 f211af0f8cbd2cd9ebb5431d9eabf29f274fc7686f9cfbee544cb18fe6314c6c, center-crop without resampling.
- Removes obsolete sentence about 30 archived image samples.
- Fixes CPU architecture to Golden Cove refresh and Thread Director to hardware feedback mechanism.
- Updates software versions to match real environment: NumPy 2.5.4, OpenCV 5.0.0.93, Matplotlib 3.11.2, SciPy 1.18.1, Psutil 7.2.2, Python 3.14.3.
- Details CPUMonitor implementation (background daemon thread, 20 ms interval, warmup reset call).
- Details pre-warming worker pool with dummy task dispatch pool.map(abs, range(P)).
- Clarifies statistical analysis: right-skewed execution time, near-normal speedup validating CLT t-Student CI (df=29), Kruskal-Wallis for P in {2,4,8} + Scenario C, post-hoc Mann-Whitney with Holm-Bonferroni correction and Hodges-Lehmann effect size.
- Details operational definitions of Amdahl fitting, Karp-Flatt diagnosis, and bit-identical verification (float64 conversion avoiding uint8 wraparound + np.array_equal).
- Adds proper in-text citations for all references and computing libraries according to APA 7th.
- Updates standalone Bab 3 (.docx & .md) and master report (.docx in local & OneDrive).
"""

import sys
import os
import shutil
import docx
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')

MASTER_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
MASTER_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
STANDALONE_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_3_METODOLOGI_PENELITIAN.docx"
STANDALONE_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_3_METODOLOGI_PENELITIAN.docx"
STANDALONE_MD_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_3_METODOLOGI_PENELITIAN.md"
STANDALONE_MD_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_3_METODOLOGI_PENELITIAN.md"

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
    
    tblPr = tbl._element.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top', 'bottom', 'left', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    
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

def create_image_placeholder(doc, placeholder_lines, caption_text):
    """Create a clean placeholder frame and caption paragraph for Figure 3.1."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.rows[0].cells[0].width = Cm(14.0)
    
    tblPr = tbl._element.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top', 'bottom', 'left', 'right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')  # 0.5 pt
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'B0B0B0')
        tblBorders.append(b)
    for side in ['insideH', 'insideV']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    
    cell = tbl.rows[0].cells[0]
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F8F9FA')
    tcPr.append(shd)
    
    set_cell_margins(cell, top=180, bottom=180, left=150, right=150)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.first_line_indent = Cm(0)
    
    for idx, line in enumerate(placeholder_lines):
        if idx > 0:
            p.add_run('\n')
        r = p.add_run(line)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.italic = True
        r.font.color.rgb = RGBColor(100, 100, 100)
        
    p_cap = doc.add_paragraph(style='Normal')
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(6)
    p_cap.paragraph_format.space_after = Pt(6)
    p_cap.paragraph_format.line_spacing = 1.15
    p_cap.paragraph_format.first_line_indent = Cm(0)
    
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(11)
    r_cap.bold = True
    
    return [tbl, p_cap]

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

def build_table_3_1(doc):
    """Table 3.1 Spesifikasi Perangkat Keras dan Kondisi Operasional Pengujian."""
    headers = [
        "Komponen Perangkat Keras",
        "Spesifikasi Teknis",
        "Kondisi Operasional Pengujian"
    ]
    widths_cm = [2.8, 5.6, 5.6]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Prosesor (CPU)", False)],
            [("Intel Core i5-13420H (13th Gen ", False), ("Raptor Lake", True), ("), 8 Inti Fisik: 4 P-Cores (arsitektur ", False), ("Golden Cove refresh", True), (", frekuensi dasar 2,1 GHz / ", False), ("turbo", True), (" 4,6 GHz, SMT 8 ", False), ("threads", True), (") + 4 E-Cores (arsitektur ", False), ("Gracemont", True), (", frekuensi dasar 1,5 GHz / ", False), ("turbo", True), (" 3,4 GHz, 4 ", False), ("threads", True), ("), total kapasitas eksekusi 12 ", False), ("threads", True), (".", False)],
            [("Dijalankan pada skema daya Windows ", False), ("Best Performance", True), ("; laptop terhubung kontinu ke adaptor catu daya listrik AC eksternal; pemantauan suhu awal sebelum pengujian dimulai.", False)]
        ),
        (
            [("Memori ", False), ("Cache", True), (" CPU", False)],
            [("L1: 80 KB per P-Core, 96 KB per E-Core;\nL2: 1,25 MB per P-Core (privat), 2 MB terbagi per kluster empat E-Core;\nL3: 12 MB Intel ", False), ("Smart Cache", True), (" terbagi bersama (", False), ("shared", True), (").", False)],
            [("Berbagi pakai dinamis untuk seluruh proses pekerja; pengujian mengevaluasi efek pelonjakan ", False), ("cache hit", True), (" pada matriks citra 512 × 512 piksel dan degradasi latensi memori pada resolusi 4096 × 4096 piksel.", False)]
        ),
        (
            [("Memori Utama (RAM)", False)],
            [("16 GB DDR5 5200 MT/s ", False), ("Dual-Channel", True)],
            [("Kapasitas memadai untuk menampung seluruh larik citra masukan dan luaran secara simultan tanpa terjadinya penukaran halaman memori (", False), ("memory swapping", True), (") ke media penyimpanan sekunder.", False)]
        ),
        (
            [("Media Penyimpanan", False)],
            [("512 GB SSD M.2 NVMe PCIe 4.0", False)],
            [("Digunakan khusus untuk pembacaan berkas citra awal dan penyimpanan hasil luaran akhir; operasi I/O penyimpanan diisolasi di luar rentang pewaktuan komputasi paralel.", False)]
        ),
        (
            [("Catu Daya Listrik", False)],
            [("Adaptor AC 135 W eksternal", False)],
            [("Terhubung secara kontinu selama eksperimen berlangsung guna mencegah penurunan frekuensi kerja prosesor yang dipicu mekanisme penghematan daya (", False), ("battery power throttling", True), (").", False)]
        ),
        (
            [("Suhu Lingkungan", False)],
            [("Ruang kerja terkondisi (~24 °C)", False)],
            [("Suhu ruangan dijaga stabil guna meminimalkan fluktuasi termal lingkungan selama 810 pasangan eksekusi pengujian.", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = Cm(widths_cm[i])
        set_cell_margins(hdr_cells[i], top=70, bottom=70, left=80, right=80)
        format_cell_text(hdr_cells[i], [(title, False, True)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.5))
        
    for r_idx, (c0, c1, c2) in enumerate(rows_data):
        row_cells = tbl.rows[r_idx + 1].cells
        for col_i, runs in enumerate([c0, c1, c2]):
            row_cells[col_i].width = Cm(widths_cm[col_i])
            set_cell_margins(row_cells[col_i], top=50, bottom=50, left=80, right=80)
            align = WD_ALIGN_PARAGRAPH.CENTER if col_i == 0 else WD_ALIGN_PARAGRAPH.JUSTIFY
            format_cell_text(row_cells[col_i], runs, align=align, font_size=Pt(9.0))
            
    return tbl

def build_table_3_2(doc):
    """Table 3.2 Spesifikasi Perangkat Lunak dan Pustaka Komputasi."""
    headers = [
        "Perangkat Lunak / Pustaka",
        "Versi Rilis",
        "Fungsi dan Peran dalam Penelitian"
    ]
    widths_cm = [3.2, 2.3, 8.5]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Windows 11 Home 64-bit", False)],
            [("Build 22631", False)],
            [("Sistem operasi induk; manajemen penjadwalan proses bekerja sama dengan mekanisme umpan balik perangkat keras (", False), ("hardware feedback mechanism", True), (") Intel Thread Director.", False)]
        ),
        (
            [("Python (CPython)", False)],
            [("3.14.3", False)],
            [("Platform bahasa pemrograman utama untuk implementasi mesin komputasi serial dan paralel (Python Software Foundation, n.d.-b).", False)]
        ),
        (
            [("NumPy", False)],
            [("2.5.4", False)],
            [("Pengelolaan struktur larik multidimensi berbasis ", False), ("row-major", True), (" (C-", False), ("contiguous", True), ("), dekomposisi partisi blok baris horizontal, dan rekonstruksi citra utuh via ", False), ("numpy.vstack", True), (" (Harris et al., 2020).", False)]
        ),
        (
            [("OpenCV (", False), ("opencv-python", True), (")", False)],
            [("5.0.0.93", False)],
            [("Operasi pembacaan dan penulisan berkas citra masukan/luaran (I/O); utas komputasi internal dinonaktifkan secara permanen melalui ", False), ("cv2.setNumThreads(1)", True), (" (Bradski, 2000).", False)]
        ),
        (
            [("Multiprocessing", True)],
            [("Bawaan Python", False)],
            [("Orkestrasi proses paralel independen berbasis metode ", False), ("spawn", True), (", alokasi kolam pekerja (", False), ("Pool", True), ("), transmisi data ", False), ("payload", True), (" via pipa IPC, dan sinkronisasi tugas.", False)]
        ),
        (
            [("Psutil", True)],
            [("7.2.2", False)],
            [("Perekaman persentase beban utilisasi CPU sistem melalui ", False), ("thread daemon", True), (" latar belakang pemantau mandiri selama siklus eksekusi berlangsung.", False)]
        ),
        (
            [("SciPy", False)],
            [("1.18.1", False)],
            [("Eksekusi regresi non-linier kuadrat terkecil untuk pencocokan kurva Hukum Amdahl serta pengujian signifikansi statistik (Kruskal–Wallis dan Mann–Whitney ", False), ("U", True), (") (Virtanen et al., 2020).", False)]
        ),
        (
            [("Matplotlib", False)],
            [("3.11.2", False)],
            [("Pustaka grafis untuk memvisualisasikan kurva performa komparasi waktu, ", False), ("speedup", True), (", efisiensi, dan ", False), ("overhead", True), (" (Hunter, 2007).", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = Cm(widths_cm[i])
        set_cell_margins(hdr_cells[i], top=70, bottom=70, left=80, right=80)
        format_cell_text(hdr_cells[i], [(title, False, True)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.5))
        
    for r_idx, (c0, c1, c2) in enumerate(rows_data):
        row_cells = tbl.rows[r_idx + 1].cells
        for col_i, runs in enumerate([c0, c1, c2]):
            row_cells[col_i].width = Cm(widths_cm[col_i])
            set_cell_margins(row_cells[col_i], top=50, bottom=50, left=80, right=80)
            align = WD_ALIGN_PARAGRAPH.CENTER if col_i <= 1 else WD_ALIGN_PARAGRAPH.JUSTIFY
            format_cell_text(row_cells[col_i], runs, align=align, font_size=Pt(9.0))
            
    return tbl

def build_table_3_3(doc):
    """Table 3.3 Matriks Desain Eksperimen Pengujian Komputasi Paralel."""
    headers = [
        "Blok Skenario",
        "Kode Kondisi",
        "Jenis Filter Spasial",
        "Resolusi Citra (px)",
        "Alokasi Pekerja (P)",
        "Repetisi dan Peran Metodologis"
    ]
    widths_cm = [2.2, 1.4, 2.6, 2.1, 1.4, 4.3]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Skenario A\n(Dimensi Spasial)", False)],
            [("A1 – A4", False)],
            [("Grayscale", False)],
            [("512, 1024,\n2048, 4096", False)],
            [("4", False)],
            [("30 repetisi berpasangan; evaluasi pengaruh volume data matriks pada operasi titik (", False), ("point-wise", True), (") berbeban komputasi ringan.", False)]
        ),
        (
            [("Skenario A\n(Dimensi Spasial)", False)],
            [("A5 – A8", False)],
            [("Gaussian Blur 3×3", False)],
            [("512, 1024,\n2048, 4096", False)],
            [("4", False)],
            [("30 repetisi berpasangan; evaluasi pengaruh volume data pada konvolusi 3 kanal RGB dengan beban transmisi memori besar.", False)]
        ),
        (
            [("Skenario A\n(Dimensi Spasial)", False)],
            [("A9 – A12", False)],
            [("Sobel 3×3", False)],
            [("512, 1024,\n2048, 4096", False)],
            [("4", False)],
            [("30 repetisi berpasangan; evaluasi pengaruh volume data pada konvolusi gradien ganda intensif komputasi matematis.", False)]
        ),
        (
            [("Skenario B\n(Alokasi Pekerja)", False)],
            [("B1 – B4", False)],
            [("Grayscale", False)],
            [("2048 × 2048", False)],
            [("1, 2, 4, 8", False)],
            [("30 repetisi berpasangan; P=1 (B1) sebagai kontrol A/A; P=2,4,8 (B2, B3, B4) untuk pemodelan Hukum Amdahl dan metrik Karp–Flatt.", False)]
        ),
        (
            [("Skenario B\n(Alokasi Pekerja)", False)],
            [("B5 – B8", False)],
            [("Gaussian Blur 3×3", False)],
            [("2048 × 2048", False)],
            [("1, 2, 4, 8", False)],
            [("30 repetisi berpasangan; P=1 (B5) sebagai kontrol A/A; P=2,4,8 (B6, B7, B8) untuk pemodelan Hukum Amdahl dan metrik Karp–Flatt.", False)]
        ),
        (
            [("Skenario B\n(Alokasi Pekerja)", False)],
            [("B9 – B12", False)],
            [("Sobel 3×3", False)],
            [("2048 × 2048", False)],
            [("1, 2, 4, 8", False)],
            [("30 repetisi berpasangan; P=1 (B9) sebagai kontrol A/A; P=2,4,8 (B10, B11, B12) untuk pemodelan Hukum Amdahl dan metrik Karp–Flatt.", False)]
        ),
        (
            [("Skenario C\n(Kompleksitas)", False)],
            [("C1 – C3", False)],
            [("Grayscale, Gaussian, Sobel", False)],
            [("2048 × 2048", False)],
            [("4", False)],
            [("30 repetisi berpasangan; komparasi hierarki kompleksitas filter serta instrumen uji keterulangan terhadap kondisi A3, A7, A11 dan B3, B7, B11.", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = Cm(widths_cm[i])
        set_cell_margins(hdr_cells[i], top=70, bottom=70, left=60, right=60)
        format_cell_text(hdr_cells[i], [(title, False, True)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.0))
        
    for r_idx, (c0, c1, c2, c3, c4, c5) in enumerate(rows_data):
        row_cells = tbl.rows[r_idx + 1].cells
        for col_i, runs in enumerate([c0, c1, c2, c3, c4, c5]):
            row_cells[col_i].width = Cm(widths_cm[col_i])
            set_cell_margins(row_cells[col_i], top=50, bottom=50, left=60, right=60)
            align = WD_ALIGN_PARAGRAPH.JUSTIFY if col_i == 5 else WD_ALIGN_PARAGRAPH.CENTER
            format_cell_text(row_cells[col_i], runs, align=align, font_size=Pt(8.5))
            
    return tbl

def build_table_3_4(doc):
    """Table 3.4 Definisi Operasional Parameter Kinerja yang Diuji."""
    headers = [
        "Parameter Kinerja",
        "Simbol dan Satuan",
        "Alat Ukur / Formulasi",
        "Deskripsi Operasional"
    ]
    widths_cm = [2.8, 2.3, 3.8, 5.1]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Waktu Eksekusi Serial", False)],
            [("T_serial (detik)", True)],
            [("time.perf_counter()", True), (" pada eksekusi serial satu inti", False)],
            [("Durasi pemrosesan citra pada satu inti prosesor tanpa pemanggilan modul ", False), ("multiprocessing", True), ("; bertindak sebagai nilai acuan dasar (", False), ("baseline", True), (").", False)]
        ),
        (
            [("Waktu Eksekusi Paralel", False)],
            [("T_paralel (detik)", True)],
            [("time.perf_counter()", True), (" pada eksekusi paralel", False)],
            [("Durasi eksekusi paralel murni sejak partisi blok baris, transmisi pipa IPC, kalkulasi oleh kolam pekerja, hingga rekonstruksi citra utuh via ", False), ("numpy.vstack", True), (". Pada P=1, merefleksikan eksekusi serial kedua independen.", False)]
        ),
        (
            [("Rasio Percepatan", False)],
            [("S (nirdimensi)", True)],
            [("S = T_serial / T_paralel\n(Persamaan 2.2)", True)],
            [("Kelipatan percepatan komputasi yang dihasilkan sistem paralel dibandingkan eksekusi serial pada pasangan iterasi yang berdekatan.", False)]
        ),
        (
            [("Efisiensi Paralel", False)],
            [("E (%)", True)],
            [("E = (S / P) × 100%\n(Persamaan 2.3, P ∈ {2, 4, 8})", True)],
            [("Persentase pemanfaatan daya komputasi dari setiap unit proses pekerja paralel riil yang dialokasikan (dihitung khusus untuk P > 1).", False)]
        ),
        (
            [("Beban Tambahan Paralel", False)],
            [("T_overhead (detik)", True)],
            [("T_overhead = T_paralel - (T_serial / P)\n(Persamaan 2.4, P ∈ {2, 4, 8})", True)],
            [("Durasi beban penalti sistem akibat latensi komunikasi pipa IPC, serialisasi objek NumPy (", False), ("pickle", True), ("), transmisi baris batas (", False), ("halo", True), ("), dan rekonstruksi matriks (dihitung untuk P > 1).", False)]
        ),
        (
            [("Utilisasi Kapasitas CPU", False)],
            [("CPU (%)", True)],
            [("CPUMonitor via psutil", True)],
            [("Persentase beban kerja prosesor yang dicatat oleh ", False), ("thread daemon", True), (" pemantau latar belakang sebagai indikator tren beban relatif sistem.", False)]
        ),
        (
            [("Integritas Citra Bit-Identik", False)],
            [("Δmax (uint8)", True)],
            [("Δmax = max |I_paralel - I_serial|\nvia float64 & np.array_equal", True)],
            [("Selisih nilai intensitas piksel maksimum antara citra paralel dan serial yang dihitung pada presisi ", False), ("float64", True), (" untuk mencegah ", False), ("wraparound", True), ("; kriteria kelulusan biner pada Δmax = 0.", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = Cm(widths_cm[i])
        set_cell_margins(hdr_cells[i], top=70, bottom=70, left=70, right=70)
        format_cell_text(hdr_cells[i], [(title, False, True)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.5))
        
    for r_idx, (c0, c1, c2, c3) in enumerate(rows_data):
        row_cells = tbl.rows[r_idx + 1].cells
        for col_i, runs in enumerate([c0, c1, c2, c3]):
            row_cells[col_i].width = Cm(widths_cm[col_i])
            set_cell_margins(row_cells[col_i], top=50, bottom=50, left=70, right=70)
            align = WD_ALIGN_PARAGRAPH.CENTER if col_i <= 1 else WD_ALIGN_PARAGRAPH.JUSTIFY
            format_cell_text(row_cells[col_i], runs, align=align, font_size=Pt(8.5))
            
    return tbl

REVISED_REFERENCES_BAB3 = [
    ("Aesthetic-4K Dataset. (2025). High-resolution aesthetic photographic image benchmark under CC-BY 4.0. Open Repository.", [
        ("Aesthetic-4K Dataset. (2025). ", False),
        ("High-resolution aesthetic photographic image benchmark under CC-BY 4.0", True),
        (". Open Repository.", False)
    ]),
    ("Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", [
        ("Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In ", False),
        ("Proceedings of the April 18–20, 1967, Spring Joint Computer Conference", True),
        (" (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", False)
    ]),
    ("Bradski, G. (2000). The OpenCV Library. Dr. Dobb's Journal of Software Tools, 25(11), 120–125.", [
        ("Bradski, G. (2000). The OpenCV Library. ", False),
        ("Dr. Dobb's Journal of Software Tools", True),
        (", 25(11), 120–125.", False)
    ]),
    ("Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A., del Río, J. F., Wiebe, M., Peterson, P., … Oliphant, T. E. (2020). Array programming with NumPy. Nature, 585(7825), 357–362. https://doi.org/10.1038/s41586-020-2649-2", [
        ("Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A., del Río, J. F., Wiebe, M., Peterson, P., … Oliphant, T. E. (2020). Array programming with NumPy. ", False),
        ("Nature", True),
        (", 585(7825), 357–362. https://doi.org/10.1038/s41586-020-2649-2", False)
    ]),
    ("Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90–95. https://doi.org/10.1109/MCSE.2007.55", [
        ("Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. ", False),
        ("Computing in Science & Engineering", True),
        (", 9(3), 90–95. https://doi.org/10.1109/MCSE.2007.55", False)
    ]),
    ("Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.", [
        ("Intel Corporation. (2023). ", False),
        ("13th Generation Intel Core processor family datasheet: Volume 1 of 2", True),
        (". Intel Corporation.", False)
    ]),
    ("International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.", [
        ("International Telecommunication Union. (2011). ", False),
        ("Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios", True),
        (" (Recommendation ITU-R BT.601-7). ITU.", False)
    ]),
    ("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614", [
        ("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. ", False),
        ("Communications of the ACM", True),
        (", 33(5), 539–543. https://doi.org/10.1145/78607.78614", False)
    ]),
    ("Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.", [
        ("Pacheco, P. S., & Malensek, M. (2022). ", False),
        ("An introduction to parallel programming", True),
        (" (2nd ed.). Morgan Kaufmann.", False)
    ]),
    ("Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", [
        ("Python Software Foundation. (n.d.-a). ", False),
        ("Global interpreter lock", True),
        (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", False)
    ]),
    ("Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", [
        ("Python Software Foundation. (n.d.-b). ", False),
        ("multiprocessing — Process-based parallelism", True),
        (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", False)
    ]),
    ("Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.", [
        ("Tanenbaum, A. S., & Bos, H. (2022). ", False),
        ("Modern operating systems", True),
        (" (5th ed.). Pearson.", False)
    ]),
    ("Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., … SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. Nature Methods, 17(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2", [
        ("Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., … SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. ", False),
        ("Nature Methods", True),
        (", 17(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2", False)
    ])
]

def generate_bab3_revised_elements(doc):
    """Generate all document elements (paragraphs, tables, headings) for revised Bab 3."""
    elements = []
    
    # BAB 3 Title
    p_title = create_heading(doc, "BAB 3 METODOLOGI PENELITIAN", level=1, space_before=18, space_after=12)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elements.append(p_title)
    
    # 3.1 Tahapan Penelitian
    elements.append(create_heading(doc, "3.1 Tahapan Penelitian", level=2))
    
    elements.append(create_para(doc, [
        ("Penelitian ini dilaksanakan melalui enam tahapan terstruktur guna memastikan proses evaluasi komparasi kinerja komputasi paralel dan serial dapat terukur secara objektif, terkendali, dan dapat direplikasi (", False),
        ("reproducible", True),
        ("). Tahapan penelitian tersebut mencakup:", False)
    ]))
    
    stages = [
        [("Studi literatur: ", True), ("Mengkaji teori komputasi paralel (", False), ("data parallelism", True), (") (Pacheco & Malensek, 2022), manajemen memori larik NumPy berbasis baris (", False), ("row-major order", True), (" / C-", False), ("contiguous", True), (") (Harris et al., 2020), arsitektur konkurensi modul Python ", False), ("multiprocessing", True), (", batasan ", False), ("Global Interpreter Lock", True), (" (CPython GIL) (Python Software Foundation, n.d.-a), arsitektur prosesor hibrida heterogen (Intel Corporation, 2023; Tanenbaum & Bos, 2022), serta formulasi matematis algoritma filter spasial citra (Grayscale ITU-R BT.601, Gaussian Blur 3×3, dan Sobel 3×3).", False)],
        [("Perancangan dan pengkodean algoritma: ", True), ("Mengembangkan dua varian sistem komputasi pengujian, yaitu skrip serial satu inti prosesor sebagai acuan pembanding (", False), ("baseline", True), (") dan skrip paralel yang mengintegrasikan pemotongan blok baris horizontal dengan penambahan baris batas (", False), ("boundary halo", True), ("), distribusi tugas via ", False), ("multiprocessing.Pool", True), (", pemangkasan baris batas (", False), ("halo stripping", True), ("), dan rekonstruksi citra utuh melalui ", False), ("numpy.vstack", True), (".", False)],
        [("Pengumpulan dan standardisasi data citra master: ", True), ("Menyiapkan citra acuan master beresolusi tinggi 4K (4096 × 4096 piksel) berkas ", False), ("img_01.png", True), (" dengan kode biner SHA-256 ", False), ("f211af0f8cbd2cd9ebb5431d9eabf29f274fc7686f9cfbee544cb18fe6314c6c", True), (" dari repositori terbuka Aesthetic-4K (Aesthetic-4K Dataset, 2025) berlisensi ", False), ("Creative Commons Attribution 4.0 International", True), (" (CC-BY 4.0), yang dipotong secara terpusat (", False), ("center-crop", True), (") tanpa ", False), ("resampling", True), (" ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.", False)],
        [("Eksekusi eksperimen terkontrol: ", True), ("Menjalankan pengujian kinerja pada lingkungan sistem operasi terkendali tanpa interferensi aplikasi latar belakang non-esensial. Sebanyak 810 pasangan perlakuan dieksekusi secara berselang-seling (", False), ("interleaved execution", True), (") antara pengukuran serial dan paralel (terdiri atas 90 pasangan kontrol A/A dan 720 pasangan komparasi paralel-serial) guna meredam fluktuasi termal dan beban penjadwalan sistem operasi.", False)],
        [("Pencatatan parameter kinerja: ", True), ("Merekam durasi waktu komputasi menggunakan fungsi pewaktu presisi tinggi ", False), ("time.perf_counter()", True), (", memantau persentase beban CPU melalui ", False), ("thread daemon", True), (" latar belakang modul ", False), ("psutil", True), (", serta menghitung metrik rasio percepatan (", False), ("speedup", True), (" S), efisiensi paralel (E), dan beban tambahan (", False), ("overhead", True), (") paralel (T_overhead) ke dalam berkas log telemetri CSV.", False)],
        [("Analisis skalabilitas dan pencocokan model: ", True), ("Menganalisis karakteristik skalabilitas melalui statistik non-parametrik deskriptif (median dan IQR), mencocokkan kurva percepatan empiris terhadap batas teoretis Hukum Amdahl (Amdahl, 1967), mengevaluasi fraksi serial efektif melalui metrik Karp–Flatt (Karp & Flatt, 1990), serta memvalidasi kebenaran numerik luaran melalui verifikasi bit-identik (Δmax = 0).", False)]
    ]
    for stg in stages:
        elements.append(create_para(doc, stg, style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Bagan alir pelaksanaan tahapan penelitian secara menyeluruh disajikan pada Gambar 3.1. Bagan alir ini merangkum urutan logis dari keenam tahapan penelitian, mulai dari inisialisasi studi pustaka dan penyiapan data citra master, pelaksanaan pengujian berulang 30 kali secara berselang-seling, verifikasi bit-identik dengan percabangan koreksi algoritma, pencatatan telemetri kinerja, hingga analisis kuantitatif data dan pemodelan skalabilitas.", False)
    ]))
    
    # Placeholder Gambar 3.1
    p_img_items = create_image_placeholder(
        doc,
        [
            "[Area Gambar 3.1: Diagram Alir Tahapan Penelitian]",
            "(Diagram alir sedang dalam proses penyempurnaan format visual beresolusi tinggi 300 DPI untuk disematkan pada area ini)"
        ],
        "Gambar 3.1 Diagram Alir Tahapan Penelitian"
    )
    elements.extend(p_img_items)
    
    # 3.2 Pengumpulan dan Standardisasi Data Citra Master
    elements.append(create_heading(doc, "3.2 Pengumpulan dan Standardisasi Data Citra Master", level=2))
    
    elements.append(create_para(doc, [
        ("Data citra yang digunakan dalam penelitian ini bersumber dari repositori fotografi terbuka beresolusi tinggi Aesthetic-4K (Aesthetic-4K Dataset, 2025) yang didistribusikan di bawah lisensi resmi ", False),
        ("Creative Commons Attribution 4.0 International", True),
        (" (CC-BY 4.0). Citra master yang dipilih adalah berkas ", False),
        ("img_01.png", True),
        (" berformat asli RGB 24-bit tanpa kompresi (", False),
        ("uncompressed PNG", True),
        (") dengan dimensi asli 4096 × 4096 piksel, bebas dari artefak distorsi kompresi ", False),
        ("lossy", True),
        (" JPEG, serta diverifikasi melalui nilai ", False),
        ("hash", True),
        (" SHA-256: ", False),
        ("f211af0f8cbd2cd9ebb5431d9eabf29f274fc7686f9cfbee544cb18fe6314c6c", True),
        (" guna mendukung keterulangan (", False),
        ("reproducibility", True),
        (") data masukan.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Untuk menghasilkan variasi dimensi data yang seragam dan konsisten secara proporsi visual, citra master 4K (4096 × 4096 piksel) diproses melalui pemotongan terpusat (", False),
        ("center-crop", True),
        (") tanpa proses ", False),
        ("resampling", True),
        (" atau interpolasi piksel. Pemotongan terpusat dilakukan secara bertingkat dengan rasio penggandaan panjang sisi dua kali lipat pada setiap tingkatan, menghasilkan empat berkas citra masukan berdimensi bujur sangkar, yaitu: 512 × 512 piksel (volume memori mentah sekitar 768 KB), 1024 × 1024 piksel (volume memori mentah sekitar 3 MB), 2048 × 2048 piksel (volume memori mentah sekitar 12 MB), dan 4096 × 4096 piksel (volume memori mentah sekitar 48 MB data RGB tak terkompresi bertipe data ", False),
        ("uint8", True),
        (").", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Dalam evaluasi komputasi paralel visi komputer, terdapat pertimbangan metodologis mendasar mengenai apakah pengujian memerlukan variasi banyak berkas gambar ataukah cukup menggunakan satu citra acuan master yang distandardisasi. Pada penelitian ini, diputuskan secara ilmiah untuk menggunakan satu citra acuan master terstandardisasi berdasarkan karakteristik intrinsik algoritma filter spasial yang dievaluasi. Operasi konvolusi matriks spasial (Gaussian Blur 3×3 dan Sobel 3×3) serta konversi derajat keabuan (Grayscale ITU-R BT.601; International Telecommunication Union, 2011) memiliki karakteristik komputasi yang bebas dari isi visual citra (", False),
        ("data-independent computation", True),
        ("). Pada seluruh algoritma tersebut, setiap piksel diproses melalui rantai instruksi aritmetika perkalian dan penjumlahan koefisien kernel yang seragam tanpa adanya percabangan kondisional (", False),
        ("conditional branching / if-else", True),
        (") yang dipicu oleh variasi nilai intensitas piksel. Akibatnya, beban siklus instruksi ALU prosesor per piksel bernilai konstan, terlepas dari tekstur visual citra yang diproses. Penggunaan satu citra acuan master terstandardisasi mengeliminasi variabilitas tekstur visual antar-berkas sehingga seluruh variabilitas waktu eksekusi yang terukur mencerminkan perilaku sistem komputasi (interferensi penjadwalan OS, latensi komunikasi pipa IPC antar-proses, dan dinamika arsitektur inti hibrida). Sebagai batasan eksperimental, kesimpulan penelitian ini berlaku spesifik untuk jenis filter spasial dengan beban kerja bebas isi, rentang resolusi hingga 4K, dan platform perangkat keras yang dievaluasi.", False)
    ]))
    
    # 3.3 Alat dan Bahan Penelitian
    elements.append(create_heading(doc, "3.3 Alat dan Bahan Penelitian", level=2))
    
    elements.append(create_para(doc, [
        ("Pelaksanaan eksperimen komputasi paralel memerlukan dukungan perangkat keras, perangkat lunak, dan instrumen pengukuran yang terdefinisi secara terukur untuk mendukung keterulangan (", False),
        ("reproducibility", True),
        (") pengujian.", False)
    ]))
    
    # 3.3.1 Perangkat Keras dan Kondisi Operasional
    elements.append(create_heading(doc, "3.3.1 Perangkat Keras dan Kondisi Operasional", level=3))
    
    elements.append(create_para(doc, [
        ("Eksperimen komputasi paralel dilaksanakan pada satu unit komputer jinjing (laptop) dengan prosesor heterogen modern Intel Core i5-13420H generasi ke-13 (nama sandi ", False),
        ("Raptor Lake", True),
        ("; Intel Corporation, 2023). Prosesor ini memiliki 8 inti fisik (", False),
        ("physical cores", True),
        (") yang terdiri atas 4 Performance-Cores (P-Cores, arsitektur ", False),
        ("Golden Cove refresh", True),
        (") dengan frekuensi dasar 2,1 GHz dan dorongan ", False),
        ("turbo", True),
        (" hingga 4,6 GHz yang mendukung ", False),
        ("Simultaneous Multithreading", True),
        (" (SMT / Hyper-Threading 8 ", False),
        ("threads", True),
        ("), serta 4 Efficient-Cores (E-Cores, arsitektur ", False),
        ("Gracemont", True),
        (") dengan frekuensi dasar 1,5 GHz dan ", False),
        ("turbo", True),
        (" hingga 3,4 GHz tanpa SMT (4 ", False),
        ("threads", True),
        ("), menghasilkan kapasitas pemrosesan total 12 ", False),
        ("threads", True),
        (". Subsistem memori ", False),
        ("cache", True),
        (" prosesor terdiri atas L1 Cache (80 KB per P-Core dan 96 KB per E-Core), L2 Cache (1,25 MB per P-Core privat dan 2 MB terbagi per kluster empat E-Core), serta 12 MB L3 Intel Smart Cache yang terbagi bersama (", False),
        ("shared cache", True),
        (") untuk seluruh inti prosesor.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Sistem didukung oleh memori utama (RAM) berkapasitas 16 GB DDR5 dengan frekuensi transfer 5200 MT/s berkonfigurasi ", False),
        ("dual-channel", True),
        (", serta media penyimpanan Solid State Drive (SSD) M.2 NVMe PCIe 4.0 berkapasitas 512 GB. Untuk menjaga konsistensi kinerja termal dan kelistrikan selama proses pengujian:", False)
    ]))
    
    hw_conds = [
        [("Perangkat keras dihubungkan secara kontinu ke adaptor catu daya listrik AC (pengisi daya 135 W) guna meniadakan penurunan frekuensi kerja prosesor yang dipicu mekanisme penghematan daya baterai (", False), ("battery power throttling", True), (").", False)],
        [("Profil daya pada sistem operasi Windows 11 dikunci pada skema ", False), ("Best Performance", True), (".", False)],
        [("Seluruh pengujian dijalankan di dalam ruangan kerja terkondisi pada suhu kamar stabil (~24 °C) dengan pemantauan suhu awal prosesor sebelum pengujian dimulai.", False)]
    ]
    for hc in hw_conds:
        elements.append(create_para(doc, hc, style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_table_title(doc, "Tabel 3.1 Spesifikasi Perangkat Keras dan Kondisi Operasional Pengujian"))
    elements.append(build_table_3_1(doc))
    
    # 3.3.2 Perangkat Lunak dan Pustaka Komputasi
    elements.append(create_heading(doc, "3.3.2 Perangkat Lunak dan Pustaka Komputasi", level=3))
    
    elements.append(create_para(doc, [
        ("Lingkungan perangkat lunak yang digunakan dalam penelitian ini meliputi sistem operasi Windows 11 Home 64-bit (Build 22631) sebagai platform eksekusi sistem. Bahasa pemrograman yang digunakan adalah Python 3.14.3 (CPython 64-bit; Python Software Foundation, n.d.-b). Komputasi matriks citra bertumpu pada pustaka NumPy versi 2.5.4 (Harris et al., 2020) yang mengelola representasi data larik multidimensi dalam format ", False),
        ("row-major", True),
        (" (C-", False),
        ("contiguous memory layout", True),
        (").", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Pustaka OpenCV versi 5.0.0.93 (Bradski, 2000) digunakan secara terbatas hanya untuk operasi pembacaan dan penyimpanan berkas citra (file I/O). Guna mencegah interferensi akselerasi internal OpenCV yang dapat mengaburkan evaluasi ", False),
        ("multiprocessing", True),
        (", utas komputasi internal OpenCV dinonaktifkan secara eksplisit menggunakan perintah ", False),
        ("cv2.setNumThreads(1)", True),
        (". Modul bawaan Python ", False),
        ("multiprocessing", True),
        (" digunakan sebagai pengendali orkestrasi paralel berbasis kolam proses pekerja (", False),
        ("Pool", True),
        ("). Pustaka ", False),
        ("psutil", True),
        (" versi 7.2.2 digunakan untuk merekam persentase utilisasi CPU sistem. Pustaka SciPy versi 1.18.1 (Virtanen et al., 2020) digunakan untuk melakukan regresi non-linier kuadrat terkecil (", False),
        ("least squares curve fitting", True),
        (") dan uji hipotesis statistik, sedangkan Matplotlib versi 3.11.2 (Hunter, 2007) digunakan untuk menghasilkan grafik komparasi data kinerja.", False)
    ]))
    
    elements.append(create_table_title(doc, "Tabel 3.2 Spesifikasi Perangkat Lunak dan Pustaka Komputasi"))
    elements.append(build_table_3_2(doc))
    
    # 3.3.3 Alat Ukur dan Instrumentasi Kinerja
    elements.append(create_heading(doc, "3.3.3 Alat Ukur dan Instrumentasi Kinerja", level=3))
    
    elements.append(create_para(doc, [
        ("Pengukuran durasi waktu eksekusi komputasi dilakukan menggunakan fungsi pewaktu presisi tinggi berbasis monotonik ", False),
        ("time.perf_counter()", True),
        (" dari pustaka standar Python. Pewaktu ini memiliki resolusi tingkat nanodetik dan bersifat monotonik, artinya nilai pewaktu selalu bertambah secara linier dan tidak pernah terdistorsi oleh penyesuaian jam sistem operasi (", False),
        ("system clock drift", True),
        (") maupun sinkronisasi waktu jaringan (NTP). Pencatatan stempel waktu awal (", False),
        ("start timestamp", True),
        (") dan stempel waktu akhir (", False),
        ("stop timestamp", True),
        (") dilakukan hanya pada blok kalkulasi pemrosesan citra, sehingga waktu pembacaan citra dari penyimpanan (", False),
        ("disk reading", True),
        (") dan waktu penulisan kembali hasil ke media penyimpanan (", False),
        ("disk writing", True),
        (") diisolasi dari pengukuran kinerja komputasi.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Instrumentasi utilisasi kapasitas prosesor dicatat menggunakan kelas pemantau ", False),
        ("CPUMonitor", True),
        (" yang berjalan pada ", False),
        ("thread daemon", True),
        (" latar belakang independen dengan interval percontohan 20 milidetik (0,02 detik). Sebelum siklus komputasi dimulai, dijalankan satu pemanggilan awal ", False),
        ("psutil.cpu_percent(interval=None, percpu=True)", True),
        (" untuk mereset dan memanaskan jendela pencatatan psutil, sehingga sampel yang terkumpul merefleksikan aktivitas prosesor selama eksekusi. Sebagai batasan metodologis, pembacaan nilai ini merefleksikan utilisasi CPU sistem secara keseluruhan dari sudut pandang proses utama, sehingga pada durasi eksekusi yang sangat singkat (di bawah 100 milidetik pada citra resolusi kecil), pembacaan utilisasi CPU cenderung merefleksikan artefak jendela sampel (", False),
        ("sampling window artifact", True),
        (") dan tidak merefleksikan seluruh aktivitas proses pekerja secara instan. Oleh karena itu, data utilisasi CPU diperlakukan sebagai indikator tren beban relatif dan bukan sebagai penentu utama efisiensi komputasi.", False)
    ]))
    
    # 3.4 Desain Eksperimen
    elements.append(create_heading(doc, "3.4 Desain Eksperimen", level=2))
    
    elements.append(create_para(doc, [
        ("Penelitian ini menerapkan desain eksperimen faktorial parsial per skenario (", False),
        ("partial factorial experimental design", True),
        (") dengan variasi satu faktor per blok pengujian untuk menganalisis pengaruh dari variabel ukuran data matriks, alokasi unit proses kerja, dan tingkat kompleksitas algoritma filter spasial. Identifikasi variabel penelitian diklasifikasikan sebagai berikut:\n", False),
        ("1. Variabel bebas (", False),
        ("independent variables", True),
        ("): Resolusi spasial citra masukan (512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel), alokasi jumlah proses pekerja (P ∈ {1, 2, 4, 8}), serta jenis algoritma filter spasial citra (Grayscale ITU-R BT.601, Gaussian Blur 3×3, dan Sobel 3×3).\n", False),
        ("2. Variabel terikat (", False),
        ("dependent variables", True),
        ("): Waktu eksekusi serial (", False),
        ("T_serial", True),
        (") dan waktu eksekusi paralel (", False),
        ("T_paralel", True),
        (") dalam detik, rasio percepatan komputasi (", False),
        ("speedup", True),
        (" S), persentase efisiensi paralel (E), durasi beban tambahan paralel (", False),
        ("parallel overhead", True),
        (" T_overhead) dalam detik, persentase utilisasi kapasitas CPU, serta status integritas keidentikan bit piksel (Δmax).\n", False),
        ("3. Variabel kontrol (", False),
        ("controlled variables", True),
        ("): Citra acuan master tunggal terstandardisasi (Aesthetic-4K ", False),
        ("img_01.png", True),
        (" terpotong terpusat), spesifikasi perangkat keras dan sistem operasi yang seragam, metode peluncuran proses pekerja ", False),
        ("spawn", True),
        (", ukuran partisi tugas ", False),
        ("chunksize", True),
        (" = 1, penanganan baris batas ketetanggaan (", False),
        ("boundary halo", True),
        (" k = 1 dengan pemangkasan ", False),
        ("halo stripping", True),
        (" per pekerja), tipe data representasi matriks (uint8 masukan, konversi float64 untuk operasi konvolusi dan validasi bit-identik), penguncian utas tunggal OpenCV (", False),
        ("cv2.setNumThreads(1)", True),
        ("), ketiadaan pengikatan afinitas inti prosesor (", False),
        ("no core affinity pinning", True),
        ("), serta kondisi ", False),
        ("garbage collector", True),
        (" bawaan interpreter.\n", False),
        ("4. Variabel tak terkendali (", False),
        ("uncontrolled variables", True),
        ("): Fluktuasi termal silikon mikroprosesor, interupsi periodik layanan sistem operasi Windows di latar belakang, serta mekanisme penempatan beban kerja dinamis antara P-Core dan E-Core oleh penjadwal perangkat keras Intel Thread Director.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Ruang lingkup pengujian dibagi ke dalam tiga blok skenario eksperimental yang saling melengkapi:\n", False),
        ("1. Skenario A (Variasi Dimensi Spasial Citra): Alokasi proses pekerja dikunci pada 4 pekerja (P = 4), sedangkan dimensi spasial citra dinaikkan secara bertahap dari 512 × 512 hingga 4096 × 4096 piksel pada ketiga filter. Skenario ini bertujuan memetakan bagaimana pertumbuhan volume data memengaruhi rasio ", False),
        ("speedup", True),
        (" dan efisiensi pada masing-masing karakteristik operasi filter. Skenario ini mencakup 12 sel kondisi perlakuan (A1 s.d. A12).\n", False),
        ("2. Skenario B (Variasi Alokasi Proses Kerja): Dimensi spasial citra dikunci pada resolusi menengah 2048 × 2048 piksel, sedangkan alokasi proses kerja divariasikan untuk P ∈ {1, 2, 4, 8} pada ketiga filter. Alokasi P = 1 dijalankan sebagai instrumen kontrol dasar A/A (", False),
        ("A/A control", True),
        ("). Skenario ini bertujuan memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan mendiagnosis perilaku metrik Karp–Flatt untuk P ∈ {2, 4, 8}. Skenario ini mencakup 12 sel kondisi perlakuan (B1 s.d. B12).\n", False),
        ("3. Skenario C (Variasi Kompleksitas Algoritma Filter): Dijalankan pada resolusi 2048 × 2048 piksel dengan alokasi 4 proses pekerja (P = 4) untuk ketiga jenis filter. Skenario ini bertujuan mengevaluasi interaksi antara beban kalkulasi matematis per piksel terhadap beban tambahan (", False),
        ("overhead", True),
        (") komunikasi IPC, sekaligus bertindak sebagai instrumen uji keterulangan (", False),
        ("repeatability test", True),
        (") terhadap kondisi A3, A7, A11 pada Skenario A dan kondisi B3, B7, B11 pada Skenario B. Skenario ini mencakup 3 sel kondisi perlakuan (C1 s.d. C3).", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Secara keseluruhan, matriks desain eksperimen mencakup 27 sel kondisi blok perlakuan (12 + 12 + 3). Matriks ini merepresentasikan 21 kombinasi parameter fisik unik (faktor filter, resolusi, dan alokasi pekerja), dengan 3 kombinasi perlakuan pada resolusi 2048 × 2048 piksel dan alokasi P = 4 direplikasi pada ketiga blok skenario. Setiap sel kondisi perlakuan diuji sebanyak 30 kali repetisi berpasangan secara berselang-seling, menghasilkan total 810 pasangan eksekusi pengujian eksperimental (mencakup 90 pasangan kontrol A/A serial-ke-serial dan 720 pasangan komparasi paralel-terhadap-serial). Rincian matriks desain eksperimen dan definisi operasional parameter kinerja masing-masing dirangkum pada Tabel 3.3 dan Tabel 3.4.", False)
    ]))
    
    elements.append(create_table_title(doc, "Tabel 3.3 Matriks Desain Eksperimen Pengujian Komputasi Paralel"))
    elements.append(build_table_3_3(doc))
    
    elements.append(create_table_title(doc, "Tabel 3.4 Definisi Operasional Parameter Kinerja yang Diuji"))
    elements.append(build_table_3_4(doc))
    
    # 3.5 Prosedur Pengukuran dan Pengujian
    elements.append(create_heading(doc, "3.5 Prosedur Pengukuran dan Pengujian", level=2))
    
    elements.append(create_para(doc, [
        ("Prosedur pengujian dirancang dengan protokol terstruktur guna mengendalikan variabel pengganggu (", False),
        ("confounding factors", True),
        (") yang bersumber dari mekanisme internal interpreter Python, karakteristik termal prosesor, dan dinamika penjadwalan sistem operasi.", False)
    ]))
    
    # 3.5.1 Protokol Pemanasan Awal (Pre-Warming Worker Pool)
    elements.append(create_heading(doc, "3.5.1 Protokol Pemanasan Awal (Pre-Warming Worker Pool)", level=3))
    
    elements.append(create_para(doc, [
        ("Pada sistem operasi Windows, modul ", False),
        ("multiprocessing", True),
        (" menggunakan metode inisialisasi proses ", False),
        ("spawn", True),
        (" (Python Software Foundation, n.d.-b). Metode ini meluncurkan interpreter Python baru dari awal untuk setiap proses pekerja, yang membutuhkan alokasi memori dan waktu inisialisasi awal (", False),
        ("cold spawn penalty", True),
        (" berkisar ~0,1 hingga ~0,5 detik per proses). Apabila inisialisasi proses pekerja dilakukan di dalam blok pengukuran waktu komputasi, durasi peluncuran proses baru mendominasi dan mendistorsi waktu eksekusi paralel yang sebenarnya. Untuk mengeliminasi distorsi tersebut, diterapkan protokol pemanasan awal (", False),
        ("pre-warming worker pool", True),
        ("). Kolam proses pekerja (", False),
        ("multiprocessing.Pool(processes=P)", True),
        (") diinisialisasi sebelum siklus pengujian dimulai, lalu dikirimkan satu tugas kosong (", False),
        ("dummy task", True),
        (") berupa ", False),
        ("pool.map(abs, range(P))", True),
        (" ke seluruh pekerja. Langkah ini memastikan seluruh interpreter proses pekerja telah aktif penuh (", False),
        ("idle-ready", True),
        (") dan siap menerima distribusi blok data irisan citra. Durasi yang diukur dalam penelitian ini merepresentasikan kinerja kondisi mantap (", False),
        ("steady-state performance", True),
        (") kalkulasi murni, dengan biaya pembuatan kolam pekerja diisolasi di luar pencatatan waktu komputasi.", False)
    ]))
    
    # 3.5.2 Protokol Pengkondisian Termal dan Isolasi Derau Sistem
    elements.append(create_heading(doc, "3.5.2 Protokol Pengkondisian Termal dan Isolasi Derau Sistem", level=3))
    
    elements.append(create_para(doc, [
        ("Eksekusi beban kerja komputasi numerik intensif secara kontinu pada prosesor modern dapat memicu peningkatan akumulasi panas silikon. Peningkatan temperatur yang melampaui ambang batas termal dapat memicu mekanisme proteksi perangkat keras berupa penurunan frekuensi kerja secara otomatis (", False),
        ("thermal throttling", True),
        ("), yang berpotensi menghasilkan variabilitas waktu eksekusi yang semu. Untuk meredam fluktuasi termal, pengujian dijalankan di dalam ruangan kerja terkondisi pada suhu kamar stabil (~24 °C) serta diberikan jeda pendinginan selama 2 detik sebelum pergantian blok perlakuan skenario. Di samping itu, sebelum eksekusi pengujian dimulai, seluruh aplikasi pengguna pihak ketiga non-esensial, koneksi jaringan eksternal, dan layanan pembaruan otomatis sistem operasi dinonaktifkan guna meminimalkan derau interupsi penjadwalan OS (", False),
        ("operating system scheduling jitter", True),
        (").", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Sebagai catatan batasan eksperimental, sistem tidak mencatat sensor suhu mikroprosesor dan frekuensi kerja per iterasi ke dalam berkas telemetri CSV. Terdapat pula sedikit asimetri posisi dalam pasangan pengujian, karena eksekusi serial dijalankan saat sistem dalam kondisi dingin sedangkan eksekusi paralel berjalan segera setelah komputasi serial selesai. Asimetri ini dipertimbangkan secara objektif dalam interpretasi data.", False)
    ]))
    
    # 3.5.3 Pengujian Berselang-seling (Interleaved Execution 30 Repetisi) dan Kontrol A/A
    elements.append(create_heading(doc, "3.5.3 Pengujian Berselang-seling (Interleaved Execution 30 Repetisi) dan Kontrol A/A", level=3))
    
    elements.append(create_para(doc, [
        ("Untuk memastikan data waktu eksekusi serial dan paralel dapat dikomparasikan secara valid dan bebas dari bias tren waktu (", False),
        ("temporal trend bias", True),
        ("), seluruh pengujian dieksekusi melalui protokol 30 kali repetisi terkontrol yang dijalankan secara berselang-seling (", False),
        ("interleaved execution", True),
        ("). Alih-alih mengeksekusi 30 kali pengujian serial secara berurutan lalu dilanjutkan 30 kali pengujian paralel, protokol ini menjalankan pengujian secara bergantian pada setiap repetisi: Iterasi 1 Serial → Iterasi 1 Paralel → Iterasi 2 Serial → Iterasi 2 Paralel … hingga Iterasi 30. Melalui metode berselang-seling ini, setiap pasangan data serial dan paralel berdekatan secara waktu (", False),
        ("temporally proximate", True),
        ("), sehingga dampak fluktuasi termal jangka panjang dan interupsi latar belakang sistem dialami secara seimbang oleh kedua perlakuan.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Pada alokasi satu proses pekerja (P = 1) pada Skenario B dijalankan kontrol A/A, yaitu dua pengukuran serial independen yang disisipkan berselang-seling dengan protokol yang sama. Karena kedua pengukuran mengeksekusi instruksi kode identik pada satu inti prosesor, nilai rasio percepatan S yang diharapkan secara teoretis mendekati 1,00. Simpangan nilai S empiris dari 1,00 dipakai untuk memperkirakan ambang batas derau sistem (", False),
        ("system noise floor", True),
        (") dan menguji ada tidaknya bias posisi (pengukuran pertama versus kedua) dalam setiap pasangan iterasi. Kontrol A/A ini tidak mengukur beban komunikasi pipa IPC maupun serialisasi data.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Sebagai catatan transparansi mengenai batasan eksperimen, urutan eksekusi ketiga blok skenario dijalankan secara sekuensial (Blok A dijalankan pertama, diikuti Blok B, lalu diakhiri oleh Blok C) tanpa pengacakan blok menyeluruh (", False),
        ("global randomized block", True),
        ("). Fenomena pergeseran waktu ", False),
        ("baseline", True),
        (" serial antar-blok (karena Skenario A memiliki durasi ", False),
        ("baseline", True),
        (" serial lebih lambat sekitar +20% hingga +28% dibandingkan Skenario B dan C akibat dinamika termal dan frekuensi awal sistem) dicatat sebagai batasan metodologis yang dianalisis pada Bab 5.", False)
    ]))
    
    # 3.6 Teknik Analisis Data
    elements.append(create_heading(doc, "3.6 Teknik Analisis Data", level=2))
    
    elements.append(create_para(doc, [
        ("Analisis data hasil pengujian bertumpu pada pendekatan statistik deskriptif dan inferensial non-parametrik yang sesuai dengan karakteristik data sistem komputasi riil. Waktu eksekusi sistem komputer umumnya memiliki distribusi yang asimetris dengan kecenderungan menjulur ke kanan (", False),
        ("right-skewed distribution", True),
        ("), akibat munculnya beberapa nilai pencilan (", False),
        ("outliers", True),
        (") yang dipicu oleh interupsi periodik sistem operasi. Mengingat asumsi normalitas baku tidak terpenuhi pada durasi eksekusi, analisis pemusatan data mengutamakan statistik non-parametrik yang tahan terhadap pencilan (", False),
        ("robust statistics", True),
        ("), yaitu nilai median dan rentang antarkuartil (IQR, [", False),
        ("Q25 - Q75", True),
        ("]). Nilai rerata sampel (", False),
        ("x̄", True),
        (") dan simpangan baku sampel (", False),
        ("s", True),
        (") tetap dilaporkan sebagai parameter pelengkap.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Meskipun waktu eksekusi berdistribusi menjulur ke kanan, distribusi rasio percepatan (", False),
        ("speedup", True),
        (" S) memiliki karakteristik yang mendekati simetris. Berdasarkan Teorema Limit Pusat (", False),
        ("Central Limit Theorem / CLT", True),
        (") untuk ukuran sampel n = 30 per kondisi, rerata sampel mendekati normal sehingga selang kepercayaan 95% (", False),
        ("confidence interval", True),
        (") dihitung menggunakan distribusi t-Student dengan derajat kebebasan df = n - 1 = 29 dan nilai kritis t_(29; 0,025) = 2,04523. Independensi observasi diperiksa melalui autokorelasi lag-1 antar-iterasi. Selang kepercayaan 95% dihitung untuk estimasi rerata parameter S, E, dan T_overhead (Persamaan 3.1):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "CI_95% = x̄ ± 2,04523 · (s / √30)",
        "(3.1)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    p_eq1_notes = [
        ("CI_95%", " : Selang kepercayaan 95% (confidence interval) nilai rerata parameter populasi."),
        ("x̄", " : Nilai rerata sampel dari n = 30 repetisi pengujian."),
        ("s", " : Simpangan baku sampel."),
        ("n", " : Ukuran sampel pengujian (n = 30, derajat kebebasan df = n - 1 = 29).")
    ]
    for sym, desc in p_eq1_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Pengujian signifikansi perbedaan performa antar-perlakuan dievaluasi melalui uji hipotesis non-parametrik dengan taraf signifikansi α = 0,05. Uji Kruskal–Wallis digunakan untuk menguji variasi kinerja antar-alokasi proses pekerja paralel murni (P ∈ {2, 4, 8}) pada Skenario B, serta menguji perbedaan kinerja antar-tiga jenis filter pada Skenario C. Apabila uji Kruskal–Wallis menunjukkan perbedaan signifikan (p < 0,05), analisis dilanjutkan dengan uji Mann–Whitney U berpasangan dengan penyesuaian nilai p melalui koreksi Holm-Bonferroni guna mengendalikan laju kesalahan keluarga perlakuan (", False),
        ("family-wise error rate", True),
        ("). Ukuran efek (", False),
        ("effect size", True),
        (") dilaporkan menggunakan estimasi selisih median Hodges–Lehmann untuk melengkapi nilai signifikansi statistik.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Pencocokan model teoretis skalabilitas dilakukan dengan mencocokkan kurva rasio percepatan empiris terhadap formulasi Hukum Amdahl (Amdahl, 1967) menggunakan metode regresi non-linier kuadrat terkecil (", False),
        ("non-linear least squares", True),
        ("). Regresi meminimalkan jumlah kuadrat residu pada rerata percepatan S̄(P) untuk alokasi P ∈ {2, 4, 8} dengan batas parameter fraksi paralel f ∈ [0, 1] per algoritma filter, disertai estimasi selang kepercayaan 95% berbasis ", False),
        ("bootstrap", True),
        (" sebanyak 2.000 ulangan perlakuan. Estimasi tiga titik data untuk satu parameter bebas ini bertindak sebagai uji kelayakan kurva teoretis. Evaluasi dilanjutkan dengan menghitung fraksi serial eksperimental metrik Karp–Flatt (Karp & Flatt, 1990) e = ((1/S̄) - (1/P)) / (1 - (1/P)) untuk P ∈ {2, 4, 8} guna mengevaluasi apakah fraksi serial efektif bernilai relatif tetap ataukah mengalami kenaikan seiring pertambahan unit pekerja.", False)
    ]))
    
    elements.append(create_para(doc, [
        ("Validasi integritas data luaran dilakukan secara deterministik melalui verifikasi bit-identik antara matriks citra hasil pemrosesan paralel terhadap matriks citra hasil pemrosesan serial pada seluruh 720 pasangan komparasi paralel-serial (90 pasangan kontrol A/A bersifat trivial) di luar jendela pengukuran waktu komputasi. Selisih intensitas piksel dihitung dengan mengonversi matriks uint8 ke representasi numerik float64 guna mencegah terjadinya ", False),
        ("integer underflow / wraparound", True),
        (" saat nilai piksel paralel lebih kecil dari serial. Keidentikan bit-per-bit diverifikasi penuh menggunakan fungsi ", False),
        ("numpy.array_equal", True),
        (". Kriteria kelulusan integritas ditetapkan pada nilai selisih absolut maksimum piksel harus bernilai nol di seluruh koordinat spasial (Δmax = max |I_paralel - I_serial| = 0). Apabila ditemukan Δmax > 0, pengujian dinyatakan mengalami kegagalan integritas data. Seluruh angka hasil pengujian aktual dan besaran parameter empiris disimpan dan disajikan secara objektif pada Bab 5.", False)
    ]))
    
    return elements

def update_standalone_documents():
    print("=== Updating Standalone BAB 3 Documents ===")
    doc = docx.Document()
    
    # Set page margins 4-3-3-3 cm
    for s in doc.sections:
        s.top_margin = Cm(4.0)
        s.left_margin = Cm(4.0)
        s.bottom_margin = Cm(3.0)
        s.right_margin = Cm(3.0)
        
    elements = generate_bab3_revised_elements(doc)
    
    # Add References
    elements.append(create_heading(doc, "DAFTAR PUSTAKA (RUJUKAN BAB 3)", level=1, space_before=24, space_after=12))
    
    for plain_text, runs_spec in REVISED_REFERENCES_BAB3:
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
    md_lines = ["# BAB 3 METODOLOGI PENELITIAN\n"]
    doc_for_md = docx.Document(STANDALONE_DOCX_LOCAL)
    for child in doc_for_md.element.body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(child, doc_for_md)
            txt = p.text.strip()
            style = p.style.name
            if style.startswith('Heading 1'):
                if 'METODOLOGI PENELITIAN' in txt:
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
            elif len(tbl.rows) == 1 and len(tbl.columns) == 1:
                # Placeholder frame
                p_text = tbl.rows[0].cells[0].text.strip()
                md_lines.append(f"\n> **{p_text}**\n")
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
    print("\n=== Updating Master Document with Revised Bab 3 ===")
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
            if p.style.name.startswith('Heading 1') and 'METODOLOGI PENELITIAN' in txt:
                start_idx = i
            elif p.style.name.startswith('Heading 1') and 'PERANCANGAN SISTEM' in txt:
                end_idx = i
                break
                
    assert start_idx is not None and end_idx is not None, f"Could not find Bab 3 bounds: {start_idx}, {end_idx}"
    print(f"Found Bab 3 bounds in master docx: start={start_idx}, end={end_idx}")
    
    target_p_before = elements[end_idx]
    
    scratch_doc = docx.Document()
    revised_elements = generate_bab3_revised_elements(scratch_doc)
    
    # Insert new elements before target_p_before
    for item in revised_elements:
        target_p_before.addprevious(item._element)
        
    # Remove old Bab 3 elements from start_idx to end_idx - 1
    for i in range(start_idx, end_idx):
        body.remove(elements[i])
        
    print(f"Old Bab 3 elements ({end_idx - start_idx} elements) removed and replaced.")
    
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
    print("\n>>> ALL BAB 3 REVISIONS APPLIED SUCCESSFULLY! <<<")
