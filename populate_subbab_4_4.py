# -*- coding: utf-8 -*-
"""
Script to populate Subbab 4.4 Perancangan Pengukuran dan Pencatatan Telemetri in Laporan Akhir.
Strictly non-destructive:
- Replaces paragraph 292 (between Heading 2 4.4 and Heading 2 4.5) with complete Subbab 4.4 text and Table 4.1.
- Leaves Subbab 4.1, Subbab 4.2, Subbab 4.3 (with Gambar 4.1), and Subbab 4.5 100% untouched.
- Strictly adheres to PUEBI/EYD V, APA 7th, no 'di mana', passive voice, no first-person pronouns, open-format table.
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

sys.stdout.reconfigure(encoding='utf-8')

MASTER_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
MASTER_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"

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

def set_cell_margins(cell, top=50, bottom=50, left=70, right=70):
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

def format_cell_text(cell, runs_spec, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT, font_size=Pt(8.5)):
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

def build_table_4_1(doc):
    """Table 4.1 Skema Struktur Data Telemetri Kinerja CSV (15 Atribut Rekaman)."""
    headers = [
        "No.",
        "Nama Atribut (Kolom CSV)",
        "Tipe Data",
        "Satuan / Format",
        "Deskripsi dan Peran Metodologis"
    ]
    widths_cm = [0.8, 3.1, 1.6, 2.7, 5.8]  # Sum = 14.0 cm
    
    rows_data = [
        (
            [("1", False)],
            [("timestamp", True)],
            [("str", True)],
            [("YYYY-MM-DD HH:MM:SS", False)],
            [("Stempel waktu penanda eksekusi awal blok perlakuan eksperimen.", False)]
        ),
        (
            [("2", False)],
            [("scenario", True)],
            [("str", True)],
            [("Kategori (A, B, C)", False)],
            [("Kode blok skenario eksperimen yang sedang dieksekusi.", False)]
        ),
        (
            [("3", False)],
            [("filter", True)],
            [("str", True)],
            [("Nama Filter", False)],
            [("Algoritma filter spasial yang diuji (Grayscale, Gaussian Blur, Sobel).", False)]
        ),
        (
            [("4", False)],
            [("resolution", True)],
            [("int64", True)],
            [("Piksel (px)", False)],
            [("Dimensi panjang dan lebar sisi matriks citra bujur sangkar (512, 1024, 2048, 4096).", False)]
        ),
        (
            [("5", False)],
            [("image_id", True)],
            [("str", True)],
            [("Identifier Teks", False)],
            [("Identitas berkas citra acuan master yang diproses (misal: ", False), ("ref_img_01_512px", True), (").", False)]
        ),
        (
            [("6", False)],
            [("iteration", True)],
            [("int64", True)],
            [("Indeks (1 s.d. 30)", False)],
            [("Nomor urut repetisi pengujian berpasangan serial-paralel.", False)]
        ),
        (
            [("7", False)],
            [("p", True)],
            [("int64", True)],
            [("Unit Pekerja", False)],
            [("Alokasi jumlah proses pekerja pada kolam pemrosesan (P ∈ {1, 2, 4, 8}).", False)]
        ),
        (
            [("8", False)],
            [("t_serial", True)],
            [("float64", True)],
            [("Detik (s)", False)],
            [("Durasi waktu eksekusi komputasi serial satu inti prosesor (nilai acuan ", False), ("baseline", True), (").", False)]
        ),
        (
            [("9", False)],
            [("t_parallel", True)],
            [("float64", True)],
            [("Detik (s)", False)],
            [("Durasi waktu eksekusi komputasi paralel murni (atau pengukuran serial kedua independen pada P = 1).", False)]
        ),
        (
            [("10", False)],
            [("speedup", True)],
            [("float64", True)],
            [("Nirdimensi", False)],
            [("Rasio kelipatan percepatan komputasi empiris (S = T_serial / T_paralel).", False)]
        ),
        (
            [("11", False)],
            [("efficiency", True)],
            [("float64", True)],
            [("Persen (%)", False)],
            [("Persentase efisiensi pemanfaatan kapasitas unit proses pekerja (E = (S / P) × 100%, P > 1).", False)]
        ),
        (
            [("12", False)],
            [("overhead", True)],
            [("float64", True)],
            [("Detik (s)", False)],
            [("Durasi penalti beban tambahan koordinasi paralel (T_overhead = T_paralel - (T_serial / P), P > 1).", False)]
        ),
        (
            [("13", False)],
            [("cpu_utilization", True)],
            [("float64", True)],
            [("Persen (%)", False)],
            [("Rata-rata persentase beban utilisasi prosesor sistem yang direkam oleh ", False), ("thread daemon", True), (" latar belakang.", False)]
        ),
        (
            [("14", False)],
            [("is_identical", True)],
            [("bool", True)],
            [("Boolean", False)],
            [("Status keidentikan bit piksel: ", False), ("True", True), (" jika Δmax = 0; ", False), ("False", True), (" jika terjadi perbedaan piksel.", False)]
        ),
        (
            [("15", False)],
            [("max_diff", True)],
            [("float64", True)],
            [("Intensitas Piksel", False)],
            [("Nilai selisih absolut maksimum intensitas piksel antara citra paralel dan serial (Δmax).", False)]
        )
    ]
    
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_open_table_borders(tbl)
    
    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = Cm(widths_cm[i])
        set_cell_margins(hdr_cells[i], top=60, bottom=60, left=50, right=50)
        format_cell_text(hdr_cells[i], [(title, False, True)], bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=Pt(9.0))
        
    for r_idx, (c0, c1, c2, c3, c4) in enumerate(rows_data):
        row_cells = tbl.rows[r_idx + 1].cells
        for col_i, runs in enumerate([c0, c1, c2, c3, c4]):
            row_cells[col_i].width = Cm(widths_cm[col_i])
            set_cell_margins(row_cells[col_i], top=40, bottom=40, left=50, right=50)
            align = WD_ALIGN_PARAGRAPH.JUSTIFY if col_i == 4 else WD_ALIGN_PARAGRAPH.CENTER
            format_cell_text(row_cells[col_i], runs, align=align, font_size=Pt(8.0))
            
    return tbl

def generate_subbab_4_4_elements(doc):
    """Generate all document elements for Subbab 4.4."""
    elements = []
    
    # Paragraf 1: Isolasi Pewaktuan dan Titik Instrumentasi Presisi
    elements.append(create_para(doc, [
        ("Pengukuran durasi waktu eksekusi komputasi dirancang dengan penempatan titik instrumentasi pewaktu berbasis fungsi monotonik ", False),
        ("time.perf_counter()", True),
        (" dari pustaka standar Python. Titik stempel waktu awal (", False),
        ("start timestamp", True),
        (", ", False),
        ("t_start", True),
        (") dicatat tepat sesaat sebelum proses partisi matriks citra dan penambahan baris batas dimulai. Seluruh fase pemrosesan paralel—mencakup dekomposisi baris horizontal, serialisasi objek data (", False),
        ("pickle", True),
        ("), transmisi melalui saluran pipa IPC, eksekusi komputasi filter pada kolam proses pekerja, pemangkasan baris batas (", False),
        ("halo stripping", True),
        ("), transmisi pengembalian hasil parsial, hingga rekonstruksi citra utuh melalui ", False),
        ("numpy.vstack", True),
        ("—berada di dalam jendela pengukuran waktu komputasi. Stempel waktu akhir (", False),
        ("stop timestamp", True),
        (", ", False),
        ("t_stop", True),
        (") dicatat segera setelah matriks citra utuh berhasil disusun kembali pada memori proses utama. Selisih ", False),
        ("t_stop - t_start", True),
        (" ditetapkan sebagai waktu eksekusi paralel aktual (", False),
        ("T_paralel", True),
        ("). Operasi pembacaan citra awal dari media penyimpanan (", False),
        ("cv2.imread", True),
        (") dan penyimpanan berkas luaran ke media penyimpanan (", False),
        ("cv2.imwrite", True),
        (") diisolasi di luar rentang stempel waktu tersebut, sehingga durasi yang tercatat mencerminkan performa komputasi murni dan beban tambahan (", False),
        ("overhead", True),
        (") koordinasi paralel sistem.", False)
    ]))
    
    # Paragraf 2: Pemantauan Utilisasi CPU Latar Belakang
    elements.append(create_para(doc, [
        ("Pemantauan beban kerja prosesor dirancang secara asinkron menggunakan kelas ", False),
        ("CPUMonitor", True),
        (" yang berjalan pada ", False),
        ("thread daemon", True),
        (" latar belakang mandiri. Kelas ini melakukan percontohan (", False),
        ("sampling", True),
        (") persentase utilisasi CPU setiap interval 20 milidetik (0,02 detik) tanpa memblokir eksekusi komputasi proses utama atau menambah latensi pada pengukuran waktu monotonik. Sebelum siklus kalkulasi dimulai, fungsi ", False),
        ("psutil.cpu_percent(interval=None, percpu=True)", True),
        (" dipanggil satu kali untuk mengosongkan riwayat pembacaan internal psutil, sehingga nilai rata-rata utilisasi CPU yang dihimpun merefleksikan aktivitas prosesor selama jendela komputasi berlangsung.", False)
    ]))
    
    # Paragraf 3: Pengantar Skema Data Telemetri CSV 15 Kolom
    elements.append(create_para(doc, [
        ("Guna mendukung keterlacakan data (", False),
        ("data traceability", True),
        (") dan keterulangan pengujian, seluruh data hasil pengukuran dari 810 pasangan repetisi eksperimen disimpan ke dalam berkas telemetri berformat ", False),
        ("Comma-Separated Values", True),
        (" (CSV). Setiap baris rekaman merepresentasikan satu iterasi pengujian terperinci dengan 15 atribut parameter kinerja. Struktur skema data telemetri dirangkum pada Tabel 4.1.", False)
    ]))
    
    # Tabel 4.1 Skema Struktur Data Telemetri Kinerja CSV (15 Atribut Rekaman)
    elements.append(create_table_title(doc, "Tabel 4.1 Skema Struktur Data Telemetri Kinerja CSV (15 Kolom Rekaman)"))
    elements.append(build_table_4_1(doc))
    
    # Paragraf 4: Mekanisme Agregasi dan Penyimpanan Berkas
    elements.append(create_para(doc, [
        ("Data telemetri mentah yang dihimpun pada berkas ", False),
        ("benchmark_results.csv", True),
        (" mencakup 810 baris pengamatan individual. Untuk memfasilitasi analisis komparatif dan pemodelan kurva skalabilitas pada Bab 5, sistem secara otomatis melakukan agregasi statistik (menghitung nilai median, rentang antarkuartil IQR, nilai rerata, dan simpangan baku per kelompok perlakuan) dan menyimpannya ke dalam berkas ikhtisar ", False),
        ("benchmark_results_summary.csv", True),
        (". Berkas data mentah dan ringkasan telemetri ini dilampirkan secara lengkap pada Lampiran A dan Lampiran B sebagai wujud transparansi ilmiah.", False)
    ]))
    
    return elements

def populate_subbab_4_4():
    print("=== Populating Subbab 4.4 in Master Document ===")
    doc = docx.Document(MASTER_DOCX_LOCAL)
    body = doc.element.body
    elements = list(body)
    
    target_p4_4_idx = None
    target_p4_5_idx = None
    
    for i, el in enumerate(elements):
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, doc)
            txt = p.text.strip()
            if 'Perancangan Pengukuran dan Pencatatan Telemetri' in txt:
                target_p4_4_idx = i
            elif 'Perancangan Verifikasi Integritas Citra Bit-Identik' in txt:
                target_p4_5_idx = i
                break
                
    assert target_p4_4_idx is not None and target_p4_5_idx is not None, f"Bounds not found: {target_p4_4_idx}, {target_p4_5_idx}"
    print(f"Found Subbab 4.4 at element {target_p4_4_idx}, Subbab 4.5 at element {target_p4_5_idx}")
    print(f"Elements between 4.4 and 4.5 to be replaced: {target_p4_5_idx - target_p4_4_idx - 1}")
    
    # Update Heading 2 for 4.4
    p4_4 = docx.text.paragraph.Paragraph(elements[target_p4_4_idx], doc)
    p4_4.text = ""
    p4_4.style = 'Heading 2'
    p4_4.paragraph_format.space_before = Pt(12)
    p4_4.paragraph_format.space_after = Pt(6)
    p4_4.paragraph_format.line_spacing = 1.5
    p4_4.paragraph_format.first_line_indent = Cm(0)
    r4_4 = p4_4.add_run("4.4 Perancangan Pengukuran dan Pencatatan Telemetri")
    r4_4.font.name = 'Times New Roman'
    r4_4.font.size = Pt(12)
    r4_4.bold = True
    
    # Generate Subbab 4.4 items
    scratch_doc = docx.Document()
    items_to_insert = generate_subbab_4_4_elements(scratch_doc)
    
    # Insert before Subbab 4.5 heading element
    target_p4_5_el = elements[target_p4_5_idx]
    for item in items_to_insert:
        target_p4_5_el.addprevious(item._element)
        
    # Remove old elements between target_p4_4_idx + 1 and target_p4_5_idx - 1
    for i in range(target_p4_4_idx + 1, target_p4_5_idx):
        body.remove(elements[i])
        
    print(f"Successfully inserted {len(items_to_insert)} elements into Subbab 4.4 and removed old elements.")
    
    print(f"Saving to local master: {MASTER_DOCX_LOCAL}")
    doc.save(MASTER_DOCX_LOCAL)
    print("Local master save successful!")
    
    try:
        print(f"Saving to OneDrive master: {MASTER_DOCX_ONEDRIVE}")
        shutil.copy2(MASTER_DOCX_LOCAL, MASTER_DOCX_ONEDRIVE)
        print("OneDrive master copy successful!")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

if __name__ == '__main__':
    populate_subbab_4_4()
