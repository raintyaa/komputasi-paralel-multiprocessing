**ANALISIS KINERJA DAN SKALABILITAS PADA OPERASI FILTER CITRA DIGITAL MENGGUNAKAN KOMPUTASI PARALEL BERBASIS MULTIPROCESSING
**

**PROPOSAL TUGAS AKHIR
**

DOSEN PENGAMPU :
**Kartika Sari, S.Kom., M.Cs**

Disusun Oleh :


**PROGRAM STUDI REKAYASA SISTEM KOMPUTER
FAKULTAS MATEMATIKA DAN ILMU PENGETAHUAN ALAM
UNIVERSITAS TANJUNGPURA
PONTIANAK
2026**

# 1. Latar Belakang

Perkembangan kamera digital dan sensor pencitraan terus memperbesar ukuran matriks citra yang harus diproses oleh sistem visi komputer modern (Cremel & Arruda, 2026). Citra beresolusi tinggi, yang dalam satu berkas dapat memuat jutaan piksel, telah diterapkan secara luas pada berbagai bidang strategis, antara lain sistem penunjang diagnosis medis, pemantauan pertanian cerdas berbasis sensor udara, dan inspeksi visual otomasi industri (Cremel & Arruda, 2026). Setiap elemen piksel pada matriks tersebut harus diproses melalui operasi spasial seperti konvolusi, yang beban komputasinya tumbuh seiring peningkatan dimensi citra dan ukuran matriks kernel yang digunakan (Cremel & Arruda, 2026; Gonzalez & Woods, 2018). Pada operasi deteksi tepi Sobel, nilai intensitas setiap piksel dihitung dari interaksi piksel ketetanggaannya melalui konvolusi kernel turunan ganda (_Gx_ dan _Gy_). Karakteristik komputasi ini menyebabkan beban kalkulasi berbanding lurus dengan jumlah total piksel, sehingga kebutuhan komputasi bertambah secara kuadratik atau empat kali lipat setiap kali panjang sisi citra digandakan.

Di sisi lain, perkembangan arsitektur perangkat keras prosesor modern telah beralih ke integrasi banyak inti fisik (_multi-core processor_) yang mampu mengeksekusi instruksi secara serentak (Pacheco & Malensek, 2022). Akan tetapi, perangkat lunak yang dirancang secara serial konvensional tidak dapat memanfaatkan ketersediaan inti tambahan tersebut secara otomatis (Pacheco & Malensek, 2022). Eksekusi program serial hanya membebani satu inti prosesor, sementara inti-inti lainnya berada dalam kondisi menganggur (_idle_), sehingga kapasitas daya komputasi terbuang dan latensi pemrosesan memanjang (_computational bottleneck_) (Cremel & Arruda, 2026; Pacheco & Malensek, 2022).

Berbagai penelitian telah dilakukan untuk menangani akselerasi pengolahan citra digital. Chang et al. (2023) menunjukkan bahwa penerapan operator Sobel multi-arah berukuran kernel besar mampu menghasilkan deteksi tepi yang lebih stabil, namun menuntut komputasi intensif yang diatasi melalui akselerasi GPU dengan pencapaian _speedup_ 6,7 hingga 13 kali lipat dibandingkan pustaka OpenCV-GPU standar. Dari sudut pandang arsitektur perangkat keras, Vasile et al. (2024) menegaskan bahwa pemrosesan citra beresolusi tinggi secara _real-time_ memerlukan efisiensi penanganan aliran data yang tinggi, di mana arsitektur CPU serial konvensional memiliki keterbatasan laten dalam memenuhi ambang batas waktu respons. Pada ranah prosesor _multi-core_, Cremel dan Arruda (2026) mengevaluasi percepatan filter spasial citra berbasis OpenMP dan melaporkan bahwa resolusi citra dan kompleksitas algoritma sangat menentukan rasio percepatan (_speedup_) dan efisiensi, dengan kecenderungan efisiensi yang menurun seiring bertambahnya jumlah _thread_ kerja serta penurunan paling tajam pada deteksi tepi Sobel (mencapai sekitar 24% pada delapan _thread_). Ibrahim et al. (2021) turut memperkuat temuan tersebut melalui pengujian konvolusi Gaussian blur paralel pada CPU _multi-core_ dan GPU. Namun, implementasi komputasi paralel pada CPU menggunakan bahasa pemrograman Python memiliki tantangan arsitektur khusus berupa Global Interpreter Lock (GIL) pada rilis resmi CPython, yaitu mekanisme penguncian internal interpreter yang membatasi eksekusi bytecode Python hanya pada satu _thread_ dalam satu waktu (Python Software Foundation, n.d.-a). Gultom dan Sarumaha (2025) membuktikan secara empiris bahwa GIL membatasi eksekusi utas serentak pada beban kerja intensif komputasi (_CPU-bound_), di mana _multithreading_ hanya menghasilkan _speedup_ marjinal sekitar 1,05 kali. Sebaliknya, paradigma _multiprocessing_ mampu melipatgandakan kinerja dengan _speedup_ mencapai 3,16 hingga 3,55 kali pada empat proses kerja karena setiap proses dialokasikan ruang memori (_address space_) dan interpreter independen (Gultom & Sarumaha, 2025; Tanenbaum & Bos, 2022).

Berdasarkan permasalahan tersebut, penelitian ini menerapkan komputasi paralel berbasis paradigma dekomposisi data spasial (_data parallelism_), yaitu strategi pemecahan struktur matriks data untuk didistribusikan ke sejumlah unit proses pekerja yang mengeksekusi instruksi filter secara bersamaan (Pacheco & Malensek, 2022), memanfaatkan modul bawaan _multiprocessing_ pada Python (Python Software Foundation, n.d.-b) dengan metode partisi baris horizontal (_horizontal row partitioning_). Pendekatan dekomposisi domain ini dipilih karena operasi filter spasial citra memiliki karakteristik komputasi yang mandiri (_embarrassingly parallel_), di mana nilai luaran suatu piksel hanya ditentukan oleh nilai masukan piksel pada area ketetanggaannya (Cremel & Arruda, 2026). Pada rancangan penelitian ini, ketergantungan data antar-bagian hanya terjadi pada batas tepi partisi, yang ditangani secara khusus melalui mekanisme baris batas (_boundary halo_) yang dibaca tanpa operasi penulisan ulang, sehingga mencegah terjadinya konflik akses data (_race condition_). Pembagian matriks ke dalam blok horizontal mendistribusikan beban kerja ke seluruh inti fisik prosesor sekaligus mengeliminasi hambatan GIL.

Kajian pustaka memperlihatkan bahwa evaluasi percepatan dan efisiensi filter spasial citra pada prosesor _multi-core_ selama ini didominasi oleh model komputasi berbasis _thread_ seperti OpenMP (Cremel & Arruda, 2026). Karakteristik skalabilitas komputasi paralel pada Python yang berbasis proses independen, termasuk beban tambahan komunikasi antar-proses (_inter-process communication overhead_) serta dampaknya pada prosesor modern berarsitektur hibrida (_Performance-Core_ dan _Efficient-Core_), belum banyak dipetakan secara terukur. Penelitian ini mengisi celah tersebut melalui serangkaian pengujian terkontrol terhadap tiga variasi filter bertingkat (Grayscale, Gaussian Blur 3×3, dan Sobel 3×3) pada rentang resolusi 512 × 512 hingga 4096 × 4096 piksel dengan alokasi proses kerja satu, dua, empat, dan delapan proses. Parameter kinerja yang diukur meliputi waktu eksekusi, rasio percepatan (_speedup_), efisiensi, beban tambahan (_overhead_) paralel, dan pemantauan utilisasi CPU, yang kemudian dikomparasikan terhadap batas percepatan teoretis Hukum Amdahl (Amdahl, 1967) serta diagnostik fraksi serial melalui metrik Karp–Flatt (Karp & Flatt, 1990). Hasil penelitian ini diharapkan dapat menjadi tolok ukur empiris bagi efektivitas dan batas skalabilitas komputasi paralel pada pemrosesan citra digital di sistem komputer modern.

# 2. Perumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam penelitian ini adalah sebagai berikut:

1. Bagaimana pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (speedup) dan efisiensi komputasi paralel berbasis multiprocessing?
2. Bagaimana pola skalabilitas penambahan alokasi proses kerja (worker processes) pada prosesor multi-core terhadap batas percepatan teoretis Hukum Amdahl?
3. Bagaimana pengaruh variasi tingkat kompleksitas algoritma filter citra (Grayscale, Gaussian Blur, dan Sobel) terhadap beban tambahan (overhead) paralel dan utilisasi CPU?

# 3. Tujuan Penelitian

Sesuai dengan rumusan masalah di atas, tujuan dari penelitian ini adalah:

1. Menganalisis pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (speedup) dan efisiensi komputasi paralel berbasis multiprocessing.
2. Mengevaluasi pola skalabilitas penambahan alokasi proses kerja (worker processes) pada prosesor multi-core terhadap batas percepatan teoretis Hukum Amdahl.
3. Menganalisis pengaruh variasi tingkat kompleksitas algoritma filter citra (Grayscale, Gaussian Blur, dan Sobel) terhadap beban tambahan (overhead) paralel dan utilisasi CPU.

# 4. Batasan Masalah

Ruang lingkup penelitian dibatasi pada hal-hal berikut:

1. Citra masukan: citra digital berformat RGB tanpa kompresi dengan variasi resolusi 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.
2. Operasi filter: tiga jenis operasi dengan tingkat kompleksitas bertingkat, yaitu Grayscale (operasi titik), Gaussian Blur dengan kernel 3 × 3 (operasi area), dan Sobel (operasi gradien).
3. Perangkat lunak: bahasa pemrograman Python 3.14 (CPython) dengan modul bawaan multiprocessing, pustaka NumPy untuk komputasi matriks, serta OpenCV untuk I/O citra dengan pembatasan thread tunggal (cv2.setNumThreads(1)).
4. Metode partisi: pembagian data secara horizontal (horizontal row partitioning) melalui multiprocessing.Pool() dengan penanganan baris batas (boundary halo).
5. Lingkungan pengujian: satu unit komputer uji multi-core dengan prosesor 13th Gen Intel Core i5-13420H (8 inti fisik: 4 P-core + 4 E-core, 12 thread), memori RAM 16 GB, dan sistem operasi Windows 11 64-bit, dengan alokasi pengujian satu proses (serial sebagai baseline), dua proses, empat proses, dan delapan proses kerja.

# 5. Manfaat Penelitian

Hasil penelitian ini diharapkan memberikan manfaat bagi pihak-pihak berikut:

1. Praktisi visi komputer dan rekayasa perangkat lunak: acuan kuantitatif mengenai ukuran citra yang layak diparalelkan, sehingga penurunan kinerja akibat beban tambahan (overhead) dapat dihindari.
2. Industri otomasi dan pencitraan medis: data empiris tentang percepatan pra-pemrosesan citra beresolusi tinggi pada CPU multi-core tanpa memerlukan GPU.
3. Akademisi: data empiris tentang perilaku komputasi paralel di Python serta pengujian kesesuaian hasil terhadap batas percepatan Hukum Amdahl pada prosesor multi-core.

# 6. Deskripsi Penelitian

Sistem pemrosesan citra pada penelitian ini menerapkan paradigma data parallelism untuk mempercepat filter pada citra beresolusi tinggi. Alur kerjanya memadukan larik multidimensi NumPy, modul bawaan Python multiprocessing, dan pustaka OpenCV yang hanya digunakan untuk pembacaan dan penulisan citra (I/O) dengan satu thread (cv2.setNumThreads(1)).

Berkas citra RGB dibaca ke memori utama dengan cv2.imread dan direpresentasikan sebagai matriks piksel tiga dimensi berukuran H × W × C (tinggi, lebar, dan jumlah kanal warna). Larik NumPy disimpan dalam urutan berbasis baris (row-major order atau C-contiguous), sehingga elemen pada satu baris menempati alamat memori yang berurutan. Susunan ini meningkatkan lokalitas spasial dan mengurangi cache miss ketika baris piksel diakses secara berurutan (Pacheco dan Malensek, 2022).

Pengukuran waktu dimulai sebelum matriks dipartisi (start timestamp). Matriks dibagi secara horizontal (horizontal row partitioning): tinggi citra H dibagi rata ke P proses pekerja, sehingga setiap pekerja menerima blok berukuran (H/P) × W × C. Seluruh nilai H dan P pada pengujian habis dibagi, sehingga tidak ada baris sisa. Setiap blok diperluas dengan k baris tetangga di sisi atas dan bawah (boundary halo, dengan k sesuai Persamaan (1)) agar konvolusi pada baris tepi blok tetap memakai piksel sekitarnya. Blok pertama dan terakhir hanya memiliki baris batas pada satu sisi. Blok dikirim ke worker pool melalui Pool.map().

Modul multiprocessing dipilih berdasarkan temuan Gultom dan Sarumaha (2025) bahwa multithreading pada Python hanya menghasilkan speedup sekitar 1,05 kali pada beban kerja CPU-bound akibat Global Interpreter Lock (GIL). Modul multiprocessing melewati batasan ini dengan membuat proses sistem operasi yang independen, masing-masing memiliki ruang alamat memori (address space) dan interpreter sendiri (Tanenbaum dan Bos, 2022). Karena itu, eksekusi paralel sesungguhnya (true parallelism) dapat berjalan pada prosesor multi-core. Setiap pekerja menjalankan filter yang ditentukan pada bloknya secara serentak: konversi Grayscale, penghalusan Gaussian Blur dengan kernel 3 × 3, atau deteksi tepi Sobel. Pada Sobel, konvolusi dilakukan dengan dua kernel gradien (arah horizontal dan vertikal), dan hasilnya digabung menjadi magnitudo gradien.

Setiap pekerja membuang baris batas dari hasilnya sebelum mengembalikan blok ke proses utama (master process). Proses utama menyusun ulang citra utuh dengan penggabungan vertikal (vertical concatenation, numpy.vstack). Stempel waktu akhir (stop timestamp) dicatat segera setelah citra utuh terbentuk, sehingga selisihnya menjadi waktu eksekusi paralel aktual (T_paralel).

**Gambar 1. Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel**

## 6.1. Formulasi Matematis dan Parameter Kinerja

Operasi filter dan parameter kinerja dirumuskan melalui enam persamaan berikut.

### 6.1.1. Konvolusi Citra Digital 2D

Gaussian Blur dan Sobel diproses dengan menggeser matriks kernel di atas bidang piksel citra masukan. Mengacu pada Vasile et al. (2024), operasi ini dinyatakan pada Persamaan (1). Grayscale merupakan operasi titik sehingga tidak memerlukan persamaan ini:

Keterangan:

1. I_filter(x, y) : Nilai intensitas piksel hasil pemfilteran pada koordinat spasial (x, y).
2. I(x + i, y + j) : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (x + i, y + j).
3. K(i, j) : Koefisien bobot matriks kernel konvolusi pada posisi relatif (i, j).
4. k : Radius spasial matriks kernel (pada matriks kernel berukuran 3 × 3, bernilai k = 1).
5. i, j : Indeks koordinat pergeseran spasial kernel secara vertikal dan horizontal.

Bentuk ini merupakan korelasi silang yang lazim disebut konvolusi pada pengolahan citra. Untuk kernel simetris seperti Gaussian, hasilnya identik dengan konvolusi sejati. Pada Sobel, perbedaannya hanya pada tanda gradien, sehingga magnitudo gradien tidak berubah.

### 6.1.2. Rasio Percepatan (Speedup)

Rasio percepatan (_speedup_) mengukur seberapa besar komputasi paralel mempercepat penyelesaian dibandingkan eksekusi serial. Setiap nilai waktu eksekusi (T_serial dan T_paralel) diperoleh melalui 30 kali repetisi pengujian terkontrol secara berselang-seling (_interleaved_) antara eksekusi serial dan paralel pada masing-masing tingkatan perlakuan guna mengisolasi fluktuasi derau sistem. Mengacu pada Pacheco dan Malensek (2022), _speedup_ (S) dirumuskan pada Persamaan (2):

Keterangan:

1. S : Nilai rasio percepatan (speedup) komputasi (rasio tanpa satuan).
2. T_serial : Waktu eksekusi pemrosesan citra pada skrip serial murni (tanpa inisialisasi pool proses) pada satu inti prosesor (detik).
3. T_paralel : Waktu eksekusi pemrosesan citra secara paralel pada alokasi P proses pekerja (detik).

T_serial dan T_paralel diukur secara selang-seling (interleaved) pada setiap repetisi, sehingga setiap nilai S dihitung dari pasangan pengukuran serial dan paralel yang berdekatan. Hasil dilaporkan sebagai median, rerata, dan simpangan baku dari 30 repetisi.

### 6.1.3. Efisiensi Paralel (Efficiency)

Efisiensi mengukur persentase pemanfaatan daya komputasi tiap proses pekerja (Pacheco dan Malensek, 2022), sebagaimana dirumuskan pada Persamaan (3):

Keterangan:

1. E : Persentase efisiensi komputasi paralel (%).
2. S : Nilai rasio percepatan (speedup) yang diperoleh dari Persamaan (2).
3. P : Jumlah proses pekerja (worker processes) yang dialokasikan dalam eksekusi paralel.

### 6.1.4. Beban Tambahan Paralel (Parallel Overhead)

Beban tambahan (overhead) paralel adalah selisih antara waktu paralel aktual dan waktu paralel ideal T_serial / P. Mengacu pada Pacheco dan Malensek (2022), T_overhead dirumuskan pada Persamaan (4):

Keterangan:

1. T_overhead : Durasi beban tambahan sistem paralel akibat komunikasi antar-proses (IPC), serialisasi data NumPy (pickling), penyalinan baris batas (boundary halo), serta rekonstruksi matriks (detik).
2. T_paralel : Waktu eksekusi paralel aktual yang terukur (detik).
3. T_serial / P : Waktu eksekusi paralel ideal secara teoritis tanpa penalti koordinasi sistem (detik).
4. T_serial : Waktu eksekusi serial baseline (detik).
5. P : Jumlah proses pekerja yang dialokasikan.

### 6.1.5. Batas Skalabilitas Berdasarkan Hukum Amdahl dan Metrik Karp–Flatt

Hukum Amdahl menyatakan batas percepatan teoretis suatu program berdasarkan fraksi yang tidak dapat diparalelkan (Pacheco dan Malensek, 2022), sebagaimana dinyatakan pada Persamaan (5):

Keterangan:

1. S_Amdahl : Percepatan teoretis pada P proses menurut Hukum Amdahl; untuk P → ∞ nilainya mendekati 1/(1 − f).
2. f : Fraksi beban kerja yang dapat diparalelkan (0 ≤ f ≤ 1).
3. (1 - f) : Fraksi efektif yang tidak mengalami percepatan, mencakup bagian sekuensial program, beban koordinasi paralel (partisi, IPC, baris batas, rekonstruksi), dan pengaruh arsitektur inti yang tidak setara.
4. P : Jumlah proses pekerja atau inti prosesor (core) yang dialokasikan.

Hukum Amdahl mengasumsikan inti prosesor yang setara. Prosesor uji memiliki arsitektur hibrida (empat performance core dan empat efficient core), sehingga kurva Amdahl diperlakukan sebagai pendekatan teoretis. Nilai f diestimasi per filter dengan metode kuadrat terkecil (least squares) pada rasio percepatan Skenario B untuk P = 2, 4, dan 8, disertai selang kepercayaan 95% hasil bootstrap. Kecocokan model diperiksa dengan fraksi serial eksperimental Karp–Flatt (Karp dan Flatt, 1990), dinyatakan pada Persamaan (6):

dengan e sebagai fraksi serial eksperimental. Nilai e yang konstan terhadap P menunjukkan kesesuaian dengan Hukum Amdahl, sedangkan e yang meningkat menunjukkan beban koordinasi yang membesar seiring P. Estimasi ini bersifat deskriptif atas data pengukuran dan bukan validasi independen.

# 7. Metode Penelitian

Metode penelitian ini menggunakan pendekatan eksperimen faktorial terkontrol (controlled factorial experimental research) untuk mengevaluasi kinerja dan skalabilitas komputasi paralel secara empiris. Pengujian membandingkan eksekusi serial tunggal (baseline) dengan eksekusi paralel berbasis partisi spasial pada prosesor multi-core.

## 7.1. Tahapan Penelitian

Penelitian dilaksanakan dalam enam tahap sebagai berikut:

1. Studi literatur, yaitu pengkajian teori komputasi paralel, mekanisme pengalamatan memori larik NumPy, arsitektur konkurensi modul Python _multiprocessing_, batasan Global Interpreter Lock (GIL), serta formulasi matematis filter spasial citra (Grayscale, Gaussian Blur 3×3, dan Sobel 3×3).
2. Perancangan dan pengkodean algoritma, yaitu pengembangan dua versi perangkat lunak pengujian: skrip serial sebagai _baseline_ dan skrip paralel yang memadukan fungsi partisi matriks horizontal dengan distribusi tugas melalui _multiprocessing_.Pool().
3. Penyiapan dataset citra uji, yaitu standardisasi citra acuan master fotografi beresolusi tinggi 4K (4096 × 4096 piksel) yang bersumber dari repositori fotografi terbuka Aesthetic-4K (Aesthetic-4K Dataset, 2025) berlisensi Creative Commons Attribution 4.0 International (CC-BY 4.0). Citra acuan master tersebut dipotong secara terpusat (_center-crop_) tanpa kompresi ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel. Waktu eksekusi ketiga filter bersifat tidak bergantung pada isi citra (_data-independent_) karena operasi konvolusi matriks tidak memiliki percabangan kondisional berbasis nilai piksel, sehingga satu citra acuan master memadai untuk meniadakan variabilitas tekstur dan mengisolasi variabilitas sistem komputasi (penjadwalan sistem operasi, fluktuasi termal, dan alokasi inti heterogen). Seluruh 30 sampel citra multiresolusi awal tetap diarsipkan sebagai opsi dataset alternatif.
4. Eksekusi eksperimen terkontrol, yaitu pengujian algoritma pada sistem operasi tanpa aplikasi latar belakang yang membebani CPU. Setiap kombinasi perlakuan pengujian dieksekusi sebanyak 30 kali repetisi terkontrol secara selang-seling (_interleaved_) antara pengukuran serial dan paralel pada masing-masing tingkatan resolusi guna memperoleh estimasi parameter statistik yang stabil dan representatif (median, rerata x̄, simpangan baku s, dan selang kepercayaan 95%). Pengukuran durasi komputasi murni memanfaatkan arsitektur _pre-warmed pool_ untuk meniadakan penalti inisialisasi proses (_cold spawn_) pada Windows sesuai aturan proses bawaan CPython (Python Software Foundation, n.d.-b), serta dilengkapi jeda pendinginan termal CPU (_cool-down buffer_) antar-filter guna meminimalkan pelambatan termal (_thermal throttling_). Pergeseran waktu eksekusi antar-blok pengujian (di mana Skenario A dijalankan pertama dan memiliki _baseline_ serial sedikit lebih lambat) dicatat sebagai batasan pengujian.
5. Pencatatan parameter kinerja, yaitu pengukuran waktu komputasi murni dengan time.perf_counter(), pemantauan utilisasi CPU diukur pada proses utama menggunakan modul psutil sebagai estimasi tren beban kerja sistem secara keseluruhan, serta penghitungan _speedup_, efisiensi, dan _overhead_ paralel.
6. Analisis skalabilitas dan penarikan kesimpulan, yaitu penyajian data dalam kurva komparatif, evaluasi kurva percepatan terhadap batas teoretis Hukum Amdahl, serta penarikan kesimpulan tentang efektivitas komputasi paralel pada berbagai ukuran data dan kompleksitas filter.

**Gambar 2. Diagram Alir Proses Penelitian**

## 7.2. Desain Eksperimen dan Skenario Pengujian

Setiap operasi filter diuji pada variasi ukuran data dan alokasi proses kerja yang dirinci dalam tiga skenario berikut.

### 7.2.1. Skenario A: Variasi Dimensi Citra

Alokasi proses kerja dikunci pada empat proses (Pool(processes=4)). Resolusi citra dinaikkan bertahap dengan sisi berlipat dua pada setiap langkah, dari 512 × 512 hingga 4096 × 4096 piksel, pada ketiga filter (Grayscale, Gaussian Blur, dan Sobel). Skenario ini menganalisis pengaruh ukuran matriks terhadap rasio speedup pada tiap karakteristik operasi. Matriks pengujian dirangkum pada Tabel 1.

**Tabel 1. Matriks Pengujian Skenario A (Variasi Dimensi Citra)**

### 7.2.2. Skenario B: Variasi Alokasi Proses Kerja

Dimensi citra dikunci pada 2048 × 2048 piksel. Alokasi proses kerja divariasikan dari satu proses (baseline serial), dua proses, empat proses, hingga delapan proses pada ketiga filter. Kondisi satu proses (B0) dijalankan sebagai kontrol serial terhadap serial (A/A control), yaitu dua pengukuran serial independen, untuk memperkirakan variasi alami sistem. Skenario ini memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan menguji apakah operasi berbeban berat (Sobel) lebih mendekati percepatan linear daripada operasi ringan (Grayscale). Matriks pengujian disajikan pada Tabel 2.

**Tabel 2. Matriks Pengujian Skenario B (Variasi Alokasi Proses Kerja)**

### 7.2.3. Skenario C: Variasi Jenis Operasi Filter

Skenario C dijalankan sebagai blok pengujian terpisah pada resolusi 2048 × 2048 piksel dengan empat proses, dan hasilnya dibandingkan dengan titik uji A3 dan B2 untuk memeriksa keterulangan. Skenario C membandingkan kompleksitas matematis tiap algoritma dengan efisiensi, beban tambahan (overhead), dan utilisasi CPU yang dihasilkannya. Ketiga tingkat beban algoritma dirinci pada Tabel 3.

**Tabel 3. Klasifikasi Tingkat Kompleksitas Operasi Filter Citra**

## 7.3. Parameter Kinerja yang Diuji

Efektivitas komputasi paralel dievaluasi melalui lima parameter kinerja pada Tabel 4. Setiap parameter dilaporkan sebagai median, rerata (x̄), simpangan baku (s), dan selang kepercayaan 95% dari 30 kali repetisi pada masing-masing kombinasi perlakuan.

**Tabel 4. Parameter Kinerja Pengujian Komputasi Paralel**

# DAFTAR PUSTAKA

Aesthetic-4K Dataset. (2025). Aesthetic-4K: High-resolution uncompressed image repository for visual computing research. Creative Commons CC-BY 4.0. https://huggingface.co/datasets/aesthetic-4k

Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. AFIPS Conference Proceedings, 30, 483–485. https://doi.org/10.1145/1465482.1465560

Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). Multi-directional Sobel operator kernel on GPUs. arXiv preprint arXiv:2305.00515. https://doi.org/10.48550/arXiv.2305.00515

Cremel, G. D., & Arruda, L. F. M. (2026). High-performance parallel acceleration of image processing filters on multicore CPUs using OpenMP. Anais do XVII Computer on the Beach, 466–473. https://periodicos.univali.br/index.php/acotb/article/view/22235

Gonzalez, R. C., & Woods, R. E. (2018). Digital image processing (4th ed.). Pearson.

Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. Journal of Informatics, Computer Science, Data Science and Artificial Intelligence, 3(2), 1–11.

Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021) (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179

Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614

Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.

Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock

Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html

Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.

Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. Journal of Imaging, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298
