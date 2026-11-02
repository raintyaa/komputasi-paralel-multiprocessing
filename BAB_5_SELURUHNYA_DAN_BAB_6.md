
# IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN


## Implementasi Sistem Pemrosesan Citra Paralel


**Subbab ini menguraikan realisasi kode program dari perancangan arsitektur pemrosesan paralel yang telah dirancang pada Bab 4. Implementasi sistem dikonstruksi ke dalam tiga berkas modul utama: manajemen tugas konkurensi (src/parallel_engine.py), operasi pemfilteran spasial (src/filter.py), serta validasi eksekusi dan telemetri (run_benchmark.py). Cuplikan kode pada bagian ini menampilkan fungsi-fungsi inti, sedangkan keseluruhan kode sumber sistem didokumentasikan pada Lampiran C dan D.**


### Mesin Konkurensi Paralel (src/parallel_engine.py)

Mesin paralel merupakan inti arsitektur sistem yang bertugas mendekomposisi matriks citra skala besar menjadi submatriks tugas independen agar dapat dieksekusi secara serentak (konkuren) pada multi-inti prosesor. Dekomposisi dilakukan menggunakan teknik partisi baris horizontal (domain decomposition) dengan penambahan lapisan batas (boundary halo) selebar radius kernel agar kalkulasi konvolusi di tepi submatriks memperoleh data piksel tetangga yang lengkap.


**Kode Program 5.1 Fungsi Partisi Baris dan Penambahan Boundary Halo**

```python
def create_horizontal_partitions(
    image: np.ndarray, num_workers: int, filter_func: Callable, kernel_radius: int = 1
) -> List[Tuple[np.ndarray, Callable, int, int]]:
    height = image.shape[0]
    chunk_height = height // num_workers
    tasks = []
 
    for i in range(num_workers):
        start_y = i * chunk_height
        end_y = (i + 1) * chunk_height if i < num_workers - 1 else height
 
        # Tentukan baris boundary halo (k = 1 untuk filter spasial 3x3)
        halo_top = kernel_radius if (i > 0 and kernel_radius > 0) else 0
        halo_bottom = kernel_radius if (i < num_workers - 1 and kernel_radius > 0) else 0
 
        # Ekstraksi submatriks baris dengan penambahan baris halo fisik
        sub_chunk = image[start_y - halo_top : end_y + halo_bottom]
        tasks.append((sub_chunk, filter_func, halo_top, halo_bottom))
 
    return tasks
```

Fungsi create_horizontal_partitions membagi matriks citra secara vertikal berdasarkan jumlah proses pekerja yang dialokasikan. Untuk filter spasial berukuran 3×3 dengan radius kernel satu piksel (k = 1), fungsi mengekstrak satu baris piksel ekstra dari segmen tetangganya sebagai boundary halo atas dan bawah, kecuali pada batas terluar citra asli. Submatriks beserta informasi koordinat pemotongan batas kemudian dipaketkan ke dalam daftar tupel penugasan (tasks).

Setelah struktur tugas terpartisi, kolam pekerja (worker pool) mendistribusikan data melalui komunikasi antar-proses (inter-process communication/IPC), mengeksekusi fungsi filter secara independen pada setiap proses pekerja, memangkas kembali baris halo tambahan (halo stripping), lalu merekonstruksi citra utuh.


**Kode Program 5.2 Eksekusi Tugas pada Kolam Pekerja dan Rekonstruksi Citra**

```python
def _worker_filter_task(task_args: Tuple[np.ndarray, Callable, int, int]) -> np.ndarray:
    sub_image_with_halo, filter_func, halo_top, halo_bottom = task_args
 
    # 1. Eksekusi filter spasial pada submatriks ber-halo secara lokal
    filtered_block = filter_func(sub_image_with_halo)
 
    # 2. Pangkas baris batas tambahan (halo stripping) sebelum data dikembalikan
    h = filtered_block.shape[0]
    end_idx = h - halo_bottom if halo_bottom > 0 else h
    trimmed_result = filtered_block[halo_top:end_idx]
 
    return trimmed_result
 
# Pada proses utama: distribusi tugas via IPC dan rekonstruksi vertikal
with multiprocessing.Pool(processes=p_processes) as pool:
    processed_chunks = pool.map(_worker_filter_task, tasks)
reconstructed_image = np.vstack(processed_chunks)
```

Tugas komputasi dieksekusi secara terisolasi oleh fungsi _worker_filter_task pada proses pekerja masing-masing. Pascapemfilteran, indeks pemangkasan (halo stripping) diterapkan guna membuang area batas (overlap) di sisi atas dan bawah blok matriks sebelum luaran dikembalikan ke proses utama melalui mekanisme antrean IPC. Pada proses utama, pustaka multiprocessing.Pool memetakan seluruh tugas, dan luaran dari setiap segmen digabungkan kembali secara terurut menjadi satu matriks utuh menggunakan np.vstack().


### Modul Filter Spasial  (src/filter.py)

Modul filter spasial bertanggung jawab atas operasi matematis tingkat piksel untuk mengaplikasikan transformasi visual pada citra. Pemfilteran dilakukan melalui konvolusi matriks kernel diskret terhadap matriks citra, sebagaimana diimplementasikan pada filter Gaussian Blur dan deteksi tepi Sobel L2.


**Kode Program 5.3 Implementasi Konvolusi Filter Spasial (Gaussian Blur dan Sobel L2)**

```python
# --- Realisasi Konvolusi Gaussian Blur 3x3 ---
padded = np.pad(image.astype(np.float64), ((1,1), (1,1), (0,0)), mode="edge")
kernel_gauss = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float64) / 16.0
blur_result = np.zeros_like(image, dtype=np.float64)
 
for i in range(3):
    for j in range(3):
        blur_result += kernel_gauss[i, j] * padded[i:i + H, j:j + W]
output_blur = np.clip(blur_result, 0, 255).astype(np.uint8)
 
# --- Realisasi Magnitudo Gradien Sobel L2 ---
# (Setelah konvolusi kernel gx dan gy pada citra derajat keabuan)
magnitude = np.sqrt(gx**2 + gy**2)
output_sobel = np.clip(magnitude, 0, 255).astype(np.uint8)
```

Pada algoritma Gaussian Blur 3×3, batas citra diberikan bantalan (padding) bermode edge guna mencegah artefak pada batas visual. Operasi konvolusi diimplementasikan melalui pergeseran jendela matriks 3×3 yang dibobotkan dengan nilai kernel Gaussian terdistribusi. Pada implementasi filter Sobel, magnitudo gradien diekstraksi menggunakan formulasi Euclidean (L2) dengan menghitung akar jumlahan kuadrat dari gradien sumbu mendatar (Gx) dan tegak (Gy), sebelum nilainya dipotong (clip) pada rentang [0, 255] dan dikonversi ke tipe data uint8.


### Orkestrator Pengujian dan Telemetri (run_benchmark.py)

Guna memverifikasi determinisme dan keabsahan kalkulasi dalam eksekusi paralel, modul telemetri menyediakan fungsi validasi otomatis yang mengomparasikan luaran eksekusi serial baseline terhadap luaran yang dihasilkan oleh kolam pekerja paralel.


**Kode Program 5.4 Fungsi Validasi Integritas Luaran Citra Bit-Identik**

```python
def validate_results(serial_result: np.ndarray, parallel_result: np.ndarray) -> tuple[bool, float]:
    # Tahap 1: Verifikasi keselarasan dimensi geometris matriks
    if serial_result.shape != parallel_result.shape:
        return False, -1.0
 
    # Tahap 2: Evaluasi deterministik kesetaraan bit piksel
    is_identical = np.array_equal(serial_result, parallel_result)
 
    # Kalkulasi disparitas absolut maksimum pada presisi float64 (bebas wraparound)
    serial_f64 = serial_result.astype(np.float64)
    parallel_f64 = parallel_result.astype(np.float64)
    max_diff = float(np.max(np.abs(serial_f64 - parallel_f64)))
 
    return is_identical, max_diff
```

Fungsi validate_results beroperasi melalui dua tahapan evaluasi. Pertama, verifikasi keselarasan dimensi geometris memastikan matriks luaran serial dan paralel memiliki resolusi yang identik. Kedua, fungsi np.array_equal menguji kesetaraan deterministik seluruh bit piksel matriks. Disparitas absolut maksimum (Δmax) turut dihitung menggunakan presisi float64 untuk mencegah galat pelimpahan (wraparound error) pada format integer, sehingga anomali nilai piksel sekecil apa pun dapat terdeteksi secara dini.


## Validasi Integritas Data dan Keterulangan Pengujian

Tahapan validasi integritas data dan evaluasi keterulangan pengujian dilakukan sebelum menganalisis metrik percepatan dan efisiensi sistem. Pengujian ini bertujuan untuk memverifikasi keabsahan matematis dari luaran pemrosesan paralel serta mengukur stabilitas lingkungan eksekusi komputasi.


### Evaluasi Integritas Luaran Citra Bit-Identik

Berdasarkan fungsi validasi telemetri yang telah diimplementasikan, seluruh 810 pasangan pengujian pada ketiga skenario eksperimen menghasilkan nilai disparitas absolut maksimum Δmax = 0, yang secara programatis menghasilkan status is_identical = True. Hasil ini menegaskan bahwa partisi baris, penambahan boundary halo, dan pemangkasan batas (halo stripping) berhasil mencegah degradasi informasi piksel maupun timbulnya cacat garis sambungan (seam artifact) pada area pertemuan submatriks. Ringkasan hasil validasi integritas bit-identik disajikan pada Tabel 5.1.


**Tabel 5.1 Ringkasan Hasil Validasi Integritas Bit-Identik pada Seluruh Skenario Pengujian**


| Skenario Pengujian | Algoritma Filter | Parameter Uji | Pasangan Uji | Rasio Bit-Identik | Δmax | Status Keabsahan |
| --- | --- | --- | --- | --- | --- | --- |
| Skenario A (Variasi Resolusi) | Grayscale, Gaussian, Sobel | 512–4096 px (P = 4) | 360 | 360 / 360 (100%) | 0 | Valid |
| Skenario B (Variasi Pekerja) | Grayscale, Gaussian, Sobel | P ∈ {1, 2, 4, 8} (2048 px) | 360 | 360 / 360 (100%) | 0 | Valid |
| Skenario C (Variasi Kompleksitas) | Grayscale, Gaussian, Sobel | 2048 px (P = 4) | 90 | 90 / 90 (100%) | 0 | Valid |
| Total Kumulatif | Tiga Algoritma Filter | Seluruh Skenario (27 Kondisi) | 810 | 810 / 810 (100%) | 0 | Valid (100%) |



*Keterangan: Seluruh evaluasi menggunakan fungsi np.array_equal() dan disparitas absolut dihitung pada presisi float64.*


### Evaluasi Kontrol Dasar A/A (P = 1) dan Batas Derau Sistem

Guna mengukur batasan derau pada ekosistem komputasi (noise floor), pengujian kontrol dasar A/A dilakukan dengan mengomparasikan eksekusi serial baseline terhadap eksekusi pada kolam pekerja dengan alokasi pekerja tunggal (P = 1) melalui 90 pasangan iterasi pada resolusi 2048 × 2048 piksel (kondisi B1, B5, dan B9). Hasil pengujian dirangkum pada Tabel 5.2. Nilai speedup rerata berada di sekitar 1,00×, yaitu 1,06× [CI 95%: 0,97–1,15] untuk Grayscale, 1,02× [CI 95%: 0,98–1,05] untuk Gaussian Blur, dan 1,00× [CI 95%: 0,95–1,05] untuk Sobel. Selang kepercayaan 95% dari ketiga filter seluruhnya mencakup nilai teoretis 1,00×. Rata-rata speedup agregat tercatat sebesar 1,03× dengan deviasi derau sistem di bawah 3%, dan nilai overhead mendekati nol (−0,0082 detik hingga +0,0054 detik). Stabilitas ini menegaskan bahwa peningkatan kinerja yang teramati pada alokasi multi-pekerja (P > 1) merefleksikan pengaruh nyata dari konkurensi pemrosesan paralel, bukan fluktuasi derau latar belakang sistem operasi.


**Tabel 5.2 Ringkasan Metrik Pengujian Kontrol Dasar A/A (Resolusi 2048 × 2048 Piksel; P = 1; N = 30 Iterasi per Filter)**


| Kode | Filter | Ts Rerata ± Std (s) | Tp Rerata ± Std (s) | S Median [Q25–Q75] | S Rerata [CI 95%] | Overhead Rerata (s) | Status Integritas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Grayscale | 0,1333 ± 0,0200 | 0,1303 ± 0,0273 | 1,05 [0,92–1,21] | 1,06 [0,97–1,15] | −0,0030 | Valid (100%) |
| B5 | Gaussian Blur | 0,6688 ± 0,0553 | 0,6606 ± 0,0715 | 1,01 [0,96–1,09] | 1,02 [0,98–1,05] | −0,0082 | Valid (100%) |
| B9 | Sobel | 0,5743 ± 0,0482 | 0,5797 ± 0,0582 | 1,00 [0,94–1,06] | 1,00 [0,95–1,05] | +0,0054 | Valid (100%) |
| Agregat | Semua Filter | — | — | 1,02 [0,94–1,12] | 1,03 [0,97–1,08] | −0,0019 | Valid (100%) |



*Keterangan: N = 30 iterasi per kondisi (total 90 iterasi kontrol A/A); alokasi P = 1 berfungsi sebagai verifikasi batas derau (noise floor) sistem komputasi.*


### Evaluasi Keterulangan Antar-Blok Pengujian (Repeatability Drift)

Evaluasi keterulangan antar-blok (repeatability drift) dianalisis dengan mengomparasikan sel perlakuan identik pada resolusi 2048 × 2048 piksel dengan konfigurasi pekerja P = 4 yang direplikasi melintasi tiga blok sekuens pengujian, yaitu Blok A (kondisi A3, A7, A11), Blok B (B3, B7, B11), dan Blok C (C1, C2, C3). Hasil observasi menunjukkan adanya variasi waktu eksekusi baseline serial pada Blok A yang tercatat sekitar 20% hingga 28% lebih lambat dibandingkan Blok B dan Blok C. Sebagai contoh, durasi serial Sobel tercatat 0,73 detik pada Blok A, 0,61 detik pada Blok B, dan 0,58 detik pada Blok C. Variasi ini diklasifikasikan sebagai limitasi pergeseran sistematis (systematic drift limitation), yang dipengaruhi oleh dinamika termal dan governor daya perangkat sebelum mencapai saturasi termal stabil. Oleh karena itu, komparasi speedup antar-kondisi difokuskan pada perbandingan di dalam blok yang sama, sementara analisis lintas-blok ditafsirkan secara cermat sesuai batasan metodologis.


## Hasil Pengujian Sistem dan Analisis Kinerja

Bagian ini menyajikan hasil pengujian pada seluruh 27 sel kondisi perlakuan dari tiga skenario eksperimen. Setiap kondisi diuji sebanyak 30 repetisi berselang-seling (810 pasangan eksekusi) dan seluruh pasangan lulus verifikasi bit-identik dengan Δmax = 0 (Subbab 5.2.1). Hasil dilaporkan dalam bentuk median beserta rentang antarkuartil [Q25–Q75], rerata, dan selang kepercayaan (confidence interval, CI) 95% berdasarkan distribusi t-Student dengan df = 29. Efisiensi paralel (E) dan beban tambahan (overhead) hanya dihitung untuk P > 1 sesuai definisi operasional pada Tabel 3.4.


### Skenario A: Pengaruh Skalabilitas Resolusi Matriks Citra

Skenario A menguji pengaruh variasi resolusi matriks citra dari 512 × 512 hingga 4096 × 4096 piksel pada alokasi tetap empat proses pekerja (P = 4) untuk ketiga filter, sehingga terbentuk 12 kondisi uji (A1–A12). Setiap kondisi memiliki 30 repetisi. Metrik kinerja dirangkum pada Tabel 5.3 dan kurva speedup terhadap resolusi ditampilkan pada Gambar 5.1.

Hubungan antara resolusi dan speedup tidak monoton. Speedup rerata tertinggi diraih Sobel pada resolusi 512 × 512 piksel, yaitu 3,89× (median 4,04×; CI 95% 3,58–4,20), setara efisiensi 97,3% dan mendekati batas ideal S = P = 4. Nilai rerata tersebut turun menjadi 2,30× pada 1024 piksel dan 2,21× pada 2048 piksel, lalu meningkat kembali menjadi 2,85× pada 4096 piksel. Gaussian Blur menunjukkan rerata 2,52×, 2,12×, 2,38×, dan 2,46× pada empat resolusi berurutan. Sementara itu, Grayscale berada pada kisaran 1,68× hingga 2,10× tanpa tren yang konsisten.


**Tabel 5.3 Metrik Kinerja Skenario A (P = 4; 12 Kondisi Uji)**


| Kode | Filter | Resolusi (px) | S Median [Q25–Q75] | S Rerata | CI 95% S | E (%) | Overhead (detik) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | Grayscale | 512 | 1,52 [1,23–1,92] | 1,68 | 1,35–2,02 | 42,1 | 0,0081 |
| A2 | Grayscale | 1024 | 2,06 [1,89–2,30] | 2,10 | 1,97–2,22 | 52,4 | 0,0085 |
| A3 | Grayscale | 2048 | 1,95 [1,67–2,15] | 1,91 | 1,75–2,07 | 47,7 | 0,0448 |
| A4 | Grayscale | 4096 | 2,12 [1,88–2,32] | 2,08 | 1,94–2,23 | 52,1 | 0,1450 |
| A5 | Gaussian Blur | 512 | 2,50 [2,35–2,65] | 2,52 | 2,39–2,64 | 63,0 | 0,0068 |
| A6 | Gaussian Blur | 1024 | 1,92 [1,66–2,58] | 2,12 | 1,89–2,35 | 53,0 | 0,0562 |
| A7 | Gaussian Blur | 2048 | 2,33 [1,85–2,71] | 2,38 | 2,14–2,62 | 59,5 | 0,1610 |
| A8 | Gaussian Blur | 4096 | 2,40 [2,30–2,67] | 2,46 | 2,32–2,59 | 61,4 | 0,5108 |
| A9 | Sobel | 512 | 4,04 [3,23–4,57] | 3,89 | 3,58–4,20 | 97,3 | 0,0013 |
| A10 | Sobel | 1024 | 2,26 [1,86–2,64] | 2,30 | 2,07–2,52 | 57,4 | 0,0419 |
| A11 | Sobel | 2048 | 2,08 [1,83–2,50] | 2,21 | 2,00–2,41 | 55,1 | 0,1564 |
| A12 | Sobel | 4096 | 2,82 [2,60–3,14] | 2,85 | 2,69–3,01 | 71,3 | 0,2824 |



*Keterangan: S = speedup; CI 95% rerata dihitung dengan distribusi t-Student (n = 30); E = efisiensi paralel; overhead = rerata T_overhead (Persamaan 2.4).*

Beban tambahan absolut umumnya meningkat seiring volume data yang harus diserialisasi dan dikirim antar-proses, meskipun besar kenaikannya berbeda antar-filter. Overhead rerata Sobel naik dari 0,0013 detik pada 512 piksel menjadi 0,2824 detik pada 4096 piksel, sedangkan Gaussian Blur naik dari 0,0068 detik menjadi 0,5108 detik. Pada rentang resolusi yang sama, efisiensi Sobel turun dari 97,3% menjadi 71,3%; Gaussian Blur relatif tetap (63,0% dan 61,4%); sedangkan Grayscale meningkat dari 42,1% menjadi 52,1%. Dengan demikian, efisiensi tidak selalu menurun ketika resolusi meningkat. Temuan ini konsisten dengan adanya pengaruh biaya transfer memori dan IPC pada resolusi besar, tetapi pola nonmonoton menunjukkan bahwa pengaruhnya juga bergantung pada karakteristik filter dan kondisi eksekusi.

Perlu dicatat bahwa baseline serial Skenario A pada sejumlah kondisi tercatat lebih lambat daripada Skenario B dan C (batasan metodologis pada Bab 3), sehingga perbandingan nilai speedup antar-blok perlu ditafsirkan dengan hati-hati; kajian keterulangan antar-blok disajikan pada Subbab 5.2.3.


*[Gambar disematkan di dokumen docx]*


*Gambar 5.1. Kurva Speedup terhadap Variasi Resolusi Matriks Citra (P = 4; Titik = Rerata, Batang Galat = CI 95%)*


### Skenario B: Pengaruh Skalabilitas Alokasi Proses Kerja (Worker)

Skenario B menguji pengaruh jumlah proses pekerja P ∈ {1, 2, 4, 8} pada resolusi tetap 2048 × 2048 piksel untuk ketiga filter (12 kondisi uji, B1–B12), masing-masing dengan 30 repetisi. Alokasi P = 1 berfungsi sebagai kontrol A/A sehingga speedup rerata berada di sekitar 1 (Grayscale 1,06×; Gaussian Blur 1,02×; Sobel 1,00×). Alokasi P = 2, 4, dan 8 dianalisis untuk mengevaluasi skalabilitas paralel. Metrik seluruh kondisi disajikan pada Tabel 5.4.

Penambahan proses pekerja meningkatkan speedup rerata pada ketiga filter. Pada P = 2, 4, dan 8, rerata S masing-masing mencapai 1,46×, 1,90×, dan 2,62× untuk Grayscale; 1,60×, 2,34×, dan 2,99× untuk Gaussian Blur; serta 1,77×, 2,74×, dan 3,09× untuk Sobel. Namun, efisiensi menurun seiring penambahan pekerja: pada P = 8 efisiensi rerata sebesar 32,8% (Grayscale), 37,4% (Gaussian Blur), dan 38,6% (Sobel), dibandingkan 73,2%, 80,1%, dan 88,3% pada P = 2.


**Tabel 5.4 Metrik Kinerja Skenario B (2048 × 2048 Piksel; 12 Kondisi Uji)**


| Kode | Filter | P | S Median [Q25–Q75] | S Rerata | CI 95% S | E (%) | Overhead (detik) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 | Grayscale | 1 | 1,05 [0,92–1,21] | 1,06 | 0,97–1,15 | – | – |
| B2 | Grayscale | 2 | 1,39 [1,32–1,53] | 1,46 | 1,36–1,57 | 73,2 | 0,0261 |
| B3 | Grayscale | 4 | 1,98 [1,62–2,09] | 1,90 | 1,74–2,06 | 47,5 | 0,0460 |
| B4 | Grayscale | 8 | 2,55 [2,22–2,90] | 2,62 | 2,43–2,82 | 32,8 | 0,0365 |
| B5 | Gaussian Blur | 1 | 1,01 [0,96–1,09] | 1,02 | 0,98–1,05 | – | – |
| B6 | Gaussian Blur | 2 | 1,60 [1,39–1,78] | 1,60 | 1,51–1,70 | 80,1 | 0,0881 |
| B7 | Gaussian Blur | 4 | 2,31 [2,04–2,69] | 2,34 | 2,16–2,53 | 58,6 | 0,1424 |
| B8 | Gaussian Blur | 8 | 2,90 [2,61–3,32] | 2,99 | 2,80–3,18 | 37,4 | 0,1492 |
| B9 | Sobel | 1 | 1,00 [0,94–1,06] | 1,00 | 0,95–1,05 | – | – |
| B10 | Sobel | 2 | 1,76 [1,62–1,80] | 1,77 | 1,66–1,87 | 88,3 | 0,0482 |
| B11 | Sobel | 4 | 2,87 [2,60–3,06] | 2,74 | 2,56–2,92 | 68,5 | 0,0771 |
| B12 | Sobel | 8 | 2,88 [2,55–3,62] | 3,09 | 2,81–3,36 | 38,6 | 0,1271 |



*Keterangan: P = 1 adalah kontrol A/A sehingga E dan overhead tidak dihitung (–). Simbol dan metode statistik sama dengan Tabel 5.3.*

Uji Kruskal–Wallis menunjukkan perbedaan speedup yang signifikan antar-alokasi P = 2, 4, dan 8 pada ketiga filter (Grayscale: H = 52,56; p < 0,001; Gaussian Blur: H = 59,14; p < 0,001; Sobel: H = 49,82; p < 0,001). Uji lanjut Mann–Whitney U dengan koreksi Holm–Bonferroni menunjukkan bahwa peningkatan dari P = 4 ke P = 8 signifikan pada Grayscale (p < 0,001; estimasi Hodges–Lehmann +0,69) dan Gaussian Blur (p < 0,001; +0,59), tetapi tidak signifikan pada Sobel (p = 0,149; +0,27). Pada Sobel, median speedup hanya berubah dari 2,87× pada P = 4 menjadi 2,88× pada P = 8, sehingga hasil ini menunjukkan indikasi saturasi pada rentang tersebut.


*Gambar 5.2 membandingkan kurva empiris dengan batas Hukum Amdahl yang diestimasi pada Subbab 5.4.1. Pada alokasi paralel P = 2, 4, dan 8, titik empiris berada di bawah garis ideal S = P. Pada P = 1, nilai speedup berfungsi sebagai kontrol A/A dan berada di sekitar 1,00; nilai Grayscale (1,06×) dan Gaussian Blur (1,02×) yang sedikit melampaui garis ideal merupakan variasi pengukuran kontrol, bukan percepatan paralel. Pola pada P > 1 menjadi dasar diagnostik beban koordinasi pada Subbab 5.4.2.*


*[Gambar disematkan di dokumen docx]*


*Gambar 5.2. Evaluasi Skalabilitas Jumlah Proses Pekerja terhadap Batas Hukum Amdahl (2048 × 2048 Piksel)*


### Skenario C: Pengaruh Variasi Kompleksitas Algoritma Filter

Skenario C membandingkan ketiga filter pada kondisi yang sama, yaitu resolusi 2048 × 2048 piksel dan P = 4 (kondisi C1–C3), masing-masing dengan 30 repetisi. Ringkasan metrik disajikan pada Tabel 5.5 dan visualisasinya pada Gambar 5.3.


**Tabel 5.5 Perbandingan Kinerja Tiga Filter pada Skenario C (2048 × 2048 Piksel; P = 4)**


| Kode | Filter | S Median [Q25–Q75] | S Rerata | CI 95% S | E (%) | Overhead (detik) | CPU (%) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | Grayscale | 2,11 [1,93–2,27] | 2,05 | 1,94–2,16 | 51,2 | 0,0337 | 30,6 |
| C2 | Gaussian Blur | 2,50 [2,22–2,70] | 2,44 | 2,27–2,61 | 61,0 | 0,1129 | 44,2 |
| C3 | Sobel | 2,68 [2,37–2,88] | 2,59 | 2,42–2,76 | 64,8 | 0,0849 | 43,3 |



*Keterangan: CPU = rerata utilisasi CPU sistem selama jendela komputasi; simbol lain sama dengan Tabel 5.3.*

Filter konvolusi menghasilkan percepatan rerata lebih tinggi dibandingkan operasi titik. Rerata speedup Sobel dan Gaussian Blur masing-masing sebesar 2,59× dan 2,44×, sedangkan Grayscale sebesar 2,05×. Uji Kruskal–Wallis menunjukkan perbedaan speedup yang signifikan antar-filter (H = 26,22; p < 0,001). Uji lanjut Mann–Whitney U dengan koreksi Holm–Bonferroni menunjukkan bahwa Sobel dan Gaussian Blur masing-masing lebih tinggi daripada Grayscale (estimasi Hodges–Lehmann +0,57 dan +0,39; keduanya p < 0,001), sedangkan perbedaan Sobel dan Gaussian Blur tidak signifikan (p = 0,145). Efisiensi rerata masing-masing sebesar 64,8% (Sobel), 61,0% (Gaussian Blur), dan 51,2% (Grayscale).

Perbedaan ini sejalan dengan rasio antara waktu komputasi dan waktu komunikasi IPC. Median waktu serial Gaussian Blur (0,6335 detik) dan Sobel (0,5777 detik) masing-masing sekitar 4,7 dan 4,3 kali median Grayscale (0,1344 detik), sehingga biaya serialisasi dan transmisi antar-proses lebih teramortisasi pada beban komputasi yang lebih besar. Overhead rerata berbeda signifikan antar-filter (Kruskal–Wallis H = 52,58; p < 0,001), yaitu 0,1129 detik pada Gaussian Blur, 0,0849 detik pada Sobel, dan 0,0337 detik pada Grayscale. Jika dibandingkan dengan rerata waktu paralel, overhead tersebut setara sekitar 40,8% (Gaussian Blur), 36,9% (Sobel), dan 49,9% (Grayscale). Utilisasi CPU rerata juga berbeda signifikan (H = 32,22; p < 0,001): Grayscale 30,6%, Gaussian Blur 44,2%, dan Sobel 43,3%. Hasil ini menunjukkan bahwa beban komputasi, biaya komunikasi, dan pemanfaatan CPU berbeda menurut karakteristik filter.


*[Gambar disematkan di dokumen docx]*


*Gambar 5.3. Perbandingan Durasi Overhead Komunikasi dan Sinkronisasi serta Rata-rata Utilisasi CPU pada Ketiga Filter (2048 × 2048 Piksel; P = 4)*


## Pencocokan Model Teoritis Skalabilitas

Pencocokan model teoretis dilakukan terhadap data empiris Skenario B pada P = 2, 4, dan 8 dengan memakai rerata speedup setiap kondisi (Tabel 5.4); kondisi P = 1 dikeluarkan karena berfungsi sebagai kontrol A/A. Fraksi paralel efektif f pada Persamaan (2.5) diestimasi dengan regresi non-linier kuadrat terkecil (least-squares fitting), dengan batas 0 ≤ f ≤ 1 untuk setiap filter. Selang kepercayaan 95% diperoleh melalui bootstrap 2.000 ulangan dengan pengambilan ulang 30 repetisi pada masing-masing nilai P. Fraksi serial eksperimental e dihitung menggunakan Persamaan (2.6).


### Estimasi Parameter Fraksi Paralel Hukum Amdahl

Pencocokan kurva menghasilkan fraksi paralel efektif f = 0,69 untuk Grayscale, f = 0,76 untuk Gaussian Blur, dan f = 0,79 untuk Sobel (Tabel 5.6). Batas percepatan asimtotik S_maks = 1/(1 − f) berturut-turut adalah 3,21×, 4,19×, dan 4,77×. Selang kepercayaan bootstrap 95% masing-masing adalah 0,66–0,72; 0,74–0,78; dan 0,77–0,81. Hasil ini menunjukkan bahwa satu nilai f tunggal tidak dapat digeneralisasi untuk seluruh beban kerja pengolahan citra. Karena Hukum Amdahl memperlakukan seluruh biaya koordinasi sebagai bagian serial, f pada penelitian ini merupakan fraksi paralel efektif, bukan fraksi kode paralel murni.


**Tabel 5.6 Estimasi Parameter Fraksi Paralel (f) dan Evaluasi Goodness-of-Fit (R2)**


| Filter | Fraksi paralel f | CI 95% bootstrap f | Smaks = 1/(1 − f) | R2 | RMSE S |
| --- | --- | --- | --- | --- | --- |
| Grayscale | 0,69 | 0,66–0,72 | 3,21 | 0,936 | 0,121 |
| Gaussian Blur | 0,76 | 0,74–0,78 | 4,19 | 1,000 | 0,011 |
| Sobel | 0,79 | 0,77–0,81 | 4,77 | 0,876 | 0,197 |



*Keterangan: pencocokan memakai tiga titik data (P = 2, 4, 8) dengan satu parameter bebas; RMSE dalam satuan speedup.*

Kualitas pencocokan berbeda antar-filter. Gaussian Blur paling dekat dengan kurva Amdahl (R² = 1,000; RMSE = 0,011), sedangkan Grayscale (R² = 0,936; RMSE = 0,121) dan Sobel (R² = 0,876; RMSE = 0,197) menunjukkan penyimpangan lebih besar. Karena pencocokan hanya menggunakan tiga titik data (P = 2, 4, 8) dengan satu parameter bebas, nilai R² harus ditafsirkan sebagai ukuran kecocokan deskriptif, bukan validasi statistik yang kuat. Pada Sobel, model meremehkan speedup pada P = 2 dan P = 4, tetapi melebihkannya pada P = 8, yang menunjukkan bahwa kurva empiris mulai menjenuh lebih cepat daripada prediksi model. Sebaliknya, pada Grayscale speedup terukur pada P = 8 melampaui prediksi model.


### Diagnostik Beban Koordinasi Berdasarkan Metrik Karp-Flatt

Fraksi serial eksperimental e dihitung pada P = 2, 4, dan 8 dari rerata speedup Skenario B, disertai selang kepercayaan 95% bootstrap 2.000 ulangan. Hasilnya disajikan pada Tabel 5.7.


**Tabel 5.7 Nilai Metrik Karp–Flatt (e) terhadap Alokasi Proses Pekerja**


| Filter | e pada P = 2 | e pada P = 4 | e pada P = 8 | Pola e terhadap P |
| --- | --- | --- | --- | --- |
| Grayscale | 0,37[0,27–0,46] | 0,37[0,31–0,43] | 0,29[0,26–0,32] | Relatif  konstan; cenderung menurun pada P = 8 |
| Gaussian Blur | 0,25[0,18–0,32] | 0,24[0,20–0,28] | 0,24[0,22–0,26] | Relatif konstan |
| Sobel | 0,13[0,07–0,20] | 0,15[0,13–0,19] | 0,23[0,20–0,26] | Meningkat |



*Keterangan: nilai dalam kurung siku adalah CI 95% bootstrap (2.000 ulangan).*

Nilai e pada Sobel meningkat seiring penambahan proses, yaitu sekitar 0,13 pada P = 2, 0,15 pada P = 4, dan 0,23 pada P = 8. CI 95% pada P = 8 (0,20–0,26) tidak beririsan dengan P = 4 (0,13–0,19), yang mengindikasikan pembengkakan beban koordinasi paralel ketika jumlah pekerja bertambah. Dengan demikian, pembatas skalabilitas Sobel kemungkinan tidak hanya berasal dari bagian sekuensial kode, tetapi juga dari biaya koordinasi dan serialisasi IPC. Interpretasi ini bersifat indikatif karena metrik Karp–Flatt tidak memisahkan fraksi sekuensial inheren dari biaya komunikasi.

Gaussian Blur memperlihatkan e yang relatif konstan (sekitar 0,25; 0,24; 0,24), konsisten dengan model fraksi serial yang relatif tetap. Pada Grayscale, e sekitar 0,37; 0,37; dan 0,29. Penurunan pada P = 8 sejalan dengan speedup terukur yang melampaui prediksi Amdahl, tetapi CI antar-alokasi masih beririsan sehingga pola tersebut belum dapat dinyatakan sebagai perbedaan yang tegas. Secara keseluruhan, ketiga filter menunjukkan pola e yang berbeda: meningkat pada Sobel, relatif konstan pada Gaussian Blur, dan cenderung menurun pada Grayscale.


## Pembahasan Temuan dan Keterbatasan Penelitian

Subbab ini membahas temuan empiris dari Skenario A, B, dan C berdasarkan prinsip arsitektur komputasi, karakteristik perangkat keras, serta perbandingannya terhadap literatur terdahulu.


### Dinamika Resolusi Citra dan Hipotesis Pengaruh Hierarki Cache L2 dan L3

Pada pengujian Skenario A, filter Sobel pada resolusi 512 × 512 piksel dengan alokasi empat proses pekerja (P = 4) mencatatkan rasio percepatan yang mendekati batas linier ideal (S ≈ P), dengan median speedup sebesar 4,04× dan rerata 3,89× (deviasi standar 0,84; interval kepercayaan 95% [3,58; 4,20]). Efisiensi komputasi median tercatat sebesar 101,02% (rerata 97,26%). Sebanyak 16 dari 30 repetisi pengujian menghasilkan nilai overhead negatif tipis dengan median −0,0002 detik (mendekati nol). Pada resolusi yang sama, Gaussian Blur memperoleh median speedup 2,50× (rerata 2,52×), sedangkan Grayscale memperoleh median speedup 1,52× (rerata 1,68×).

Tingginya rasio percepatan filter Sobel pada dimensi 512 × 512 piksel konsisten dengan hipotesis interaksi ukuran data terhadap hierarki memori cache prosesor Intel Core i5-13420H. Prosesor ini dilengkapi 12 MB L3 Intel Smart Cache yang digunakan bersama dan 1,25 MB L2 cache privat pada setiap Performance-Core (P-Core).

Citra RGB 512 × 512 piksel berukuran total sekitar 768 KB (atau 262 KB dalam format monokrom satu kanal). Ukuran data tersebut beserta lapisan batas halo padding (k = 1) termuat utuh ke dalam 12 MB L3 cache bersama, baik pada eksekusi serial maupun paralel. Pembeda kinerja antara eksekusi serial dan paralel pada konfigurasi ini didorong oleh distribusi beban ke dalam hierarki L2 cache privat masing-masing inti.

Ketika citra dipartisi ke empat pekerja, setiap pekerja memproses irisan submatriks berukuran 130 × 512 piksel (termasuk boundary halo) dengan ukuran data masukan sekitar 195 KB. Partisi data masukan yang ringkas ini beserta larik perantara gradien konvolusi berpeluang besar tertampung pada 1,25 MB L2 cache privat masing-masing P-Core, sehingga mengurangi frekuensi akses ke memori utama DRAM.

Selain itu, eksekusi paralel empat pekerja mendistribusikan lalu lintas data ke empat jalur L2 cache privat. Pembagian ini mengurangi terjadinya kegagalan kapasitas (capacity misses) dan kontensi antrean bus memori yang dihadapi eksekusi serial satu inti saat mengolah keseluruhan larik citra secara berulang.

Karakteristik luaran filter Sobel juga berperan penting. Filter Sobel menghasilkan luaran monokromatik satu kanal berukuran ringkas (sekitar 262 KB pada 512 × 512 piksel), berbeda dari Gaussian Blur yang harus mengembalikan luaran tiga kanal warna penuh (sekitar 786 KB). Muatan transmisi IPC yang lebih kecil pada filter Sobel membuat biaya komunikasi antar-proses tetap rendah pada resolusi kecil, sehingga akselerasi komputasi dapat tercapai optimal.

Pola percepatan mendekati linier pada resolusi 512 × 512 piksel tidak teramati pada operasi Grayscale maupun Gaussian Blur. Pada Grayscale, intensitas aritmatika berada pada tingkat 1,25 FLOP/bita dan durasi pemrosesan serial berlangsung singkat (median 0,0203 detik). Pada durasi tersebut, latensi tetap pipa komunikasi antar-proses (pembuatan pipa IPC, serialisasi, dan deserialisasi pickle) yang berkisar 0,008 detik mendominasi perbandingan, sehingga speedup tertahan pada angka 1,52× (rerata 1,68×). Pada Gaussian Blur, intensitas komputasi yang mencapai 8,50 FLOP/bita terhambat oleh volume data luaran tiga kanal RGB yang harus dialirkan kembali melalui pipa IPC — tiga kali lipat lebih besar dibandingkan Sobel (satu kanal). Beban transmisi IPC yang besar ini menekan efisiensi paralel Gaussian Blur pada angka 2,50× (rerata 2,52×).

Seiring peningkatan dimensi citra masukan, rasio percepatan filter Sobel memperlihatkan penurunan dari resolusi 512 × 512 piksel ke 1024 × 1024 piksel (median speedup turun dari 4,04× ke 2,26×; rerata 2,30×). Pada dimensi 1024 × 1024 piksel, ukuran partisi data per pekerja melampaui kapasitas L2 cache privat 1,25 MB sehingga memicu capacity misses, disertai pembengkakan volume transmisi data IPC. Pada resolusi yang lebih tinggi (2048 × 2048 hingga 4096 × 4096 piksel), percepatan filter Sobel terdistribusi pada kisaran 2,08× hingga 2,87×.

Evaluasi lintas skenario menunjukkan bahwa nilai percepatan pada sel 2048 × 2048 piksel (P = 4) bervariasi antar-blok pengujian: median speedup bernilai 2,08× (rerata 2,21×) pada Skenario A, 2,87× (rerata 2,74×) pada Skenario B, dan 2,68× (rerata 2,59×) pada Skenario C. Variasi ini mencerminkan pengaruh pergeseran keterulangan (repeatability drift) akibat perbedaan suhu awal prosesor antar-skenario. Sementara itu, pada resolusi 4096 × 4096 piksel (Skenario A), percepatan tercatat sebesar 2,82× (rerata 2,85×) dengan efisiensi 70,59%. Keuntungan utama pemrosesan paralel pada resolusi 4096 × 4096 piksel terletak pada penghematan waktu absolut, yaitu mereduksi durasi eksekusi dari 2,62 detik (serial) menjadi 0,94 detik (paralel), dengan proporsi overhead terhadap waktu serial menurun dari sekitar 21% pada resolusi 2048 piksel menjadi 10,6% pada resolusi 4096 piksel.

Penjelasan mengenai pengaruh hierarki memori cache terhadap rasio percepatan ini berstatus sebagai hipotesis ilmiah yang konsisten dengan data empiris, bukan bukti pengukuran instrumentasi langsung. Pengujian ini tidak mengukur tingkat kegagalan cache (cache miss rate) secara langsung melalui hardware performance counters (seperti Intel VTune atau Linux perf) dan tidak menerapkan penguncian afinitas inti (core affinity pinning) guna mengontrol penempatan proses pekerja. Keterbatasan metodologis ini dicatat pada Subbab 5.5.5.


### Karakteristik Skalabilitas Worker, Arsitektur Hibrida, dan Diminishing Returns

Pengujian Skenario B mengevaluasi perilaku penskalaan kuat (strong scaling) sistem ketika alokasi proses pekerja ditingkatkan secara bertahap (P ∈ {1, 2, 4, 8}) pada dimensi citra konstan 2048 × 2048 piksel. Data empiris memperlihatkan penurunan efisiensi marjinal (diminishing returns) pada seluruh algoritma filter, dengan titik saturasi teramati pada filter Sobel ketika alokasi ditingkatkan dari empat ke delapan proses pekerja.

1. Titik Plato pada Filter Sobel di P = 8

Pada filter Sobel, penambahan pekerja dari P = 2 ke P = 4 menghasilkan peningkatan percepatan: median waktu eksekusi berkurang dari 0,3477 detik menjadi 0,2087 detik, meningkatkan median speedup dari 1,76× ke 2,87× (rerata 2,74×) dengan efisiensi 71,84%.

Ketika alokasi pekerja ditingkatkan dari P = 4 ke P = 8, peningkatan percepatan terhenti. Median waktu eksekusi paralel hanya bergeser sebesar 0,0026 detik (dari 0,2087 detik menjadi 0,2061 detik), dan median speedup hanya berubah dari 2,8738× ke 2,8783× (perbedaan marjinal +0,0045× yang tidak signifikan secara statistik, p = 0,15 pada uji Mann–Whitney). Di sisi lain, efisiensi komputasi menurun dari 71,84% menjadi 35,98%, sementara median durasi overhead sistem meningkat dari 0,0596 detik menjadi 0,1320 detik (kenaikan bersih +0,0724 detik). Persentase utilisasi CPU global sistem meningkat dari 39,94% ke 70,49%, mencerminkan peningkatan aktivitas komputasi latar belakang tanpa memberikan reduksi waktu pemrosesan yang sebanding.

Perilaku ini menunjukkan deviasi terhadap model teoretis Hukum Amdahl. Menggunakan estimasi fraksi paralel f = 0,79 pada filter Sobel, model Hukum Amdahl memproyeksikan rasio percepatan teoretis sebesar 3,24× pada P = 8. Capaian empiris rata-rata berada pada angka 2,88× (defisit 0,36× terhadap batas teoretis), mengindikasikan adanya faktor penghambat koordinasi pada alokasi pekerja tinggi.

2. Hipotesis Pengaruh Arsitektur Prosesor Hibrida (P-Core dan E-Core)

Salah satu penjelasan potensial mengenai munculnya titik plato pada P = 8 berkaitan dengan karakteristik mikroarsitektur prosesor Intel Core i5-13420H. Prosesor ini memiliki delapan inti fisik heterogen yang terbagi menjadi dua kluster: empat Performance-Cores (P-Cores, arsitektur Golden Cove) dengan frekuensi turbo hingga 4,6 GHz dan L2 cache privat 1,25 MB per inti, serta empat Efficient-Cores (E-Cores, arsitektur Gracemont) dengan frekuensi turbo maksimum 3,4 GHz, kapasitas instruksi per siklus (IPC) lebih rendah, dan berbagi pakai 2 MB L2 cache per kluster.

Pada alokasi P = 2 dan P = 4, beban kerja proses pekerja kemungkinan besar diprioritaskan oleh penjadwal sistem operasi dan Intel Thread Director pada kluster P-Core yang berkinerja lebih tinggi, sehingga proses pekerja mengeksekusi komputasi dengan laju yang relatif seimbang.

Pada alokasi P = 8, sistem melibatkan seluruh delapan inti fisik yang tersedia, memadukan 4 P-Core dan 4 E-Core secara bersamaan. Skema partisi pada sistem ini menerapkan dekomposisi spasial statis (static row partitioning), membagi matriks citra 2048 baris secara seragam menjadi delapan blok yang masing-masing memuat 256 baris piksel (ditambah baris batas halo).

Pembagian beban kerja statis seragam pada prosesor heterogen berpotensi memicu ketimpangan waktu penyelesaian (load imbalance). Pekerja yang dialokasikan pada P-Core (frekuensi hingga 4,6 GHz) menyelesaikan pemrosesan blok lebih cepat dibandingkan pekerja yang berjalan pada E-Core (frekuensi 3,4 GHz). Karena pemanggilan multiprocessing.Pool.map() menerapkan pembatas sinkronisasi (synchronous barrier), proses utama harus menunggu hingga pekerja pada E-Core menyelesaikan tugasnya sebelum dapat menjalankan rekonstruksi numpy.vstack(). Waktu tunggu ini berpotensi membatasi penambahan percepatan pada P = 8.

3. Karakteristik Efisiensi dan Evaluasi Metrik Karp–Flatt

Penurunan efisiensi paralel seiring bertambahnya alokasi pekerja teramati pada ketiga jenis filter. Pada Grayscale, efisiensi menurun dari 69,33% (P = 2) menjadi 49,38% (P = 4) dan 31,88% (P = 8). Pada Gaussian Blur, efisiensi menurun dari 80,27% (P = 2) menjadi 57,73% (P = 4) dan 36,20% (P = 8). Pada Sobel, efisiensi menurun dari 87,88% (P = 2) menjadi 71,84% (P = 4) dan 35,98% (P = 8). Pada P = 8, efisiensi ketiga filter berada pada rentang 32% hingga 36%.

Evaluasi menggunakan metrik fraksi serial eksperimental Karp–Flatt (e) memperlihatkan perbedaan perilaku antar-filter. Pada filter Sobel, nilai e berbasis rerata bernilai 0,1292 (P = 2), 0,1535 (P = 4), dan meningkat menjadi 0,2272 pada P = 8 (berbasis median: 0,1379 pada P = 2, 0,1306 pada P = 4, dan 0,2542 pada P = 8). Sebaliknya, pada Gaussian Blur, nilai e relatif stabil pada kisaran 0,2474 (P = 2), 0,2499 (P = 4), dan 0,2520 (P = 8). Pada Grayscale, nilai e justru mengalami penurunan dari 0,4376 (P = 2) menjadi 0,3662 (P = 4) dan 0,3168 (P = 8).

Karakteristik metrik Karp–Flatt tersebut menunjukkan bahwa peningkatan fraksi serial efektif pada P = 8 hanya teramati secara nyata pada filter Sobel. Perbedaan respons antar-filter ini mengindikasikan bahwa hambatan pada P = 8 tidak semata disebabkan oleh heterogenitas inti fisik, melainkan merupakan interaksi antara waktu komputasi lokal, alokasi larik perantara, dan biaya transmisi data antar-proses.


### Karakteristik Beban Tambahan (Overhead) Serialisasi IPC dan Utilisasi CPU

Pengujian Skenario C dirancang untuk menganalisis beban koordinasi internal sistem pada kondisi resolusi 2048 × 2048 piksel dan alokasi pekerja tetap (P = 4) dengan memvariasikan karakteristik algoritma: konversi Grayscale (operasi titik), penghalusan Gaussian Blur 3 × 3 (konvolusi spasial tiga kanal), dan deteksi tepi Sobel 3 × 3 (konvolusi gradien ganda). Evaluasi berfokus pada dua parameter: durasi beban tambahan paralel (T_overhead) dan persentase utilisasi prosesor.

1. Karakteristik Beban Tambahan Komunikasi IPC dan Alokasi Memori

Berdasarkan data empiris Skenario C sebagaimana disajikan pada Gambar 5.3(a), durasi beban tambahan paralel (T_overhead) menunjukkan perbedaan antar-filter. Grayscale mencatatkan median overhead terendah sebesar 0,0294 detik (rerata 0,0337 ± 0,0138 detik, interval kepercayaan 95% [0,0286; 0,0389] detik). Gaussian Blur mencatatkan median overhead tertinggi sebesar 0,0924 detik (rerata 0,1129 ± 0,0563 detik, interval kepercayaan 95% [0,0919; 0,1339] detik). Sobel menghasilkan median overhead moderat sebesar 0,0695 detik (rerata 0,0849 ± 0,0445 detik, interval kepercayaan 95% [0,0683; 0,1015] detik).

Durasi overhead Gaussian Blur lebih tinggi dibandingkan Sobel meskipun Sobel memiliki tahapan kalkulasi gradien horizontal dan vertikal. Pada modul multiprocessing, parameter T_overhead mencakup latensi pengaliran pipa antar-proses (IPC pipe latency), serialisasi dan deserialisasi objek larik NumPy (pickle), alokasi memori larik lokal pada pekerja, serta rekonsiliasi akhir melalui numpy.vstack().

Perbedaan durasi overhead tersebut sejalan dengan volume muatan data (payload size) yang ditransmisikan. Pada filter Gaussian Blur, setiap pekerja menerima irisan masukan berukuran (512 + 2) × 2048 × 3 bita (sekitar 3,16 MB) dan mengembalikan matriks luaran tiga kanal berukuran 512 × 2048 × 3 bita (sekitar 3,15 MB), sehingga total volume luaran yang diserialisasi oleh keempat pekerja via pickle dan digabungkan kembali oleh proses utama mencapai 12,58 MB. Pada filter Sobel, konversi ke derajat keabuan dilakukan di dalam memori pekerja sebelum perhitungan gradien, sehingga luaran akhir berupa matriks monokromatik satu kanal berukuran 512 × 2048 × 1 bita (sekitar 1,05 MB) dengan total volume luaran kembalian sebesar 4,19 MB — sepertiga dari volume keluaran Gaussian Blur. Pada filter Grayscale, ketiadaan penambahan lapisan batas (k = 0) dan ringkasnya matriks kembalian (total 4,19 MB) menghasilkan nilai overhead terendah pada angka 0,0294 detik.

Meskipun demikian, perbedaan durasi overhead antara Sobel (0,0695 detik) dan Grayscale (0,0294 detik) pada volume luaran kembalian yang sama (4,19 MB) menunjukkan bahwa T_overhead tidak semata merefleksikan transmisi IPC murni, melainkan juga memuat alokasi memori larik perantara float64 dan waktu komputasi tambahan di tingkat pekerja.

2. Karakteristik dan Batasan Interpretasi Utilisasi CPU

Pengukuran beban prosesor melalui modul psutil pada Gambar 5.3(b) memperlihatkan perbedaan pola utilisasi. Grayscale menghasilkan rerata utilisasi CPU sistem sebesar 30,57% (median 28,18%, rentang interkuartil [23,15% – 35,72%]). Gaussian Blur menghasilkan rerata 44,17% (median 44,17%, rentang interkuartil [38,41% – 48,68%]). Sobel menghasilkan rerata 43,34% (median 40,11%, rentang interkuartil [37,03% – 48,16%]).

Angka utilisasi CPU yang dilaporkan oleh pustaka psutil berstatus sebagai tren indikatif kasar agregat sistem, bukan pengukuran deterministik per proses pekerja. Hal ini disebabkan oleh mekanisme pemantauan psutil yang mengambil percontohan berkala beban CPU global sistem pada interval waktu diskret 20 milidetik, tanpa memisahkan kontribusi spesifik masing-masing sub-proses pekerja multiprocessing.

Pada Grayscale, durasi eksekusi paralel murni (T_paralel) hanya berlangsung selama 0,0620 detik (62 milidetik). Melalui interval percontohan kelas CPUMonitor sebesar 20 milidetik, pemantau hanya sempat mengambil sekitar 3 titik sampel. Akibatnya, estimasi utilisasi lebih rentan terhadap fluktuasi transien sistem. Sebaliknya, durasi komputasi paralel Gaussian Blur (0,2532 detik) dan Sobel (0,2110 detik) berlangsung lebih panjang sehingga tertangkap oleh sekitar 10 hingga 13 siklus percontohan psutil, menghasilkan nilai utilisasi sistem yang stabil di kisaran 40% hingga 44%.

Nilai utilisasi sistem 40% hingga 44% diinterpretasikan dalam konteks kapasitas total prosesor Intel Core i5-13420H yang mengekspos 12 utas logis ke sistem operasi Windows 11 (4 P-Cores dengan Hyper-Threading = 8 utas logis, ditambah 4 E-Cores tanpa Hyper-Threading = 4 utas logis). Beban empat proses pekerja secara teoretis menyumbang setidaknya 4/12 × 100% = 33,33% dari kapasitas total utas logis sistem.

Capaian utilisasi aktual sebesar 40% hingga 44% mengindikasikan adanya pemanfaatan komputasi multi-inti yang aktif selama fase paralel berlangsung, dengan sisa persentase utilisasi di atas 33,33% merepresentasikan aktivitas proses sistem operasi dan thread pemantau latar belakang.


### Komparasi Temuan terhadap Penelitian Terdahulu

Hasil pengujian dikomparasikan terhadap literatur rujukan utama yang telah dipetakan pada Bab 2, mencakup kajian komputasi paralel berbasis memori bersama OpenMP, akselerasi GPU, serta model konkurensi CPython.

1. Komparasi terhadap Model Konkurensi Python (Gultom dan Sarumaha, 2025)

Gultom dan Sarumaha (2025) menguji efektivitas modul multithreading dan multiprocessing CPython pada beban komputasi numerik berulang hingga 120 juta iterasi. Penelitian tersebut menunjukkan bahwa batasan Global Interpreter Lock (GIL) menyebabkan multithreading hanya menghasilkan percepatan marjinal sekitar 1,05×, sedangkan multiprocessing menghasilkan speedup 3,16× hingga 3,55× pada alokasi empat proses pekerja.

Rasio percepatan pada penelitian ini pada empat pekerja (resolusi 2048 × 2048 piksel) berada pada kisaran 1,90× hingga 2,74×, lebih rendah dibandingkan capaian Gultom dan Sarumaha. Perbedaan ini kemungkinan besar bersumber dari perbedaan karakteristik beban kerja dan platform pengujian. Beban kerja Gultom dan Sarumaha berupa kalkulasi skalar numerik dengan volume data komunikasi yang sangat kecil. Sebaliknya, penelitian ini memproses matriks citra berukuran jutaan piksel, saat setiap pekerja harus menerima dan mengembalikan larik data berukuran megabita melalui saluran pipa IPC. Serialisasi objek NumPy via pickle dan penggabungan akhir via numpy.vstack() menyita waktu terukur yang membatasi percepatan pada pengolahan citra digital.

2. Komparasi terhadap Model Memori Bersama OpenMP (Cremel dan Arruda, 2026)

Cremel dan Arruda (2026) mengevaluasi akselerasi filter spasial citra termasuk deteksi tepi menggunakan pustaka OpenMP berbasis bahasa C/C++ pada CPU multi-core. Model berbasis utas OpenMP beroperasi pada satu ruang alamat memori bersama sehingga tidak memerlukan serialisasi objek. Meskipun demikian, Cremel dan Arruda melaporkan bahwa efisiensi paralel OpenMP pada deteksi tepi mengalami penurunan pada alokasi delapan utas (efisiensi sekitar 24%) akibat keterbatasan lebar pita memori (memory bandwidth bottleneck).

Hasil pengujian Skenario B pada penelitian ini memperlihatkan kecenderungan penurunan efisiensi yang sejalan pada alokasi delapan pekerja (P = 8), dengan efisiensi Sobel turun menjadi 35,98% dan Gaussian Blur menjadi 36,20%. Penurunan efisiensi pada sistem ini dipengaruhi oleh kombinasi faktor heterogenitas frekuensi clock P-Core dan E-Core, transmisi pipa IPC, serta perebutan lebar pita bus memori utama.

Terdapat perbedaan pola skalabilitas resolusi antara penelitian ini dan temuan Cremel dan Arruda. Cremel dan Arruda melaporkan bahwa rasio percepatan meningkat seiring kenaikan resolusi citra secara monoton. Sebaliknya, pada penelitian ini, rasio percepatan tertinggi filter Sobel tercapai pada resolusi kecil (512 × 512 piksel) akibat partisi kerja tertampung pada memori cache L2 privat, sebelum kemudian menurun dan mendatar pada resolusi 1024 hingga 4096 piksel.

3. Komparasi terhadap Akselerasi GPU (Chang et al., 2023)

Chang et al. (2023) melaporkan penerapan operator Sobel pada GPU NVIDIA berbasis CUDA dengan capaian percepatan 6,7× hingga 13,0× terhadap pustaka OpenCV-GPU standar. Di sisi lain, literatur komputasi paralel GPU (Ibrahim et al., 2021; Vasile et al., 2024) mencatat bahwa akselerasi GPU memiliki beban tambahan transfer data antara memori host (RAM) dan memori perangkat grafis (VRAM) melalui bus PCIe.

Perilaku transfer data tersebut memperlihatkan kesamaan konseptual dengan beban transmisi pipa IPC pada CPU multiprocessing dalam penelitian ini. Pada citra berdimensi kecil, durasi overhead transmisi menyita proporsi yang cukup terasa terhadap total waktu eksekusi. Keuntungan praktis pemrosesan paralel CPU terlihat pada citra beresolusi tinggi (4096 × 4096 piksel), dengan reduksi waktu eksekusi Sobel dari 2,62 detik (serial) menjadi 0,94 detik (paralel).

Perlu dicatat bahwa perbandingan nilai percepatan antara penelitian ini (2,85× pada 4096 piksel dan 4,04× pada 512 piksel) dan hasil Chang et al. (6,7× hingga 13,0×) tidak berada pada dasar pembanding yang setara, karena penelitian ini menggunakan baseline serial CPU NumPy sedangkan Chang et al. menggunakan baseline pustaka OpenCV-GPU. Pendekatan multiprocessing CPU Python murni menawarkan keunggulan berupa ketiadaan ketergantungan pada perangkat keras GPU diskret dan driver berpemilik (proprietary), sehingga lebih mudah diimplementasikan pada lingkungan komputasi berdaya rendah.

Sintesis perbandingan posisi temuan penelitian ini terhadap penelitian terdahulu dirangkum pada Tabel 5.8.


**Tabel 5.8 Komparasi Temuan Penelitian terhadap Literatur Terdahulu**


| Aspek Komparasi | Chang et al. (2023) | Cremel dan Arruda (2026) | Gultom dan Sarumaha (2025) | Penelitian Ini |
| --- | --- | --- | --- | --- |
| Platform dan Paradigma | GPU NVIDIA CUDA (warp primitives) | CPU multi-core via OpenMP (C/C++ threads) | CPU multi-core via Python multiprocessing | CPU multi-core heterogen via Python multiprocessing |
| Beban dan Skala Data | Operator Sobel 5 × 5 pada citra standar | Multiresolusi citra (Blur, Edge, Denoise) | Iterasi numerik skalar (20M–120M iterasi) | Tiga filter bertingkat pada resolusi 512–4096 px |
| Capaian Percepatan | Speedup 6,7× hingga 13,0× vs OpenCV-GPU | Speedup tumbuh seiring resolusi | Speedup 3,16×–3,55× pada 4 proses | Speedup 2,21×–2,85× (4096 px) hingga 4,04× (512 px) pada 4 worker |
| Perilaku Efisiensi pada Alokasi Tinggi | Tidak dievaluasi untuk skala multi-core CPU | Efisiensi Sobel anjlok ke ~24% pada 8 utas | Tidak mengevaluasi alokasi di atas 4 proses | Efisiensi Sobel turun ke 35,98% pada 8 worker (efek E-Core dan IPC) |
| Faktor Pembatas Utama | Latensi akses memori global GPU | Keterbatasan lebar pita memori DRAM | Global Interpreter Lock (GIL) pada CPython | Serialisasi IPC pipa OS, kontensi DRAM, dan heterogenitas inti |
| Verifikasi Integritas | Evaluasi visual kualitatif | Pengukuran waktu komputasi | Validasi numerik nilai akumulator | Uji biner bit-identik 100% deterministik (Δ_max = 0) |



### Sintesis Jawaban Rumusan Masalah dan Keterbatasan Penelitian

Subbab ini menyajikan sintesis jawaban atas rumusan masalah penelitian, diikuti oleh identifikasi keterbatasan metodologis dan eksperimental.

1. Sintesis Jawaban Rumusan Masalah

Jawaban Rumusan Masalah 1: Pengaruh Resolusi Citra terhadap Speedup dan Efisiensi

Peningkatan resolusi citra masukan menghasilkan respons skalabilitas yang dipengaruhi oleh ukuran partisi kerja dan volume transmisi data IPC. Pada filter Sobel (P = 4), percepatan mendekati batas linier ideal pada dimensi 512 × 512 piksel (median 4,04×, rerata 3,89×, efisiensi median 101,02%) sejalan dengan hipotesis partisi data tertampung di dalam L2 cache privat P-Core (1,25 MB). Percepatan menurun pada resolusi 1024 × 1024 piksel (median 2,26×) seiring terjadinya capacity misses pada L2 cache dan peningkatan volume IPC, kemudian berada pada rentang 2,08× hingga 2,87× pada resolusi 2048 dan 4096 piksel dengan reduksi waktu absolut terbesar terjadi pada resolusi 4096 piksel (dari 2,62 detik menjadi 0,94 detik). Pada konversi Grayscale, percepatan terdistribusi datar pada rentang 1,52× hingga 2,12× di seluruh resolusi karena karakteristik operasi terikat memori (memory-bound) dengan batasan transfer memori DRAM DDR5.

Pada filter Gaussian Blur, intensitas komputasi yang lebih tinggi (8,50 FLOP/bita) menghasilkan speedup yang moderat (median 2,50× pada 512 piksel hingga 2,31× pada 2048 piksel) karena beban pengaliran matriks luaran tiga kanal RGB (12,58 MB pada citra 2048 piksel) menyita porsi waktu transmisi IPC yang signifikan.

Jawaban Rumusan Masalah 2: Pola Skalabilitas Alokasi Worker terhadap Batas Teoretis Hukum Amdahl

Peningkatan alokasi proses pekerja (P ∈ {1, 2, 4, 8}) pada resolusi 2048 × 2048 piksel memperlihatkan pola penurunan efisiensi marjinal. Alokasi pekerja hingga P = 4 menghasilkan peningkatan speedup yang stabil (Sobel meningkat dari 1,00× pada P = 1 menjadi 1,76× pada P = 2, dan 2,87× pada P = 4 dengan efisiensi 71,84%). Namun, penambahan alokasi ke P = 8 menghasilkan titik plato pada filter Sobel (speedup median 2,88×, perbedaan marjinal +0,0045× yang tidak signifikan secara statistik, p = 0,15), dengan efisiensi turun menjadi 35,98% dan berada di bawah proyeksi Hukum Amdahl teoretis (3,24× pada f = 0,79).

Kenaikan metrik fraksi serial Karp–Flatt (e) dari 0,1306 (P = 4) ke 0,2542 (P = 8) teramati secara spesifik pada filter Sobel, mengindikasikan adanya beban koordinasi tambahan pada P = 8 yang konsisten dengan hipotesis ketimpangan waktu eksekusi antara P-Core dan E-Core serta pembengkakan waktu transmisi pipa IPC.

Jawaban Rumusan Masalah 3: Pengaruh Kompleksitas Filter terhadap Overhead IPC dan Utilisasi CPU

Pengujian Skenario C menunjukkan bahwa durasi beban tambahan (T_overhead) sejalan dengan volume muatan data keluaran yang diserialisasi melalui pipa IPC. Gaussian Blur mencatatkan overhead tertinggi (median 0,0924 detik) karena mentransmisikan luaran tiga kanal RGB (12,58 MB). Sobel menghasilkan overhead moderat (median 0,0695 detik) karena luaran tereduksi menjadi satu kanal monokrom (4,19 MB), dan Grayscale menghasilkan overhead terendah (0,0294 detik) karena ketiadaan operasi boundary halo (k = 0). Perbedaan overhead antara Sobel dan Grayscale pada volume luaran yang sama mengindikasikan bahwa T_overhead juga memuat alokasi memori larik perantara lokal pada pekerja.

Pengukuran beban prosesor menggunakan psutil pada P = 4 berada pada kisaran 40%–44% dari total 12 utas logis sistem, mengindikasikan aktivitas multi-inti yang aktif selama fase eksekusi paralel. Pada Grayscale, utilisasi terukur lebih rendah (median 28,18%) akibat durasi komputasi yang sangat singkat (62 milidetik) dibandingkan interval percontohan psutil 20 milidetik.

Jawaban Rumusan Masalah 4: Integritas Luaran Citra Bit-Identik

Integritas luaran citra paralel terjaga secara deterministik melalui penerapan mekanisme boundary halo selebar k = 1 piksel dengan metode replikasi batas (edge replication padding, mode='edge') pada setiap submatriks partisi, diikuti oleh pemangkasan baris batas (halo stripping) sebelum rekonstruksi utuh via numpy.vstack().

Validasi biner terhadap 720 pasangan komparasi non-trivial (serial-paralel) dan 90 pasangan kontrol trivial A/A (total 810 iterasi) menunjukkan status kesetaraan elemen matriks numpy.array_equal() = True sebesar 100% dengan nilai disparitas absolut maksimum piksel bernilai nol (Δ_max = 0) pada seluruh citra uji, mengonfirmasi bahwa pembagian baris horizontal dan pertukaran batas spasial tidak menimbulkan distorsi sambungan atau pergeseran indeks.

2. Keterbatasan Penelitian

Penelitian ini memiliki beberapa keterbatasan metodologis dan eksperimental yang perlu dicatat:

Pertama, pengujian dieksekusi secara sekuensial antar-skenario (diawali Skenario A, dilanjutkan B, dan diakhiri C) tanpa pengacakan blok global (no global randomized block design). Ketiadaan pengacakan urutan ini memicu fenomena pergeseran keterulangan (repeatability drift) yang terlihat dari perbedaan baseline waktu serial Skenario A terhadap B dan C pada konfigurasi identik (citra 2048 × 2048 piksel, P = 4). Selain itu, urutan eksekusi selalu mendahulukan serial sebelum paralel pada setiap repetisi.

Kedua, eksperimen menggunakan satu citra acuan master tunggal yang dipotong secara pemotongan tengah murni (center-crop) ke berbagai dimensi (512 × 512 hingga 4096 × 4096 piksel) tanpa proses resampling atau interpolasi. Pendekatan ini menjaga konsistensi visual antarsampel, namun belum mengevaluasi konten citra dengan karakteristik frekuensi spasial dan entropi yang bervariasi.

Ketiga, evaluasi kinerja dijalankan pada satu unit perangkat keras laptop dengan prosesor Intel Core i5-13420H (arsitektur hibrida 4 P-Core + 4 E-Core, 12 utas logis, RAM 16 GB DDR5). Karakteristik skalabilitas yang teramati sangat dipengaruhi oleh konfigurasi perangkat keras ini dan belum divalidasi silang pada arsitektur prosesor homogen (seperti AMD Ryzen) maupun prosesor tingkat peladen.

Keempat, sistem telemetri pengujian tidak merekam sensor suhu silikon (°C) dan frekuensi clock aktual prosesor (GHz) secara kontinu ke dalam berkas data log. Mitigasi termal bertumpu pada suhu ruangan (~24 °C) dan jeda pendinginan selama 0,5 detik (cool-down buffer), sehingga fluktuasi termal mikro tidak tercatat secara numerik per iterasi.

Kelima, sistem tidak menerapkan penguncian afinitas proses pekerja ke inti fisik tertentu (psutil.Process().cpu_affinity()). Penempatan proses dikelola oleh penjadwal Windows 11 dan Intel Thread Director, sehingga migrasi proses antar-inti dapat memengaruhi variansi latensi.

Keenam, analisis mengenai kontribusi memori cache L2 dan L3 terhadap percepatan pada resolusi 512 × 512 piksel berstatus sebagai hipotesis ilmiah berbasis analisis ukuran partisi kerja (working set analysis), bukan hasil pencatatan langsung dari unit pencacah kinerja perangkat keras (hardware performance counters).

Ketujuh, pengujian difokuskan pada filter spasial independen (embarrassingly parallel) dengan kernel lokal 3 × 3. Karakteristik ini tidak dapat digeneralisasi langsung pada operasi citra non-lokal atau konvolusi kernel berukuran besar (7 × 7 ke atas).


# PENUTUP


## Kesimpulan

Berdasarkan serangkaian pengujian sebanyak 810 iterasi (mencakup 720 pasangan komparasi non-trivial serial-paralel dan 90 pasangan kontrol A/A) pada prosesor Intel Core i5-13420H, diperoleh empat kesimpulan pokok:

Pada filter Sobel (P = 4), percepatan mendekati batas linier pada resolusi 512 × 512 piksel (median 4,04×, rerata 3,89× [CI 95%: 3,58; 4,20]) dan terdistribusi pada kisaran 2,2× hingga 2,9× pada resolusi 1024 hingga 4096 piksel. Perbedaan hasil antar-blok pengujian pada resolusi 2048 piksel (2,21× pada Blok A, 2,74× pada Blok B, dan 2,59× pada Blok C) menunjukkan bahwa variasi keterulangan termal memengaruhi capaian percepatan. Percepatan pada 512 piksel konsisten dengan hipotesis bahwa partisi per pekerja tertampung di dalam cache L2 privat, meskipun tidak diukur melalui instrumentasi langsung. Pada konversi Grayscale, median percepatan berada pada rentang 1,52× hingga 2,12× di seluruh resolusi.

Pada dimensi citra konstan 2048 × 2048 piksel, percepatan filter Sobel meningkat dari 1,76× (P = 2) ke 2,87× (P = 4), dan tidak berbeda secara signifikan antara P = 4 dan P = 8 (p = 0,15 pada uji Mann–Whitney), sementara efisiensi menurun dari 71,84% ke 35,98%. Pola data konsisten dengan estimasi model Hukum Amdahl pada fraksi paralel efektif f = 0,69 hingga 0,79 sesuai jenis filter. Kenaikan metrik fraksi serial Karp–Flatt teramati secara nyata pada filter Sobel (dari 0,1306 ke 0,2542), saat heterogenitas inti P-Core dan E-Core serta pembengkakan koordinasi IPC menjadi penjelasan yang konsisten dengan data.

Durasi beban tambahan (overhead) pada P = 4 dan resolusi 2048 × 2048 piksel berurutan: Gaussian Blur (median 0,0924 detik) > Sobel (0,0695 detik) > Grayscale (0,0294 detik). Urutan ini sejalan dengan volume muatan luaran kembalian (12,58 MB pada Gaussian Blur vs 4,19 MB pada Sobel dan Grayscale) serta alokasi memori larik perantara lokal pada pekerja. Sementara itu, persentase utilisasi CPU global psutil berada pada kisaran 40%–44% yang merefleksikan aktivitas komputasi multi-inti pada prosesor.

Penerapan dekomposisi domain spasial horizontal dengan mekanisme boundary halo padding selebar k = 1 piksel bermetode replikasi tepi (edge replication, mode='edge') dan pemangkasan batas (halo stripping) menjaga integritas rekonstruksi citra secara konsisten. Seluruh 720 pasangan pengujian serial-paralel dan 90 pasangan kontrol A/A menghasilkan kesetaraan matriks biner deterministik numpy.array_equal() = True sebesar 100% dengan disparitas absolut maksimum nol (Δ_max = 0) pada seluruh citra uji.


## Saran

Berdasarkan temuan empiris dan analisis keterbatasan yang diperoleh, diajukan beberapa saran untuk penelitian lanjutan:

Mengevaluasi skema pembagian beban dinamis (dynamic chunk scheduling atau work-stealing pool) dengan mengalokasikan porsi baris lebih banyak dibandingkan jumlah pekerja guna mengurangi potensi waktu tunggu sinkronisasi pada prosesor berarsitektur heterogen (P-Core dan E-Core).

Mengurangi beban tambahan serialisasi data antar-proses dengan memanfaatkan arsitektur memori bersama (shared memory via multiprocessing.shared_memory) atau pemetaan berkas ke memori (memory-mapped files, mmap) agar proses utama dan pekerja dapat berbagi akses larik citra tanpa penalti waktu serialisasi pickle.

Menerapkan mekanisme penguncian afinitas proses pekerja ke inti fisik prosesor (core affinity pinning via psutil.Process().cpu_affinity()) dengan memilih satu utas per P-Core setelah memeriksa topologi prosesor guna meminimalkan migrasi proses antar-inti (thread hopping).

Menyempurnakan protokol eksperimen dengan mengintegrasikan pencatatan telemetri suhu silikon (°C) dan frekuensi aktual prosesor (GHz) secara kontinu, menerapkan pengacakan urutan blok pengujian (randomized block design) guna mengurangi bias termal awal, serta memanfaatkan hardware performance counters untuk mengukur laju cache misses secara empiris.

Memperluas evaluasi komparatif ke akselerasi komputasi berbasis unit pengolah grafis (GPU) menggunakan pustaka seperti CuPy atau PyTorch CUDA, serta vektorisasi instruksi SIMD (AVX2) pada CPU untuk memetakan titik impas performa pada citra beresolusi sangat tinggi.

DAFTAR PUSTAKA

LAMPIRAN


## Lampiran A: Data Mentah Hasil Pengujian Benchmark (810 Iterasi)


## Lampiran B: Tabel Ringkasan Metrik Kinerja Lengkap (49 Kolom × 27 Kondisi)


## Lampiran C: Kode Program Implementasi Engine Komputasi Paralel


## Lampiran D: Kode Program Skrip Pengujian Otomatis dan Visualisasi Data


## Lampiran E: Log Spesifikasi Lingkungan Perangkat Keras dan Perangkat Lunak
