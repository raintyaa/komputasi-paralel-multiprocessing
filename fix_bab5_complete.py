import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
import shutil, os, sys, re

sys.stdout.reconfigure(encoding='utf-8')

MASTER_PATH = 'UTS/Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx'
BACKUP_PATH = 'UTS/Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx.bak_teammate_raw'

# 1. Create raw backup
print(f"Creating backup: {BACKUP_PATH}")
shutil.copy(MASTER_PATH, BACKUP_PATH)

# Load document
doc = docx.Document(MASTER_PATH)
body = doc._body._element

print(f"Initial state: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")

# Helper functions for formatting
def set_open_table_borders(table):
    tblPr = table._element.tblPr
    for child in list(tblPr):
        if child.tag.endswith('tblBorders'):
            tblPr.remove(child)
    tblBorders = OxmlElement('w:tblBorders')
    
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '8')
    top.set(qn('w:space'), '0')
    top.set(qn('w:color'), '000000')
    tblBorders.append(top)
    
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
    
    # Header bottom border 0.75 pt
    for cell in table.rows[0].cells:
        tcPr = cell._element.get_or_add_tcPr()
        for child in list(tcPr):
            if child.tag.endswith('tcBorders'):
                tcPr.remove(child)
        tcBorders = OxmlElement('w:tcBorders')
        b = OxmlElement('w:bottom')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '6')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), '000000')
        tcBorders.append(b)
        tcPr.append(tcBorders)

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def style_cell_text(cell, text, font_size=8.5, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER):
    p = cell.paragraphs[0]
    p.text = ''
    p.alignment = align
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

# Helper for code table styling
def style_code_table(table, code_text):
    cell = table.rows[0].cells[0]
    # Set light gray box border
    tcPr = cell._element.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith('tcBorders'):
            tcPr.remove(child)
    tcBorders = OxmlElement('w:tcBorders')
    for side in ['top', 'left', 'bottom', 'right']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4') # 0.5 pt
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), 'CCCCCC')
        tcBorders.append(b)
    tcPr.append(tcBorders)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    # Light gray shading
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F8F9FA')
    tcPr.append(shd)
    
    # Populate code lines
    # Clear all paragraphs in cell except first
    while len(cell.paragraphs) > 1:
        p_extra = cell.paragraphs[-1]
        p_extra._element.getparent().remove(p_extra._element)
    
    lines = code_text.splitlines()
    for idx, line in enumerate(lines):
        if idx == 0:
            p = cell.paragraphs[0]
            p.text = ''
        else:
            p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line if line.strip() else ' ')
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(30, 30, 30)

# Load clean code files
with open('UTS/Kode Program 5.1 Fungsi Partisi Baris dan Penambahan Boundary Halo.py', 'r', encoding='utf-8') as f:
    CODE_5_1 = f.read().strip()
with open('UTS/Kode Program 5.2 Eksekusi Tugas pada Kolam Pekerja dan Halo Stripping.py', 'r', encoding='utf-8') as f:
    CODE_5_2 = f.read().strip()
with open('UTS/Kode Program 5.3 Implementasi Konvolusi Filter Spasial (Gaussian Blur & Sobel L2).py', 'r', encoding='utf-8') as f:
    CODE_5_3 = f.read().strip()
with open('UTS/Kode Program 5.4 Fungsi Validasi Integritas Luaran Citra Bit-Identik.py', 'r', encoding='utf-8') as f:
    CODE_5_4 = f.read().strip()

print("Clean code snippets loaded successfully.")

# ==============================================================================
# STEP A: REORDER SUBBAB 5.1 SUBSECTIONS AND RESTRUCTURE TEXT/CODE
# ==============================================================================
# We reorder XML elements in body:
# Move Mesin Konkurensi Paralel (5.1.1) before Modul Filter Spasial (5.1.2)

start_idx = None
end_idx = None
for idx, child in enumerate(body):
    if child.tag.endswith('p'):
        p = docx.text.paragraph.Paragraph(child, doc)
        if 'IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN' in p.text:
            start_idx = idx
        if 'Validasi Integritas Data dan Keterulangan Pengujian' in p.text:
            end_idx = idx
            break

print(f"Subbab 5.1 body range: {start_idx} to {end_idx}")

# Collect block 2 (Mesin Konkurensi Paralel)
block2_elems = []
for i in range(start_idx, end_idx):
    child = body[i]
    if child.tag.endswith('p'):
        p = docx.text.paragraph.Paragraph(child, doc)
        if 'Mesin Konkurensi Paralel' in p.text:
            for j in range(i, end_idx):
                c = body[j]
                if c.tag.endswith('p'):
                    pj = docx.text.paragraph.Paragraph(c, doc)
                    if 'Orkestrator Pengujian' in pj.text:
                        break
                block2_elems.append(c)
            break

# First element of block 1 (Modul Filter Spasial)
block1_first = None
for i in range(start_idx, end_idx):
    child = body[i]
    if child.tag.endswith('p'):
        p = docx.text.paragraph.Paragraph(child, doc)
        if 'Modul Filter Spasial' in p.text:
            block1_first = child
            break

print(f"Moving {len(block2_elems)} elements of Mesin Konkurensi Paralel before Modul Filter Spasial...")
for elem in block2_elems:
    block1_first.addprevious(elem)

# Now update texts, captions, and code tables in Subbab 5.1
# Let's map elements in Subbab 5.1 after reordering:
p_intro_5_1 = None
p_h3_engine = None
p_intro_engine = None
p_cap_code_5_1 = None
tbl_code_5_1 = None
p_exp_code_5_1 = None
p_bridge_engine = None
p_cap_code_5_2 = None
tbl_code_5_2 = None
p_exp_code_5_2 = None

p_h3_filter = None
p_intro_filter = None
p_cap_code_5_3 = None
tbl_code_5_3 = None
p_exp_code_5_3 = None

p_h3_telemetry = None
p_intro_telemetry = None
p_cap_code_5_4 = None
tbl_code_5_4 = None
p_exp_code_5_4 = None

for i in range(start_idx, end_idx):
    child = body[i]
    if child.tag.endswith('p'):
        p = docx.text.paragraph.Paragraph(child, doc)
        txt = p.text.strip()
        if 'Subbab ini menguraikan realisasi kode program' in txt:
            p_intro_5_1 = p
        elif 'Mesin Konkurensi Paralel' in txt:
            p_h3_engine = p
        elif 'Mesin paralel merupakan inti dari sistem' in txt:
            p_intro_engine = p
        elif 'Kode Program 5.1' in txt:
            p_cap_code_5_1 = p
        elif 'Fungsi create_horizontal_partitions melakukan pembagian' in txt:
            p_exp_code_5_1 = p
        elif 'Setelah tugas-tugas terpartisi' in txt:
            p_bridge_engine = p
        elif 'Kode Program 5.2' in txt:
            p_cap_code_5_2 = p
        elif 'Tugas dijalankan secara independen' in txt:
            p_exp_code_5_2 = p
        elif 'Modul Filter Spasial' in txt:
            p_h3_filter = p
        elif 'Modul ini bertanggung jawab atas operasi' in txt:
            p_intro_filter = p
        elif 'Kode Program 5.3' in txt:
            p_cap_code_5_3 = p
        elif 'Pada algoritma Gaussian Blur 3x3' in txt:
            p_exp_code_5_3 = p
        elif 'Orkestrator Pengujian dan Telemetri' in txt:
            p_h3_telemetry = p
        elif 'Untuk menjamin kebenaran kalkulasi' in txt:
            p_intro_telemetry = p
        elif 'Kode Program 5.4' in txt:
            p_cap_code_5_4 = p
        elif 'Fungsi validate_results bekerja' in txt:
            p_exp_code_5_4 = p
    elif child.tag.endswith('tbl'):
        t = docx.table.Table(child, doc)
        txt = t.rows[0].cells[0].text
        if 'create_horizontal_partitions' in txt:
            tbl_code_5_1 = t
        elif '_worker_filter_task' in txt:
            tbl_code_5_2 = t
        elif 'Gaussian Blur' in txt or 'magnitude' in txt:
            tbl_code_5_3 = t
        elif 'validate_results' in txt:
            tbl_code_5_4 = t

print("Mapped all Subbab 5.1 elements successfully.")

# Helper to set paragraph text cleanly with TNR 12 pt justified
def set_p_text(p, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, bold=False, italic=False, space_before=0, space_after=6):
    p.text = ''
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)

# Helper to set code caption
def set_code_caption(p, text):
    p.text = ''
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 0, 0)

# Apply refined texts and code
set_p_text(p_intro_5_1, "Subbab ini menguraikan realisasi kode program dari perancangan arsitektur pemrosesan paralel yang telah dirancang pada Bab 4. Implementasi sistem dikonstruksi ke dalam tiga berkas modul utama: manajemen tugas konkurensi (src/parallel_engine.py), operasi pemfilteran spasial (src/filter.py), serta validasi eksekusi dan telemetri (run_benchmark.py). Cuplikan kode pada bagian ini menampilkan fungsi-fungsi inti, sedangkan keseluruhan kode sumber sistem didokumentasikan pada Lampiran C dan D.")

set_code_caption(p_cap_code_5_1, "Kode Program 5.1 Fungsi Partisi Baris dan Penambahan Boundary Halo")
set_p_text(p_intro_engine, "Mesin paralel merupakan inti arsitektur sistem yang bertugas mendekomposisi matriks citra skala besar menjadi submatriks tugas independen agar dapat dieksekusi secara serentak (konkuren) pada multi-inti prosesor. Dekomposisi dilakukan menggunakan teknik partisi baris horizontal (domain decomposition) dengan penambahan lapisan batas (boundary halo) selebar radius kernel agar kalkulasi konvolusi di tepi submatriks memperoleh data piksel tetangga yang lengkap.")
style_code_table(tbl_code_5_1, CODE_5_1)
set_p_text(p_exp_code_5_1, "Fungsi create_horizontal_partitions membagi matriks citra secara vertikal berdasarkan jumlah proses pekerja yang dialokasikan. Untuk filter spasial berukuran 3×3 dengan radius kernel satu piksel (k = 1), fungsi mengekstrak satu baris piksel ekstra dari segmen tetangganya sebagai boundary halo atas dan bawah, kecuali pada batas terluar citra asli. Submatriks beserta informasi koordinat pemotongan batas kemudian dipaketkan ke dalam daftar tupel penugasan (tasks).")

set_p_text(p_bridge_engine, "Setelah struktur tugas terpartisi, kolam pekerja (worker pool) mendistribusikan data melalui komunikasi antar-proses (inter-process communication/IPC), mengeksekusi fungsi filter secara independen pada setiap proses pekerja, memangkas kembali baris halo tambahan (halo stripping), lalu merekonstruksi citra utuh.")
set_code_caption(p_cap_code_5_2, "Kode Program 5.2 Eksekusi Tugas pada Kolam Pekerja dan Rekonstruksi Citra")
style_code_table(tbl_code_5_2, CODE_5_2)
set_p_text(p_exp_code_5_2, "Tugas komputasi dieksekusi secara terisolasi oleh fungsi _worker_filter_task pada proses pekerja masing-masing. Pascapemfilteran, indeks pemangkasan (halo stripping) diterapkan guna membuang area batas (overlap) di sisi atas dan bawah blok matriks sebelum luaran dikembalikan ke proses utama melalui mekanisme antrean IPC. Pada proses utama, pustaka multiprocessing.Pool memetakan seluruh tugas, dan luaran dari setiap segmen digabungkan kembali secara terurut menjadi satu matriks utuh menggunakan np.vstack().")

set_p_text(p_intro_filter, "Modul filter spasial bertanggung jawab atas operasi matematis tingkat piksel untuk mengaplikasikan transformasi visual pada citra. Pemfilteran dilakukan melalui konvolusi matriks kernel diskret terhadap matriks citra, sebagaimana diimplementasikan pada filter Gaussian Blur dan deteksi tepi Sobel L2.")
set_code_caption(p_cap_code_5_3, "Kode Program 5.3 Implementasi Konvolusi Filter Spasial (Gaussian Blur dan Sobel L2)")
style_code_table(tbl_code_5_3, CODE_5_3)
set_p_text(p_exp_code_5_3, "Pada algoritma Gaussian Blur 3×3, batas citra diberikan bantalan (padding) bermode edge guna mencegah artefak pada batas visual. Operasi konvolusi diimplementasikan melalui pergeseran jendela matriks 3×3 yang dibobotkan dengan nilai kernel Gaussian terdistribusi. Pada implementasi filter Sobel, magnitudo gradien diekstraksi menggunakan formulasi Euclidean (L2) dengan menghitung akar jumlahan kuadrat dari gradien sumbu mendatar (Gx) dan tegak (Gy), sebelum nilainya dipotong (clip) pada rentang [0, 255] dan dikonversi ke tipe data uint8.")

set_p_text(p_intro_telemetry, "Guna memverifikasi determinisme dan keabsahan kalkulasi dalam eksekusi paralel, modul telemetri menyediakan fungsi validasi otomatis yang mengomparasikan luaran eksekusi serial baseline terhadap luaran yang dihasilkan oleh kolam pekerja paralel.")
set_code_caption(p_cap_code_5_4, "Kode Program 5.4 Fungsi Validasi Integritas Luaran Citra Bit-Identik")
style_code_table(tbl_code_5_4, CODE_5_4)
set_p_text(p_exp_code_5_4, "Fungsi validate_results beroperasi melalui dua tahapan evaluasi. Pertama, verifikasi keselarasan dimensi geometris memastikan matriks luaran serial dan paralel memiliki resolusi yang identik. Kedua, fungsi np.array_equal menguji kesetaraan deterministik seluruh bit piksel matriks. Disparitas absolut maksimum (Δmax) turut dihitung menggunakan presisi float64 untuk mencegah galat pelimpahan (wraparound error) pada format integer, sehingga anomali nilai piksel sekecil apa pun dapat terdeteksi secara dini.")

print("Subbab 5.1 reordering, code styling, and text refinement complete.")

# ==============================================================================
# STEP B: SUBBAB 5.2 - TEXT REFINEMENT AND INSERTION OF TABEL 5.1 & TABEL 5.2
# ==============================================================================
p_intro_5_2 = None
p_text_5_2_1 = None
p_text_5_2_2 = None
p_text_5_2_3 = None

for p in doc.paragraphs:
    txt = p.text.strip()
    if 'Tahapan awal ini bersifat esensial dan wajib dilakukan' in txt:
        p_intro_5_2 = p
    elif 'Berdasarkan fungsi validasi telemetri yang telah diimplementasikan sebelumnya' in txt:
        p_text_5_2_1 = p
    elif 'Guna mengukur batasan derau pada ekosistem komputasi' in txt:
        p_text_5_2_2 = p
    elif 'Tahapan evaluasi keterulangan (repeatability drift) diukur' in txt:
        p_text_5_2_3 = p

# Refine P_intro_5_2
set_p_text(p_intro_5_2, "Tahapan validasi integritas data dan evaluasi keterulangan pengujian dilakukan sebelum menganalisis metrik percepatan dan efisiensi sistem. Pengujian ini bertujuan untuk memverifikasi keabsahan matematis dari luaran pemrosesan paralel serta mengukur stabilitas lingkungan eksekusi komputasi.")

# Refine P_text_5_2_1
set_p_text(p_text_5_2_1, "Berdasarkan fungsi validasi telemetri yang telah diimplementasikan, seluruh 810 pasangan pengujian pada ketiga skenario eksperimen menghasilkan nilai disparitas absolut maksimum Δmax = 0, yang secara programatis menghasilkan status is_identical = True. Hasil ini menegaskan bahwa partisi baris, penambahan boundary halo, dan pemangkasan batas (halo stripping) berhasil mencegah degradasi informasi piksel maupun timbulnya cacat garis sambungan (seam artifact) pada area pertemuan submatriks. Ringkasan hasil validasi integritas bit-identik disajikan pada Tabel 5.1.")

# Create Tabel 5.1 elements
p_cap_t5_1 = doc.add_paragraph()
set_p_text(p_cap_t5_1, "Tabel 5.1 Ringkasan Hasil Validasi Integritas Bit-Identik pada Seluruh Skenario Pengujian", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, space_before=12, space_after=4)

t5_1 = doc.add_table(rows=5, cols=7)
t5_1.alignment = WD_TABLE_ALIGNMENT.CENTER
t5_1_data = [
    ["Skenario Pengujian", "Algoritma Filter", "Parameter Uji", "Pasangan Uji", "Rasio Bit-Identik", "Δmax", "Status Keabsahan"],
    ["Skenario A (Variasi Resolusi)", "Grayscale, Gaussian, Sobel", "512–4096 px (P = 4)", "360", "360 / 360 (100%)", "0", "Valid"],
    ["Skenario B (Variasi Pekerja)", "Grayscale, Gaussian, Sobel", "P ∈ {1, 2, 4, 8} (2048 px)", "360", "360 / 360 (100%)", "0", "Valid"],
    ["Skenario C (Variasi Kompleksitas)", "Grayscale, Gaussian, Sobel", "2048 px (P = 4)", "90", "90 / 90 (100%)", "0", "Valid"],
    ["Total Kumulatif", "Tiga Algoritma Filter", "Seluruh Skenario (27 Kondisi)", "810", "810 / 810 (100%)", "0", "Valid (100%)"]
]

col_widths_t5_1 = [Inches(1.5), Inches(1.5), Inches(1.4), Inches(0.8), Inches(1.1), Inches(0.6), Inches(0.8)]
for r_idx, row in enumerate(t5_1.rows):
    is_header = (r_idx == 0)
    for c_idx, cell in enumerate(row.cells):
        val = t5_1_data[r_idx][c_idx]
        bold = is_header or (r_idx == 4)
        align = WD_ALIGN_PARAGRAPH.CENTER if (is_header or c_idx >= 3) else WD_ALIGN_PARAGRAPH.LEFT
        style_cell_text(cell, val, font_size=8.5, bold=bold, align=align)
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        cell.width = col_widths_t5_1[c_idx]

set_open_table_borders(t5_1)

p_note_t5_1 = doc.add_paragraph()
set_p_text(p_note_t5_1, "Keterangan: Seluruh evaluasi menggunakan fungsi np.array_equal() dan disparitas absolut dihitung pada presisi float64.", align=WD_ALIGN_PARAGRAPH.LEFT, italic=True, space_before=2, space_after=12)

# Insert Tabel 5.1 after p_text_5_2_1
p_text_5_2_1._element.addnext(p_note_t5_1._element)
p_text_5_2_1._element.addnext(t5_1._element)
p_text_5_2_1._element.addnext(p_cap_t5_1._element)

print("Tabel 5.1 inserted successfully.")

# Refine P_text_5_2_2
set_p_text(p_text_5_2_2, "Guna mengukur batasan derau pada ekosistem komputasi (noise floor), pengujian kontrol dasar A/A dilakukan dengan mengomparasikan eksekusi serial baseline terhadap eksekusi pada kolam pekerja dengan alokasi pekerja tunggal (P = 1) melalui 90 pasangan iterasi pada resolusi 2048 × 2048 piksel (kondisi B1, B5, dan B9). Hasil pengujian dirangkum pada Tabel 5.2. Nilai speedup rerata berada di sekitar 1,00×, yaitu 1,06× [CI 95%: 0,97–1,15] untuk Grayscale, 1,02× [CI 95%: 0,98–1,05] untuk Gaussian Blur, dan 1,00× [CI 95%: 0,95–1,05] untuk Sobel. Selang kepercayaan 95% dari ketiga filter seluruhnya mencakup nilai teoretis 1,00×. Rata-rata speedup agregat tercatat sebesar 1,03× dengan deviasi derau sistem di bawah 3%, dan nilai overhead mendekati nol (−0,0082 detik hingga +0,0054 detik). Stabilitas ini menegaskan bahwa peningkatan kinerja yang teramati pada alokasi multi-pekerja (P > 1) merefleksikan pengaruh nyata dari konkurensi pemrosesan paralel, bukan fluktuasi derau latar belakang sistem operasi.")

# Create Tabel 5.2 elements
p_cap_t5_2 = doc.add_paragraph()
set_p_text(p_cap_t5_2, "Tabel 5.2 Ringkasan Metrik Pengujian Kontrol Dasar A/A (Resolusi 2048 × 2048 Piksel; P = 1; N = 30 Iterasi per Filter)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, space_before=12, space_after=4)

t5_2 = doc.add_table(rows=5, cols=8)
t5_2.alignment = WD_TABLE_ALIGNMENT.CENTER
t5_2_data = [
    ["Kode", "Filter", "Ts Rerata ± Std (s)", "Tp Rerata ± Std (s)", "S Median [Q25–Q75]", "S Rerata [CI 95%]", "Overhead Rerata (s)", "Status Integritas"],
    ["B1", "Grayscale", "0,1333 ± 0,0200", "0,1303 ± 0,0273", "1,05 [0,92–1,21]", "1,06 [0,97–1,15]", "−0,0030", "Valid (100%)"],
    ["B5", "Gaussian Blur", "0,6688 ± 0,0553", "0,6606 ± 0,0715", "1,01 [0,96–1,09]", "1,02 [0,98–1,05]", "−0,0082", "Valid (100%)"],
    ["B9", "Sobel", "0,5743 ± 0,0482", "0,5797 ± 0,0582", "1,00 [0,94–1,06]", "1,00 [0,95–1,05]", "+0,0054", "Valid (100%)"],
    ["Agregat", "Semua Filter", "—", "—", "1,02 [0,94–1,12]", "1,03 [0,97–1,08]", "−0,0019", "Valid (100%)"]
]

col_widths_t5_2 = [Inches(0.6), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.2), Inches(1.2), Inches(0.9), Inches(0.8)]
for r_idx, row in enumerate(t5_2.rows):
    is_header = (r_idx == 0)
    for c_idx, cell in enumerate(row.cells):
        val = t5_2_data[r_idx][c_idx]
        bold = is_header or (r_idx == 4)
        align = WD_ALIGN_PARAGRAPH.LEFT if (not is_header and c_idx == 1) else WD_ALIGN_PARAGRAPH.CENTER
        style_cell_text(cell, val, font_size=8.5, bold=bold, align=align)
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        cell.width = col_widths_t5_2[c_idx]

set_open_table_borders(t5_2)

p_note_t5_2 = doc.add_paragraph()
set_p_text(p_note_t5_2, "Keterangan: N = 30 iterasi per kondisi (total 90 iterasi kontrol A/A); alokasi P = 1 berfungsi sebagai verifikasi batas derau (noise floor) sistem komputasi.", align=WD_ALIGN_PARAGRAPH.LEFT, italic=True, space_before=2, space_after=12)

# Insert Tabel 5.2 after p_text_5_2_2
p_text_5_2_2._element.addnext(p_note_t5_2._element)
p_text_5_2_2._element.addnext(t5_2._element)
p_text_5_2_2._element.addnext(p_cap_t5_2._element)

print("Tabel 5.2 inserted successfully.")

# Refine P_text_5_2_3 (repeatability drift)
set_p_text(p_text_5_2_3, "Evaluasi keterulangan antar-blok (repeatability drift) dianalisis dengan mengomparasikan sel perlakuan identik pada resolusi 2048 × 2048 piksel dengan konfigurasi pekerja P = 4 yang direplikasi melintasi tiga blok sekuens pengujian, yaitu Blok A (kondisi A3, A7, A11), Blok B (B3, B7, B11), dan Blok C (C1, C2, C3). Hasil observasi menunjukkan adanya variasi waktu eksekusi baseline serial pada Blok A yang tercatat sekitar 20% hingga 28% lebih lambat dibandingkan Blok B dan Blok C. Sebagai contoh, durasi serial Sobel tercatat 0,73 detik pada Blok A, 0,61 detik pada Blok B, dan 0,58 detik pada Blok C. Variasi ini diklasifikasikan sebagai limitasi pergeseran sistematis (systematic drift limitation), yang dipengaruhi oleh dinamika termal dan governor daya perangkat sebelum mencapai saturasi termal stabil. Oleh karena itu, komparasi speedup antar-kondisi difokuskan pada perbandingan di dalam blok yang sama, sementara analisis lintas-blok ditafsirkan secara cermat sesuai batasan metodologis.")

print("Subbab 5.2 texts and tables refined successfully.")

# ==============================================================================
# STEP C: SUBBAB 5.3 & 5.4 - FIX DROPPED DIGITS AND FORMATTING IN TABLES 5.3, 5.4, 5.5
# ==============================================================================
# Find Table 5.3, 5.4, 5.5 in doc
# Table 5.3 has "A1", Table 5.4 has "B1", Table 5.5 has "C1"
t5_3 = None
t5_4 = None
t5_5 = None

for t in doc.tables:
    txt = " ".join(c.text for c in t.rows[0].cells)
    if 'Kode' in txt and 'Resolusi (px)' in txt:
        t5_3 = t
    elif 'Kode' in txt and 'P' in txt and 'Overhead' in txt:
        t5_4 = t
    elif 'Kode' in txt and 'CPU (%)' in txt:
        t5_5 = t

print(f"Found existing tables: t5_3={'yes' if t5_3 else 'no'}, t5_4={'yes' if t5_4 else 'no'}, t5_5={'yes' if t5_5 else 'no'}")

if t5_4:
    # Fix dropped digits in Table 5.4 (Skenario B)
    # Row 2: Grayscale P=2 -> S Median was "1,3 [1,32–1,53]" -> fix to "1,39 [1,32–1,53]"
    # Row 11: Sobel P=4 -> S Median was "2,8 [2,60–3,06]" -> fix to "2,87 [2,60–3,06]"
    # Row 5: Gaussian Blur P=1 -> "1,01 [0,96–1,09]"
    # Also standardize spacing: e.g. "1,05 [0,92–1,21]" instead of "1,05[0,92–1,21]"
    for r_idx, row in enumerate(t5_4.rows[1:], start=1):
        cell_s_med = row.cells[3]
        txt = cell_s_med.text.strip()
        # Clean formatting
        if r_idx == 2 and '1,3 ' in txt:
            txt = '1,39 [1,32–1,53]'
        elif r_idx == 11 and '2,8 ' in txt:
            txt = '2,87 [2,60–3,06]'
        # Ensure space before '['
        txt = re.sub(r'(\d)\[', r'\1 [', txt)
        # Update run text
        cell_s_med.text = ''
        p = cell_s_med.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0, 0, 0)
    print("Table 5.4 (Skenario B) dropped digits and spacing fixed.")

if t5_3:
    # Standardize spacing before '[' in Table 5.3 (Skenario A)
    for r_idx, row in enumerate(t5_3.rows[1:], start=1):
        cell_s_med = row.cells[3]
        txt = re.sub(r'(\d)\[', r'\1 [', cell_s_med.text.strip())
        cell_s_med.text = ''
        p = cell_s_med.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0, 0, 0)
    print("Table 5.3 (Skenario A) spacing standardized.")

if t5_5:
    # Standardize spacing before '[' in Table 5.5 (Skenario C)
    for r_idx, row in enumerate(t5_5.rows[1:], start=1):
        cell_s_med = row.cells[2]
        txt = re.sub(r'(\d)\[', r'\1 [', cell_s_med.text.strip())
        cell_s_med.text = ''
        p = cell_s_med.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0, 0, 0)
    print("Table 5.5 (Skenario C) spacing standardized.")

# ==============================================================================
# STEP D: SPLIT DRAWINGS AND CAPTIONS FOR GAMBAR 5.2 AND GAMBAR 5.3
# ==============================================================================
# Find paragraphs containing Gambar 5.2 and Gambar 5.3 with drawings
# We process in reverse order so inserting after does not displace previous paragraphs
target_ps = []
for idx, p in enumerate(doc.paragraphs):
    if len(p._element.xpath('.//w:drawing')) > 0:
        if 'Gambar 5.2' in p.text:
            target_ps.append((idx, p, 'Gambar 5.2'))
        elif 'Gambar 5.3' in p.text:
            target_ps.append((idx, p, 'Gambar 5.3'))

print(f"Target figure paragraphs to split: {len(target_ps)}")
for idx, p, label in sorted(target_ps, key=lambda x: x[0], reverse=True):
    caption_text = "".join(r.text for r in p.runs[1:]).strip()
    print(f"Splitting {label} at P{idx}: caption='{caption_text}'")
    
    # Remove text runs from drawing paragraph
    for r in list(p.runs[1:]):
        p._element.remove(r._element)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    
    # Create caption paragraph
    new_p = doc.add_paragraph()
    set_p_text(new_p, caption_text, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)
    p._element.addnext(new_p._element)

print("Gambar 5.2 and Gambar 5.3 drawings and captions split successfully.")

# Save modified document
doc.save(MASTER_PATH)
print(f"Document saved to {MASTER_PATH}")
