# PANDUAN AUDIT PROPOSAL PENELITIAN UNTUK CLAUDE (DENGAN SKILL HUMANIZER)

## 📌 INSTRUKSI UNTUK CLAUDE:
> "Halo Claude, tolong bertindak sebagai **Senior Academic Editor dan Peer Reviewer** untuk bidang Rekayasa Sistem Komputer, FMIPA Universitas Tanjungpura (UNTAN). Aktifkan kapabilitas skill **`humanizer`**.
>
> Dokumen di bawah ini adalah naskah lengkap proposal penelitian tugas akhir berjudul:
> **'Analisis Kinerja dan Skalabilitas pada Operasi Filter Citra Digital Menggunakan Komputasi Paralel Berbasis Multiprocessing'**.
>
> **Konteks Dokumen & Status Bab:**
> 1. **FOKUS UTAMA AUDIT KALI INI:**
>    - **POIN 8 (DESKRIPSI PENELITIAN & PENULISAN PERSAMAAN)**
>    - Periksa deskripsi alur sistem pemrosesan paralel (Row-Major Order, dekomposisi horizontal, worker pool, np.vstack).
>    - Periksa Diagram Blok Arsitektur Sistem (Gambar 1).
>    - **Periksa keabsahan dan akurasi 5 Persamaan Matematis:**
>      * Persamaan (1): Konvolusi Spasial 2D (Vasile et al., 2024).
>      * Persamaan (2): Rasio Percepatan / Speedup (Pacheco & Malensek, 2022).
>      * Persamaan (3): Efisiensi Paralel (Pacheco & Malensek, 2022).
>      * Persamaan (4): Beban Tambahan / Overhead Paralel (Pacheco & Malensek, 2022; Gultom & Sarumaha, 2025).
>      * Persamaan (5): Batas Skalabilitas Hukum Amdahl (Pacheco & Malensek, 2022).
>    - Pastikan notasi dan variabel pada keterangan persamaan selaras dengan Tabel 4 Parameter Kinerja di Poin 9.3.
> 2. **POIN 10 (DAFTAR PUSTAKA):** Memuat 5 referensi terbitan 5 tahun terakhir (3 jurnal + 2 buku teks). Pastikan seluruh sitasi di Poin 8 selaras 100% dengan entri Daftar Pustaka.
> 3. Poin 1 s.d. 7 dan Poin 9 sebelumnya sudah selesai diaudit.
>
> **Aturan Wajib Buku Panduan UNTAN (DILARANG DILANGGAR):**
> 1. **Tanpa Kata Ganti Orang:** Dilarang menggunakan *kami*, *saya*, *penulis*, atau *kita*. Gunakan sudut pandang pasif formal ilmiah.
> 2. **Tanpa Kata Hubung di Awal Kalimat:** Dilarang memulai kalimat dengan *maka*, *sehingga*, *dengan*, atau *sedangkan*.
> 3. **Tipografi Asing:** Istilah teknis asing wajib tetap dicetak miring (*italic*).
> 4. **Penulisan Judul Gambar:** Judul Gambar 1 diletakkan di **BAWAH** gambar, rata tengah.
>
> **Tugas Audit dan Polish (Humanizer):**
> 1. **Hilangkan AI Slop & Kata Pengisi:** Bersihkan frasa yang terdengar klise atau hiasan berlebihan.
> 2. **Ketajaman Teknis & Matematis:** Pastikan penjelasan matematis dan notasi rumus presisi, logis, dan tidak mengandung celah ilmiah.
> 3. **Format Output:**
>    - Berikan ulasan singkat mengenai kelebihan, celah teknis/matematis, dan ketepatan referensi pada Poin 8.
>    - Tampilkan hasil naskah revisi akhir Poin 8 yang sudah dipoles sempurna agar bisa langsung saya gunakan."

---

COVER

# Judul Penelitian

Tulis ulang judul resmi:  
_Analisis Kinerja dan Skalabilitas pada Operasi Filter Citra Digital Menggunakan Komputasi Paralel Berbasis Multiprocessing_

# Mata Kuliah Pilihan

Tulis: Komputasi Paralel

# Latar Belakang

Teknologi kamera digital dan sensor pencitraan terus menghasilkan citra dengan matriks yang semakin besar. Citra beresolusi tinggi, misalnya 2048 × 2048 hingga 4096 × 4096 piksel, kini digunakan secara luas pada pencitraan medis (CT-Scan dan MRI), penginderaan jauh berbasis satelit, dan sistem inspeksi industri. Setiap citra tersusun atas jutaan elemen piksel yang harus diproses melalui operasi spasial seperti konvolusi. Pada deteksi tepi _Sobel_, misalnya, nilai setiap piksel dihitung dari piksel di sekitarnya melalui konvolusi dengan _kernel_, sehingga beban komputasi berbanding lurus dengan jumlah piksel. Beban ini bertambah empat kali lipat setiap kali panjang sisi citra digandakan.

Di sisi lain, prosesor modern telah dilengkapi banyak inti fisik (_multi-core processor_) yang mampu mengeksekusi instruksi secara bersamaan. Penambahan inti ini tidak otomatis mempercepat pemrosesan apabila program berjalan secara serial. Eksekusi serial hanya membebani satu inti, sementara inti lainnya menganggur, sehingga daya komputasi terbuang dan latensi pemrosesan memanjang (_computational bottleneck_).

Kebutuhan akselerasi pengolahan citra telah menjadi perhatian berbagai penelitian. Chang et al. (2023) menunjukkan bahwa operator _Sobel_ multi-arah berkernel besar menghasilkan deteksi tepi yang lebih stabil, tetapi dengan mengorbankan kecepatan. Kernel GPU empat arah 5 × 5 yang dikembangkan dalam penelitian tersebut mencapai percepatan 6,7 hingga 13 kali dibandingkan pustaka OpenCV-GPU. Dari sisi perangkat keras, tinjauan Vasile et al. (2024) menegaskan bahwa pemrosesan citra beresolusi tinggi secara _real-time_ membutuhkan penanganan data yang lebih cepat dan efisien. CPU konvensional yang tidak mengeksploitasi konkurensi dinilai terbatas dari sisi latensi, sehingga solusi seperti ASIC, GPU, dan FPGA dibahas sebagai alternatifnya. Paralelisme serupa sebenarnya tersedia pada CPU _multi-core_, tetapi pemanfaatannya di Python terkendala _Global Interpreter Lock_ (GIL) pada CPython. Gultom dan Sarumaha (2025) menunjukkan secara empiris bahwa GIL membatasi eksekusi _thread_ serentak pada beban kerja _CPU-bound_, sehingga _multithreading_ hanya menghasilkan _speedup_ sekitar 1,05 kali. Sebaliknya, _multiprocessing_ menghasilkan _speedup_ sebesar 3,16 hingga 3,55 kali pada empat proses kerja karena setiap proses memiliki ruang memori sendiri dan tidak terikat GIL.

Berdasarkan permasalahan tersebut, penelitian ini menerapkan komputasi paralel dengan paradigma data parallelism melalui modul multiprocessing Python dan partisi spasial horizontal (horizontal row partitioning). Pendekatan ini dipilih karena filter citra bersifat embarrassingly parallel: nilai tiap piksel keluaran hanya bergantung pada piksel masukan di sekitarnya, sehingga ketergantungan data antarproses minim. Irisan data hanya terjadi pada baris tepi antarblok (boundary halo) yang dibaca tanpa ditulis, sehingga blok dapat diproses serentak tanpa race condition. Pembagian matriks ke dalam blok horizontal mendistribusikan beban kerja ke seluruh inti fisik, sekaligus melewati batasan GIL.

Ketiga rujukan di atas membahas akselerasi _Sobel_ pada GPU, akselerator perangkat keras, dan beban kerja _CPU-bound_ Python secara umum, sehingga perilaku skalabilitas _multiprocessing_ pada filter citra masih terbatas dan belum banyak dipetakan secara terperinci. Penelitian ini mengisi celah tersebut melalui pengujian terkontrol terhadap tiga filter (_Grayscale_, _Gaussian Blur_, dan _Sobel_) pada resolusi 512 × 512 hingga 4096 × 4096 piksel dengan alokasi satu, dua, empat, dan delapan proses. Parameter yang diukur meliputi waktu eksekusi, rasio percepatan (_speedup_), efisiensi, beban tambahan (_overhead_) paralel, dan utilisasi CPU, kemudian dibandingkan dengan batas skalabilitas Hukum Amdahl. Hasilnya diharapkan menjadi tolok ukur empiris bagi efektivitas komputasi paralel pada sistem komputer modern.

# Perumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam penelitian ini adalah sebagai berikut:

1. Bagaimana pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (_speedup_) dan efisiensi komputasi paralel berbasis _multiprocessing_?
2. Bagaimana pola skalabilitas penambahan alokasi proses kerja (_worker processes_) pada prosesor _multi-core_ terhadap batas percepatan teoretis Hukum Amdahl?
3. Bagaimana pengaruh variasi tingkat kompleksitas algoritma filter citra (_Grayscale_, _Gaussian Blur_, dan _Sobel_) terhadap beban tambahan (_overhead_) paralel dan utilisasi CPU?

# Tujuan Penelitian

Sesuai dengan rumusan masalah di atas, tujuan dari penelitian ini adalah:

1. Menganalisis pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (_speedup_) dan efisiensi komputasi paralel berbasis _multiprocessing_.
2. Mengevaluasi pola skalabilitas penambahan alokasi proses kerja (_worker processes_) pada prosesor _multi-core_ terhadap batas percepatan teoretis Hukum Amdahl.
3. Menganalisis pengaruh variasi tingkat kompleksitas algoritma filter citra (_Grayscale_, _Gaussian Blur_, dan _Sobel_) terhadap beban tambahan (_overhead_) paralel dan utilisasi CPU.

# Batasan Masalah

Agar penelitian lebih terarah dan tidak melebar, ruang lingkup penelitian dibatasi pada hal-hal berikut:

- 1. Citra masukan: citra digital berformat RGB tanpa kompresi dengan variasi resolusi 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.
  2. Operasi filter: tiga jenis operasi dengan tingkat kompleksitas bertingkat, yaitu Grayscale (operasi titik), Gaussian Blur dengan kernel 3 × 3 (operasi area), dan Sobel (operasi gradien).
  3. Perangkat lunak: bahasa pemrograman Python 3.12/3.14 dengan modul bawaan multiprocessing, pustaka NumPy untuk komputasi matriks, serta OpenCV untuk I/O citra dengan pembatasan thread tunggal (cv2.setNumThreads(1)).
  4. Metode partisi: pembagian data secara horizontal (horizontal row partitioning) melalui multiprocessing.Pool() dengan penanganan baris batas (overlapping boundary).
  5. Lingkungan pengujian: satu unit komputer uji multi-core dengan prosesor 13th Gen Intel Core i5-13420H (8 inti fisik, 12 thread), memori RAM 16 GB, dan sistem operasi Windows 11 64-bit, dengan alokasi pengujian satu proses (serial sebagai baseline), dua proses, empat proses, dan delapan proses kerja.

# Manfaat Penelitian

Hasil penelitian ini diharapkan memberikan manfaat bagi pihak-pihak berikut:

1. Praktisi visi komputer dan rekayasa perangkat lunak: acuan kuantitatif mengenai ukuran citra yang layak diparalelkan, sehingga penurunan kinerja akibat beban tambahan (_overhead_) dapat dihindari.
2. Industri otomasi dan pencitraan medis: data empiris tentang percepatan pra-pemrosesan citra beresolusi tinggi pada CPU _multi-core_ tanpa memerlukan GPU.
3. Akademisi: data empiris tentang perilaku komputasi paralel di Python serta pengujian kesesuaian hasil terhadap batas percepatan Hukum Amdahl pada prosesor _multi-core_.

# Deskripsi Penelitian

Sistem pemrosesan citra digital yang dikembangkan pada penelitian ini mengimplementasikan paradigma _data parallelism_ untuk mengakselerasi komputasi filter pada citra beresolusi tinggi. Alur kerja program dirancang secara terpadu melalui integrasi pemrosesan larik multidimensi _NumPy_, pustaka _OpenCV_, dan modul bawaan Python _multiprocessing_.

Tahapan sistem dimulai dengan pembacaan berkas citra masukan berformat RGB menggunakan _OpenCV_ (cv2.imread) ke dalam memori utama. Citra tersebut direpresentasikan sebagai matriks piksel tiga dimensi berukuran H×W×C (tinggi, lebar, dan kanal warna). Pola peny impanan memori array _NumPy_ menggunakan urutan berbasis baris (_Row-Major Order_ atau _C-contiguous_). Pengorganisasian data secara kontigu per baris pada memori fisik sangat menguntungkan bagi operasi filter citra karena memaksimalkan lokalitas spasial dan meminimalkan kegagalan _cache_ (_cache misses_) saat data diakses oleh inti prosesor (Tanenbaum & Bos, 2022).

Sebelum proses dekomposisi data dijalankan, sistem mencatat stempel waktu awal (_start timestamp_). Matriks citra selanjutnya dipartisi secara horizontal (_horizontal row partitioning_). Dimensi tinggi citra (H) dibagi secara merata ke dalam sejumlah P proses pekerja yang dialokasikan, di mana setiap pekerja menerima sub-matriks berdimensi ⌊H/P⌋×W×C dengan penyertaan baris batas tetangga (_overlapping boundary padding_) untuk mendukung konvolusi area. Data segmen baris ini kemudian disalurkan ke kumpulan proses pekerja (_worker pool_) menggunakan antarmuka Pool.map() pada modul _multiprocessing_.

Pemilihan modul _multiprocessing_ didasarkan pada temuan empiris Gultom dan Sarumaha (2025), yang membuktikan bahwa pendekatan multi-benang (_multithreading_) pada Python tidak mampu memberikan percepatan pada beban komputasi intensif CPU (_CPU-bound_) akibat restriksi _Global Interpreter Lock_ (GIL). Modul _multiprocessing_ mengatasi kendala tersebut dengan membangkitkan proses-proses independen pada tingkat sistem operasi yang memiliki ruang alamat memori (_address space_) dan penerjemah terpisah. Mekanisme ini memungkinkan eksekusi paralel murni (_true parallelism_) pada prosesor _multi-core_ (Pacheco & Malensek, 2022). Setiap proses pekerja secara serentak mengeksekusi operasi filter yang ditentukan pada segmennya, meliputi konversi _Grayscale_, penghalusan derau _Gaussian Blur_ _kernel_ 3×3, dan deteksi tepi gradien spasial _Sobel_.

Setelah komputasi pada seluruh sub-matriks selesai, pecahan matriks hasil dikirimkan kembali ke proses utama (_master process_). Proses utama kemudian melakukan rekonstruksi matriks citra utuh melalui penyambungan baris vertikal (_vertical concatenation_ / numpy.vstack). Tepat setelah matriks citra utuh terbentuk kembali, stempel waktu akhir (_stop timestamp_) dicatat guna mengukur total durasi eksekusi paralel aktual (TparalelT_{paralel}Tparalel​).

Arsitektur aliran data dan pembagian kerja multi-proses pada sistem pemrosesan citra digital paralel disajikan pada Gambar 1.

![Gambar 1. Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel](image1.png)


Gambar 1. Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel

## Formulasi Matematis dan Parameter Kinerja

Evaluasi kinerja algoritma komputasi dan analisis matematis dalam penelitian ini didefinisikan secara kuantitatif melalui formulasi parameter kinerja berikut.

### Konvolusi Citra Digital 2D

Operasi filter spasial (_Gaussian Blur_ dan deteksi tepi _Sobel_) diproses dengan menggeser matriks _kernel_ di atas bidang piksel citra masukan. Berdasarkan formulasi standar pengolahan citra digital (Vasile et al., 2024), konvolusi diskret dua dimensi dinyatakan pada Persamaan (1):



$$I_{filter}(x, y) = \sum_{i=-k}^{k} \sum_{j=-k}^{k} I(x + i, y + j) \cdot K(i, j) \qquad (1)$$

Keterangan:

- 1. _Ifilter(x, y)_ : Nilai intensitas piksel hasil pemfilteran pada koordinat spasial (x, y).
  2. _I(x + i, y + j)_ : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (x + i, y + j).
  3. _K(i, j)_ : Koefisien bobot matriks kernel konvolusi pada posisi relatif (i, j).
  4. _k_ : Radius spasial matriks kernel (pada matriks kernel berukuran 3 × 3, bernilai k = 1).
  5. _i, j_ : Indeks koordinat pergeseran spasial kernel secara vertikal dan horizontal.

### Rasio Percepatan (Speedup)

Rasio percepatan (speedup) mengukur seberapa banyak komputasi paralel mampu mempercepat proses penyelesaian dibandingkan dengan eksekusi program serial sekuensial. Merujuk pada Pacheco dan Malensek (2022), speedup (S) dirumuskan pada Persamaan (2):



$$S = \frac{T_{serial}}{T_{paralel}} \qquad (2)$$

Keterangan:

- 1. _S_ : Nilai rasio percepatan (speedup) komputasi (rasio tanpa satuan).
  2. _T_serial_ : Waktu eksekusi pemrosesan citra secara serial pada satu proses pekerja tunggal (detik).
  3. _T_paralel_ : Waktu eksekusi pemrosesan citra secara paralel pada alokasi P proses pekerja (detik).

### Efisiensi Paralel (Efficiency)

Efisiensi mengukur persentase pemanfaatan daya komputasi dari setiap proses pekerja atau inti prosesor yang dikerahkan (Pacheco & Malensek, 2022), sebagaimana dirumuskan pada Persamaan (3):



$$E = \frac{S}{P} \times 100\% \qquad (3)$$

Keterangan:

- 1. _E_ : Persentase efisiensi komputasi paralel (%).
  2. _S_ : Nilai rasio percepatan (speedup) yang diperoleh dari Persamaan (2).
  3. _P_ : Jumlah proses pekerja (worker processes) yang dialokasikan dalam eksekusi paralel.

### Beban Tambahan Paralel (Parallel Overhead)

Beban tambahan (_overhead_) komputasi paralel merupakan selisih antara waktu eksekusi paralel aktual dengan waktu paralel ideal teoretis. Sesuai dengan analisis Pacheco dan Malensek (2022) serta Gultom dan Sarumaha (2025), waktu beban tambahan (T<sub>overhead</sub>) dirumuskan pada Persamaan (4):

$$T_{overhead} = T_{paralel} - \frac{T_{serial}}{P} \qquad (4)$$

Keterangan:

- 1. _Toverhead_ : Durasi beban tambahan sistem paralel akibat pembuatan proses (process spawning), komunikasi antar-proses (IPC), serialisasi data NumPy (pickling), serta rekonstruksi matriks (detik).
  2. _Tparalel_ : Waktu eksekusi paralel aktual yang terukur (detik).
  3. _Tserial / P_ : Waktu eksekusi paralel ideal secara teoritis tanpa penalti koordinasi sistem (detik).
  4. _Tserial_ : Waktu eksekusi serial baseline (detik).
  5. _P_ : Jumlah proses pekerja yang dialokasikan.

### Batas Skalabilitas Berdasarkan Hukum Amdahl

Hukum Amdahl mendefinisikan batas percepatan teoretis maksimum yang dapat dicapai oleh sistem multi-core dengan memperhitungkan fraksi program yang tidak dapat dibagi secara paralel (Pacheco & Malensek, 2022), sebagaimana dinyatakan pada Persamaan (5):



$$S_{Amdahl} = \frac{1}{(1 - f) + \frac{f}{P}} \qquad (5)$$

Keterangan:

- 1. _S<sub>Amdahl</sub>_ : Batas percepatan teoritis maksimum (theoretical maximum speedup) menurut Hukum Amdahl.
  2. _f_ : Fraksi program yang dapat dieksekusi secara paralel secara sempurna (parallelizable fraction), bernilai 0 ≤ f ≤ 1.
  3. _(1 - f)_ : Fraksi program yang bersifat sekuensial murni (strictly sequential fraction) yang tidak dapat dibagi ke multi-core (seperti partisi awal matriks secara horizontal dan rekonstruksi citra akhir).
  4. _P_ : Jumlah proses pekerja atau inti prosesor (core) yang dialokasikan.

# Metode Penelitian

Metode penelitian ini menggunakan pendekatan eksperimen faktorial terkontrol (_controlled factorial experimental research_) untuk mengevaluasi kinerja dan skalabilitas komputasi paralel secara empiris. Pengujian membandingkan eksekusi serial tunggal (_baseline_) dengan eksekusi paralel berbasis partisi spasial pada prosesor _multi-core_.

## Tahapan Penelitian

Penelitian dilaksanakan dalam enam tahap sebagai berikut:

1. Studi literatur, yaitu pengkajian teori komputasi paralel, mekanisme pengalamatan memori larik _NumPy_, arsitektur konkurensi modul Python _multiprocessing_, batasan _Global Interpreter Lock_ (GIL), serta formulasi matematis filter spasial citra (_Grayscale_, _Gaussian Blur_, dan _Sobel_).
2. Perancangan dan pengkodean algoritma, yaitu pengembangan dua versi perangkat lunak pengujian: skrip serial sebagai _baseline_ dan skrip paralel yang memadukan fungsi partisi matriks horizontal dengan distribusi tugas melalui _multiprocessing.Pool()_.
3. Penyiapan _dataset_ citra uji, yaitu penyeragaman citra masukan berformat RGB tanpa kompresi pada dimensi 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel dengan sebaran warna yang identik.
4. Eksekusi eksperimen terkontrol, yaitu pengujian algoritma pada sistem operasi tanpa aplikasi latar belakang yang berat. Setiap kombinasi perlakuan pengujian dieksekusi sebanyak satu kali secara deterministik pada citra uji standar untuk mengukur durasi komputasi murni.
5. Pencatatan parameter kinerja, yaitu pengukuran waktu komputasi murni dengan _time.perf_counter()_, pemantauan utilisasi inti prosesor dengan _psutil_, serta penghitungan _speedup_, efisiensi, dan _overhead_ paralel.
6. Analisis skalabilitas dan penarikan kesimpulan, yaitu penyajian data dalam kurva komparatif, evaluasi kurva percepatan terhadap batas teoretis Hukum Amdahl, serta penarikan kesimpulan tentang efektivitas komputasi paralel pada berbagai ukuran data dan kompleksitas filter.

Bagan alir pelaksanaan tahapan penelitian secara menyeluruh disajikan pada Gambar 2.

![Gambar 2. Diagram Alir Proses Penelitian](Flowchart Komputasi Paralel.drawio.png)


Gambar 2. Diagram Alir Proses Penelitian

## Desain Eksperimen dan Skenario Pengujian

Setiap operasi filter diuji pada variasi ukuran data dan alokasi proses kerja yang dirinci dalam tiga skenario berikut.

### Skenario A: Variasi Dimensi Citra

Alokasi proses kerja dikunci pada empat proses (_Pool(processes=4)_). Resolusi citra dinaikkan bertahap dengan sisi berlipat dua pada setiap langkah, dari 512 × 512 hingga 4096 × 4096 piksel, pada ketiga filter (_Grayscale_, _Gaussian Blur_, dan _Sobel_). Skenario ini menganalisis pengaruh ukuran matriks terhadap rasio _speedup_ pada tiap karakteristik operasi. Matriks pengujian dirangkum pada Tabel 1.

Tabel 1. Matriks Pengujian Skenario A (Variasi Dimensi Citra)

| Kode Uji | Resolusi Citra (Piksel) | Total Elemen Matriks | Jenis Operasi yang Diuji              | Alokasi Proses | Jumlah Pengujian |
| -------- | ----------------------- | -------------------- | ------------------------------------- | -------------- | ---------------- |
| A1       | 512 × 512               | 262.144              | _Grayscale_, _Gaussian Blur_, _Sobel_ | 4 Proses       | 2 Kali           |
| A2       | 1024 × 1024             | 1.048.576            | _Grayscale_, _Gaussian Blur_, _Sobel_ | 4 Proses       | 2 Kali           |
| A3       | 2048 × 2048             | 4.194.304            | Grayscale, Gaussian Blur, Sobel       | 4 Proses       | 2 Kali           |
| A4       | 4096 × 4096             | 16.777.216           | Grayscale, Gaussian Blur, Sobel       | 4 Proses       | 2 Kali           |

### Skenario B: Variasi Alokasi Proses Kerja

Dimensi citra dikunci pada 2048 × 2048 piksel. Alokasi proses kerja divariasikan dari satu proses (_baseline_ serial), dua proses, empat proses, hingga delapan proses pada ketiga filter. Skenario ini memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan menguji apakah operasi berbeban berat (_Sobel_) lebih mendekati percepatan linear daripada operasi ringan (_Grayscale_). Matriks pengujian disajikan pada Tabel 2.

Tabel 2. Matriks Pengujian Skenario B

| Kode Uji | Alokasi Proses Kerja | Mode Eksekusi                 | Jenis Operasi yang Diuji              | Dimensi Citra | Jumlah Pengujian |
| -------- | -------------------- | ----------------------------- | ------------------------------------- | ------------- | ---------------- |
| B0       | 1 Proses             | Mode Serial (_Baseline_)      | _Grayscale_, _Gaussian Blur_, _Sobel_ | 2048 × 2048   | 2 Kali           |
| B1       | 2 Proses             | Mode Paralel (_Dual-Process_) | _Grayscale_, _Gaussian Blur_, _Sobel_ | 2048 × 2048   | 2 Kali           |
| B2       | 4 Proses             | Mode Paralel (_Quad-Process_) | Grayscale, Gaussian Blur, Sobel       | 2048 × 2048   | 2 Kali           |
| B3       | 8 Proses             | Mode Paralel (_Octa-Process_) | Grayscale, Gaussian Blur, Sobel       | 2048 × 2048   | 2 Kali           |

### Skenario C: Variasi Jenis Operasi Filter

Skenario C membandingkan kompleksitas matematis tiap algoritma dengan efisiensi paralel yang dihasilkannya, berdasarkan data Skenario A dan B. Ketiga tingkat beban algoritma dirinci pada Tabel 3.

Tabel 3. Klasifikasi Tingkat Kompleksitas Operasi Filter Citra

| Kode | Jenis Operasi Filter | Karakteristik Perhitungan Matematis                             | Tingkat Kompleksitas | Kondisi Titik Uji Komparasi      |
| ---- | -------------------- | --------------------------------------------------------------- | -------------------- | -------------------------------- |
| C1   | Konversi Grayscale   | Operasi Titik Matematis Tunggal (1 × 1) per piksel              | Ringan               | Resolusi 2048 px (1 vs 4 proses) |
| C2   | _Gaussian Blur_      | Konvolusi Matriks Ketetanggan Kernel (3 × 3)                    | Moderat              | Resolusi 2048 px (1 vs 4 proses) |
| C3   | Deteksi Tepi _Sobel_ | Gradien Turunan Parsial Ganda (G<sub>x</sub> dan G<sub>y</sub>) | Berat                | Resolusi 2048 px (1 vs 4 proses) |

## Parameter Kinerja yang Diuji

Efektivitas komputasi paralel dievaluasi melalui lima parameter kinerja pada Tabel 4. Waktu eksekusi yang dipakai untuk menghitung percepatan dan efisiensi diperoleh dari hasil satu kali pengujian terkontrol pada masing-masing kombinasi perlakuan.

Tabel 4. Parameter Kinerja Pengujian Komputasi Paralel

| Nama Parameter    | Notasi                 | Definisi Operasional                                                                 | Satuan                     |
| ----------------- | ---------------------- | ------------------------------------------------------------------------------------ | -------------------------- |
| Waktu Eksekusi    | T                      | Durasi waktu yang dibutuhkan untuk menyelesaikan kalkulasi filter citra pada pengujian terkontrol  | Detik (s) / Milidetik (ms) |
| Rasio Percepatan  | S                      | Perbandingan kelipatan kecepatan antara waktu eksekusi serial terhadap waktu paralel | Rasio (Tanpa satuan)       |
| Efisiensi Paralel | E                      | Persentase daya pemanfaatan inti prosesor terhadap percepatan yang diraih            | Persen (%)                 |
| Utilisasi CPU     | %CPU                   | Rata-rata beban pemakaian daya komputasi di seluruh inti prosesor selama eksekusi    | Persen (%)                 |
| Beban Tambahan    | _T<sub>overhead</sub>_ | Selisih waktu keterlambatan akibat partisi data di memori dan komunikasi proses      | Detik (s)                  |

# DAFTAR PUSTAKA

Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). Multi-directional Sobel operator kernel on GPUs. *arXiv*. https://doi.org/10.48550/arXiv.2305.00515

Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. *Journal of Informatics, Computer Science, Data Science and Artificial Intelligence*, *3*(2), 1–8. https://doi.org/10.63532/jicsda.v3i2.146

Pacheco, P. S., & Malensek, M. (2022). *An introduction to parallel programming* (2nd ed.). Morgan Kaufmann.

Tanenbaum, A. S., & Bos, H. (2022). *Modern operating systems* (5th ed.). Pearson.

Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. *Journal of Imaging*, *10*(12), 298. https://doi.org/10.3390/jimaging10120298
