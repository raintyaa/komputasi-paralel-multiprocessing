# BAB 3 METODOLOGI PENELITIAN


## Tahapan Penelitian

Penelitian ini dilaksanakan melalui enam tahapan terstruktur guna memastikan proses evaluasi komparasi kinerja komputasi paralel dan serial dapat terukur secara objektif, terkontrol, dan dapat diulang (reproducible). Tahapan penelitian tersebut mencakup:

* Studi literatur: Mengkaji teori komputasi paralel (data parallelism), mekanisme pengalamatan memori larik NumPy (row-major order), arsitektur konkurensi modul Python multiprocessing, batasan Global Interpreter Lock (GIL) pada CPython, arsitektur prosesor heterogen modern, serta formulasi matematis algoritma filter spasial citra (Grayscale, Gaussian Blur 3×3, dan Sobel 3×3).
* Perancangan dan pengkodean algoritma: Mengembangkan dua varian siste komputasi pengujian, yaitu skrip serial murni satu inti prosesor sebagai acuan pembanding (baseline) dan skrip paralel yang mengintegrasikan pemotongan blok baris horizontal dengan distribusi tugas melalui multiprocessing.Pool.
* Pengumpulan dan standardisasi data citra master: Menyiapkan citra acuan master beresolusi tinggi 4K (4096 × 4096 piksel) yang bersumber dari repositori fotografi terbuka Aesthetic-4K (Aesthetic-4K Dataset, 2025) berlisensi Creative Commons Attribution 4.0 International (CC-BY 4.0), yang dipotong secara terpusat (center-crop) tanpa kompresi ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel.
* Eksekusi eksperimen terkontrol: Menjalankan pengujian kinerja pada lingkungan sistem operasi terkendali tanpa interferensi aplikasi latar belakang pengguna. Setiap kombinasi perlakuan dieksekusi sebanyak 30 kali repetisi secara berselang-seling (interleaved execution) antara pengukuran serial dan paralel guna meminimalkan fluktuasi termal dan beban penjadwalan sistem operasi.
* Pencatatan parameter kinerja: Merekam durasi waktu komputasi murni menggunakan fungsi pewaktu presisi tinggi time.perf_counter(), memantau persentase beban CPU proses utama via modul psutil, serta menghitung metrik rasio percepatan (speedup), efisiensi paralel, dan beban tambahan (overhead) paralel ke dalam berkas log telemetri CSV.
* Analisis skalabilitas dan pencocokan model: Menganalisis karakteristik skalabilitas melalui statistik non-parametrik deskriptif, mencocokkan kurva percepatan empiris terhadap batas teoretis Hukum Amdahl, mendiagnosis hambatan koordinasi paralel menggunakan metrik Karp–Flatt, serta memvalidasi determinisme luaran melalui kriteria verifikasi bit-identik (Δmax = 0).
Bagan alir pelaksanaan tahapan penelitian secara menyeluruh disajikan pada Gambar 3.1. Bagan alir ini merangkum urutan logis dari keenam tahapan penelitian, mulai dari inisialisasi studi pustaka dan penyiapan data citra master, pelaksanaan pengujian berulang 30 kali secara berselang-seling, pencatatan telemetri kinerja, hingga analisis kuantitatif dan evaluasi integritas bit-identik.


> **[Area Gambar 3.1: Diagram Alir Tahapan Penelitian] (Diagram alir dalam proses penyempurnaan format visual beresolusi tinggi 300 DPI untuk disematkan pada area ini)**

Gambar 3.1 Diagram Alir Tahapan Penelitian


## Pengumpulan dan Standardisasi Data Citra Master

Data citra yang digunakan dalam penelitian ini bersumber dari repositori fotografi terbuka beresolusi tinggi Aesthetic-4K (Aesthetic-4K Dataset, 2025) yang didistribusikan di bawah lisensi resmi Creative Commons Attribution 4.0 International (CC-BY 4.0). Citra master yang dipilih memiliki format asli RGB 24-bit tanpa kompresi (uncompressed PNG) dengan kualitas visual prima, bebas dari artefak distorsi kompresi lossy JPEG, serta memiliki sebaran gradien intensitas dan tepi spasial yang kaya guna memberikan beban kalkulasi konvolusi yang representatif.

Untuk menghasilkan variasi dimensi data yang seragam dan konsisten secara proporsi visual, citra master 4K (4096 × 4096 piksel) diproses melalui pemotongan terpusat (center-crop) tanpa proses resampling atau interpolasi piksel. Pemotongan terpusat dilakukan secara bertingkat dengan rasio penggandaan panjang sisi dua kali lipat pada setiap tingkatan, menghasilkan empat berkas citra masukan berdimensi bujur sangkar, yaitu: 512 × 512 piksel (volume memori mentah sekitar 768 KB), 1024 × 1024 piksel (volume memori mentah sekitar 3 MB), 2048 × 2048 piksel (volume memori mentah sekitar 12 MB), dan 4096 × 4096 piksel (volume memori mentah sekitar 48 MB data RGB tak terkompresi bertipe data uint8).

Dalam evaluasi komputasi paralel visi komputer, terdapat pertimbangan metodologis mendasar terkait pemilihan apakah pengujian memerlukan variasi banyak berkas gambar ataukah cukup menggunakan satu citra acuan master yang distandardisasi. Pada penelitian ini, diputuskan secara ilmiah untuk menggunakan satu citra acuan master terstandardisasi berdasarkan karakteristik intrinsik algoritma filter spasial yang diuji. Operasi konvolusi matriks spasial (Gaussian Blur 3×3 dan Sobel 3×3) serta konversi derajat keabuan (Grayscale ITU-R BT.601) memiliki karakteristik komputasi yang sepenuhnya tidak bergantung pada isi visual citra (data-independent computation). Pada seluruh algoritma tersebut, setiap piksel diproses melalui rantai instruksi aritmatika perkalian dan penjumlahan koefisien kernel yang identik tanpa adanya percabangan kondisional (conditional branching / if-else) yang dipengaruhi oleh nilai intensitas piksel. Dengan demikian, beban siklus instruksi ALU prosesor per piksel bernilai konstan, terlepas dari tekstur visual citra yang diproses. Penggunaan satu citra acuan master terstandardisasi memberikan keunggulan metodologis yang penting, yaitu mengeliminasi variabilitas tekstur visual antar-berkas sehingga seluruh variabilitas waktu eksekusi yang terukur murni mencerminkan perilaku sistem komputasi (interferensi penjadwalan OS, latensi komunikasi IPC antar-proses, dan dinamika arsitektur inti hibrida). Seluruh 30 sampel citra multiresolusi awal tetap diarsipkan secara lengkap sebagai cadangan dataset.


## Alat dan Bahan Penelitian

Pelaksanaan eksperimen komputasi paralel memerlukan dukungan perangkat keras, perangkat lunak, dan instrumen pengukuran yang terdefinisi secara presisi untuk menjamin keterulangan (reproducibility) pengujian.


### Perangkat Keras dan Kondisi Operasional

Eksperimen komputasi paralel dilaksanakan pada satu unit komputer jinjing (laptop) dengan spesifikasi prosesor heterogen modern Intel Core i5-13420H generasi ke-13 (nama sandi Raptor Lake). Prosesor ini memiliki 8 inti fisik (physical cores) yang terdiri atas 4 Performance-Cores (P-Cores, arsitektur Raptor Cove) dengan frekuensi dasar 2,1 GHz dan dorongan turbo hingga 4,6 GHz yang mendukung Simultaneous Multithreading (SMT / Hyper-Threading 8 threads), serta 4 Efficient-Cores (E-Cores, arsitektur Gracemont) dengan frekuensi dasar 1,5 GHz dan turbo hingga 3,4 GHz tanpa SMT (4 threads), menghasilkan kapasitas pemrosesan total 12 threads. Subsistem memori cache prosesor terdiri atas L1 Cache (80 KB per P-Core dan 96 KB per E-Core), L2 Cache (1,25 MB per P-Core dan 2 MB terbagi per kluster empat E-Core), serta 12 MB L3 Intel Smart Cache yang terbagi secara bersama (shared cache) untuk seluruh inti prosesor.

Sistem didukung oleh memori utama (RAM) berkapasitas 16 GB DDR5 dengan frekuensi transfer 5200 MT/s berkonfigurasi dual-channel, serta media penyimpanan berkecepatan tinggi Solid State Drive (SSD) M.2 NVMe PCIe 4.0 berkapasitas 512 GB. Untuk menjaga konsistensi kinerja termal dan kelistrikan selama proses pengujian:

* Perangkat keras dihubungkan secara kontinu ke adaptor catu daya listrik AC (pengisi daya 135 W) guna meniadakan penurunan frekuensi kerja prosesor yang dipicu oleh mekanisme penghematan daya baterai (battery power throttling).
* Profil daya pada sistem operasi Windows 11 dikunci secara permanen pada skema Best Performance.
* Seluruh pengujian dijalankan di dalam ruangan kerja terkondisi pada suhu kamar stabil (~24 °C) dengan pemantauan suhu awal prosesor sebelum pengujian dimulai.
Tabel 3.1 Spesifikasi Perangkat Keras dan Kondisi Operasional Pengujian



| Komponen Perangkat Keras | Spesifikasi Teknis | Kondisi Operasional Pengujian |
| --- | --- | --- |
| Prosesor (CPU) | Intel Core i5-13420H (13th Gen Raptor Lake), 8 Inti Fisik (4 P-Cores + 4 E-Cores), 12 Threads, Base Clock P-Core 2,1 GHz / Turbo 4,6 GHz, E-Core 1,5 GHz / Turbo 3,4 GHz | Dijalankan pada skema daya Windows Best Performance; laptop terhubung kontinu ke adaptor listrik AC; pemantauan suhu awal sebelum pengujian. |
| Memori Cache CPU | L1: 80 KB/P-Core, 96 KB/E-Core;<br>L2: 1,25 MB/P-Core, 2 MB/E-Core kluster;<br>L3: 12 MB Intel Smart Cache terbagi bersama (shared) | Berbagi pakai secara merata untuk seluruh proses pekerja; pengujian mengevaluasi efek pelonjakan cache hit pada matriks citra 512 × 512 piksel. |
| Memori Utama (RAM) | 16 GB DDR5 5200 MT/s Dual-Channel | Kapasitas memadai untuk menampung seluruh larik citra masukan dan luaran secara simultan tanpa swapping ke penyimpanan sekunder. |
| Media Penyimpanan | 512 GB SSD M.2 NVMe PCIe 4.0 | Hanya digunakan untuk operasi I/O pembacaan berkas awal dan penyimpanan luaran; diisolasi penuh dari durasi waktu komputasi paralel. |
| Catu Daya Listrik | Adaptor AC 135 W eksternal | Terhubung secara kontinu selama pengujian guna mencegah penurunan frekuensi kerja (battery power throttling). |
| Suhu Lingkungan | Ruang kerja terkondisi (~24 °C) | Suhu ruangan dijaga stabil guna meminimalkan fluktuasi termal lingkungan selama 810 eksekusi pengujian. |



### Perangkat Lunak dan Pustaka Komputasi

Lingkungan perangkat lunak yang digunakan dalam penelitian ini meliputi sistem operasi Windows 11 Home 64-bit (Build 22631) sebagai platform eksekusi sistem. Bahasa pemrograman yang digunakan adalah Python 3.14.3 (rilis resmi CPython 64-bit dari Python Software Foundation). Komputasi matriks citra bertumpu pada pustaka NumPy versi 2.5.4 yang mengelola representasi data larik multidimensi dalam format row-major (C-contiguous memory layout).

Pustaka OpenCV versi 5.0.0 digunakan secara terbatas hanya untuk operasi pembacaan dan penyimpanan berkas citra (file I/O). Guna mencegah interferensi akselerasi internal OpenCV yang dapat mengaburkan evaluasi multiprocessing murni, utas komputasi internal OpenCV dinonaktifkan secara eksplisit menggunakan perintah cv2.setNumThreads(1). Modul bawaan Python multiprocessing digunakan sebagai pengendali orkestrasi paralel berbasis kolam proses pekerja (Pool). Pustaka psutil versi 7.2.2 digunakan untuk merekam persentase utilisasi CPU sistem. Pustaka SciPy versi 1.15.2 digunakan untuk melakukan regresi non-linier kuadrat terkecil (least squares curve fitting) dan uji hipotesis statistik, sedangkan Matplotlib versi 3.10.0 digunakan untuk menghasilkan grafik komparasi data kinerja.

Tabel 3.2 Spesifikasi Perangkat Lunak dan Pustaka Komputasi



| Perangkat Lunak / Pustaka | Versi Rilis | Fungsi dan Peran dalam Penelitian |
| --- | --- | --- |
| Windows 11 Home 64-bit | Build 22631 | Sistem operasi induk; manajemen penjadwalan proses bekerja sama dengan mikrokontroler Intel Thread Director. |
| Python (CPython) | 3.14.3 | Bahasa pemrograman utama untuk implementasi mesin komputasi serial dan paralel. |
| NumPy | 2.5.4 | Pengelolaan struktur larik multidimensi berbasis row-major (C-contiguous), pemotongan blok baris, dan rekonstruksi citra utuh via numpy.vstack. |
| OpenCV (cv2) | 5.0.0 | Pembacaan dan penulisan berkas citra masukan/luaran (I/O); utas komputasi dikunci satu secara permanen melalui cv2.setNumThreads(1). |
| Multiprocessing | Bawaan Python | Orkestrasi proses paralel independen, alokasi kolam pekerja (Pool), dan saluran komunikasi antre/pipa IPC. |
| Psutil | 7.2.2 | Perekaman persentase beban utilisasi CPU sistem pada proses utama selama eksekusi komputasi filter. |
| SciPy | 1.15.2 | Eksekusi regresi non-linier kuadrat terkecil untuk pencocokan Hukum Amdahl dan pengujian signifikansi statistik (Kruskal–Wallis / Mann–Whitney). |
| Matplotlib | 3.10.0 | Pustaka grafis untuk memvisualisasikan kurva performa komparasi waktu, speedup, efisiensi, dan overhead. |



### Alat Ukur dan Instrumentasi Kinerja

Pengukuran durasi waktu eksekusi komputasi dilakukan menggunakan fungsi pewaktu presisi tinggi berbasis monotonik time.perf_counter() dari modul pustaka standar Python. Pewaktu ini memiliki resolusi tingkat nanodetik dan bersifat monotonik, artinya nilai pewaktu selalu bertambah secara linier dan tidak pernah terdistorsi oleh penyesuaian jam sistem operasi (system clock drift) maupun sinkronisasi waktu jaringan (NTP). Pencatatan stempel waktu awal (start timestamp) dan stempel waktu akhir (stop timestamp) dilakukan secara ketat hanya pada blok kalkulasi pemrosesan citra murni, sehingga waktu pembacaan citra dari penyimpanan (disk reading) dan waktu penulisan kembali hasil ke media penyimpanan (disk writing) diisolasi sepenuhnya dari pengukuran kinerja komputasi.

Instrumentasi utilisasi kapasitas prosesor dicatat menggunakan modul psutil.cpu_percent(interval=None) yang dipanggil pada proses utama. Perlu dicatat sebagai batasan metodologis bahwa pembacaan nilai ini merefleksikan utilisasi CPU sistem secara keseluruhan dari sudut pandang proses utama, sehingga pada durasi eksekusi yang sangat singkat (di bawah 100 milidetik pada citra resolusi kecil), pembacaan utilisasi CPU cenderung merefleksikan artefak jendela sampel (sampling window artifact) dan tidak merefleksikan seluruh aktivitas proses pekerja secara instan. Oleh karena itu, data utilisasi CPU diperlakukan sebagai indikator tren beban relatif dan bukan sebagai penentu utama efisiensi komputasi.


## Desain Eksperimen

Penelitian ini menerapkan desain eksperimen faktorial terkontrol (controlled factorial experimental design) untuk menganalisis pengaruh simultan dari variabel ukuran data matriks, alokasi unit proses kerja, dan tingkat kompleksitas algoritma filter spasial. Identifikasi variabel penelitian diklasifikasikan sebagai berikut:

* Variabel bebas (independent variables): Resolusi spasial citra masukan (512 × 512, 1024 × 1024, 2048 × 2048, dan 4096 × 4096 piksel), alokasi jumlah proses pekerja (P = 1, 2, 4, dan 8 proses pekerja), serta jenis algoritma filter spasial citra (Grayscale ITU-R BT.601, Gaussian Blur 3×3, dan Sobel 3×3).
* Variabel terikat (dependent variables): Waktu eksekusi serial (T_serial) dan waktu eksekusi paralel (T_paralel) dalam detik, rasio percepatan komputasi (speedup S), persentase efisiensi paralel (E), durasi beban tambahan paralel (parallel overhead T_overhead) dalam detik, dan persentase utilisasi kapasitas CPU.
* Variabel kontrol (controlled variables): Citra acuan master tunggal terstandardisasi (Aesthetic-4K terpotong terpusat), spesifikasi perangkat keras dan sistem operasi yang seragam, penguncian utas tunggal OpenCV (cv2.setNumThreads(1)), serta eliminasi proses latar belakang pengguna non-esensial.
Ruang lingkup pengujian dibagi ke dalam tiga blok skenario eksperimental yang saling melengkapi:

* Skenario A (Variasi Dimensi Citra): Alokasi proses pekerja dikunci pada 4 pekerja (P = 4), sedangkan dimensi spasial citra dinaikkan secara bertahap dari 512 × 512 hingga 4096 × 4096 piksel pada ketiga filter. Skenario ini bertujuan memetakan bagaimana pertumbuhan volume data memengaruhi rasio speedup dan efisiensi pada masing-masing karakteristik operasi filter. Skenario ini mencakup 12 kondisi pengujian (A1 s.d. A12).
* Skenario B (Variasi Alokasi Proses Kerja): Dimensi spasial citra dikunci pada resolusi menengah 2048 × 2048 piksel, sedangkan alokasi proses kerja divariasikan untuk P ∈ {1, 2, 4, 8} pada ketiga filter. Alokasi P = 1 dijalankan sebagai instrumen kontrol dasar A/A (A/A control). Skenario ini bertujuan memetakan kurva percepatan terhadap batas saturasi Hukum Amdahl dan mendiagnosis perilaku metrik Karp–Flatt seiring penambahan unit kerja. Skenario ini mencakup 12 kondisi pengujian (B1 s.d. B12).
* Skenario C (Variasi Kompleksitas Algoritma Filter): Dijalankan sebagai blok pengujian terpisah pada resolusi 2048 × 2048 piksel dengan alokasi 4 proses pekerja (P = 4) untuk ketiga jenis filter. Skenario ini bertujuan mengevaluasi interaksi antara beban kalkulasi matematis per piksel terhadap beban tambahan (overhead) komunikasi IPC, sekaligus bertindak sebagai instrumen uji keterulangan (repeatability test) terhadap titik uji A3 dan B2. Skenario ini mencakup 3 kondisi pengujian (C1 s.d. C3).
Secara keseluruhan, matriks desain eksperimen mencakup 27 kombinasi kondisi pengujian unik (12 + 12 + 3). Setiap kondisi perlakuan diuji sebanyak 30 kali repetisi terkontrol secara berselang-seling, menghasilkan total 810 eksekusi pengujian eksperimental. Rincian matriks desain eksperimen dan definisi operasional parameter kinerja masing-masing dirangkum pada Tabel 3.3 dan Tabel 3.4.

Tabel 3.3 Matriks Desain Eksperimen Pengujian Komputasi Paralel



| Blok Skenario | Kode Kondisi | Jenis Filter Spasial | Resolusi Citra (px) | Alokasi Pekerja (P) | Repetisi & Peran Metodologis |
| --- | --- | --- | --- | --- | --- |
| Skenario A<br>(Dimensi Citra) | A1 – A4 | Grayscale | 512, 1024,<br>2048, 4096 | 4 | 30 repetisi selang-seling; evaluasi dampak volume data pada operasi titik berbeban komputasi rendah. |
| Skenario A<br>(Dimensi Citra) | A5 – A8 | Gaussian Blur 3×3 | 512, 1024,<br>2048, 4096 | 4 | 30 repetisi selang-seling; evaluasi dampak volume data pada konvolusi 3 kanal RGB dengan transfer memori besar. |
| Skenario A<br>(Dimensi Citra) | A9 – A12 | Sobel 3×3 | 512, 1024,<br>2048, 4096 | 4 | 30 repetisi selang-seling; evaluasi dampak volume data pada konvolusi gradien ganda intensif komputasi. |
| Skenario B<br>(Alokasi Pekerja) | B1 – B4 | Grayscale | 2048 × 2048 | 1, 2, 4, 8 | 30 repetisi selang-seling; P=1 sebagai kontrol A/A; pemodelan kurva Amdahl dan diagnostik metrik Karp–Flatt. |
| Skenario B<br>(Alokasi Pekerja) | B5 – B8 | Gaussian Blur 3×3 | 2048 × 2048 | 1, 2, 4, 8 | 30 repetisi selang-seling; P=1 sebagai kontrol A/A; pemodelan kurva Amdahl dan diagnostik metrik Karp–Flatt. |
| Skenario B<br>(Alokasi Pekerja) | B9 – B12 | Sobel 3×3 | 2048 × 2048 | 1, 2, 4, 8 | 30 repetisi selang-seling; P=1 sebagai kontrol A/A; pemodelan kurva Amdahl dan diagnostik metrik Karp–Flatt. |
| Skenario C<br>(Kompleksitas Filter) | C1 – C3 | Grayscale, Gaussian Blur 3×3, Sobel 3×3 | 2048 × 2048 | 4 | 30 repetisi selang-seling; blok terpisah untuk komparasi hierarki kompleksitas dan uji keterulangan (repeatability) terhadap A3 dan B2. |


Tabel 3.4 Definisi Operasional Parameter Kinerja yang Diuji



| Parameter Kinerja | Simbol & Satuan | Alat Ukur / Formulasi | Deskripsi Operasional |
| --- | --- | --- | --- |
| Waktu Eksekusi Serial | T_serial (detik) | time.perf_counter() pada skrip serial murni | Durasi pemrosesan citra pada satu inti prosesor tanpa pemanggilan modul multiprocessing; bertindak sebagai nilai acuan (baseline). |
| Waktu Eksekusi Paralel | T_paralel (detik) | time.perf_counter() pada skrip paralel | Durasi eksekusi paralel sejak awal partisi blok baris, transmisi pipa IPC, kalkulasi filter oleh kolam pekerja, hingga rekonstruksi citra utuh via vstack. |
| Rasio Percepatan | S (nirdimensi) | S = T_serial / T_paralel<br>(Persamaan 2.2) | Kelipatan percepatan komputasi yang dihasilkan oleh sistem paralel dibandingkan eksekusi serial pada kondisi perlakuan yang identik. |
| Efisiensi Paralel | E (%) | E = (S / P) × 100%<br>(Persamaan 2.3) | Persentase pemanfaatan kapasitas komputasi dari setiap unit proses pekerja yang dialokasikan dalam eksekusi paralel. |
| Beban Tambahan Paralel | T_overhead (detik) | T_overhead = T_paralel - (T_serial / P)<br>(Persamaan 2.4) | Durasi beban penalti sistem akibat latensi komunikasi pipa IPC, serialisasi objek NumPy (pickle), replikasi baris batas (halo), dan rekonstruksi matriks. |
| Utilisasi Kapasitas CPU | CPU (%) | psutil.cpu_percent(interval=None) | Persentase beban kerja prosesor yang dicatat pada proses utama sebagai indikator tren pemanfaatan sistem secara keseluruhan. |
| Integritas Citra Bit-Identik | Δmax (uint8) | Δmax = max |I_paralel - I_serial| | Selisih nilai intensitas piksel maksimum antara citra paralel dan serial; kriteria kelulusan mutlak ditetapkan pada Δmax = 0. |



## Prosedur Pengukuran dan Pengujian

Prosedur pengujian dirancang dengan protokol ketat guna mengisolasi variabel pengganggu (confounding factors) yang bersumber dari mekanisme internal interpreter Python, karakteristik termal prosesor, dan dinamika penjadwalan sistem operasi.


### Protokol Pemanasan Awal (Pre-Warming Worker Pool)

Pada sistem operasi Windows, modul multiprocessing menggunakan metode inisialisasi proses spawn (Python Software Foundation, n.d.-b). Metode ini meluncurkan interpreter Python baru dari awal untuk setiap proses pekerja, yang membutuhkan alokasi memori dan waktu inisialisasi yang signifikan (~0,1 hingga ~0,5 detik per proses). Apabila inisialisasi proses pekerja dilakukan di dalam blok pengukuran waktu komputasi, durasi peluncuran proses baru (cold spawn penalty) mendominasi dan mendistorsi waktu eksekusi paralel yang sebenarnya. Untuk mengeliminasi distorsi tersebut, dirancang protokol pemanasan awal (pre-warming worker pool). Kolam proses pekerja (multiprocessing.Pool(processes=P)) diinisialisasi dan distabilkan satu kali sebelum siklus pengujian dimulai. Stempel waktu komputasi paralel baru dicatat setelah seluruh proses pekerja berada dalam status aktif (idle-ready) dan siap menerima distribusi blok data irisan citra.


### Protokol Jeda Dingin (Cool-Down Buffer) dan Isolasi Derau Sistem

Eksekusi beban kerja komputasi numerik intensif secara kontinu pada prosesor modern dapat memicu peningkatan akumulasi panas pada inti silikon. Peningkatan temperatur yang melampaui batas ambang termal dapat memicu mekanisme proteksi perangkat keras berupa penurunan frekuensi kerja secara otomatis (thermal throttling), yang berpotensi menghasilkan variabilitas waktu eksekusi yang semu. Untuk meminimalkan efek pelambatan termal (thermal throttling), diterapkan protokol jeda dingin (cool-down buffer) berupa penundaan waktu tidur sistem selama 0,5 detik (time.sleep(0.5)) di antara setiap repetisi pengujian, serta jeda waktu pendinginan tambahan selama 2 detik sebelum pergantian blok perlakuan filter. Di samping itu, sebelum eksekusi pengujian dimulai, seluruh aplikasi pengguna pihak ketiga non-esensial, koneksi jaringan eksternal, dan layanan pembaruan otomatis sistem operasi dinonaktifkan guna meminimalkan derau interupsi penjadwalan OS (operating system scheduling jitter).


### Pengujian Berselang-seling (Interleaved Execution 30 Repetisi) dan Kontrol A/A

Untuk memastikan data waktu eksekusi serial dan paralel dapat dikomparasikan secara valid dan bebas bias, seluruh pengujian dieksekusi melalui protokol 30 kali repetisi terkontrol yang dijalankan secara berselang-seling (interleaved execution). Alih-alih mengeksekusi 30 kali pengujian serial secara berurutan lalu dilanjutkan 30 kali pengujian paralel, protokol ini menjalankan pengujian secara bergantian pada setiap repetisi: Iterasi 1 Serial → Iterasi 1 Paralel → Iterasi 2 Serial → Iterasi 2 Paralel … hingga Iterasi 30. Dengan metode berselang-seling ini, setiap pasangan data serial dan paralel mengalami kondisi beban sistem latar belakang dan profil termal lingkungan yang setara, sehingga nilai rasio percepatan (speedup) yang dihitung dari pasangan iterasi yang berdekatan memiliki validitas internal yang kokoh.

Pengujian pada alokasi satu proses pekerja (P = 1) pada Skenario B difungsikan sebagai instrumen kontrol dasar serial terhadap serial (A/A control). Karena pada P = 1 seluruh komputasi hanya dieksekusi oleh satu proses pekerja tanpa pembagian beban ke beberapa inti fisik prosesor, secara teoretis tidak terjadi percepatan komputasi (S ≈ 1,00). Nilai selisih waktu eksekusi yang terukur (T_overhead, P=1 = T_paralel, P=1 - T_serial) secara presisi merepresentasikan ambang batas derau sistem (system noise floor) serta biaya struktural inheren dari modul multiprocessing Python (mekanisme transmisi pipa IPC dan serialisasi objek data) tanpa campur tangan akselerasi perangkat keras.

Sebagai catatan transparansi ilmiah mengenai batasan eksperimen, urutan eksekusi ketiga blok skenario dijalankan secara sekuensial (Blok A dijalankan pertama, diikuti Blok B, lalu diakhiri oleh Blok C) tanpa pengacakan menyeluruh (global randomized block). Fenomena pergeseran waktu baseline serial antar-blok (karena Skenario A memiliki durasi baseline serial sedikit lebih lambat dibandingkan Skenario B dan C akibat dinamika termal awal sistem) dicatat sebagai batasan metodologis yang dianalisis secara objektif pada Bab 5.


## Teknik Analisis Data

Analisis data hasil pengujian bertumpu pada pendekatan statistik deskriptif dan inferensial non-parametrik yang tangguh terhadap karakteristik data sistem komputasi riil. Waktu eksekusi sistem komputer umumnya memiliki distribusi yang asimetris dengan kecenderungan menjulur ke kanan (right-skewed distribution), akibat munculnya beberapa nilai pencilan (outliers) yang dipicu oleh interupsi periodik sistem operasi. Mengingat asumsi normalitas baku tidak terpenuhi, analisis pemusatan data mengutamakan statistik non-parametrik yang tangguh terhadap pencilan (robust statistics), yaitu nilai median dan rentang antarkuartil (IQR, [Q25 - Q75]). Nilai rerata sampel (x̄) dan simpangan baku sampel (s) tetap dilaporkan sebagai parameter pelengkap.

Untuk mengestimasi presisi statistik pada nilai rerata parameter kinerja, dihitung selang kepercayaan 95% (confidence interval) menggunakan distribusi t-Student untuk ukuran sampel n = 30 (df = n - 1 = 29) dengan nilai kritis t_(29, 0,025) = 2,04523:
CI_95% = x̄ ± 2,04523 · (s / √30)
Formulasi ini menjamin estimasi rentang parameter populasi dengan tingkat kepercayaan 95%.

Pengujian signifikansi perbedaan performa antar-perlakuan dievaluasi melalui uji hipotesis non-parametrik dengan taraf signifikansi α = 0,05. Uji Mann–Whitney U digunakan untuk menguji signifikansi perbedaan antara dua kelompok perlakuan independen, sedangkan uji Kruskal–Wallis digunakan untuk menguji variasi kinerja antar-alokasi proses pekerja (P = 1, 2, 4, 8). Suatu perbedaan perlakuan dinyatakan signifikan secara statistik apabila nilai signifikansi terhitung lebih kecil dari ambang batas (p < 0,05).

Pencocokan model teoretis skalabilitas dilakukan dengan mencocokkan kurva rasio percepatan empiris terhadap formulasi Hukum Amdahl menggunakan metode regresi non-linier kuadrat terkecil (non-linear least squares). Melalui pendekatan ini, diestimasi besaran fraksi paralel teoretis f per algoritma filter pada Skenario B (P ∈ {2, 4, 8}) beserta selang kepercayaan 95% berbasis bootstrap. Evaluasi dilanjutkan dengan menghitung fraksi serial eksperimental metrik Karp–Flatt e = ((1/S) - (1/P)) / (1 - (1/P)) untuk mendiagnosis apakah keterbatasan skalabilitas bersifat algoritmik murni ataukah dipicu oleh pembengkakan beban koordinasi paralel.

Validasi integritas data luaran dilakukan secara deterministik melalui verifikasi bit-identik antara matriks citra hasil pemrosesan paralel terhadap matriks citra hasil pemrosesan serial pada seluruh 810 iterasi pengujian. Kriteria kelulusan integritas ditetapkan dengan kriteria biner yang ketat, yaitu selisih nilai intensitas piksel maksimum antara citra paralel dan serial harus bernilai nol di seluruh koordinat spasial (Δmax = max |I_paralel - I_serial| = 0). Apabila ditemukan Δmax > 0, pengujian dinyatakan mengalami kegagalan integritas (data corruption). Mengikuti kaidah akademik penulisan metodologi, seluruh angka hasil pengujian aktual dan besaran parameter empiris disimpan dan disajikan secara komprehensif pada Bab 5.


# DAFTAR PUSTAKA (RUJUKAN BAB 3)

Aesthetic-4K Dataset. (2025). High-resolution aesthetic photographic image benchmark under CC-BY 4.0. Kaggle / Open Repository.

Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560

Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.

International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.

Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614

Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.

Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock

Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html

Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.
