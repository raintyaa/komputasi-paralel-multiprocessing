# -*- coding: utf-8 -*-
"""
Script to populate Subbab 4.2 Perancangan Algoritma Filter Spasial in Laporan Akhir.
Strictly non-destructive:
- Inserts content precisely between Heading 2 (4.2) and Heading 2 (4.3).
- Leaves Subbab 4.1, Subbab 4.3 (with Gambar 4.1), Subbab 4.4, and Subbab 4.5 100% untouched.
- Strictly adheres to PUEBI/EYD V, APA 7th, no 'di mana', passive voice, no first-person pronouns.
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

def set_cell_margins(cell, top=40, bottom=40, left=60, right=60):
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

def create_heading(doc, text, level=3, space_before=10, space_after=4):
    """Create a heading paragraph."""
    p = doc.add_paragraph(style=f'Heading {level}')
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(0)
    
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
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

def generate_subbab_4_2_elements(doc):
    """Generate all document elements for Subbab 4.2."""
    elements = []
    
    # Paragraf Pengantar Subbab 4.2
    elements.append(create_para(doc, [
        ("Perancangan algoritma filter spasial citra pada penelitian ini mencakup tiga tingkatan kompleksitas komputasi: konversi derajat keabuan (", False),
        ("Grayscale", True),
        (" ITU-R BT.601) sebagai representasi operasi titik (", False),
        ("point-wise", True),
        (") berbeban ringan, penghalusan citra (", False),
        ("Gaussian Blur", True),
        (" 3×3) sebagai representasi konvolusi spasial berbeban moderat pada tiga kanal warna, serta ekstraksi tepi (", False),
        ("Sobel", True),
        (" 3×3) sebagai representasi konvolusi gradien ganda intensif komputasi. Seluruh algoritma dirancang menggunakan kalkulasi larik NumPy murni tanpa percabangan kondisional (", False),
        ("data-independent execution", True),
        (") guna memastikan stabilitas instruksi siklus pemrosesan per piksel.", False)
    ]))
    
    # 4.2.1 Algoritma Filter Grayscale (Operasi Titik / Point-wise)
    elements.append(create_heading(doc, "4.2.1 Algoritma Filter Grayscale (Operasi Titik)", level=3))
    
    elements.append(create_para(doc, [
        ("Konversi citra digital berwarna RGB menjadi derajat keabuan dirancang berdasarkan rekomendasi standar ITU-R BT.601 (International Telecommunication Union, 2011). Operasi ini menghitung nilai intensitas luminansi monokrom ", False),
        ("Y", True),
        (" dari kombinasi linier terbobot tiga kanal warna masukan (Merah ", False),
        ("R", True),
        (", Hijau ", False),
        ("G", True),
        (", dan Biru ", False),
        ("B", True),
        (") pada setiap koordinat spasial piksel ", False),
        ("(x, y)", True),
        (". Formulasi matematis konversi dinyatakan pada Persamaan (4.1):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "Y(x, y) = 0,299 · R(x, y) + 0,587 · G(x, y) + 0,114 · B(x, y)",
        "(4.1)"
    ))
    
    elements.append(create_para(doc, [("Keterangan:", False)], space_after=2))
    eq1_notes = [
        ("Y(x, y)", " : Nilai intensitas luminansi derajat keabuan pada koordinat (x, y) bertipe uint8 [0, 255]."),
        ("R(x, y)", " : Nilai intensitas kanal warna Merah (Red) masukan [0, 255]."),
        ("G(x, y)", " : Nilai intensitas kanal warna Hijau (Green) masukan [0, 255]."),
        ("B(x, y)", " : Nilai intensitas kanal warna Biru (Blue) masukan [0, 255].")
    ]
    for sym, desc in eq1_notes:
        elements.append(create_para(doc, [(sym, True), (desc, False)], style='List Paragraph', space_before=1, space_after=1, first_line_indent=Cm(0)))
        
    elements.append(create_para(doc, [
        ("Operasi ini memiliki radius ketetanggaan kernel ", False),
        ("k = 0", True),
        (", karena kalkulasi setiap piksel bersifat independen secara spasial dan tidak membutuhkan informasi nilai piksel di sekitarnya. Pada implementasi program, larik citra masukan bertipe ", False),
        ("uint8", True),
        (" dikonversi sementara ke presisi ", False),
        ("float64", True),
        (" untuk mencegah terjadinya pemotongan galat pembulatan dini, lalu dipotong pada batas saturasi [0, 255] menggunakan fungsi ", False),
        ("numpy.clip", True),
        (" sebelum dikembalikan ke tipe ", False),
        ("uint8", True),
        (". Transformasi ini menghasilkan luaran matriks dua dimensi berukuran ", False),
        ("H × W", True),
        (" dari citra masukan tiga dimensi berukuran ", False),
        ("H × W × 3", True),
        (".", False)
    ]))
    
    # 4.2.2 Algoritma Filter Gaussian Blur 3×3 (Konvolusi Spasial Moderat)
    elements.append(create_heading(doc, "4.2.2 Algoritma Filter Gaussian Blur 3×3", level=3))
    
    elements.append(create_para(doc, [
        ("Penghalusan citra (", False),
        ("image smoothing", True),
        (") dirancang menggunakan konvolusi matriks kernel Gaussian berdimensi 3×3 berbasis koefisien binomial diskret. Matriks kernel Gaussian simetris dua dimensi ", False),
        ("K_Gauss", True),
        (" dengan faktor normalisasi 1/16 didefinisikan pada Persamaan (4.2):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "K_Gauss = (1 / 16) · [[1, 2, 1], [2, 4, 2], [1, 2, 1]]",
        "(4.2)"
    ))
    
    elements.append(create_para(doc, [
        ("Operasi konvolusi spasial diskret diterapkan secara independen pada setiap kanal warna ", False),
        ("c ∈ {R, G, B}", True),
        (" dengan radius ketetanggaan kernel ", False),
        ("k = 1", True),
        (". Formulasi nilai intensitas piksel keluaran terfilter ", False),
        ("I_blur(x, y, c)", True),
        (" dinyatakan pada Persamaan (4.3):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "I_blur(x, y, c) = Σ_(i=-1)^(1) Σ_(j=-1)^(1) K_Gauss(i + 1, j + 1) · I(x + i, y + j, c)",
        "(4.3)"
    ))
    
    elements.append(create_para(doc, [
        ("Kalkulasi dilakukan dalam representasi data presisi ", False),
        ("float64", True),
        (" dengan mengalikan 9 bobot koefisien terhadap jendela pergeseran lokal, diikuti pemotongan saturasi [0, 255] dan konversi akhir ke tipe ", False),
        ("uint8", True),
        (". Karena konvolusi diaplikasikan pada masing-masing kanal warna RGB secara terpisah, keluaran filter Gaussian Blur mempertahankan dimensi larik tiga dimensi yang identik dengan masukan, yaitu ", False),
        ("H × W × 3", True),
        (".", False)
    ]))
    
    # 4.2.3 Algoritma Filter Sobel 3×3 (Deteksi Tepi Gradien Ganda)
    elements.append(create_heading(doc, "4.2.3 Algoritma Filter Sobel 3×3", level=3))
    
    elements.append(create_para(doc, [
        ("Ekstraksi kontur dan tepi citra dirancang menggunakan operator diferensial Sobel 3×3. Pada tahap awal, citra masukan RGB dikonversi ke format monokrom melalui fungsi konversi derajat keabuan. Selanjutnya, diaplikasikan dua matriks kernel konvolusi ortogonal, yaitu kernel horizontal ", False),
        ("K_x", True),
        (" untuk mendeteksi perubahan gradien intensitas pada sumbu mendatar dan kernel vertikal ", False),
        ("K_y", True),
        (" untuk sumbu tegak, sebagaimana dirumuskan pada Persamaan (4.4):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "K_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],   K_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]",
        "(4.4)"
    ))
    
    elements.append(create_para(doc, [
        ("Komponen gradien spasial horizontal ", False),
        ("G_x(x, y)", True),
        (" dan vertikal ", False),
        ("G_y(x, y)", True),
        (" dihitung secara terpisah melalui konvolusi matriks derajat keabuan ", False),
        ("Y", True),
        (" dengan radius kernel ", False),
        ("k = 1", True),
        (" pada Persamaan (4.5) dan Persamaan (4.6):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "G_x(x, y) = Σ_(i=-1)^(1) Σ_(j=-1)^(1) K_x(i + 1, j + 1) · Y(x + i, y + j)",
        "(4.5)"
    ))
    
    elements.append(create_equation_table(
        doc,
        "G_y(x, y) = Σ_(i=-1)^(1) Σ_(j=-1)^(1) K_y(i + 1, j + 1) · Y(x + i, y + j)",
        "(4.6)"
    ))
    
    elements.append(create_para(doc, [
        ("Magnitudo gradien total ", False),
        ("G(x, y)", True),
        (" yang merepresentasikan kekuatan tepi citra dihitung menggunakan formulasi jarak Euclidean pada Persamaan (4.7):", False)
    ]))
    
    elements.append(create_equation_table(
        doc,
        "G(x, y) = √(G_x(x, y)^2 + G_y(x, y)^2)",
        "(4.7)"
    ))
    
    elements.append(create_para(doc, [
        ("Nilai magnitudo gradien ", False),
        ("G(x, y)", True),
        (" dipotong pada batas rentang [0, 255] dan dikonversi kembali ke tipe data ", False),
        ("uint8", True),
        (". Hasil akhir komputasi filter Sobel menghasilkan larik matriks dua dimensi berukuran ", False),
        ("H × W", True),
        (" yang merepresentasikan peta kontur tepi citra.", False)
    ]))
    
    # 4.2.4 Penanganan Tepi Lokal pada Partisi Submatriks
    elements.append(create_heading(doc, "4.2.4 Penanganan Tepi Lokal pada Partisi Submatriks", level=3))
    
    elements.append(create_para(doc, [
        ("Dalam arsitektur pemrosesan paralel, penanganan batas tepi matriks memiliki dua tingkatan: batas global (tepi terluar citra asli) dan batas lokal (sambungan antar-blok pekerja). Untuk batas lokal antar-pekerja, sistem menerapkan mekanisme penambahan baris batas (", False),
        ("boundary halo", True),
        (") yang dibahas pada Subbab 4.3.2. Sedangkan pada level eksekusi fungsi filter di dalam masing-masing submatriks, penanganan tepi dilakukan secara seragam menggunakan metode replikasi batas (", False),
        ("edge replication padding", True),
        (") selebar ", False),
        ("k = 1", True),
        (" piksel melalui fungsi ", False),
        ("numpy.pad(..., mode='edge')", True),
        (". Metode replikasi ini menduplikasi nilai piksel terluar ke area bantalan batas, sehingga mencegah timbulnya distorsi penggelapan piksel (", False),
        ("zero-padding darkening artifact", True),
        (") pada garis sambungan batas potongan citra saat direkonstruksi kembali.", False)
    ]))
    
    return elements

def populate_subbab_4_2():
    print("=== Populating Subbab 4.2 in Master Document ===")
    doc = docx.Document(MASTER_DOCX_LOCAL)
    body = doc.element.body
    elements = list(body)
    
    target_p4_2_idx = None
    target_p4_3_idx = None
    
    for i, el in enumerate(elements):
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, doc)
            txt = p.text.strip()
            if 'Perancangan Algoritma Filter Spasial' in txt:
                target_p4_2_idx = i
            elif 'Perancangan Arsitektur Paralel' in txt:
                target_p4_3_idx = i
                break
                
    assert target_p4_2_idx is not None and target_p4_3_idx is not None, f"Bounds not found: {target_p4_2_idx}, {target_p4_3_idx}"
    print(f"Found Subbab 4.2 at {target_p4_2_idx}, Subbab 4.3 at {target_p4_3_idx}")
    
    # Update Heading 2 for 4.2
    p4_2 = doc.paragraphs[target_p4_2_idx]
    p4_2.text = ""
    p4_2.style = 'Heading 2'
    p4_2.paragraph_format.space_before = Pt(12)
    p4_2.paragraph_format.space_after = Pt(6)
    p4_2.paragraph_format.line_spacing = 1.5
    p4_2.paragraph_format.first_line_indent = Cm(0)
    r4_2 = p4_2.add_run("4.2 Perancangan Algoritma Filter Spasial")
    r4_2.font.name = 'Times New Roman'
    r4_2.font.size = Pt(12)
    r4_2.bold = True
    
    # Generate Subbab 4.2 items in a scratch doc
    scratch_doc = docx.Document()
    items_to_insert = generate_subbab_4_2_elements(scratch_doc)
    
    # Insert before Subbab 4.3 heading element
    target_p_before = elements[target_p_3_idx] if 'target_p_3_idx' in locals() else elements[target_p4_3_idx]
    for item in items_to_insert:
        target_p_before.addprevious(item._element)
        
    print(f"Successfully inserted {len(items_to_insert)} elements into Subbab 4.2.")
    
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
    populate_subbab_4_2()
