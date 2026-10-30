# SUBBAB 5.5 PEMBAHASAN TEMUAN DAN KETERBATASAN PENELITIAN & BAB 6 PENUTUP


## 5.5 Pembahasan Temuan dan Keterbatasan Penelitian

Subbab ini membahas temuan empiris dari Skenario A, B, dan C berdasarkan prinsip arsitektur komputasi, karakteristik perangkat keras, serta perbandingannya terhadap literatur terdahulu.


### Dinamika Resolusi Citra dan Hipotesis Pengaruh Hierarki Cache L2 dan L3

Pada pengujian Skenario A, filter Sobel pada resolusi 512 × 512 piksel dengan alokasi empat proses pekerja (P = 4) mencatatkan rasio percepatan yang mendekati batas linier ideal (S ≈ P), dengan median *speedup* sebesar 4,04× dan rerata 3,89× (deviasi standar 0,84; interval kepercayaan 95% [3,58; 4,20]). Efisiensi komputasi median tercatat sebesar 101,02% (rerata 97,26%). Sebanyak 16 dari 30 repetisi pengujian menghasilkan nilai *overhead* negatif tipis dengan median −0,0002 detik (mendekati nol). Pada resolusi yang sama, Gaussian Blur memperoleh median *speedup* 2,50× (rerata 2,52×), sedangkan Grayscale memperoleh median *speedup* 1,52× (rerata 1,68×).

Tingginya rasio percepatan filter Sobel pada dimensi 512 × 512 piksel konsisten dengan hipotesis interaksi ukuran data terhadap hierarki memori cache prosesor *Intel Core i5-13420H*. Prosesor ini dilengkapi 12 MB L3 *Intel Smart Cache* yang digunakan bersama dan 1,25 MB L2 cache privat pada setiap *Performance-Core* (*P-Core*).

Citra RGB 512 × 512 piksel berukuran total sekitar 768 KB (atau 262 KB dalam format monokrom satu kanal). Ukuran data tersebut beserta lapisan batas *halo padding* (k = 1) termuat utuh ke dalam 12 MB L3 cache bersama, baik pada eksekusi serial maupun paralel. Pembeda kinerja antara eksekusi serial dan paralel pada konfigurasi ini didorong oleh distribusi beban ke dalam hierarki L2 cache privat masing-masing inti.

Ketika citra dipartisi ke empat pekerja, setiap pekerja memproses irisan submatriks berukuran 130 × 512 piksel (termasuk *boundary halo*) dengan ukuran data masukan sekitar 195 KB. Partisi data masukan yang ringkas ini beserta larik perantara gradien konvolusi berpeluang besar tertampung pada 1,25 MB L2 cache privat masing-masing *P-Core*, sehingga mengurangi frekuensi akses ke memori utama DRAM.

Selain itu, eksekusi paralel empat pekerja mendistribusikan lalu lintas data ke empat jalur L2 cache privat. Pembagian ini mengurangi terjadinya kegagalan kapasitas (*capacity misses*) dan kontensi antrean bus memori yang dihadapi eksekusi serial satu inti saat mengolah keseluruhan larik citra secara berulang.

Karakteristik luaran filter Sobel juga berperan penting. Filter Sobel menghasilkan luaran monokromatik satu kanal berukuran ringkas (sekitar 262 KB pada 512 × 512 piksel), berbeda dari Gaussian Blur yang harus mengembalikan luaran tiga kanal warna penuh (sekitar 786 KB). Muatan transmisi IPC yang lebih kecil pada filter Sobel membuat biaya komunikasi antar-proses tetap rendah pada resolusi kecil, sehingga akselerasi komputasi dapat tercapai optimal.

Pola percepatan mendekati linier pada resolusi 512 × 512 piksel tidak teramati pada operasi Grayscale maupun Gaussian Blur. Pada Grayscale, intensitas aritmatika berada pada tingkat 1,25 FLOP/bita dan durasi pemrosesan serial berlangsung singkat (median 0,0203 detik). Pada durasi tersebut, latensi tetap pipa komunikasi antar-proses (pembuatan pipa IPC, serialisasi, dan deserialisasi *pickle*) yang berkisar 0,008 detik mendominasi perbandingan, sehingga *speedup* tertahan pada angka 1,52× (rerata 1,68×). Pada Gaussian Blur, intensitas komputasi yang mencapai 8,50 FLOP/bita terhambat oleh volume data luaran tiga kanal RGB yang harus dialirkan kembali melalui pipa IPC — tiga kali lipat lebih besar dibandingkan Sobel (satu kanal). Beban transmisi IPC yang besar ini menekan efisiensi paralel Gaussian Blur pada angka 2,50× (rerata 2,52×).

Seiring peningkatan dimensi citra masukan, rasio percepatan filter Sobel memperlihatkan penurunan dari resolusi 512 × 512 piksel ke 1024 × 1024 piksel (median *speedup* turun dari 4,04× ke 2,26×; rerata 2,30×). Pada dimensi 1024 × 1024 piksel, ukuran partisi data per pekerja melampaui kapasitas L2 cache privat 1,25 MB sehingga memicu *capacity misses*, disertai pembengkakan volume transmisi data IPC. Pada resolusi yang lebih tinggi (2048 × 2048 hingga 4096 × 4096 piksel), percepatan filter Sobel terdistribusi pada kisaran 2,08× hingga 2,87×.

Evaluasi lintas skenario menunjukkan bahwa nilai percepatan pada sel 2048 × 2048 piksel (P = 4) bervariasi antar-blok pengujian: median *speedup* bernilai 2,08× (rerata 2,21×) pada Skenario A, 2,87× (rerata 2,74×) pada Skenario B, dan 2,68× (rerata 2,59×) pada Skenario C. Variasi ini mencerminkan pengaruh pergeseran keterulangan (*repeatability drift*) akibat perbedaan suhu awal prosesor antar-skenario. Sementara itu, pada resolusi 4096 × 4096 piksel (Skenario A), percepatan tercatat sebesar 2,82× (rerata 2,85×) dengan efisiensi 70,59%. Keuntungan utama pemrosesan paralel pada resolusi 4096 × 4096 piksel terletak pada penghematan waktu absolut, yaitu mereduksi durasi eksekusi dari 2,62 detik (serial) menjadi 0,94 detik (paralel), dengan proporsi *overhead* terhadap waktu serial menurun dari sekitar 21% pada resolusi 2048 piksel menjadi 10,6% pada resolusi 4096 piksel.

Penjelasan mengenai pengaruh hierarki memori cache terhadap rasio percepatan ini berstatus sebagai hipotesis ilmiah yang konsisten dengan data empiris, bukan bukti pengukuran instrumentasi langsung. Pengujian ini tidak mengukur tingkat kegagalan cache (cache miss rate) secara langsung melalui *hardware performance counters* (seperti Intel VTune atau *Linux perf*) dan tidak menerapkan penguncian afinitas inti (core affinity pinning) guna mengontrol penempatan proses pekerja. Keterbatasan metodologis ini dicatat pada Subbab 5.5.5.


### Karakteristik Skalabilitas Worker, Arsitektur Hibrida, dan Diminishing Returns

Pengujian Skenario B mengevaluasi perilaku penskalaan kuat (*strong scaling*) sistem ketika alokasi proses pekerja ditingkatkan secara bertahap (P ∈ {1, 2, 4, 8}) pada dimensi citra konstan 2048 × 2048 piksel. Data empiris memperlihatkan penurunan efisiensi marjinal (*diminishing returns*) pada seluruh algoritma filter, dengan titik saturasi teramati pada filter Sobel ketika alokasi ditingkatkan dari empat ke delapan proses pekerja.


#### 1. Titik Plato pada Filter Sobel di P = 8

Pada filter Sobel, penambahan pekerja dari P = 2 ke P = 4 menghasilkan peningkatan percepatan: median waktu eksekusi berkurang dari 0,3477 detik menjadi 0,2087 detik, meningkatkan median *speedup* dari 1,76× ke 2,87× (rerata 2,74×) dengan efisiensi 71,84%.

Ketika alokasi pekerja ditingkatkan dari P = 4 ke P = 8, peningkatan percepatan terhenti. Median waktu eksekusi paralel hanya bergeser sebesar 0,0026 detik (dari 0,2087 detik menjadi 0,2061 detik), dan median *speedup* hanya berubah dari 2,8738× ke 2,8783× (perbedaan marjinal +0,0045× yang tidak signifikan secara statistik, p = 0,15 pada uji Mann–Whitney). Di sisi lain, efisiensi komputasi menurun dari 71,84% menjadi 35,98%, sementara median durasi *overhead* sistem meningkat dari 0,0596 detik menjadi 0,1320 detik (kenaikan bersih +0,0724 detik). Persentase utilisasi CPU global sistem meningkat dari 39,94% ke 70,49%, mencerminkan peningkatan aktivitas komputasi latar belakang tanpa memberikan reduksi waktu pemrosesan yang sebanding.

Perilaku ini menunjukkan deviasi terhadap model teoretis Hukum Amdahl. Menggunakan estimasi fraksi paralel f = 0,79 pada filter Sobel, model Hukum Amdahl memproyeksikan rasio percepatan teoretis sebesar 3,24× pada P = 8. Capaian empiris rata-rata berada pada angka 2,88× (defisit 0,36× terhadap batas teoretis), mengindikasikan adanya faktor penghambat koordinasi pada alokasi pekerja tinggi.


#### 2. Hipotesis Pengaruh Arsitektur Prosesor Hibrida (P-Core dan E-Core)

Salah satu penjelasan potensial mengenai munculnya titik plato pada P = 8 berkaitan dengan karakteristik mikroarsitektur prosesor *Intel Core i5-13420H*. Prosesor ini memiliki delapan inti fisik heterogen yang terbagi menjadi dua kluster: empat *Performance-Cores* (*P-Cores*, arsitektur *Golden Cove*) dengan frekuensi turbo hingga 4,6 GHz dan L2 cache privat 1,25 MB per inti, serta empat *Efficient-Cores* (*E-Cores*, arsitektur *Gracemont*) dengan frekuensi turbo maksimum 3,4 GHz, kapasitas instruksi per siklus (IPC) lebih rendah, dan berbagi pakai 2 MB L2 cache per kluster.

Pada alokasi P = 2 dan P = 4, beban kerja proses pekerja kemungkinan besar diprioritaskan oleh penjadwal sistem operasi dan *Intel Thread Director* pada kluster *P-Core* yang berkinerja lebih tinggi, sehingga proses pekerja mengeksekusi komputasi dengan laju yang relatif seimbang.

Pada alokasi P = 8, sistem melibatkan seluruh delapan inti fisik yang tersedia, memadukan 4 *P-Core* dan 4 *E-Core* secara bersamaan. Skema partisi pada sistem ini menerapkan dekomposisi spasial statis (*static row partitioning*), membagi matriks citra 2048 baris secara seragam menjadi delapan blok yang masing-masing memuat 256 baris piksel (ditambah baris batas halo).

Pembagian beban kerja statis seragam pada prosesor heterogen berpotensi memicu ketimpangan waktu penyelesaian (*load imbalance*). Pekerja yang dialokasikan pada *P-Core* (frekuensi hingga 4,6 GHz) menyelesaikan pemrosesan blok lebih cepat dibandingkan pekerja yang berjalan pada *E-Core* (frekuensi 3,4 GHz). Karena pemanggilan *multiprocessing.Pool.map()* menerapkan pembatas sinkronisasi (*synchronous barrier*), proses utama harus menunggu hingga pekerja pada *E-Core* menyelesaikan tugasnya sebelum dapat menjalankan rekonstruksi *numpy.vstack()*. Waktu tunggu ini berpotensi membatasi penambahan percepatan pada P = 8.


#### 3. Karakteristik Efisiensi dan Evaluasi Metrik Karp–Flatt

Penurunan efisiensi paralel seiring bertambahnya alokasi pekerja teramati pada ketiga jenis filter. Pada Grayscale, efisiensi menurun dari 69,33% (P = 2) menjadi 49,38% (P = 4) dan 31,88% (P = 8). Pada Gaussian Blur, efisiensi menurun dari 80,27% (P = 2) menjadi 57,73% (P = 4) dan 36,20% (P = 8). Pada Sobel, efisiensi menurun dari 87,88% (P = 2) menjadi 71,84% (P = 4) dan 35,98% (P = 8). Pada P = 8, efisiensi ketiga filter berada pada rentang 32% hingga 36%.

Evaluasi menggunakan metrik fraksi serial eksperimental Karp–Flatt (e) memperlihatkan perbedaan perilaku antar-filter. Pada filter Sobel, nilai e berbasis rerata bernilai 0,1292 (P = 2), 0,1535 (P = 4), dan meningkat menjadi 0,2272 pada P = 8 (berbasis median: 0,1379 pada P = 2, 0,1306 pada P = 4, dan 0,2542 pada P = 8). Sebaliknya, pada Gaussian Blur, nilai e relatif stabil pada kisaran 0,2474 (P = 2), 0,2499 (P = 4), dan 0,2520 (P = 8). Pada Grayscale, nilai e justru mengalami penurunan dari 0,4376 (P = 2) menjadi 0,3662 (P = 4) dan 0,3168 (P = 8).

Karakteristik metrik Karp–Flatt tersebut menunjukkan bahwa peningkatan fraksi serial efektif pada P = 8 hanya teramati secara nyata pada filter Sobel. Perbedaan respons antar-filter ini mengindikasikan bahwa hambatan pada P = 8 tidak semata disebabkan oleh heterogenitas inti fisik, melainkan merupakan interaksi antara waktu komputasi lokal, alokasi larik perantara, dan biaya transmisi data antar-proses.


### Karakteristik Beban Tambahan (Overhead) Serialisasi IPC dan Utilisasi CPU

Pengujian Skenario C dirancang untuk menganalisis beban koordinasi internal sistem pada kondisi resolusi 2048 × 2048 piksel dan alokasi pekerja tetap (P = 4) dengan memvariasikan karakteristik algoritma: konversi Grayscale (operasi titik), penghalusan Gaussian Blur 3 × 3 (konvolusi spasial tiga kanal), dan deteksi tepi Sobel 3 × 3 (konvolusi gradien ganda). Evaluasi berfokus pada dua parameter: durasi beban tambahan paralel (T_*overhead*) dan persentase utilisasi prosesor.


#### 1. Karakteristik Beban Tambahan Komunikasi IPC dan Alokasi Memori

Berdasarkan data empiris Skenario C sebagaimana disajikan pada Gambar 5.3(a), durasi beban tambahan paralel (T_*overhead*) menunjukkan perbedaan antar-filter. Grayscale mencatatkan median *overhead* terendah sebesar 0,0294 detik (rerata 0,0337 ± 0,0138 detik, interval kepercayaan 95% [0,0286; 0,0389] detik). Gaussian Blur mencatatkan median *overhead* tertinggi sebesar 0,0924 detik (rerata 0,1129 ± 0,0563 detik, interval kepercayaan 95% [0,0919; 0,1339] detik). Sobel menghasilkan median *overhead* moderat sebesar 0,0695 detik (rerata 0,0849 ± 0,0445 detik, interval kepercayaan 95% [0,0683; 0,1015] detik).

Durasi *overhead* Gaussian Blur lebih tinggi dibandingkan Sobel meskipun Sobel memiliki tahapan kalkulasi gradien horizontal dan vertikal. Pada modul *multiprocessing*, parameter T_*overhead* mencakup latensi pengaliran pipa antar-proses (IPC *pipe latency*), serialisasi dan deserialisasi objek larik NumPy (*pickle*), alokasi memori larik lokal pada pekerja, serta rekonsiliasi akhir melalui *numpy.vstack()*.

Perbedaan durasi *overhead* tersebut sejalan dengan volume muatan data (payload size) yang ditransmisikan. Pada filter Gaussian Blur, setiap pekerja menerima irisan masukan berukuran (512 + 2) × 2048 × 3 bita (sekitar 3,16 MB) dan mengembalikan matriks luaran tiga kanal berukuran 512 × 2048 × 3 bita (sekitar 3,15 MB), sehingga total volume luaran yang diserialisasi oleh keempat pekerja via *pickle* dan digabungkan kembali oleh proses utama mencapai 12,58 MB. Pada filter Sobel, konversi ke derajat keabuan dilakukan di dalam memori pekerja sebelum perhitungan gradien, sehingga luaran akhir berupa matriks monokromatik satu kanal berukuran 512 × 2048 × 1 bita (sekitar 1,05 MB) dengan total volume luaran kembalian sebesar 4,19 MB — sepertiga dari volume keluaran Gaussian Blur. Pada filter Grayscale, ketiadaan penambahan lapisan batas (k = 0) dan ringkasnya matriks kembalian (total 4,19 MB) menghasilkan nilai *overhead* terendah pada angka 0,0294 detik.

Meskipun demikian, perbedaan durasi *overhead* antara Sobel (0,0695 detik) dan Grayscale (0,0294 detik) pada volume luaran kembalian yang sama (4,19 MB) menunjukkan bahwa T_*overhead* tidak semata merefleksikan transmisi IPC murni, melainkan juga memuat alokasi memori larik perantara float64 dan waktu komputasi tambahan di tingkat pekerja.


#### 2. Karakteristik dan Batasan Interpretasi Utilisasi CPU

Pengukuran beban prosesor melalui modul *psutil* pada Gambar 5.3(b) memperlihatkan perbedaan pola utilisasi. Grayscale menghasilkan rerata utilisasi CPU sistem sebesar 30,57% (median 28,18%, rentang interkuartil [23,15% – 35,72%]). Gaussian Blur menghasilkan rerata 44,17% (median 44,17%, rentang interkuartil [38,41% – 48,68%]). Sobel menghasilkan rerata 43,34% (median 40,11%, rentang interkuartil [37,03% – 48,16%]).

Angka utilisasi CPU yang dilaporkan oleh pustaka *psutil* berstatus sebagai tren indikatif kasar agregat sistem, bukan pengukuran deterministik per proses pekerja. Hal ini disebabkan oleh mekanisme pemantauan *psutil* yang mengambil percontohan berkala beban CPU global sistem pada interval waktu diskret 20 milidetik, tanpa memisahkan kontribusi spesifik masing-masing sub-proses pekerja *multiprocessing*.

Pada Grayscale, durasi eksekusi paralel murni (T_paralel) hanya berlangsung selama 0,0620 detik (62 milidetik). Melalui interval percontohan kelas CPUMonitor sebesar 20 milidetik, pemantau hanya sempat mengambil sekitar 3 titik sampel. Akibatnya, estimasi utilisasi lebih rentan terhadap fluktuasi transien sistem. Sebaliknya, durasi komputasi paralel Gaussian Blur (0,2532 detik) dan Sobel (0,2110 detik) berlangsung lebih panjang sehingga tertangkap oleh sekitar 10 hingga 13 siklus percontohan *psutil*, menghasilkan nilai utilisasi sistem yang stabil di kisaran 40% hingga 44%.

Nilai utilisasi sistem 40% hingga 44% diinterpretasikan dalam konteks kapasitas total prosesor *Intel Core i5-13420H* yang mengekspos 12 utas logis ke sistem operasi Windows 11 (4 *P-Cores* dengan *Hyper-Threading* = 8 utas logis, ditambah 4 *E-Cores* tanpa *Hyper-Threading* = 4 utas logis). Beban empat proses pekerja secara teoretis menyumbang setidaknya 4/12 × 100% = 33,33% dari kapasitas total utas logis sistem.

Capaian utilisasi aktual sebesar 40% hingga 44% mengindikasikan adanya pemanfaatan komputasi multi-inti yang aktif selama fase paralel berlangsung, dengan sisa persentase utilisasi di atas 33,33% merepresentasikan aktivitas proses sistem operasi dan thread pemantau latar belakang.


### Komparasi Temuan terhadap Penelitian Terdahulu

Hasil pengujian dikomparasikan terhadap literatur rujukan utama yang telah dipetakan pada Bab 2, mencakup kajian komputasi paralel berbasis memori bersama *OpenMP*, akselerasi GPU, serta model konkurensi CPython.


#### 1. Komparasi terhadap Model Konkurensi Python (Gultom dan Sarumaha, 2025)

Gultom dan Sarumaha (2025) menguji efektivitas modul *multithreading* dan *multiprocessing* CPython pada beban komputasi numerik berulang hingga 120 juta iterasi. Penelitian tersebut menunjukkan bahwa batasan Global Interpreter Lock (GIL) menyebabkan *multithreading* hanya menghasilkan percepatan marjinal sekitar 1,05×, sedangkan *multiprocessing* menghasilkan *speedup* 3,16× hingga 3,55× pada alokasi empat proses pekerja.

Rasio percepatan pada penelitian ini pada empat pekerja (resolusi 2048 × 2048 piksel) berada pada kisaran 1,90× hingga 2,74×, lebih rendah dibandingkan capaian Gultom dan Sarumaha. Perbedaan ini kemungkinan besar bersumber dari perbedaan karakteristik beban kerja dan platform pengujian. Beban kerja Gultom dan Sarumaha berupa kalkulasi skalar numerik dengan volume data komunikasi yang sangat kecil. Sebaliknya, penelitian ini memproses matriks citra berukuran jutaan piksel, saat setiap pekerja harus menerima dan mengembalikan larik data berukuran megabita melalui saluran pipa IPC. Serialisasi objek NumPy via *pickle* dan penggabungan akhir via *numpy.vstack()* menyita waktu terukur yang membatasi percepatan pada pengolahan citra digital.


#### 2. Komparasi terhadap Model Memori Bersama OpenMP (Cremel dan Arruda, 2026)

Cremel dan Arruda (2026) mengevaluasi akselerasi filter spasial citra termasuk deteksi tepi menggunakan pustaka *OpenMP* berbasis bahasa C/C++ pada CPU multi-core. Model berbasis utas *OpenMP* beroperasi pada satu ruang alamat memori bersama sehingga tidak memerlukan serialisasi objek. Meskipun demikian, Cremel dan Arruda melaporkan bahwa efisiensi paralel *OpenMP* pada deteksi tepi mengalami penurunan pada alokasi delapan utas (efisiensi sekitar 24%) akibat keterbatasan lebar pita memori (memory bandwidth bottleneck).

Hasil pengujian Skenario B pada penelitian ini memperlihatkan kecenderungan penurunan efisiensi yang sejalan pada alokasi delapan pekerja (P = 8), dengan efisiensi Sobel turun menjadi 35,98% dan Gaussian Blur menjadi 36,20%. Penurunan efisiensi pada sistem ini dipengaruhi oleh kombinasi faktor heterogenitas frekuensi clock *P-Core* dan *E-Core*, transmisi pipa IPC, serta perebutan lebar pita bus memori utama.

Terdapat perbedaan pola skalabilitas resolusi antara penelitian ini dan temuan Cremel dan Arruda. Cremel dan Arruda melaporkan bahwa rasio percepatan meningkat seiring kenaikan resolusi citra secara monoton. Sebaliknya, pada penelitian ini, rasio percepatan tertinggi filter Sobel tercapai pada resolusi kecil (512 × 512 piksel) akibat partisi kerja tertampung pada memori cache L2 privat, sebelum kemudian menurun dan mendatar pada resolusi 1024 hingga 4096 piksel.


#### 3. Komparasi terhadap Akselerasi GPU (Chang et al., 2023)

Chang et al. (2023) melaporkan penerapan operator Sobel pada GPU NVIDIA berbasis CUDA dengan capaian percepatan 6,7× hingga 13,0× terhadap pustaka *OpenCV-GPU* standar. Di sisi lain, literatur komputasi paralel GPU (Ibrahim et al., 2021; Vasile et al., 2024) mencatat bahwa akselerasi GPU memiliki beban tambahan transfer data antara memori host (RAM) dan memori perangkat grafis (VRAM) melalui bus PCIe.

Perilaku transfer data tersebut memperlihatkan kesamaan konseptual dengan beban transmisi pipa IPC pada CPU *multiprocessing* dalam penelitian ini. Pada citra berdimensi kecil, durasi *overhead* transmisi menyita proporsi yang cukup terasa terhadap total waktu eksekusi. Keuntungan praktis pemrosesan paralel CPU terlihat pada citra beresolusi tinggi (4096 × 4096 piksel), dengan reduksi waktu eksekusi Sobel dari 2,62 detik (serial) menjadi 0,94 detik (paralel).

Perlu dicatat bahwa perbandingan nilai percepatan antara penelitian ini (2,85× pada 4096 piksel dan 4,04× pada 512 piksel) dan hasil Chang et al. (6,7× hingga 13,0×) tidak berada pada dasar pembanding yang setara, karena penelitian ini menggunakan baseline serial CPU NumPy sedangkan Chang et al. menggunakan baseline pustaka *OpenCV-GPU*. Pendekatan *multiprocessing* CPU Python murni menawarkan keunggulan berupa ketiadaan ketergantungan pada perangkat keras GPU diskret dan driver berpemilik (proprietary), sehingga lebih mudah diimplementasikan pada lingkungan komputasi berdaya rendah.

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


#### 1. Sintesis Jawaban Rumusan Masalah


**Jawaban Rumusan Masalah 1: Pengaruh Resolusi Citra terhadap Speedup dan Efisiensi**

Peningkatan resolusi citra masukan menghasilkan respons skalabilitas yang dipengaruhi oleh ukuran partisi kerja dan volume transmisi data IPC. Pada filter Sobel (P = 4), percepatan mendekati batas linier ideal pada dimensi 512 × 512 piksel (median 4,04×, rerata 3,89×, efisiensi median 101,02%) sejalan dengan hipotesis partisi data tertampung di dalam L2 cache privat *P-Core* (1,25 MB). Percepatan menurun pada resolusi 1024 × 1024 piksel (median 2,26×) seiring terjadinya *capacity misses* pada L2 cache dan peningkatan volume IPC, kemudian berada pada rentang 2,08× hingga 2,87× pada resolusi 2048 dan 4096 piksel dengan reduksi waktu absolut terbesar terjadi pada resolusi 4096 piksel (dari 2,62 detik menjadi 0,94 detik). Pada konversi Grayscale, percepatan terdistribusi datar pada rentang 1,52× hingga 2,12× di seluruh resolusi karena karakteristik operasi terikat memori (*memory-bound*) dengan batasan transfer memori DRAM DDR5.

Pada filter Gaussian Blur, intensitas komputasi yang lebih tinggi (8,50 FLOP/bita) menghasilkan *speedup* yang moderat (median 2,50× pada 512 piksel hingga 2,31× pada 2048 piksel) karena beban pengaliran matriks luaran tiga kanal RGB (12,58 MB pada citra 2048 piksel) menyita porsi waktu transmisi IPC yang signifikan.


**Jawaban Rumusan Masalah 2: Pola Skalabilitas Alokasi Worker terhadap Batas Teoretis Hukum Amdahl**

Peningkatan alokasi proses pekerja (P ∈ {1, 2, 4, 8}) pada resolusi 2048 × 2048 piksel memperlihatkan pola penurunan efisiensi marjinal. Alokasi pekerja hingga P = 4 menghasilkan peningkatan *speedup* yang stabil (Sobel meningkat dari 1,00× pada P = 1 menjadi 1,76× pada P = 2, dan 2,87× pada P = 4 dengan efisiensi 71,84%). Namun, penambahan alokasi ke P = 8 menghasilkan titik plato pada filter Sobel (*speedup* median 2,88×, perbedaan marjinal +0,0045× yang tidak signifikan secara statistik, p = 0,15), dengan efisiensi turun menjadi 35,98% dan berada di bawah proyeksi Hukum Amdahl teoretis (3,24× pada f = 0,79).

Kenaikan metrik fraksi serial Karp–Flatt (e) dari 0,1306 (P = 4) ke 0,2542 (P = 8) teramati secara spesifik pada filter Sobel, mengindikasikan adanya beban koordinasi tambahan pada P = 8 yang konsisten dengan hipotesis ketimpangan waktu eksekusi antara *P-Core* dan *E-Core* serta pembengkakan waktu transmisi pipa IPC.


**Jawaban Rumusan Masalah 3: Pengaruh Kompleksitas Filter terhadap Overhead IPC dan Utilisasi CPU**

Pengujian Skenario C menunjukkan bahwa durasi beban tambahan (T_*overhead*) sejalan dengan volume muatan data keluaran yang diserialisasi melalui pipa IPC. Gaussian Blur mencatatkan *overhead* tertinggi (median 0,0924 detik) karena mentransmisikan luaran tiga kanal RGB (12,58 MB). Sobel menghasilkan *overhead* moderat (median 0,0695 detik) karena luaran tereduksi menjadi satu kanal monokrom (4,19 MB), dan Grayscale menghasilkan *overhead* terendah (0,0294 detik) karena ketiadaan operasi *boundary halo* (k = 0). Perbedaan *overhead* antara Sobel dan Grayscale pada volume luaran yang sama mengindikasikan bahwa T_*overhead* juga memuat alokasi memori larik perantara lokal pada pekerja.

Pengukuran beban prosesor menggunakan *psutil* pada P = 4 berada pada kisaran 40%–44% dari total 12 utas logis sistem, mengindikasikan aktivitas multi-inti yang aktif selama fase eksekusi paralel. Pada Grayscale, utilisasi terukur lebih rendah (median 28,18%) akibat durasi komputasi yang sangat singkat (62 milidetik) dibandingkan interval percontohan *psutil* 20 milidetik.


**Jawaban Rumusan Masalah 4: Integritas Luaran Citra Bit-Identik**

Integritas luaran citra paralel terjaga secara deterministik melalui penerapan mekanisme *boundary halo* selebar k = 1 piksel dengan metode replikasi batas (*edge replication* padding, *mode='edge'*) pada setiap submatriks partisi, diikuti oleh pemangkasan baris batas (*halo stripping*) sebelum rekonstruksi utuh via *numpy.vstack()*.

Validasi biner terhadap 720 pasangan komparasi non-trivial (serial-paralel) dan 90 pasangan kontrol trivial A/A (total 810 iterasi) menunjukkan status kesetaraan elemen matriks *numpy.array_equal()* = True sebesar 100% dengan nilai disparitas absolut maksimum piksel bernilai nol (Δ_max = 0) pada seluruh citra uji, mengonfirmasi bahwa pembagian baris horizontal dan pertukaran batas spasial tidak menimbulkan distorsi sambungan atau pergeseran indeks.


#### 2. Keterbatasan Penelitian

Penelitian ini memiliki beberapa keterbatasan metodologis dan eksperimental yang perlu dicatat:

Pertama, pengujian dieksekusi secara sekuensial antar-skenario (diawali Skenario A, dilanjutkan B, dan diakhiri C) tanpa pengacakan blok global (no global *randomized block design*). Ketiadaan pengacakan urutan ini memicu fenomena pergeseran keterulangan (*repeatability drift*) yang terlihat dari perbedaan baseline waktu serial Skenario A terhadap B dan C pada konfigurasi identik (citra 2048 × 2048 piksel, P = 4). Selain itu, urutan eksekusi selalu mendahulukan serial sebelum paralel pada setiap repetisi.

Kedua, eksperimen menggunakan satu citra acuan master tunggal yang dipotong secara pemotongan tengah murni (*center-crop*) ke berbagai dimensi (512 × 512 hingga 4096 × 4096 piksel) tanpa proses resampling atau interpolasi. Pendekatan ini menjaga konsistensi visual antarsampel, namun belum mengevaluasi konten citra dengan karakteristik frekuensi spasial dan entropi yang bervariasi.

Ketiga, evaluasi kinerja dijalankan pada satu unit perangkat keras laptop dengan prosesor *Intel Core i5-13420H* (arsitektur hibrida 4 *P-Core* + 4 *E-Core*, 12 utas logis, RAM 16 GB DDR5). Karakteristik skalabilitas yang teramati sangat dipengaruhi oleh konfigurasi perangkat keras ini dan belum divalidasi silang pada arsitektur prosesor homogen (seperti AMD Ryzen) maupun prosesor tingkat peladen.

Keempat, sistem telemetri pengujian tidak merekam sensor suhu silikon (°C) dan frekuensi clock aktual prosesor (GHz) secara kontinu ke dalam berkas data log. Mitigasi termal bertumpu pada suhu ruangan (~24 °C) dan jeda pendinginan selama 0,5 detik (*cool-down buffer*), sehingga fluktuasi termal mikro tidak tercatat secara numerik per iterasi.

Kelima, sistem tidak menerapkan penguncian afinitas proses pekerja ke inti fisik tertentu (*psutil.Process().cpu_affinity()*). Penempatan proses dikelola oleh penjadwal Windows 11 dan *Intel Thread Director*, sehingga migrasi proses antar-inti dapat memengaruhi variansi latensi.

Keenam, analisis mengenai kontribusi memori cache L2 dan L3 terhadap percepatan pada resolusi 512 × 512 piksel berstatus sebagai hipotesis ilmiah berbasis analisis ukuran partisi kerja (*working set analysis*), bukan hasil pencatatan langsung dari unit pencacah kinerja perangkat keras (*hardware performance counters*).

Ketujuh, pengujian difokuskan pada filter spasial independen (*embarrassingly parallel*) dengan kernel lokal 3 × 3. Karakteristik ini tidak dapat digeneralisasi langsung pada operasi citra non-lokal atau konvolusi kernel berukuran besar (7 × 7 ke atas).


# BAB 6 PENUTUP

Bab ini menyajikan kesimpulan yang ditarik dari hasil pengujian empiris dan analisis kinerja komparasi filter spasial menggunakan Python *multiprocessing*, diikuti oleh saran untuk pengembangan penelitian selanjutnya.


## 6.1 Kesimpulan

Berdasarkan serangkaian pengujian sebanyak 810 iterasi (mencakup 720 pasangan komparasi non-trivial serial-paralel dan 90 pasangan kontrol A/A) pada prosesor *Intel Core i5-13420H*, diperoleh empat kesimpulan pokok:

1. Pada filter Sobel (P = 4), percepatan mendekati batas linier pada resolusi 512 × 512 piksel (median 4,04×, rerata 3,89× [CI 95%: 3,58; 4,20]) dan terdistribusi pada kisaran 2,2× hingga 2,9× pada resolusi 1024 hingga 4096 piksel. Perbedaan hasil antar-blok pengujian pada resolusi 2048 piksel (2,21× pada Blok A, 2,74× pada Blok B, dan 2,59× pada Blok C) menunjukkan bahwa variasi keterulangan termal memengaruhi capaian percepatan. Percepatan pada 512 piksel konsisten dengan hipotesis bahwa partisi per pekerja tertampung di dalam cache L2 privat, meskipun tidak diukur melalui instrumentasi langsung. Pada konversi Grayscale, median percepatan berada pada rentang 1,52× hingga 2,12× di seluruh resolusi.

2. Pada dimensi citra konstan 2048 × 2048 piksel, percepatan filter Sobel meningkat dari 1,76× (P = 2) ke 2,87× (P = 4), dan tidak berbeda secara signifikan antara P = 4 dan P = 8 (p = 0,15 pada uji Mann–Whitney), sementara efisiensi menurun dari 71,84% ke 35,98%. Pola data konsisten dengan estimasi model Hukum Amdahl pada fraksi paralel efektif f = 0,69 hingga 0,79 sesuai jenis filter. Kenaikan metrik fraksi serial Karp–Flatt teramati secara nyata pada filter Sobel (dari 0,1306 ke 0,2542), saat heterogenitas inti *P-Core* dan *E-Core* serta pembengkakan koordinasi IPC menjadi penjelasan yang konsisten dengan data.

3. Durasi beban tambahan (*overhead*) pada P = 4 dan resolusi 2048 × 2048 piksel berurutan: Gaussian Blur (median 0,0924 detik) > Sobel (0,0695 detik) > Grayscale (0,0294 detik). Urutan ini sejalan dengan volume muatan luaran kembalian (12,58 MB pada Gaussian Blur vs 4,19 MB pada Sobel dan Grayscale) serta alokasi memori larik perantara lokal pada pekerja. Sementara itu, persentase utilisasi CPU global *psutil* berada pada kisaran 40%–44% yang merefleksikan aktivitas komputasi multi-inti pada prosesor.

4. Penerapan dekomposisi domain spasial horizontal dengan mekanisme *boundary halo* padding selebar k = 1 piksel bermetode replikasi tepi (*edge replication*, *mode='edge'*) dan pemangkasan batas (*halo stripping*) menjaga integritas rekonstruksi citra secara konsisten. Seluruh 720 pasangan pengujian serial-paralel dan 90 pasangan kontrol A/A menghasilkan kesetaraan matriks biner deterministik *numpy.array_equal()* = True sebesar 100% dengan disparitas absolut maksimum nol (Δ_max = 0) pada seluruh citra uji.


## 6.2 Saran

Berdasarkan temuan empiris dan analisis keterbatasan yang diperoleh, diajukan beberapa saran untuk penelitian lanjutan:

1. Mengevaluasi skema pembagian beban dinamis (*dynamic chunk scheduling* atau *work-stealing pool*) dengan mengalokasikan porsi baris lebih banyak dibandingkan jumlah pekerja guna mengurangi potensi waktu tunggu sinkronisasi pada prosesor berarsitektur heterogen (*P-Core* dan *E-Core*).

2. Mengurangi beban tambahan serialisasi data antar-proses dengan memanfaatkan arsitektur memori bersama (*shared memory* via *multiprocessing.shared_memory*) atau pemetaan berkas ke memori (*memory-mapped files*, *mmap*) agar proses utama dan pekerja dapat berbagi akses larik citra tanpa penalti waktu serialisasi *pickle*.

3. Menerapkan mekanisme penguncian afinitas proses pekerja ke inti fisik prosesor (core affinity pinning via *psutil.Process().cpu_affinity()*) dengan memilih satu utas per *P-Core* setelah memeriksa topologi prosesor guna meminimalkan migrasi proses antar-inti (*thread hopping*).

4. Menyempurnakan protokol eksperimen dengan mengintegrasikan pencatatan telemetri suhu silikon (°C) dan frekuensi aktual prosesor (GHz) secara kontinu, menerapkan pengacakan urutan blok pengujian (*randomized block design*) guna mengurangi bias termal awal, serta memanfaatkan *hardware performance counters* untuk mengukur laju *cache misses* secara empiris.

5. Memperluas evaluasi komparatif ke akselerasi komputasi berbasis unit pengolah grafis (GPU) menggunakan pustaka seperti *CuPy* atau *PyTorch CUDA*, serta vektorisasi instruksi SIMD (AVX2) pada CPU untuk memetakan titik impas performa pada citra beresolusi sangat tinggi.
