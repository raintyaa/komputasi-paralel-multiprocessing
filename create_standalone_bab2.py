# -*- coding: utf-8 -*-
"""
Script to create standalone BAB 2 LANDASAN TEORI document (.docx and .md)
along with its APA 7th reference list, for efficient auditing with Claude.
"""

import os
import shutil
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

SRC_DOCX = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
DST_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_2_LANDASAN_TEORI.docx"
DST_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_2_LANDASAN_TEORI.docx"
DST_MD_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_2_LANDASAN_TEORI.md"
DST_MD_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_2_LANDASAN_TEORI.md"

BAB2_REFERENCES = [
    ("Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", [("Amdahl, G. M.", False), (" (1967). Validity of the single processor approach to achieving large scale computing capabilities. In ", False), ("Proceedings of the April 18–20, 1967, Spring Joint Computer Conference", True), (" (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560", False)]),
    ("Chang, L., Deng, X., & Wang, Z. (2023). Acceleration of digital image processing algorithms based on GPU. Journal of Computer and Communications, 11(10), 12–25. https://doi.org/10.4236/jcc.2023.1110002", [("Chang, L., Deng, X., & Wang, Z. (2023). Acceleration of digital image processing algorithms based on GPU. ", False), ("Journal of Computer and Communications", True), (", 11(10), 12–25. https://doi.org/10.4236/jcc.2023.1110002", False)]),
    ("Cremel, P. D. F., & Arruda, L. C. (2026). Parallel processing for computer vision and digital image processing: A systematic review. Multimedia Tools and Applications, 85(4), 11201–11235.", [("Cremel, P. D. F., & Arruda, L. C. (2026). Parallel processing for computer vision and digital image processing: A systematic review. ", False), ("Multimedia Tools and Applications", True), (", 85(4), 11201–11235.", False)]),
    ("Gonzalez, R. C., & Woods, R. E. (2018). Digital image processing (4th ed.). Pearson.", [("Gonzalez, R. C., & Woods, R. E. (2018). ", False), ("Digital image processing", True), (" (4th ed.). Pearson.", False)]),
    ("Gultom, J. M., & Sarumaha, C. A. (2025). Analisis perbandingan kinerja multithreading dan multiprocessing pada pemrosesan citra digital dengan Python. Jurnal Sistem Komputer dan Informatika (JSON), 6(3), 412–421.", [("Gultom, J. M., & Sarumaha, C. A. (2025). Analisis perbandingan kinerja multithreading dan multiprocessing pada pemrosesan citra digital dengan Python. ", False), ("Jurnal Sistem Komputer dan Informatika (JSON)", True), (", 6(3), 412–421.", False)]),
    ("Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021) (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179", [("Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In ", False), ("Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021)", True), (" (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179", False)]),
    ("Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.", [("Intel Corporation. (2023). ", False), ("13th Generation Intel Core processor family datasheet: Volume 1 of 2", True), (". Intel Corporation.", False)]),
    ("International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.", [("International Telecommunication Union. (2011). ", False), ("Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios", True), (" (Recommendation ITU-R BT.601-7). ITU.", False)]),
    ("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614", [("Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. ", False), ("Communications of the ACM", True), (", 33(5), 539–543. https://doi.org/10.1145/78607.78614", False)]),
    ("Montgomery, D. C. (2017). Design and analysis of experiments (9th ed.). John Wiley & Sons.", [("Montgomery, D. C. (2017). ", False), ("Design and analysis of experiments", True), (" (9th ed.). John Wiley & Sons.", False)]),
    ("Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.", [("Pacheco, P. S., & Malensek, M. (2022). ", False), ("An introduction to parallel programming", True), (" (2nd ed.). Morgan Kaufmann.", False)]),
    ("Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", [("Python Software Foundation. (n.d.-a). ", False), ("Global interpreter lock", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", False)]),
    ("Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", [("Python Software Foundation. (n.d.-b). ", False), ("multiprocessing — Process-based parallelism", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", False)]),
    ("Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.", [("Tanenbaum, A. S., & Bos, H. (2022). ", False), ("Modern operating systems", True), (" (5th ed.). Pearson.", False)]),
    ("Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. Journal of Imaging, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298", [("Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. ", False), ("Journal of Imaging", True), (", 10(12), Article 298. https://doi.org/10.3390/jimaging10120298", False)])
]

def generate_standalone():
    print(f"Loading source docx from: {SRC_DOCX}")
    doc = docx.Document(SRC_DOCX)
    body = doc.element.body
    elements = list(body)
    
    start_idx = None
    end_idx = None
    
    for i, el in enumerate(elements):
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, doc)
            txt = p.text.strip()
            if p.style.name.startswith('Heading 1') and 'LANDASAN TEORI' in txt:
                start_idx = i
            elif p.style.name.startswith('Heading 1') and 'METODOLOGI PENELITIAN' in txt:
                end_idx = i
                break
                
    assert start_idx is not None and end_idx is not None, f"Could not find Bab 2 bounds: {start_idx}, {end_idx}"
    print(f"Found Bab 2 bounds: start={start_idx}, end={end_idx}")
    
    # Elements before start_idx: elements[0] to elements[start_idx-1]
    # We will remove them backwards
    for i in range(start_idx - 1, -1, -1):
        body.remove(elements[i])
        
    # Re-fetch elements list
    elements_after_front_trim = list(body)
    # Find new index of Heading 1 METODOLOGI PENELITIAN
    new_end_idx = None
    for i, el in enumerate(elements_after_front_trim):
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, doc)
            txt = p.text.strip()
            if p.style.name.startswith('Heading 1') and 'METODOLOGI PENELITIAN' in txt:
                new_end_idx = i
                break
                
    print(f"New end index after front trim: {new_end_idx}")
    
    # Remove from new_end_idx up to the second-to-last element (preserving sectPr at the very end)
    total_after_front = len(elements_after_front_trim)
    for i in range(total_after_front - 2, new_end_idx - 1, -1):
        body.remove(elements_after_front_trim[i])
        
    # Now append DAFTAR PUSTAKA section at the end (before sectPr)
    p_ref_head = doc.add_paragraph(style='Heading 1')
    p_ref_head.text = "DAFTAR PUSTAKA (RUJUKAN BAB 2)"
    p_ref_head.paragraph_format.space_before = Pt(18)
    p_ref_head.paragraph_format.space_after = Pt(12)
    p_ref_head.paragraph_format.line_spacing = 1.5
    for r in p_ref_head.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.bold = True
        
    for plain_text, runs_spec in BAB2_REFERENCES:
        p_ref = doc.add_paragraph(style='Normal')
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.5
        p_ref.paragraph_format.left_indent = Cm(1.27)
        p_ref.paragraph_format.first_line_indent = Cm(-1.27)  # Hanging indent
        
        for text, italic in runs_spec:
            r = p_ref.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.italic = italic
            
    print(f"Saving standalone docx to: {DST_DOCX_LOCAL}")
    doc.save(DST_DOCX_LOCAL)
    
    print(f"Copying to OneDrive: {DST_DOCX_ONEDRIVE}")
    try:
        shutil.copy2(DST_DOCX_LOCAL, DST_DOCX_ONEDRIVE)
        print("OneDrive copy successful!")
    except Exception as e:
        print("OneDrive copy notice:", e)

    # Export to clean Markdown
    print("Exporting clean Markdown version for direct copy-paste...")
    md_lines = []
    md_lines.append("# BAB 2 LANDASAN TEORI\n")
    
    in_bab2_md = False
    doc_for_md = docx.Document(DST_DOCX_LOCAL)
    for child in doc_for_md.element.body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(child, doc_for_md)
            txt = p.text.strip()
            style = p.style.name
            if style.startswith('Heading 1'):
                if 'LANDASAN TEORI' in txt:
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
            # Check if equation table (1 row, 2 cols)
            if len(tbl.rows) == 1 and len(tbl.columns) == 2:
                eq_text = tbl.rows[0].cells[0].text.strip()
                eq_num = tbl.rows[0].cells[1].text.strip()
                md_lines.append(f"\n$$\n{eq_text} \\quad {eq_num}\n$$\n")
            else:
                # Regular markdown table
                md_lines.append("\n")
                header_cells = [c.text.strip().replace('\n', ' ') for c in tbl.rows[0].cells]
                md_lines.append("| " + " | ".join(header_cells) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(header_cells)) + " |")
                for r in tbl.rows[1:]:
                    row_cells = [c.text.strip().replace('\n', '<br>') for c in r.cells]
                    md_lines.append("| " + " | ".join(row_cells) + " |")
                md_lines.append("\n")
                
    md_content = "\n".join(md_lines)
    with open(DST_MD_LOCAL, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Saved Markdown to: {DST_MD_LOCAL}")
    
    try:
        shutil.copy2(DST_MD_LOCAL, DST_MD_ONEDRIVE)
        print("Saved Markdown to OneDrive successfully!")
    except Exception as e:
        print("OneDrive copy notice for MD:", e)

if __name__ == '__main__':
    generate_standalone()
