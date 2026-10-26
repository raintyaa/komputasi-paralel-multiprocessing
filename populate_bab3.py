# -*- coding: utf-8 -*-
"""
Script to populate BAB 3 METODOLOGI PENELITIAN in OneDrive and local docx.
Follows:
- academic-paper-builder SOP & UNTAN 2022 guidelines
- Open-format tables (Tabel 3.1, 3.2, 3.3, 3.4)
- Clean placeholder frame for Gambar 3.1 with caption
- Times New Roman, 12 pt body, 1.5 spacing, 1.0 cm first-line indent, justified
- Proper APA 7th citations and PUEBI / EYD V orthography
- Strict zero-leakage of experimental results in Bab 3
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

ONEDRIVE_PATH = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
LOCAL_PATH = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"

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

def create_image_placeholder(doc, placeholder_lines, caption_text):
    """Create a clean placeholder frame and caption paragraph for an unrevised figure."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.rows[0].cells[0].width = Cm(14.0)
    
    # Border light gray single 0.5 pt
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
    
    # Cell background light gray #F8F9FA
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
        
    # Caption paragraph below table
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
    """Build Table 3.1 Spesifikasi Perangkat Keras dan Kondisi Operasional Pengujian."""
    headers = [
        "Komponen Perangkat Keras",
        "Spesifikasi Teknis",
        "Kondisi Operasional Pengujian"
    ]
    widths_cm = [2.8, 5.6, 5.6]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Prosesor (CPU)", False)],
            [("Intel Core i5-13420H (13th Gen ", False), ("Raptor Lake", True), ("), 8 Inti Fisik (4 P-Cores + 4 E-Cores), 12 ", False), ("Threads", True), (", Base Clock P-Core 2,1 GHz / Turbo 4,6 GHz, E-Core 1,5 GHz / Turbo 3,4 GHz", False)],
            [("Dijalankan pada skema daya Windows ", False), ("Best Performance", True), ("; laptop terhubung kontinu ke adaptor listrik AC; pemantauan suhu awal sebelum pengujian.", False)]
        ),
        (
            [("Memori ", False), ("Cache", True), (" CPU", False)],
            [("L1: 80 KB/P-Core, 96 KB/E-Core;\nL2: 1,25 MB/P-Core, 2 MB/E-Core kluster;\nL3: 12 MB Intel ", False), ("Smart Cache", True), (" terbagi bersama (", False), ("shared", True), (")", False)],
            [("Berbagi pakai secara merata untuk seluruh proses pekerja; pengujian mengevaluasi efek pelonjakan ", False), ("cache hit", True), (" pada matriks citra 512 × 512 piksel.", False)]
        ),
        (
            [("Memori Utama (RAM)", False)],
            [("16 GB DDR5 5200 MT/s ", False), ("Dual-Channel", True)],
            [("Kapasitas memadai untuk menampung seluruh larik citra masukan dan luaran secara simultan tanpa ", False), ("swapping", True), (" ke penyimpanan sekunder.", False)]
        ),
        (
            [("Media Penyimpanan", False)],
            [("512 GB SSD M.2 NVMe PCIe 4.0", False)],
            [("Hanya digunakan untuk operasi I/O pembacaan berkas awal dan penyimpanan luaran; diisolasi penuh dari durasi waktu komputasi paralel.", False)]
        ),
        (
            [("Catu Daya Listrik", False)],
            [("Adaptor AC 135 W eksternal", False)],
            [("Terhubung secara kontinu selama pengujian guna mencegah penurunan frekuensi kerja (", False), ("battery power throttling", True), (").", False)]
        ),
        (
            [("Suhu Lingkungan", False)],
            [("Ruang kerja terkondisi (~24 °C)", False)],
            [("Suhu ruangan dijaga stabil guna meminimalkan fluktuasi termal lingkungan selama 810 eksekusi pengujian.", False)]
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
            align = WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.5))
            
    return tbl

def build_table_3_2(doc):
    """Build Table 3.2 Spesifikasi Perangkat Lunak dan Pustaka Komputasi."""
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
            [("Sistem operasi induk; manajemen penjadwalan proses bekerja sama dengan mikrokontroler Intel ", False), ("Thread Director", True), (".", False)]
        ),
        (
            [("Python (CPython)", False)],
            [("3.14.3", False)],
            [("Bahasa pemrograman utama untuk implementasi mesin komputasi serial dan paralel.", False)]
        ),
        (
            [("NumPy", False)],
            [("2.5.4", False)],
            [("Pengelolaan struktur larik multidimensi berbasis ", False), ("row-major (C-contiguous)", True), (", pemotongan blok baris, dan rekonstruksi citra utuh via ", False), ("numpy.vstack", True), (".", False)]
        ),
        (
            [("OpenCV (cv2)", False)],
            [("5.0.0", False)],
            [("Pembacaan dan penulisan berkas citra masukan/luaran (I/O); utas komputasi dikunci satu secara permanen melalui ", False), ("cv2.setNumThreads(1)", True), (".", False)]
        ),
        (
            [("Multiprocessing", True)],
            [("Bawaan Python", False)],
            [("Orkestrasi proses paralel independen, alokasi kolam pekerja (", False), ("Pool", True), ("), dan saluran komunikasi antre/pipa IPC.", False)]
        ),
        (
            [("Psutil", True)],
            [("7.2.2", False)],
            [("Perekaman persentase beban utilisasi CPU sistem pada proses utama selama eksekusi komputasi filter.", False)]
        ),
        (
            [("SciPy", False)],
            [("1.15.2", False)],
            [("Eksekusi regresi non-linier kuadrat terkecil untuk pencocokan Hukum Amdahl dan pengujian signifikansi statistik (Kruskal–Wallis / Mann–Whitney).", False)]
        ),
        (
            [("Matplotlib", False)],
            [("3.10.0", False)],
            [("Pustaka grafis untuk memvisualisasikan kurva performa komparasi waktu, ", False), ("speedup", True), (", efisiensi, dan ", False), ("overhead", True), (".", False)]
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
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 1 else WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.5))
            
    return tbl

def build_table_3_3(doc):
    """Build Table 3.3 Matriks Desain Eksperimen Pengujian Komputasi Paralel."""
    headers = [
        "Blok Skenario",
        "Kode Kondisi",
        "Jenis Filter Spasial",
        "Resolusi Citra (px)",
        "Alokasi Pekerja (P)",
        "Repetisi & Peran Metodologis"
    ]
    widths_cm = [2.3, 1.5, 2.2, 2.0, 1.5, 4.5]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Skenario A\n(Dimensi Citra)", False)],
            [("A1 – A4", False)],
            [("Grayscale", True)],
            [("512, 1024,\n2048, 4096", False)],
            [("4", False)],
            [("30 repetisi selang-seling; evaluasi dampak volume data pada operasi titik berbeban komputasi rendah.", False)]
        ),
        (
            [("Skenario A\n(Dimensi Citra)", False)],
            [("A5 – A8", False)],
            [("Gaussian Blur 3×3", True)],
            [("512, 1024,\n2048, 4096", False)],
            [("4", False)],
            [("30 repetisi selang-seling; evaluasi dampak volume data pada konvolusi 3 kanal RGB dengan transfer memori besar.", False)]
        ),
        (
            [("Skenario A\n(Dimensi Citra)", False)],
            [("A9 – A12", False)],
            [("Sobel 3×3", True)],
            [("512, 1024,\n2048, 4096", False)],
            [("4", False)],
            [("30 repetisi selang-seling; evaluasi dampak volume data pada konvolusi gradien ganda intensif komputasi.", False)]
        ),
        (
            [("Skenario B\n(Alokasi Pekerja)", False)],
            [("B1 – B4", False)],
            [("Grayscale", True)],
            [("2048 × 2048", False)],
            [("1, 2, 4, 8", False)],
            [("30 repetisi selang-seling; P=1 sebagai kontrol A/A; pemodelan kurva Amdahl dan diagnostik metrik Karp–Flatt.", False)]
        ),
        (
            [("Skenario B\n(Alokasi Pekerja)", False)],
            [("B5 – B8", False)],
            [("Gaussian Blur 3×3", True)],
            [("2048 × 2048", False)],
            [("1, 2, 4, 8", False)],
            [("30 repetisi selang-seling; P=1 sebagai kontrol A/A; pemodelan kurva Amdahl dan diagnostik metrik Karp–Flatt.", False)]
        ),
        (
            [("Skenario B\n(Alokasi Pekerja)", False)],
            [("B9 – B12", False)],
            [("Sobel 3×3", True)],
            [("2048 × 2048", False)],
            [("1, 2, 4, 8", False)],
            [("30 repetisi selang-seling; P=1 sebagai kontrol A/A; pemodelan kurva Amdahl dan diagnostik metrik Karp–Flatt.", False)]
        ),
        (
            [("Skenario C\n(Kompleksitas Filter)", False)],
            [("C1 – C3", False)],
            [("Grayscale", True), (", ", False), ("Gaussian Blur 3×3", True), (", ", False), ("Sobel 3×3", True)],
            [("2048 × 2048", False)],
            [("4", False)],
            [("30 repetisi selang-seling; blok terpisah untuk komparasi hierarki kompleksitas dan uji keterulangan (", False), ("repeatability", True), (") terhadap A3 dan B2.", False)]
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
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 3, 4] else WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.5))
            
    return tbl

def build_table_3_4(doc):
    """Build Table 3.4 Definisi Operasional Parameter Kinerja yang Diuji."""
    headers = [
        "Parameter Kinerja",
        "Simbol & Satuan",
        "Alat Ukur / Formulasi",
        "Deskripsi Operasional"
    ]
    widths_cm = [2.8, 2.0, 3.4, 5.8]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("Waktu Eksekusi Serial", False)],
            [("T_serial", True), (" (detik)", False)],
            [("time.perf_counter()", True), (" pada skrip serial murni", False)],
            [("Durasi pemrosesan citra pada satu inti prosesor tanpa pemanggilan modul ", False), ("multiprocessing", True), ("; bertindak sebagai nilai acuan (", False), ("baseline", True), (").", False)]
        ),
        (
            [("Waktu Eksekusi Paralel", False)],
            [("T_paralel", True), (" (detik)", False)],
            [("time.perf_counter()", True), (" pada skrip paralel", False)],
            [("Durasi eksekusi paralel sejak awal partisi blok baris, transmisi pipa IPC, kalkulasi filter oleh kolam pekerja, hingga rekonstruksi citra utuh via ", False), ("vstack", True), (".", False)]
        ),
        (
            [("Rasio Percepatan", False)],
            [("S", True), (" (nirdimensi)", False)],
            [("S = T_serial / T_paralel\n(Persamaan 2.2)", False)],
            [("Kelipatan percepatan komputasi yang dihasilkan oleh sistem paralel dibandingkan eksekusi serial pada kondisi perlakuan yang identik.", False)]
        ),
        (
            [("Efisiensi Paralel", False)],
            [("E", True), (" (%)", False)],
            [("E = (S / P) × 100%\n(Persamaan 2.3)", False)],
            [("Persentase pemanfaatan kapasitas komputasi dari setiap unit proses pekerja yang dialokasikan dalam eksekusi paralel.", False)]
        ),
        (
            [("Beban Tambahan Paralel", False)],
            [("T_overhead", True), (" (detik)", False)],
            [("T_overhead = T_paralel - (T_serial / P)\n(Persamaan 2.4)", False)],
            [("Durasi beban penalti sistem akibat latensi komunikasi pipa IPC, serialisasi objek NumPy (", False), ("pickle", True), ("), replikasi baris batas (", False), ("halo", True), ("), dan rekonstruksi matriks.", False)]
        ),
        (
            [("Utilisasi Kapasitas CPU", False)],
            [("CPU (%)", False)],
            [("psutil.cpu_percent(interval=None)", True)],
            [("Persentase beban kerja prosesor yang dicatat pada proses utama sebagai indikator tren pemanfaatan sistem secara keseluruhan.", False)]
        ),
        (
            [("Integritas Citra Bit-Identik", False)],
            [("Δmax (uint8)", False)],
            [("Δmax = max |I_paralel - I_serial|", False)],
            [("Selisih nilai intensitas piksel maksimum antara citra paralel dan serial; kriteria kelulusan mutlak ditetapkan pada ", False), ("Δmax = 0", True), (".", False)]
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
            align = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 1 else WD_ALIGN_PARAGRAPH.LEFT
            format_cell_text(cell, cell_runs, bold=False, align=align, font_size=Pt(8.5))
            
    return tbl

def populate_bab_3():
    print(f"Loading OneDrive document from: {ONEDRIVE_PATH}")
    doc = docx.Document(ONEDRIVE_PATH)
    
    # Map target headings in Bab 3
    h_map = {}
    for i, p in enumerate(doc.paragraphs):
        txt = p.text.strip()
        if "METODOLOGI PENELITIAN" in txt and p.style.name.startswith("Heading 1"):
            h_map["3.0"] = p
        elif "Tahapan Penelitian" in txt and p.style.name.startswith("Heading 2"):
            h_map["3.1"] = p
        elif "Pengumpulan dan Standardisasi Data Citra Master" in txt and p.style.name.startswith("Heading 2"):
            h_map["3.2"] = p
        elif "Alat dan Bahan Penelitian" in txt and p.style.name.startswith("Heading 2"):
            h_map["3.3"] = p
        elif "Perangkat Keras dan Kondisi Operasional" in txt and p.style.name.startswith("Heading 3"):
            h_map["3.3.1"] = p
        elif "Perangkat Lunak dan Pustaka Komputasi" in txt and p.style.name.startswith("Heading 3"):
            h_map["3.3.2"] = p
        elif "Alat Ukur dan Instrumentasi Kinerja" in txt and p.style.name.startswith("Heading 3"):
            h_map["3.3.3"] = p
        elif "Desain Eksperimen" in txt and p.style.name.startswith("Heading 2"):
            h_map["3.4"] = p
        elif "Prosedur Pengukuran dan Pengujian" in txt and p.style.name.startswith("Heading 2"):
            h_map["3.5"] = p
        elif "Protokol Pemanasan Awal (Pre-Warming Worker Pool)" in txt and p.style.name.startswith("Heading 3"):
            h_map["3.5.1"] = p
        elif "Protokol Jeda Dingin" in txt and p.style.name.startswith("Heading 3"):
            h_map["3.5.2"] = p
            # Ensure proper heading title
            p.text = "Protokol Jeda Dingin (Cool-Down Buffer) dan Isolasi Derau Sistem"
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(12)
            p.runs[0].bold = True
        elif "Pengujian Berselang-seling" in txt and p.style.name.startswith("Heading 3"):
            h_map["3.5.3"] = p
        elif "Teknik Analisis Data" in txt and p.style.name.startswith("Heading 2"):
            h_map["3.6"] = p
        elif "PERANCANGAN SISTEM" in txt and p.style.name.startswith("Heading 1"):
            h_map["4.0"] = p
            
    print(f"Mapped {len(h_map)} headings in Bab 3.")
    assert len(h_map) == 14, f"Expected 14 heading markers, found {len(h_map)}: {list(h_map.keys())}"

    def insert_items_before(target_p, items_list):
        for item in items_list:
            target_p._element.addprevious(item._element)

    # -------------------------------------------------------------
    # SUBBAB 3.1: Tahapan Penelitian
    # -------------------------------------------------------------
    print("Building Subbab 3.1 items...")
    sec_3_1_items = []
    
    p3_1_1 = create_para(doc, [
        ("Penelitian ini dilaksanakan melalui enam tahapan terstruktur guna memastikan proses evaluasi komparasi kinerja komputasi paralel dan serial dapat terukur secara objektif, terkontrol, dan dapat diulang (", False),
        ("reproducible", True),
        ("). Tahapan penelitian tersebut mencakup:\n", False),
        ("1. Studi literatur: Mengkaji teori komputasi paralel (", False),
        ("data parallelism", True),
        ("), mekanisme pengalamatan memori larik NumPy (", False),
        ("row-major order", True),
        ("), arsitektur konkurensi modul Python ", False),
        ("multiprocessing", True),
        (", batasan Global Interpreter Lock (GIL) pada CPython, arsitektur prosesor heterogen modern, serta formulasi matematis algoritma filter spasial citra (", False),
        ("Grayscale", True),
        (", ", False),
        ("Gaussian Blur 3×3", True),
        (", dan ", False),
        ("Sobel 3×3", True),
        (").\n", False),
        ("2. Perancangan dan pengkodean algoritma: Mengembangkan dua varian sistem komputasi pengujian, yaitu skrip serial murni satu inti prosesor sebagai acuan pembanding (", False),
        ("baseline", True),
        (") dan skrip paralel yang mengintegrasikan pemotongan blok baris horizontal dengan distribusi tugas melalui ", False),
        ("multiprocessing.Pool", True),
        (".\n", False),
        ("3. Pengumpulan dan standardisasi data citra master: Menyiapkan citra acuan master beresolusi tinggi 4K (4096 × 4096 piksel) yang bersumber dari repositori fotografi terbuka Aesthetic-4K (Aesthetic-4K Dataset, 2025) berlisensi Creative Commons Attribution 4.0 International (CC-BY 4.0), yang dipotong secara terpusat (", False),
        ("center-crop", True),
        (") tanpa kompresi ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.\n", False),
        ("4. Eksekusi eksperimen terkontrol: Menjalankan pengujian kinerja pada lingkungan sistem operasi terkendali tanpa interferensi aplikasi latar belakang pengguna. Setiap kombinasi perlakuan dieksekusi sebanyak 30 kali repetisi secara berselang-seling (", False),
        ("interleaved execution", True),
        (") antara pengukuran serial dan paralel guna meminimalkan fluktuasi termal dan beban penjadwalan sistem operasi.\n", False),
        ("5. Pencatatan parameter kinerja: Merekam durasi waktu komputasi murni menggunakan fungsi pewaktu presisi tinggi ", False),
        ("time.perf_counter()", True),
        (", memantau persentase beban CPU proses utama via modul ", False),
        ("psutil", True),
        (", serta menghitung metrik rasio percepatan (", False),
        ("speedup", True),
        ("), efisiensi paralel, dan beban tambahan (", False),
        ("overhead", True),
        (") paralel ke dalam berkas log telemetri CSV.\n", False),
        ("6. Analisis skalabilitas dan pencocokan model: Menganalisis karakteristik skalabilitas melalui statistik non-parametrik deskriptif, mencocokkan kurva percepatan empiris terhadap batas teoretis Hukum Amdahl, mendiagnosis hambatan koordinasi paralel menggunakan metrik Karp–Flatt, serta memvalidasi determinisme luaran melalui kriteria verifikasi bit-identik (Δmax = 0).", False)
    ])
    sec_3_1_items.append(p3_1_1)
    
    p3_1_2 = create_para(doc, [
        ("Bagan alir pelaksanaan tahapan penelitian secara menyeluruh disajikan pada Gambar 3.1. Bagan alir ini merangkum urutan logis dari keenam tahapan penelitian, mulai dari inisialisasi studi pustaka dan penyiapan data citra master, pelaksanaan pengujian berulang 30 kali secara berselang-seling, pencatatan telemetri kinerja, hingga analisis kuantitatif dan evaluasi integritas bit-identik.", False)
    ])
    sec_3_1_items.append(p3_1_2)
    
    # Placeholder for Gambar 3.1
    placeholder_g3_1 = create_image_placeholder(doc, [
        "[Area Gambar 3.1: Diagram Alir Tahapan Penelitian]",
        "(Diagram alir dalam proses penyempurnaan format visual beresolusi tinggi 300 DPI untuk disematkan pada area ini)"
    ], "Gambar 3.1 Diagram Alir Tahapan Penelitian")
    sec_3_1_items.extend(placeholder_g3_1)
    
    insert_items_before(h_map["3.2"], sec_3_1_items)

    # -------------------------------------------------------------
    # SUBBAB 3.2: Pengumpulan dan Standardisasi Data Citra Master
    # -------------------------------------------------------------
    print("Building Subbab 3.2 items...")
    sec_3_2_items = []
    
    p3_2_1 = create_para(doc, [
        ("Data citra yang digunakan dalam penelitian ini bersumber dari repositori fotografi terbuka beresolusi tinggi Aesthetic-4K (Aesthetic-4K Dataset, 2025) yang didistribusikan di bawah lisensi resmi Creative Commons Attribution 4.0 International (CC-BY 4.0). Citra master yang dipilih memiliki format asli RGB 24-bit tanpa kompresi (", False),
        ("uncompressed PNG", True),
        (") dengan kualitas visual prima, bebas dari artefak distorsi kompresi ", False),
        ("lossy", True),
        (" JPEG, serta memiliki sebaran gradien intensitas dan tepi spasial yang kaya guna memberikan beban kalkulasi konvolusi yang representatif.", False)
    ])
    sec_3_2_items.append(p3_2_1)
    
    p3_2_2 = create_para(doc, [
        ("Untuk menghasilkan variasi dimensi data yang seragam dan konsisten secara proporsi visual, citra master 4K (4096 × 4096 piksel) diproses melalui pemotongan terpusat (", False),
        ("center-crop", True),
        (") tanpa proses ", False),
        ("resampling", True),
        (" atau interpolasi piksel. Pemotongan terpusat dilakukan secara bertingkat dengan rasio penggandaan panjang sisi dua kali lipat pada setiap tingkatan, menghasilkan empat berkas citra masukan berdimensi bujur sangkar, yaitu: 512 × 512 piksel (volume memori mentah sekitar 768 KB), 1024 × 1024 piksel (volume memori mentah sekitar 3 MB), 2048 × 2048 piksel (volume memori mentah sekitar 12 MB), dan 4096 × 4096 piksel (volume memori mentah sekitar 48 MB data RGB tak terkompresi bertipe data uint8).", False)
    ])
    sec_3_2_items.append(p3_2_2)
    
    p3_2_3 = create_para(doc, [
        ("Dalam evaluasi komputasi paralel visi komputer, terdapat pertimbangan metodologis mendasar terkait pemilihan apakah pengujian memerlukan variasi banyak berkas gambar ataukah cukup menggunakan satu citra acuan master yang distandardisasi. Pada penelitian ini, diputuskan secara ilmiah untuk menggunakan satu citra acuan master terstandardisasi berdasarkan karakteristik intrinsik algoritma filter spasial yang diuji. Operasi konvolusi matriks spasial (Gaussian Blur 3×3 dan Sobel 3×3) serta konversi derajat keabuan (Grayscale ITU-R BT.601) memiliki karakteristik komputasi yang sepenuhnya tidak bergantung pada isi visual citra (", False),
        ("data-independent computation", True),
        ("). Pada seluruh algoritma tersebut, setiap piksel diproses melalui rantai instruksi aritmatika perkalian dan penjumlahan koefisien kernel yang identik tanpa adanya percabangan kondisional (", False),
        ("conditional branching / if-else", True),
        (") yang dipengaruhi oleh nilai intensitas piksel. Dengan demikian, beban siklus instruksi ALU prosesor per piksel bernilai konstan, terlepas dari tekstur visual citra yang diproses. Penggunaan satu citra acuan master terstandardisasi memberikan keunggulan metodologis yang krusial, yaitu mengeliminasi variabilitas tekstur visual antar-berkas sehingga seluruh variabilitas waktu eksekusi yang terukur murni mencerminkan perilaku sistem komputasi (interferensi penjadwalan OS, latensi komunikasi IPC antar-proses, dan dinamika arsitektur inti hibrida). Seluruh 30 sampel citra multiresolusi awal tetap diarsipkan secara lengkap sebagai cadangan dataset.", False)
    ])
    sec_3_2_items.append(p3_2_3)
    
    insert_items_before(h_map["3.3"], sec_3_2_items)

    # -------------------------------------------------------------
    # SUBBAB 3.3: Alat dan Bahan Penelitian (Bridge)
    # -------------------------------------------------------------
    print("Building Subbab 3.3 Bridge items...")
    sec_3_3_items = []
    p3_3_bridge = create_para(doc, [
        ("Pelaksanaan eksperimen komputasi paralel memerlukan dukungan perangkat keras, perangkat lunak, dan instrumen pengukuran yang terdefinisi secara presisi untuk menjamin keterulangan (", False),
        ("reproducibility", True),
        (") pengujian.", False)
    ])
    sec_3_3_items.append(p3_3_bridge)
    insert_items_before(h_map["3.3.1"], sec_3_3_items)

    # -------------------------------------------------------------
    # SUBBAB 3.3.1: Perangkat Keras dan Kondisi Operasional
    # -------------------------------------------------------------
    print("Building Subbab 3.3.1 items...")
    sec_3_3_1_items = []
    
    p3_3_1_1 = create_para(doc, [
        ("Eksperimen komputasi paralel dilaksanakan pada satu unit komputer jinjing (", False),
        ("laptop", True),
        (") dengan spesifikasi prosesor heterogen modern Intel Core i5-13420H generasi ke-13 (nama sandi ", False),
        ("Raptor Lake", True),
        ("). Prosesor ini memiliki 8 inti fisik (", False),
        ("physical cores", True),
        (") yang terdiri atas 4 ", False),
        ("Performance-Cores", True),
        (" (P-Cores, arsitektur Raptor Cove) dengan frekuensi dasar 2,1 GHz dan dorongan turbo hingga 4,6 GHz yang mendukung ", False),
        ("Simultaneous Multithreading", True),
        (" (SMT / Hyper-Threading 8 ", False),
        ("threads", True),
        ("), serta 4 ", False),
        ("Efficient-Cores", True),
        (" (E-Cores, arsitektur Gracemont) dengan frekuensi dasar 1,5 GHz dan turbo hingga 3,4 GHz tanpa SMT (4 ", False),
        ("threads", True),
        ("), menghasilkan kapasitas pemrosesan total 12 ", False),
        ("threads", True),
        (". Subsistem memori ", False),
        ("cache", True),
        (" prosesor terdiri atas L1 Cache (80 KB per P-Core dan 96 KB per E-Core), L2 Cache (1,25 MB per P-Core dan 2 MB terbagi per kluster empat E-Core), serta 12 MB L3 Intel Smart Cache yang terbagi secara bersama (", False),
        ("shared cache", True),
        (") untuk seluruh inti prosesor.", False)
    ])
    sec_3_3_1_items.append(p3_3_1_1)
    
    p3_3_1_2 = create_para(doc, [
        ("Sistem didukung oleh memori utama (RAM) berkapasitas 16 GB DDR5 dengan frekuensi transfer 5200 MT/s berkonfigurasi ", False),
        ("dual-channel", True),
        (", serta media penyimpanan berkecepatan tinggi Solid State Drive (SSD) M.2 NVMe PCIe 4.0 berkapasitas 512 GB. Untuk menjaga konsistensi kinerja termal dan kelistrikan selama proses pengujian:\n", False),
        ("1. Perangkat keras dihubungkan secara kontinu ke adaptor catu daya listrik AC (pengisi daya 135 W) guna meniadakan penurunan frekuensi kerja prosesor yang dipicu oleh mekanisme penghematan daya baterai (", False),
        ("battery power throttling", True),
        (").\n", False),
        ("2. Profil daya pada sistem operasi Windows 11 dikunci secara permanen pada skema ", False),
        ("Best Performance", True),
        (".\n", False),
        ("3. Seluruh pengujian dijalankan di dalam ruangan kerja terkondisi pada suhu kamar stabil (~24 °C) dengan pemantauan suhu awal prosesor sebelum pengujian dimulai.", False)
    ])
    sec_3_3_1_items.append(p3_3_1_2)
    
    t3_1_title = create_table_title(doc, "Tabel 3.1 Spesifikasi Perangkat Keras dan Kondisi Operasional Pengujian")
    sec_3_3_1_items.append(t3_1_title)
    t3_1_tbl = build_table_3_1(doc)
    sec_3_3_1_items.append(t3_1_tbl)
    
    insert_items_before(h_map["3.3.2"], sec_3_3_1_items)

    # -------------------------------------------------------------
    # SUBBAB 3.3.2: Perangkat Lunak dan Pustaka Komputasi
    # -------------------------------------------------------------
    print("Building Subbab 3.3.2 items...")
    sec_3_3_2_items = []
    
    p3_3_2_1 = create_para(doc, [
        ("Lingkungan perangkat lunak yang digunakan dalam penelitian ini meliputi sistem operasi Windows 11 Home 64-bit (Build 22631) sebagai platform eksekusi sistem. Bahasa pemrograman yang digunakan adalah Python 3.14.3 (rilis resmi CPython 64-bit dari Python Software Foundation). Komputasi matriks citra bertumpu pada pustaka NumPy versi 2.5.4 yang mengelola representasi data larik multidimensi dalam format ", False),
        ("row-major", True),
        (" (", False),
        ("C-contiguous memory layout", True),
        (").", False)
    ])
    sec_3_3_2_items.append(p3_3_2_1)
    
    p3_3_2_2 = create_para(doc, [
        ("Pustaka OpenCV versi 5.0.0 digunakan secara terbatas hanya untuk operasi pembacaan dan penyimpanan berkas citra (", False),
        ("file I/O", True),
        ("). Guna mencegah interferensi akselerasi internal OpenCV yang dapat mengaburkan evaluasi multiprocessing murni, utas komputasi internal OpenCV dinonaktifkan secara eksplisit menggunakan perintah ", False),
        ("cv2.setNumThreads(1)", True),
        (". Modul bawaan Python ", False),
        ("multiprocessing", True),
        (" digunakan sebagai pengendali orkestrasi paralel berbasis kolam proses pekerja (", False),
        ("Pool", True),
        ("). Pustaka ", False),
        ("psutil", True),
        (" versi 7.2.2 digunakan untuk merekam persentase utilisasi CPU sistem. Pustaka SciPy versi 1.15.2 digunakan untuk melakukan regresi non-linier kuadrat terkecil (", False),
        ("least squares curve fitting", True),
        (") dan uji hipotesis statistik, sedangkan Matplotlib versi 3.10.0 digunakan untuk menghasilkan grafik komparasi data kinerja.", False)
    ])
    sec_3_3_2_items.append(p3_3_2_2)
    
    t3_2_title = create_table_title(doc, "Tabel 3.2 Spesifikasi Perangkat Lunak dan Pustaka Komputasi")
    sec_3_3_2_items.append(t3_2_title)
    t3_2_tbl = build_table_3_2(doc)
    sec_3_3_2_items.append(t3_2_tbl)
    
    insert_items_before(h_map["3.3.3"], sec_3_3_2_items)

    # -------------------------------------------------------------
    # SUBBAB 3.3.3: Alat Ukur dan Instrumentasi Kinerja
    # -------------------------------------------------------------
    print("Building Subbab 3.3.3 items...")
    sec_3_3_3_items = []
    
    p3_3_3_1 = create_para(doc, [
        ("Pengukuran durasi waktu eksekusi komputasi dilakukan menggunakan fungsi pewaktu presisi tinggi berbasis monotonik ", False),
        ("time.perf_counter()", True),
        (" dari modul pustaka standar Python. Pewaktu ini memiliki resolusi tingkat nanodetik dan bersifat monotonik, artinya nilai pewaktu selalu bertambah secara linier dan tidak pernah terdistorsi oleh penyesuaian jam sistem operasi (", False),
        ("system clock drift", True),
        (") maupun sinkronisasi waktu jaringan (NTP). Pencatatan stempel waktu awal (", False),
        ("start timestamp", True),
        (") dan stempel waktu akhir (", False),
        ("stop timestamp", True),
        (") dilakukan secara ketat hanya pada blok kalkulasi pemrosesan citra murni, sehingga waktu pembacaan citra dari penyimpanan (", False),
        ("disk reading", True),
        (") dan waktu penulisan kembali hasil ke media penyimpanan (", False),
        ("disk writing", True),
        (") diisolasi sepenuhnya dari pengukuran kinerja komputasi.", False)
    ])
    sec_3_3_3_items.append(p3_3_3_1)
    
    p3_3_3_2 = create_para(doc, [
        ("Instrumentasi utilisasi kapasitas prosesor dicatat menggunakan modul ", False),
        ("psutil.cpu_percent(interval=None)", True),
        (" yang dipanggil pada proses utama. Perlu dicatat sebagai batasan metodologis bahwa pembacaan nilai ini merefleksikan utilisasi CPU sistem secara keseluruhan dari sudut pandang proses utama, di mana pada durasi eksekusi yang sangat singkat (di bawah 100 milidetik pada citra resolusi kecil), pembacaan utilisasi CPU cenderung merefleksikan artefak jendela sampel (", False),
        ("sampling window artifact", True),
        (") dan tidak merefleksikan seluruh aktivitas proses pekerja secara instan. Oleh karena itu, data utilisasi CPU diperlakukan sebagai indikator tren beban relatif dan bukan sebagai penentu utama efisiensi komputasi.", False)
    ])
    sec_3_3_3_items.append(p3_3_3_2)
    
    insert_items_before(h_map["3.4"], sec_3_3_3_items)

    # -------------------------------------------------------------
    # SUBBAB 3.4: Desain Eksperimen
    # -------------------------------------------------------------
    print("Building Subbab 3.4 items...")
    sec_3_4_items = []
    
    p3_4_1 = create_para(doc, [
        ("Penelitian ini menerapkan desain eksperimen faktorial terkontrol (", False),
        ("controlled factorial experimental design", True),
        (") untuk menganalisis pengaruh simultan dari variabel ukuran data matriks, alokasi unit proses kerja, dan tingkat kompleksitas algoritma filter spasial. Identifikasi variabel penelitian diklasifikasikan sebagai berikut:\n", False),
        ("1. Variabel bebas (", False),
        ("independent variables", True),
        ("): Resolusi spasial citra masukan (512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel), alokasi jumlah proses pekerja (", False),
        ("P", True),
        (" = 1, 2, 4, dan 8 proses pekerja), serta jenis algoritma filter spasial citra (Grayscale ITU-R BT.601, Gaussian Blur 3×3, dan Sobel 3×3).\n", False),
        ("2. Variabel terikat (", False),
        ("dependent variables", True),
        ("): Waktu eksekusi serial (", False),
        ("T_serial", True),
        (") dan waktu eksekusi paralel (", False),
        ("T_paralel", True),
        (") dalam detik, rasio percepatan komputasi (", False),
        ("speedup S", True),
        ("), persentase efisiensi paralel (", False),
        ("E", True),
        ("), durasi beban tambahan paralel (", False),
        ("parallel overhead T_overhead", True),
        (") dalam detik, dan persentase utilisasi kapasitas CPU.\n", False),
        ("3. Variabel kontrol (", False),
        ("controlled variables", True),
        ("): Citra acuan master tunggal terstandardisasi (Aesthetic-4K terpotong terpusat), spesifikasi perangkat keras dan sistem operasi yang seragam, penguncian utas tunggal OpenCV (", False),
        ("cv2.setNumThreads(1)", True),
        ("), serta eliminasi proses latar belakang pengguna non-esensial.", False)
    ])
    sec_3_4_items.append(p3_4_1)
    
    p3_4_2 = create_para(doc, [
        ("Ruang lingkup pengujian dibagi ke dalam tiga blok skenario eksperimental yang saling melengkapi:\n", False),
        ("1. Skenario A (Variasi Dimensi Citra): Alokasi proses pekerja dikunci pada 4 pekerja (", False),
        ("P", True),
        (" = 4), sedangkan dimensi spasial citra dinaikkan secara bertahap dari 512 × 512 hingga 4096 × 4096 piksel pada ketiga filter. Skenario ini bertujuan memetakan bagaimana pertumbuhan volume data memengaruhi rasio ", False),
        ("speedup", True),
        (" dan efisiensi pada masing-masing karakteristik operasi filter. Skenario ini mencakup 12 kondisi pengujian (A1 s.d. A12).\n", False),
        ("2. Skenario B (Variasi Alokasi Proses Kerja): Dimensi spasial citra dikunci pada resolusi menengah 2048 × 2048 piksel, sedangkan alokasi proses kerja divariasikan untuk ", False),
        ("P ∈ {1, 2, 4, 8}", True),
        (" pada ketiga filter. Alokasi ", False),
        ("P = 1", True),
        (" dijalankan sebagai instrumen kontrol dasar A/A (", False),
        ("A/A control", True),
        ("). Skenario ini bertujuan memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan mendiagnosis perilaku metrik Karp–Flatt seiring penambahan unit kerja. Skenario ini mencakup 12 kondisi pengujian (B1 s.d. B12).\n", False),
        ("3. Skenario C (Variasi Kompleksitas Algoritma Filter): Dijalankan sebagai blok pengujian terpisah pada resolusi 2048 × 2048 piksel dengan alokasi 4 proses pekerja (", False),
        ("P", True),
        (" = 4) untuk ketiga jenis filter. Skenario ini bertujuan mengevaluasi interaksi antara beban kalkulasi matematis per piksel terhadap beban tambahan (", False),
        ("overhead", True),
        (") komunikasi IPC, sekaligus bertindak sebagai instrumen uji keterulangan (", False),
        ("repeatability test", True),
        (") terhadap titik uji A3 dan B2. Skenario ini mencakup 3 kondisi pengujian (C1 s.d. C3).", False)
    ])
    sec_3_4_items.append(p3_4_2)
    
    p3_4_3 = create_para(doc, [
        ("Secara keseluruhan, matriks desain eksperimen mencakup 27 kombinasi kondisi pengujian unik (12 + 12 + 3). Setiap kondisi perlakuan diuji sebanyak 30 kali repetisi terkontrol secara berselang-seling, menghasilkan total 810 eksekusi pengujian eksperimental. Rincian matriks desain eksperimen dan definisi operasional parameter kinerja masing-masing dirangkum pada Tabel 3.3 dan Tabel 3.4.", False)
    ])
    sec_3_4_items.append(p3_4_3)
    
    t3_3_title = create_table_title(doc, "Tabel 3.3 Matriks Desain Eksperimen Pengujian Komputasi Paralel")
    sec_3_4_items.append(t3_3_title)
    t3_3_tbl = build_table_3_3(doc)
    sec_3_4_items.append(t3_3_tbl)
    
    t3_4_title = create_table_title(doc, "Tabel 3.4 Definisi Operasional Parameter Kinerja yang Diuji")
    sec_3_4_items.append(t3_4_title)
    t3_4_tbl = build_table_3_4(doc)
    sec_3_4_items.append(t3_4_tbl)
    
    insert_items_before(h_map["3.5"], sec_3_4_items)

    # -------------------------------------------------------------
    # SUBBAB 3.5: Prosedur Pengukuran dan Pengujian (Bridge)
    # -------------------------------------------------------------
    print("Building Subbab 3.5 Bridge items...")
    sec_3_5_items = []
    p3_5_bridge = create_para(doc, [
        ("Prosedur pengujian dirancang dengan protokol ketat guna mengisolasi variabel pengganggu (", False),
        ("confounding factors", True),
        (") yang bersumber dari mekanisme internal interpreter Python, karakteristik termal prosesor, dan dinamika penjadwalan sistem operasi.", False)
    ])
    sec_3_5_items.append(p3_5_bridge)
    insert_items_before(h_map["3.5.1"], sec_3_5_items)

    # -------------------------------------------------------------
    # SUBBAB 3.5.1: Protokol Pemanasan Awal (Pre-Warming Worker Pool)
    # -------------------------------------------------------------
    print("Building Subbab 3.5.1 items...")
    sec_3_5_1_items = []
    p3_5_1_1 = create_para(doc, [
        ("Pada sistem operasi Windows, modul ", False),
        ("multiprocessing", True),
        (" menggunakan metode inisialisasi proses ", False),
        ("spawn", True),
        (" (Python Software Foundation, n.d.-b). Metode ini meluncurkan interpreter Python baru dari awal untuk setiap proses pekerja, yang membutuhkan alokasi memori dan waktu inisialisasi yang signifikan (~0,1 hingga ~0,5 detik per proses). Apabila inisialisasi proses pekerja dilakukan di dalam blok pengukuran waktu komputasi, durasi peluncuran proses baru (", False),
        ("cold spawn penalty", True),
        (") mendominasi dan mendistorsi waktu eksekusi paralel yang sebenarnya. Untuk mengeliminasi distorsi tersebut, dirancang protokol pemanasan awal (", False),
        ("pre-warming worker pool", True),
        ("). Kolam proses pekerja (", False),
        ("multiprocessing.Pool(processes=P)", True),
        (") diinisialisasi dan distabilkan satu kali sebelum siklus pengujian dimulai. Stempel waktu komputasi paralel baru dicatat setelah seluruh proses pekerja berada dalam status aktif (", False),
        ("idle-ready", True),
        (") dan siap menerima distribusi blok data irisan citra.", False)
    ])
    sec_3_5_1_items.append(p3_5_1_1)
    insert_items_before(h_map["3.5.2"], sec_3_5_1_items)

    # -------------------------------------------------------------
    # SUBBAB 3.5.2: Protokol Jeda Dingin dan Isolasi Derau Sistem
    # -------------------------------------------------------------
    print("Building Subbab 3.5.2 items...")
    sec_3_5_2_items = []
    p3_5_2_1 = create_para(doc, [
        ("Eksekusi beban kerja komputasi numerik intensif secara kontinu pada prosesor modern dapat memicu peningkatan akumulasi panas pada inti silikon. Peningkatan temperatur yang melampaui batas ambang termal dapat memicu mekanisme proteksi perangkat keras berupa penurunan frekuensi kerja secara otomatis (", False),
        ("thermal throttling", True),
        ("), yang berpotensi menghasilkan variabilitas waktu eksekusi yang semu. Untuk meminimalkan efek pelambatan termal (", False),
        ("thermal throttling", True),
        ("), diterapkan protokol jeda dingin (", False),
        ("cool-down buffer", True),
        (") berupa penundaan waktu tidur sistem selama 0,5 detik (", False),
        ("time.sleep(0.5)", True),
        (") di antara setiap repetisi pengujian, serta jeda waktu pendinginan tambahan selama 2 detik sebelum pergantian blok perlakuan filter. Di samping itu, sebelum eksekusi pengujian dimulai, seluruh aplikasi pengguna pihak ketiga non-esensial, koneksi jaringan eksternal, dan layanan pembaruan otomatis sistem operasi dinonaktifkan guna meminimalkan derau interupsi penjadwalan OS (", False),
        ("operating system scheduling jitter", True),
        (").", False)
    ])
    sec_3_5_2_items.append(p3_5_2_1)
    insert_items_before(h_map["3.5.3"], sec_3_5_2_items)

    # -------------------------------------------------------------
    # SUBBAB 3.5.3: Pengujian Berselang-seling dan Kontrol A/A
    # -------------------------------------------------------------
    print("Building Subbab 3.5.3 items...")
    sec_3_5_3_items = []
    
    p3_5_3_1 = create_para(doc, [
        ("Untuk memastikan data waktu eksekusi serial dan paralel dapat dikomparasikan secara valid dan bebas bias, seluruh pengujian dieksekusi melalui protokol 30 kali repetisi terkontrol yang dijalankan secara berselang-seling (", False),
        ("interleaved execution", True),
        ("). Alih-alih mengeksekusi 30 kali pengujian serial secara berurutan lalu dilanjutkan 30 kali pengujian paralel, protokol ini menjalankan pengujian secara bergantian pada setiap repetisi: Iterasi 1 Serial → Iterasi 1 Paralel → Iterasi 2 Serial → Iterasi 2 Paralel … hingga Iterasi 30. Dengan metode berselang-seling ini, setiap pasangan data serial dan paralel mengalami kondisi beban sistem latar belakang dan profil termal lingkungan yang setara, sehingga nilai rasio percepatan (", False),
        ("speedup", True),
        (") yang dihitung dari pasangan iterasi yang berdekatan memiliki validitas internal yang kokoh.", False)
    ])
    sec_3_5_3_items.append(p3_5_3_1)
    
    p3_5_3_2 = create_para(doc, [
        ("Pengujian pada alokasi satu proses pekerja (", False),
        ("P = 1", True),
        (") pada Skenario B difungsikan sebagai instrumen kontrol dasar serial terhadap serial (", False),
        ("A/A control", True),
        ("). Karena pada ", False),
        ("P = 1", True),
        (" seluruh komputasi hanya dieksekusi oleh satu proses pekerja tanpa pembagian beban ke beberapa inti fisik prosesor, secara teoretis tidak terjadi percepatan komputasi (", False),
        ("S ≈ 1,00", True),
        ("). Nilai selisih waktu eksekusi yang terukur (", False),
        ("T_overhead, P=1 = T_paralel, P=1 - T_serial", True),
        (") secara presisi merepresentasikan ambang batas derau sistem (", False),
        ("system noise floor", True),
        (") serta biaya struktural inheren dari modul ", False),
        ("multiprocessing", True),
        (" Python (mekanisme transmisi pipa IPC dan serialisasi objek data) tanpa campur tangan akselerasi perangkat keras.", False)
    ])
    sec_3_5_3_items.append(p3_5_3_2)
    
    p3_5_3_3 = create_para(doc, [
        ("Sebagai catatan transparansi ilmiah mengenai batasan eksperimen, urutan eksekusi ketiga blok skenario dijalankan secara sekuensial (Blok A dijalankan pertama, diikuti Blok B, lalu diakhiri oleh Blok C) tanpa pengacakan menyeluruh (", False),
        ("global randomized block", True),
        ("). Fenomena pergeseran waktu ", False),
        ("baseline", True),
        (" serial antar-blok (di mana Skenario A memiliki durasi ", False),
        ("baseline", True),
        (" serial sedikit lebih lambat dibandingkan Skenario B dan C akibat dinamika termal awal sistem) dicatat sebagai batasan metodologis yang dianalisis secara objektif pada Bab 5.", False)
    ])
    sec_3_5_3_items.append(p3_5_3_3)
    
    insert_items_before(h_map["3.6"], sec_3_5_3_items)

    # -------------------------------------------------------------
    # SUBBAB 3.6: Teknik Analisis Data
    # -------------------------------------------------------------
    print("Building Subbab 3.6 items...")
    sec_3_6_items = []
    
    p3_6_1 = create_para(doc, [
        ("Analisis data hasil pengujian bertumpu pada pendekatan statistik deskriptif dan inferensial non-parametrik yang tangguh terhadap karakteristik data sistem komputasi riil. Waktu eksekusi sistem komputer umumnya memiliki distribusi yang asimetris dengan kecenderungan menjulur ke kanan (", False),
        ("right-skewed distribution", True),
        ("), akibat munculnya beberapa nilai pencilan (", False),
        ("outliers", True),
        (") yang dipicu oleh interupsi periodik sistem operasi. Mengingat asumsi normalitas baku tidak terpenuhi, analisis pemusatan data mengutamakan statistik non-parametrik yang tangguh terhadap pencilan (", False),
        ("robust statistics", True),
        ("), yaitu nilai median dan rentang antarkuartil (IQR, [", False),
        ("Q25 - Q75", True),
        ("]). Nilai rerata sampel (", False),
        ("x̄", True),
        (") dan simpangan baku sampel (", False),
        ("s", True),
        (") tetap dilaporkan sebagai parameter pelengkap.", False)
    ])
    sec_3_6_items.append(p3_6_1)
    
    p3_6_2 = create_para(doc, [
        ("Untuk mengestimasi presisi statistik pada nilai rerata parameter kinerja, dihitung selang kepercayaan 95% (", False),
        ("confidence interval", True),
        (") menggunakan distribusi ", False),
        ("t", True),
        ("-Student untuk ukuran sampel ", False),
        ("n = 30", True),
        (" (", False),
        ("df = n - 1 = 29", True),
        (") dengan nilai kritis ", False),
        ("t_(29, 0,025) = 2,04523", True),
        (":\n", False),
        ("CI_95% = x̄ ± 2,04523 · (s / √30)", True),
        ("\nFormulasi ini menjamin estimasi rentang parameter populasi dengan tingkat kepercayaan 95%.", False)
    ])
    sec_3_6_items.append(p3_6_2)
    
    p3_6_3 = create_para(doc, [
        ("Pengujian signifikansi perbedaan performa antar-perlakuan dievaluasi melalui uji hipotesis non-parametrik dengan taraf signifikansi ", False),
        ("α = 0,05", True),
        (". Uji Mann–Whitney ", False),
        ("U", True),
        (" digunakan untuk menguji signifikansi perbedaan antara dua kelompok perlakuan independen, sedangkan uji Kruskal–Wallis digunakan untuk menguji variasi kinerja antar-alokasi proses pekerja (", False),
        ("P = 1, 2, 4, 8", True),
        ("). Suatu perbedaan perlakuan dinyatakan signifikan secara statistik apabila nilai signifikansi terhitung lebih kecil dari ambang batas (", False),
        ("p < 0,05", True),
        (").", False)
    ])
    sec_3_6_items.append(p3_6_3)
    
    p3_6_4 = create_para(doc, [
        ("Pencocokan model teoretis skalabilitas dilakukan dengan mencocokkan kurva rasio percepatan empiris terhadap formulasi Hukum Amdahl menggunakan metode regresi non-linier kuadrat terkecil (", False),
        ("non-linear least squares", True),
        ("). Melalui pendekatan ini, diestimasi besaran fraksi paralel teoretis ", False),
        ("f", True),
        (" per algoritma filter pada Skenario B (", False),
        ("P ∈ {2, 4, 8}", True),
        (") beserta selang kepercayaan 95% berbasis ", False),
        ("bootstrap", True),
        (". Evaluasi dilanjutkan dengan menghitung fraksi serial eksperimental metrik Karp–Flatt ", False),
        ("e = ((1/S) - (1/P)) / (1 - (1/P))", True),
        (" untuk mendiagnosis apakah keterbatasan skalabilitas bersifat algoritmik murni ataukah dipicu oleh pembengkakan beban koordinasi paralel.", False)
    ])
    sec_3_6_items.append(p3_6_4)
    
    p3_6_5 = create_para(doc, [
        ("Validasi integritas data luaran dilakukan secara deterministik melalui verifikasi bit-identik antara matriks citra hasil pemrosesan paralel terhadap matriks citra hasil pemrosesan serial pada seluruh 810 iterasi pengujian. Kriteria kelulusan integritas ditetapkan secara mutlak, di mana selisih nilai intensitas piksel maksimum antara citra paralel dan serial harus bernilai nol di seluruh koordinat spasial (", False),
        ("Δmax = max |I_paralel - I_serial| = 0", True),
        ("). Apabila ditemukan ", False),
        ("Δmax > 0", True),
        (", pengujian dinyatakan mengalami kegagalan integritas (", False),
        ("data corruption", True),
        ("). Mengikuti kaidah akademik penulisan metodologi, seluruh angka hasil pengujian aktual dan besaran parameter empiris disimpan dan disajikan secara komprehensif pada Bab 5.", False)
    ])
    sec_3_6_items.append(p3_6_5)
    
    # Clean up empty paragraphs between 3.6 and 4.0 if any
    p_target_4_0 = h_map["4.0"]
    # Check paragraphs immediately before p_target_4_0
    parent = p_target_4_0._element.getparent()
    p_prev = p_target_4_0._element.getprevious()
    while p_prev is not None and p_prev.tag.endswith('p'):
        # Check text
        txt_prev = "".join(p_prev.itertext()).strip()
        if len(txt_prev) == 0:
            p_to_remove = p_prev
            p_prev = p_prev.getprevious()
            parent.remove(p_to_remove)
            print("Removed trailing empty paragraph before Heading 4.0")
        else:
            break
            
    insert_items_before(p_target_4_0, sec_3_6_items)
    
    print(f"Saving updated document to OneDrive: {ONEDRIVE_PATH}")
    doc.save(ONEDRIVE_PATH)
    print("OneDrive save successful!")
    
    print(f"Mirroring updated document to local: {LOCAL_PATH}")
    shutil.copy2(ONEDRIVE_PATH, LOCAL_PATH)
    print("Local mirror successful!")

if __name__ == '__main__':
    populate_bab_3()
