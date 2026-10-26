# BAB 2 LANDASAN TEORI


## Perbandingan Terhadap Penelitian Terdahulu

Akselerasi proses komputasi pada visi komputer dan pengolahan citra digital telah menjadi fokus kajian intensif seiring dengan eksponensialnya pertumbuhan resolusi citra modern (Cremel & Arruda, 2026). Dalam menangani beban komputasi konvolusi matriks yang masif, berbagai penelitian terdahulu mengarahkan fokus implementasi pada unit pemrosesan grafis (GPU). Chang et al. (2023) meneliti penerapan operator Sobel multi-arah dengan ukuran kernel besar (5 × 5 dan 7 × 7) dan membuktikan bahwa akselerasi GPU berbasis CUDA mampu menghasilkan rasio percepatan (speedup) sebesar 6,7 hingga 13,0 kali lipat dibandingkan pustaka OpenCV-GPU standar. Dari perspektif arsitektur perangkat keras, Vasile et al. (2024) menegaskan bahwa sistem visi komputer beresolusi tinggi menuntut penanganan aliran data (data stream) secara real-time, di mana arsitektur CPU serial konvensional memiliki keterbatasan laten dalam memenuhi ambang batas waktu respons akibat ketergantungan memori dan keterbatasan instruksi per siklus.

Pada ranah prosesor multi-core, eksplorasi komputasi paralel umumnya memanfaatkan model shared memory berbasis utas (threading). Cremel dan Arruda (2026) mengevaluasi akselerasi filter spasial citra (Grayscale, Gaussian Blur, dan Sobel) menggunakan pustaka OpenMP pada bahasa C/C++. Temuan mereka menunjukkan bahwa rasio percepatan dan efisiensi meningkat seiring dengan bertambahnya dimensi matriks citra, namun efisiensi paralel mengalami degradasi tajam saat jumlah utas ditingkatkan hingga 8 utas, di mana efisiensi pada deteksi tepi Sobel merosot hingga mencapai sekitar 24%. Ibrahim et al. (2021) turut memperkuat karakteristik tersebut melalui komparasi konvolusi Gaussian Blur 2D pada CPU multi-core dan GPU, yang menyimpulkan bahwa beban tambahan (overhead) transfer memori mendominasi waktu total pada matriks berukuran kecil hingga menengah, sehingga keuntungan komputasi paralel baru tercapai secara optimal pada matriks berdimensi besar.

Di sisi lain, implementasi komputasi paralel pada bahasa pemrograman Python menghadapi kendala arsitektural yang unik berupa Global Interpreter Lock (GIL) pada rilis resmi CPython (Python Software Foundation, n.d.-a). Gultom dan Sarumaha (2025) membuktikan secara empiris bahwa GIL membatasi eksekusi instruksi Python hanya pada satu utas dalam satu waktu, sehingga paradigma multithreading pada beban kerja intensif komputasi (CPU-bound) hanya menghasilkan rasio percepatan marjinal sekitar 1,05 kali lipat. Sebaliknya, modul multiprocessing mampu mendistribusikan beban komputasi secara efektif ke banyak inti prosesor fisik melalui alokasi ruang memori (address space) dan interpreter independen, dengan pencapaian speedup mencapai 3,16 hingga 3,55 kali lipat pada alokasi empat proses pekerja (Gultom & Sarumaha, 2025; Tanenbaum & Bos, 2022).

Meskipun demikian, kajian pustaka terdahulu memperlihatkan adanya kesenjangan penelitian (research gap) yang mendasar. Sebagian besar penelitian filter citra paralel pada CPU berbasis prosesor simetris seragam dengan model memori bersama OpenMP (Cremel & Arruda, 2026). Karakteristik skalabilitas modul multiprocessing Python—yang melibatkan beban komunikasi antar-proses (inter-process communication / IPC), serialisasi objek matriks (pickling), replikasi baris batas (boundary halo), serta rekonstruksi citra—belum dievaluasi secara komprehensif pada arsitektur prosesor heterogen modern yang memadukan inti kinerja tinggi (Performance-Core) dan inti hemat daya (Efficient-Core). Selain itu, pengujian terdahulu umumnya mengabaikan fluktuasi derau sistem operasi dan belum mengonfirmasi integritas bit-identik secara deterministik. Pada rancangan penelitian ini, evaluasi dilakukan secara mendalam terhadap tiga variasi filter spasial bertingkat pada rentang resolusi 512 × 512 hingga 4096 × 4096 piksel, memetakan metrik kinerja empiris terhadap batas teoretis Hukum Amdahl dan metrik Karp–Flatt, serta menerapkan pengujian kontrol A/A untuk mengukur ambang batas derau sistem (system noise floor).

Tabel 2.1 Perbandingan Penelitian Terdahulu Terkait Akselerasi Pengolahan Citra Digital



| Peneliti & Tahun | Paradigma / Perangkat | Filter yang Diuji | Temuan Utama | Posisi dan Perbedaan Penelitian Ini |
| --- | --- | --- | --- | --- |
| Chang et al. (2023) | Akselerasi GPU (NVIDIA CUDA) | Sobel multi-arah kernel besar (5 × 5, 7 × 7) | Akselerasi GPU menghasilkan speedup 6,7× hingga 13,0× dibanding OpenCV-GPU standar; komputasi konvolusi turunan terbukti menjadi beban komputasi masif pada resolusi tinggi. | Menguji arsitektur CPU multi-core heterogen berbasis Python multiprocessing; fokus mengevaluasi overhead komunikasi IPC dan batas derau sistem. |
| Vasile et al. (2024) | CPU Single-Core vs Hardware Acceleration | Konvolusi 2D spasial generik | Pengolahan citra beresolusi tinggi secara real-time menuntut efisiensi penanganan aliran data; arsitektur CPU serial konvensional tidak mampu memenuhi latensi target. | Menerapkan dekomposisi data spasial pada CPU multi-core untuk mengatasi keterbatasan CPU serial tanpa akselerator khusus (FPGA/ASIC). |
| Cremel & Arruda (2026) | CPU Multi-Core (OpenMP C/C++) | Grayscale, Gaussian Blur, Sobel | Speedup dan efisiensi meningkat seiring dimensi citra, namun efisiensi menurun tajam pada 8 utas (efisiensi Sobel merosot hingga ~24%). | Mengevaluasi multiprocessing Python dengan ruang memori terpisah dan kendala GIL, dibandingkan model memori bersama OpenMP. |
| Ibrahim et al. (2021) | CPU Multi-Core & GPU | Gaussian Blur 2D | Peningkatan resolusi citra memperbesar skalabilitas paralel; overhead transfer data mendominasi pada citra kecil hingga menengah. | Meneliti rentang resolusi 512×512 hingga 4096×4096 px pada CPU hibrida modern serta mengukur overhead IPC dan kontrol A/A secara kuantitatif. |
| Gultom & Sarumaha (2025) | CPU Multi-Core (Python CPython) | Operasi citra CPU-bound | Multithreading Python dibatasi GIL (speedup hanya ~1,05×), sedangkan multiprocessing mencapai speedup 3,16–3,55× pada 4 proses. | Memperluas evaluasi ke P = 1, 2, 4, 8 proses pada prosesor hibrida P/E-Core, pencocokan Amdahl, Karp–Flatt, dan verifikasi bit-identik. |
| Penelitian Ini (2026) | CPU Multi-Core Hibrida (Python Multiprocessing) | Grayscale, Gaussian Blur 3×3, Sobel 3×3 | Memetakan speedup, efisiensi, overhead IPC, utilisasi CPU, kecocokan Amdahl, metrik Karp–Flatt, dan integritas bit-identik (Δmax = 0). | Komparasi komprehensif pengaruh resolusi, jumlah pekerja, dan kompleksitas filter pada prosesor Intel Raptor Lake dengan hierarki 12 MB L3 Smart Cache. |


Berdasarkan sintesis pada Tabel 2.1, posisi penelitian ini adalah melengkapi pemahaman empiris mengenai efektivitas dan batasan skalabilitas komputasi paralel berbasis multiprocessing Python pada prosesor multi-core modern. Analisis difokuskan pada interaksi antara beban komputasi per piksel, beban transmisi data antar-proses, dan karakteristik hierarki memori cache sistem.


## Pengolahan Citra Digital dan Operasi Filter Spasial

Pengolahan citra digital merupakan disiplin rekayasa yang memanipulasi data piksel dalam format matriks diskret untuk berbagai tujuan, seperti perbaikan kualitas visual citra (image enhancement), penajaman kontras, penekanan derau (noise reduction), maupun ekstraksi fitur penting untuk analisis lebih lanjut (Gonzalez & Woods, 2018). Pada sistem visi komputer, operasi filter spasial memegang peranan krusial sebagai tahap prapemrosesan (preprocessing) yang menentukan akurasi interpretasi visual tahap lanjut. Bagian ini menguraikan representasi matematis citra dan karakteristik operasi konvolusi spasial yang menjadi objek pengujian dalam penelitian ini.


### Representasi Citra Digital dan Operasi Konvolusi 2D

Secara matematis, citra digital monokromatik dimodelkan sebagai fungsi intensitas spasial diskret dua dimensi I(x, y), di mana x dan y merepresentasikan koordinat baris dan kolom spasial, sedangkan I(x, y) menyatakan derajat keabuan (gray level) piksel pada rentang nilai diskret [0, 255] untuk format 8-bit (Gonzalez & Woods, 2018). Pada citra berwarna berformat RGB (Red, Green, Blue), citra direpresentasikan sebagai tensor tiga dimensi berukuran H × W × C, dengan H menyatakan tinggi citra (jumlah baris piksel), W menyatakan lebar citra (jumlah kolom piksel), dan C = 3 menyatakan tiga kanal warna komponen dasar. Dalam lingkungan pemrograman Python menggunakan pustaka NumPy, matriks citra disimpan dalam memori utama dengan urutan berbasis baris (row-major order atau C-contiguous layout). Pada tata letak ini, piksel-piksel yang berada pada baris horizontal yang sama dialokasikan pada alamat memori fisik yang berurutan. Karakteristik ini memaksimalkan lokalitas spasial (spatial locality) perangkat keras, sehingga ketika CPU membaca suatu piksel, baris cache (cache line) berukuran 64 bita akan memuat piksel-piksel di sekitarnya secara bersamaan, yang secara signifikan meminimalkan terjadinya kegagalan pemanggilan data (cache miss) (Pacheco & Malensek, 2022).

Operasi filter spasial linier pada citra digital dilakukan melalui operasi konvolusi diskret dua dimensi (atau korelasi silang diskret) dengan menggeser matriks bobot berukuran kecil yang disebut kernel konvolusi di atas matriks citra masukan (Vasile et al., 2024). Untuk matriks kernel K berukuran ganjil (2k + 1) × (2k + 1) dengan radius spasial k, nilai intensitas piksel luaran I_filter(x, y) dihitung melalui penjumlahan terbobot dari nilai piksel masukan pada area ketetanggaannya, sebagaimana dirumuskan pada Persamaan (2.1):


$$
I_filter(x, y) = ∑(i=-k to k) ∑(j=-k to k) I(x + i, y + j) · K(i, j) \quad (2.1)
$$

Keterangan:

* I_filter(x, y) : Nilai intensitas piksel luaran hasil pemfilteran pada koordinat spasial (x, y).
* I(x + i, y + j) : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (x + i, y + j).
* K(i, j) : Koefisien bobot matriks kernel konvolusi pada posisi relatif (i, j).
* k : Radius spasial matriks kernel (pada matriks kernel berukuran 3 × 3, bernilai k = 1).
* i, j : Indeks koordinat pergeseran spasial kernel secara vertikal dan horizontal.
Ketika pusat matriks kernel berada pada baris atau kolom terluar citra (x = 0, x = H - 1, y = 0, atau y = W - 1), sebagian elemen kernel berada di luar batas fisik matriks citra. Untuk mengatasi kendala ini, diterapkan penanganan batas tepi citra (boundary condition handling). Pada rancangan penelitian ini, penanganan batas tepi menggunakan teknik replikasi tepi (mode edge), di mana nilai intensitas piksel terluar diduplikasi ke area imajiner di luar citra. Metode ini mencegah timbulnya artefak gelap di sepanjang tepi bingkai citra sekaligus menjamin determinisme hasil komputasi antara implementasi serial dan paralel. Secara teoritis, bentuk matematis pada Persamaan (2.1) merupakan korelasi silang diskret yang dalam domain pengolahan citra lazim diidentifikasi sebagai konvolusi spasial (Gonzalez & Woods, 2018). Pada matriks kernel simetris seperti Gaussian, hasil korelasi silang identik secara mutlak dengan konvolusi sejati. Sementara itu, pada operator Sobel yang bersifat anti-simetris, korelasi silang hanya membalikkan tanda aljabar gradien tanpa mengubah magnitudo gradien yang dihasilkan.


### Karakteristik Algoritma Filter Spasial yang Diuji

Penelitian ini menguji tiga algoritma filter spasial dengan karakteristik beban komputasi bertingkat, yang merepresentasikan variasi intensitas kalkulasi matematis terhadap rasio transfer memori:

* Konversi Grayscale (ITU-R BT.601): Merupakan operasi per-piksel murni (point operation) yang mentransformasikan matriks citra RGB tiga kanal menjadi citra derajat keabuan satu kanal. Transformasi ini menghitung intensitas luma (Y) berdasarkan standar persepsi visual manusia ITU-R BT.601: Y(x, y) = 0,299·R(x, y) + 0,587·G(x, y) + 0,114·B(x, y). Operasi ini tidak memiliki ketergantungan terhadap piksel tetangga sama sekali (k = 0), sehingga kompleksitas komputasinya relatif rendah, yaitu hanya 3 perkalian skalar dan 2 penjumlahan per piksel. Tipe data masukan adalah matriks uint8 berdimensi H × W × 3, dan luaran berupa matriks uint8 berdimensi H × W.
* Penghalusan Citra Gaussian Blur 3×3: Merupakan filter linier penghalus spasial (low-pass smoothing filter) yang bertujuan mereduksi derau frekuensi tinggi dan menghaluskan variasi intensitas lokal. Kernel Gaussian berukuran 3 × 3 (k = 1) mengaproksimasi fungsi sebaran normal dua dimensi secara diskret dengan matriks bobot K_Gaussian = [[1, 2, 1], [2, 4, 2], [1, 2, 1]] / 16. Operasi konvolusi dilakukan secara terpisah pada masing-masing kanal warna RGB (C = 3). Setiap piksel luaran membutuhkan 9 perkalian bobot dan 8 penjumlahan per kanal, sehingga secara total melibatkan 27 perkalian dan 24 penjumlahan per piksel masukan RGB. Masukan dan luaran filter berdimensi H × W × 3 dengan tipe data uint8.
* Deteksi Tepi Sobel 3×3: Merupakan filter diferensial non-linier berbasis operator gradien spasial turunan pertama (first-order derivative) untuk menonjolkan batas kontur dan tepi objek. Perhitungan dilakukan pada citra representasi grayscale satu kanal menggunakan dua kernel konvolusi ortogonal berukuran 3 × 3 (k = 1), yaitu kernel gradien horizontal (Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]) dan kernel gradien vertikal (Gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]). Setelah konvolusi kedua gradien selesai, magnitudo gradien total dihitung melalui formulasi modulus Euclidean: G(x, y) = √(Gx(x, y)² + Gy(x, y)²). Nilai magnitudo kemudian dinormalisasi dan dipotong (clipped) ke rentang [0, 255] dengan format data uint8 berdimensi H × W. Kompleksitas komputasi Sobel meliputi 12 operasi perkalian, 12 penjumlahan, 2 pemangkatan kuadrat, 1 penarikan akar kuadrat, serta operasi pemotongan rentang intensitas pada setiap piksel.
Tabel 2.2 Karakteristik Algoritma Filter Spasial yang Diuji



| Nama Filter | Tipe Operasi Spasial | Ukuran Kernel & Radius (k) | Operasi Komputasi per Piksel | Dimensi Kanal Masukan & Luaran | Ketergantungan Baris Batas (Halo) |
| --- | --- | --- | --- | --- | --- |
| Grayscale (ITU-R BT.601) | Operasi Titik (Point Operation) | Tanpa kernel (k = 0) | 3 perkalian, 2 penjumlahan bobot luma (0,299R + 0,587G + 0,114B) | Masukan: H × W × 3 (uint8)<br>Luaran: H × W (uint8) | Tidak memerlukan halo (k = 0) |
| Gaussian Blur 3×3 | Konvolusi Linier Spasial (Smoothing) | Kernel 3 × 3 (k = 1) | 27 perkalian, 24 penjumlahan (9 perkalian dan 8 penjumlahan independen per kanal RGB) | Masukan: H × W × 3 (uint8)<br>Luaran: H × W × 3 (uint8) | Memerlukan 1 baris halo atas dan bawah (k = 1) |
| Sobel 3×3 | Diferensiasi Gradien (Edge Detection) | Dua kernel 3 × 3 (Gx & Gy, k = 1) | 12 perkalian, 12 penjumlahan, 2 pemangkatan kuadrat, 1 penarikan akar kuadrat, dan pemotongan clipping [0, 255] | Masukan: H × W Grayscale (uint8)<br>Luaran: H × W Peta Tepi (uint8) | Memerlukan 1 baris halo atas dan bawah (k = 1) |


Hierarki ketiga filter pada Tabel 2.2 memungkinkan evaluasi komparatif yang sistematis: Grayscale merepresentasikan beban komputasi terendah dengan ketergantungan memori tinggi (memory-bandwidth bound), Gaussian Blur merepresentasikan beban konvolusi kanal jamak dengan volume transfer data terbesar, sedangkan Sobel merepresentasikan beban kalkulasi matematis terberat (compute-bound) dengan keterlibatan fungsi non-linier akar kuadrat.


## Komputasi Paralel dan Multiprocessing Python

Komputasi paralel adalah paradigma pemrosesan informasi di mana sejumlah instruksi atau kalkulasi dieksekusi secara simultan pada beberapa unit pemrosesan fisik untuk mempercepat penyelesaian suatu masalah komputasi (Pacheco & Malensek, 2022). Bagian ini membahas arsitektur dekomposisi data spasial, implementasi pada lingkungan eksekusi Python beserta mitigasi kendala arsitekturalnya, serta karakteristik arsitektur perangkat keras prosesor modern yang melandasinya.


### Paradigma Data Parallelism dan Dekomposisi Domain Spasial

Dalam taksonomi komputasi paralel, terdapat dua strategi pemecahan masalah utama: task parallelism dan data parallelism (Pacheco & Malensek, 2022). Task parallelism mendistribusikan fungsi atau tugas komputasi yang berbeda ke beberapa prosesor, sedangkan data parallelism mendistribusikan elemen-elemen data berukuran besar ke beberapa unit pemrosesan yang masing-masing menjalankan instruksi komputasi yang serupa. Pengolahan filter citra digital merupakan contoh klasik dari permasalahan embarrassingly parallel, di mana setiap piksel atau wilayah spasial citra dapat diproses secara terisolasi tanpa memerlukan pertukaran status perantara antar-unit kerja (Cremel & Arruda, 2026).

Dekomposisi domain spasial pada penelitian ini diterapkan melalui strategi partisi baris horizontal (horizontal row partitioning). Matriks citra berdimensi tinggi H, lebar W, dan kanal C dibagi secara merata di sepanjang sumbu vertikal (sumbu baris) ke dalam P blok data terpisah. Setiap proses pekerja menerima sub-matriks berukuran ⌊H/P⌋ × W × C. Pemilihan partisi berbasis baris horizontal selaras dengan tata letak memori row-major NumPy, di mana setiap blok irisan menempati blok memori yang berurutan secara fisik. Hal ini meminimalkan biaya rekonstruksi data matriks dibandingkan partisi berbasis kolom atau blok dua dimensi (grid partition).

Tantangan utama dekomposisi spasial pada operasi konvolusi adalah ketergantungan data pada perbatasan partisi. Operasi konvolusi dengan kernel beradius k = 1 menuntut ketersediaan piksel tetangga di atas dan di bawah baris terluar blok kerja. Untuk mengatasi hal ini tanpa sinkronisasi interaktif di tengah komputasi, dirancang mekanisme baris batas (boundary halo). Sebelum didistribusikan ke proses pekerja, setiap blok baris diperluas dengan menambahkan k baris tetangga dari blok di sebelahnya. Untuk blok perantara, ditambahkan 1 baris halo di sisi atas dan 1 baris halo di sisi bawah. Khusus untuk blok teratas, perluasan hanya dilakukan pada sisi bawah, sedangkan blok terbawah hanya diperluas pada sisi atas. Pada operasi Grayscale yang bersifat titik, nilai k = 0 sehingga tidak ada penambahan baris batas.

Mekanisme baris batas ini menjamin keamanan konkurensi data secara mutlak. Seluruh proses pekerja hanya membaca (read-only) baris batas tersebut selama proses konvolusi lokal tanpa pernah menulis ulang ke memori bersama, sehingga risiko terjadinya kondisi balapan (race condition) dapat dieliminasi secara inheren. Setelah operasi filter selesai dieksekusi, masing-masing proses pekerja memotong dan membuang (discard) k baris batas dari hasil keluarannya sebelum mengirimkan blok data akhir kembali ke proses utama (master process). Proses utama kemudian menggabungkan kembali seluruh blok secara berurutan menggunakan fungsi numpy.vstack, menghasilkan matriks citra utuh yang memiliki dimensi dan koordinat piksel yang presisi.


### Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC

CPython, implementasi referensi standar bahasa Python, mengandalkan mekanisme manajemen memori berbasis pencacah referensi (reference counting). Untuk mencegah bahaya korupsi memori internal dan konflik alokasi objek saat beberapa utas berjalan serentak, CPython mengimplementasikan Global Interpreter Lock (GIL) (Python Software Foundation, n.d.-a; Tanenbaum & Bos, 2022). GIL adalah mekanisme kunci biner (mutex) yang mewajibkan bahwa hanya satu utas yang diizinkan mengeksekusi bytecode Python pada satu waktu, terlepas dari jumlah inti prosesor fisik yang tersedia pada perangkat keras. Konsekuensinya, pustaka threading standar Python tidak mampu meningkatkan kinerja pada beban komputasi intensif (CPU-bound), sebagaimana dibuktikan oleh Gultom & Sarumaha (2025) yang mencatat rasio percepatan hanya 1,05 kali lipat.

Modul bawaan multiprocessing pada Python dirancang khusus untuk mengatasi keterbatasan GIL dengan mengalihkan paradigma pemrograman dari tingkat utas (multithreading) ke tingkat proses sistem operasi (multiprocessing) (Python Software Foundation, n.d.-b). Alih-alih mengeksekusi beberapa utas di dalam satu interpreter, modul multiprocessing menciptakan beberapa proses sistem operasi independen. Setiap proses pekerja memiliki ruang alamat memori virtual (virtual address space) terisolasi, pencacah referensi privat, dan instansiasi interpreter CPython mandiri (Tanenbaum & Bos, 2022). Dengan arsitektur ini, setiap inti prosesor fisik dapat mengeksekusi proses pekerjanya masing-masing secara serentak tanpa saling terhalang oleh kunci interpreter, mewujudkan komputasi paralel sejati (true parallelism).

Isolasi ruang alamat memori pada arsitektur proses terpisah membawa konsekuensi teknis berupa perlunya mekanisme komunikasi antar-proses (inter-process communication / IPC) untuk mendistribusikan data masukan dan menghimpun hasil luaran. Proses utama dan pekerja berkomunikasi melalui saluran pipa sistem operasi (OS pipes). Karena memori tidak dapat diakses secara langsung oleh proses lain, objek matriks NumPy harus diubah menjadi representasi aliran bita terurut (byte streams) melalui proses serialisasi (pickling) menggunakan protokol modul pickle, lalu dikirimkan melalui pipa IPC, dan direkonstruksi kembali melalui deserialisasi (unpickling) di proses pekerja (Python Software Foundation, n.d.-b). Pada matriks citra beresolusi tinggi, volume data yang diserialisasi sangat masif (sebagai contoh, citra 4096 × 4096 piksel RGB memerlukan transfer data mentah sekitar 48 MB per arah transmisi). Durasi yang dihabiskan untuk serialisasi, transmisi pipa IPC, dan deserialisasi ini menjadi komponen utama dari beban tambahan paralel (parallel overhead), yang mengurangi efisiensi komputasi pada sistem paralel berbasis proses.

Aspek kritis lain dalam ekosistem Python adalah model inisialisasi proses pekerja pada sistem operasi Windows. Berbeda dengan sistem operasi berbasis POSIX (seperti Linux atau macOS) yang menyediakan panggilan sistem fork untuk menyalin ruang memori proses induk secara efisien (copy-on-write), sistem operasi Windows hanya mendukung metode inisialisasi spawn (Python Software Foundation, n.d.-b). Pada metode spawn, sistem operasi meluncurkan proses baru secara utuh dengan memuat ulang interpreter Python dari penyimpanan sekunder, mengalokasikan struktur proses baru, dan mengeksekusi ulang modul kode sumber dari awal. Mekanisme ini mewajibkan penyusunan skrip menggunakan blok proteksi if __name__ == '__main__': guna mencegah rekursi pembuatan proses tak berhingga. Metode spawn menimbulkan latensi inisialisasi yang cukup besar, berkisar antara 0,1 hingga 0,5 detik per proses. Untuk mencegah distorsi pengukuran waktu akibat latensi inisialisasi tersebut, penelitian ini menerapkan strategi pre-warmed worker pool (multiprocessing.Pool), di mana kolam proses pekerja diinisialisasi dan distabilkan terlebih dahulu sebelum pengukuran waktu benchmarking dimulai.


### Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache

Evolusi arsitektur mikroprosesor modern telah bergeser dari peningkatan frekuensi kerja tunggal (clock scaling) menuju integrasi banyak inti pemrosesan fisik (multi-core architecture) dalam satu keping silikon (Pacheco & Malensek, 2022). Inti fisik merepresentasikan unit eksekusi lengkap yang memiliki unit logika aritmatika (arithmetic logic unit / ALU), unit vektor SIMD, dan unit kendali instruksi tersendiri. Di atas inti fisik, prosesor modern sering mengimplementasikan teknologi Simultaneous Multithreading (SMT atau Intel Hyper-Threading), yang menduplikasi register arsitektural untuk menyajikan dua prosesor logis per inti fisik. SMT meningkatkan throughput pemrosesan saat terjadi penundaan memori (memory stall), namun pada komputasi intensif berbasis pemrosesan larik numerik penuh, penambahan beban melampaui jumlah inti fisik tidak memberikan percepatan linier karena unit kalkulasi fisik tetap dibagi bersama.

* Perangkat keras uji yang digunakan dalam penelitian ini mengusung arsitektur heterogen hibrida kontemporer, yaitu prosesor Intel Core i5-13420H generasi ke-13 (nama sandi Raptor Lake). Arsitektur hibrida ini mengombinasikan dua jenis mikroarsitektur inti prosesor yang memiliki karakteristik daya dan kinerja asimetris:
1. Performance-Cores (P-Cores, arsitektur Raptor Cove): Berjumlah 4 inti fisik yang dirancang khusus untuk beban kerja komputasi berat dengan latensi rendah. P-Core memiliki pipa instruksi lebar, kapasitas prediksi percabangan mendalam, frekuensi kerja dasar 2,1 GHz dengan dorongan turbo hingga 4,6 GHz, serta mendukung SMT (menghasilkan 8 utas logis).
* Efficient-Cores (E-Cores, arsitektur Gracemont): Berjumlah 4 inti fisik yang dirancang dengan tapak silikon kompak dan konsumsi daya sangat rendah untuk menangani komputasi latar belakang dan pemrosesan multi-utas throughput tinggi. E-Core beroperasi pada frekuensi dasar 1,5 GHz dengan turbo hingga 3,4 GHz, dan tidak mendukung SMT (4 utas logis).
Secara keseluruhan, prosesor menyediakan 8 inti fisik dan 12 utas logis. Penjadwalan proses sepenuhnya dikendalikan oleh sistem operasi Windows 11 melalui kolaborasi dengan mikrokontroler perangkat keras Intel Thread Director.
Hierarki subsistem memori prosesor memainkan peran yang sangat menentukan dalam kinerja algoritma pengolahan citra. Prosesor Intel Core i5-13420H memiliki struktur hierarki cache tiga tingkat:

* Cache Level 1 (L1): Terdiri atas 80 KB per P-Core (48 KB L1-Data + 32 KB L1-Instruction) dan 96 KB per E-Core (32 KB L1-D + 64 KB L1-I), dengan latensi akses sekitar 1 nanodetik (ns).
* Cache Level 2 (L2): Bersifat privat berkapasitas 1,25 MB per P-Core dan 2 MB terbagi (shared) per kluster empat E-Core, dengan latensi akses sekitar 3–4 ns.
* Cache Level 3 (L3 / Intel Smart Cache): Berkapasitas total 12 MB yang terbagi secara merata (shared cache) untuk seluruh inti prosesor (baik P-Core maupun E-Core) dengan latensi sekitar 10–12 ns.
Di luar L3 cache, data harus diambil dari memori utama (DDR5 SDRAM pada kecepatan transfer 5200 MT/s) yang memiliki latensi jauh lebih tinggi, yaitu sekitar 60 hingga 80 ns.
Interaksi antara dimensi matriks citra dan kapasitas 12 MB L3 Smart Cache menjadi faktor penjelas fundamental terhadap perilaku percepatan paralel. Pada citra masukan berdimensi kecil, seperti 512 × 512 piksel berformat RGB (ukuran matriks mentah sekitar 768 KB), seluruh data citra beserta sub-matriks hasil partisi untuk seluruh proses pekerja dapat ditampung secara penuh di dalam 12 MB L3 Smart Cache. Kondisi ini menghasilkan tingkat keberhasilan temu data memori (cache hit rate) yang sangat tinggi, mengurangi latensi akses secara drastis, dan memungkinkan pencapaian rasio percepatan yang sangat tinggi (bahkan mendekati atau melampaui batas linier pada komputasi intensif). Sebaliknya, pada citra berdimensi ultra-tinggi 4096 × 4096 piksel (ukuran matriks mentah sekitar 48 MB data RGB tak terkompresi), ukuran data melampaui kapasitas 12 MB L3 cache hingga empat kali lipat. Akibatnya, terjadi penggantian baris cache yang masif dan terus-menerus (cache thrashing), memaksa prosesor untuk mengambil data secara berulang dari RAM DDR5 melalui bus memori sistem. Perebutan lebar pita (memory bandwidth contention) antar-inti prosesor pada citra berukuran masif ini menjadi pembatas utama skalabilitas komputasi paralel.


## Metrik Evaluasi Kinerja dan Model Skalabilitas

Untuk mengukur dan menganalisis efektivitas komputasi paralel secara objektif, diperlukan parameter kuantitatif yang terstandarisasi. Bagian ini merumuskan metrik kinerja empiris dasar, batas skalabilitas teoretis berdasarkan Hukum Amdahl dan metrik Karp–Flatt, serta kerangka analisis statistik dan metodologi evaluasi batas derau sistem (kontrol A/A) yang diterapkan dalam penelitian ini.


### Metrik Kinerja Dasar: Waktu Eksekusi, Speedup, Efisiensi, dan Overhead Paralel

Evaluasi kinerja komputasi bertumpu pada perbandingan durasi waktu eksekusi program. Waktu eksekusi diukur dalam satuan detik menggunakan fungsi pewaktu berpresisi tinggi berbasis monotonik time.perf_counter() pada bahasa Python. Waktu eksekusi serial (T_serial atau Ts) merepresentasikan durasi pemrosesan citra pada skrip serial murni satu inti prosesor tanpa inisialisasi kolam pekerja. Sementara itu, waktu eksekusi paralel (T_paralel atau Tp) mencakup seluruh rentang waktu mulai dari pencatatan stempel waktu awal sebelum partisi matriks citra, pemotongan blok dan baris batas, transmisi data melalui pipa IPC, eksekusi filter serentak oleh kolam proses pekerja, pembuangan baris batas, transmisi balik, hingga rekonstruksi citra utuh selesai dilakukan melalui penggabungan vertikal.

Rasio percepatan (speedup) mengukur seberapa banyak komputasi paralel mampu mempersingkat durasi pemrosesan dibandingkan eksekusi serial pada beban kerja yang identik (Pacheco & Malensek, 2022). Rasio percepatan (S) dirumuskan pada Persamaan (2.2):


$$
S = T_serial / T_paralel \quad (2.2)
$$

Keterangan:

* S : Nilai rasio percepatan (speedup) komputasi (rasio nirdimensi).
* T_serial : Waktu eksekusi pemrosesan citra pada skrip serial murni satu inti prosesor tanpa inisialisasi kolam proses (detik).
* T_paralel : Waktu eksekusi pemrosesan citra secara paralel pada alokasi P proses pekerja (detik).
Efisiensi paralel (parallel efficiency) mengukur fraksi pemanfaatan daya komputasi dari setiap unit proses pekerja yang dialokasikan (Pacheco & Malensek, 2022). Pada kondisi ideal tanpa hambatan komunikasi, penambahan P prosesor akan menghasilkan percepatan sebesar P kali lipat dengan efisiensi 100%. Namun pada sistem riil, efisiensi selalu terdegradasi seiring peningkatan P. Efisiensi paralel (E) dinyatakan dalam persentase sebagaimana dirumuskan pada Persamaan (2.3):


$$
E = (S / P) × 100% = (T_serial / (P · T_paralel)) × 100% \quad (2.3)
$$

Keterangan:

* E : Persentase efisiensi komputasi paralel (%).
* S : Nilai rasio percepatan (speedup) yang diperoleh dari Persamaan (2.2).
* P : Jumlah proses pekerja (worker processes) yang dialokasikan dalam eksekusi paralel.
Beban tambahan paralel (parallel overhead) merepresentasikan penalti durasi waktu tambahan yang timbul akibat koordinasi sistem paralel di luar waktu komputasi pemrosesan citra murni (Pacheco & Malensek, 2022). Beban ini dihitung dari selisih antara waktu eksekusi paralel aktual (T_paralel) dengan waktu eksekusi paralel ideal teoretis (T_serial / P), sebagaimana dirumuskan pada Persamaan (2.4):


$$
T_overhead = T_paralel - (T_serial / P) \quad (2.4)
$$

Keterangan:

* T_overhead : Durasi beban tambahan sistem paralel akibat komunikasi antar-proses (IPC), serialisasi matriks (pickling), replikasi baris batas (halo), dan rekonstruksi matriks citra (detik).
* T_paralel : Waktu eksekusi paralel aktual yang terukur (detik).
* T_serial / P : Waktu eksekusi paralel ideal secara teoretis tanpa beban koordinasi sistem (detik).
* T_serial : Waktu eksekusi serial baseline (detik).
* P : Jumlah proses pekerja yang dialokasikan.

### Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp–Flatt

Batas percepatan maksimum suatu sistem komputasi paralel secara klasik dimodelkan oleh Hukum Amdahl (Amdahl, 1967). Hukum Amdahl menyatakan bahwa rasio percepatan program paralel dibatasi secara fundamental oleh proporsi instruksi kode yang bersifat serial dan tidak dapat dibagi ke banyak prosesor (Pacheco & Malensek, 2022). Apabila suatu program memiliki fraksi beban kerja paralel sebesar f (di mana 0 ≤ f ≤ 1), maka batas rasio percepatan teoretis pada alokasi P proses pekerja dirumuskan pada Persamaan (2.5):


$$
S_Amdahl = 1 / ((1 - f) + (f / P)) \quad (2.5)
$$

Keterangan:

* S_Amdahl : Percepatan teoretis pada alokasi P proses pekerja menurut model Amdahl.
* f : Fraksi beban komputasi yang dapat diparalelkan secara sempurna (0 ≤ f ≤ 1).
* (1 - f) : Fraksi serial efektif yang tidak mengalami percepatan, mencakup bagian kode sekuensial program, beban koordinasi paralel (partisi, transmisi pipa IPC, baris batas, rekonstruksi), dan pengaruh disparitas arsitektur inti prosesor yang tidak setara (P-Core dan E-Core).
* P : Jumlah proses pekerja yang dialokasikan.
Ketika jumlah prosesor ditingkatkan mendekati tak hingga (P → ∞), suku f / P mendekati nol, sehingga batas percepatan asimtotik maksimum program dibatasi oleh 1 / (1 - f). Hukum Amdahl klasik mengasumsikan bahwa seluruh prosesor bersifat homogen dan tidak memperhitungkan pembengkakan biaya koordinasi yang tumbuh seiring pertambahan prosesor. Dalam konteks sistem riil penelitian ini pada prosesor hibrida Intel Raptor Lake, fraksi serial (1 - f) diperlakukan sebagai fraksi serial efektif (effective serial fraction), yang menyerap seluruh penalti non-ideal sistem, termasuk transmisi IPC, serialisasi pickle, rekonstruksi vstack, serta asimetri kemampuan komputasi antara P-Core dan E-Core. Parameter fraksi paralel f diestimasi per algoritma filter melalui regresi non-linier kuadrat terkecil (non-linear least squares) terhadap data empiris Skenario B untuk P ∈ {2, 4, 8} disertai estimasi selang kepercayaan 95% berbasis bootstrap.

Untuk memeriksa apakah hambatan skalabilitas yang terjadi berakar dari keterbatasan inheren algoritma ataukah didominasi oleh inefisiensi arsitektur komunikasi sistem, diterapkan metrik Karp–Flatt (Karp & Flatt, 1990). Metrik Karp–Flatt mendefinisikan fraksi serial eksperimental (e) secara independen dari estimasi parameter Amdahl, sebagaimana dirumuskan pada Persamaan (2.6):


$$
e = ((1 / S) - (1 / P)) / (1 - (1 / P)) \quad (2.6)
$$

Keterangan:

* e : Fraksi serial eksperimental (experimentally determined serial fraction).
* S : Rasio percepatan empiris yang terukur pada alokasi P proses pekerja.
* P : Jumlah proses pekerja yang dialokasikan (P > 1).
Metrik Karp–Flatt memberikan alat diagnostik yang sangat kuat untuk mengidentifikasi perilaku sistem paralel:
1. Jika nilai fraksi serial eksperimental e bernilai konstan seiring dengan penambahan alokasi proses pekerja P, maka keterbatasan skalabilitas program murni disebabkan oleh keberadaan bagian kode serial sekuensial yang konstan, sehingga sistem mematuhi asumsi model klasik Amdahl.
2. Jika nilai fraksi serial eksperimental e meningkat secara monoton seiring penambahan P, hal tersebut membuktikan secara diagnostik bahwa pembatas utama skalabilitas bukanlah kode serial murni, melainkan diakibatkan oleh pembengkakan beban koordinasi paralel, latensi transmisi pipa IPC, biaya serialisasi matriks, atau saturasi lebar pita memori yang tumbuh sebanding dengan penambahan proses kerja.


### Analisis Statistik Pengukuran dan Evaluasi Batas Derau Sistem (Kontrol A/A)

Akurasi pengukuran kinerja pada sistem komputer modern sangat rentan terdistorsi oleh fluktuasi derau perangkat keras dan perangkat lunak, seperti fluktuasi suhu prosesor (thermal throttling) serta interupsi aktivitas latar belakang sistem operasi (layanan sistem Windows, pembaruan otomatis, dan manajemen memori OS). Untuk mengisolasi faktor pengganggu tersebut, seluruh pengujian dalam penelitian ini dieksekusi melalui protokol 30 kali repetisi pengujian terkontrol yang dijalankan secara berselang-seling (interleaved execution) antara skrip serial dan skrip paralel pada setiap tingkatan perlakuan. Dengan metode berselang-seling ini, setiap pasangan data serial dan paralel mengalami kondisi termal dan beban sistem latar belakang yang setara.

Data durasi waktu eksekusi pada sistem komputer riil memiliki karakteristik distribusi yang asimetris dengan kecenderungan menjulur ke kanan (right-skewed distribution), akibat munculnya beberapa nilai pencilan (outliers) yang dipicu oleh lonjakan aktivitas proses latar belakang sistem operasi. Mengingat asumsi normalitas tidak selalu terpenuhi, analisis pemusatan data mengutamakan statistik non-parametrik yang tangguh terhadap pencilan (robust statistics), yaitu nilai median dan rentang antarkuartil (IQR, [Q25 - Q75]). Nilai rerata sampel (x̄) dan simpangan baku sampel (s) tetap dilaporkan sebagai parameter pelengkap.

Untuk memberikan estimasi kepastian statistik pada nilai rerata parameter kinerja, dihitung selang kepercayaan 95% (confidence interval) menggunakan distribusi t-Student untuk ukuran sampel n = 30, sebagaimana dirumuskan pada Persamaan (2.7):


$$
CI_95% = x̄ ± t_(n-1, α/2) · (s / √n) \quad (2.7)
$$

Keterangan:

* CI_95% : Selang kepercayaan 95% (confidence interval) untuk nilai rerata parameter kinerja.
* x̄ : Rerata sampel dari n = 30 repetisi pengujian.
* s : Simpangan baku sampel.
* n : Ukuran sampel pengujian (n = 30).
* t_(n-1, α/2) : Nilai kritis distribusi t-Student pada derajat kebebasan df = n - 1 = 29 dan tingkat signifikansi α = 0,05, bernilai t_(29, 0,025) = 2,04523.
Pengujian signifikansi perbedaan performa antar-perlakuan dievaluasi melalui uji hipotesis non-parametrik dengan taraf signifikansi α = 0,05. Uji Mann–Whitney U digunakan untuk membandingkan signifikansi perbedaan antara dua kelompok independen, sedangkan uji Kruskal–Wallis digunakan untuk menguji variasi kinerja antar-alokasi proses pekerja (P = 1, 2, 4, 8). Suatu perbedaan perlakuan dinyatakan signifikan secara statistik apabila nilai signifikansi terhitung lebih kecil dari ambang batas (p < 0,05).

Sebagai instrumen kendali mutu pengukuran, penelitian ini menyertakan rancangan pengujian kontrol A/A dengan alokasi satu proses pekerja (P = 1). Pada perlakuan kontrol A/A, skrip arsitektur paralel dieksekusi dengan satu pekerja (T_paralel, P=1) lalu dikomparasikan secara langsung terhadap skrip serial murni (T_serial). Karena pada P = 1 tidak terjadi pembagian beban komputasi ke beberapa inti fisik prosesor, secara teoretis rasio percepatan yang dihasilkan harus bernilai mendekati satu (S ≈ 1,00). Nilai selisih T_overhead, P=1 = T_paralel, P=1 - T_serial secara presisi merepresentasikan batas derau sistem (system noise floor) dan biaya struktural inheren dari modul multiprocessing Python (mekanisme transmisi pipa IPC dan serialisasi data matriks) tanpa campur tangan akselerasi perangkat keras. Metodologi kontrol A/A ini menjadi fondasi empiris yang memvalidasi bahwa seluruh peningkatan performa pada P = 2, 4, dan 8 benar-benar bersumber dari akselerasi komputasi paralel dan bukan merupakan artefak derau pengukuran.


# DAFTAR PUSTAKA (RUJUKAN BAB 2)

Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560

Chang, L., Deng, X., & Wang, Z. (2023). Acceleration of digital image processing algorithms based on GPU. Journal of Computer and Communications, 11(10), 12–25. https://doi.org/10.4236/jcc.2023.1110002

Cremel, P. D. F., & Arruda, L. C. (2026). Parallel processing for computer vision and digital image processing: A systematic review. Multimedia Tools and Applications, 85(4), 11201–11235.

Gonzalez, R. C., & Woods, R. E. (2018). Digital image processing (4th ed.). Pearson.

Gultom, J. M., & Sarumaha, C. A. (2025). Analisis perbandingan kinerja multithreading dan multiprocessing pada pemrosesan citra digital dengan Python. Jurnal Sistem Komputer dan Informatika (JSON), 6(3), 412–421.

Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021) (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179

Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.

International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.

Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614

Montgomery, D. C. (2017). Design and analysis of experiments (9th ed.). John Wiley & Sons.

Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.

Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock

Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html

Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.

Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. Journal of Imaging, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298
