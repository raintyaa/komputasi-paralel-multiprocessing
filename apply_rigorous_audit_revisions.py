# -*- coding: utf-8 -*-
"""
Script to apply rigorous audit revisions to Subbab 5.5 and Bab 6 in master docx.
Based on verified empirical findings from Claude's audit:
1. Bathtub curve & rebound removed; empirical multi-block stabilization at 2.2x-2.9x documented.
2. Superlinear claims toned down to "approaching linear ideal (S ≈ P)", mean vs median clarified, A/A noise scope corrected.
3. Cache explanation clarified (L2 working set vs shared L3, capacity misses, memory bus bandwidth).
4. Arithmetic intensity corrected: Gaussian (51 ops/px, 8.5 FLOP/byte) > Sobel (26-31 ops/px, 6.5 FLOP/byte); Sobel speedup advantage attributed to 1-ch (4.19MB) vs 3-ch (12.58MB) output payload.
5. Scenario C causality moderated to "consistent with data payload and local array memory allocation".
6. Karp-Flatt evaluated accurately: e jump unique to Sobel, P/E-core heterogeneity framed as working hypothesis.
7. CPU utilization treated as coarse global indicator without unverified per-core 100% saturation claims.
8. Literature comparisons cleaned up: Cremel "deteksi tepi" and no-lock correction; Gultom workload caveats; Chang baseline caveat.
9. All foreign technical terms italicized, raw LaTeX converted to clean academic notation, clichés eliminated.
"""

import sys
import os
import shutil
import docx
import re
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

sys.stdout.reconfigure(encoding='utf-8')

MASTER_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
MASTER_ONEDRIVE = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"

def set_para(p, text, style_name='Normal', align=WD_ALIGN_PARAGRAPH.JUSTIFY, 
             space_before=0, space_after=0, line_spacing=1.5, indent=Cm(1.0), bold=False, italic_terms=None):
    p.text = ''
    p.style = style_name
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.first_line_indent = indent
    
    if italic_terms is None:
        italic_terms = []
        
    # Sort italic terms by length descending to match longest phrases first
    italic_terms = sorted(italic_terms, key=len, reverse=True)
    pattern = '|'.join([re.escape(term) for term in italic_terms]) if italic_terms else None
    
    if pattern:
        tokens = re.split(f'({pattern})', text)
        for token in tokens:
            if not token:
                continue
            r = p.add_run(token)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.bold = bold
            if token in italic_terms:
                r.italic = True
    else:
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = bold

def set_heading(p, text, style_name='Heading 2', space_before=12, space_after=6, bold=True):
    p.text = ''
    p.style = style_name
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.bold = bold

def run_revision():
    print("Opening master docx...")
    doc = docx.Document(MASTER_LOCAL)
    
    # Common technical terms to italicize across academic paragraphs
    COMMON_ITALICS = [
        "boundary halo", "halo padding", "halo stripping", "edge replication", "mode='edge'",
        "speedup", "overhead", "worker", "Performance-Core", "Performance-Cores", "P-Core", "P-Cores",
        "Efficient-Core", "Efficient-Cores", "E-Core", "E-Cores", "Intel Smart Cache",
        "Golden Cove", "Gracemont", "Intel Thread Director", "Intel Core i5-13420H",
        "Hyper-Threading", "capacity misses", "cache misses", "working set", "working set analysis",
        "memory-bound", "compute-bound", "embarrassingly parallel", "strong scaling",
        "diminishing returns", "load imbalance", "synchronous barrier", "idle waiting",
        "inter-process communication", "pipe latency", "pickle", "numpy.vstack()", "numpy.array_equal()",
        "psutil", "psutil.cpu_percent()", "psutil.Process().cpu_affinity()", "time.perf_counter()",
        "pool.map()", "multiprocessing.Pool", "multiprocessing.Pool.map()", "multiprocessing.shared_memory",
        "multiprocessing", "multithreading", "shared memory", "memory-mapped files", "mmap",
        "static row partitioning", "uniform static slicing", "center-crop", "cool-down buffer",
        "repeatability drift", "randomized block design", "hardware performance counters",
        "Intel VTune Profiler", "Linux perf", "CuPy", "PyTorch CUDA", "OpenCV-GPU", "OpenMP",
        "warp-level primitives", "parallel for", "thread hopping", "zero-copy data sharing",
        "work-stealing pool", "dynamic chunk scheduling", "heterogeneity-aware dynamic scheduling"
    ]
    
    # -------------------------------------------------------------
    # SUBBAB 5.5
    # -------------------------------------------------------------
    # P318: Heading 2
    set_heading(doc.paragraphs[318], "Pembahasan Temuan dan Keterbatasan Penelitian", style_name='Heading 2')
    
    # P319: Opening
    set_para(doc.paragraphs[319],
        "Subbab ini membahas temuan empiris dari Skenario A, B, dan C berdasarkan prinsip arsitektur komputasi, karakteristik perangkat keras, serta perbandingannya terhadap literatur terdahulu.",
        italic_terms=COMMON_ITALICS
    )
    
    # P320: Heading 3
    set_heading(doc.paragraphs[320], "Dinamika Resolusi Citra dan Hipotesis Pengaruh Hierarki Cache L2 dan L3", style_name='Heading 3', space_before=9, space_after=4)
    
    # P321: Sobel 512
    set_para(doc.paragraphs[321],
        "Pada pengujian Skenario A, filter Sobel pada resolusi 512 × 512 piksel dengan alokasi empat proses pekerja (P = 4) mencatatkan rasio percepatan yang mendekati batas linier ideal (S ≈ P), dengan median speedup sebesar 4,04× dan rerata 3,89× (deviasi standar 0,84; interval kepercayaan 95% [3,58; 4,20]). Efisiensi komputasi median tercatat sebesar 101,02% (rerata 97,26%). Sebanyak 16 dari 30 repetisi pengujian menghasilkan nilai overhead negatif tipis dengan median −0,0002 detik (mendekati nol). Pada resolusi yang sama, Gaussian Blur memperoleh median speedup 2,50× (rerata 2,52×), sedangkan Grayscale memperoleh median speedup 1,52× (rerata 1,68×).",
        italic_terms=COMMON_ITALICS
    )
    
    # P322: Cache hypothesis framing
    set_para(doc.paragraphs[322],
        "Tingginya rasio percepatan filter Sobel pada dimensi 512 × 512 piksel konsisten dengan hipotesis interaksi ukuran data terhadap hierarki memori cache prosesor Intel Core i5-13420H. Prosesor ini dilengkapi 12 MB L3 Intel Smart Cache yang digunakan bersama dan 1,25 MB L2 cache privat pada setiap Performance-Core (P-Core).",
        italic_terms=COMMON_ITALICS
    )
    
    # P323: L3 shared vs L2 private
    set_para(doc.paragraphs[323],
        "Citra RGB 512 × 512 piksel berukuran total sekitar 768 KB (atau 262 KB dalam format monokrom satu kanal). Ukuran data tersebut beserta lapisan batas halo padding (k = 1) termuat utuh ke dalam 12 MB L3 cache bersama, baik pada eksekusi serial maupun paralel. Pembeda kinerja antara eksekusi serial dan paralel pada konfigurasi ini didorong oleh distribusi beban ke dalam hierarki L2 cache privat masing-masing inti.",
        italic_terms=COMMON_ITALICS
    )
    
    # P324: Working set L2
    set_para(doc.paragraphs[324],
        "Ketika citra dipartisi ke empat pekerja, setiap pekerja memproses irisan submatriks berukuran 130 × 512 piksel (termasuk boundary halo) dengan ukuran data masukan sekitar 195 KB. Partisi data masukan yang ringkas ini beserta larik perantara gradien konvolusi berpeluang besar tertampung pada 1,25 MB L2 cache privat masing-masing P-Core, sehingga mengurangi frekuensi akses ke memori utama DRAM.",
        italic_terms=COMMON_ITALICS
    )
    
    # P325: Parallel bandwidth & capacity misses
    set_para(doc.paragraphs[325],
        "Selain itu, eksekusi paralel empat pekerja mendistribusikan lalu lintas data ke empat jalur L2 cache privat. Pembagian ini mengurangi terjadinya kegagalan kapasitas (capacity misses) dan kontensi antrean bus memori yang dihadapi eksekusi serial satu inti saat mengolah keseluruhan larik citra secara berulang.",
        italic_terms=COMMON_ITALICS
    )
    
    # P326: Output payload Sobel vs Gaussian Blur
    set_para(doc.paragraphs[326],
        "Karakteristik luaran filter Sobel juga berperan penting. Filter Sobel menghasilkan luaran monokromatik satu kanal berukuran ringkas (sekitar 262 KB pada 512 × 512 piksel), berbeda dari Gaussian Blur yang harus mengembalikan luaran tiga kanal warna penuh (sekitar 786 KB). Muatan transmisi IPC yang lebih kecil pada filter Sobel membuat biaya komunikasi antar-proses tetap rendah pada resolusi kecil, sehingga akselerasi komputasi dapat tercapai optimal.",
        italic_terms=COMMON_ITALICS
    )
    
    # P327: Comparison with Grayscale and Gaussian Blur
    set_para(doc.paragraphs[327],
        "Pola percepatan mendekati linier pada resolusi 512 × 512 piksel tidak teramati pada operasi Grayscale maupun Gaussian Blur. Pada Grayscale, intensitas aritmatika berada pada tingkat 1,25 FLOP/bita dan durasi pemrosesan serial berlangsung singkat (median 0,0203 detik). Pada durasi tersebut, latensi tetap pipa komunikasi antar-proses (pembuatan pipa IPC, serialisasi, dan deserialisasi pickle) yang berkisar 0,008 detik mendominasi perbandingan, sehingga speedup tertahan pada angka 1,52× (rerata 1,68×). Pada Gaussian Blur, intensitas komputasi yang mencapai 8,50 FLOP/bita terhambat oleh volume data luaran tiga kanal RGB yang harus dialirkan kembali melalui pipa IPC — tiga kali lipat lebih besar dibandingkan Sobel (satu kanal). Beban transmisi IPC yang besar ini menekan efisiensi paralel Gaussian Blur pada angka 2,50× (rerata 2,52×).",
        italic_terms=COMMON_ITALICS
    )
    
    # P328: Drop to 1024, stabilization at 2048-4096
    set_para(doc.paragraphs[328],
        "Seiring peningkatan dimensi citra masukan, rasio percepatan filter Sobel memperlihatkan penurunan dari resolusi 512 × 512 piksel ke 1024 × 1024 piksel (median speedup turun dari 4,04× ke 2,26×; rerata 2,30×). Pada dimensi 1024 × 1024 piksel, ukuran partisi data per pekerja melampaui kapasitas L2 cache privat 1,25 MB sehingga memicu capacity misses, disertai pembengkakan volume transmisi data IPC. Pada resolusi yang lebih tinggi (2048 × 2048 hingga 4096 × 4096 piksel), percepatan filter Sobel terdistribusi pada kisaran 2,08× hingga 2,87×.",
        italic_terms=COMMON_ITALICS
    )
    
    # P329: Multi-block 2048 variation and 4096 absolute reduction
    set_para(doc.paragraphs[329],
        "Evaluasi lintas skenario menunjukkan bahwa nilai percepatan pada sel 2048 × 2048 piksel (P = 4) bervariasi antar-blok pengujian: median speedup bernilai 2,08× (rerata 2,21×) pada Skenario A, 2,87× (rerata 2,74×) pada Skenario B, dan 2,68× (rerata 2,59×) pada Skenario C. Variasi ini mencerminkan pengaruh pergeseran keterulangan (repeatability drift) akibat perbedaan suhu awal prosesor antar-skenario. Sementara itu, pada resolusi 4096 × 4096 piksel (Skenario A), percepatan tercatat sebesar 2,82× (rerata 2,85×) dengan efisiensi 70,59%. Keuntungan utama pemrosesan paralel pada resolusi 4096 × 4096 piksel terletak pada penghematan waktu absolut, yaitu mereduksi durasi eksekusi dari 2,62 detik (serial) menjadi 0,94 detik (paralel), dengan proporsi overhead terhadap waktu serial menurun dari sekitar 21% pada resolusi 2048 piksel menjadi 10,6% pada resolusi 4096 piksel.",
        italic_terms=COMMON_ITALICS
    )
    
    # P330: Cache caveat
    set_para(doc.paragraphs[330],
        "Penjelasan mengenai pengaruh hierarki memori cache terhadap rasio percepatan ini berstatus sebagai hipotesis ilmiah yang konsisten dengan data empiris, bukan bukti pengukuran instrumentasi langsung. Pengujian ini tidak mengukur tingkat kegagalan cache (cache miss rate) secara langsung melalui hardware performance counters (seperti Intel VTune atau Linux perf) dan tidak menerapkan penguncian afinitas inti (core affinity pinning) guna mengontrol penempatan proses pekerja. Keterbatasan metodologis ini dicatat pada Subbab 5.5.5.",
        italic_terms=COMMON_ITALICS
    )
    
    # P331: Heading 3
    set_heading(doc.paragraphs[331], "Karakteristik Skalabilitas Worker, Arsitektur Hibrida, dan Diminishing Returns", style_name='Heading 3', space_before=9, space_after=4)
    
    # P332: Skenario B intro
    set_para(doc.paragraphs[332],
        "Pengujian Skenario B mengevaluasi perilaku penskalaan kuat (strong scaling) sistem ketika alokasi proses pekerja ditingkatkan secara bertahap (P ∈ {1, 2, 4, 8}) pada dimensi citra konstan 2048 × 2048 piksel. Data empiris memperlihatkan penurunan efisiensi marjinal (diminishing returns) pada seluruh algoritma filter, dengan titik saturasi teramati pada filter Sobel ketika alokasi ditingkatkan dari empat ke delapan proses pekerja.",
        italic_terms=COMMON_ITALICS
    )
    
    # P333: Minor subhead 1
    set_para(doc.paragraphs[333], "1. Titik Plato pada Filter Sobel di P = 8", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P334: Sobel P=2 to P=4
    set_para(doc.paragraphs[334],
        "Pada filter Sobel, penambahan pekerja dari P = 2 ke P = 4 menghasilkan peningkatan percepatan: median waktu eksekusi berkurang dari 0,3477 detik menjadi 0,2087 detik, meningkatkan median speedup dari 1,76× ke 2,87× (rerata 2,74×) dengan efisiensi 71,84%.",
        italic_terms=COMMON_ITALICS
    )
    
    # P335: Sobel P=4 to P=8 plato
    set_para(doc.paragraphs[335],
        "Ketika alokasi pekerja ditingkatkan dari P = 4 ke P = 8, peningkatan percepatan terhenti. Median waktu eksekusi paralel hanya bergeser sebesar 0,0026 detik (dari 0,2087 detik menjadi 0,2061 detik), dan median speedup hanya berubah dari 2,8738× ke 2,8783× (perbedaan marjinal +0,0045× yang tidak signifikan secara statistik, p = 0,15 pada uji Mann–Whitney). Di sisi lain, efisiensi komputasi menurun dari 71,84% menjadi 35,98%, sementara median durasi overhead sistem meningkat dari 0,0596 detik menjadi 0,1320 detik (kenaikan bersih +0,0724 detik). Persentase utilisasi CPU global sistem meningkat dari 39,94% ke 70,49%, mencerminkan peningkatan aktivitas komputasi latar belakang tanpa memberikan reduksi waktu pemrosesan yang sebanding.",
        italic_terms=COMMON_ITALICS
    )
    
    # P336: Amdahl deficit
    set_para(doc.paragraphs[336],
        "Perilaku ini menunjukkan deviasi terhadap model teoretis Hukum Amdahl. Menggunakan estimasi fraksi paralel f = 0,79 pada filter Sobel, model Hukum Amdahl memproyeksikan rasio percepatan teoretis sebesar 3,24× pada P = 8. Capaian empiris rata-rata berada pada angka 2,88× (defisit 0,36× terhadap batas teoretis), mengindikasikan adanya faktor penghambat koordinasi pada alokasi pekerja tinggi.",
        italic_terms=COMMON_ITALICS
    )
    
    # P337: Minor subhead 2
    set_para(doc.paragraphs[337], "2. Hipotesis Pengaruh Arsitektur Prosesor Hibrida (P-Core dan E-Core)", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P338: Raptor Lake architecture
    set_para(doc.paragraphs[338],
        "Salah satu penjelasan potensial mengenai munculnya titik plato pada P = 8 berkaitan dengan karakteristik mikroarsitektur prosesor Intel Core i5-13420H. Prosesor ini memiliki delapan inti fisik heterogen yang terbagi menjadi dua kluster: empat Performance-Cores (P-Cores, arsitektur Golden Cove) dengan frekuensi turbo hingga 4,6 GHz dan L2 cache privat 1,25 MB per inti, serta empat Efficient-Cores (E-Cores, arsitektur Gracemont) dengan frekuensi turbo maksimum 3,4 GHz, kapasitas instruksi per siklus (IPC) lebih rendah, dan berbagi pakai 2 MB L2 cache per kluster.",
        italic_terms=COMMON_ITALICS
    )
    
    # P339: P=2 & P=4 scheduling
    set_para(doc.paragraphs[339],
        "Pada alokasi P = 2 dan P = 4, beban kerja proses pekerja kemungkinan besar diprioritaskan oleh penjadwal sistem operasi dan Intel Thread Director pada kluster P-Core yang berkinerja lebih tinggi, sehingga proses pekerja mengeksekusi komputasi dengan laju yang relatif seimbang.",
        italic_terms=COMMON_ITALICS
    )
    
    # P340: P=8 activation
    set_para(doc.paragraphs[340],
        "Pada alokasi P = 8, sistem melibatkan seluruh delapan inti fisik yang tersedia, memadukan 4 P-Core dan 4 E-Core secara bersamaan. Skema partisi pada sistem ini menerapkan dekomposisi spasial statis (static row partitioning), membagi matriks citra 2048 baris secara seragam menjadi delapan blok yang masing-masing memuat 256 baris piksel (ditambah baris batas halo).",
        italic_terms=COMMON_ITALICS
    )
    
    # P341: Load imbalance
    set_para(doc.paragraphs[341],
        "Pembagian beban kerja statis seragam pada prosesor heterogen berpotensi memicu ketimpangan waktu penyelesaian (load imbalance). Pekerja yang dialokasikan pada P-Core (frekuensi hingga 4,6 GHz) menyelesaikan pemrosesan blok lebih cepat dibandingkan pekerja yang berjalan pada E-Core (frekuensi 3,4 GHz). Karena pemanggilan multiprocessing.Pool.map() menerapkan pembatas sinkronisasi (synchronous barrier), proses utama harus menunggu hingga pekerja pada E-Core menyelesaikan tugasnya sebelum dapat menjalankan rekonstruksi numpy.vstack(). Waktu tunggu ini berpotensi membatasi penambahan percepatan pada P = 8.",
        italic_terms=COMMON_ITALICS
    )
    
    # P342: Minor subhead 3
    set_para(doc.paragraphs[342], "3. Karakteristik Efisiensi dan Evaluasi Metrik Karp–Flatt", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P343: Efficiency degradation across filters
    set_para(doc.paragraphs[343],
        "Penurunan efisiensi paralel seiring bertambahnya alokasi pekerja teramati pada ketiga jenis filter. Pada Grayscale, efisiensi menurun dari 69,33% (P = 2) menjadi 49,38% (P = 4) dan 31,88% (P = 8). Pada Gaussian Blur, efisiensi menurun dari 80,27% (P = 2) menjadi 57,73% (P = 4) dan 36,20% (P = 8). Pada Sobel, efisiensi menurun dari 87,88% (P = 2) menjadi 71,84% (P = 4) dan 35,98% (P = 8). Pada P = 8, efisiensi ketiga filter berada pada rentang 32% hingga 36%.",
        italic_terms=COMMON_ITALICS
    )
    
    # P344: Karp-Flatt values
    set_para(doc.paragraphs[344],
        "Evaluasi menggunakan metrik fraksi serial eksperimental Karp–Flatt (e) memperlihatkan perbedaan perilaku antar-filter. Pada filter Sobel, nilai e berbasis rerata bernilai 0,1292 (P = 2), 0,1535 (P = 4), dan meningkat menjadi 0,2272 pada P = 8 (berbasis median: 0,1379 pada P = 2, 0,1306 pada P = 4, dan 0,2542 pada P = 8). Sebaliknya, pada Gaussian Blur, nilai e relatif stabil pada kisaran 0,2474 (P = 2), 0,2499 (P = 4), dan 0,2520 (P = 8). Pada Grayscale, nilai e justru mengalami penurunan dari 0,4376 (P = 2) menjadi 0,3662 (P = 4) dan 0,3168 (P = 8).",
        italic_terms=COMMON_ITALICS
    )
    
    # P345: Karp-Flatt interpretation
    set_para(doc.paragraphs[345],
        "Karakteristik metrik Karp–Flatt tersebut menunjukkan bahwa peningkatan fraksi serial efektif pada P = 8 hanya teramati secara nyata pada filter Sobel. Perbedaan respons antar-filter ini mengindikasikan bahwa hambatan pada P = 8 tidak semata disebabkan oleh heterogenitas inti fisik, melainkan merupakan interaksi antara waktu komputasi lokal, alokasi larik perantara, dan biaya transmisi data antar-proses.",
        italic_terms=COMMON_ITALICS
    )
    
    # P346: Empty spacing paragraph (keep empty)
    doc.paragraphs[346].text = ""
    
    # P347: Heading 3
    set_heading(doc.paragraphs[347], "Karakteristik Beban Tambahan (Overhead) Serialisasi IPC dan Utilisasi CPU", style_name='Heading 3', space_before=9, space_after=4)
    
    # P348: Skenario C intro
    set_para(doc.paragraphs[348],
        "Pengujian Skenario C dirancang untuk menganalisis beban koordinasi internal sistem pada kondisi resolusi 2048 × 2048 piksel dan alokasi pekerja tetap (P = 4) dengan memvariasikan karakteristik algoritma: konversi Grayscale (operasi titik), penghalusan Gaussian Blur 3 × 3 (konvolusi spasial tiga kanal), dan deteksi tepi Sobel 3 × 3 (konvolusi gradien ganda). Evaluasi berfokus pada dua parameter: durasi beban tambahan paralel (T_overhead) dan persentase utilisasi prosesor.",
        italic_terms=COMMON_ITALICS
    )
    
    # P349: Minor subhead 1
    set_para(doc.paragraphs[349], "1. Karakteristik Beban Tambahan Komunikasi IPC dan Alokasi Memori", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P350: Skenario C overhead numbers
    set_para(doc.paragraphs[350],
        "Berdasarkan data empiris Skenario C sebagaimana disajikan pada Gambar 5.3(a), durasi beban tambahan paralel (T_overhead) menunjukkan perbedaan antar-filter. Grayscale mencatatkan median overhead terendah sebesar 0,0294 detik (rerata 0,0337 ± 0,0138 detik, interval kepercayaan 95% [0,0286; 0,0389] detik). Gaussian Blur mencatatkan median overhead tertinggi sebesar 0,0924 detik (rerata 0,1129 ± 0,0563 detik, interval kepercayaan 95% [0,0919; 0,1339] detik). Sobel menghasilkan median overhead moderat sebesar 0,0695 detik (rerata 0,0849 ± 0,0445 detik, interval kepercayaan 95% [0,0683; 0,1015] detik).",
        italic_terms=COMMON_ITALICS
    )
    
    # P351: Overhead component deconstruction
    set_para(doc.paragraphs[351],
        "Durasi overhead Gaussian Blur lebih tinggi dibandingkan Sobel meskipun Sobel memiliki tahapan kalkulasi gradien horizontal dan vertikal. Pada modul multiprocessing, parameter T_overhead mencakup latensi pengaliran pipa antar-proses (IPC pipe latency), serialisasi dan deserialisasi objek larik NumPy (pickle), alokasi memori larik lokal pada pekerja, serta rekonsiliasi akhir melalui numpy.vstack().",
        italic_terms=COMMON_ITALICS
    )
    
    # P352: Payload analysis
    set_para(doc.paragraphs[352],
        "Perbedaan durasi overhead tersebut sejalan dengan volume muatan data (payload size) yang ditransmisikan. Pada filter Gaussian Blur, setiap pekerja menerima irisan masukan berukuran (512 + 2) × 2048 × 3 bita (sekitar 3,16 MB) dan mengembalikan matriks luaran tiga kanal berukuran 512 × 2048 × 3 bita (sekitar 3,15 MB), sehingga total volume luaran yang diserialisasi oleh keempat pekerja via pickle dan digabungkan kembali oleh proses utama mencapai 12,58 MB. Pada filter Sobel, konversi ke derajat keabuan dilakukan di dalam memori pekerja sebelum perhitungan gradien, sehingga luaran akhir berupa matriks monokromatik satu kanal berukuran 512 × 2048 × 1 bita (sekitar 1,05 MB) dengan total volume luaran kembalian sebesar 4,19 MB — sepertiga dari volume keluaran Gaussian Blur. Pada filter Grayscale, ketiadaan penambahan lapisan batas (k = 0) dan ringkasnya matriks kembalian (total 4,19 MB) menghasilkan nilai overhead terendah pada angka 0,0294 detik.",
        italic_terms=COMMON_ITALICS
    )
    
    # P353: Nuanced conclusion on overhead causality
    set_para(doc.paragraphs[353],
        "Meskipun demikian, perbedaan durasi overhead antara Sobel (0,0695 detik) dan Grayscale (0,0294 detik) pada volume luaran kembalian yang sama (4,19 MB) menunjukkan bahwa T_overhead tidak semata merefleksikan transmisi IPC murni, melainkan juga memuat alokasi memori larik perantara float64 dan waktu komputasi tambahan di tingkat pekerja.",
        italic_terms=COMMON_ITALICS
    )
    
    # P354: Minor subhead 2
    set_para(doc.paragraphs[354], "2. Karakteristik dan Batasan Interpretasi Utilisasi CPU", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P355: CPU utilisation numbers
    set_para(doc.paragraphs[355],
        "Pengukuran beban prosesor melalui modul psutil pada Gambar 5.3(b) memperlihatkan perbedaan pola utilisasi. Grayscale menghasilkan rerata utilisasi CPU sistem sebesar 30,57% (median 28,18%, rentang interkuartil [23,15% – 35,72%]). Gaussian Blur menghasilkan rerata 44,17% (median 44,17%, rentang interkuartil [38,41% – 48,68%]). Sobel menghasilkan rerata 43,34% (median 40,11%, rentang interkuartil [37,03% – 48,16%]).",
        italic_terms=COMMON_ITALICS
    )
    
    # P356: Status as coarse global trend
    set_para(doc.paragraphs[356],
        "Angka utilisasi CPU yang dilaporkan oleh pustaka psutil berstatus sebagai tren indikatif kasar agregat sistem, bukan pengukuran deterministik per proses pekerja. Hal ini disebabkan oleh mekanisme pemantauan psutil yang mengambil percontohan berkala beban CPU global sistem pada interval waktu diskret 20 milidetik, tanpa memisahkan kontribusi spesifik masing-masing sub-proses pekerja multiprocessing.",
        italic_terms=COMMON_ITALICS
    )
    
    # P357: Grayscale vs convolution sampling count
    set_para(doc.paragraphs[357],
        "Pada Grayscale, durasi eksekusi paralel murni (T_paralel) hanya berlangsung selama 0,0620 detik (62 milidetik). Dengan interval percontohan kelas CPUMonitor sebesar 20 milidetik, pemantau hanya sempat mengambil sekitar 3 titik sampel. Akibatnya, estimasi utilisasi lebih rentan terhadap fluktuasi transien sistem. Sebaliknya, durasi komputasi paralel Gaussian Blur (0,2532 detik) dan Sobel (0,2110 detik) berlangsung lebih panjang sehingga tertangkap oleh sekitar 10 hingga 13 siklus percontohan psutil, menghasilkan nilai utilisasi sistem yang stabil di kisaran 40% hingga 44%.",
        italic_terms=COMMON_ITALICS
    )
    
    # P358: Thread capacity baseline
    set_para(doc.paragraphs[358],
        "Nilai utilisasi sistem 40% hingga 44% diinterpretasikan dalam konteks kapasitas total prosesor Intel Core i5-13420H yang mengekspos 12 utas logis ke sistem operasi Windows 11 (4 P-Cores dengan Hyper-Threading = 8 utas logis, ditambah 4 E-Cores tanpa Hyper-Threading = 4 utas logis). Beban empat proses pekerja secara teoretis menyumbang setidaknya 4/12 × 100% = 33,33% dari kapasitas total utas logis sistem.",
        italic_terms=COMMON_ITALICS
    )
    
    # P359: Multicore engagement
    set_para(doc.paragraphs[359],
        "Capaian utilisasi aktual sebesar 40% hingga 44% mengindikasikan adanya pemanfaatan komputasi multi-inti yang aktif selama fase paralel berlangsung, dengan sisa persentase utilisasi di atas 33,33% merepresentasikan aktivitas proses sistem operasi dan thread pemantau latar belakang.",
        italic_terms=COMMON_ITALICS
    )
    
    # P360: Heading 3
    set_heading(doc.paragraphs[360], "Komparasi Temuan terhadap Penelitian Terdahulu", style_name='Heading 3', space_before=9, space_after=4)
    
    # P361: Section intro
    set_para(doc.paragraphs[361],
        "Hasil pengujian dikomparasikan terhadap literatur rujukan utama yang telah dipetakan pada Bab 2, mencakup kajian komputasi paralel berbasis memori bersama OpenMP, akselerasi GPU, serta model konkurensi CPython.",
        italic_terms=COMMON_ITALICS
    )
    
    # P362: Minor subhead 1
    set_para(doc.paragraphs[362], "1. Komparasi terhadap Model Konkurensi Python (Gultom dan Sarumaha, 2025)", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P363: Gultom & Sarumaha
    set_para(doc.paragraphs[363],
        "Gultom dan Sarumaha (2025) menguji efektivitas modul multithreading dan multiprocessing CPython pada beban komputasi numerik berulang hingga 120 juta iterasi. Penelitian tersebut menunjukkan bahwa batasan Global Interpreter Lock (GIL) menyebabkan multithreading hanya menghasilkan percepatan marjinal sekitar 1,05×, sedangkan multiprocessing menghasilkan speedup 3,16× hingga 3,55× pada alokasi empat proses pekerja.",
        italic_terms=COMMON_ITALICS
    )
    
    # P364: Contrast with Gultom
    set_para(doc.paragraphs[364],
        "Rasio percepatan pada penelitian ini pada empat pekerja (resolusi 2048 × 2048 piksel) berada pada kisaran 1,90× hingga 2,74×, lebih rendah dibandingkan capaian Gultom dan Sarumaha. Perbedaan ini kemungkinan besar bersumber dari perbedaan karakteristik beban kerja dan platform pengujian. Beban kerja Gultom dan Sarumaha berupa kalkulasi skalar numerik dengan volume data komunikasi yang sangat kecil. Sebaliknya, penelitian ini memproses matriks citra berukuran jutaan piksel, saat setiap pekerja harus menerima dan mengembalikan larik data berukuran megabita melalui saluran pipa IPC. Serialisasi objek NumPy via pickle dan penggabungan akhir via numpy.vstack() menyita waktu terukur yang membatasi percepatan pada ranah pengolahan citra digital.",
        italic_terms=COMMON_ITALICS
    )
    
    # P365: Minor subhead 2
    set_para(doc.paragraphs[365], "2. Komparasi terhadap Model Memori Bersama OpenMP (Cremel dan Arruda, 2026)", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P366: Cremel & Arruda
    set_para(doc.paragraphs[366],
        "Cremel dan Arruda (2026) mengevaluasi akselerasi filter spasial citra termasuk deteksi tepi menggunakan pustaka OpenMP berbasis bahasa C/C++ pada CPU multi-core. Model berbasis utas OpenMP beroperasi pada satu ruang alamat memori bersama sehingga tidak memerlukan serialisasi objek. Meskipun demikian, Cremel dan Arruda melaporkan bahwa efisiensi paralel OpenMP pada deteksi tepi mengalami penurunan pada alokasi delapan utas (efisiensi sekitar 24%) akibat keterbatasan lebar pita memori (memory bandwidth bottleneck).",
        italic_terms=COMMON_ITALICS
    )
    
    # P367: Efficiency decline confirmation
    set_para(doc.paragraphs[367],
        "Hasil pengujian Skenario B pada penelitian ini memperlihatkan kecenderungan penurunan efisiensi yang sejalan pada alokasi delapan pekerja (P = 8), dengan efisiensi Sobel turun menjadi 35,98% dan Gaussian Blur menjadi 36,20%. Penurunan efisiensi pada sistem ini dipengaruhi oleh kombinasi faktor heterogenitas frekuensi clock P-Core dan E-Core, transmisi pipa IPC, serta perebutan lebar pita bus memori utama.",
        italic_terms=COMMON_ITALICS
    )
    
    # P368: Resolution scaling contrast with Cremel
    set_para(doc.paragraphs[368],
        "Terdapat perbedaan pola skalabilitas resolusi antara penelitian ini dan temuan Cremel dan Arruda. Cremel dan Arruda melaporkan bahwa rasio percepatan meningkat seiring kenaikan resolusi citra secara monoton. Sebaliknya, pada penelitian ini, rasio percepatan tertinggi filter Sobel tercapai pada resolusi kecil (512 × 512 piksel) akibat partisi kerja tertampung pada memori cache L2 privat, sebelum kemudian menurun dan mendatar pada resolusi 1024 hingga 4096 piksel.",
        italic_terms=COMMON_ITALICS
    )
    
    # P369: Minor subhead 3
    set_para(doc.paragraphs[369], "3. Komparasi terhadap Akselerasi GPU (Chang et al., 2023)", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P370: Chang et al.
    set_para(doc.paragraphs[370],
        "Chang et al. (2023) melaporkan penerapan operator Sobel pada GPU NVIDIA berbasis CUDA dengan capaian percepatan 6,7× hingga 13,0× terhadap pustaka OpenCV-GPU standar. Di sisi lain, literatur komputasi paralel GPU (Ibrahim et al., 2021; Vasile et al., 2024) mencatat bahwa akselerasi GPU memiliki beban tambahan transfer data antara memori host (RAM) dan memori perangkat grafis (VRAM) melalui bus PCIe.",
        italic_terms=COMMON_ITALICS
    )
    
    # P371: Analogous transfer overhead
    set_para(doc.paragraphs[371],
        "Perilaku transfer data tersebut memperlihatkan kesamaan konseptual dengan beban transmisi pipa IPC pada CPU multiprocessing dalam penelitian ini. Pada citra berdimensi kecil, durasi overhead transmisi menyita proporsi yang cukup terasa terhadap total waktu eksekusi. Keuntungan praktis pemrosesan paralel CPU terlihat pada citra beresolusi tinggi (4096 × 4096 piksel), dengan reduksi waktu eksekusi Sobel dari 2,62 detik (serial) menjadi 0,94 detik (paralel).",
        italic_terms=COMMON_ITALICS
    )
    
    # P372: Baseline caveat
    set_para(doc.paragraphs[372],
        "Perlu dicatat bahwa perbandingan nilai percepatan antara penelitian ini (2,85× pada 4096 piksel dan 4,04× pada 512 piksel) dan hasil Chang et al. (6,7× hingga 13,0×) tidak berada pada dasar pembanding yang setara, karena penelitian ini menggunakan baseline serial CPU NumPy sedangkan Chang et al. menggunakan baseline pustaka OpenCV-GPU. Pendekatan multiprocessing CPU Python murni menawarkan keunggulan berupa ketiadaan ketergantungan pada perangkat keras GPU diskret dan driver berpemilik (proprietary), sehingga lebih mudah diimplementasikan pada lingkungan komputasi berdaya rendah.",
        italic_terms=COMMON_ITALICS
    )
    
    # P373: Table intro
    set_para(doc.paragraphs[373],
        "Sintesis perbandingan posisi temuan penelitian ini terhadap penelitian terdahulu dirangkum pada Tabel 5.8.",
        italic_terms=COMMON_ITALICS
    )
    
    # P374: Table caption
    p374 = doc.paragraphs[374]
    p374.text = "Tabel 5.8 Komparasi Temuan Penelitian terhadap Literatur Terdahulu"
    p374.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in p374.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.bold = True
        
    # Table 22 in docx: clean headers ("&" -> "dan")
    t22 = doc.tables[22]
    t22.cell(0, 1).text = "Chang et al. (2023)"
    t22.cell(0, 2).text = "Cremel dan Arruda (2026)"
    t22.cell(0, 3).text = "Gultom dan Sarumaha (2025)"
    t22.cell(0, 4).text = "Penelitian Ini"
    
    t22.cell(3, 4).text = "Speedup 2,21×–2,85× (4096 px) hingga 4,04× (512 px) pada 4 worker"
    t22.cell(4, 4).text = "Efisiensi Sobel turun ke 35,98% pada 8 worker (efek E-Core dan IPC)"
    t22.cell(6, 4).text = "Uji biner bit-identik 100% deterministik (Δ_max = 0)"
    
    for row in t22.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(10)
    for cell in t22.rows[0].cells:
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
                
    # P375: Empty
    doc.paragraphs[375].text = ""
    
    # P376: Heading 3
    set_heading(doc.paragraphs[376], "Sintesis Jawaban Rumusan Masalah dan Keterbatasan Penelitian", style_name='Heading 3', space_before=9, space_after=4)
    
    # P377: Synthesis intro
    set_para(doc.paragraphs[377],
        "Subbab ini menyajikan sintesis jawaban atas rumusan masalah penelitian, diikuti oleh identifikasi keterbatasan metodologis dan eksperimental.",
        italic_terms=COMMON_ITALICS
    )
    
    # P378: Minor subhead 1
    set_para(doc.paragraphs[378], "1. Sintesis Jawaban Rumusan Masalah", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P379: RM 1 title
    set_para(doc.paragraphs[379], "Jawaban Rumusan Masalah 1: Pengaruh Resolusi Citra terhadap Speedup dan Efisiensi", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P380: RM 1 answer (merged and corrected)
    set_para(doc.paragraphs[380],
        "Peningkatan resolusi citra masukan menghasilkan respons skalabilitas yang dipengaruhi oleh ukuran partisi kerja dan volume transmisi data IPC. Pada filter Sobel (P = 4), percepatan mendekati batas linier ideal pada dimensi 512 × 512 piksel (median 4,04×, rerata 3,89×, efisiensi median 101,02%) sejalan dengan hipotesis partisi data tertampung di dalam L2 cache privat P-Core (1,25 MB). Percepatan menurun pada resolusi 1024 × 1024 piksel (median 2,26×) seiring terjadinya capacity misses pada L2 cache dan peningkatan volume IPC, kemudian berada pada rentang 2,08× hingga 2,87× pada resolusi 2048 dan 4096 piksel dengan reduksi waktu absolut terbesar terjadi pada resolusi 4096 piksel (dari 2,62 detik menjadi 0,94 detik). Pada konversi Grayscale, percepatan terdistribusi datar pada rentang 1,52× hingga 2,12× di seluruh resolusi karena karakteristik operasi terikat memori (memory-bound) dengan batasan transfer memori DRAM DDR5.",
        italic_terms=COMMON_ITALICS
    )
    
    # P381: (Was duplicate Grayscale paragraph) - repurpose as smooth connector
    set_para(doc.paragraphs[381],
        "Pada filter Gaussian Blur, intensitas komputasi yang lebih tinggi (8,50 FLOP/bita) menghasilkan speedup yang moderat (median 2,50× pada 512 piksel hingga 2,31× pada 2048 piksel) karena beban pengaliran matriks luaran tiga kanal RGB (12,58 MB pada citra 2048 piksel) menyita porsi waktu transmisi IPC yang signifikan.",
        italic_terms=COMMON_ITALICS
    )
    
    # P382: RM 2 title
    set_para(doc.paragraphs[382], "Jawaban Rumusan Masalah 2: Pola Skalabilitas Alokasi Worker terhadap Batas Teoretis Hukum Amdahl", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P383: RM 2 answer part 1
    set_para(doc.paragraphs[383],
        "Peningkatan alokasi proses pekerja (P ∈ {1, 2, 4, 8}) pada resolusi 2048 × 2048 piksel memperlihatkan pola penurunan efisiensi marjinal. Alokasi pekerja hingga P = 4 menghasilkan peningkatan speedup yang stabil (Sobel meningkat dari 1,00× pada P = 1 menjadi 1,76× pada P = 2, dan 2,87× pada P = 4 dengan efisiensi 71,84%). Namun, penambahan alokasi ke P = 8 menghasilkan titik plato pada filter Sobel (speedup median 2,88×, perbedaan marjinal +0,0045× yang tidak signifikan secara statistik, p = 0,15), dengan efisiensi turun menjadi 35,98% dan berada di bawah proyeksi Hukum Amdahl teoretis (3,24× pada f = 0,79).",
        italic_terms=COMMON_ITALICS
    )
    
    # P384: RM 2 answer part 2 (Karp-Flatt nuanced)
    set_para(doc.paragraphs[384],
        "Kenaikan metrik fraksi serial Karp–Flatt (e) dari 0,1306 (P = 4) ke 0,2542 (P = 8) teramati secara spesifik pada filter Sobel, mengindikasikan adanya beban koordinasi tambahan pada P = 8 yang konsisten dengan hipotesis ketimpangan waktu eksekusi antara P-Core dan E-Core serta pembengkakan waktu transmisi pipa IPC.",
        italic_terms=COMMON_ITALICS
    )
    
    # P385: RM 3 title
    set_para(doc.paragraphs[385], "Jawaban Rumusan Masalah 3: Pengaruh Kompleksitas Filter terhadap Overhead IPC dan Utilisasi CPU", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P386: RM 3 answer part 1 (Overhead payload)
    set_para(doc.paragraphs[386],
        "Pengujian Skenario C menunjukkan bahwa durasi beban tambahan (T_overhead) sejalan dengan volume muatan data keluaran yang diserialisasi melalui pipa IPC. Gaussian Blur mencatatkan overhead tertinggi (median 0,0924 detik) karena mentransmisikan luaran tiga kanal RGB (12,58 MB). Sobel menghasilkan overhead moderat (median 0,0695 detik) karena luaran tereduksi menjadi satu kanal monokrom (4,19 MB), dan Grayscale menghasilkan overhead terendah (0,0294 detik) karena ketiadaan operasi boundary halo (k = 0). Perbedaan overhead antara Sobel dan Grayscale pada volume luaran yang sama mengindikasikan bahwa T_overhead juga memuat alokasi memori larik perantara lokal pada pekerja.",
        italic_terms=COMMON_ITALICS
    )
    
    # P387: RM 3 answer part 2 (CPU Utilisation)
    set_para(doc.paragraphs[387],
        "Pengukuran beban prosesor menggunakan psutil pada P = 4 berada pada kisaran 40%–44% dari total 12 utas logis sistem, mengindikasikan aktivitas multi-inti yang aktif selama fase eksekusi paralel. Pada Grayscale, utilisasi terukur lebih rendah (median 28,18%) akibat durasi komputasi yang sangat singkat (62 milidetik) dibandingkan interval percontohan psutil 20 milidetik.",
        italic_terms=COMMON_ITALICS
    )
    
    # P388: RM 4 title
    set_para(doc.paragraphs[388], "Jawaban Rumusan Masalah 4: Integritas Luaran Citra Bit-Identik", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P389: RM 4 mechanism
    set_para(doc.paragraphs[389],
        "Integritas luaran citra paralel terjaga secara deterministik melalui penerapan mekanisme boundary halo selebar k = 1 piksel dengan metode replikasi batas (edge replication padding, mode='edge') pada setiap submatriks partisi, diikuti oleh pemangkasan baris batas (halo stripping) sebelum rekonstruksi utuh via numpy.vstack().",
        italic_terms=COMMON_ITALICS
    )
    
    # P390: RM 4 verification results
    set_para(doc.paragraphs[390],
        "Validasi biner terhadap 720 pasangan komparasi non-trivial (serial-paralel) dan 90 pasangan kontrol trivial A/A (total 810 iterasi) menunjukkan status kesetaraan elemen matriks numpy.array_equal() = True sebesar 100% dengan nilai disparitas absolut maksimum piksel bernilai nol (Δ_max = 0) pada seluruh citra uji, mengonfirmasi bahwa pembagian baris horizontal dan pertukaran batas spasial tidak menimbulkan distorsi sambungan atau pergeseran indeks.",
        italic_terms=COMMON_ITALICS
    )
    
    # P391: Minor subhead 2
    set_para(doc.paragraphs[391], "2. Keterbatasan Penelitian", indent=Cm(0), bold=True, space_before=6, space_after=2)
    
    # P392: Limitations intro
    set_para(doc.paragraphs[392],
        "Penelitian ini memiliki beberapa keterbatasan metodologis dan eksperimental yang perlu dicatat:",
        italic_terms=COMMON_ITALICS
    )
    
    # P393: Limitation 1
    set_para(doc.paragraphs[393],
        "Pertama, pengujian dieksekusi secara sekuensial antar-skenario (diawali Skenario A, dilanjutkan B, dan diakhiri C) tanpa pengacakan blok global (no global randomized block design). Ketiadaan pengacakan urutan ini memicu fenomena pergeseran keterulangan (repeatability drift) yang terlihat dari perbedaan baseline waktu serial Skenario A terhadap B dan C pada konfigurasi identik (citra 2048 × 2048 piksel, P = 4). Selain itu, urutan eksekusi selalu mendahulukan serial sebelum paralel pada setiap repetisi.",
        italic_terms=COMMON_ITALICS
    )
    
    # P394: Limitation 2
    set_para(doc.paragraphs[394],
        "Kedua, eksperimen menggunakan satu citra acuan master tunggal yang dipotong secara pemotongan tengah murni (center-crop) ke berbagai dimensi (512 × 512 hingga 4096 × 4096 piksel) tanpa proses resampling atau interpolasi. Pendekatan ini menjaga konsistensi visual antarsampel, namun belum mengevaluasi konten citra dengan karakteristik frekuensi spasial dan entropi yang bervariasi.",
        italic_terms=COMMON_ITALICS
    )
    
    # P395: Limitation 3
    set_para(doc.paragraphs[395],
        "Ketiga, evaluasi kinerja dijalankan pada satu unit perangkat keras laptop dengan prosesor Intel Core i5-13420H (arsitektur hibrida 4 P-Core + 4 E-Core, 12 utas logis, RAM 16 GB DDR5). Karakteristik skalabilitas yang teramati sangat dipengaruhi oleh konfigurasi perangkat keras ini dan belum divalidasi silang pada arsitektur prosesor homogen (seperti AMD Ryzen) maupun prosesor tingkat peladen.",
        italic_terms=COMMON_ITALICS
    )
    
    # P396: Limitation 4
    set_para(doc.paragraphs[396],
        "Keempat, sistem telemetri pengujian tidak merekam sensor suhu silikon (°C) dan frekuensi clock aktual prosesor (GHz) secara kontinu ke dalam berkas data log. Mitigasi termal bertumpu pada suhu ruangan (~24 °C) dan jeda pendinginan selama 0,5 detik (cool-down buffer), sehingga fluktuasi termal mikro tidak tercatat secara numerik per iterasi.",
        italic_terms=COMMON_ITALICS
    )
    
    # P397: Limitation 5
    set_para(doc.paragraphs[397],
        "Kelima, sistem tidak menerapkan penguncian afinitas proses pekerja ke inti fisik tertentu (psutil.Process().cpu_affinity()). Penempatan proses dikelola oleh penjadwal Windows 11 dan Intel Thread Director, sehingga migrasi proses antar-inti dapat memengaruhi variansi latensi.",
        italic_terms=COMMON_ITALICS
    )
    
    # P398: Limitation 6
    set_para(doc.paragraphs[398],
        "Keenam, analisis mengenai kontribusi memori cache L2 dan L3 terhadap percepatan pada resolusi 512 × 512 piksel berstatus sebagai hipotesis ilmiah berbasis analisis ukuran partisi kerja (working set analysis), bukan hasil pencatatan langsung dari unit pencacah kinerja perangkat keras (hardware performance counters).",
        italic_terms=COMMON_ITALICS
    )
    
    # P399: Limitation 7
    set_para(doc.paragraphs[399],
        "Ketujuh, pengujian difokuskan pada filter spasial independen (embarrassingly parallel) dengan kernel lokal 3 × 3. Karakteristik ini tidak dapat digeneralisasi langsung pada operasi citra non-lokal atau konvolusi kernel berukuran besar (7 × 7 ke atas).",
        italic_terms=COMMON_ITALICS
    )
    
    # P400 & P401: Spacing paragraphs
    doc.paragraphs[400].text = ""
    doc.paragraphs[401].text = ""
    
    # -------------------------------------------------------------
    # BAB 6 (Draf Kerja yang Diselaraskan dengan Subbab 5.5)
    # -------------------------------------------------------------
    # P402: Heading 1
    doc.paragraphs[402].text = "PENUTUP"
    doc.paragraphs[402].style = 'Heading 1'
    doc.paragraphs[402].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in doc.paragraphs[402].runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True
        
    # P403: Intro
    set_para(doc.paragraphs[403],
        "Bab ini menyajikan kesimpulan yang ditarik dari hasil pengujian empiris dan analisis kinerja komparasi filter spasial menggunakan Python multiprocessing, diikuti oleh saran untuk pengembangan penelitian selanjutnya.",
        italic_terms=COMMON_ITALICS
    )
    
    # P404: Heading 2
    set_heading(doc.paragraphs[404], "Kesimpulan", style_name='Heading 2')
    
    # P405: Kesimpulan intro
    set_para(doc.paragraphs[405],
        "Berdasarkan serangkaian pengujian sebanyak 810 iterasi (mencakup 720 pasangan komparasi non-trivial serial-paralel dan 90 pasangan kontrol A/A) pada prosesor Intel Core i5-13420H, diperoleh empat kesimpulan pokok:",
        italic_terms=COMMON_ITALICS
    )
    
    # P406: Kesimpulan 1
    set_para(doc.paragraphs[406],
        "1. Pada filter Sobel (P = 4), percepatan mendekati batas linier pada resolusi 512 × 512 piksel (median 4,04×, rerata 3,89× [CI 95%: 3,58; 4,20]) dan terdistribusi pada kisaran 2,2× hingga 2,9× pada resolusi 1024 hingga 4096 piksel. Perbedaan hasil antar-blok pengujian pada resolusi 2048 piksel (2,21× pada Blok A, 2,74× pada Blok B, dan 2,59× pada Blok C) menunjukkan bahwa variasi keterulangan termal memengaruhi capaian percepatan. Percepatan pada 512 piksel konsisten dengan hipotesis bahwa partisi per pekerja tertampung di dalam cache L2 privat, meskipun tidak diukur melalui instrumentasi langsung. Pada konversi Grayscale, median percepatan berada pada rentang 1,52× hingga 2,12× di seluruh resolusi.",
        italic_terms=COMMON_ITALICS
    )
    
    # P407: Kesimpulan 2
    set_para(doc.paragraphs[407],
        "2. Pada dimensi citra konstan 2048 × 2048 piksel, percepatan filter Sobel meningkat dari 1,76× (P = 2) ke 2,87× (P = 4), dan tidak berbeda secara signifikan antara P = 4 dan P = 8 (p = 0,15 pada uji Mann–Whitney), sementara efisiensi menurun dari 71,84% ke 35,98%. Pola data konsisten dengan estimasi model Hukum Amdahl pada fraksi paralel efektif f = 0,69 hingga 0,79 sesuai jenis filter. Kenaikan metrik fraksi serial Karp–Flatt teramati secara nyata pada filter Sobel (dari 0,1306 ke 0,2542), saat heterogenitas inti P-Core dan E-Core serta pembengkakan koordinasi IPC menjadi penjelasan yang konsisten dengan data.",
        italic_terms=COMMON_ITALICS
    )
    
    # P408: Kesimpulan 3
    set_para(doc.paragraphs[408],
        "3. Durasi beban tambahan (overhead) pada P = 4 dan resolusi 2048 × 2048 piksel berurutan: Gaussian Blur (median 0,0924 detik) > Sobel (0,0695 detik) > Grayscale (0,0294 detik). Urutan ini sejalan dengan volume muatan luaran kembalian (12,58 MB pada Gaussian Blur vs 4,19 MB pada Sobel dan Grayscale) serta alokasi memori larik perantara lokal pada pekerja. Sementara itu, persentase utilisasi CPU global psutil berada pada kisaran 40%–44% yang merefleksikan aktivitas komputasi multi-inti pada prosesor.",
        italic_terms=COMMON_ITALICS
    )
    
    # P409: Kesimpulan 4
    set_para(doc.paragraphs[409],
        "4. Penerapan dekomposisi domain spasial horizontal dengan mekanisme boundary halo padding selebar k = 1 piksel bermetode replikasi tepi (edge replication, mode='edge') dan pemangkasan batas (halo stripping) menjaga integritas rekonstruksi citra secara konsisten. Seluruh 720 pasangan pengujian serial-paralel dan 90 pasangan kontrol A/A menghasilkan kesetaraan matriks biner deterministik numpy.array_equal() = True sebesar 100% dengan disparitas absolut maksimum nol (Δ_max = 0) pada seluruh citra uji.",
        italic_terms=COMMON_ITALICS
    )
    
    # P410: Heading 2
    set_heading(doc.paragraphs[410], "Saran", style_name='Heading 2')
    
    # P411: Saran intro
    set_para(doc.paragraphs[411],
        "Berdasarkan temuan empiris dan analisis keterbatasan yang diperoleh, diajukan beberapa saran untuk penelitian lanjutan:",
        italic_terms=COMMON_ITALICS
    )
    
    # P412: Saran 1
    set_para(doc.paragraphs[412],
        "1. Mengevaluasi skema pembagian beban dinamis (dynamic chunk scheduling atau work-stealing pool) dengan mengalokasikan porsi baris lebih banyak dibandingkan jumlah pekerja guna mengurangi potensi waktu tunggu sinkronisasi pada prosesor berarsitektur heterogen (P-Core dan E-Core).",
        italic_terms=COMMON_ITALICS
    )
    
    # P413: Saran 2
    set_para(doc.paragraphs[413],
        "2. Mengurangi beban tambahan serialisasi data antar-proses dengan memanfaatkan arsitektur memori bersama (shared memory via multiprocessing.shared_memory) atau pemetaan berkas ke memori (memory-mapped files, mmap) agar proses utama dan pekerja dapat berbagi akses larik citra tanpa penalti waktu serialisasi pickle.",
        italic_terms=COMMON_ITALICS
    )
    
    # P414: Saran 3
    set_para(doc.paragraphs[414],
        "3. Menerapkan mekanisme penguncian afinitas proses pekerja ke inti fisik prosesor (core affinity pinning via psutil.Process().cpu_affinity()) dengan memilih satu utas per P-Core setelah memeriksa topologi prosesor guna meminimalkan migrasi proses antar-inti (thread hopping).",
        italic_terms=COMMON_ITALICS
    )
    
    # P415: Saran 4
    set_para(doc.paragraphs[415],
        "4. Menyempurnakan protokol eksperimen dengan mengintegrasikan pencatatan telemetri suhu silikon (°C) dan frekuensi aktual prosesor (GHz) secara kontinu, menerapkan pengacakan urutan blok pengujian (randomized block design) guna mengurangi bias termal awal, serta memanfaatkan hardware performance counters untuk mengukur laju cache misses secara empiris.",
        italic_terms=COMMON_ITALICS
    )
    
    # P416: Saran 5
    set_para(doc.paragraphs[416],
        "5. Memperluas evaluasi komparatif ke akselerasi komputasi berbasis unit pengolah grafis (GPU) menggunakan pustaka seperti CuPy atau PyTorch CUDA, serta vektorisasi instruksi SIMD (AVX2) pada CPU untuk memetakan titik impas performa pada citra beresolusi sangat tinggi.",
        italic_terms=COMMON_ITALICS
    )
    
    # Save local master
    doc.save(MASTER_LOCAL)
    print("Master local successfully updated!")
    
    # Sync to OneDrive
    shutil.copy2(MASTER_LOCAL, MASTER_ONEDRIVE)
    print("Master OneDrive successfully synchronized!")

if __name__ == '__main__':
    run_revision()
