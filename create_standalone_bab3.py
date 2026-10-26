# -*- coding: utf-8 -*-
"""
Script to create standalone BAB 3 METODOLOGI PENELITIAN document (.docx and .md)
and polish minor language nuances (no 'di mana', no hyperbolic words)
in both master docx and standalone docx/md for Claude's audit.
"""

from copy import deepcopy
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
STANDALONE_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_3_METODOLOGI_PENELITIAN.docx"
STANDALONE_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_3_METODOLOGI_PENELITIAN.docx"
STANDALONE_MD_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_3_METODOLOGI_PENELITIAN.md"
STANDALONE_MD_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_3_METODOLOGI_PENELITIAN.md"

BAB3_REFERENCES = [
    ("Aesthetic-4K Dataset. (2025). High-resolution aesthetic photographic image benchmark under CC-BY 4.0. Kaggle / Open Repository.", [("Aesthetic-4K Dataset. (2025). ", False), ("High-resolution aesthetic photographic image benchmark under CC-BY 4.0", True), (". Kaggle / Open Repository.", False)]),
    ("Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", [("Amdahl, G. M.", False), (" (1967). Validity of the single processor approach to achieving large scale computing capabilities. In ", False), ("Proceedings of the April 18–20, 1967, Spring Joint Computer Conference", True), (" (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", False)]),
    ("Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.", [("Intel Corporation. (2023). ", False), ("13th Generation Intel Core processor family datasheet: Volume 1 of 2", True), (". Intel Corporation.", False)]),
    ("International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.", [("International Telecommunication Union. (2011). ", False), ("Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios", True), (" (Recommendation ITU-R BT.601-7). ITU.", False)]),
    ("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614", [("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. ", False), ("Communications of the ACM", True), (", 33(5), 539–543. https://doi.org/10.1145/78607.78614", False)]),
    ("Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.", [("Pacheco, P. S., & Malensek, M. (2022). ", False), ("An introduction to parallel programming", True), (" (2nd ed.). Morgan Kaufmann.", False)]),
    ("Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", [("Python Software Foundation. (n.d.-a). ", False), ("Global interpreter lock", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", False)]),
    ("Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", [("Python Software Foundation. (n.d.-b). ", False), ("multiprocessing — Process-based parallelism", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", False)]),
    ("Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.", [("Tanenbaum, A. S., & Bos, H. (2022). ", False), ("Modern operating systems", True), (" (5th ed.). Pearson.", False)])
]

def polish_bab3_in_master(doc):
    """Polish minor language nuances in Bab 3 in the master document."""
    in_bab3 = False
    modified_count = 0
    for p in doc.paragraphs:
        txt = p.text.strip()
        if p.style.name.startswith("Heading 1") and "METODOLOGI PENELITIAN" in txt:
            in_bab3 = True
        elif p.style.name.startswith("Heading 1") and "PERANCANGAN SISTEM" in txt:
            in_bab3 = False
            break
            
        if in_bab3:
            # Check for polishing targets in runs
            # 1. keunggulan metodologis yang krusial -> keunggulan metodologis yang penting
            if "keunggulan metodologis yang krusial" in p.text:
                for r in p.runs:
                    if "krusial" in r.text:
                        r.text = r.text.replace("krusial", "penting")
                        modified_count += 1
            # 2. dari sudut pandang proses utama, di mana pada durasi eksekusi -> sehingga pada durasi eksekusi
            if "dari sudut pandang proses utama, di mana pada durasi eksekusi" in p.text:
                for r in p.runs:
                    if "di mana pada durasi eksekusi" in r.text:
                        r.text = r.text.replace("di mana pada durasi eksekusi", "sehingga pada durasi eksekusi")
                        modified_count += 1
            # 3. antar-blok (di mana Skenario A memiliki durasi baseline -> (karena Skenario A memiliki durasi baseline
            if "(di mana Skenario A memiliki durasi" in p.text:
                for r in p.runs:
                    if "(di mana Skenario A" in r.text:
                        r.text = r.text.replace("(di mana Skenario A", "(karena Skenario A")
                        modified_count += 1
            # 4. Kriteria kelulusan integritas ditetapkan secara mutlak, di mana selisih -> ditetapkan dengan kriteria biner yang ketat, yaitu selisih
            if "secara mutlak, di mana selisih" in p.text:
                for r in p.runs:
                    if "secara mutlak, di mana selisih" in r.text:
                        r.text = r.text.replace("secara mutlak, di mana selisih", "dengan kriteria biner yang ketat, yaitu selisih")
                        modified_count += 1
                        
    print(f"Polished {modified_count} language nuance occurrences in Master Bab 3.")

def generate_standalone_bab3():
    print(f"Loading master document from: {MASTER_DOCX_LOCAL}")
    doc_master = docx.Document(MASTER_DOCX_LOCAL)
    
    # Polish master first
    polish_bab3_in_master(doc_master)
    print(f"Saving polished master to local: {MASTER_DOCX_LOCAL}")
    doc_master.save(MASTER_DOCX_LOCAL)
    
    try:
        shutil.copy2(MASTER_DOCX_LOCAL, MASTER_DOCX_ONEDRIVE)
        print("Polished master copied to OneDrive successfully!")
    except Exception as e:
        print("OneDrive copy notice:", e)

    # Now create standalone document
    print("\nExtracting Bab 3 elements for standalone document...")
    body = doc_master.element.body
    elements = list(body)
    
    start_idx = None
    end_idx = None
    for i, el in enumerate(elements):
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, doc_master)
            txt = p.text.strip()
            if p.style.name.startswith('Heading 1') and 'METODOLOGI PENELITIAN' in txt:
                start_idx = i
            elif p.style.name.startswith('Heading 1') and 'PERANCANGAN SISTEM' in txt:
                end_idx = i
                break
                
    assert start_idx is not None and end_idx is not None, f"Could not find Bab 3 bounds: {start_idx}, {end_idx}"
    print(f"Found Bab 3 bounds: start={start_idx}, end={end_idx}")
    
    # Create fresh docx with 4-3-3-3 cm margins
    doc_standalone = docx.Document()
    for s in doc_standalone.sections:
        s.top_margin = Cm(4.0)
        s.left_margin = Cm(4.0)
        s.bottom_margin = Cm(3.0)
        s.right_margin = Cm(3.0)
        
    # Copy elements from start_idx to end_idx - 1 into doc_standalone
    # To copy properly, we append paragraphs and tables from master
    sectPr = doc_standalone.element.body[-1]
    for idx in range(start_idx, end_idx):
        el = elements[idx]
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p_src = docx.text.paragraph.Paragraph(el, doc_master)
            txt = p_src.text.strip()
            if not txt and idx == end_idx - 1:
                continue  # skip trailing empty paragraph
            sectPr.addprevious(deepcopy(el))
        elif tag == 'tbl':
            sectPr.addprevious(deepcopy(el))
            
    # Append DAFTAR PUSTAKA (RUJUKAN BAB 3)
    p_ref_h = doc_standalone.add_paragraph(style='Heading 1')
    p_ref_h.paragraph_format.space_before = Pt(24)
    p_ref_h.paragraph_format.space_after = Pt(12)
    p_ref_h.paragraph_format.line_spacing = 1.5
    p_ref_h.paragraph_format.first_line_indent = Cm(0)
    r_h = p_ref_h.add_run("DAFTAR PUSTAKA (RUJUKAN BAB 3)")
    r_h.font.name = 'Times New Roman'
    r_h.font.size = Pt(14)
    r_h.bold = True
    
    for plain_text, runs_spec in BAB3_REFERENCES:
        p_ref = doc_standalone.add_paragraph(style='Normal')
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
            
    print(f"Saving standalone Bab 3 docx to: {STANDALONE_DOCX_LOCAL}")
    doc_standalone.save(STANDALONE_DOCX_LOCAL)
    
    try:
        shutil.copy2(STANDALONE_DOCX_LOCAL, STANDALONE_DOCX_ONEDRIVE)
        print("Standalone Bab 3 docx copied to OneDrive successfully!")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

    # Export to clean Markdown
    print("Generating standalone Bab 3 Markdown...")
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
            if len(tbl.rows) == 1 and len(tbl.columns) == 1:
                # Placeholder box
                box_txt = tbl.rows[0].cells[0].text.strip().replace('\n', ' ')
                md_lines.append(f"\n> **{box_txt}**\n")
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
    print(f"Saved standalone Bab 3 Markdown to: {STANDALONE_MD_LOCAL}")
    
    try:
        shutil.copy2(STANDALONE_MD_LOCAL, STANDALONE_MD_ONEDRIVE)
        print("Standalone Bab 3 Markdown copied to OneDrive successfully!")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

if __name__ == '__main__':
    generate_standalone_bab3()
