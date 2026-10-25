# -*- coding: utf-8 -*-
import docx

doc_path = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
doc = docx.Document(doc_path)

p153 = doc.paragraphs[153]
p153.text = "Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp\u2013Flatt"
p153.runs[0].font.name = "Times New Roman"
p153.runs[0].font.size = docx.shared.Pt(12)
p153.runs[0].bold = True

p237 = doc.paragraphs[237]
p237.text = "Lampiran B: Tabel Ringkasan Metrik Kinerja Lengkap (49 Kolom \u00d7 27 Kondisi)"
p237.runs[0].font.name = "Times New Roman"
p237.runs[0].font.size = docx.shared.Pt(12)
p237.runs[0].bold = True

doc.save(doc_path)
print("Saved clean UTF-8 characters successfully!")
