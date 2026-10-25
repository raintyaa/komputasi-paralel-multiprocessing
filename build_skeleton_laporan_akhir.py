# -*- coding: utf-8 -*-
import os
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def build_skeleton_laporan():
    base_dir = Path("d:/Rakha/File Kuliah/Semester 5/Komputasi Paralel/UTS")
    logo_path = base_dir / "assets" / "logo_untan.png"
    output_docx = base_dir / "Laporan_Akhir_Komparasi_Kinerja_Paralel.docx"

    doc = Document()

    # 1. SETUP PAGE DIMENSIONS & MARGINS (A4, 4-3-3-3 CM)
    sec1 = doc.sections[0]
    sec1.page_width = Cm(21.0)
    sec1.page_height = Cm(29.7)
    sec1.top_margin = Cm(3.0)
    sec1.bottom_margin = Cm(3.0)
    sec1.left_margin = Cm(4.0)
    sec1.right_margin = Cm(3.0)
    sec1.different_first_page_header_footer = True

    # Page Numbering for Section 1: lowerRoman starting at 1 (i)
    sectPr1 = sec1._sectPr
    sectPr1.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="1"/>'))

    # Footer for Section 1 normal pages: Bottom Center
    f1 = sec1.footer.paragraphs[0]
    f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f1_run = f1.add_run()
    f1_run.font.name = 'Times New Roman'
    f1_run.font.size = Pt(10)
    f1_run._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))

    # 2. CONFIGURE NUMBERING DEFINITIONS (MULTILEVEL LIST)
    numbering = doc.part.numbering_part.element

    abstract_num_xml = f"""
    <w:abstractNum {nsdecls('w')} w:abstractNumId="1">
      <w:multiLevelType w:val="multilevel"/>
      
      <!-- Level 0: BAB 1, BAB 2, ... -->
      <w:lvl w:ilvl="0">
        <w:start w:val="1"/>
        <w:numFmt w:val="decimal"/>
        <w:pStyle w:val="Heading1"/>
        <w:lvlText w:val="BAB %1  "/>
        <w:lvlJc w:val="center"/>
        <w:pPr>
          <w:jc w:val="center"/>
          <w:ind w:left="0" w:firstLine="0"/>
        </w:pPr>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
          <w:b/>
          <w:sz w:val="24"/>
        </w:rPr>
      </w:lvl>
      
      <!-- Level 1: 1.1, 1.2, ... -->
      <w:lvl w:ilvl="1">
        <w:start w:val="1"/>
        <w:numFmt w:val="decimal"/>
        <w:pStyle w:val="Heading2"/>
        <w:lvlText w:val="%1.%2  "/>
        <w:lvlJc w:val="left"/>
        <w:pPr>
          <w:ind w:left="0" w:firstLine="0"/>
        </w:pPr>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
          <w:b/>
          <w:sz w:val="24"/>
        </w:rPr>
      </w:lvl>
      
      <!-- Level 2: 1.1.1, 1.1.2, ... -->
      <w:lvl w:ilvl="2">
        <w:start w:val="1"/>
        <w:numFmt w:val="decimal"/>
        <w:pStyle w:val="Heading3"/>
        <w:lvlText w:val="%1.%2.%3  "/>
        <w:lvlJc w:val="left"/>
        <w:pPr>
          <w:ind w:left="0" w:firstLine="0"/>
        </w:pPr>
        <w:rPr>
          <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
          <w:b/>
          <w:sz w:val="24"/>
        </w:rPr>
      </w:lvl>
    </w:abstractNum>
    """
    numbering.append(parse_xml(abstract_num_xml))

    num_xml = f"""
    <w:num {nsdecls('w')} w:numId="1">
      <w:abstractNumId w:val="1"/>
    </w:num>
    """
    numbering.append(parse_xml(num_xml))

    # 3. CONFIGURE STYLES
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

    # Heading 1: BAB X JUDUL
    h1 = styles['Heading 1']
    h1.font.name = 'Times New Roman'
    h1.font.size = Pt(12)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.paragraph_format.line_spacing = 1.5
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.first_line_indent = Cm(0)
    pPr1 = h1.element.get_or_add_pPr()
    pPr1.append(parse_xml(f'<w:numPr {nsdecls("w")}><w:numId w:val="1"/><w:ilvl w:val="0"/></w:numPr>'))

    # Heading 2: X.Y Subbab
    h2 = styles['Heading 2']
    h2.font.name = 'Times New Roman'
    h2.font.size = Pt(12)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.paragraph_format.line_spacing = 1.5
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h2.paragraph_format.first_line_indent = Cm(0)
    pPr2 = h2.element.get_or_add_pPr()
    pPr2.append(parse_xml(f'<w:numPr {nsdecls("w")}><w:numId w:val="1"/><w:ilvl w:val="1"/></w:numPr>'))

    # Heading 3: X.Y.Z Anak Subbab
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
    pPr3 = h3.element.get_or_add_pPr()
    pPr3.append(parse_xml(f'<w:numPr {nsdecls("w")}><w:numId w:val="1"/><w:ilvl w:val="2"/></w:numPr>'))

    # Custom Style: Heading Non-Nomor (Bagian Depan & Bagian Akhir)
    h_non = styles.add_style('Heading Non-Nomor', WD_STYLE_TYPE.PARAGRAPH)
    h_non.base_style = styles['Normal']
    h_non.font.name = 'Times New Roman'
    h_non.font.size = Pt(12)
    h_non.font.bold = True
    h_non.font.color.rgb = RGBColor(0, 0, 0)
    h_non.paragraph_format.line_spacing = 1.5
    h_non.paragraph_format.space_before = Pt(12)
    h_non.paragraph_format.space_after = Pt(12)
    h_non.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h_non.paragraph_format.first_line_indent = Cm(0)
    pPr_non = h_non.element.get_or_add_pPr()
    pPr_non.append(parse_xml(f'<w:outlineLvl {nsdecls("w")} w:val="0"/>'))

    # Helper Functions
    def add_blank_body():
        p = doc.add_paragraph()
        p.style = 'Normal'
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        return p

    def add_front_heading(title_text):
        p = doc.add_paragraph(title_text, style='Heading Non-Nomor')
        return p

    def add_h1(title_text):
        p = doc.add_paragraph(title_text, style='Heading 1')
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:numPr {nsdecls("w")}><w:numId w:val="1"/><w:ilvl w:val="0"/></w:numPr>'))
        return p

    def add_h2(title_text):
        p = doc.add_paragraph(title_text, style='Heading 2')
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:numPr {nsdecls("w")}><w:numId w:val="1"/><w:ilvl w:val="1"/></w:numPr>'))
        return p

    def add_h3(title_text):
        p = doc.add_paragraph(title_text, style='Heading 3')
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:numPr {nsdecls("w")}><w:numId w:val="1"/><w:ilvl w:val="2"/></w:numPr>'))
        return p

    # =============================================================
    # 4. BAGIAN AWAL (FRONT MATTER)
    # =============================================================
    # --- HALAMAN SAMPUL (COVER) ---
    p_cov_type = doc.add_paragraph()
    p_cov_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_type.paragraph_format.space_before = Pt(36)
    p_cov_type.paragraph_format.space_after = Pt(12)
    r = p_cov_type.add_run("LAPORAN AKHIR PRAKTIKUM KOMPUTASI PARALEL")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True

    p_cov_title = doc.add_paragraph()
    p_cov_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_title.paragraph_format.space_before = Pt(18)
    p_cov_title.paragraph_format.space_after = Pt(36)
    r = p_cov_title.add_run("KOMPARASI KINERJA FILTER SPASIAL MENGGUNAKAN MULTIPROCESSING PYTHON: EVALUASI SPEEDUP, EFISIENSI, DAN OVERHEAD PADA RESOLUSI TINGGI")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True

    if logo_path.exists():
        p_cov_logo = doc.add_paragraph()
        p_cov_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cov_logo.paragraph_format.space_after = Pt(24)
        doc.add_picture(str(logo_path), width=Cm(4.5))

    p_cov_author = doc.add_paragraph()
    p_cov_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_author.paragraph_format.space_before = Pt(18)
    p_cov_author.paragraph_format.space_after = Pt(6)
    r = p_cov_author.add_run("Disusun Oleh:\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r = p_cov_author.add_run("Muhammad Rakha Firdaus (H1051221041)\nAhmad Dani (H1051221033)\nFarrel Dinata (H1051221008)\nGuido Leonardo Tarigan (H1051221021)")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_cov_dos = doc.add_paragraph()
    p_cov_dos.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_dos.paragraph_format.space_before = Pt(18)
    p_cov_dos.paragraph_format.space_after = Pt(24)
    r = p_cov_dos.add_run("Dosen Pengampu:\n")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r = p_cov_dos.add_run("Anggi Perwitasari, S.T., M.T.")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    p_cov_inst = doc.add_paragraph()
    p_cov_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_inst.paragraph_format.space_before = Pt(18)
    p_cov_inst.paragraph_format.space_after = Pt(0)
    r = p_cov_inst.add_run(
        "PROGRAM STUDI REKAYASA SISTEM KOMPUTER\n"
        "JURUSAN SISTEM KOMPUTER\n"
        "FAKULTAS MATEMATIKA DAN ILMU PENGETAHUAN ALAM\n"
        "UNIVERSITAS TANJUNGPURA\n"
        "PONTIANAK\n"
        "2026"
    )
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

    # --- HALAMAN JUDUL (COVER DALAM) ---
    doc.add_page_break()
    add_front_heading("HALAMAN JUDUL")
    add_blank_body()

    # --- HALAMAN PERNYATAAN KEASLIAN ---
    doc.add_page_break()
    add_front_heading("HALAMAN PERNYATAAN KEASLIAN")
    add_blank_body()

    # --- HALAMAN PENGESAHAN ---
    doc.add_page_break()
    add_front_heading("HALAMAN PENGESAHAN")
    add_blank_body()

    # --- HALAMAN PERSEMBAHAN ---
    doc.add_page_break()
    add_front_heading("HALAMAN PERSEMBAHAN")
    add_blank_body()

    # --- KATA PENGANTAR ---
    doc.add_page_break()
    add_front_heading("KATA PENGANTAR")
    add_blank_body()

    # --- ABSTRAK (BAHASA INDONESIA) ---
    doc.add_page_break()
    add_front_heading("ABSTRAK")
    add_blank_body()

    # --- ABSTRACT (BAHASA INGGRIS) ---
    doc.add_page_break()
    add_front_heading("ABSTRACT")
    add_blank_body()

    # --- DAFTAR ISI ---
    doc.add_page_break()
    add_front_heading("DAFTAR ISI")
    p_toc = doc.add_paragraph()
    p_toc._p.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="TOC \\o &quot;1-3&quot; \\h \\z \\u"/>'))

    # --- DAFTAR GAMBAR ---
    doc.add_page_break()
    add_front_heading("DAFTAR GAMBAR")
    add_blank_body()

    # --- DAFTAR TABEL ---
    doc.add_page_break()
    add_front_heading("DAFTAR TABEL")
    add_blank_body()

    # --- DAFTAR KODE PROGRAM ---
    doc.add_page_break()
    add_front_heading("DAFTAR KODE PROGRAM")
    add_blank_body()

    # --- DAFTAR SIMBOL DAN SINGKATAN ---
    doc.add_page_break()
    add_front_heading("DAFTAR SIMBOL DAN SINGKATAN")
    add_blank_body()

    # --- DAFTAR LAMPIRAN ---
    doc.add_page_break()
    add_front_heading("DAFTAR LAMPIRAN")
    add_blank_body()

    # =============================================================
    # 5. BAGIAN UTAMA (BATANG TUBUH 6 BAB - SECTION 2)
    # =============================================================
    sec2 = doc.add_section()
    sec2.different_first_page_header_footer = True
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False
    sec2.first_page_header.is_linked_to_previous = False
    sec2.first_page_footer.is_linked_to_previous = False

    # Page Numbering: Decimal starting at 1
    sectPr2 = sec2._sectPr
    sectPr2.append(parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>'))

    # Header for Normal Pages in Section 2: Top Right Page Number
    h2_p = sec2.header.paragraphs[0]
    h2_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    h2_r = h2_p.add_run()
    h2_r.font.name = 'Times New Roman'
    h2_r.font.size = Pt(10)
    h2_r._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))

    # Footer for First Page in Section 2 (Title page of BAB 1): Bottom Center
    fp2_p = sec2.first_page_footer.paragraphs[0]
    fp2_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp2_r = fp2_p.add_run()
    fp2_r.font.name = 'Times New Roman'
    fp2_r.font.size = Pt(10)
    fp2_r._r.append(parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>'))

    # --- BAB 1 PENDAHULUAN ---
    add_h1("PENDAHULUAN")
    add_h2("Latar Belakang")
    add_blank_body()
    add_h2("Rumusan Masalah")
    add_blank_body()
    add_h2("Batasan Masalah")
    add_blank_body()
    add_h2("Tujuan Penelitian")
    add_blank_body()
    add_h2("Manfaat Penelitian")
    add_blank_body()
    add_h2("Sistematika Penulisan")
    add_blank_body()

    # --- BAB 2 LANDASAN TEORI ---
    doc.add_page_break()
    add_h1("LANDASAN TEORI")
    add_h2("Perbandingan Terhadap Penelitian Terdahulu")
    add_blank_body()
    add_h2("Pengolahan Citra Digital dan Operasi Filter Spasial")
    add_h3("Konversi Ruang Warna Grayscale")
    add_blank_body()
    add_h3("Filter Perataan Linier Mean Blur 5×5")
    add_blank_body()
    add_h3("Filter Deteksi Tepi Non-Linier Sobel 3×3")
    add_blank_body()
    add_h2("Komputasi Paralel dan Multiprocessing Python")
    add_h3("Keterbatasan Global Interpreter Lock (GIL)")
    add_blank_body()
    add_h3("Arsitektur Multi-Process dan Dekomposisi Domain")
    add_blank_body()
    add_h3("Overhead Inter-Process Communication (IPC) dan Serialisasi Pickle")
    add_blank_body()
    add_h2("Metrik Evaluasi Kinerja Komputasi Paralel")
    add_h3("Waktu Eksekusi Serial dan Paralel")
    add_blank_body()
    add_h3("Speedup dan Efisiensi Relatif")
    add_blank_body()
    add_h3("Analisis Overhead Paralel")
    add_blank_body()
    add_h3("Batas Skalabilitas Berdasarkan Hukum Amdahl")
    add_blank_body()
    add_h3("Metrik Karp–Flatt dan Evaluasi Skalabilitas")
    add_blank_body()

    # --- BAB 3 METODOLOGI PENELITIAN ---
    doc.add_page_break()
    add_h1("METODOLOGI PENELITIAN")
    add_h2("Studi Literatur")
    add_blank_body()
    add_h2("Pengumpulan Data Master Citra")
    add_blank_body()
    add_h2("Analisis Kebutuhan Sistem")
    add_h3("Kebutuhan Perangkat Keras")
    add_blank_body()
    add_h3("Kebutuhan Perangkat Lunak")
    add_blank_body()
    add_h2("Prosedur Penelitian Eksperimental")
    add_h3("Protokol Pre-Warming Worker Pool")
    add_blank_body()
    add_h3("Protokol Cool-Down dan Isolasi Noise Sistem")
    add_blank_body()
    add_h3("Pengujian Interleaved Serial-Paralel (30 Repetisi)")
    add_blank_body()

    # --- BAB 4 PERANCANGAN SISTEM ---
    doc.add_page_break()
    add_h1("PERANCANGAN SISTEM")
    add_h2("Deskripsi Sistem Komputasi Paralel")
    add_blank_body()
    add_h2("Perancangan Arsitektur Sistem dan Halo Padding")
    add_h3("Pembagian Slice Citra Horizontal")
    add_blank_body()
    add_h3("Mekanisme Baris Batas (Halo Padding)")
    add_blank_body()
    add_h3("Rekonstruksi dan Sinkronisasi Citra (Barrier np.vstack)")
    add_blank_body()
    add_h2("Perancangan Parameter dan Skenario Pengujian")
    add_blank_body()
    add_h2("Perancangan Verifikasi Integritas Citra Bit-Identik")
    add_blank_body()

    # --- BAB 5 IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN ---
    doc.add_page_break()
    add_h1("IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN")
    add_h2("Implementasi Sistem dan Kode Program")
    add_blank_body()
    add_h2("Pengujian Sistem dan Analisis Hasil")
    add_h3("Skenario A: Variasi Resolusi Citra")
    add_blank_body()
    add_h3("Skenario B: Skalabilitas Jumlah Worker")
    add_blank_body()
    add_h3("Skenario C: Kompleksitas Operasi Filter")
    add_blank_body()
    add_h2("Perhitungan dan Pembuktian Model Teoretis")
    add_h3("Verifikasi Kontrol A/A pada P = 1 Worker")
    add_blank_body()
    add_h3("Estimasi Parameter Hukum Amdahl dan Metrik Karp–Flatt")
    add_blank_body()
    add_h3("Evaluasi Keterulangan Antar-Blok Pengujian")
    add_blank_body()
    add_h2("Pembahasan Temuan dan Analisis Kinerja")
    add_h3("Fenomena Superlinear pada Citra Beresolusi Kecil (Efek L3 CPU Cache Hit)")
    add_blank_body()
    add_h3("Karakteristik Skalabilitas Worker dan Titik Plateau Kinerja pada P = 8")
    add_blank_body()
    add_h3("Pengaruh Arsitektur Prosesor Hibrida (P-Core vs E-Core) dan Batasan Termal")
    add_blank_body()
    add_h3("Analisis Trade-Off Overhead Komunikasi IPC dan Utilisasi CPU")
    add_blank_body()
    add_h3("Jaminan Integritas Citra Bit-Identik")
    add_blank_body()

    # --- BAB 6 PENUTUP ---
    doc.add_page_break()
    add_h1("PENUTUP")
    add_h2("Kesimpulan")
    add_blank_body()
    add_h2("Saran")
    add_blank_body()

    # =============================================================
    # 6. BAGIAN AKHIR (BACK MATTER - SECTION 3)
    # =============================================================
    sec3 = doc.add_section()
    sec3.different_first_page_header_footer = True
    sec3.header.is_linked_to_previous = True
    sec3.footer.is_linked_to_previous = True

    # --- DAFTAR PUSTAKA ---
    add_front_heading("DAFTAR PUSTAKA")
    add_blank_body()

    # --- LAMPIRAN ---
    doc.add_page_break()
    add_front_heading("LAMPIRAN")
    add_h2("Lampiran A: Data Mentah Hasil Pengujian Benchmark (810 Iterasi)")
    add_blank_body()
    add_h2("Lampiran B: Tabel Ringkasan Metrik Kinerja Lengkap (49 Kolom × 27 Kondisi)")
    add_blank_body()
    add_h2("Lampiran C: Kode Program Implementasi Engine Komputasi Paralel")
    add_blank_body()
    add_h2("Lampiran D: Kode Program Skrip Pengujian Otomatis dan Visualisasi Data")
    add_blank_body()
    add_h2("Lampiran E: Log Spesifikasi Lingkungan Perangkat Keras dan Perangkat Lunak")
    add_blank_body()

    # SAVE DOCUMENT
    target_kerangka = base_dir / "Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
    doc.save(str(target_kerangka))
    print(f"Skeleton document successfully created at: {target_kerangka}")

    try:
        doc.save(str(output_docx))
        print(f"Also successfully overwritten main file: {output_docx}")
    except PermissionError:
        print(f"Note: Main file {output_docx.name} is currently open in Microsoft Word. Saved to {target_kerangka.name}.")

if __name__ == "__main__":
    build_skeleton_laporan()
