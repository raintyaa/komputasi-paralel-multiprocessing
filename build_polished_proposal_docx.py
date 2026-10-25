# -*- coding: utf-8 -*-
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

def build_polished_proposal_docx():
    base_dir = Path("d:/Rakha/File Kuliah/Semester 5/Komputasi Paralel/UTS")
    logo_path = base_dir / "assets" / "logo_untan.png"
    img1_path = base_dir / "results" / "plots" / "gambar_1_arsitektur_paralel.png"
    img2_path = base_dir / "results" / "plots" / "gambar_2_bagan_alir_penelitian.png"
    output_docx = base_dir / "Proposal Komputasi Paralel.docx"

    doc = Document()

    # 1. SETUP PAGE DIMENSIONS & MARGINS (A4, 4-3-3-3 CM)
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(3.0)
    sec.bottom_margin = Cm(3.0)
    sec.left_margin = Cm(4.0)
    sec.right_margin = Cm(3.0)

    # 2. CONFIGURE STYLES
    styles = doc.styles

    # Normal Style
    normal = styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(12)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Heading 1
    h1 = styles['Heading 1']
    h1.font.name = 'Times New Roman'
    h1.font.size = Pt(12)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.paragraph_format.line_spacing = 1.5
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(4)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h1.paragraph_format.first_line_indent = Cm(0)

    # Heading 2
    h2 = styles['Heading 2']
    h2.font.name = 'Times New Roman'
    h2.font.size = Pt(12)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.paragraph_format.line_spacing = 1.5
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(3)
    h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h2.paragraph_format.first_line_indent = Cm(0)

    # Heading 3
    h3 = styles['Heading 3']
    h3.font.name = 'Times New Roman'
    h3.font.size = Pt(12)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor(0, 0, 0)
    h3.paragraph_format.line_spacing = 1.5
    h3.paragraph_format.space_before = Pt(6)
    h3.paragraph_format.space_after = Pt(2)
    h3.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h3.paragraph_format.first_line_indent = Cm(0)

    # Helper Functions
    def add_body(text=""):
        p = doc.add_paragraph()
        p.style = 'Normal'
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if text:
            p.add_run(text)
        return p

    def add_h1(text):
        p = doc.add_paragraph(text, style='Heading 1')
        return p

    def add_h2(text):
        p = doc.add_paragraph(text, style='Heading 2')
        return p

    def add_h3(text):
        p = doc.add_paragraph(text, style='Heading 3')
        return p

    def add_table_title(tbl_num, title_text):
        p = doc.add_paragraph()
        p.style = 'Normal'
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(f"Tabel {tbl_num}. {title_text}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        return p

    def add_image_title(img_num, title_text):
        p = doc.add_paragraph()
        p.style = 'Normal'
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(10)
        run = p.add_run(f"Gambar {img_num}. {title_text}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        return p

    def add_equation(eq_text, eq_num):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = tbl._tbl.tblPr
        tblPr.append(parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/></w:tblBorders>'))
        
        cell0 = tbl.cell(0, 0)
        cell0.width = Cm(12.5)
        p0 = cell0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(3)
        p0.paragraph_format.space_after = Pt(3)
        r0 = p0.add_run(eq_text)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(11)
        r0.font.italic = True
        
        cell1 = tbl.cell(0, 1)
        cell1.width = Cm(1.5)
        p1 = cell1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before = Pt(3)
        p1.paragraph_format.space_after = Pt(3)
        r1 = p1.add_run(f"({eq_num})")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11)

    def style_open_table(table, col_widths=None, alignments=None):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = table._tbl.tblPr
        tblBorders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:insideH w:val="none"/>\n'
            f'  <w:insideV w:val="none"/>\n'
            f'  <w:left w:val="none"/>\n'
            f'  <w:right w:val="none"/>\n'
            f'</w:tblBorders>'
        )
        tblPr.append(tblBorders)
        
        for idx, cell in enumerate(table.rows[0].cells):
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/></w:tcBorders>')
            tcPr.append(tcBorders)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)
                run.font.bold = True
        
        for row in table.rows[1:]:
            for col_idx, cell in enumerate(row.cells):
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.0
                if alignments and col_idx < len(alignments):
                    p.alignment = alignments[col_idx]
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(9.5)
        
        if col_widths:
            for row in table.rows:
                for col_idx, w in enumerate(col_widths):
                    if col_idx < len(row.cells):
                        row.cells[col_idx].width = w

    # --- COVER PROPOSAL ---
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(6)
    r = p_title.add_run("ANALISIS KINERJA DAN SKALABILITAS PADA OPERASI FILTER CITRA DIGITAL MENGGUNAKAN KOMPUTASI PARALEL BERBASIS MULTIPROCESSING\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(18)
    r = p_sub.add_run("PROPOSAL TUGAS AKHIR\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    if logo_path.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(24)
        doc.add_picture(str(logo_path), width=Cm(4.5))

    p_dos = doc.add_paragraph()
    p_dos.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dos.paragraph_format.space_after = Pt(12)
    r = p_dos.add_run("DOSEN PENGAMPU :\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r = p_dos.add_run("Kartika Sari, S.Kom., M.Cs")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.bold = True

    p_tim = doc.add_paragraph()
    p_tim.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tim.paragraph_format.space_after = Pt(4)
    r = p_tim.add_run("Disusun Oleh :\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)

    t_authors = doc.add_table(rows=4, cols=2)
    t_authors.alignment = WD_TABLE_ALIGNMENT.CENTER
    authors_data = [
        ("Guido Marco Silvio", "H1051241006"),
        ("Ahmad Dzaky Buhairil Ma'Arif", "H1051241074"),
        ("Muhammad Zaki Rakha Bahy", "H1051241066"),
        ("Farrel Nathannael", "H1051241094")
    ]
    for idx, (name, nim) in enumerate(authors_data):
        row = t_authors.rows[idx]
        p0 = row.cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p0.paragraph_format.line_spacing = 1.0
        r0 = p0.add_run(name)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(10)
        r0.font.bold = True

        p1 = row.cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.line_spacing = 1.0
        r1 = p1.add_run(nim)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        r1.font.bold = True

    tblPr = t_authors._tbl.tblPr
    tblPr.append(parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/></w:tblBorders>'))
    for row in t_authors.rows:
        row.cells[0].width = Cm(7.0)
        row.cells[1].width = Cm(4.0)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(36)
    p_inst.paragraph_format.space_after = Pt(0)
    r = p_inst.add_run(
        "PROGRAM STUDI REKAYASA SISTEM KOMPUTER\n"
        "FAKULTAS MATEMATIKA DAN ILMU PENGETAHUAN ALAM\n"
        "UNIVERSITAS TANJUNGPURA\n"
        "PONTIANAK\n"
        "2026"
    )
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    # --- 1. LATAR BELAKANG ---
    doc.add_page_break()
    add_h1("1. Latar Belakang")
    add_body("Teknologi kamera digital dan sensor pencitraan terus menghasilkan citra dengan matriks yang semakin besar. Citra beresolusi tinggi, misalnya 2048 × 2048 hingga 4096 × 4096 piksel, kini digunakan secara luas pada pencitraan medis (CT-Scan dan MRI), penginderaan jauh berbasis satelit, dan sistem inspeksi industri. Setiap citra tersusun atas jutaan elemen piksel yang harus diproses melalui operasi spasial seperti konvolusi. Pada deteksi tepi Sobel, misalnya, nilai setiap piksel dihitung dari piksel di sekitarnya melalui konvolusi dengan kernel, sehingga beban komputasi berbanding lurus dengan jumlah piksel. Beban ini bertambah empat kali lipat setiap kali panjang sisi citra digandakan.")
    add_body("Di sisi lain, prosesor modern telah dilengkapi banyak inti fisik (multi-core processor) yang mampu mengeksekusi instruksi secara bersamaan. Penambahan inti ini tidak otomatis mempercepat pemrosesan apabila program berjalan secara serial. Eksekusi serial hanya membebani satu inti, sementara inti lainnya menganggur, sehingga daya komputasi terbuang dan latensi pemrosesan memanjang (computational bottleneck).")
    add_body("Kebutuhan akselerasi pengolahan citra telah menjadi perhatian berbagai penelitian. Chang et al. (2023) menunjukkan bahwa operator Sobel multi-arah berkernel besar menghasilkan deteksi tepi yang lebih stabil, tetapi dengan mengorbankan kecepatan. Kernel GPU empat arah 5 × 5 yang dikembangkan dalam penelitian tersebut mencapai percepatan 6,7 hingga 13 kali dibandingkan pustaka OpenCV-GPU. Dari sisi perangkat keras, tinjauan Vasile et al. (2024) menegaskan bahwa pemrosesan citra beresolusi tinggi secara real-time membutuhkan penanganan data yang lebih cepat dan efisien. CPU konvensional yang tidak mengeksploitasi konkurensi dinilai terbatas dari sisi latensi, sehingga solusi seperti ASIC, GPU, dan FPGA dibahas sebagai alternatifnya. Paralelisme serupa sebenarnya tersedia pada CPU multi-core, tetapi pemanfaatannya di Python terkendala Global Interpreter Lock (GIL) pada CPython. Gultom dan Sarumaha (2025) menunjukkan secara empiris bahwa GIL membatasi eksekusi thread serentak pada beban kerja CPU-bound, sehingga multithreading hanya menghasilkan speedup sekitar 1,05 kali. Sebaliknya, multiprocessing menghasilkan speedup sebesar 3,16 hingga 3,55 kali pada empat proses kerja karena setiap proses memiliki ruang memori sendiri dan tidak terikat GIL.")
    add_body("Berdasarkan permasalahan tersebut, penelitian ini menerapkan komputasi paralel dengan paradigma data parallelism melalui modul multiprocessing Python dan partisi spasial horizontal (horizontal row partitioning). Pendekatan ini dipilih karena filter citra bersifat embarrassingly parallel: nilai tiap piksel keluaran hanya bergantung pada piksel masukan di sekitarnya, sehingga ketergantungan data antarproses minim. Irisan data hanya terjadi pada baris batas antar-blok (boundary halo) yang dibaca tanpa ditulis, sehingga blok dapat diproses serentak tanpa race condition. Pembagian matriks ke dalam blok horizontal mendistribusikan beban kerja ke seluruh inti fisik, sekaligus melewati batasan GIL.")
    add_body("Ketiga rujukan di atas membahas akselerasi Sobel pada GPU, akselerator perangkat keras, dan beban kerja CPU-bound Python secara umum, sehingga perilaku skalabilitas multiprocessing pada filter citra masih terbatas dan belum banyak dipetakan secara terperinci. Penelitian ini mengisi celah tersebut melalui pengujian terkontrol terhadap tiga filter (Grayscale, Gaussian Blur, dan Sobel) pada resolusi 512 × 512 hingga 4096 × 4096 piksel dengan alokasi satu, dua, empat, dan delapan proses. Parameter yang diukur meliputi waktu eksekusi, rasio percepatan (speedup), efisiensi, beban tambahan (overhead) paralel, dan utilisasi CPU, kemudian dibandingkan dengan batas skalabilitas Hukum Amdahl. Hasilnya diharapkan menjadi tolok ukur empiris bagi efektivitas komputasi paralel pada sistem komputer modern.")

    # --- 2. PERUMUSAN MASALAH ---
    add_h1("2. Perumusan Masalah")
    add_body("Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam penelitian ini adalah sebagai berikut:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. Bagaimana pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (speedup) dan efisiensi komputasi paralel berbasis multiprocessing?\n"
              "2. Bagaimana pola skalabilitas penambahan alokasi proses kerja (worker processes) pada prosesor multi-core terhadap batas percepatan teoretis Hukum Amdahl?\n"
              "3. Bagaimana pengaruh variasi tingkat kompleksitas algoritma filter citra (Grayscale, Gaussian Blur, dan Sobel) terhadap beban tambahan (overhead) paralel dan utilisasi CPU?")

    # --- 3. TUJUAN PENELITIAN ---
    add_h1("3. Tujuan Penelitian")
    add_body("Sesuai dengan rumusan masalah di atas, tujuan dari penelitian ini adalah:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. Menganalisis pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (speedup) dan efisiensi komputasi paralel berbasis multiprocessing.\n"
              "2. Mengevaluasi pola skalabilitas penambahan alokasi proses kerja (worker processes) pada prosesor multi-core terhadap batas percepatan teoretis Hukum Amdahl.\n"
              "3. Menganalisis pengaruh variasi tingkat kompleksitas algoritma filter citra (Grayscale, Gaussian Blur, dan Sobel) terhadap beban tambahan (overhead) paralel dan utilisasi CPU.")

    # --- 4. BATASAN MASALAH ---
    add_h1("4. Batasan Masalah")
    add_body("Ruang lingkup penelitian dibatasi pada hal-hal berikut:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. Citra masukan: citra digital berformat RGB tanpa kompresi dengan variasi resolusi 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.\n"
              "2. Operasi filter: tiga jenis operasi dengan tingkat kompleksitas bertingkat, yaitu Grayscale (operasi titik), Gaussian Blur dengan kernel 3 × 3 (operasi area), dan Sobel (operasi gradien).\n"
              "3. Perangkat lunak: bahasa pemrograman Python 3.14 (CPython) dengan modul bawaan multiprocessing, pustaka NumPy untuk komputasi matriks, serta OpenCV untuk I/O citra dengan pembatasan thread tunggal (cv2.setNumThreads(1)).\n"
              "4. Metode partisi: pembagian data secara horizontal (horizontal row partitioning) melalui multiprocessing.Pool() dengan penanganan baris batas (boundary halo).\n"
              "5. Lingkungan pengujian: satu unit komputer uji multi-core dengan prosesor 13th Gen Intel Core i5-13420H (8 inti fisik: 4 P-core + 4 E-core, 12 thread), memori RAM 16 GB, dan sistem operasi Windows 11 64-bit, dengan alokasi pengujian satu proses (serial sebagai baseline), dua proses, empat proses, dan delapan proses kerja.")

    # --- 5. MANFAAT PENELITIAN ---
    add_h1("5. Manfaat Penelitian")
    add_body("Hasil penelitian ini diharapkan memberikan manfaat bagi pihak-pihak berikut:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. Praktisi visi komputer dan rekayasa perangkat lunak: acuan kuantitatif mengenai ukuran citra yang layak diparalelkan, sehingga penurunan kinerja akibat beban tambahan (overhead) dapat dihindari.\n"
              "2. Industri otomasi dan pencitraan medis: data empiris tentang percepatan pra-pemrosesan citra beresolusi tinggi pada CPU multi-core tanpa memerlukan GPU.\n"
              "3. Akademisi: data empiris tentang perilaku komputasi paralel di Python serta pengujian kesesuaian hasil terhadap batas percepatan Hukum Amdahl pada prosesor multi-core.")

    # --- 6. DESKRIPSI PENELITIAN ---
    add_h1("6. Deskripsi Penelitian")
    add_body("Sistem pemrosesan citra pada penelitian ini menerapkan paradigma data parallelism untuk mempercepat filter pada citra beresolusi tinggi. Alur kerjanya memadukan larik multidimensi NumPy, modul bawaan Python multiprocessing, dan pustaka OpenCV yang hanya digunakan untuk pembacaan dan penulisan citra (I/O) dengan satu thread (cv2.setNumThreads(1)).")
    add_body("Berkas citra RGB dibaca ke memori utama dengan cv2.imread dan direpresentasikan sebagai matriks piksel tiga dimensi berukuran H × W × C (tinggi, lebar, dan jumlah kanal warna). Larik NumPy disimpan dalam urutan berbasis baris (row-major order atau C-contiguous), sehingga elemen pada satu baris menempati alamat memori yang berurutan. Susunan ini meningkatkan lokalitas spasial dan mengurangi cache miss ketika baris piksel diakses secara berurutan (Pacheco dan Malensek, 2022).")
    add_body("Pengukuran waktu dimulai sebelum matriks dipartisi (start timestamp). Matriks dibagi secara horizontal (horizontal row partitioning): tinggi citra H dibagi rata ke P proses pekerja, sehingga setiap pekerja menerima blok berukuran (H/P) × W × C. Seluruh nilai H dan P pada pengujian habis dibagi, sehingga tidak ada baris sisa. Setiap blok diperluas dengan k baris tetangga di sisi atas dan bawah (boundary halo, dengan k sesuai Persamaan (1)) agar konvolusi pada baris tepi blok tetap memakai piksel sekitarnya. Blok pertama dan terakhir hanya memiliki baris batas pada satu sisi. Blok dikirim ke worker pool melalui Pool.map().")
    add_body("Modul multiprocessing dipilih berdasarkan temuan Gultom dan Sarumaha (2025) bahwa multithreading pada Python hanya menghasilkan speedup sekitar 1,05 kali pada beban kerja CPU-bound akibat Global Interpreter Lock (GIL). Modul multiprocessing melewati batasan ini dengan membuat proses sistem operasi yang independen, masing-masing memiliki ruang alamat memori (address space) dan interpreter sendiri (Tanenbaum dan Bos, 2022). Karena itu, eksekusi paralel sesungguhnya (true parallelism) dapat berjalan pada prosesor multi-core. Setiap pekerja menjalankan filter yang ditentukan pada bloknya secara serentak: konversi Grayscale, penghalusan Gaussian Blur dengan kernel 3 × 3, atau deteksi tepi Sobel. Pada Sobel, konvolusi dilakukan dengan dua kernel gradien (arah horizontal dan vertikal), dan hasilnya digabung menjadi magnitudo gradien.")
    add_body("Setiap pekerja membuang baris batas dari hasilnya sebelum mengembalikan blok ke proses utama (master process). Proses utama menyusun ulang citra utuh dengan penggabungan vertikal (vertical concatenation, numpy.vstack). Stempel waktu akhir (stop timestamp) dicatat segera setelah citra utuh terbentuk, sehingga selisihnya menjadi waktu eksekusi paralel aktual (T_paralel).")

    if img1_path.exists():
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_before = Pt(6)
        p_img1.paragraph_format.space_after = Pt(2)
        doc.add_picture(str(img1_path), width=Cm(14.0))
        add_image_title("1", "Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel")

    add_h2("6.1. Formulasi Matematis dan Parameter Kinerja")
    add_body("Operasi filter dan parameter kinerja dirumuskan melalui enam persamaan berikut.")

    add_h3("6.1.1. Konvolusi Citra Digital 2D")
    add_body("Gaussian Blur dan Sobel diproses dengan menggeser matriks kernel di atas bidang piksel citra masukan. Mengacu pada Vasile et al. (2024), operasi ini dinyatakan pada Persamaan (1). Grayscale merupakan operasi titik sehingga tidak memerlukan persamaan ini:")
    add_equation("I_{filter}(x, y) = \\sum_{i=-k}^{k} \\sum_{j=-k}^{k} I(x+i, y+j) \\cdot K(i, j)", "1")
    add_body("Keterangan:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. I_filter(x, y) : Nilai intensitas piksel hasil pemfilteran pada koordinat spasial (x, y).\n"
              "2. I(x + i, y + j) : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (x + i, y + j).\n"
              "3. K(i, j) : Koefisien bobot matriks kernel konvolusi pada posisi relatif (i, j).\n"
              "4. k : Radius spasial matriks kernel (pada matriks kernel berukuran 3 × 3, bernilai k = 1).\n"
              "5. i, j : Indeks koordinat pergeseran spasial kernel secara vertikal dan horizontal.")
    add_body("Bentuk ini merupakan korelasi silang yang lazim disebut konvolusi pada pengolahan citra. Untuk kernel simetris seperti Gaussian, hasilnya identik dengan konvolusi sejati. Pada Sobel, perbedaannya hanya pada tanda gradien, sehingga magnitudo gradien tidak berubah.")

    add_h3("6.1.2. Rasio Percepatan (Speedup)")
    add_body("Rasio percepatan (speedup) mengukur seberapa besar komputasi paralel mempercepat penyelesaian dibandingkan eksekusi serial. Mengacu pada Pacheco dan Malensek (2022), speedup (S) dirumuskan pada Persamaan (2):")
    add_equation("S = \\frac{T_{serial}}{T_{paralel}}", "2")
    add_body("Keterangan:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. S : Nilai rasio percepatan (speedup) komputasi (rasio tanpa satuan).\n"
              "2. T_serial : Waktu eksekusi pemrosesan citra pada skrip serial murni (tanpa inisialisasi pool proses) pada satu inti prosesor (detik).\n"
              "3. T_paralel : Waktu eksekusi pemrosesan citra secara paralel pada alokasi P proses pekerja (detik).")
    add_body("T_serial dan T_paralel diukur secara selang-seling (interleaved) pada setiap repetisi, sehingga setiap nilai S dihitung dari pasangan pengukuran serial dan paralel yang berdekatan. Hasil dilaporkan sebagai median, rerata, dan simpangan baku dari 30 repetisi.")

    add_h3("6.1.3. Efisiensi Paralel (Efficiency)")
    add_body("Efisiensi mengukur persentase pemanfaatan daya komputasi tiap proses pekerja (Pacheco dan Malensek, 2022), sebagaimana dirumuskan pada Persamaan (3):")
    add_equation("E = \\left(\\frac{S}{P}\\right) \\times 100\\%", "3")
    add_body("Keterangan:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. E : Persentase efisiensi komputasi paralel (%).\n"
              "2. S : Nilai rasio percepatan (speedup) yang diperoleh dari Persamaan (2).\n"
              "3. P : Jumlah proses pekerja (worker processes) yang dialokasikan dalam eksekusi paralel.")

    add_h3("6.1.4. Beban Tambahan Paralel (Parallel Overhead)")
    add_body("Beban tambahan (overhead) paralel adalah selisih antara waktu paralel aktual dan waktu paralel ideal T_serial / P. Mengacu pada Pacheco dan Malensek (2022), T_overhead dirumuskan pada Persamaan (4):")
    add_equation("T_{overhead} = T_{paralel} - \\frac{T_{serial}}{P}", "4")
    add_body("Keterangan:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. T_overhead : Durasi beban tambahan sistem paralel akibat komunikasi antar-proses (IPC), serialisasi data NumPy (pickling), penyalinan baris batas (boundary halo), serta rekonstruksi matriks (detik).\n"
              "2. T_paralel : Waktu eksekusi paralel aktual yang terukur (detik).\n"
              "3. T_serial / P : Waktu eksekusi paralel ideal secara teoritis tanpa penalti koordinasi sistem (detik).\n"
              "4. T_serial : Waktu eksekusi serial baseline (detik).\n"
              "5. P : Jumlah proses pekerja yang dialokasikan.")

    add_h3("6.1.5. Batas Skalabilitas Berdasarkan Hukum Amdahl dan Metrik Karp–Flatt")
    add_body("Hukum Amdahl menyatakan batas percepatan teoretis suatu program berdasarkan fraksi yang tidak dapat diparalelkan (Pacheco dan Malensek, 2022), sebagaimana dinyatakan pada Persamaan (5):")
    add_equation("S_{Amdahl} = \\frac{1}{(1 - f) + \\frac{f}{P}}", "5")
    add_body("Keterangan:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. S_Amdahl : Percepatan teoretis pada P proses menurut Hukum Amdahl; untuk P → ∞ nilainya mendekati 1/(1 − f).\n"
              "2. f : Fraksi beban kerja yang dapat diparalelkan (0 ≤ f ≤ 1).\n"
              "3. (1 - f) : Fraksi efektif yang tidak mengalami percepatan, mencakup bagian sekuensial program, beban koordinasi paralel (partisi, IPC, baris batas, rekonstruksi), dan pengaruh arsitektur inti yang tidak setara.\n"
              "4. P : Jumlah proses pekerja atau inti prosesor (core) yang dialokasikan.")
    add_body("Hukum Amdahl mengasumsikan inti prosesor yang setara. Prosesor uji memiliki arsitektur hibrida (empat performance core dan empat efficient core), sehingga kurva Amdahl diperlakukan sebagai pendekatan teoretis. Nilai f diestimasi per filter dengan metode kuadrat terkecil (least squares) pada rasio percepatan Skenario B untuk P = 2, 4, dan 8, disertai selang kepercayaan 95% hasil bootstrap. Kecocokan model diperiksa dengan fraksi serial eksperimental Karp–Flatt (Karp dan Flatt, 1990), dinyatakan pada Persamaan (6):")
    add_equation("e = \\frac{\\frac{1}{S} - \\frac{1}{P}}{1 - \\frac{1}{P}}", "6")
    add_body("dengan e sebagai fraksi serial eksperimental. Nilai e yang konstan terhadap P menunjukkan kesesuaian dengan Hukum Amdahl, sedangkan e yang meningkat menunjukkan beban koordinasi yang membesar seiring P. Estimasi ini bersifat deskriptif atas data pengukuran dan bukan validasi independen.")

    # --- 7. METODE PENELITIAN ---
    doc.add_page_break()
    add_h1("7. Metode Penelitian")
    add_body("Metode penelitian ini menggunakan pendekatan eksperimen faktorial terkontrol (controlled factorial experimental research) untuk mengevaluasi kinerja dan skalabilitas komputasi paralel secara empiris. Pengujian membandingkan eksekusi serial tunggal (baseline) dengan eksekusi paralel berbasis partisi spasial pada prosesor multi-core.")

    add_h2("7.1. Tahapan Penelitian")
    add_body("Penelitian dilaksanakan dalam enam tahap sebagai berikut:")
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.add_run("1. Studi literatur, yaitu pengkajian teori komputasi paralel, mekanisme pengalamatan memori larik NumPy, arsitektur konkurensi modul Python multiprocessing, batasan Global Interpreter Lock (GIL), serta formulasi matematis filter spasial citra (Grayscale, Gaussian Blur, dan Sobel).\n"
              "2. Perancangan dan pengkodean algoritma, yaitu pengembangan dua versi perangkat lunak pengujian: skrip serial sebagai baseline dan skrip paralel yang memadukan fungsi partisi matriks horizontal dengan distribusi tugas melalui multiprocessing.Pool().\n"
              "3. Penyiapan dataset citra uji, yaitu standardisasi citra acuan master fotografi beresolusi tinggi 4K (4096 × 4096 piksel) yang bersumber dari repositori fotografi terbuka (Aesthetic-4K). Citra acuan master tersebut dipotong secara terpusat (center-crop) tanpa kompresi ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel. Waktu eksekusi ketiga filter bersifat tidak bergantung pada isi citra (data-independent) karena operasi konvolusi matriks tidak memiliki percabangan kondisional berbasis nilai piksel, sehingga satu citra acuan master memadai untuk meniadakan variabilitas tekstur dan mengisolasi variabilitas sistem komputasi (penjadwalan sistem operasi, fluktuasi termal, dan alokasi inti heterogen). Seluruh 30 sampel citra multiresolusi awal tetap diarsipkan sebagai opsi dataset alternatif.\n"
              "4. Eksekusi eksperimen terkontrol, yaitu pengujian algoritma pada sistem operasi tanpa aplikasi latar belakang yang membebani CPU. Setiap kombinasi perlakuan pengujian dieksekusi sebanyak 30 kali repetisi terkontrol secara selang-seling (interleaved) antara pengukuran serial dan paralel pada masing-masing tingkatan resolusi guna memperoleh estimasi parameter statistik yang stabil dan representatif (median, rerata, simpangan baku, dan selang kepercayaan 95%). Pengukuran durasi komputasi murni memanfaatkan arsitektur pre-warmed pool untuk meniadakan penalti inisialisasi proses (cold spawn) pada Windows, serta dilengkapi jeda pendinginan termal CPU (cool-down buffer) antar-filter guna meminimalkan pelambatan termal (thermal throttling). Pergeseran waktu eksekusi antar-blok pengujian (di mana Skenario A dijalankan pertama dan memiliki baseline serial sedikit lebih lambat) dicatat sebagai batasan pengujian.\n"
              "5. Pencatatan parameter kinerja, yaitu pengukuran waktu komputasi murni dengan time.perf_counter(), pemantauan utilisasi CPU diukur pada proses utama menggunakan modul psutil sebagai estimasi tren beban kerja sistem secara keseluruhan, serta penghitungan speedup, efisiensi, dan overhead paralel.\n"
              "6. Analisis skalabilitas dan penarikan kesimpulan, yaitu penyajian data dalam kurva komparatif, evaluasi kurva percepatan terhadap batas teoretis Hukum Amdahl, serta penarikan kesimpulan tentang efektivitas komputasi paralel pada berbagai ukuran data dan kompleksitas filter.")

    if img2_path.exists():
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(6)
        p_img2.paragraph_format.space_after = Pt(2)
        doc.add_picture(str(img2_path), width=Cm(14.0))
        add_image_title("2", "Diagram Alir Proses Penelitian")

    add_h2("7.2. Desain Eksperimen dan Skenario Pengujian")
    add_body("Setiap operasi filter diuji pada variasi ukuran data dan alokasi proses kerja yang dirinci dalam tiga skenario berikut.")

    add_h3("7.2.1. Skenario A: Variasi Dimensi Citra")
    add_body("Alokasi proses kerja dikunci pada empat proses (Pool(processes=4)). Resolusi citra dinaikkan bertahap dengan sisi berlipat dua pada setiap langkah, dari 512 × 512 hingga 4096 × 4096 piksel, pada ketiga filter (Grayscale, Gaussian Blur, dan Sobel). Skenario ini menganalisis pengaruh ukuran matriks terhadap rasio speedup pada tiap karakteristik operasi. Matriks pengujian dirangkum pada Tabel 1.")

    add_table_title("1", "Matriks Pengujian Skenario A (Variasi Dimensi Citra)")
    t1_data = [
        ["Kode Uji", "Resolusi Citra (Piksel)", "Total Elemen Matriks", "Jenis Operasi yang Diuji", "Alokasi Proses", "Replikasi Pengujian"],
        ["A1", "512 × 512", "262.144", "Grayscale, Gaussian Blur, Sobel", "4 Proses", "1 Citra Acuan Master (30x Repetisi)"],
        ["A2", "1024 × 1024", "1.048.576", "Grayscale, Gaussian Blur, Sobel", "4 Proses", "1 Citra Acuan Master (30x Repetisi)"],
        ["A3", "2048 × 2048", "4.194.304", "Grayscale, Gaussian Blur, Sobel", "4 Proses", "1 Citra Acuan Master (30x Repetisi)"],
        ["A4", "4096 × 4096", "16.777.216", "Grayscale, Gaussian Blur, Sobel", "4 Proses", "1 Citra Acuan Master (30x Repetisi)"]
    ]
    tbl1 = doc.add_table(rows=len(t1_data), cols=6)
    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            tbl1.rows[r_idx].cells[c_idx].paragraphs[0].add_run(val)
    style_open_table(tbl1, [Cm(1.8), Cm(2.5), Cm(2.2), Cm(3.2), Cm(2.0), Cm(2.8)], 
                     [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    add_h3("7.2.2. Skenario B: Variasi Alokasi Proses Kerja")
    add_body("Dimensi citra dikunci pada 2048 × 2048 piksel. Alokasi proses kerja divariasikan dari satu proses (baseline serial), dua proses, empat proses, hingga delapan proses pada ketiga filter. Kondisi satu proses (B0) dijalankan sebagai kontrol serial terhadap serial (A/A control), yaitu dua pengukuran serial independen, untuk memperkirakan variasi alami sistem. Skenario ini memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan menguji apakah operasi berbeban berat (Sobel) lebih mendekati percepatan linear daripada operasi ringan (Grayscale). Matriks pengujian disajikan pada Tabel 2.")

    add_table_title("2", "Matriks Pengujian Skenario B (Variasi Alokasi Proses Kerja)")
    t2_data = [
        ["Kode Uji", "Alokasi Proses Kerja", "Mode Eksekusi", "Jenis Operasi yang Diuji", "Dimensi Citra", "Replikasi Pengujian"],
        ["B0", "1 Proses", "Mode Serial (Kontrol A/A)", "Grayscale, Gaussian Blur, Sobel", "2048 × 2048", "1 Citra Acuan Master (30x Repetisi)"],
        ["B1", "2 Proses", "Mode Paralel (Dual-Process)", "Grayscale, Gaussian Blur, Sobel", "2048 × 2048", "1 Citra Acuan Master (30x Repetisi)"],
        ["B2", "4 Proses", "Mode Paralel (Quad-Process)", "Grayscale, Gaussian Blur, Sobel", "2048 × 2048", "1 Citra Acuan Master (30x Repetisi)"],
        ["B3", "8 Proses", "Mode Paralel (Octa-Process)", "Grayscale, Gaussian Blur, Sobel", "2048 × 2048", "1 Citra Acuan Master (30x Repetisi)"]
    ]
    tbl2 = doc.add_table(rows=len(t2_data), cols=6)
    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            tbl2.rows[r_idx].cells[c_idx].paragraphs[0].add_run(val)
    style_open_table(tbl2, [Cm(1.8), Cm(2.2), Cm(2.8), Cm(3.2), Cm(2.0), Cm(2.8)], 
                     [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    add_h3("7.2.3. Skenario C: Variasi Jenis Operasi Filter")
    add_body("Skenario C dijalankan sebagai blok pengujian terpisah pada resolusi 2048 × 2048 piksel dengan empat proses, dan hasilnya dibandingkan dengan titik uji A3 dan B2 untuk memeriksa keterulangan. Skenario C membandingkan kompleksitas matematis tiap algoritma dengan efisiensi, beban tambahan (overhead), dan utilisasi CPU yang dihasilkannya. Ketiga tingkat beban algoritma dirinci pada Tabel 3.")

    add_table_title("3", "Klasifikasi Tingkat Kompleksitas Operasi Filter Citra")
    t3_data = [
        ["Kode", "Jenis Operasi Filter", "Karakteristik Perhitungan Matematis", "Tingkat Kompleksitas", "Kondisi Titik Uji Komparasi"],
        ["C1", "Konversi Grayscale", "Operasi Titik Matematis Tunggal (1 × 1) per piksel", "Ringan", "Resolusi 2048 px (1 vs 4 proses)"],
        ["C2", "Gaussian Blur", "Konvolusi Matriks Ketetanggaan Kernel (3 × 3)", "Moderat", "Resolusi 2048 px (1 vs 4 proses)"],
        ["C3", "Deteksi Tepi Sobel", "Gradien Turunan Parsial Ganda (Gx dan Gy)", "Berat", "Resolusi 2048 px (1 vs 4 proses)"]
    ]
    tbl3 = doc.add_table(rows=len(t3_data), cols=5)
    for r_idx, row in enumerate(t3_data):
        for c_idx, val in enumerate(row):
            tbl3.rows[r_idx].cells[c_idx].paragraphs[0].add_run(val)
    style_open_table(tbl3, [Cm(1.5), Cm(2.8), Cm(4.5), Cm(2.2), Cm(3.5)], 
                     [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    add_h2("7.3. Parameter Kinerja yang Diuji")
    add_body("Efektivitas komputasi paralel dievaluasi melalui lima parameter kinerja pada Tabel 4. Setiap parameter dilaporkan sebagai median, rerata (x̄), simpangan baku (s), dan selang kepercayaan 95% dari 30 kali repetisi pada masing-masing kombinasi perlakuan.")

    add_table_title("4", "Parameter Kinerja Pengujian Komputasi Paralel")
    t4_data = [
        ["Nama Parameter", "Notasi", "Definisi Operasional", "Satuan"],
        ["Waktu Eksekusi", "T", "Durasi waktu yang dibutuhkan untuk menyelesaikan kalkulasi filter citra pada pengujian terkontrol", "Detik (s) / Milidetik (ms)"],
        ["Rasio Percepatan", "S", "Perbandingan kelipatan kecepatan antara waktu eksekusi serial terhadap waktu paralel", "Rasio (Tanpa satuan)"],
        ["Efisiensi Paralel", "E", "Persentase daya pemanfaatan inti prosesor terhadap percepatan yang diraih", "Persen (%)"],
        ["Utilisasi CPU", "%CPU", "Rata-rata beban pemakaian daya komputasi di seluruh inti prosesor selama eksekusi", "Persen (%)"],
        ["Beban Tambahan", "T_overhead", "Selisih waktu keterlambatan akibat partisi data di memori dan komunikasi proses", "Detik (s)"]
    ]
    tbl4 = doc.add_table(rows=len(t4_data), cols=4)
    for r_idx, row in enumerate(t4_data):
        for c_idx, val in enumerate(row):
            tbl4.rows[r_idx].cells[c_idx].paragraphs[0].add_run(val)
    style_open_table(tbl4, [Cm(3.0), Cm(2.0), Cm(7.5), Cm(2.5)], 
                     [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])

    # --- DAFTAR PUSTAKA ---
    doc.add_page_break()
    add_h1("DAFTAR PUSTAKA")
    
    pustaka_items = [
        "Aesthetic-4K Dataset. (2025). High-resolution uncompressed image repository for visual computing research. Creative Commons CC-BY 4.0.",
        "Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). Multi-directional Sobel operator kernel on GPUs. arXiv preprint arXiv:2305.00515. https://doi.org/10.48550/arXiv.2305.00515",
        "Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. JICDA: Journal of Informatics, Computer Science, Data Science and Artificial Intelligence, 3(2), 55–64. https://doi.org/10.51505/jicda.2025.3202",
        "Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614",
        "Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.",
        "Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.",
        "Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. Journal of Imaging, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298"
    ]
    for item in pustaka_items:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(-1.27)
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(item)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

    output_docx = base_dir / "Proposal Komputasi Paralel_revisi_audit.docx"
    doc.save(str(output_docx))
    print(f"Successfully built polished proposal docx to: {output_docx}")
    
    # Try saving to original file if possible
    orig_docx = base_dir / "Proposal Komputasi Paralel.docx"
    try:
        doc.save(str(orig_docx))
        print(f"Also successfully overwritten original file: {orig_docx}")
    except PermissionError:
        print(f"Original file {orig_docx.name} is currently open in Word. Saved to {output_docx.name}.")

if __name__ == "__main__":
    build_polished_proposal_docx()
