# -*- coding: utf-8 -*-
"""
Script to populate allowable sections of BAB 4 PERANCANGAN SISTEM from proposal.
Follows:
- UNTAN 2022 guidelines & academic paper standards
- Only allowable points from proposal Poin 6
- Zero future tense ('akan', 'diharapkan', 'direncanakan')
- Zero first-person pronouns ('penulis')
- Clean placeholder frame for Gambar 4.1 with official caption
- Times New Roman 12 pt, 1.5 spacing, 1.0 cm first-line indent, justified
- Updates OneDrive directly and mirrors to local git repository
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

def populate_bab_4_allowable():
    print(f"Loading OneDrive document from: {ONEDRIVE_PATH}")
    doc = docx.Document(ONEDRIVE_PATH)
    
    # Map target headings in Bab 4
    h_map = {}
    for i, p in enumerate(doc.paragraphs):
        txt = p.text.strip()
        if p.style.name.startswith("Heading 1") and "PERANCANGAN SISTEM" in txt:
            h_map["4.0"] = p
        elif p.style.name.startswith("Heading 2") and "Deskripsi Sistem Pemrosesan Citra Paralel" in txt:
            h_map["4.1"] = p
        elif p.style.name.startswith("Heading 2") and "Perancangan Algoritma Filter Spasial" in txt:
            h_map["4.2"] = p
        elif p.style.name.startswith("Heading 2") and "Perancangan Arsitektur Paralel" in txt:
            h_map["4.3"] = p
        elif p.style.name.startswith("Heading 3") and "Pembagian Blok Baris Horizontal" in txt:
            h_map["4.3.1"] = p
        elif p.style.name.startswith("Heading 3") and "Penanganan Baris Batas (Boundary Halo)" in txt:
            h_map["4.3.2"] = p
        elif p.style.name.startswith("Heading 3") and "Distribusi Tugas dan Sinkronisasi Proses" in txt:
            h_map["4.3.3"] = p
        elif p.style.name.startswith("Heading 3") and "Rekonstruksi Citra Utuh" in txt:
            h_map["4.3.4"] = p
        elif p.style.name.startswith("Heading 2") and "Perancangan Pengukuran dan Pencatatan Telemetri" in txt:
            h_map["4.4"] = p
        elif p.style.name.startswith("Heading 2") and "Perancangan Verifikasi Integritas Citra Bit-Identik" in txt:
            h_map["4.5"] = p
        elif p.style.name.startswith("Heading 1") and "IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN" in txt:
            h_map["5.0"] = p
            
    print(f"Mapped {len(h_map)} headings in Bab 4.")
    assert len(h_map) == 11, f"Expected 11 heading markers, found {len(h_map)}: {list(h_map.keys())}"

    def insert_items_before(target_p, items_list):
        for item in items_list:
            target_p._element.addprevious(item._element)

    # -------------------------------------------------------------
    # SUBBAB 4.1: Deskripsi Sistem Pemrosesan Citra Paralel
    # -------------------------------------------------------------
    print("Building Subbab 4.1 items...")
    sec_4_1_items = []
    
    p4_1_1 = create_para(doc, [
        ("Sistem pemrosesan citra paralel pada penelitian ini dirancang dengan menerapkan paradigma dekomposisi data (", False),
        ("data parallelism", True),
        (") guna mempercepat eksekusi operasi filter spasial pada citra digital beresolusi tinggi. Alur kerja sistem memadukan pengelolaan struktur larik multidimensi pustaka NumPy, orkestrasi proses paralel modul bawaan Python ", False),
        ("multiprocessing", True),
        (", serta pemanfaatan pustaka OpenCV yang dibatasi secara ketat hanya untuk operasi pembacaan dan penyimpanan berkas citra masukan dan luaran (", False),
        ("file I/O", True),
        ("). Guna menjamin bahwa akselerasi pemrosesan murni berasal dari alokasi proses pekerja paralel tanpa adanya campur tangan utas internal OpenCV, konkurensi internal pustaka dinonaktifkan secara permanen melalui penguncian parameter ", False),
        ("cv2.setNumThreads(1)", True),
        (".", False)
    ])
    sec_4_1_items.append(p4_1_1)
    
    p4_1_2 = create_para(doc, [
        ("Berkas citra digital berformat RGB dibaca ke dalam memori utama menggunakan fungsi ", False),
        ("cv2.imread()", True),
        (" dan direpresentasikan sebagai matriks piksel tiga dimensi berukuran ", False),
        ("H × W × C", True),
        (", di mana ", False),
        ("H", True),
        (" merepresentasikan tinggi matriks (jumlah baris piksel), ", False),
        ("W", True),
        (" merepresentasikan lebar matriks (jumlah kolom piksel), dan ", False),
        ("C", True),
        (" menyatakan jumlah kanal warna (tiga kanal untuk format warna RGB). Struktur larik NumPy dialokasikan dalam memori mengikuti urutan berbasis baris (", False),
        ("row-major order", True),
        (" atau tata letak memori ", False),
        ("C-contiguous", True),
        ("), sehingga seluruh elemen piksel yang berada pada baris horizontal yang sama menempati alamat ruang memori fisik yang berurutan secara linier. Susunan pengalamatan memori ini dirancang secara strategis guna memaksimalkan derajat lokalitas spasial (", False),
        ("spatial locality", True),
        (") dan menekan probabilitas terjadinya kegagalan pemuatan memori ", False),
        ("cache", True),
        (" (", False),
        ("cache misses", True),
        (") pada saat baris-baris piksel diakses secara berurutan oleh unit pemrosesan prosesor (Pacheco & Malensek, 2022).", False)
    ])
    sec_4_1_items.append(p4_1_2)
    
    insert_items_before(h_map["4.2"], sec_4_1_items)

    # -------------------------------------------------------------
    # SUBBAB 4.3: Perancangan Arsitektur Paralel (Bridge & Gambar 4.1)
    # -------------------------------------------------------------
    print("Building Subbab 4.3 Bridge & Placeholder items...")
    sec_4_3_items = []
    
    p4_3_bridge = create_para(doc, [
        ("Arsitektur sistem pemrosesan citra paralel dirancang dengan membagi beban komputasi secara merata ke seluruh unit proses pekerja melalui tahapan dekomposisi domain spasial horizontal, penambahan baris batas (", False),
        ("boundary halo", True),
        ("), transmisi tugas antar-proses, dan rekonstruksi kembali matriks luaran utuh. Diagram blok arsitektur sistem pemrosesan citra paralel disajikan secara skematis pada Gambar 4.1.", False)
    ])
    sec_4_3_items.append(p4_3_bridge)
    
    placeholder_g4_1 = create_image_placeholder(doc, [
        "[Area Gambar 4.1: Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel]",
        "(Diagram blok arsitektur dalam proses penyempurnaan format visual beresolusi tinggi 300 DPI untuk disematkan pada area ini)"
    ], "Gambar 4.1 Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel")
    sec_4_3_items.extend(placeholder_g4_1)
    
    insert_items_before(h_map["4.3.1"], sec_4_3_items)

    # -------------------------------------------------------------
    # SUBBAB 4.3.1: Pembagian Blok Baris Horizontal
    # -------------------------------------------------------------
    print("Building Subbab 4.3.1 items...")
    sec_4_3_1_items = []
    
    p4_3_1_1 = create_para(doc, [
        ("Dekomposisi matriks citra masukan dilakukan dengan menerapkan metode pembagian baris horizontal (", False),
        ("horizontal row partitioning", True),
        ("). Matriks citra berdimensi ", False),
        ("H × W × C", True),
        (" dipotong secara merata sepanjang sumbu vertikal ke sejumlah ", False),
        ("P", True),
        (" proses pekerja, sehingga setiap unit pekerja menerima blok data irisan citra berukuran ", False),
        ("(H/P) × W × C", True),
        (". Seluruh kombinasi dimensi tinggi citra ", False),
        ("H", True),
        (" (512, 1024, 2048, dan 4096 piksel) dan alokasi jumlah proses pekerja ", False),
        ("P", True),
        (" (1, 2, 4, dan 8 proses) yang dirancang dalam matriks pengujian memiliki sifat habis dibagi (", False),
        ("H mod P = 0", True),
        ("). Karakteristik keterbagian penuh ini memastikan bahwa setiap proses pekerja menerima volume beban piksel yang seimbang secara presisi tanpa adanya baris sisa yang dapat menimbulkan ketimpangan beban kerja (", False),
        ("load imbalance", True),
        (") antar-proses.", False)
    ])
    sec_4_3_1_items.append(p4_3_1_1)
    
    insert_items_before(h_map["4.3.2"], sec_4_3_1_items)

    # -------------------------------------------------------------
    # SUBBAB 4.3.2: Penanganan Baris Batas (Boundary Halo)
    # -------------------------------------------------------------
    print("Building Subbab 4.3.2 items...")
    sec_4_3_2_items = []
    
    p4_3_2_1 = create_para(doc, [
        ("Operasi konvolusi matriks spasial (seperti Gaussian Blur 3×3 dan Sobel 3×3) membutuhkan informasi intensitas piksel tetangga di sekeliling piksel target dengan radius spasial ", False),
        ("k = 1", True),
        (". Pada saat citra dipartisi menjadi potongan-potongan baris independen, piksel-piksel yang berada pada baris tepi atas dan bawah dari setiap potongan kehilangan akses terhadap baris tetangga aslinya. Untuk mengatasi ketergantungan data lokal tersebut tanpa menimbulkan konflik akses memori, setiap blok irisan citra diperluas dengan menambahkan ", False),
        ("k", True),
        (" baris tetangga fisik di sisi atas dan bawah yang disebut sebagai baris batas (", False),
        ("boundary halo", True),
        ("). Untuk blok interior (blok pekerja di antara batas citra terluar), ditambahkan satu baris batas atas dari blok sebelumnya dan satu baris batas bawah dari blok sesudahnya, menghasilkan potongan masukan berukuran ", False),
        ("((H/P) + 2k) × W × C", True),
        (". Adapun untuk blok pertama (paling atas), penambahan baris batas hanya dilakukan pada sisi bawah, dan untuk blok terakhir (paling bawah), penambahan baris batas hanya dilakukan pada sisi atas, masing-masing berukuran ", False),
        ("((H/P) + k) × W × C", True),
        (". Baris batas ini dibaca secara mandiri oleh proses pekerja tanpa adanya operasi penulisan balik ke proses lain, sehingga meniadakan potensi terjadinya kondisi balapan (", False),
        ("race condition", True),
        (").", False)
    ])
    sec_4_3_2_items.append(p4_3_2_1)
    
    insert_items_before(h_map["4.3.3"], sec_4_3_2_items)

    # -------------------------------------------------------------
    # SUBBAB 4.3.3: Distribusi Tugas dan Sinkronisasi Proses
    # -------------------------------------------------------------
    print("Building Subbab 4.3.3 items...")
    sec_4_3_3_items = []
    
    p4_3_3_1 = create_para(doc, [
        ("Distribusi tugas komputasi memanfaatkan modul bawaan Python ", False),
        ("multiprocessing", True),
        (". Modul ini dipilih secara khusus untuk mengatasi kendala ", False),
        ("Global Interpreter Lock", True),
        (" (GIL) pada CPython yang membatasi eksekusi ", False),
        ("multithreading", True),
        (" pada beban kerja intensif komputasi (", False),
        ("CPU-bound", True),
        (") sehingga hanya menghasilkan percepatan marjinal sekitar 1,05 kali (Gultom & Sarumaha, 2025). Modul ", False),
        ("multiprocessing", True),
        (" melangkahi hambatan GIL dengan menciptakan proses sistem operasi yang sepenuhnya independen, di mana setiap proses pekerja memiliki ruang alamat memori (", False),
        ("address space", True),
        (") dan instansiasi ", False),
        ("interpreter", True),
        (" sendiri (Tanenbaum & Bos, 2022). Mekanisme ini memungkinkan terjadinya eksekusi paralel sesungguhnya (", False),
        ("true parallelism", True),
        (") pada inti fisik prosesor ", False),
        ("multi-core", True),
        (". Seluruh blok irisan citra yang telah dilengkapi baris batas dibungkus ke dalam pasangan argumen (", False),
        ("tuple payload", True),
        (") bersama parameter filter, kemudian didistribusikan secara simultan ke kolam pekerja (", False),
        ("worker pool", True),
        (") melalui fungsi pemetaan ", False),
        ("multiprocessing.Pool.map()", True),
        (". Setiap proses pekerja mengeksekusi algoritma filter yang ditugaskan secara serentak pada blok memorinya masing-masing tanpa interupsi komunikasi antar-pekerja selama fase komputasi berlangsung.", False)
    ])
    sec_4_3_3_items.append(p4_3_3_1)
    
    insert_items_before(h_map["4.3.4"], sec_4_3_3_items)

    # -------------------------------------------------------------
    # SUBBAB 4.3.4: Rekonstruksi Citra Utuh
    # -------------------------------------------------------------
    print("Building Subbab 4.3.4 items...")
    sec_4_3_4_items = []
    
    p4_3_4_1 = create_para(doc, [
        ("Setelah setiap proses pekerja menyelesaikan eksekusi filter pada blok masing-masing, langkah krusial berikutnya adalah mengembalikan dimensi blok terfilter ke ukuran murni aslinya. Setiap proses pekerja melakukan pemotongan pembuangan (", False),
        ("halo stripping", True),
        (") terhadap baris batas atas dan baris batas bawah yang sebelumnya ditambahkan, sehingga ukuran matriks hasil kembali tepat berukuran ", False),
        ("(H/P) × W", True),
        (" (atau ", False),
        ("(H/P) × W × C", True),
        (" untuk operasi yang mempertahankan kanal warna). Blok-blok luaran yang bersih dari baris batas tersebut kemudian dikirimkan kembali ke proses utama (", False),
        ("master process", True),
        (") melalui saluran komunikasi antre pipa IPC (", False),
        ("Inter-Process Communication", True),
        ("). Proses utama selanjutnya menyatukan kembali potongan-potongan blok luaran secara sekuensial sepanjang sumbu vertikal menggunakan fungsi penggabungan larik ", False),
        ("numpy.vstack()", True),
        (". Rekonstruksi ini menghasilkan matriks citra utuh berukuran ", False),
        ("H × W", True),
        (" yang siap divalidasi dan disimpan.", False)
    ])
    sec_4_3_4_items.append(p4_3_4_1)
    
    insert_items_before(h_map["4.4"], sec_4_3_4_items)

    # -------------------------------------------------------------
    # SUBBAB 4.4: Perancangan Pengukuran dan Pencatatan Telemetri
    # (Hanya poin penempatan start & stop timestamp dari proposal)
    # -------------------------------------------------------------
    print("Building Subbab 4.4 items (proposal timestamp placement only)...")
    sec_4_4_items = []
    
    p4_4_1 = create_para(doc, [
        ("Pengukuran durasi waktu eksekusi komputasi dirancang dengan penempatan titik instrumentasi pewaktu yang ketat guna mengukur kinerja sistem secara objektif. Stempel waktu awal (", False),
        ("start timestamp", True),
        (") dicatat tepat sesaat sebelum proses partisi matriks citra dan penambahan baris batas dimulai. Seluruh tahapan partisi domain, serialisasi objek data, transmisi melalui pipa IPC, eksekusi komputasi pada kolam proses pekerja, pemotongan baris batas, pengembalian data, hingga rekonstruksi citra utuh via ", False),
        ("numpy.vstack()", True),
        (" berada di dalam jendela pengukuran waktu. Stempel waktu akhir (", False),
        ("stop timestamp", True),
        (") dicatat segera setelah matriks citra utuh berhasil disusun kembali di memori proses utama. Selisih antara stempel waktu akhir dan stempel waktu awal ditetapkan sebagai waktu eksekusi paralel aktual (", False),
        ("T_paralel", True),
        ("). Seluruh operasi pembacaan citra awal dari media penyimpanan (", False),
        ("disk reading", True),
        (") dan penulisan kembali berkas luaran ke penyimpanan (", False),
        ("disk writing", True),
        (") diisolasi sepenuhnya di luar rentang stempel waktu ini, sehingga durasi yang tercatat murni merefleksikan performa komputasi dan beban tambahan (", False),
        ("overhead", True),
        (") koordinasi paralel sistem.", False)
    ])
    sec_4_4_items.append(p4_4_1)
    
    insert_items_before(h_map["4.5"], sec_4_4_items)

    print(f"Saving updated document to OneDrive: {ONEDRIVE_PATH}")
    doc.save(ONEDRIVE_PATH)
    print("OneDrive save successful!")
    
    print(f"Mirroring updated document to local: {LOCAL_PATH}")
    shutil.copy2(ONEDRIVE_PATH, LOCAL_PATH)
    print("Local mirror successful!")

if __name__ == '__main__':
    populate_bab_4_allowable()
