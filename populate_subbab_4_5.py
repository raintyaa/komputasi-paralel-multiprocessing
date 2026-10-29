# -*- coding: utf-8 -*-
"""
Script to populate Subbab 4.5 Perancangan Verifikasi Integritas Citra Bit-Identik in Laporan Akhir.
Strictly non-destructive:
- Replaces element 321 (between Heading 2 4.5 and the page break before Bab 5) with complete Subbab 4.5 text and Equation (4.8).
- Leaves Subbab 4.1, Subbab 4.2, Subbab 4.3 (with Gambar 4.1), Subbab 4.4 (with Tabel 4.1), and Bab 5 100% untouched.
- Strictly adheres to PUEBI/EYD V, APA 7th, no 'di mana', passive voice, no first-person pronouns, zero AI-slop hype words.
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

def create_para(doc, runs_spec, style='Normal', space_before=0, space_after=6, 
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

def create_equation_table(doc, eq_runs, eq_number_text):
    """Create a borderless table for equations with centered equation and right-aligned number."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Borderless
    tblPr = tbl._element.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    
    row = tbl.rows[0]
    cell_eq, cell_num = row.cells[0], row.cells[1]
    cell_eq.width = Cm(13.5)
    cell_num.width = Cm(1.5)
    set_cell_margins(cell_eq, top=40, bottom=40, left=20, right=20)
    set_cell_margins(cell_num, top=40, bottom=40, left=20, right=20)
    
    p_eq = cell_eq.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq.paragraph_format.space_before = Pt(4)
    p_eq.paragraph_format.space_after = Pt(4)
    p_eq.paragraph_format.line_spacing = 1.15
    p_eq.paragraph_format.first_line_indent = Cm(0)
    
    for item in eq_runs:
        if isinstance(item, str):
            text, italic, bold = item, False, False
        elif len(item) == 2:
            text, italic = item
            bold = False
        else:
            text, italic, bold = item
        r = p_eq.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.italic = italic
        r.bold = bold
        
    p_num = cell_num.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_before = Pt(4)
    p_num.paragraph_format.space_after = Pt(4)
    p_num.paragraph_format.line_spacing = 1.15
    p_num.paragraph_format.first_line_indent = Cm(0)
    r_num = p_num.add_run(eq_number_text)
    r_num.font.name = 'Times New Roman'
    r_num.font.size = Pt(12)
    
    return tbl

def generate_subbab_4_5_elements(doc):
    """Generate all document elements for Subbab 4.5."""
    elements = []
    
    # Paragraf 1: Urgensi dan Peran Metodologis Verifikasi Bit-Identik
    elements.append(create_para(doc, [
        ("Perancangan verifikasi integritas citra bertujuan menjaga keabsahan luaran hasil komputasi paralel agar identik hingga level bit (", False),
        ("bit-identical", True),
        (") terhadap citra hasil komputasi serial acuan (", False),
        ("ground truth baseline", True),
        ("). Dekomposisi domain spasial berbasis partisi baris horizontal, serialisasi data antar-proses melalui saluran pipa ", False),
        ("Inter-Process Communication", True),
        (" (IPC), penambahan baris batas (", False),
        ("boundary halo", True),
        ("), hingga rekonstruksi matriks utuh melalui ", False),
        ("numpy.vstack", True),
        (" membawa risiko timbulnya artefak spasial, distorsi pergeseran baris, maupun diskontinuitas nilai piksel antarsubmatriks apabila batas partisi tidak ditangani secara tepat. Verifikasi bit-identik membuktikan bahwa kelipatan percepatan komputasi (", False),
        ("speedup", True),
        (") paralel dicapai murni melalui konkurensi eksekusi perangkat keras, tanpa degradasi kualitas citra, kehilangan informasi spasial, atau kompromi ketepatan numerik. Prosedur verifikasi ini diterapkan pada seluruh 720 pasangan pengujian serial-paralel dan 90 pasangan kontrol A/A (sehingga mencakup 810 pasangan pengujian secara individual).", False)
    ]))
    
    # Paragraf 2: Alur Kerja Dua Tahap (Dimensi dan Numerik Bebas Wraparound)
    elements.append(create_para(doc, [
        ("Alur kerja verifikasi integritas citra dirancang melalui dua tahapan inspeksi berurutan. Tahap pertama adalah verifikasi keselarasan geometri matriks, yaitu memeriksa kesesuaian atribut dimensi (", False),
        ("shape", True),
        (") matriks citra keluaran paralel (", False),
        ("I_paralel", True),
        (") terhadap matriks serial (", False),
        ("I_serial", True),
        ("), mencakup tinggi matriks (", False),
        ("H", True),
        ("), lebar matriks (", False),
        ("W", True),
        ("), dan jumlah kanal warna (", False),
        ("C", True),
        ("). Ketidaksesuaian dimensi mengindikasikan kegagalan pada mekanisme pemangkasan baris batas (", False),
        ("halo stripping", True),
        (") atau rekonstruksi partisi domain. Tahap kedua adalah evaluasi disparitas nilai piksel. Karena representasi citra digital menggunakan tipe data bilangan bulat tak bertanda 8-bit (", False),
        ("uint8", True),
        ("), operasi pengurangan langsung ", False),
        ("I_paralel - I_serial", True),
        (" rentan mengalami anomali luapan bawah (", False),
        ("integer underflow / modulo wraparound", True),
        ("), seperti nilai intensitas ", False),
        ("0 - 1", True),
        (" yang membungkus menjadi 255 pada format ", False),
        ("uint8", True),
        (". Guna mencegah galat interpretasi tersebut, matriks citra dikonversi terlebih dahulu ke tipe data bilangan riil presisi ganda bertanda (", False),
        ("float64", True),
        (") sebelum operasi diferensiasi matriks dieksekusi.", False)
    ]))
    
    # Paragraf 3: Formulasi Kriteria Kelulusan Bit-Identik dan Persamaan (4.8)
    elements.append(create_para(doc, [
        ("Disparitas absolut maksimum (", False),
        ("Δ_max", True),
        (") dihitung guna mendeteksi deviasi nilai piksel paling ekstrem di seluruh koordinat spasial citra, sebagaimana diformulasikan pada Persamaan (4.8).", False)
    ]))
    
    # Persamaan (4.8)
    elements.append(create_equation_table(doc, [
        ("Δ_max = max | I_paralel(x, y) - I_serial(x, y) |", True),
        ("   untuk seluruh  (x, y)", False)
    ], "(4.8)"))
    
    # Paragraf 4: Kriteria Evaluasi dan Penanda Status Telemetri
    elements.append(create_para(doc, [
        ("Kriteria kelulusan integritas citra ditetapkan secara biner tanpa toleransi deviasi numerik (", False),
        ("Δ_max = 0", True),
        ("). Evaluasi kesetaraan seluruh elemen matriks dieksekusi melalui fungsi deterministik ", False),
        ("numpy.array_equal(I_paralel, I_serial)", True),
        (". Apabila kriteria ", False),
        ("Δ_max = 0", True),
        (" terpenuhi, atribut ", False),
        ("is_identical", True),
        (" pada rekaman telemetri dicatat bernilai ", False),
        ("True", True),
        (" dan atribut ", False),
        ("max_diff", True),
        (" bernilai 0,0. Sebaliknya, apabila ", False),
        ("Δ_max > 0", True),
        (", atribut ", False),
        ("is_identical", True),
        (" dicatat bernilai ", False),
        ("False", True),
        (", nilai deviasi maksimum direkam pada atribut ", False),
        ("max_diff", True),
        (", dan iterasi tersebut ditandai sebagai anomali komputasi.", False)
    ]))
    
    # Paragraf 5: Isolasi Prosedur Verifikasi di Luar Jendela Pewaktuan
    elements.append(create_para(doc, [
        ("Seluruh prosedur verifikasi integritas citra bit-identik ditempatkan secara terisolasi di luar jendela pengukuran waktu komputasi, yaitu setelah stempel waktu akhir (", False),
        ("t_stop", True),
        (") dicatat oleh fungsi pewaktu ", False),
        ("time.perf_counter()", True),
        (". Dengan arsitektur isolasi ini, beban komputasi tambahan yang timbul akibat konversi tipe data ke ", False),
        ("float64", True),
        (", pengurangan matriks piksel, dan pemindaian nilai ekstrem tidak membebani catatan durasi waktu eksekusi paralel (", False),
        ("T_paralel", True),
        (") maupun metrik percepatan komputasi yang dihimpun pada sistem telemetri.", False)
    ]))
    
    return elements

def populate_subbab_4_5():
    print("=== Populating Subbab 4.5 in Master Document ===")
    doc = docx.Document(MASTER_DOCX_LOCAL)
    body = doc.element.body
    elements = list(body)
    
    target_p4_5_idx = None
    target_bab5_break_idx = None
    
    for i, el in enumerate(elements):
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, doc)
            txt = p.text.strip()
            if 'Perancangan Verifikasi Integritas Citra Bit-Identik' in txt:
                target_p4_5_idx = i
            elif target_p4_5_idx is not None and ('IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN' in txt or 'BAB V' in txt or 'BAB 5' in txt):
                # The page break element is right before this heading
                target_bab5_break_idx = i - 1
                break
                
    assert target_p4_5_idx is not None and target_bab5_break_idx is not None, f"Bounds not found: {target_p4_5_idx}, {target_bab5_break_idx}"
    print(f"Found Subbab 4.5 at element {target_p4_5_idx}, Bab 5 page break at element {target_bab5_break_idx}")
    print(f"Elements between 4.5 and page break to be replaced: {target_bab5_break_idx - target_p4_5_idx - 1}")
    
    # Verify Heading 2 for 4.5
    p4_5 = docx.text.paragraph.Paragraph(elements[target_p4_5_idx], doc)
    p4_5.text = ""
    p4_5.style = 'Heading 2'
    p4_5.paragraph_format.space_before = Pt(12)
    p4_5.paragraph_format.space_after = Pt(6)
    p4_5.paragraph_format.line_spacing = 1.5
    p4_5.paragraph_format.first_line_indent = Cm(0)
    r4_5 = p4_5.add_run("4.5 Perancangan Verifikasi Integritas Citra Bit-Identik")
    r4_5.font.name = 'Times New Roman'
    r4_5.font.size = Pt(12)
    r4_5.bold = True
    
    # Generate Subbab 4.5 items
    scratch_doc = docx.Document()
    items_to_insert = generate_subbab_4_5_elements(scratch_doc)
    
    # Insert before Bab 5 page break element
    target_break_el = elements[target_bab5_break_idx]
    for item in items_to_insert:
        target_break_el.addprevious(item._element)
        
    # Remove old elements between target_p4_5_idx + 1 and target_bab5_break_idx - 1
    for i in range(target_p4_5_idx + 1, target_bab5_break_idx):
        body.remove(elements[i])
        
    print(f"Successfully inserted {len(items_to_insert)} elements into Subbab 4.5 and removed old elements.")
    
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
    populate_subbab_4_5()
