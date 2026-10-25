# -*- coding: utf-8 -*-
import os
from pathlib import Path

def generate_polished_proposal_md():
    output_path = Path("d:/Rakha/File Kuliah/Semester 5/Komputasi Paralel/UTS/Proposal Komputasi Paralel.md")
    
    content = """ANALISIS KINERJA DAN SKALABILITAS PADA OPERASI FILTER CITRA DIGITAL MENGGUNAKAN KOMPUTASI PARALEL BERBASIS MULTIPROCESSING

KOMPUTASI PARALEL

![Logo Universitas Tanjungpura](assets/logo_untan.png)

DOSEN PENGAMPU :

Kartika Sari , S.Kom., M.Cs

Disusun Oleh :

| Guido Marco Silvio           | H1051241006 |
| ---------------------------- | ----------- |
| Ahmad Dzaky Buhairil Ma'Arif | H1051241074 |
| Muhammad Zaki Rakha Bahy     | H1051241066 |
| Farrel Nathannael            | H1051241094 |

PROGRAM STUDI REKAYASA SISTEM KOMPUTER

FAKULTAS MATEMATIKA DAN ILMU PENGETAHUAN ALAM

UNIVERSITAS TANJUNGPURA

2026

# 1. Latar Belakang

Teknologi kamera digital dan sensor pencitraan terus menghasilkan citra dengan matriks yang semakin besar. Citra beresolusi tinggi, misalnya 2048 × 2048 hingga 4096 × 4096 piksel, kini digunakan secara luas pada pencitraan medis (CT-Scan dan MRI), penginderaan jauh berbasis satelit, dan sistem inspeksi industri. Setiap citra tersusun atas jutaan elemen piksel yang harus diproses melalui operasi spasial seperti konvolusi. Pada deteksi tepi _Sobel_, misalnya, nilai setiap piksel dihitung dari piksel di sekitarnya melalui konvolusi dengan _kernel_, sehingga beban komputasi berbanding lurus dengan jumlah piksel. Beban ini bertambah empat kali lipat setiap kali panjang sisi citra digandakan.

Di sisi lain, prosesor modern telah dilengkapi banyak inti fisik (_multi-core processor_) yang mampu mengeksekusi instruksi secara bersamaan. Penambahan inti ini tidak otomatis mempercepat pemrosesan apabila program berjalan secara serial. Eksekusi serial hanya membebani satu inti, sementara inti lainnya menganggur, sehingga daya komputasi terbuang dan latensi pemrosesan memanjang (_computational bottleneck_).

Kebutuhan akselerasi pengolahan citra telah menjadi perhatian berbagai penelitian. Chang et al. (2023) menunjukkan bahwa operator _Sobel_ multi-arah berkernel besar menghasilkan deteksi tepi yang lebih stabil, tetapi dengan mengorbankan kecepatan. Kernel GPU empat arah 5 × 5 yang dikembangkan dalam penelitian tersebut mencapai percepatan 6,7 hingga 13 kali dibandingkan pustaka OpenCV-GPU. Dari sisi perangkat keras, tinjauan Vasile et al. (2024) menegaskan bahwa pemrosesan citra beresolusi tinggi secara _real-time_ membutuhkan penanganan data yang lebih cepat dan efisien. CPU konvensional yang tidak mengeksploitasi konkurensi dinilai terbatas dari sisi latensi, sehingga solusi seperti ASIC, GPU, dan FPGA dibahas sebagai alternatifnya. Paralelisme serupa sebenarnya tersedia pada CPU _multi-core_, tetapi pemanfaatannya di Python terkendala _Global Interpreter Lock_ (GIL) pada CPython. Gultom dan Sarumaha (2025) menunjukkan secara empiris bahwa GIL membatasi eksekusi _thread_ serentak pada beban kerja _CPU-bound_, sehingga _multithreading_ hanya menghasilkan _speedup_ sekitar 1,05 kali. Sebaliknya, _multiprocessing_ menghasilkan _speedup_ sebesar 3,16 hingga 3,55 kali pada empat proses kerja karena setiap proses memiliki ruang memori sendiri dan tidak terikat GIL.

Berdasarkan permasalahan tersebut, penelitian ini menerapkan komputasi paralel dengan paradigma _data parallelism_ melalui modul _multiprocessing_ Python dan partisi spasial horizontal (_horizontal row partitioning_). Pendekatan ini dipilih karena filter citra bersifat _embarrassingly parallel_: nilai tiap piksel keluaran hanya bergantung pada piksel masukan di sekitarnya, sehingga ketergantungan data antarproses minim. Irisan data hanya terjadi pada baris batas antar-blok (_boundary halo_) yang dibaca tanpa ditulis, sehingga blok dapat diproses serentak tanpa _race condition_. Pembagian matriks ke dalam blok horizontal mendistribusikan beban kerja ke seluruh inti fisik, sekaligus melewati batasan GIL.

Ketiga rujukan di atas membahas akselerasi _Sobel_ pada GPU, akselerator perangkat keras, dan beban kerja _CPU-bound_ Python secara umum, sehingga perilaku skalabilitas _multiprocessing_ pada filter citra masih terbatas dan belum banyak dipetakan secara terperinci. Penelitian ini mengisi celah tersebut melalui pengujian terkontrol terhadap tiga filter (_Grayscale_, _Gaussian Blur_, dan _Sobel_) pada resolusi 512 × 512 hingga 4096 × 4096 piksel dengan alokasi satu, dua, empat, dan delapan proses. Parameter yang diukur meliputi waktu eksekusi, rasio percepatan (_speedup_), efisiensi, beban tambahan (_overhead_) paralel, dan utilisasi CPU, kemudian dibandingkan dengan batas skalabilitas Hukum Amdahl. Hasilnya diharapkan menjadi tolok ukur empiris bagi efektivitas komputasi paralel pada sistem komputer modern.

# 2. Perumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam penelitian ini adalah sebagai berikut:

1. Bagaimana pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (_speedup_) dan efisiensi komputasi paralel berbasis _multiprocessing_?
2. Bagaimana pola skalabilitas penambahan alokasi proses kerja (_worker processes_) pada prosesor _multi-core_ terhadap batas percepatan teoretis Hukum Amdahl?
3. Bagaimana pengaruh variasi tingkat kompleksitas algoritma filter citra (_Grayscale_, _Gaussian Blur_, dan _Sobel_) terhadap beban tambahan (_overhead_) paralel dan utilisasi CPU?

# 3. Tujuan Penelitian

Sesuai dengan rumusan masalah di atas, tujuan dari penelitian ini adalah:

1. Menganalisis pengaruh peningkatan resolusi matriks citra digital terhadap rasio percepatan (_speedup_) dan efisiensi komputasi paralel berbasis _multiprocessing_.
2. Mengevaluasi pola skalabilitas penambahan alokasi proses kerja (_worker processes_) pada prosesor _multi-core_ terhadap batas percepatan teoretis Hukum Amdahl.
3. Menganalisis pengaruh variasi tingkat kompleksitas algoritma filter citra (_Grayscale_, _Gaussian Blur_, dan _Sobel_) terhadap beban tambahan (_overhead_) paralel dan utilisasi CPU.

# 4. Batasan Masalah

Ruang lingkup penelitian dibatasi pada hal-hal berikut:

1. Citra masukan: citra digital berformat RGB tanpa kompresi dengan variasi resolusi 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.
2. Operasi filter: tiga jenis operasi dengan tingkat kompleksitas bertingkat, yaitu _Grayscale_ (operasi titik), _Gaussian Blur_ dengan _kernel_ 3 × 3 (operasi area), dan _Sobel_ (operasi gradien).
3. Perangkat lunak: bahasa pemrograman Python 3.14 (CPython) dengan modul bawaan _multiprocessing_, pustaka _NumPy_ untuk komputasi matriks, serta _OpenCV_ untuk I/O citra dengan pembatasan _thread_ tunggal (_cv2.setNumThreads(1)_).
4. Metode partisi: pembagian data secara horizontal (_horizontal row partitioning_) melalui _multiprocessing.Pool()_ dengan penanganan baris batas (_boundary halo_).
5. Lingkungan pengujian: satu unit komputer uji _multi-core_ dengan prosesor 13th Gen Intel Core i5-13420H (8 inti fisik: 4 P-core + 4 E-core, 12 _thread_), memori RAM 16 GB, dan sistem operasi Windows 11 64-bit, dengan alokasi pengujian satu proses (serial sebagai _baseline_), dua proses, empat proses, dan delapan proses kerja.

# 5. Manfaat Penelitian

Hasil penelitian ini diharapkan memberikan manfaat bagi pihak-pihak berikut:

1. Praktisi visi komputer dan rekayasa perangkat lunak: acuan kuantitatif mengenai ukuran citra yang layak diparalelkan, sehingga penurunan kinerja akibat beban tambahan (_overhead_) dapat dihindari.
2. Industri otomasi dan pencitraan medis: data empiris tentang percepatan pra-pemrosesan citra beresolusi tinggi pada CPU _multi-core_ tanpa memerlukan GPU.
3. Akademisi: data empiris tentang perilaku komputasi paralel di Python serta pengujian kesesuaian hasil terhadap batas percepatan Hukum Amdahl pada prosesor _multi-core_.

# 6. Deskripsi Penelitian

Sistem pemrosesan citra pada penelitian ini menerapkan paradigma _data parallelism_ untuk mempercepat filter pada citra beresolusi tinggi. Alur kerjanya memadukan larik multidimensi _NumPy_, modul bawaan Python _multiprocessing_, dan pustaka _OpenCV_ yang hanya digunakan untuk pembacaan dan penulisan citra (I/O) dengan satu _thread_ (_cv2.setNumThreads(1)_).

Berkas citra RGB dibaca ke memori utama dengan _cv2.imread_ dan direpresentasikan sebagai matriks piksel tiga dimensi berukuran _H_ × _W_ × _C_ (tinggi, lebar, dan jumlah kanal warna). Larik _NumPy_ disimpan dalam urutan berbasis baris (_row-major order_ atau _C-contiguous_), sehingga elemen pada satu baris menempati alamat memori yang berurutan. Susunan ini meningkatkan lokalitas spasial dan mengurangi _cache miss_ ketika baris piksel diakses secara berurutan (Pacheco dan Malensek, 2022).

Pengukuran waktu dimulai sebelum matriks dipartisi (_start timestamp_). Matriks dibagi secara horizontal (_horizontal row partitioning_): tinggi citra _H_ dibagi rata ke _P_ proses pekerja, sehingga setiap pekerja menerima blok berukuran (_H_/_P_) × _W_ × _C_. Seluruh nilai _H_ dan _P_ pada pengujian habis dibagi, sehingga tidak ada baris sisa. Setiap blok diperluas dengan _k_ baris tetangga di sisi atas dan bawah (_boundary halo_, dengan _k_ sesuai Persamaan (1)) agar konvolusi pada baris tepi blok tetap memakai piksel sekitarnya. Blok pertama dan terakhir hanya memiliki baris batas pada satu sisi. Blok dikirim ke _worker pool_ melalui _Pool.map()_.

Modul _multiprocessing_ dipilih berdasarkan temuan Gultom dan Sarumaha (2025) bahwa _multithreading_ pada Python hanya menghasilkan _speedup_ sekitar 1,05 kali pada beban kerja _CPU-bound_ akibat _Global Interpreter Lock_ (GIL). Modul _multiprocessing_ melewati batasan ini dengan membuat proses sistem operasi yang independen, masing-masing memiliki ruang alamat memori (_address space_) dan _interpreter_ sendiri (Tanenbaum dan Bos, 2022). Karena itu, eksekusi paralel sesungguhnya (_true parallelism_) dapat berjalan pada prosesor _multi-core_. Setiap pekerja menjalankan filter yang ditentukan pada bloknya secara serentak: konversi _Grayscale_, penghalusan _Gaussian Blur_ dengan _kernel_ 3 × 3, atau deteksi tepi _Sobel_. Pada _Sobel_, konvolusi dilakukan dengan dua _kernel_ gradien (arah horizontal dan vertikal), dan hasilnya digabung menjadi magnitudo gradien.

Setiap pekerja membuang baris batas dari hasilnya sebelum mengembalikan blok ke proses utama (_master process_). Proses utama menyusun ulang citra utuh dengan penggabungan vertikal (_vertical concatenation_, _numpy.vstack_). Stempel waktu akhir (_stop timestamp_) dicatat segera setelah citra utuh terbentuk, sehingga selisihnya menjadi waktu eksekusi paralel aktual (_T_<sub>paralel</sub>).

Arsitektur aliran data dan pembagian kerja multi-proses pada sistem pemrosesan citra digital paralel disajikan pada Gambar 1.

![Gambar 1. Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel](results/plots/gambar_1_arsitektur_paralel.png)

Gambar 1. Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel

## 6.1. Formulasi Matematis dan Parameter Kinerja

Operasi filter dan parameter kinerja dirumuskan melalui enam persamaan berikut.

### 6.1.1. Konvolusi Citra Digital 2D

_Gaussian Blur_ dan _Sobel_ diproses dengan menggeser matriks _kernel_ di atas bidang piksel citra masukan. Mengacu pada Vasile et al. (2024), operasi ini dinyatakan pada Persamaan (1). _Grayscale_ merupakan operasi titik sehingga tidak memerlukan persamaan ini:

| $I_{filter}(x,y)=\sum_{i=-k}^k \sum_{j=-k}^k I(x+i,y+j)\cdot K(i,j)$ | (1) |
| ------- | --- |

Keterangan:

1. _I<sub>filter</sub>(x, y)_ : Nilai intensitas piksel hasil pemfilteran pada koordinat spasial (x, y).
2. _I(x + i, y + j)_ : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (x + i, y + j).
3. _K(i, j)_ : Koefisien bobot matriks _kernel_ konvolusi pada posisi relatif (i, j).
4. _k_ : Radius spasial matriks _kernel_ (pada matriks _kernel_ berukuran 3 × 3, bernilai k = 1).
5. _i, j_ : Indeks koordinat pergeseran spasial _kernel_ secara vertikal dan horizontal.

Bentuk ini merupakan korelasi silang yang lazim disebut konvolusi pada pengolahan citra. Untuk _kernel_ simetris seperti _Gaussian_, hasilnya identik dengan konvolusi sejati. Pada _Sobel_, perbedaannya hanya pada tanda gradien, sehingga magnitudo gradien tidak berubah.

### 6.1.2. Rasio Percepatan (Speedup)

Rasio percepatan (_speedup_) mengukur seberapa besar komputasi paralel mempercepat penyelesaian dibandingkan eksekusi serial. Mengacu pada Pacheco dan Malensek (2022), _speedup_ (_S_) dirumuskan pada Persamaan (2):

| $S=\frac{T_{serial}}{T_{paralel}}$ | (2) |
| ------- | --- |

Keterangan:

1. _S_ : Nilai rasio percepatan (_speedup_) komputasi (rasio tanpa satuan).
2. _T<sub>serial</sub>_ : Waktu eksekusi pemrosesan citra pada skrip serial murni (tanpa inisialisasi pool proses) pada satu inti prosesor (detik).
3. _T<sub>paralel</sub>_ : Waktu eksekusi pemrosesan citra secara paralel pada alokasi _P_ proses pekerja (detik).

_T_<sub>serial</sub> dan _T_<sub>paralel</sub> diukur secara selang-seling (_interleaved_) pada setiap repetisi, sehingga setiap nilai _S_ dihitung dari pasangan pengukuran serial dan paralel yang berdekatan. Hasil dilaporkan sebagai median, rerata, dan simpangan baku dari 30 repetisi.

### 6.1.3. Efisiensi Paralel (Efficiency)

Efisiensi mengukur persentase pemanfaatan daya komputasi tiap proses pekerja (Pacheco dan Malensek, 2022), sebagaimana dirumuskan pada Persamaan (3):

| $E=\left(\frac{S}{P}\right) \times 100\%$ | (3) |
| ------- | --- |

Keterangan:

1. _E_ : Persentase efisiensi komputasi paralel (%).
2. _S_ : Nilai rasio percepatan (_speedup_) yang diperoleh dari Persamaan (2).
3. _P_ : Jumlah proses pekerja (_worker processes_) yang dialokasikan dalam eksekusi paralel.

### 6.1.4. Beban Tambahan Paralel (Parallel Overhead)

Beban tambahan (_overhead_) paralel adalah selisih antara waktu paralel aktual dan waktu paralel ideal _T_<sub>serial</sub>/_P_. Mengacu pada Pacheco dan Malensek (2022), _T_<sub>overhead</sub> dirumuskan pada Persamaan (4):

| $T_{overhead}=T_{paralel}-\frac{T_{serial}}{P}$ | (4) |
| ------- | --- |

Keterangan:

1. _T<sub>overhead</sub>_ : Durasi beban tambahan sistem paralel akibat komunikasi antar-proses (IPC), serialisasi data NumPy (_pickling_), penyalinan baris batas (_boundary halo_), serta rekonstruksi matriks (detik).
2. _T<sub>paralel</sub>_ : Waktu eksekusi paralel aktual yang terukur (detik).
3. _T<sub>serial</sub> / P_ : Waktu eksekusi paralel ideal secara teoritis tanpa penalti koordinasi sistem (detik).
4. _T<sub>serial</sub>_ : Waktu eksekusi serial baseline (detik).
5. _P_ : Jumlah proses pekerja yang dialokasikan.

### 6.1.5. Batas Skalabilitas Berdasarkan Hukum Amdahl

Hukum Amdahl menyatakan batas percepatan teoretis suatu program berdasarkan fraksi yang tidak dapat diparalelkan (Pacheco dan Malensek, 2022), sebagaimana dinyatakan pada Persamaan (5):

| $S_{Amdahl}=\frac{1}{(1-f)+\frac{f}{P}}$ | (5) |
| ------- | --- |

Keterangan:

1. _S<sub>Amdahl</sub>_ : Percepatan teoretis pada _P_ proses menurut Hukum Amdahl; untuk _P_ → ∞ nilainya mendekati 1/(1 − _f_).
2. _f_ : Fraksi beban kerja yang dapat diparalelkan (0 ≤ _f_ ≤ 1).
3. _(1 - f)_ : Fraksi efektif yang tidak mengalami percepatan, mencakup bagian sekuensial program, beban koordinasi paralel (partisi, IPC, baris batas, rekonstruksi), dan pengaruh arsitektur inti yang tidak setara.
4. _P_ : Jumlah proses pekerja atau inti prosesor (_core_) yang dialokasikan.

Hukum Amdahl mengasumsikan inti prosesor yang setara. Prosesor uji memiliki arsitektur hibrida (empat _performance core_ dan empat _efficient core_), sehingga kurva Amdahl diperlakukan sebagai pendekatan teoretis. Nilai _f_ diestimasi per filter dengan metode kuadrat terkecil (_least squares_) pada rasio percepatan Skenario B untuk _P_ = 2, 4, dan 8, disertai selang kepercayaan 95% hasil _bootstrap_. Kecocokan model diperiksa dengan fraksi serial eksperimental Karp–Flatt (Karp dan Flatt, 1990), dinyatakan pada Persamaan (6):

| $e = \frac{\frac{1}{S} - \frac{1}{P}}{1 - \frac{1}{P}}$ | (6) |
| ------- | --- |

dengan _e_ sebagai fraksi serial eksperimental. Nilai _e_ yang konstan terhadap _P_ menunjukkan kesesuaian dengan Hukum Amdahl, sedangkan _e_ yang meningkat menunjukkan beban koordinasi yang membesar seiring _P_. Estimasi ini bersifat deskriptif atas data pengukuran dan bukan validasi independen.

# 7. Metode Penelitian

Metode penelitian ini menggunakan pendekatan eksperimen faktorial terkontrol (_controlled factorial experimental research_) untuk mengevaluasi kinerja dan skalabilitas komputasi paralel secara empiris. Pengujian membandingkan eksekusi serial tunggal (_baseline_) dengan eksekusi paralel berbasis partisi spasial pada prosesor _multi-core_.

## 7.1. Tahapan Penelitian

Penelitian dilaksanakan dalam enam tahap sebagai berikut:

1. Studi literatur, yaitu pengkajian teori komputasi paralel, mekanisme pengalamatan memori larik _NumPy_, arsitektur konkurensi modul Python _multiprocessing_, batasan _Global Interpreter Lock_ (GIL), serta formulasi matematis filter spasial citra (_Grayscale_, _Gaussian Blur_, dan _Sobel_).
2. Perancangan dan pengkodean algoritma, yaitu pengembangan dua versi perangkat lunak pengujian: skrip serial sebagai _baseline_ dan skrip paralel yang memadukan fungsi partisi matriks horizontal dengan distribusi tugas melalui _multiprocessing.Pool()_.
3. Penyiapan dataset citra uji, yaitu standardisasi citra acuan master fotografi beresolusi tinggi 4K (4096 × 4096 piksel) yang bersumber dari repositori fotografi terbuka (Aesthetic-4K). Citra acuan master tersebut dipotong secara terpusat (_center-crop_) tanpa kompresi ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel. Waktu eksekusi ketiga filter bersifat tidak bergantung pada isi citra (_data-independent_) karena operasi konvolusi matriks tidak memiliki percabangan kondisional berbasis nilai piksel, sehingga satu citra acuan master memadai untuk meniadakan variabilitas tekstur dan mengisolasi variabilitas sistem komputasi (penjadwalan sistem operasi, fluktuasi termal, dan alokasi inti heterogen). Seluruh 30 sampel citra multiresolusi awal tetap diarsipkan sebagai opsi dataset alternatif.
4. Eksekusi eksperimen terkontrol, yaitu pengujian algoritma pada sistem operasi tanpa aplikasi latar belakang yang membebani CPU. Setiap kombinasi perlakuan pengujian dieksekusi sebanyak 30 kali repetisi terkontrol secara selang-seling (_interleaved_) antara pengukuran serial dan paralel pada masing-masing tingkatan resolusi guna memperoleh estimasi parameter statistik yang stabil dan representatif (median, rerata, simpangan baku, dan selang kepercayaan 95%). Pengukuran durasi komputasi murni memanfaatkan arsitektur _pre-warmed pool_ untuk meniadakan penalti inisialisasi proses (_cold spawn_) pada Windows, serta dilengkapi jeda pendinginan termal CPU (_cool-down buffer_) antar-filter guna meminimalkan pelambatan termal (_thermal throttling_). Pergeseran waktu eksekusi antar-blok pengujian (di mana Skenario A dijalankan pertama dan memiliki baseline serial sedikit lebih lambat) dicatat sebagai batasan pengujian.
5. Pencatatan parameter kinerja, yaitu pengukuran waktu komputasi murni dengan _time.perf_counter()_, pemantauan utilisasi CPU diukur pada proses utama menggunakan modul _psutil_ sebagai estimasi tren beban kerja sistem secara keseluruhan, serta penghitungan _speedup_, efisiensi, dan _overhead_ paralel.
6. Analisis skalabilitas dan penarikan kesimpulan, yaitu penyajian data dalam kurva komparatif, evaluasi kurva percepatan terhadap batas teoretis Hukum Amdahl, serta penarikan kesimpulan tentang efektivitas komputasi paralel pada berbagai ukuran data dan kompleksitas filter.

Bagan alir pelaksanaan tahapan penelitian secara menyeluruh disajikan pada Gambar 2.

![Gambar 2. Diagram Alir Proses Penelitian](results/plots/gambar_2_bagan_alir_penelitian.png)

Gambar 2. Diagram Alir Proses Penelitian

## 7.2. Desain Eksperimen dan Skenario Pengujian

Setiap operasi filter diuji pada variasi ukuran data dan alokasi proses kerja yang dirinci dalam tiga skenario berikut.

### 7.2.1. Skenario A: Variasi Dimensi Citra

Alokasi proses kerja dikunci pada empat proses (_Pool(processes=4)_). Resolusi citra dinaikkan bertahap dengan sisi berlipat dua pada setiap langkah, dari 512 × 512 hingga 4096 × 4096 piksel, pada ketiga filter (_Grayscale_, _Gaussian Blur_, dan _Sobel_). Skenario ini menganalisis pengaruh ukuran matriks terhadap rasio _speedup_ pada tiap karakteristik operasi. Matriks pengujian dirangkum pada Tabel 1.

Tabel 1. Matriks Pengujian Skenario A (Variasi Dimensi Citra)

| Kode Uji | Resolusi Citra (Piksel) | Total Elemen Matriks | Jenis Operasi yang Diuji              | Alokasi Proses | Replikasi Pengujian                 |
| -------- | ----------------------- | -------------------- | ------------------------------------- | -------------- | ----------------------------------- |
| A1       | 512 × 512               | 262.144              | _Grayscale_, _Gaussian Blur_, _Sobel_ | 4 Proses       | 1 Citra Acuan Master (30x Repetisi) |
| A2       | 1024 × 1024             | 1.048.576            | _Grayscale_, _Gaussian Blur_, _Sobel_ | 4 Proses       | 1 Citra Acuan Master (30x Repetisi) |
| A3       | 2048 × 2048             | 4.194.304            | _Grayscale_, _Gaussian Blur_, _Sobel_ | 4 Proses       | 1 Citra Acuan Master (30x Repetisi) |
| A4       | 4096 × 4096             | 16.777.216           | _Grayscale_, _Gaussian Blur_, _Sobel_ | 4 Proses       | 1 Citra Acuan Master (30x Repetisi) |

### 7.2.2. Skenario B: Variasi Alokasi Proses Kerja

Dimensi citra dikunci pada 2048 × 2048 piksel. Alokasi proses kerja divariasikan dari satu proses (_baseline_ serial), dua proses, empat proses, hingga delapan proses pada ketiga filter. Kondisi satu proses (B0) dijalankan sebagai kontrol serial terhadap serial (_A/A control_), yaitu dua pengukuran serial independen, untuk memperkirakan variasi alami sistem. Skenario ini memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan menguji apakah operasi berbeban berat (_Sobel_) lebih mendekati percepatan linear daripada operasi ringan (_Grayscale_). Matriks pengujian disajikan pada Tabel 2.

Tabel 2. Matriks Pengujian Skenario B

| Kode Uji | Alokasi Proses Kerja | Mode Eksekusi                 | Jenis Operasi yang Diuji              | Dimensi Citra | Replikasi Pengujian                 |
| -------- | -------------------- | ----------------------------- | ------------------------------------- | ------------- | ----------------------------------- |
| B0       | 1 Proses             | Mode Serial (Kontrol A/A)     | _Grayscale_, _Gaussian Blur_, _Sobel_ | 2048 × 2048   | 1 Citra Acuan Master (30x Repetisi) |
| B1       | 2 Proses             | Mode Paralel (_Dual-Process_) | _Grayscale_, _Gaussian Blur_, _Sobel_ | 2048 × 2048   | 1 Citra Acuan Master (30x Repetisi) |
| B2       | 4 Proses             | Mode Paralel (_Quad-Process_) | _Grayscale_, _Gaussian Blur_, _Sobel_ | 2048 × 2048   | 1 Citra Acuan Master (30x Repetisi) |
| B3       | 8 Proses             | Mode Paralel (_Octa-Process_) | _Grayscale_, _Gaussian Blur_, _Sobel_ | 2048 × 2048   | 1 Citra Acuan Master (30x Repetisi) |

### 7.2.3. Skenario C: Variasi Jenis Operasi Filter

Skenario C dijalankan sebagai blok pengujian terpisah pada resolusi 2048 × 2048 piksel dengan empat proses, dan hasilnya dibandingkan dengan titik uji A3 dan B2 untuk memeriksa keterulangan. Skenario C membandingkan kompleksitas matematis tiap algoritma dengan efisiensi, beban tambahan (_overhead_), dan utilisasi CPU yang dihasilkannya. Ketiga tingkat beban algoritma dirinci pada Tabel 3.

Tabel 3. Klasifikasi Tingkat Kompleksitas Operasi Filter Citra

| Kode | Jenis Operasi Filter | Karakteristik Perhitungan Matematis                             | Tingkat Kompleksitas | Kondisi Titik Uji Komparasi      |
| ---- | -------------------- | --------------------------------------------------------------- | -------------------- | -------------------------------- |
| C1   | Konversi _Grayscale_ | Operasi Titik Matematis Tunggal (1 × 1) per piksel              | Ringan               | Resolusi 2048 px (1 vs 4 proses) |
| C2   | _Gaussian Blur_      | Konvolusi Matriks Ketetanggaan Kernel (3 × 3)                   | Moderat              | Resolusi 2048 px (1 vs 4 proses) |
| C3   | Deteksi Tepi _Sobel_ | Gradien Turunan Parsial Ganda (G<sub>x</sub> dan G<sub>y</sub>) | Berat                | Resolusi 2048 px (1 vs 4 proses) |

## 7.3. Parameter Kinerja yang Diuji

Efektivitas komputasi paralel dievaluasi melalui lima parameter kinerja pada Tabel 4. Setiap parameter dilaporkan sebagai median, rerata ($\bar{x}$), simpangan baku ($s$), dan selang kepercayaan 95% dari 30 kali repetisi pada masing-masing kombinasi perlakuan.

Tabel 4. Parameter Kinerja Pengujian Komputasi Paralel

| Nama Parameter    | Notasi                 | Definisi Operasional                                                                              | Satuan                     |
| ----------------- | ---------------------- | ------------------------------------------------------------------------------------------------- | -------------------------- |
| Waktu Eksekusi    | T                      | Durasi waktu yang dibutuhkan untuk menyelesaikan kalkulasi filter citra pada pengujian terkontrol | Detik (s) / Milidetik (ms) |
| Rasio Percepatan  | S                      | Perbandingan kelipatan kecepatan antara waktu eksekusi serial terhadap waktu paralel              | Rasio (Tanpa satuan)       |
| Efisiensi Paralel | E                      | Persentase daya pemanfaatan inti prosesor terhadap percepatan yang diraih                         | Persen (%)                 |
| Utilisasi CPU     | %CPU                   | Rata-rata beban pemakaian daya komputasi di seluruh inti prosesor selama eksekusi                 | Persen (%)                 |
| Beban Tambahan    | _T<sub>overhead</sub>_ | Selisih waktu keterlambatan akibat partisi data di memori dan komunikasi proses                   | Detik (s)                  |

# DAFTAR PUSTAKA

Aesthetic-4K Dataset. (2025). High-resolution uncompressed image repository for visual computing research. Creative Commons CC-BY 4.0.

Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). Multi-directional Sobel operator kernel on GPUs. _arXiv preprint arXiv:2305.00515_. https://doi.org/10.48550/arXiv.2305.00515

Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. _JICDA: Journal of Informatics, Computer Science, Data Science and Artificial Intelligence_, 3(2), 55–64. https://doi.org/10.51505/jicda.2025.3202

Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. _Communications of the ACM_, 33(5), 539–543. https://doi.org/10.1145/78607.78614

Pacheco, P. S., & Malensek, M. (2022). _An introduction to parallel programming_ (2nd ed.). Morgan Kaufmann.

Tanenbaum, A. S., & Bos, H. (2022). _Modern operating systems_ (5th ed.). Pearson.

Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. _Journal of Imaging_, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully generated polished proposal to: {output_path}")

if __name__ == "__main__":
    generate_polished_proposal_md()
