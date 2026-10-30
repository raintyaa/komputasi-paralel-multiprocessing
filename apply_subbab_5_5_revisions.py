# -*- coding: utf-8 -*-
"""
Script to apply comprehensive revisions to Subbab 5.5 and Bab 6 in master docx.
Revisions:
1. Eliminate all 11 instances of 'di mana' in 5.5 and Bab 6 with proper Indonesian connectors.
2. Replace 'sepenuhnya' with 'mandiri terisolasi' / 'diserahkan langsung' / 'dibatasi secara dominan'.
3. Replace 'mutlak' ('nol mutlak' -> 'nol').
4. Replace 'Jaminan' in P388 with 'Integritas' and 'menjamin' in P409 with 'terbukti menjaga'.
5. Correct 'resample' in P394 to 'center-crop murni tanpa proses resampling atau interpolasi piksel'.
6. Correct 'jeda pendinginan 2 detik' in P396 to '0,5 detik (cool-down buffer)'.
7. Correct 'deviasi standar 0,31' in P321 to '0,84' (Speedup_Std = 0.8381 for Sobel 512).
8. Renumber Table 5.2 in Subbab 5.5 to Table 5.8 (both text reference P373 and caption P374).
"""

import sys
import os
import shutil
import docx
import re
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.stdout.reconfigure(encoding='utf-8')

MASTER_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
TEMP_DOCX = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\temp_onedrive_check.docx"
MASTER_ONEDRIVE = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"

def set_para_text(p, text, style=None, space_before=None, space_after=None, line_spacing=None, first_line_indent=None):
    if style is None:
        style = p.style.name
    p.text = text
    p.style = style
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if space_before is not None:
        p.paragraph_format.space_before = Pt(space_before)
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if line_spacing is not None:
        p.paragraph_format.line_spacing = line_spacing
    if first_line_indent is not None:
        p.paragraph_format.first_line_indent = first_line_indent
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

def run_update():
    print("=== Opening Document from Temp Copy ===")
    doc = docx.Document(TEMP_DOCX)
    
    # 1. P321 (Sobel 512 std dev 0.84, remove 'di mana')
    p321 = doc.paragraphs[321]
    set_para_text(p321,
        "Temuan paling mencolok dari Skenario A adalah anomali percepatan superlinear filter Sobel pada resolusi 512 × 512 piksel, dengan rerata percepatan mencapai S ≈ 3,89× (median speedup 4,04×, deviasi standar 0,84) serta tingkat efisiensi komputasi mencapai 101,02% pada alokasi empat proses pekerja (P = 4). Dari 30 iterasi pengujian, 16 iterasi menghasilkan nilai overhead negatif (median −0,0002 detik), yang bermakna bahwa eksekusi paralel empat pekerja secara konsisten menyelesaikan komputasi lebih cepat daripada prediksi pembagian linier waktu serial (T_serial / P). Sementara itu, pada resolusi yang sama, Gaussian Blur memperoleh speedup median 2,50× (rerata 2,52×) dan Grayscale hanya 1,52× (rerata 1,68×)."
    )
    
    # 2. P328 (Sobel 1024-2048, replace 'di mana')
    p328 = doc.paragraphs[328]
    set_para_text(p328,
        "Seiring peningkatan dimensi citra masukan, rasio percepatan filter Sobel memperlihatkan dinamika penurunan sebelum akhirnya mengalami pemulihan. Ketika resolusi ditingkatkan ke 1024 × 1024 piksel, speedup Sobel anjlok dari 4,04× ke 2,26× (rerata 2,30×). Pada dimensi ini, ukuran partisi data per pekerja melampaui batas kapasitas L2 cache privat 1,25 MB (L2 cache capacity misses), dan biaya transmisi data melalui pipa IPC mulai membengkak. Titik terendah percepatan tercapai pada resolusi 2048 × 2048 piksel (speedup median 2,08×, rerata 2,21×), saat ukuran partisi data memaksa terjadinya akses berulang ke DRAM utama."
    )
    
    # 3. P329 (Sobel 4096, replace 'di mana')
    p329 = doc.paragraphs[329]
    set_para_text(p329,
        "Namun, pada resolusi ultra-tinggi 4096 × 4096 piksel, terjadi fenomena pemulihan percepatan (amortization rebound), saat median speedup Sobel melonjak kembali ke 2,82× (rerata 2,85×). Pemulihan ini terjadi bukan karena faktor cache, melainkan karena prinsip amortisasi komputasi: pertumbuhan waktu komputasi kuadratik (O(N^2)) pada resolusi 4K membuat durasi eksekusi serial membengkak hingga 2,62 detik, sehingga beban tetap koordinasi IPC teramortisasi dan keuntungan pemrosesan paralel multi-inti kembali mendominasi."
    )
    
    # 4. P340 (P = 8 static partitioning, replace 'di mana')
    p340 = doc.paragraphs[340]
    set_para_text(p340,
        "Sebaliknya, pada alokasi P = 8, sistem dipaksa mengaktifkan seluruh delapan inti fisik yang tersedia, yaitu memadukan 4 P-Core dan 4 E-Core secara bersamaan. Desain sistem paralel pada penelitian ini menerapkan dekomposisi spasial statis (static row partitioning), dengan membagi matriks citra 2048 baris secara merata menjadi delapan blok identik yang masing-masing memuat 256 baris piksel (ditambah baris batas halo)."
    )
    
    # 5. P356 (psutil CPU limitation, replace 'di mana')
    p356 = doc.paragraphs[356]
    set_para_text(p356,
        "Perlu ditegaskan bahwa angka utilisasi CPU yang dilaporkan oleh pustaka psutil merupakan tren indikatif kasar, bukan pengukuran deterministik per-proses. Hal ini disebabkan oleh mekanisme pemantauan karena proses-proses pekerja multiprocessing tidak teragregasi pada level sub-proses individu secara waktu nyata, melainkan diambil melalui percontohan berkala (periodic sampling) beban CPU global sistem pada interval waktu diskret 20 milidetik. Perbedaan persentase utilisasi ini terutama mencerminkan dinamika jendela eksekusi komputasi aktif terhadap interval percontohan tersebut."
    )
    
    # 6. P364 (Comparison Gultom, replace 'di mana')
    p364 = doc.paragraphs[364]
    set_para_text(p364,
        "Komparasi hasil eksperimen memunculkan pertanyaan penting: mengapa penelitian ini mencapai rasio percepatan rerata 1,90× hingga 2,74× pada 4 worker (pada citra 2048 × 2048), sedangkan Gultom dan Sarumaha mencapai 3,16× hingga 3,55×? Perbedaan tersebut terletak pada karakteristik beban kerja yang secara fundamental berbeda. Pada pengujian sintetis Gultom dan Sarumaha, beban kerja berupa kalkulasi aritmetika skalar dengan data masukan dan luaran hanya berupa variabel integer tunggal, sehingga biaya komunikasi antar-proses bernilai mendekati nol (near-zero IPC cost). Sebaliknya, pada penelitian ini, sistem memproses matriks citra riil berdimensi jutaan piksel, dengan setiap pekerja harus menerima irisan submatriks masukan dan mengembalikan matriks luaran berukuran megabita melalui saluran pipa IPC sistem operasi. Penalti waktu untuk serialisasi objek larik NumPy (pickle), pengaliran melalui pipa IPC Windows, dan rekonstruksi kembali via numpy.vstack() menyita fraksi waktu yang terukur — mencapai 0,0924 detik pada Gaussian Blur dan 0,0695 detik pada Sobel. Hal ini menunjukkan bahwa pada ranah pengolahan citra digital riil, skalabilitas multiprocessing Python dibatasi oleh laju transmisi I/O memori dan serialisasi IPC, bukan semata efisiensi eksekusi kernel pada inti prosesor."
    )
    
    # 7. P368 (Comparison Cremel, replace 'sepenuhnya')
    p368 = doc.paragraphs[368]
    set_para_text(p368,
        "Menariknya, efisiensi Sobel multiprocessing Python pada penelitian ini pada P = 8 (35,98%) tetap lebih tinggi dibandingkan capaian OpenMP pada studi Cremel dan Arruda (sekitar 24%). Hal ini disebabkan oleh strategi dekomposisi domain spasial: partisi baris horizontal mandiri dengan boundary halo k = 1 membuat setiap proses pekerja Python mengeksekusi komputasi secara mandiri terisolasi tanpa memerlukan operasi sinkronisasi antar-utas (inter-thread locks) selama fase konvolusi berlangsung. Degradasi efisiensi pada sistem ini terutama dipicu oleh ketimpangan arsitektur inti fisik P-Core dan E-Core serta penalti transmisi pipa IPC pada fase rekonsiliasi akhir."
    )
    
    # 8. P371 (Comparison Chang GPU, replace 'di mana')
    p371 = doc.paragraphs[371]
    set_para_text(p371,
        "Pola perilaku transfer memori tersebut menunjukkan analogi yang serupa dengan temuan pada arsitektur multiprocessing CPU dalam penelitian ini. Pada citra berdimensi kecil (512 × 512 dan 1024 × 1024 piksel), durasi overhead komunikasi (pada GPU berupa transfer PCIe, pada CPU berupa transfer pipa IPC) menyita fraksi signifikan dari total waktu eksekusi. Akselerasi paralel baru bernilai ekonomis optimal ketika dimensi citra dinaikkan ke tingkat 4096 × 4096 piksel (Skenario A), saat rasio percepatan Sobel pulih ke angka 2,82× (median) dan 2,85× (rerata) dengan efisiensi 70,59%, mereduksi latensi pemrosesan dari 2,62 detik (serial) menjadi 0,94 detik (paralel)."
    )
    
    # 9. P373 & P374 (Table renumbering: Tabel 5.2 -> Tabel 5.8)
    p373 = doc.paragraphs[373]
    set_para_text(p373,
        "Sintesis komparasi posisi temuan penelitian ini terhadap penelitian-penelitian terdahulu dirangkum secara sistematis pada Tabel 5.8."
    )
    p374 = doc.paragraphs[374]
    p374.text = "Tabel 5.8 Komparasi Temuan Penelitian terhadap Literatur Terdahulu"
    p374.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in p374.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.bold = True
        
    # 10. P380 (Rumusan Masalah 1, replace 'di mana' and 'sepenuhnya')
    p380 = doc.paragraphs[380]
    set_para_text(p380,
        "Peningkatan resolusi matriks citra masukan menghasilkan respons skalabilitas yang tidak linier dan sangat ditentukan oleh rasio intensitas aritmatika algoritma (FLOP/bita), bukan percepatan yang meningkat secara monoton. Pada filter konvolusi intensif (Sobel 3×3, P = 4), percepatan membentuk kurva bathtub saat anomali superlinear terjadi pada 512 × 512 piksel (median 4,04×, efisiensi 101,02%) akibat pemanfaatan penuh 12 MB L3 Intel Smart Cache dan 1,25 MB L2 cache privat P-Core. Percepatan mengalami kontraksi pada resolusi 1024 dan 2048 piksel akibat terjadinya L2 cache capacity misses dan penalti serialisasi IPC, sebelum akhirnya pulih kembali (amortization rebound) pada 4096 × 4096 piksel (median 2,82×, efisiensi 70,59%) saat waktu komputasi kuadratik mengamortisasi biaya tetap IPC secara efektif. Sebaliknya, operasi Grayscale dibatasi secara langsung oleh lebar pita memori DRAM (memory-bound) dengan speedup datar pada rentang 1,52× hingga 2,12×."
    )
    
    # 11. P381 (Grayscale memory-bound, replace 'sepenuhnya')
    p381 = doc.paragraphs[381]
    set_para_text(p381,
        "Sebaliknya, konversi Grayscale yang bersifat terikat memori (memory-bound) memperlihatkan kurva percepatan yang datar (1,52× hingga 2,12×) di seluruh rentang resolusi karena performa sistem dibatasi secara dominan oleh laju transfer bus memori DRAM DDR5 dan penalti serialisasi data."
    )
    
    # 12. P384 (Rumusan Masalah 2, replace 'di mana')
    p384 = doc.paragraphs[384]
    set_para_text(p384,
        "Namun, penggandaan pekerja ke P = 8 memicu stagnasi percepatan pada filter Sobel (hanya bergeser dari 2,8738× ke 2,8783×, efisiensi turun ke 35,98%), dengan penambahan alokasi yang tidak menghasilkan percepatan marjinal signifikan (p = 0,15 pada uji Mann–Whitney). Hambatan ini terkonfirmasi dari lonjakan metrik fraksi serial Karp–Flatt (e) dari 0,1306 ke 0,2542, yang mengindikasikan bahwa hambatan pada P = 8 bersumber dari pembengkakan overhead sinkronisasi dan ketimpangan arsitektur inti prosesor hibrida (P-Core versus E-Core)."
    )
    
    # 13. P388 (Title Rumusan Masalah 4, replace 'Jaminan')
    p388 = doc.paragraphs[388]
    p388.text = "Jawaban Rumusan Masalah 4: Integritas Luaran Citra Bit-Identik 100%"
    for r in p388.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True
        
    # 14. P390 (Bit-identical validation, replace 'mutlak')
    p390 = doc.paragraphs[390]
    set_para_text(p390,
        "Validasi biner deterministik terhadap seluruh 720 pasangan komparasi serial-paralel dan 90 pasangan kontrol A/A (total 810 iterasi) menunjukkan status kesetaraan elemen matriks numpy.array_equal() = True sebesar 100% dengan nilai disparitas absolut maksimum piksel bernilai nol (Δ_{max} = 0). Hal ini mengonfirmasi bahwa pembagian baris horizontal dan pertukaran data batas tidak menimbulkan pergeseran spasial, distorsi sambungan baris, maupun artefak penggelapan nol (zero-padding)."
    )
    
    # 15. P393 (Limitation 1, replace 'di mana')
    p393 = doc.paragraphs[393]
    set_para_text(p393,
        "Pertama, ketiga skenario pengujian dieksekusi secara sekuensial tanpa pengacakan blok global (no global randomized block design), diawali blok Skenario A, dilanjutkan Skenario B, dan diakhiri Skenario C. Ketiadaan pengacakan blok urutan ini memicu fenomena pergeseran keterulangan (repeatability drift), yang ditandai oleh durasi baseline serial pada Skenario A sekitar 20%–28% lebih lambat dibandingkan Skenario B dan C pada konfigurasi perlakuan yang sama persis (citra 2048 × 2048, P = 4) akibat perbedaan suhu awal dan status power governor prosesor. Selain itu, urutan pasangan komparasi selalu mendahulukan eksekusi serial sebelum paralel pada setiap repetisi, yang berpotensi menimbulkan asimetri termal mikro."
    )
    
    # 16. P394 (Limitation 2, replace 'resample' with 'center-crop murni')
    p394 = doc.paragraphs[394]
    set_para_text(p394,
        "Kedua, seluruh 810 iterasi eksperimen dijalankan menggunakan satu citra acuan master tunggal yang dipotong secara pemotongan tengah murni (center-crop) ke berbagai tingkat resolusi (512 × 512 hingga 4096 × 4096 piksel) tanpa proses resampling atau interpolasi piksel. Meskipun pendekatan ini memberikan konsistensi deterministik yang tinggi dan mengeliminasi variasi visual antarsampel, pengujian belum mengevaluasi spektrum ragam konten citra dengan karakteristik frekuensi spasial, kontras, dan entropi yang heterogen (misalnya citra medis bergradien halus versus citra lanskap bertekstur rapat)."
    )
    
    # 17. P396 (Limitation 4, replace '2 detik' with '0,5 detik')
    p396 = doc.paragraphs[396]
    set_para_text(p396,
        "Keempat, sistem telemetri pengujian tidak dilengkapi instrumentasi pencatatan sensor suhu silikon (°C) dan frekuensi clock aktual prosesor (GHz) secara kontinu dan terintegrasi ke dalam berkas CSV pada setiap iterasi. Mitigasi fluktuasi termal hanya bertumpu pada pengondisian temperatur ruang (~24 °C) dan jeda pendinginan selama 0,5 detik (cool-down buffer). Akibatnya, keberadaan thermal throttling mikro tidak dapat dideteksi secara numerik per iterasi."
    )
    
    # 18. P397 (Limitation 5, replace 'sepenuhnya')
    p397 = doc.paragraphs[397]
    set_para_text(p397,
        "Kelima, sistem tidak menerapkan pengikatan afinitas proses pekerja ke inti tertentu (psutil.Process().cpu_affinity()). Pemetaan proses diserahkan langsung kepada penjadwal Windows 11 dan Intel Thread Director, sehingga peralihan tugas antar-inti (thread hopping) secara probabilistik dapat memengaruhi variansi latensi mikroarsitektur."
    )
    
    # 19. P406 (Bab 6 Kesimpulan 1, replace 'di mana' and 'sepenuhnya')
    p406 = doc.paragraphs[406]
    set_para_text(p406,
        "1. Efektivitas peningkatan resolusi citra masukan terhadap rasio percepatan (speedup) dan efisiensi sangat dikendalikan oleh intensitas aritmatika algoritma (rasio FLOP/bita), bukan menghasilkan akselerasi linier seragam. Pada algoritma konvolusi intensif (compute-bound) seperti filter Sobel dengan alokasi empat pekerja (P = 4), skalabilitas membentuk kurva berbentuk U. Pada resolusi 512 × 512 piksel, terjadi anomali percepatan superlinear dengan rerata speedup 3,89× (median 4,04×) dan efisiensi 101,02% akibat seluruh data citra beserta halo termuat utuh ke dalam 12 MB L3 Intel Smart Cache bersama serta partisi kerja per pekerja (195 KB) tertampung di dalam 1,25 MB L2 cache privat P-Core, sehingga meniadakan latensi bus DRAM utama. Kinerja terkoreksi pada resolusi menengah (1024 × 1024 dan 2048 × 2048 piksel) ke kisaran speedup 2,08×–2,26× (efisiensi 52,00%–56,51%) akibat terjadinya L2 cache capacity misses dan penalti transmisi pipa IPC. Pada resolusi ultra-tinggi 4096 × 4096 piksel, terjadi pemulihan kinerja (amortization rebound) saat median speedup melonjak kembali ke 2,82× (rerata 2,85×) dengan efisiensi 70,59% karena pertumbuhan waktu komputasi kuadratik mengamortisasi biaya tetap koordinasi paralel. Sebaliknya, pada konversi Grayscale yang bersifat terikat memori (memory-bound, 1,25 FLOP/bita), percepatan terdistribusi datar pada rentang 1,52× hingga 2,12× (efisiensi 38,00%–53,00%) di seluruh resolusi karena performa sistem dibatasi secara dominan oleh laju transfer bus memori DRAM DDR5 dan penalti serialisasi data."
    )
    
    # 20. P407 (Bab 6 Kesimpulan 2, replace 'di mana')
    p407 = doc.paragraphs[407]
    set_para_text(p407,
        "2. Skalabilitas penambahan proses pekerja (P ∈ {1, 2, 4, 8}) pada dimensi citra konstan 2048 × 2048 piksel memperlihatkan pola diminishing returns tajam saat alokasi melampaui kapasitas inti performa fisik (P-Core). Peningkatan kinerja efektif hanya berlangsung pada rentang P = 1 hingga P = 4 saat seluruh proses dialokasikan pada kluster P-Core homogen (median speedup Sobel meningkat dari 1,00× ke 2,87× dengan efisiensi 71,84%). Ketika alokasi dinaikkan ke P = 8, terjadi saturasi dan titik plato dengan kenaikan speedup marjinal Sobel hanya mencapai +0,0045× (dari 2,8738× ke 2,8783×) dan efisiensi turun menjadi 35,98% — tertinggal jauh di bawah batas teoretis Hukum Amdahl sebesar 3,24× (f = 0,79). Hambatan ini bersumber dari arsitektur hibrida Raptor Lake: pelibatan empat Efficient-Cores (E-Cores, 3,4 GHz, IPC lebih rendah) pada partisi beban statis 256 baris seragam memicu ketimpangan beban kerja (load imbalance), sehingga unit P-Core terpaksa menganggur menunggu penyelesaian pekerja E-Core pada pembatas sinkronisasi (synchronous barrier pool.map()). Kondisi ini terkonfirmasi dari lonjakan metrik fraksi serial Karp–Flatt (e) yang meningkat drastis dari 0,1306 (P = 4) menjadi 0,2542 (P = 8)."
    )
    
    # 21. P409 (Bab 6 Kesimpulan 4, replace 'menjamin' and 'mutlak')
    p409 = doc.paragraphs[409]
    set_para_text(p409,
        "4. Penerapan dekomposisi domain spasial horizontal 1D yang dipadukan dengan mekanisme boundary halo padding selebar k = 1 piksel bermetode replikasi tepi (edge replication, mode='edge') dan pemangkasan batas (halo stripping) terbukti menjaga keabsahan rekonstruksi citra secara konsisten. Seluruh 810 pasangan evaluasi (720 pengujian serial-paralel dan 90 kontrol A/A) menghasilkan status kesetaraan matriks deterministik numpy.array_equal() = True sebesar 100% dengan disparitas nilai piksel absolut maksimum nol (Δ_{max} = 0), mengonfirmasi bahwa peningkatan kecepatan komputasi paralel tidak menimbulkan artefak batas, distorsi sambungan baris, maupun pergeseran indeks spasial."
    )
    
    print("Saving updated document to local master:", MASTER_LOCAL)
    doc.save(MASTER_LOCAL)
    print("Local master save successful!")

if __name__ == '__main__':
    run_update()
