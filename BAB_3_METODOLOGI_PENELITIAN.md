# BAB 3 METODOLOGI PENELITIAN


## 3.1 Tahapan Penelitian

Penelitian ini dilaksanakan melalui enam tahapan terstruktur guna memastikan proses evaluasi komparasi kinerja komputasi paralel dan serial dapat terukur secara objektif, terkendali, dan dapat direplikasi (reproducible). Tahapan penelitian tersebut mencakup:

* Studi literatur: Mengkaji teori komputasi paralel (data parallelism) (Pacheco & Malensek, 2022), manajemen memori larik NumPy berbasis baris (row-major order / C-contiguous) (Harris et al., 2020), arsitektur konkurensi modul Python multiprocessing, batasan Global Interpreter Lock (CPython GIL) (Python Software Foundation, n.d.-a), arsitektur prosesor hibrida heterogen (Intel Corporation, 2023; Tanenbaum & Bos, 2022), serta formulasi matematis algoritma filter spasial citra (Grayscale ITU-R BT.601, Gaussian Blur 3×3, dan Sobel 3×3).
* Perancangan dan pengkodean algoritma: Mengembangkan dua varian sistem komputasi pengujian, yaitu skrip serial satu inti prosesor sebagai acuan pembanding (baseline) dan skrip paralel yang mengintegrasikan pemotongan blok baris horizontal dengan penambahan baris batas (boundary halo), distribusi tugas via multiprocessing.Pool, pemangkasan baris batas (halo stripping), dan rekonstruksi citra utuh melalui numpy.vstack.
* Pengumpulan dan standardisasi data citra master: Menyiapkan citra acuan master beresolusi tinggi 4K (4096 × 4096 piksel) berkas img_01.png dengan kode biner SHA-256 f211af0f8cbd2cd9ebb5431d9eabf29f274fc7686f9cfbee544cb18fe6314c6c dari repositori terbuka Aesthetic-4K (Aesthetic-4K Dataset, 2025) berlisensi Creative Commons Attribution 4.0 International (CC-BY 4.0), yang dipotong secara terpusat (center-crop) tanpa resampling ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.
* Eksekusi eksperimen terkontrol: Menjalankan pengujian kinerja pada lingkungan sistem operasi terkendali tanpa interferensi aplikasi latar belakang non-esensial. Sebanyak 810 pasangan perlakuan dieksekusi secara berselang-seling (interleaved execution) antara pengukuran serial dan paralel (terdiri atas 90 pasangan kontrol A/A dan 720 pasangan komparasi paralel-serial) guna meredam fluktuasi termal dan beban penjadwalan sistem operasi.
* Pencatatan parameter kinerja: Merekam durasi waktu komputasi menggunakan fungsi pewaktu presisi tinggi time.perf_counter(), memantau persentase beban CPU melalui thread daemon latar belakang modul psutil, serta menghitung metrik rasio percepatan (speedup S), efisiensi paralel (E), dan beban tambahan (overhead) paralel (T_overhead) ke dalam berkas log telemetri CSV.
* Analisis skalabilitas dan pencocokan model: Menganalisis karakteristik skalabilitas melalui statistik non-parametrik deskriptif (median dan IQR), mencocokkan kurva percepatan empiris terhadap batas teoretis Hukum Amdahl (Amdahl, 1967), mengevaluasi fraksi serial efektif melalui metrik Karp–Flatt (Karp & Flatt, 1990), serta memvalidasi kebenaran numerik luaran melalui verifikasi bit-identik (Δmax = 0).
Bagan alir pelaksanaan tahapan penelitian secara menyeluruh disajikan pada Gambar 3.1. Bagan alir ini merangkum urutan logis dari keenam tahapan penelitian, mulai dari inisialisasi studi pustaka dan penyiapan data citra master, pelaksanaan pengujian berulang 30 kali secara berselang-seling, verifikasi bit-identik dengan percabangan koreksi algoritma, pencatatan telemetri kinerja, hingga analisis kuantitatif data dan pemodelan skalabilitas.


> **[Area Gambar 3.1: Diagram Alir Tahapan Penelitian]
(Diagram alir sedang dalam proses penyempurnaan format visual beresolusi tinggi 300 DPI untuk disematkan pada area ini)**

Gambar 3.1 Diagram Alir Tahapan Penelitian


## 3.2 Pengumpulan dan Standardisasi Data Citra Master

Data citra yang digunakan dalam penelitian ini bersumber dari repositori fotografi terbuka beresolusi tinggi Aesthetic-4K (Aesthetic-4K Dataset, 2025) yang didistribusikan di bawah lisensi resmi Creative Commons Attribution 4.0 International (CC-BY 4.0). Citra master yang dipilih adalah berkas img_01.png berformat asli RGB 24-bit tanpa kompresi (uncompressed PNG) dengan dimensi asli 4096 × 4096 piksel, bebas dari artefak distorsi kompresi lossy JPEG, serta diverifikasi melalui nilai hash SHA-256: f211af0f8cbd2cd9ebb5431d9eabf29f274fc7686f9cfbee544cb18fe6314c6c guna mendukung keterulangan (reproducibility) data masukan.

Untuk menghasilkan variasi dimensi data yang seragam dan konsisten secara proporsi visual, citra master 4K (4096 × 4096 piksel) diproses melalui pemotongan terpusat (center-crop) tanpa proses resampling atau interpolasi piksel. Pemotongan terpusat dilakukan secara bertingkat dengan rasio penggandaan panjang sisi dua kali lipat pada setiap tingkatan, menghasilkan empat berkas citra masukan berdimensi bujur sangkar, yaitu: 512 × 512 piksel (volume memori mentah sekitar 768 KB), 1024 × 1024 piksel (volume memori mentah sekitar 3 MB), 2048 × 2048 piksel (volume memori mentah sekitar 12 MB), dan 4096 × 4096 piksel (volume memori mentah sekitar 48 MB data RGB tak terkompresi bertipe data uint8).

Dalam evaluasi komputasi paralel visi komputer, terdapat pertimbangan metodologis mendasar mengenai apakah pengujian memerlukan variasi banyak berkas gambar ataukah cukup menggunakan satu citra acuan master yang distandardisasi. Pada penelitian ini, diputuskan secara ilmiah untuk menggunakan satu citra acuan master terstandardisasi berdasarkan karakteristik intrinsik algoritma filter spasial yang dievaluasi. Operasi konvolusi matriks spasial (Gaussian Blur 3×3 dan Sobel 3×3) serta konversi derajat keabuan (Grayscale ITU-R BT.601; International Telecommunication Union, 2011) memiliki karakteristik komputasi yang bebas dari isi visual citra (data-independent computation). Pada seluruh algoritma tersebut, setiap piksel diproses melalui rantai instruksi aritmetika perkalian dan penjumlahan koefisien kernel yang seragam tanpa adanya percabangan kondisional (conditional branching / if-else) yang dipicu oleh variasi nilai intensitas piksel. Akibatnya, beban siklus instruksi ALU prosesor per piksel bernilai konstan, terlepas dari tekstur visual citra yang diproses. Penggunaan satu citra acuan master terstandardisasi mengeliminasi variabilitas tekstur visual antar-berkas sehingga seluruh variabilitas waktu eksekusi yang terukur mencerminkan perilaku sistem komputasi (interferensi penjadwalan OS, latensi komunikasi pipa IPC antar-proses, dan dinamika arsitektur inti hibrida). Sebagai batasan eksperimental, kesimpulan penelitian ini berlaku spesifik untuk jenis filter spasial dengan beban kerja bebas isi, rentang resolusi hingga 4K, dan platform perangkat keras yang dievaluasi.


## 3.3 Alat dan Bahan Penelitian

Pelaksanaan eksperimen komputasi paralel memerlukan dukungan perangkat keras, perangkat lunak, dan instrumen pengukuran yang terdefinisi secara terukur untuk mendukung keterulangan (reproducibility) pengujian.


### 3.3.1 Perangkat Keras dan Kondisi Operasional

Eksperimen komputasi paralel dilaksanakan pada satu unit komputer jinjing (laptop) dengan prosesor heterogen modern Intel Core i5-13420H generasi ke-13 (nama sandi Raptor Lake; Intel Corporation, 2023). Prosesor ini memiliki 8 inti fisik (physical cores) yang terdiri atas 4 Performance-Cores (P-Cores, arsitektur Golden Cove refresh) dengan frekuensi dasar 2,1 GHz dan dorongan turbo hingga 4,6 GHz yang mendukung Simultaneous Multithreading (SMT / Hyper-Threading 8 threads), serta 4 Efficient-Cores (E-Cores, arsitektur Gracemont) dengan frekuensi dasar 1,5 GHz dan turbo hingga 3,4 GHz tanpa SMT (4 threads), menghasilkan kapasitas pemrosesan total 12 threads. Subsistem memori cache prosesor terdiri atas L1 Cache (80 KB per P-Core dan 96 KB per E-Core), L2 Cache (1,25 MB per P-Core privat dan 2 MB terbagi per kluster empat E-Core), serta 12 MB L3 Intel Smart Cache yang terbagi bersama (shared cache) untuk seluruh inti prosesor.

Sistem didukung oleh memori utama (RAM) berkapasitas 16 GB DDR5 dengan frekuensi transfer 5200 MT/s berkonfigurasi dual-channel, serta media penyimpanan Solid State Drive (SSD) M.2 NVMe PCIe 4.0 berkapasitas 512 GB. Untuk menjaga konsistensi kinerja termal dan kelistrikan selama proses pengujian:

* Perangkat keras dihubungkan secara kontinu ke adaptor catu daya listrik AC (pengisi daya 135 W) guna meniadakan penurunan frekuensi kerja prosesor yang dipicu mekanisme penghematan daya baterai (battery power throttling).
* Profil daya pada sistem operasi Windows 11 dikunci pada skema Best Performance.
* Seluruh pengujian dijalankan di dalam ruangan kerja terkondisi pada suhu kamar stabil (~24 °C) dengan pemantauan suhu awal prosesor sebelum pengujian dimulai.
Tabel 3.1 Spesifikasi Perangkat Keras dan Kondisi Operasional Pengujian



| Komponen Perangkat Keras | Spesifikasi Teknis | Kondisi Operasional Pengujian |
| --- | --- | --- |
| Prosesor (CPU) | Intel Core i5-13420H (13th Gen Raptor Lake), 8 Inti Fisik: 4 P-Cores (arsitektur Golden Cove refresh, frekuensi dasar 2,1 GHz / turbo 4,6 GHz, SMT 8 threads) + 4 E-Cores (arsitektur Gracemont, frekuensi dasar 1,5 GHz / turbo 3,4 GHz, 4 threads), total kapasitas eksekusi 12 threads. | Dijalankan pada skema daya Windows Best Performance; laptop terhubung kontinu ke adaptor catu daya listrik AC eksternal; pemantauan suhu awal sebelum pengujian dimulai. |
| Memori Cache CPU | L1: 80 KB per P-Core, 96 KB per E-Core;<br>L2: 1,25 MB per P-Core (privat), 2 MB terbagi per kluster empat E-Core;<br>L3: 12 MB Intel Smart Cache terbagi bersama (shared). | Berbagi pakai dinamis untuk seluruh proses pekerja; pengujian mengevaluasi efek pelonjakan cache hit pada matriks citra 512 × 512 piksel dan degradasi latensi memori pada resolusi 4096 × 4096 piksel. |
| Memori Utama (RAM) | 16 GB DDR5 5200 MT/s Dual-Channel | Kapasitas memadai untuk menampung seluruh larik citra masukan dan luaran secara simultan tanpa terjadinya penukaran halaman memori (memory swapping) ke media penyimpanan sekunder. |
| Media Penyimpanan | 512 GB SSD M.2 NVMe PCIe 4.0 | Digunakan khusus untuk pembacaan berkas citra awal dan penyimpanan hasil luaran akhir; operasi I/O penyimpanan diisolasi di luar rentang pewaktuan komputasi paralel. |
| Catu Daya Listrik | Adaptor AC 135 W eksternal | Terhubung secara kontinu selama eksperimen berlangsung guna mencegah penurunan frekuensi kerja prosesor yang dipicu mekanisme penghematan daya (battery power throttling). |
| Suhu Lingkungan | Ruang kerja terkondisi (~24 °C) | Suhu ruangan dijaga stabil guna meminimalkan fluktuasi termal lingkungan selama 810 pasangan eksekusi pengujian. |



### 3.3.2 Perangkat Lunak dan Pustaka Komputasi

Lingkungan perangkat lunak yang digunakan dalam penelitian ini meliputi sistem operasi Windows 11 Home 64-bit (Build 22631) sebagai platform eksekusi sistem. Bahasa pemrograman yang digunakan adalah Python 3.14.3 (CPython 64-bit; Python Software Foundation, n.d.-b). Komputasi matriks citra bertumpu pada pustaka NumPy versi 2.5.4 (Harris et al., 2020) yang mengelola representasi data larik multidimensi dalam format row-major (C-contiguous memory layout).

Pustaka OpenCV versi 5.0.0.93 (Bradski, 2000) digunakan secara terbatas hanya untuk operasi pembacaan dan penyimpanan berkas citra (file I/O). Guna mencegah interferensi akselerasi internal OpenCV yang dapat mengaburkan evaluasi multiprocessing, utas komputasi internal OpenCV dinonaktifkan secara eksplisit menggunakan perintah cv2.setNumThreads(1). Modul bawaan Python multiprocessing digunakan sebagai pengendali orkestrasi paralel berbasis kolam proses pekerja (Pool). Pustaka psutil versi 7.2.2 digunakan untuk merekam persentase utilisasi CPU sistem. Pustaka SciPy versi 1.18.1 (Virtanen et al., 2020) digunakan untuk melakukan regresi non-linier kuadrat terkecil (least squares curve fitting) dan uji hipotesis statistik, sedangkan Matplotlib versi 3.11.2 (Hunter, 2007) digunakan untuk menghasilkan grafik komparasi data kinerja.

Tabel 3.2 Spesifikasi Perangkat Lunak dan Pustaka Komputasi



| Perangkat Lunak / Pustaka | Versi Rilis | Fungsi dan Peran dalam Penelitian |
| --- | --- | --- |
| Windows 11 Home 64-bit | Build 22631 | Sistem operasi induk; manajemen penjadwalan proses bekerja sama dengan mekanisme umpan balik perangkat keras (hardware feedback mechanism) Intel Thread Director. |
| Python (CPython) | 3.14.3 | Platform bahasa pemrograman utama untuk implementasi mesin komputasi serial dan paralel (Python Software Foundation, n.d.-b). |
| NumPy | 2.5.4 | Pengelolaan struktur larik multidimensi berbasis row-major (C-contiguous), dekomposisi partisi blok baris horizontal, dan rekonstruksi citra utuh via numpy.vstack (Harris et al., 2020). |
| OpenCV (opencv-python) | 5.0.0.93 | Operasi pembacaan dan penulisan berkas citra masukan/luaran (I/O); utas komputasi internal dinonaktifkan secara permanen melalui cv2.setNumThreads(1) (Bradski, 2000). |
| Multiprocessing | Bawaan Python | Orkestrasi proses paralel independen berbasis metode spawn, alokasi kolam pekerja (Pool), transmisi data payload via pipa IPC, dan sinkronisasi tugas. |
| Psutil | 7.2.2 | Perekaman persentase beban utilisasi CPU sistem melalui thread daemon latar belakang pemantau mandiri selama siklus eksekusi berlangsung. |
| SciPy | 1.18.1 | Eksekusi regresi non-linier kuadrat terkecil untuk pencocokan kurva Hukum Amdahl serta pengujian signifikansi statistik (Kruskal–Wallis dan Mann–Whitney U) (Virtanen et al., 2020). |
| Matplotlib | 3.11.2 | Pustaka grafis untuk memvisualisasikan kurva performa komparasi waktu, speedup, efisiensi, dan overhead (Hunter, 2007). |



### 3.3.3 Alat Ukur dan Instrumentasi Kinerja

Pengukuran durasi waktu eksekusi komputasi dilakukan menggunakan fungsi pewaktu presisi tinggi berbasis monotonik time.perf_counter() dari pustaka standar Python. Pewaktu ini memiliki resolusi tingkat nanodetik dan bersifat monotonik, artinya nilai pewaktu selalu bertambah secara linier dan tidak pernah terdistorsi oleh penyesuaian jam sistem operasi (system clock drift) maupun sinkronisasi waktu jaringan (NTP). Pencatatan stempel waktu awal (start timestamp) dan stempel waktu akhir (stop timestamp) dilakukan hanya pada blok kalkulasi pemrosesan citra, sehingga waktu pembacaan citra dari penyimpanan (disk reading) dan waktu penulisan kembali hasil ke media penyimpanan (disk writing) diisolasi dari pengukuran kinerja komputasi.

Instrumentasi utilisasi kapasitas prosesor dicatat menggunakan kelas pemantau CPUMonitor yang berjalan pada thread daemon latar belakang independen dengan interval percontohan 20 milidetik (0,02 detik). Sebelum siklus komputasi dimulai, dijalankan satu pemanggilan awal psutil.cpu_percent(interval=None, percpu=True) untuk mereset dan memanaskan jendela pencatatan psutil, sehingga sampel yang terkumpul merefleksikan aktivitas prosesor selama eksekusi. Sebagai batasan metodologis, pembacaan nilai ini merefleksikan utilisasi CPU sistem secara keseluruhan dari sudut pandang proses utama, sehingga pada durasi eksekusi yang sangat singkat (di bawah 100 milidetik pada citra resolusi kecil), pembacaan utilisasi CPU cenderung merefleksikan artefak jendela sampel (sampling window artifact) dan tidak merefleksikan seluruh aktivitas proses pekerja secara instan. Oleh karena itu, data utilisasi CPU diperlakukan sebagai indikator tren beban relatif dan bukan sebagai penentu utama efisiensi komputasi.


## 3.4 Desain Eksperimen

Penelitian ini menerapkan desain eksperimen faktorial parsial per skenario (partial factorial experimental design) dengan variasi satu faktor per blok pengujian untuk menganalisis pengaruh dari variabel ukuran data matriks, alokasi unit proses kerja, dan tingkat kompleksitas algoritma filter spasial. Identifikasi variabel penelitian diklasifikasikan sebagai berikut:
1. Variabel bebas (independent variables): Resolusi spasial citra masukan (512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel), alokasi jumlah proses pekerja (P ∈ {1, 2, 4, 8}), serta jenis algoritma filter spasial citra (Grayscale ITU-R BT.601, Gaussian Blur 3×3, dan Sobel 3×3).
2. Variabel terikat (dependent variables): Waktu eksekusi serial (T_serial) dan waktu eksekusi paralel (T_paralel) dalam detik, rasio percepatan komputasi (speedup S), persentase efisiensi paralel (E), durasi beban tambahan paralel (parallel overhead T_overhead) dalam detik, persentase utilisasi kapasitas CPU, serta status integritas keidentikan bit piksel (Δmax).
3. Variabel kontrol (controlled variables): Citra acuan master tunggal terstandardisasi (Aesthetic-4K img_01.png terpotong terpusat), spesifikasi perangkat keras dan sistem operasi yang seragam, metode peluncuran proses pekerja spawn, ukuran partisi tugas chunksize = 1, penanganan baris batas ketetanggaan (boundary halo k = 1 dengan pemangkasan halo stripping per pekerja), tipe data representasi matriks (uint8 masukan, konversi float64 untuk operasi konvolusi dan validasi bit-identik), penguncian utas tunggal OpenCV (cv2.setNumThreads(1)), ketiadaan pengikatan afinitas inti prosesor (no core affinity pinning), serta kondisi garbage collector bawaan interpreter.
4. Variabel tak terkendali (uncontrolled variables): Fluktuasi termal silikon mikroprosesor, interupsi periodik layanan sistem operasi Windows di latar belakang, serta mekanisme penempatan beban kerja dinamis antara P-Core dan E-Core oleh penjadwal perangkat keras Intel Thread Director.

Ruang lingkup pengujian dibagi ke dalam tiga blok skenario eksperimental yang saling melengkapi:
1. Skenario A (Variasi Dimensi Spasial Citra): Alokasi proses pekerja dikunci pada 4 pekerja (P = 4), sedangkan dimensi spasial citra dinaikkan secara bertahap dari 512 × 512 hingga 4096 × 4096 piksel pada ketiga filter. Skenario ini bertujuan memetakan bagaimana pertumbuhan volume data memengaruhi rasio speedup dan efisiensi pada masing-masing karakteristik operasi filter. Skenario ini mencakup 12 sel kondisi perlakuan (A1 s.d. A12).
2. Skenario B (Variasi Alokasi Proses Kerja): Dimensi spasial citra dikunci pada resolusi menengah 2048 × 2048 piksel, sedangkan alokasi proses kerja divariasikan untuk P ∈ {1, 2, 4, 8} pada ketiga filter. Alokasi P = 1 dijalankan sebagai instrumen kontrol dasar A/A (A/A control). Skenario ini bertujuan memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan mendiagnosis perilaku metrik Karp–Flatt untuk P ∈ {2, 4, 8}. Skenario ini mencakup 12 sel kondisi perlakuan (B1 s.d. B12).
3. Skenario C (Variasi Kompleksitas Algoritma Filter): Dijalankan pada resolusi 2048 × 2048 piksel dengan alokasi 4 proses pekerja (P = 4) untuk ketiga jenis filter. Skenario ini bertujuan mengevaluasi interaksi antara beban kalkulasi matematis per piksel terhadap beban tambahan (overhead) komunikasi IPC, sekaligus bertindak sebagai instrumen uji keterulangan (repeatability test) terhadap kondisi A3, A7, A11 pada Skenario A dan kondisi B3, B7, B11 pada Skenario B. Skenario ini mencakup 3 sel kondisi perlakuan (C1 s.d. C3).

Secara keseluruhan, matriks desain eksperimen mencakup 27 sel kondisi blok perlakuan (12 + 12 + 3). Matriks ini merepresentasikan 21 kombinasi parameter fisik unik (faktor filter, resolusi, dan alokasi pekerja), dengan 3 kombinasi perlakuan pada resolusi 2048 × 2048 piksel dan alokasi P = 4 direplikasi pada ketiga blok skenario. Setiap sel kondisi perlakuan diuji sebanyak 30 kali repetisi berpasangan secara berselang-seling, menghasilkan total 810 pasangan eksekusi pengujian eksperimental (mencakup 90 pasangan kontrol A/A serial-ke-serial dan 720 pasangan komparasi paralel-terhadap-serial). Rincian matriks desain eksperimen dan definisi operasional parameter kinerja masing-masing dirangkum pada Tabel 3.3 dan Tabel 3.4.

Tabel 3.3 Matriks Desain Eksperimen Pengujian Komputasi Paralel



| Blok Skenario | Kode Kondisi | Jenis Filter Spasial | Resolusi Citra (px) | Alokasi Pekerja (P) | Repetisi dan Peran Metodologis |
| --- | --- | --- | --- | --- | --- |
| Skenario A<br>(Dimensi Spasial) | A1 – A4 | Grayscale | 512, 1024,<br>2048, 4096 | 4 | 30 repetisi berpasangan; evaluasi pengaruh volume data matriks pada operasi titik (point-wise) berbeban komputasi ringan. |
| Skenario A<br>(Dimensi Spasial) | A5 – A8 | Gaussian Blur 3×3 | 512, 1024,<br>2048, 4096 | 4 | 30 repetisi berpasangan; evaluasi pengaruh volume data pada konvolusi 3 kanal RGB dengan beban transmisi memori besar. |
| Skenario A<br>(Dimensi Spasial) | A9 – A12 | Sobel 3×3 | 512, 1024,<br>2048, 4096 | 4 | 30 repetisi berpasangan; evaluasi pengaruh volume data pada konvolusi gradien ganda intensif komputasi matematis. |
| Skenario B<br>(Alokasi Pekerja) | B1 – B4 | Grayscale | 2048 × 2048 | 1, 2, 4, 8 | 30 repetisi berpasangan; P=1 (B1) sebagai kontrol A/A; P=2,4,8 (B2, B3, B4) untuk pemodelan Hukum Amdahl dan metrik Karp–Flatt. |
| Skenario B<br>(Alokasi Pekerja) | B5 – B8 | Gaussian Blur 3×3 | 2048 × 2048 | 1, 2, 4, 8 | 30 repetisi berpasangan; P=1 (B5) sebagai kontrol A/A; P=2,4,8 (B6, B7, B8) untuk pemodelan Hukum Amdahl dan metrik Karp–Flatt. |
| Skenario B<br>(Alokasi Pekerja) | B9 – B12 | Sobel 3×3 | 2048 × 2048 | 1, 2, 4, 8 | 30 repetisi berpasangan; P=1 (B9) sebagai kontrol A/A; P=2,4,8 (B10, B11, B12) untuk pemodelan Hukum Amdahl dan metrik Karp–Flatt. |
| Skenario C<br>(Kompleksitas) | C1 – C3 | Grayscale, Gaussian, Sobel | 2048 × 2048 | 4 | 30 repetisi berpasangan; komparasi hierarki kompleksitas filter serta instrumen uji keterulangan terhadap kondisi A3, A7, A11 dan B3, B7, B11. |


Tabel 3.4 Definisi Operasional Parameter Kinerja yang Diuji



| Parameter Kinerja | Simbol dan Satuan | Alat Ukur / Formulasi | Deskripsi Operasional |
| --- | --- | --- | --- |
| Waktu Eksekusi Serial | T_serial (detik) | time.perf_counter() pada eksekusi serial satu inti | Durasi pemrosesan citra pada satu inti prosesor tanpa pemanggilan modul multiprocessing; bertindak sebagai nilai acuan dasar (baseline). |
| Waktu Eksekusi Paralel | T_paralel (detik) | time.perf_counter() pada eksekusi paralel | Durasi eksekusi paralel murni sejak partisi blok baris, transmisi pipa IPC, kalkulasi oleh kolam pekerja, hingga rekonstruksi citra utuh via numpy.vstack. Pada P=1, merefleksikan eksekusi serial kedua independen. |
| Rasio Percepatan | S (nirdimensi) | S = T_serial / T_paralel<br>(Persamaan 2.2) | Kelipatan percepatan komputasi yang dihasilkan sistem paralel dibandingkan eksekusi serial pada pasangan iterasi yang berdekatan. |
| Efisiensi Paralel | E (%) | E = (S / P) × 100%<br>(Persamaan 2.3, P ∈ {2, 4, 8}) | Persentase pemanfaatan daya komputasi dari setiap unit proses pekerja paralel riil yang dialokasikan (dihitung khusus untuk P > 1). |
| Beban Tambahan Paralel | T_overhead (detik) | T_overhead = T_paralel - (T_serial / P)<br>(Persamaan 2.4, P ∈ {2, 4, 8}) | Durasi beban penalti sistem akibat latensi komunikasi pipa IPC, serialisasi objek NumPy (pickle), transmisi baris batas (halo), dan rekonstruksi matriks (dihitung untuk P > 1). |
| Utilisasi Kapasitas CPU | CPU (%) | CPUMonitor via psutil | Persentase beban kerja prosesor yang dicatat oleh thread daemon pemantau latar belakang sebagai indikator tren beban relatif sistem. |
| Integritas Citra Bit-Identik | Δmax (uint8) | Δmax = max |I_paralel - I_serial|<br>via float64 & np.array_equal | Selisih nilai intensitas piksel maksimum antara citra paralel dan serial yang dihitung pada presisi float64 untuk mencegah wraparound; kriteria kelulusan biner pada Δmax = 0. |



## 3.5 Prosedur Pengukuran dan Pengujian

Prosedur pengujian dirancang dengan protokol terstruktur guna mengendalikan variabel pengganggu (confounding factors) yang bersumber dari mekanisme internal interpreter Python, karakteristik termal prosesor, dan dinamika penjadwalan sistem operasi.


### 3.5.1 Protokol Pemanasan Awal (Pre-Warming Worker Pool)

Pada sistem operasi Windows, modul multiprocessing menggunakan metode inisialisasi proses spawn (Python Software Foundation, n.d.-b). Metode ini meluncurkan interpreter Python baru dari awal untuk setiap proses pekerja, yang membutuhkan alokasi memori dan waktu inisialisasi awal (cold spawn penalty berkisar ~0,1 hingga ~0,5 detik per proses). Apabila inisialisasi proses pekerja dilakukan di dalam blok pengukuran waktu komputasi, durasi peluncuran proses baru mendominasi dan mendistorsi waktu eksekusi paralel yang sebenarnya. Untuk mengeliminasi distorsi tersebut, diterapkan protokol pemanasan awal (pre-warming worker pool). Kolam proses pekerja (multiprocessing.Pool(processes=P)) diinisialisasi sebelum siklus pengujian dimulai, lalu dikirimkan satu tugas kosong (dummy task) berupa pool.map(abs, range(P)) ke seluruh pekerja. Langkah ini memastikan seluruh interpreter proses pekerja telah aktif penuh (idle-ready) dan siap menerima distribusi blok data irisan citra. Durasi yang diukur dalam penelitian ini merepresentasikan kinerja kondisi mantap (steady-state performance) kalkulasi murni, dengan biaya pembuatan kolam pekerja diisolasi di luar pencatatan waktu komputasi.


### 3.5.2 Protokol Pengkondisian Termal dan Isolasi Derau Sistem

Eksekusi beban kerja komputasi numerik intensif secara kontinu pada prosesor modern dapat memicu peningkatan akumulasi panas silikon. Peningkatan temperatur yang melampaui ambang batas termal dapat memicu mekanisme proteksi perangkat keras berupa penurunan frekuensi kerja secara otomatis (thermal throttling), yang berpotensi menghasilkan variabilitas waktu eksekusi yang semu. Untuk meredam fluktuasi termal, pengujian dijalankan di dalam ruangan kerja terkondisi pada suhu kamar stabil (~24 °C) serta diberikan jeda pendinginan selama 2 detik sebelum pergantian blok perlakuan skenario. Di samping itu, sebelum eksekusi pengujian dimulai, seluruh aplikasi pengguna pihak ketiga non-esensial, koneksi jaringan eksternal, dan layanan pembaruan otomatis sistem operasi dinonaktifkan guna meminimalkan derau interupsi penjadwalan OS (operating system scheduling jitter).

Sebagai catatan batasan eksperimental, sistem tidak mencatat sensor suhu mikroprosesor dan frekuensi kerja per iterasi ke dalam berkas telemetri CSV. Terdapat pula sedikit asimetri posisi dalam pasangan pengujian, karena eksekusi serial dijalankan saat sistem dalam kondisi dingin sedangkan eksekusi paralel berjalan segera setelah komputasi serial selesai. Asimetri ini dipertimbangkan secara objektif dalam interpretasi data.


### 3.5.3 Pengujian Berselang-seling (Interleaved Execution 30 Repetisi) dan Kontrol A/A

Untuk memastikan data waktu eksekusi serial dan paralel dapat dikomparasikan secara valid dan bebas dari bias tren waktu (temporal trend bias), seluruh pengujian dieksekusi melalui protokol 30 kali repetisi terkontrol yang dijalankan secara berselang-seling (interleaved execution). Alih-alih mengeksekusi 30 kali pengujian serial secara berurutan lalu dilanjutkan 30 kali pengujian paralel, protokol ini menjalankan pengujian secara bergantian pada setiap repetisi: Iterasi 1 Serial → Iterasi 1 Paralel → Iterasi 2 Serial → Iterasi 2 Paralel … hingga Iterasi 30. Melalui metode berselang-seling ini, setiap pasangan data serial dan paralel berdekatan secara waktu (temporally proximate), sehingga dampak fluktuasi termal jangka panjang dan interupsi latar belakang sistem dialami secara seimbang oleh kedua perlakuan.

Pada alokasi satu proses pekerja (P = 1) pada Skenario B dijalankan kontrol A/A, yaitu dua pengukuran serial independen yang disisipkan berselang-seling dengan protokol yang sama. Karena kedua pengukuran mengeksekusi instruksi kode identik pada satu inti prosesor, nilai rasio percepatan S yang diharapkan secara teoretis mendekati 1,00. Simpangan nilai S empiris dari 1,00 dipakai untuk memperkirakan ambang batas derau sistem (system noise floor) dan menguji ada tidaknya bias posisi (pengukuran pertama versus kedua) dalam setiap pasangan iterasi. Kontrol A/A ini tidak mengukur beban komunikasi pipa IPC maupun serialisasi data.

Sebagai catatan transparansi mengenai batasan eksperimen, urutan eksekusi ketiga blok skenario dijalankan secara sekuensial (Blok A dijalankan pertama, diikuti Blok B, lalu diakhiri oleh Blok C) tanpa pengacakan blok menyeluruh (global randomized block). Fenomena pergeseran waktu baseline serial antar-blok (karena Skenario A memiliki durasi baseline serial lebih lambat sekitar +20% hingga +28% dibandingkan Skenario B dan C akibat dinamika termal dan frekuensi awal sistem) dicatat sebagai batasan metodologis yang dianalisis pada Bab 5.


## 3.6 Teknik Analisis Data

Analisis data hasil pengujian bertumpu pada pendekatan statistik deskriptif dan inferensial non-parametrik yang sesuai dengan karakteristik data sistem komputasi riil. Waktu eksekusi sistem komputer umumnya memiliki distribusi yang asimetris dengan kecenderungan menjulur ke kanan (right-skewed distribution), akibat munculnya beberapa nilai pencilan (outliers) yang dipicu oleh interupsi periodik sistem operasi. Mengingat asumsi normalitas baku tidak terpenuhi pada durasi eksekusi, analisis pemusatan data mengutamakan statistik non-parametrik yang tahan terhadap pencilan (robust statistics), yaitu nilai median dan rentang antarkuartil (IQR, [Q25 - Q75]). Nilai rerata sampel (x̄) dan simpangan baku sampel (s) tetap dilaporkan sebagai parameter pelengkap.

Meskipun waktu eksekusi berdistribusi menjulur ke kanan, distribusi rasio percepatan (speedup S) memiliki karakteristik yang mendekati simetris. Berdasarkan Teorema Limit Pusat (Central Limit Theorem / CLT) untuk ukuran sampel n = 30 per kondisi, rerata sampel mendekati normal sehingga selang kepercayaan 95% (confidence interval) dihitung menggunakan distribusi t-Student dengan derajat kebebasan df = n - 1 = 29 dan nilai kritis t_(29; 0,025) = 2,04523. Independensi observasi diperiksa melalui autokorelasi lag-1 antar-iterasi. Selang kepercayaan 95% dihitung untuk estimasi rerata parameter S, E, dan T_overhead (Persamaan 3.1):


$$
CI_95% = x̄ ± 2,04523 · (s / √30) \quad (3.1)
$$

Keterangan:

* CI_95% : Selang kepercayaan 95% (confidence interval) nilai rerata parameter populasi.
* x̄ : Nilai rerata sampel dari n = 30 repetisi pengujian.
* s : Simpangan baku sampel.
* n : Ukuran sampel pengujian (n = 30, derajat kebebasan df = n - 1 = 29).
Pengujian signifikansi perbedaan performa antar-perlakuan dievaluasi melalui uji hipotesis non-parametrik dengan taraf signifikansi α = 0,05. Uji Kruskal–Wallis digunakan untuk menguji variasi kinerja antar-alokasi proses pekerja paralel murni (P ∈ {2, 4, 8}) pada Skenario B, serta menguji perbedaan kinerja antar-tiga jenis filter pada Skenario C. Apabila uji Kruskal–Wallis menunjukkan perbedaan signifikan (p < 0,05), analisis dilanjutkan dengan uji Mann–Whitney U berpasangan dengan penyesuaian nilai p melalui koreksi Holm-Bonferroni guna mengendalikan laju kesalahan keluarga perlakuan (family-wise error rate). Ukuran efek (effect size) dilaporkan menggunakan estimasi selisih median Hodges–Lehmann untuk melengkapi nilai signifikansi statistik.

Pencocokan model teoretis skalabilitas dilakukan dengan mencocokkan kurva rasio percepatan empiris terhadap formulasi Hukum Amdahl (Amdahl, 1967) menggunakan metode regresi non-linier kuadrat terkecil (non-linear least squares). Regresi meminimalkan jumlah kuadrat residu pada rerata percepatan S̄(P) untuk alokasi P ∈ {2, 4, 8} dengan batas parameter fraksi paralel f ∈ [0, 1] per algoritma filter, disertai estimasi selang kepercayaan 95% berbasis bootstrap sebanyak 2.000 ulangan perlakuan. Estimasi tiga titik data untuk satu parameter bebas ini bertindak sebagai uji kelayakan kurva teoretis. Evaluasi dilanjutkan dengan menghitung fraksi serial eksperimental metrik Karp–Flatt (Karp & Flatt, 1990) e = ((1/S̄) - (1/P)) / (1 - (1/P)) untuk P ∈ {2, 4, 8} guna mengevaluasi apakah fraksi serial efektif bernilai relatif tetap ataukah mengalami kenaikan seiring pertambahan unit pekerja.

Validasi integritas data luaran dilakukan secara deterministik melalui verifikasi bit-identik antara matriks citra hasil pemrosesan paralel terhadap matriks citra hasil pemrosesan serial pada seluruh 720 pasangan komparasi paralel-serial (90 pasangan kontrol A/A bersifat trivial) di luar jendela pengukuran waktu komputasi. Selisih intensitas piksel dihitung dengan mengonversi matriks uint8 ke representasi numerik float64 guna mencegah terjadinya integer underflow / wraparound saat nilai piksel paralel lebih kecil dari serial. Keidentikan bit-per-bit diverifikasi penuh menggunakan fungsi numpy.array_equal. Kriteria kelulusan integritas ditetapkan pada nilai selisih absolut maksimum piksel harus bernilai nol di seluruh koordinat spasial (Δmax = max |I_paralel - I_serial| = 0). Apabila ditemukan Δmax > 0, pengujian dinyatakan mengalami kegagalan integritas data. Seluruh angka hasil pengujian aktual dan besaran parameter empiris disimpan dan disajikan secara objektif pada Bab 5.


# DAFTAR PUSTAKA (RUJUKAN BAB 3)

Aesthetic-4K Dataset. (2025). High-resolution aesthetic photographic image benchmark under CC-BY 4.0. Open Repository.

Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560

Bradski, G. (2000). The OpenCV Library. Dr. Dobb's Journal of Software Tools, 25(11), 120–125.

Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A., del Río, J. F., Wiebe, M., Peterson, P., … Oliphant, T. E. (2020). Array programming with NumPy. Nature, 585(7825), 357–362. https://doi.org/10.1038/s41586-020-2649-2

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90–95. https://doi.org/10.1109/MCSE.2007.55

Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.

International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.

Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614

Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.

Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock

Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html

Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.

Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., … SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. Nature Methods, 17(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2
