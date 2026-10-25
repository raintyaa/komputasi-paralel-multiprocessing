# PANDUAN KOMPREHENSIF DAN CATATAN AUDIT BAB LAPORAN AKHIR
**Mata Kuliah:** Komputasi Paralel  
**Topik:** Komparasi Kinerja Pemrosesan Citra Digital (Serial vs Multiprocessing) Berdasarkan Skalabilitas Resolusi, Alokasi Proses, dan Kompleksitas Algoritma  
**Repositori Proyek:** [komputasi-paralel-multiprocessing](file:///d:/Rakha/File%20Kuliah/Semester%205/Komputasi%20Paralel/UTS)  
**Dokumen Naskah:** [`Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx`](file:///d:/Rakha/File%20Kuliah/Semester%205/Komputasi%20Paralel/UTS/Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx)

---

## 1. IKHTISAR DAN PRINSIP DASAR PENULISAN
Dokumen ini merupakan panduan utama (*master guide*) yang merangkum seluruh catatan audit, struktur subbab yang telah disempurnakan, batasan ilmiah, angka empiris kunci, dan aturan sitasi akademik untuk penyusunan Laporan Akhir Tugas Akhir / Praktikum Komputasi Paralel.

> [!IMPORTANT]
> **5 Prinsip Integritas Ilmiah yang Tidak Boleh Dilanggar:**
> 1. **Kaidah Sitasi Berbasis Fakta:** Setiap kalimat yang memuat data numerik, spesifikasi teknis, atau klaim faktual WAJIB mencantumkan sitasi valid. Dilarang menggunakan klaim tanpa sumber. Kalimat rancangan mandiri harus ditandai jelas (misal: *"Pada rancangan penelitian ini..."*).
> 2. **Jendela Usia Referensi (2021–2026):** Syarat *"minimal 5 referensi terbitan 5 tahun terakhir"* adalah batas bawah (*lower bound*). Referensi klasik (Amdahl 1967, Karp & Flatt 1990) diizinkan sebagai sumber primer rumus teoretis.
> 3. **Pemisahan Konsep Teori (Bab 2), Metode (Bab 3), dan Perancangan (Bab 4):**
>    - **Bab 2:** Teori dan formula matematis murni.
>    - **Bab 3:** Desain pengujian (variabel, matriks A/B/C, instrumen ukur, protokol pengujian, dan metode statistika).
>    - **Bab 4:** Perancangan rekayasa teknis sistem (*row slicing*, *boundary halo*, alur tipe data, stempel waktu, skema CSV).
> 4. **Validitas Dahulu Sebelum Efisiensi (Bab 5):** Evaluasi integritas bit-identik (810/810 valid) dan kontrol derau A/A ($P=1$) dibahas di awal Bab 5 sebelum data waktu dan *speedup* dianalisis.
> 5. **Kejujuran Terhadap Data (*No Overclaiming*):**
>    - Penurunan imbal hasil (*diminishing returns*) pada $P=8$, bukan *plateau* menyeluruh (karena Grayscale dan Gaussian tetap naik signifikan $p < 0{,}001$).
>    - Hubungan resolusi dan *speedup* tidak monoton (jangan klaim *"makin besar citra makin cepat"*).
>    - Fenomena Sobel 512 disebut *"Hipotesis Efek Cache"*, bukan klaim pembuktian mutlak.
>    - Hukum Amdahl *"dicocokkan"* ke data (*curve fitting*), bukan *"dibuktikan"*.
>    - Utilisasi CPU adalah *"tren indikatif kasar"*, bukan metrik perbandingan performa filter.

---

## 2. PANDUAN RINCI PER BAB

### BAB 1 PENDAHULUAN
* **1.1 Latar Belakang:**
  * 5 paragraf berantai logis:
    1. Tren citra resolusi tinggi, jutaan piksel, aplikasi pada diagnosis medis, pertanian cerdas, otomasi industri (Cremel & Arruda, 2026), beban kuadratik konvolusi Sobel $4\times$ lipat (Cremel & Arruda, 2026; Gonzalez & Woods, 2018). *Catatan: Jangan gunakan klaim salah mengenai CT/MRI 2048–4096 px!*
    2. Arsitektur multi-core dan pemborosan daya pada program serial konvensional (Pacheco & Malensek, 2022; Cremel & Arruda, 2026).
    3. Tinjauan akselerasi: Sobel GPU 6,7–13× (Chang et al., 2023), latensi CPU konvensional (Vasile et al., 2024), akselerasi filter CPU multi-core OpenMP dengan penurunan efisiensi tajam ke ~24% pada 8 thread (Cremel & Arruda, 2026), Gaussian blur parallel (Ibrahim et al., 2021), mekanisme penguncian CPython GIL (Python Software Foundation, n.d.-a), pembuktian empiris keterbatasan multithreading 1,05× vs keunggulan multiprocessing 3,16–3,55× (Gultom & Sarumaha, 2025; Tanenbaum & Bos, 2022).
    4. Paradigma data parallelism (Pacheco & Malensek, 2022), multiprocessing Python (Python Software Foundation, n.d.-b), sifat embarrassingly parallel (Cremel & Arruda, 2026), penanganan baris batas (*boundary halo*) bebas race condition.
    5. Kebaruan (*Novelty / Research Gap*): Penelitian multi-core terdahulu didominasi model berbasis thread seperti OpenMP (Cremel & Arruda, 2026). Perilaku skalabilitas multiprocessing Python berbasis proses mandiri, beban overhead IPC, dan karakteristik pada prosesor hibrida (P-Core vs E-Core) belum banyak dipetakan. Pengujian 3 filter pada 512–4096 px ($P=1,2,4,8$), dikomparasikan terhadap Hukum Amdahl (Amdahl, 1967) dan Karp–Flatt (Karp & Flatt, 1990).
* **1.2 Rumusan Masalah (4 Butir):**
  1. Pengaruh kenaikan resolusi matriks ($512 \dots 4096$) terhadap *speedup*, efisiensi, dan *overhead*.
  2. Karakteristik skalabilitas alokasi *worker* ($P=1,2,4,8$) pada prosesor hibrida terhadap Hukum Amdahl dan metrik Karp–Flatt.
  3. Pengaruh kompleksitas algoritma filter (*Grayscale*, *Gaussian Blur 3×3*, *Sobel 3×3*) terhadap beban komputasi dan utilisasi CPU.
  4. Pembuktian jaminan integritas matriks luaran paralel 100% bit-identik terhadap serial tanpa cacat batas partisi.
* **1.3 Batasan Masalah (5 Butir):**
  1. Citra RGB tanpa kompresi, variasi $512 \dots 4096$ px dari basis data Aesthetic-4K.
  2. Tiga filter bertingkat: *Grayscale* (titik), *Gaussian Blur 3×3* (area linier), *Sobel 3×3* (gradien non-linier).
  3. Perangkat lunak: Python 3.14 (CPython 64-bit), multiprocessing (metode spawn), NumPy 2.5.4, OpenCV 5.0.0 (utas tunggal), psutil 7.2.2.
  4. Dekomposisi spasial horizontal (*horizontal row partitioning*) dengan baris batas (*boundary halo*) $k=0$ dan $k=1$.
  5. Perangkat keras: Intel Core i5-13420H (4 P-core + 4 E-core, 12 thread), 16 GB RAM, Windows 11, pengujian $P = 1, 2, 4, 8$.
* **1.4 Tujuan Penelitian:** 4 butir selaras 1-to-1 dengan Rumusan Masalah.
* **1.5 Manfaat Penelitian:** Praktisi visi komputer, industri otomasi/medis, dan akademisi.
* **1.6 Sistematika Penulisan:** Ringkasan struktur BAB 1 hingga BAB 6.

---

### BAB 2 LANDASAN TEORI (4 Subbab, 8 Anak Subbab)
* **2.1 Perbandingan Terhadap Penelitian Terdahulu:**
  * Tabel perbandingan penelitian: Chang et al. (2023), Vasile et al. (2024), Cremel & Arruda (2026), Ibrahim et al. (2021), Gultom & Sarumaha (2025). Kolom: Peneliti & Tahun, Metode / Perangkat, Filter yang Diuji, Temuan Utama, Posisi Perbedaan dengan Penelitian Ini.
* **2.2 Pengolahan Citra Digital dan Operasi Filter Spasial:**
  * **2.2.1 Representasi Citra Digital dan Operasi Konvolusi 2D:** Matriks larik *row-major (C-contiguous)*, koordinat $(x,y)$, Persamaan (1) konvolusi 2D dengan padding.
  * **2.2.2 Karakteristik Algoritma Filter Spasial yang Diuji:** Konversi Grayscale ITU-R BT.601 ($0{,}299R + 0{,}587G + 0{,}114B$), kernel Gaussian Blur 3×3 (bobot $[[1,2,1],[2,4,2],[1,2,1]]/16$), operator Sobel 3×3 ($G_x, G_y$ dan magnitudo $\sqrt{G_x^2 + G_y^2}$). Tabel ringkasan filter: jenis operasi, ukuran kernel, kompleksitas kalkulasi.
* **2.3 Komputasi Paralel dan Multiprocessing Python:**
  * **2.3.1 Paradigma Data Parallelism dan Dekomposisi Domain Spasial:** Prinsip *data parallelism*, partisi horizontal, konsep ketergantungan baris batas (*halo*).
  * **2.3.2 Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC:** Batasan CPython GIL, ruang memori mandiri, mekanisme komunikasi antar-proses (IPC pipe), serialisasi objek dengan *pickle*, dan aturan metode *spawn* pada OS Windows.
  * **2.3.3 Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache:** Inti fisik vs thread logis (SMT), arsitektur hibrida Raptor Lake (P-Core kinerja tinggi vs E-Core hemat daya), hierarki cache (L1, L2, dan 12 MB L3 Intel Smart Cache bersama) yang mendasari pembahasan Bab 5.
* **2.4 Metrik Evaluasi Kinerja dan Model Skalabilitas:**
  * **2.4.1 Metrik Kinerja Dasar: Waktu Eksekusi, Speedup, Efisiensi, dan Overhead Paralel:** Persamaan (2) Speedup $S = T_s / T_p$, Persamaan (3) Efisiensi $E = (S/P) \times 100\%$, Persamaan (4) Durasi Overhead $T_{\mathrm{overhead}} = T_p - (T_s/P)$.
  * **2.4.2 Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp–Flatt:** Persamaan (5) Hukum Amdahl $S = 1 / ((1-f) + f/P)$ dengan $(1-f)$ mencakup overhead koordinasi nyata; Persamaan (6) Metrik Karp–Flatt $e = ((1/S) - (1/P)) / (1 - 1/P)$ untuk mendiagnosis apakah hambatan skalabilitas berasal dari bagian serial murni atau pembengkakan koordinasi IPC.
  * **2.4.3 Analisis Statistik Pengukuran dan Evaluasi Batas Derau Sistem (Kontrol A/A):** Ukuran pemusatan median dan rentang antarkuartil (IQR $[Q_{25} - Q_{75}]$) untuk data asimetris, selang kepercayaan 95% distribusi $t$-Student ($t_{29, 0{,}025} = 2{,}04523$), dan pengujian kontrol A/A ($P=1$) untuk memetakan batas derau (*noise floor*).

---

### BAB 3 METODOLOGI PENELITIAN (6 Subbab, 9 Anak Subbab)
* **3.1 Tahapan Penelitian:**
  * Menjelaskan Gambar 3.1 Bagan Alir Penelitian 6 tahap (Tahap 1 Studi Literatur, Tahap 2 Perancangan Algoritma, Tahap 3 Penyiapan Data, Tahap 4 Eksekusi Eksperimen Terkontrol, Tahap 5 Pencatatan Kinerja, Tahap 6 Analisis Skalabilitas).
* **3.2 Pengumpulan dan Standardisasi Data Citra Master:**
  * Repositori Aesthetic-4K (Aesthetic-4K Dataset, 2025) lisensi CC-BY 4.0.
  * *Center-crop* tanpa kompresi ke 512, 1024, 2048, 4096 px.
  * Argumentasi ilmiah sifat *data-independent* konvolusi (kalkulasi piksel tidak memiliki percabangan kondisional terhadap isi visual), sehingga 1 citra master memadai untuk meniadakan variasi tekstur dan mengisolasi variabilitas sistem.
* **3.3 Alat dan Bahan Penelitian:**
  * **3.3.1 Perangkat Keras dan Kondisi Operasional:** Tabel spesifikasi Intel Core i5-13420H (4 P-Core @ 2.1–4.6 GHz, 4 E-Core @ 1.5–3.4 GHz, 12 thread), 16 GB RAM DDR4/DDR5, SSD NVMe. Catatan kondisi: laptop terhubung adaptor listrik AC, mode daya Windows Best Performance, pemantauan suhu awal.
  * **3.3.2 Perangkat Lunak dan Pustaka Komputasi:** Windows 11 Home 64-bit, Python 3.14 (CPython build standar), NumPy 2.5.4, OpenCV 5.0.0, psutil 7.2.2, Matplotlib 3.10.0, SciPy.
  * **3.3.3 Alat Ukur dan Instrumentasi Kinerja:** Fungsi `time.perf_counter()` berpresisi nanodetik untuk isolasi durasi komputasi murni. Metode pemantauan CPU proses utama via `psutil` (catatan: beban proses pekerja tidak teragregasi penuh, menjadi tren indikatif kasar).
* **3.4 Desain Eksperimen:**
  * Identifikasi variabel: Bebas (resolusi, alokasi proses, algoritma filter), Terikat (waktu, speedup, efisiensi, overhead, CPU%), Kontrol (citra master, lingkungan OS, single-thread OpenCV).
  * Tabel Matriks Uji: Skenario A (12 kondisi), Skenario B (12 kondisi termasuk $P=1$), Skenario C (3 kondisi). Total 27 kondisi $\times$ 30 repetisi = 810 eksekusi.
  * Tabel Definisi Parameter Kinerja.
* **3.5 Prosedur Pengukuran dan Pengujian:**
  * **3.5.1 Protokol Pemanasan Awal (Pre-Warming Worker Pool):** Pembentukan pool sebelum pencatatan waktu guna mengeliminasi penalti *cold spawn* Windows (Python Software Foundation, n.d.-b).
  * **3.5.2 Protokol Jeda Dingin (Cool-Down Buffer) dan Isolasi Noise Sistem:** Jeda pendinginan termal 0,5 detik antar-iterasi guna meminimalkan pelambatan termal (*thermal throttling*).
  * **3.5.3 Pengujian Berselang-seling (Interleaved Execution 30 Repetisi) dan Kontrol A/A:** Eksekusi serial-paralel berselang-seling 30x untuk meratakan fluktuasi suhu sistem; pengujian $P=1$ sebagai kontrol dasar A/A.
  * *Catatan batasan metodologis:* Urutan blok dieksekusi berurutan (Blok A, Blok B, Blok C) tanpa pengacakan global (*systematic drift limitation*).
* **3.6 Teknik Analisis Data:**
  * Uji statistik non-parametrik Median & IQR $[Q_{25} - Q_{75}]$; CI 95% $t$-Student; uji beda Kruskal–Wallis / Mann–Whitney; regresi kuadrat terkecil fitting kurva Amdahl; penghitungan $e$ Karp–Flatt; kriteria verifikasi bit-identik ($\Delta_{\max} = 0$, rujuk ke 4.5).
  * *Kaidah:* Dilarang menuliskan hasil angka ($f$, speedup) di Bab 3!

---

### BAB 4 PERANCANGAN SISTEM (5 Subbab, 4 Anak Subbab)
* **4.1 Deskripsi Sistem Pemrosesan Citra Paralel:**
  * Gambar 4.1 Diagram Blok Arsitektur Sistem Paralel.
  * Peran pustaka: NumPy (larik C-contiguous), multiprocessing (dispatcher & pool), OpenCV (I/O berkas citra dibatasi 1 utas).
* **4.2 Perancangan Algoritma Filter Spasial:**
  * Tabel terpadu nilai kernel/bobot konvolusi (Grayscale BT.601, Gaussian Blur 3×3 normalisasi 1/16, Sobel $G_x, G_y$).
  * Penanganan batas tepi citra: Menggunakan replikasi tepi (*edge replication* / `mode="edge"` pada `np.pad`) agar ukuran citra konsisten tanpa artifak garis hitam buatan.
  * Alur tipe data (*dtype lifecycle*): Masukan `uint8` $\to$ kalkulasi `float64` (mencegah overflow) $\to$ pemotongan dinamis `np.clip(..., 0, 255)` $\to$ kembalikan ke `uint8` sebelum pengiriman IPC (menghemat ukuran payload data hingga 8 kali lipat).
* **4.3 Perancangan Arsitektur Paralel:**
  * **4.3.1 Pembagian Blok Baris Horizontal:** Tinggi dasar $h_{\mathrm{chunk}} = \lfloor H/P \rfloor$, indeks $[\text{start\_y}, \text{end\_y})$, penanganan baris sisa modulo $H \pmod P$ dialokasikan ke pekerja terakhir.
  * **4.3.2 Penanganan Baris Batas (Boundary Halo):** Radius $k=1$ (Gaussian & Sobel), $k=0$ (Grayscale). Halo asimetris satu sisi untuk blok teratas ($\text{halo\_top}=0, \text{halo\_bottom}=k$) dan blok terbawah ($\text{halo\_top}=k, \text{halo\_bottom}=0$). Pemangkasan baris halo di sisi worker sebelum dikembalikan via IPC: `trimmed = block[halo_top : h - halo_bottom]`.
  * **4.3.3 Distribusi Tugas dan Sinkronisasi Proses:** Pemetaan tugas via `multiprocessing.Pool.map()`, *pre-warmed pool*, serialisasi tuple argumen via `pickle`, penjadwalan statis tanpa afinitas inti.
  * **4.3.4 Rekonstruksi Citra Utuh:** Penggabungan kembali sub-larik terfilter menggunakan `np.vstack(processed_chunks)` setelah sinkronisasi blok `Pool.map()` tuntas.
* **4.4 Perancangan Pengukuran dan Pencatatan Telemetri:**
  * Titik stempel waktu: `t_start = time.perf_counter()` tepat sebelum pembuatan partisi, `t_stop = time.perf_counter()` tepat setelah `np.vstack()`. Operasi I/O disk dikeluarkan dari interval pengukuran.
  * Skema 15 kolom data telemetri CSV mentah (`timestamp, scenario, filter, resolution, image_id, iteration, p, t_serial, t_parallel, speedup, efficiency, overhead, cpu_utilization, is_identical, max_diff`).
* **4.5 Perancangan Verifikasi Integritas Citra Bit-Identik:**
  * Kriteria uji kelulusan biner mutlak: $\Delta_{\max} = \max |I_p - I_s| = 0 \iff \text{np.array\_equal}(I_p, I_s) == \text{True}$.
  * Argumentasi deterministik: konvolusi spasial bersifat lokal terhadap ketetanggaan radius $k$, sehingga penambahan baris halo fisik menjamin hasil potongan identik dengan pemrosesan tanpa partisi.
  * Penanganan jika terjadi anomali (sesuai decision diamond bagan alir Gambar 3.1).

---

### BAB 5 HASIL DAN PEMBAHASAN (5 Subbab)
* **5.1 Implementasi Sistem Pemrosesan Citra Paralel:**
  * Uraian ringkas implementasi kode (`src/filters.py`, `src/parallel_engine.py`, `src/serial_engine.py`, `run_benchmark.py`), merujuk ke kode lengkap pada Lampiran C.
* **5.2 Validasi Integritas Data dan Keterulangan Pengujian (Wajib di Awal!):**
  * **5.2.1 Evaluasi Integritas Luaran Citra Bit-Identik:** Bukti empiris 810 dari 810 eksekusi menghasilkan $\Delta_{\max} = 0$ (100% kesetaraan bit-identik). Membuktikan arsitektur *halo padding* berhasil total meniadakan cacat jahitan partisi.
  * **5.2.2 Evaluasi Kontrol Dasar A/A (P = 1) dan Batas Derau Sistem:** Analisis serial vs serial pada $P=1$. Rata-rata speedup $0{,}997\times \approx 1{,}00\times$, efisiensi $\approx 99{,}7\%$. Ini menjadi batas derau (*noise floor*) bahwa variasi di atas $1\%$ adalah efek paralelisasi nyata.
  * **5.2.3 Evaluasi Keterulangan Antar-Blok Pengujian (Repeatability Drift):** Komparasi kondisi identik (resolusi 2048 px, $P=4$) pada Blok A3, Blok B2, dan Blok C. Mencatat pergeseran waktu eksekusi baseline serial Blok A yang sedikit lebih lambat sebagai konsekuensi urutan eksekusi tanpa pengacakan.
* **5.3 Hasil Pengujian Sistem dan Analisis Kinerja:**
  * **5.3.1 Skenario A (Pengaruh Resolusi Matriks Citra):** Tabel Ringkasan 12 baris (Median [Q25-Q75], Speedup CI95%, Efisiensi, Overhead) + Gambar 5.1 Grafik Skenario A.
  * **5.3.2 Skenario B (Skalabilitas Alokasi Worker):** Tabel Ringkasan 12 baris (termasuk $P=1$) + Gambar 5.2 Grafik Skenario B.
  * **5.3.3 Skenario C (Karakteristik Kompleksitas Filter):** Tabel Ringkasan 3 baris (kondisi 2048 px $P=4$) + Gambar 5.3 Grafik Skenario C.
* **5.4 Pencocokan Model Teoretis Skalabilitas:**
  * **5.4.1 Estimasi Parameter Fraksi Paralel Hukum Amdahl:** Pencocokan kurva kuadrat terkecil pada rasio percepatan Skenario B ($P=2, 4, 8$). Estimasi $f$: Grayscale $f \approx 0{,}69$, Gaussian Blur $f \approx 0{,}76$, Sobel $f \approx 0{,}79$. Menunjukkan bahwa satu nilai $f$ tunggal tidak dapat mewakili seluruh filter citra.
  * **5.4.2 Diagnostik Beban Koordinasi Berdasarkan Metrik Karp–Flatt:** Evaluasi $e$ terhadap $P$. Nilai $e$ pada Sobel meningkat nyata ($0{,}13 \to 0{,}15 \to 0{,}23$), membuktikan secara empiris bahwa pembatas percepatan bukan sekadar bagian sekuensial konstan, melainkan beban tambahan koordinasi IPC yang membengkak seiring bertambahnya proses.
* **5.5 Pembahasan Temuan dan Keterbatasan Penelitian:**
  * **5.5.1 Dinamika Resolusi Citra dan Hipotesis Efek L3 Cache pada Sobel 512:** Analisis mengapa speedup tidak monoton terhadap resolusi. Pembahasan superlinearitas Sobel 512 ($S \approx 3{,}89$ pada 4 proses) yang didukung hipotesis bahwa data matriks $512 \times 512$ beserta halo termuat utuh dalam 12 MB L3 Smart Cache bersama, meniadakan penalti latensi bus memori utama.
  * **5.5.2 Karakteristik Skalabilitas Worker, Arsitektur Hibrida, dan Diminishing Returns:** Penjelasan fenomena penurunan imbal hasil (*diminishing returns*) saat beralih dari $P=4$ ke $P=8$. Kenaikan tetap signifikan secara statistik untuk Grayscale dan Gaussian ($p < 0{,}001$), namun Sobel mengalami stagnasi ($p = 0{,}15$) akibat saturasi throughput memori dan alokasi 4 E-Core yang memiliki IPC lebih rendah serta tanpa hyper-threading.
  * **5.5.3 Karakteristik Beban Tambahan (Overhead) Serialisasi IPC dan Utilisasi CPU:** Hubungan searah antara dimensi citra dan overhead serialisasi *pickle* memori. Penegasan utilisasi CPU psutil sebagai tren kasar beban kerja sistem.
  * **5.5.4 Komparasi Temuan terhadap Penelitian Terdahulu:** Komparasi mendalam terhadap Gultom & Sarumaha (2025) (mengapa speedup kita $1{,}90\times - 2{,}74\times$ pada 4 worker, sedangkan Gultom mencapai $3{,}16\times - 3{,}55\times$ $\to$ perbedaan mendasar antara komputasi numerik murni vs transfer payload citra berukuran masif di IPC); perbandingan dengan Cremel & Arruda (2026) (model OpenMP thread vs Python process); dan Chang et al. (2023) (akselerasi GPU).
  * **5.5.5 Sintesis Jawaban Rumusan Masalah dan Keterbatasan Penelitian:** Jawaban tegas atas 4 rumusan masalah dan pengakuan jujur atas keterbatasan penelitian (urutan blok tidak diacak, satu citra master, pengujian pada 1 mesin laptop, dan ketiadaan telemetri sensor suhu kontinu).

---

### BAB 6 PENUTUP (2 Subbab)
* **6.1 Kesimpulan (Tepat 4 Poin Sinkron 1-to-1 dengan Rumusan Masalah):**
  1. **Pengaruh Resolusi (R1):** Peningkatan resolusi citra dari $512 \times 512$ hingga $4096 \times 4096$ piksel pada alokasi $P=4$ proses menghasilkan rasio percepatan (*speedup*) empiris antara $1{,}68\times$ hingga $3{,}89\times$, dengan pola skalabilitas yang tidak bersifat monoton terhadap kenaikan dimensi spasial. Efisiensi tertinggi diraih pada operasi Sobel resolusi $512 \times 512$ piksel ($97{,}3\%$, $S = 3{,}89\times$), sedangkan resolusi $4096 \times 4096$ piksel mencapai *speedup* $1{,}90\times$ hingga $2{,}48\times$ akibat pembengkakan beban transfer memori.
  2. **Skalabilitas Alokasi Worker (R2):** Penambahan alokasi proses kerja dari $P=2$ hingga $P=8$ pada resolusi $2048 \times 2048$ piksel meningkatkan rasio percepatan namun disertai penurunan efisiensi (*diminishing returns*). Data empiris konsisten dengan model teoretis Hukum Amdahl pada estimasi fraksi paralel efektif $f = 0{,}69$ untuk Grayscale, $f = 0{,}76$ untuk Gaussian Blur, dan $f = 0{,}79$ untuk Sobel. Evaluasi metrik Karp–Flatt memperlihatkan kenaikan fraksi serial eksperimental $e$ pada Sobel dari $0{,}13$ ($P=2$) menjadi $0{,}23$ ($P=8$), membuktikan bahwa beban koordinasi IPC membengkak seiring penambahan proses kerja.
  3. **Pengaruh Kompleksitas Algoritma Filter (R3):** Tingkat kompleksitas matematis operasi filter menentukan durasi beban tambahan (*overhead*) dan rasio percepatan secara bertingkat. Durasi *overhead* paralel tertinggi tercatat pada Gaussian Blur ($0{,}113$ detik), diikuti Sobel ($0{,}085$ detik), dan terendah pada Grayscale ($0{,}034$ detik). Algoritma dengan beban kalkulasi lebih intensif (Sobel dan Gaussian Blur) menghasilkan percepatan yang jauh lebih tinggi daripada operasi titik sederhana (Grayscale) karena rasio waktu komputasi terhadap waktu komunikasi IPC yang lebih besar.
  4. **Jaminan Integritas Citra Bit-Identik (R4):** Arsitektur dekomposisi spasial horizontal dengan penanganan baris batas (*boundary halo*) sebesar $k=1$ terbukti menjamin integritas luaran citra paralel secara sempurna. Pengujian terhadap seluruh 810 eksekusi pada 27 kondisi uji menghasilkan deviasi mutlak piksel $\Delta_{\max} = 0$ (100% bit-identik terhadap hasil referensi serial murni), membuktikan bahwa sistem sepenuhnya bebas dari cacat pemotongan atau distorsi visual pada batas partisi.
  * *Kaidah:* Panjang sekitar 1 halaman, berisi angka konkret hasil, tanpa klaim baru, tanpa sitasi literatur.
* **6.2 Saran (5 Rekomendasi Teknis Spesifik & Terukur):**
  1. **Pengukuran Utilisasi CPU Berbasis Utas/Proses:** Disarankan mengukur utilisasi CPU melalui akumulasi waktu CPU per proses pekerja (*per-process CPU user and system times* via `psutil.Process.cpu_times()`) guna memperoleh estimasi beban komputasi paralel yang akurat tanpa bias agregasi sistem operasi.
  2. **Pengacakan Urutan Blok dan Telemetri Sensor Suhu:** Penelitian selanjutnya disarankan menerapkan rancangan acak kelompok (*randomized block design*) pada urutan pengujian Skenario A, B, dan C, serta merekam telemetri suhu inti CPU dan frekuensi dinamis secara kontinu guna memetakan korelasi langsung pelambatan termal (*thermal throttling*).
  3. **Penerapan Penjadwalan Dinamis dan Pemasangan Afinitas Inti:** Disarankan mengeksplorasi strategi penjadwalan dinamis (*dynamic task chunking* dengan jumlah potongan melebihi jumlah pekerja) serta menguji penguncian afinitas inti prosesor (*CPU affinity pinning*) secara spesifik ke P-Core atau E-Core guna menganalisis dampak heterogenitas mikroarsitektur prosesor hibrida.
  4. **Eksplorasi Presisi Tipe Data dan Variasi Kernel:** Disarankan meneliti pengaruh variasi presisi tipe data (misalnya `float32` versus `uint8`) terhadap durasi transfer serialisasi memori IPC, serta menguji matriks kernel berdimensi lebih besar ($5 \times 5, 7 \times 7$) dan variasi tekstur citra masukan.
  5. **Pengukuran Terisolasi Per Tahap Pipa Paralel:** Disarankan memasang stempel waktu terpisah pada setiap tahapan pipa pemrosesan paralel (waktu partisi matriks, waktu transfer serialisasi IPC, durasi komputasi kernel murni di worker, dan waktu rekonstruksi `np.vstack()`) guna memisahkan dan membedah komponen *overhead* komunikasi secara langsung.

---

### BAGIAN AKHIR (BACK MATTER)
* **DAFTAR PUSTAKA:**
  * Berdiri sendiri sejajar BAB (style `Heading Non-Nomor`, tanpa nomor bab, masuk Daftar Isi otomatis).
  * Memuat 13 referensi terverifikasi format APA 7th (Aesthetic-4K, Amdahl, Chang, Cremel & Arruda, Gonzalez & Woods, Gultom & Sarumaha, Ibrahim, Karp & Flatt, Pacheco & Malensek, Python Software Foundation n.d.-a, Python Software Foundation n.d.-b, Tanenbaum & Bos, Vasile et al.).
* **LAMPIRAN (Berdiri Sendiri, Label Huruf A s.d. E):**
  * **Lampiran A:** Data Mentah Hasil Pengujian Benchmark (Tabel 810 Baris × 15 Kolom).
  * **Lampiran B:** Tabel Ringkasan Metrik Kinerja Lengkap (49 Kolom × 27 Kondisi Uji).
  * **Lampiran C:** Kode Program Implementasi Engine Pemrosesan Citra Paralel (`src/filters.py`, `src/parallel_engine.py`, `src/serial_engine.py`).
  * **Lampiran D:** Kode Program Skrip Pengujian Otomatis dan Visualisasi Data (`run_benchmark.py`, `src/visualizer.py`).
  * **Lampiran E:** Log Spesifikasi Lingkungan Perangkat Keras dan Perangkat Lunak.

---

Dokumen panduan komprehensif ini menjadi acuan mutlak selama proses penyusunan isi naskah Laporan Akhir agar seluruh pembahasan mengalir logis, berbasis data empiris, dan bebas dari sanggahan ilmiah.
