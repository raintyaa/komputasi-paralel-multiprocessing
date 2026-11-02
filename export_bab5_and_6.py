import docx, sys, re

sys.stdout.reconfigure(encoding='utf-8')

MASTER_PATH = 'UTS/Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx'
OUT_DOCX = 'UTS/BAB_5_SELURUHNYA_DAN_BAB_6.docx'
OUT_MD = 'UTS/BAB_5_SELURUHNYA_DAN_BAB_6.md'

doc_master = docx.Document(MASTER_PATH)
body = doc_master._body._element

# Find exact start of Bab 5 (Heading 1)
start_elem_idx = None
for idx, child in enumerate(body):
    if child.tag.endswith('p'):
        p = docx.text.paragraph.Paragraph(child, doc_master)
        if 'heading 1' in p.style.name.lower() and 'IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN' in p.text:
            start_elem_idx = idx
            break

print(f"Actual Bab 5 Heading 1 starts at body element index {start_elem_idx} (total elements: {len(body)})")

# Build Markdown text
md_lines = []

for idx in range(start_elem_idx, len(body)):
    child = body[idx]
    tag = child.tag.split('}')[-1]
    
    if tag == 'p':
        p = docx.text.paragraph.Paragraph(child, doc_master)
        txt = p.text.strip()
        if not txt:
            if len(p._element.xpath('.//w:drawing')) > 0:
                md_lines.append("\n*[Gambar disematkan di dokumen docx]*\n")
            continue
            
        style = p.style.name.lower()
        if 'heading 1' in style:
            md_lines.append(f"\n# {txt}\n")
        elif 'heading 2' in style:
            md_lines.append(f"\n## {txt}\n")
        elif 'heading 3' in style:
            md_lines.append(f"\n### {txt}\n")
        elif 'kode program' in txt.lower():
            md_lines.append(f"\n**{txt}**\n")
        elif txt.startswith('Tabel 5.') or txt.startswith('Tabel 6.'):
            md_lines.append(f"\n**{txt}**\n")
        elif txt.startswith('Gambar 5.') or txt.startswith('Gambar 6.'):
            md_lines.append(f"\n*{txt}*\n")
        elif txt.startswith('Keterangan:'):
            md_lines.append(f"\n*{txt}*\n")
        else:
            md_lines.append(f"{txt}\n")
            
    elif tag == 'tbl':
        t = docx.table.Table(child, doc_master)
        if len(t.rows) == 1 and len(t.columns) == 1:
            # Code table
            code_str = t.rows[0].cells[0].text
            md_lines.append(f"```python\n{code_str}\n```\n")
        else:
            # Data table -> markdown table
            headers = [c.text.strip().replace('\n', ' ') for c in t.rows[0].cells]
            md_lines.append("\n| " + " | ".join(headers) + " |")
            md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for row in t.rows[1:]:
                vals = [c.text.strip().replace('\n', ' ') for c in row.cells]
                md_lines.append("| " + " | ".join(vals) + " |")
            md_lines.append("\n")

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write("\n".join(md_lines))
print(f"Markdown extracted to {OUT_MD} ({len(md_lines)} lines)")

# Create standalone docx
doc_standalone = docx.Document(MASTER_PATH)
body_st = doc_standalone._body._element

st_start = None
for idx, child in enumerate(body_st):
    if child.tag.endswith('p'):
        p = docx.text.paragraph.Paragraph(child, doc_standalone)
        if 'heading 1' in p.style.name.lower() and 'IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN' in p.text:
            st_start = idx
            break

elements_to_remove = [body_st[i] for i in range(st_start)]
for elem in elements_to_remove:
    body_st.remove(elem)

doc_standalone.save(OUT_DOCX)
print(f"Standalone docx saved to {OUT_DOCX}")
