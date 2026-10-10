# -*- coding: utf-8 -*-
"""
Script to apply comprehensive revisions to BAB 4 PERANCANGAN SISTEM
in Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx and standalone files.

Revisions Applied:
1. Subbab 4.1:
   - Polished phrasing, removed hyperbole ('dibatasi secara ketat' -> 'dibatasi', 'menjamin' -> 'memastikan', 'murni' removed).
   - Fixed 'di mana' to 'dengan'.
   - Clarified memory locality.
2. Subbab 4.2:
   - 4.2.1: Clarified ITU-R BT.601-7 luma Y', R', G', B' gamma-corrected components. Explained dtype lifecycle (uint8 -> float64 arithmetic -> clip -> uint8).
   - 4.2.2: Clarified Gaussian Blur 3x3 as discrete binomial approximation (sigma approx 0.85) normalized by 1/16. Clarified mathematically separable but implemented as direct 2D 9-tap convolution.
   - 4.2.3: Reaffirmed Euclidean L2 norm magnitude sqrt(Gx^2 + Gy^2). Stated explicitly that RGB chunks are transmitted to workers via IPC, grayscale conversion is executed locally inside workers, and 2D edge chunks are returned.
   - 4.2.4: Removed cv2.BORDER_REPLICATE, explicitly defined numpy.pad(..., mode='edge') with pad_width ((1,1),(1,1)) or ((1,1),(1,1),(0,0)) avoiding padding on color channels.
3. Subbab 4.3:
   - Kept Gambar 4.1 drawing intact and untouched!
   - Corrected 'kelipatan kuadrat' to 'bilangan pangkat dua (2^k: 512, 1024, 2048, 4096 piksel)'.
   - Softened 'seimbang sempurna' to explain equal base rows with minor variations from interior halo and P/E core heterogeneity.
   - Added explicit IPC volume transmission formulas (V_in and V_out) with 4096 px P=8 numerical examples.
   - Softened 'terbebas seutuhnya dari GIL' to 'tidak berbagi GIL antar-proses'.
4. Subbab 4.4:
   - Added reference to Subbab 3.5.1 for pre-warming and worker pool initialization outside measurement window.
   - Symmetrically defined T_serial timing window.
   - Harmonized CPUMonitor description (20 ms interval daemon thread, psutil.cpu_percent, non-blocking).
   - Table 4.1: Added explanatory note regarding P=1 mathematical values recorded in raw CSV vs excluded in Chapter 5.
5. Subbab 4.5:
   - Softened overclaims ('membuktikan' -> 'memastikan bahwa luaran paralel setara secara deterministik...').
   - Described the exact two-stage check: shape verification -> deterministic numpy.array_equal -> float64 difference calculation for max_diff.
   - Clarified that 90 P=1 pairs are serial-to-serial control baseline.
6. Cleaned Banned Words:
   - Zero occurrences of 'di mana', 'menjamin', 'tangguh', 'kokoh', 'mutlak', 'secara presisi', 'sepenuhnya', 'akan', 'diharapkan'.
"""

import sys
import os
import shutil
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.stdout.reconfigure(encoding='utf-8')

MASTER_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
MASTER_ONEDRIVE = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"

def set_para_text(p, text, style='Normal', space_before=0, space_after=6, line_spacing=1.5, first_line_indent=Cm(1.0)):
    p.text = text
    p.style = style
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.first_line_indent = first_line_indent
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

def italicize_technical_terms(p):
    """Italicize technical and foreign words in paragraph runs."""
    terms = [
        "data parallelism", "multiprocessing", "file I/O", "row-major order", "C-contiguous",
        "spatial locality", "cache misses", "point-wise", "data-independent execution",
        "luma", "luminansi", "image smoothing", "separable", "9-tap", "border replication",
        "edge replication padding", "boundary halo", "halo stripping", "Inter-Process Communication",
        "IPC", "Global Interpreter Lock", "GIL", "multithreading", "CPU-bound", "address space",
        "true parallelism", "tuple payload", "worker pool", "load imbalance", "start timestamp",
        "stop timestamp", "pickle", "daemon thread", "thread daemon", "sampling",
        "Comma-Separated Values", "bit-identical", "ground truth baseline", "speedup",
        "shape", "modulo wraparound", "integer underflow", "pre-warming", "overhead"
    ]
    # We can perform run-level splitting or keep text clean with appropriate runs
    pass

def apply_revisions():
    print("=== Applying Comprehensive Bab 4 Revisions to Master Document ===")
    doc = docx.Document(MASTER_LOCAL)
    
    # 1. Update Subbab 4.1 paragraphs (P257 and P258)
    p257 = doc.paragraphs[257]
    set_para_text(p257, 
        "Sistem pemrosesan citra paralel pada penelitian ini dirancang dengan menerapkan paradigma dekomposisi data (data parallelism) guna mempercepat eksekusi operasi filter spasial pada citra digital beresolusi tinggi. Alur kerja sistem memadukan pengelolaan struktur larik multidimensi pustaka NumPy, orkestrasi proses paralel modul bawaan Python multiprocessing, serta pemanfaatan pustaka OpenCV yang dibatasi hanya untuk operasi pembacaan dan penyimpanan berkas citra masukan dan luaran (file I/O). Guna memastikan bahwa akselerasi pemrosesan bersumber dari alokasi proses pekerja paralel tanpa campur tangan utas internal OpenCV, konkurensi internal pustaka dinonaktifkan melalui pengaturan parameter cv2.setNumThreads(1)."
    )
    
    p258 = doc.paragraphs[258]
    set_para_text(p258,
        "Berkas citra digital berformat RGB dibaca ke dalam memori utama menggunakan fungsi cv2.imread() dan direpresentasikan sebagai matriks piksel tiga dimensi berukuran H × W × C, dengan H merepresentasikan tinggi matriks (jumlah baris piksel), W merepresentasikan lebar matriks (jumlah kolom piksel), dan C menyatakan jumlah kanal warna (tiga kanal untuk format warna RGB). Struktur larik NumPy dialokasikan dalam memori mengikuti urutan berbasis baris (row-major order atau tata letak memori C-contiguous), sehingga seluruh elemen piksel yang berada pada baris horizontal yang sama menempati alamat ruang memori fisik yang berurutan secara linier. Susunan pengalamatan memori ini dirancang guna mendukung derajat lokalitas spasial (spatial locality) dan meminimalkan kegagalan pemuatan memori cache (cache misses) saat baris-baris piksel diakses secara berurutan oleh unit pemrosesan prosesor."
    )
    
    # 2. Update Subbab 4.2 paragraphs
    p260 = doc.paragraphs[260]
    set_para_text(p260,
        "Perancangan algoritma filter spasial citra pada penelitian ini mencakup tiga tingkatan kompleksitas komputasi: konversi derajat keabuan (Grayscale ITU-R BT.601-7) sebagai representasi operasi titik (point-wise) berbeban ringan, penghalusan citra (Gaussian Blur 3×3) sebagai representasi konvolusi spasial berbeban moderat pada tiga kanal warna, serta ekstraksi tepi (Sobel 3×3) sebagai representasi konvolusi gradien ganda intensif komputasi. Seluruh algoritma dirancang menggunakan kalkulasi larik NumPy tanpa percabangan kondisional (data-independent execution) guna memastikan stabilitas instruksi siklus pemrosesan per piksel."
    )
    
    p262 = doc.paragraphs[262]
    set_para_text(p262,
        "Konversi citra digital berwarna RGB menjadi derajat keabuan dirancang berdasarkan rekomendasi standar penyiaran ITU-R BT.601-7 (International Telecommunication Union, 2011). Operasi ini menghitung nilai intensitas luma monokrom Y' dari kombinasi linier terbobot tiga komponen kanal warna masukan (Merah R', Hijau G', dan Biru B' ter-gamma) pada setiap koordinat spasial piksel (x, y). Formulasi matematis konversi dinyatakan pada Persamaan (4.1):"
    )
    
    # Table 14 equation text
    tbl14 = doc.tables[14]
    tbl14.rows[0].cells[0].paragraphs[0].text = "Y'(x, y) = round(0,299 · R'(x, y) + 0,587 · G'(x, y) + 0,114 · B'(x, y))"
    tbl14.rows[0].cells[0].paragraphs[0].runs[0].font.name = 'Times New Roman'
    tbl14.rows[0].cells[0].paragraphs[0].runs[0].font.size = Pt(12)
    tbl14.rows[0].cells[0].paragraphs[0].runs[0].italic = True
    
    # Keterangan list
    doc.paragraphs[264].text = "Y'(x, y) : Nilai intensitas luma derajat keabuan pada koordinat (x, y) [0, 255]."
    doc.paragraphs[265].text = "R'(x, y) : Nilai intensitas kanal warna Merah (Red) masukan ter-gamma [0, 255]."
    doc.paragraphs[266].text = "G'(x, y) : Nilai intensitas kanal warna Hijau (Green) masukan ter-gamma [0, 255]."
    doc.paragraphs[267].text = "B'(x, y) : Nilai intensitas kanal warna Biru (Blue) masukan ter-gamma [0, 255]."
    for idx in range(264, 268):
        for r in doc.paragraphs[idx].runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            
    p268 = doc.paragraphs[268]
    set_para_text(p268,
        "Operasi ini memiliki radius ketetanggaan kernel k = 0, karena kalkulasi setiap piksel bersifat independen secara spasial dan tidak membutuhkan informasi nilai piksel di sekitarnya. Pada implementasi program, larik citra masukan bertipe uint8 dikonversi sementara ke tipe data float64 oleh NumPy untuk mengalikan bobot koefisien desimal guna mencegah galat pembulatan dini. Nilai hasil kemudian dibulatkan dan dipotong pada batas saturasi rentang [0, 255] menggunakan fungsi numpy.clip sebelum dikembalikan ke tipe data uint8. Transformasi ini menghasilkan luaran matriks dua dimensi berukuran H × W dari citra masukan tiga dimensi berukuran H × W × 3."
    )
    
    p270 = doc.paragraphs[270]
    set_para_text(p270,
        "Penghalusan citra (image smoothing) dirancang menggunakan konvolusi spasial linear dengan kernel Gaussian 3×3 berbasis pendekatan koefisien binomial diskret ternormalisasi. Kernel ini merupakan aproksimasi diskret berbobot bilangan bulat dari fungsi sebaran normal bivariat simetris yang setara dengan parameter deviasi standar σ ≈ 0,85. Matriks kernel pembobotan simetris dua dimensi K_Gauss dengan faktor normalisasi 1/16 didefinisikan pada Persamaan (4.2):"
    )
    
    p271 = doc.paragraphs[271]
    set_para_text(p271,
        "Operasi konvolusi spasial diskret diterapkan secara independen pada setiap kanal warna c ∈ {R, G, B} dengan radius ketetanggaan kernel k = 1. Secara matematis, kernel Gaussian dapat dipisahkan (separable) menjadi dua vektor satu dimensi, namun pada rancangan implementasi penelitian ini konvolusi dieksekusi secara langsung melalui akumulasi konvolusi 2D 9-tap per piksel. Formulasi nilai intensitas piksel keluaran terfilter I_blur(x, y, c) dinyatakan pada Persamaan (4.3):"
    )
    
    p272 = doc.paragraphs[272]
    set_para_text(p272,
        "Kalkulasi dilakukan dalam representasi data presisi float64 dengan menjumlahkan perkalian antara intensitas piksel lokal dan bobot kernel, diikuti pembulatan, pemotongan saturasi rentang [0, 255] melalui numpy.clip, dan konversi akhir ke tipe data uint8. Karena konvolusi diaplikasikan pada masing-masing kanal warna RGB secara terpisah, keluaran filter Gaussian Blur mempertahankan dimensi larik tiga dimensi yang identik dengan masukan, yaitu H × W × 3."
    )
    
    p274 = doc.paragraphs[274]
    set_para_text(p274,
        "Ekstraksi kontur dan tepi citra dirancang menggunakan operator diferensial Sobel 3×3. Citra masukan yang diterima oleh sistem berformat warna RGB. Pada alur paralel, potongan citra RGB dikirimkan ke setiap proses pekerja melalui saluran IPC. Konversi ke derajat keabuan (Grayscale) dieksekusi secara lokal di dalam masing-masing proses pekerja sebelum perhitungan gradien dimulai. Selanjutnya, diaplikasikan dua matriks kernel konvolusi ortogonal, yaitu kernel horizontal K_x untuk mendeteksi perubahan gradien intensitas pada sumbu mendatar (kolom) dan kernel vertikal K_y untuk sumbu tegak (baris), sebagaimana dirumuskan pada Persamaan (4.4):"
    )
    
    p275 = doc.paragraphs[275]
    set_para_text(p275,
        "Komponen gradien spasial mendatar G_x(x, y) dan tegak G_y(x, y) dihitung secara terpisah melalui konvolusi matriks derajat keabuan Y dengan radius kernel k = 1 pada Persamaan (4.5) dan Persamaan (4.6):"
    )
    
    p276 = doc.paragraphs[276]
    set_para_text(p276,
        "Magnitudo gradien total G(x, y) yang merepresentasikan kekuatan tepi citra dihitung menggunakan formulasi jarak Euclidean (norma L2) pada Persamaan (4.7):"
    )
    
    p277 = doc.paragraphs[277]
    set_para_text(p277,
        "Nilai magnitudo gradien G(x, y) dipotong pada batas rentang [0, 255] via numpy.clip dan dikonversi kembali ke tipe data uint8. Hasil akhir komputasi filter Sobel menghasilkan larik matriks dua dimensi berukuran H × W (atau (H/P) × W pada masing-masing proses pekerja) yang merepresentasikan peta kontur tepi citra."
    )
    
    p279 = doc.paragraphs[279]
    set_para_text(p279,
        "Dalam arsitektur pemrosesan paralel, penanganan batas tepi matriks memiliki dua tingkatan: batas global (tepi terluar citra asli) dan batas lokal (sambungan antar-blok pekerja). Untuk batas lokal antar-pekerja, sistem menerapkan mekanisme penambahan baris batas (boundary halo) yang dibahas pada Subbab 4.3.2. Sedangkan pada level eksekusi fungsi filter di dalam masing-masing submatriks, penanganan tepi dilakukan secara seragam menggunakan metode replikasi batas (edge replication padding) selebar k = 1 piksel melalui fungsi numpy.pad(..., mode='edge'). Konfigurasi lebar bantalan diterapkan secara spesifik pada sumbu spasial, yaitu ((1, 1), (1, 1)) untuk citra dua dimensi atau ((1, 1), (1, 1), (0, 0)) untuk citra RGB tanpa menambahkan bantalan pada sumbu kanal warna. Metode replikasi ini menduplikasi nilai piksel terluar ke area bantalan batas, sehingga menghasilkan konsistensi matematis yang identik antara eksekusi serial dan paralel serta mencegah timbulnya distorsi penggelapan piksel (zero-padding darkening artifact) pada garis sambungan batas potongan citra saat direkonstruksi kembali."
    )
    
    # 3. Update Subbab 4.3 paragraphs (P281, P285, P287, P289, P291)
    p281 = doc.paragraphs[281]
    set_para_text(p281,
        "Arsitektur sistem pemrosesan citra paralel dirancang dengan membagi beban komputasi spasial ke seluruh unit proses pekerja melalui tahapan dekomposisi domain spasial horizontal, penambahan baris batas (boundary halo), transmisi tugas antar-proses, dan rekonstruksi kembali matriks luaran utuh. Diagram blok arsitektur sistem pemrosesan citra paralel disajikan secara skematis pada Gambar 4.1."
    )
    
    p285 = doc.paragraphs[285]
    set_para_text(p285,
        "Dekomposisi matriks citra masukan dilakukan dengan menerapkan metode pembagian baris horizontal (horizontal row partitioning). Matriks citra berdimensi H × W × C dipotong secara merata sepanjang sumbu vertikal ke sejumlah P proses pekerja, sehingga setiap unit pekerja menerima blok data irisan citra berukuran (H/P) × W × C. Dimensi resolusi citra yang dipilih berbasis bilangan pangkat dua (2^k, yaitu 512, 1024, 2048, dan 4096 piksel) dan alokasi jumlah proses pekerja P (1, 2, 4, dan 8 proses) memiliki sifat habis dibagi (H mod P = 0). Karakteristik keterbagian ini menghasilkan pembagian jumlah baris dasar yang setara antar-pekerja, meskipun beban komputasi riil memiliki variasi kecil karena blok interior memproses dua baris batas halo tambahan dan inti prosesor hibrida memiliki karakteristik frekuensi kerja yang berbeda."
    )
    
    p287 = doc.paragraphs[287]
    set_para_text(p287,
        "Operasi konvolusi matriks spasial (seperti Gaussian Blur 3×3 dan Sobel 3×3) membutuhkan informasi intensitas piksel tetangga di sekeliling piksel target dengan radius spasial k = 1. Pada saat citra dipartisi menjadi potongan-potongan baris independen, piksel-piksel yang berada pada baris tepi atas dan bawah dari setiap potongan kehilangan akses terhadap baris tetangga aslinya. Untuk mengatasi ketergantungan data lokal tersebut tanpa menimbulkan konflik akses memori, setiap blok irisan citra diperluas dengan menambahkan k baris tetangga fisik di sisi atas dan bawah yang disebut sebagai baris batas (boundary halo). Untuk blok interior (blok pekerja di antara batas citra terluar), ditambahkan satu baris batas atas dari blok sebelumnya dan satu baris batas bawah dari blok sesudahnya, menghasilkan potongan masukan berukuran ((H/P) + 2k) × W × C. Adapun untuk blok pertama (paling atas), penambahan baris batas hanya dilakukan pada sisi bawah, dan untuk blok terakhir (paling bawah), penambahan baris batas hanya dilakukan pada sisi atas, masing-masing berukuran ((H/P) + k) × W × C. Baris batas ini dibaca secara mandiri oleh proses pekerja tanpa adanya operasi penulisan balik ke proses lain, sehingga meniadakan potensi terjadinya kondisi balapan (race condition). Volume transmisi data yang dialirkan melalui saluran IPC per pekerja pada fase distribusi dinyatakan oleh V_in = ((H/P) + 2k) × W × C_in × sizeof(uint8), sedangkan pada fase pengembalian hasil dinyatakan oleh V_out = (H/P) × W × C_out × sizeof(uint8). Sebagai contoh, pada resolusi 4096 × 4096 piksel dengan alokasi P = 8, blok interior Gaussian dan Sobel menerima V_in = (512 + 2) × 4096 × 3 bita ≈ 6,32 MB, dan mengembalikan V_out ≈ 6,29 MB untuk Gaussian (C_out = 3) atau V_out ≈ 2,10 MB untuk Sobel (C_out = 1)."
    )
    
    p289 = doc.paragraphs[289]
    set_para_text(p289,
        "Distribusi tugas komputasi memanfaatkan modul bawaan Python multiprocessing. Modul ini dipilih untuk mengatasi kendala Global Interpreter Lock (GIL) pada CPython yang membatasi eksekusi multithreading pada beban kerja intensif komputasi (CPU-bound) sehingga hanya menghasilkan percepatan marjinal sekitar 1,05 kali. Modul multiprocessing melangkahi hambatan GIL dengan menciptakan proses sistem operasi yang independen, dengan setiap proses pekerja memiliki ruang alamat memori (address space) dan instansiasi interpreter mandiri. Mekanisme ini tidak berbagi GIL antar-proses, sehingga memungkinkan terjadinya eksekusi paralel pada inti fisik prosesor multi-core. Seluruh blok irisan citra yang telah dilengkapi baris batas dibungkus ke dalam pasangan argumen (tuple payload) bersama parameter filter, kemudian didistribusikan secara simultan ke kolam pekerja (worker pool) melalui fungsi pemetaan multiprocessing.Pool.map(). Setiap proses pekerja mengeksekusi algoritma filter yang ditugaskan secara serentak pada blok memorinya masing-masing tanpa interupsi komunikasi antar-pekerja selama fase komputasi berlangsung."
    )
    
    p291 = doc.paragraphs[291]
    set_para_text(p291,
        "Setelah setiap proses pekerja menyelesaikan eksekusi filter pada blok masing-masing, langkah berikutnya adalah mengembalikan dimensi blok terfilter ke ukuran murni aslinya. Setiap proses pekerja melakukan pemotongan pembuangan (halo stripping) terhadap baris batas atas dan baris batas bawah yang sebelumnya ditambahkan, sehingga ukuran matriks hasil kembali tepat berukuran (H/P) × W (atau (H/P) × W × C untuk operasi yang mempertahankan kanal warna). Blok-blok luaran yang bersih dari baris batas tersebut kemudian dikirimkan kembali ke proses utama (master process) melalui saluran komunikasi antre pipa IPC (Inter-Process Communication). Proses utama selanjutnya menyatukan kembali potongan-potongan blok luaran secara sekuensial sepanjang sumbu vertikal menggunakan fungsi penggabungan larik numpy.vstack(). Rekonstruksi ini menghasilkan matriks citra utuh berukuran H × W yang siap divalidasi dan disimpan."
    )
    
    # 4. Update Subbab 4.4 paragraphs (P293, P294, P295, P297)
    p293 = doc.paragraphs[293]
    set_para_text(p293,
        "Pengukuran durasi waktu eksekusi komputasi dirancang dengan penempatan titik instrumentasi pewaktu berbasis fungsi monotonik time.perf_counter() dari pustaka standar Python. Sebagaimana dijelaskan pada Subbab 3.5.1, inisialisasi kolam proses pekerja dan prosedur pemanasan awal (pre-warming) dieksekusi sebelum jendela waktu pengukuran dimulai guna mengeliminasi penalti inisialisasi proses. Titik stempel waktu awal (start timestamp, t_start) dicatat tepat sesaat sebelum proses partisi matriks citra dan penambahan baris batas dimulai. Seluruh fase pemrosesan paralel—mencakup dekomposisi baris horizontal, serialisasi objek data (pickle), transmisi melalui saluran pipa IPC, eksekusi komputasi filter pada kolam proses pekerja, pemangkasan baris batas (halo stripping), transmisi pengembalian hasil parsial, hingga rekonstruksi citra utuh melalui numpy.vstack—berada di dalam jendela pengukuran waktu komputasi. Stempel waktu akhir (stop timestamp, t_stop) dicatat segera setelah matriks citra utuh berhasil disusun kembali pada memori proses utama. Selisih t_stop - t_start ditetapkan sebagai waktu eksekusi paralel aktual (T_paralel). Secara simetris, durasi waktu eksekusi serial (T_serial) diukur dari sesaat sebelum fungsi filter dipanggil (mencakup replikasi batas tepi dan kalkulasi konvolusi) hingga matriks hasil selesai terbentuk pada memori. Operasi pembacaan citra awal dari media penyimpanan (cv2.imread) dan penyimpanan berkas luaran ke media penyimpanan (cv2.imwrite) diisolasi di luar rentang stempel waktu tersebut, sehingga durasi yang tercatat mencerminkan performa komputasi dan beban tambahan (overhead) koordinasi paralel sistem."
    )
    
    p294 = doc.paragraphs[294]
    set_para_text(p294,
        "Pemantauan beban kerja prosesor dirancang secara asinkron menggunakan kelas CPUMonitor yang berjalan pada thread daemon latar belakang mandiri. Kelas ini melakukan percontohan (sampling) persentase utilisasi CPU setiap interval 20 milidetik (0,02 detik) melalui pemanggilan psutil.cpu_percent(interval=None, percpu=True) tanpa memblokir kalkulasi pada proses utama. Sebelum jendela eksekusi dimulai, fungsi tersebut dipanggil satu kali untuk mengosongkan riwayat pembacaan internal psutil. Pemantau CPU dimulai tepat sebelum eksekusi komputasi dan dihentikan segera setelah rekonstruksi citra utuh selesai (sebelum prosedur verifikasi bit-identik), sehingga nilai rata-rata utilisasi CPU yang dihimpun merefleksikan aktivitas prosesor selama jendela komputasi berlangsung."
    )
    
    p295 = doc.paragraphs[295]
    set_para_text(p295,
        "Guna mendukung keterlacakan data (data traceability) dan keterulangan pengujian, seluruh data hasil pengukuran dari 810 pasangan repetisi eksperimen disimpan ke dalam berkas telemetri berformat Comma-Separated Values (CSV). Setiap baris rekaman merepresentasikan satu iterasi pengujian terperinci dengan 15 atribut parameter kinerja. Struktur skema data telemetri dirangkum pada Tabel 4.1."
    )
    
    p297 = doc.paragraphs[297]
    set_para_text(p297,
        "Data telemetri mentah yang dihimpun pada berkas benchmark_results.csv mencakup 810 baris pengamatan individual (720 pasangan serial-paralel dan 90 pasangan kontrol A/A). Pada baris pengamatan kontrol A/A (P = 1), nilai efisiensi dan overhead tetap dicatat secara matematis oleh skrip sebagai indikator batas derau sistem, namun dieksklusikan dari pemodelan kurva skalabilitas komputasi paralel. Untuk memfasilitasi analisis komparatif dan pemodelan kurva skalabilitas pada Bab 5, sistem secara otomatis melakukan agregasi statistik (menghitung nilai median, rentang antarkuartil IQR, nilai rerata, simpangan baku, dan selang kepercayaan 95% per kelompok perlakuan) dan menyimpannya ke dalam berkas ikhtisar 49 kolom benchmark_results_summary.csv. Berkas data mentah dan ringkasan telemetri ini dilampirkan secara lengkap pada Lampiran A dan Lampiran B sebagai wujud transparansi ilmiah."
    )
    
    # 5. Update Subbab 4.5 paragraphs (P299, P300, P301, P302, P303)
    p299 = doc.paragraphs[299]
    set_para_text(p299,
        "Perancangan verifikasi integritas citra bertujuan menjaga keabsahan luaran hasil komputasi paralel agar identik hingga level bit (bit-identical) terhadap citra hasil komputasi serial acuan (ground truth baseline). Dekomposisi domain spasial berbasis partisi baris horizontal, serialisasi data antar-proses melalui saluran pipa Inter-Process Communication (IPC), penambahan baris batas (boundary halo), hingga rekonstruksi matriks utuh melalui numpy.vstack membawa risiko timbulnya artefak spasial, distorsi pergeseran baris, maupun diskontinuitas nilai piksel antarsubmatriks apabila batas partisi tidak ditangani secara tepat. Verifikasi bit-identik memastikan bahwa luaran paralel bernilai setara secara deterministik piksel-per-piksel terhadap hasil serial acuan pada citra uji, sehingga selisih waktu eksekusi tidak dapat dikaitkan dengan perbedaan luaran komputasi. Prosedur verifikasi ini diterapkan pada seluruh 720 pasangan pengujian serial-paralel dan 90 pasangan kontrol A/A (mencakup 810 pasangan pengujian secara individual)."
    )
    
    p300 = doc.paragraphs[300]
    set_para_text(p300,
        "Alur kerja verifikasi integritas citra dirancang melalui dua tahapan inspeksi berurutan. Tahap pertama adalah verifikasi keselarasan geometri matriks, yaitu memeriksa kesesuaian atribut dimensi (shape) matriks citra keluaran paralel (I_paralel) terhadap matriks serial (I_serial), mencakup tinggi matriks (H), lebar matriks (W), dan jumlah kanal warna (C). Apabila dimensi tidak cocok, pengujian langsung dinyatakan gagal. Tahap kedua adalah evaluasi kesetaraan seluruh elemen matriks secara deterministik menggunakan fungsi numpy.array_equal(I_paralel, I_serial). Apabila fungsi tersebut mengembalikan nilai True, kondisi disparitas absolut maksimum terpenuhi tanpa perbedaan piksel (Δ_max = 0), atribut is_identical dicatat bernilai True, dan max_diff bernilai 0,0. Sebaliknya, apabila terdeteksi perbedaan (False), matriks citra dikonversi ke tipe data bilangan riil presisi ganda (float64) guna mencegah anomali luapan bawah (modulo wraparound) pada format uint8 saat menghitung nilai selisih absolut maksimum (Δ_max), atribut is_identical dicatat False, dan iterasi ditandai sebagai anomali komputasi."
    )
    
    p301 = doc.paragraphs[301]
    set_para_text(p301,
        "Disparitas absolut maksimum (Δ_max) dihitung guna mendeteksi deviasi nilai piksel paling ekstrem di seluruh koordinat spasial citra, sebagaimana diformulasikan pada Persamaan (4.8):"
    )
    
    p302 = doc.paragraphs[302]
    set_para_text(p302,
        "Kriteria kelulusan integritas citra ditetapkan secara biner tanpa toleransi deviasi numerik (Δ_max = 0). Evaluasi deterministik ini mengonfirmasi kesetaraan nilai numerik piksel pada citra hasil pengujian secara objektif. Pada 90 pasangan pengujian kontrol A/A (P = 1), prosedur verifikasi menghasilkan keidentikan bit piksel yang konsisten sebagai verifikasi dasar bahwa dua pemanggilan serial independen menghasilkan nilai yang identik."
    )
    
    p303 = doc.paragraphs[303]
    set_para_text(p303,
        "Seluruh prosedur verifikasi integritas citra bit-identik ditempatkan secara terisolasi di luar jendela pengukuran waktu komputasi, yaitu setelah stempel waktu akhir (t_stop) dicatat oleh fungsi pewaktu time.perf_counter(). Melalui arsitektur isolasi ini, beban komputasi tambahan yang timbul akibat konversi tipe data ke float64, pengurangan matriks piksel, dan pemindaian nilai ekstrem tidak membebani catatan durasi waktu eksekusi paralel (T_paralel) maupun metrik percepatan komputasi yang dihimpun pada sistem telemetri."
    )
    
    print("Saving updated master document locally...")
    doc.save(MASTER_LOCAL)
    print("Local master save successful!")
    
    try:
        shutil.copy2(MASTER_LOCAL, MASTER_ONEDRIVE)
        print("OneDrive master copy successful!")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

if __name__ == '__main__':
    apply_revisions()
