# BAB 2 LANDASAN TEORI


## Perbandingan Terhadap Penelitian Terdahulu

Akselerasi proses komputasi pada visi komputer dan pengolahan citra digital telah menjadi fokus kajian intensif seiring dengan pesatnya pertumbuhan resolusi citra digital modern (Cremel & Arruda, 2026). Dalam menangani beban kalkulasi konvolusi matriks yang besar, sejumlah penelitian terdahulu mengarahkan implementasi pada unit pemrosesan grafis (GPU). Chang et al. (2023) meneliti implementasi operator Sobel multi-arah berbasis kernel 5×5 pada GPU menggunakan antarmuka NVIDIA CUDA, serta melaporkan bahwa pemanfaatan warp-level primitives mampu mereduksi akses memori global secara signifikan dan menghasilkan rasio percepatan (speedup) sebesar 6,7 hingga 13,0 kali lipat dibandingkan pustaka OpenCV-GPU standar. Dari sudut pandang arsitektur perangkat keras, Vasile et al. (2024) mengkaji akselerasi perangkat keras visi komputer dan menegaskan bahwa pemrosesan aliran data citra beresolusi tinggi menuntut pertimbangan ketat antara kapasitas komputasi (throughput) dan latensi akses memori.

Pada ranah prosesor multi-core, eksplorasi komputasi paralel umumnya memanfaatkan model memori bersama (shared memory) berbasis utas (threading). Cremel dan Arruda (2026) mengevaluasi akselerasi filter prapemrosesan citra digital menggunakan pustaka OpenMP pada bahasa C/C++. Temuan mereka menunjukkan bahwa rasio percepatan meningkat seiring membesarnya dimensi citra, namun efisiensi paralel mengalami degradasi tajam saat jumlah utas ditingkatkan hingga 8 utas, dengan efisiensi pada operasi deteksi tepi menurun hingga mencapai 24% akibat keterbatasan lebar pita memori (memory-bound behavior). Karakteristik tersebut sejalan dengan temuan Ibrahim et al. (2021) pada komparasi konvolusi Gaussian Blur 2D antara CPU multi-core dan GPU, yang menyimpulkan bahwa beban tambahan (overhead) transfer memori mendominasi durasi total pada matriks berukuran kecil hingga menengah, sehingga efisiensi pemrosesan paralel baru tercapai secara optimal pada matriks berdimensi besar.

Di sisi lain, implementasi komputasi paralel pada bahasa pemrograman Python menghadapi karakteristik arsitektur internal berupa Global Interpreter Lock (GIL) pada implementasi referensi resmi CPython (Python Software Foundation, n.d.-a). Gultom dan Sarumaha (2025) mengevaluasi kinerja model sekuensial, multithreading, dan multiprocessing pada beban komputasi numerik intensif (CPU-bound) menggunakan Python pada prosesor multi-core. Hasil pengujian mereka menunjukkan bahwa multithreading Python hanya menghasilkan rasio percepatan marjinal sekitar 1,05 kali lipat akibat restriksi GIL pada tingkat eksekusi bytecode interpreter. Sebaliknya, modul multiprocessing mampu melipatgandakan kinerja dengan capaian speedup antara 3,16 hingga 3,55 kali lipat pada alokasi empat proses pekerja karena setiap proses memperoleh ruang memori (address space) dan instansiasi interpreter yang independen (Gultom & Sarumaha, 2025; Tanenbaum & Bos, 2022).

Tabel 2.1 Perbandingan Penelitian Terdahulu Terkait Komputasi Paralel pada Pengolahan Citra



| Peneliti dan Tahun | Objek dan Beban Uji | Platform dan Paradigma | Skala / Dimensi Uji | Metrik dan Temuan Utama |
| --- | --- | --- | --- | --- |
| Chang et al. (2023) | Operator Sobel multi-arah (kernel 5×5) untuk deteksi tepi | Akselerasi GPU berbasis NVIDIA CUDA (warp-level primitives) | Citra resolusi tinggi standar | Reduksi akses memori dan speedup 6,7× s.d. 13,0× terhadap OpenCV-GPU; fokus pada akselerasi perangkat keras skala besar. |
| Vasile et al. (2024) | Kajian literatur akselerator perangkat keras visi komputer | Tinjauan arsitektur komputasi (GPU, FPGA, ASIC) | Studi pustaka komprehensif | Pemetaan komparatif throughput dan latensi antar-arsitektur; menegaskan tuntutan pemrosesan real-time pada aliran data resolusi tinggi. |
| Cremel dan Arruda (2026) | Filter prapemrosesan citra (Blur, Sharpen, Edge detection, CLAHE, Denoise) | CPU multi-core berbasis OpenMP C/C++ (shared memory threads) | Variasi resolusi citra digital | Penurunan efisiensi tajam seiring penambahan utas kerja (mencapai 24% pada 8 utas untuk deteksi tepi); keterbatasan lebar pita memori. |
| Ibrahim et al. (2021) | Konvolusi filter Gaussian Blur 2D | Komparasi CPU multi-core dan GPU (Google Colab) | Matriks citra kecil hingga besar | Beban tambahan transfer memori mendominasi pada resolusi kecil; keuntungan paralel baru tercapai optimal pada matriks besar. |
| Gultom dan Sarumaha (2025) | Beban komputasi numerik intensif (CPU-bound loop) | CPython: Sekuensial, Threading, dan Multiprocessing | 20 juta s.d. 120 juta iterasi numerik | Multithreading dibatasi GIL (speedup ~1,05×); multiprocessing mencapai speedup 3,16× s.d. 3,55× pada 4 proses. |


Berdasarkan sintesis kajian pustaka pada Tabel 2.1, terdapat kesenjangan penelitian yang mendasar. Sebagian besar penelitian terdahulu berfokus pada model memori bersama berbasis C/C++ OpenMP (Cremel & Arruda, 2026) atau akselerasi GPU (Chang et al., 2023; Ibrahim et al., 2021), sedangkan studi multiprocessing Python (Gultom & Sarumaha, 2025) baru menguji beban iterasi sintetis murni. Belum ada penelitian yang secara sistematis membedah perilaku komputasi paralel multiprocessing Python pada pemrosesan citra multiresolusi bertingkat (512 hingga 4096 piksel) pada prosesor heterogen modern yang memadukan inti performa (P-Core) dan inti efisiensi (E-Core). Penelitian ini mengisi ruang tersebut dengan mengevaluasi tiga variasi algoritma filter spasial, memetakan kurva empiris terhadap batas teoretis Hukum Amdahl dan metrik Karp–Flatt, serta menerapkan kendali mutu pengukuran melalui protokol pengujian berselang-seling dan kontrol A/A.


## Pengolahan Citra Digital dan Operasi Filter Spasial

Pengolahan citra digital merupakan disiplin rekayasa komputer yang memanipulasi representasi visual diskret menggunakan algoritma komputasi terstruktur guna mengekstraksi informasi, meningkatkan kualitas visual, atau mempersiapkan data untuk analisis tingkat lanjut (Gonzalez & Woods, 2018). Dalam domain spasial, operasi filter citra bekerja secara langsung pada nilai intensitas piksel yang menyusun bidang matriks gambar.


### Representasi Citra Digital dan Operasi Konvolusi 2D

Secara matematis, citra digital monokromatik dimodelkan sebagai fungsi diskret intensitas dua dimensi I(x, y), dengan x dan y menyatakan koordinat spasial pada bidang matriks, sedangkan nilainya merepresentasikan derajat keabuan (gray level) piksel. Pada citra digital berwarna berformat RGB, representasi diperluas menjadi larik tiga dimensi berdimensi H × W × C, dengan H menyatakan tinggi citra (jumlah baris), W menyatakan lebar citra (jumlah kolom), dan C = 3 menyatakan komponen kanal warna primer merah (Red), hijau (Green), dan biru (Blue) (Gonzalez & Woods, 2018).

Operasi filter spasial linier pada citra digital dieksekusi melalui pergeseran matriks bobot berukuran kecil yang disebut kernel konvolusi di atas bidang citra masukan. Nilai piksel luaran pada koordinat spasial (x, y) dihitung sebagai penjumlahan berbobot dari perkalian elemen kernel terhadap nilai piksel ketetanggaannya. Mengacu pada perumusan baku pengolahan citra (Gonzalez & Woods, 2018), operasi konvolusi diskret dua dimensi (secara teknis dieksekusi sebagai korelasi silang tanpa pembalikan kernel) dinyatakan pada Persamaan (2.1):


$$
I_filter(x, y) = ∑_(i=-k)^k ∑_(j=-k)^k K(i, j) · I(x + i, y + j) \quad (2.1)
$$

Keterangan:

* I_filter(x, y) : Nilai intensitas piksel luaran hasil pemfilteran pada koordinat spasial (x, y).
* I(x + i, y + j) : Nilai intensitas piksel masukan pada posisi ketetanggaan relatif (x + i, y + j).
* K(i, j) : Koefisien bobot matriks kernel konvolusi pada koordinat relatif (i, j).
* k : Radius spasial matriks kernel (pada kernel berdimensi 3 × 3, bernilai k = 1).
* i, j : Indeks pergeseran koordinat spasial kernel secara vertikal dan horizontal.
Bentuk formulasi pada Persamaan (2.1) secara teknis merupakan operasi korelasi silang (cross-correlation) yang lazim disebut sebagai konvolusi dalam pustaka rekayasa visi komputer modern. Untuk kernel spasial simetris seperti Gaussian, hasil korelasi silang identik secara matematis dengan konvolusi sejati. Adapun pada operator diferensial seperti Sobel, korelasi silang hanya membalik tanda arah gradien tanpa mengubah nilai magnitudo gradien tepi yang dihasilkan.


### Karakteristik Algoritma Filter Spasial yang Diuji

Penelitian ini menguji tiga algoritma filter spasial dengan karakteristik beban komputasi dan kebutuhan memori yang bertingkat secara sistematis:
1. Konversi Grayscale (Rekomendasi ITU-R BT.601-7): Merupakan operasi titik linier independen tanpa ketetanggaan spasial yang mentransformasikan tiga kanal warna RGB menjadi satu kanal luminansi monokromatik berbobot matematis: Y = 0,299R + 0,587G + 0,114B (International Telecommunication Union, 2011). Operasi ini membutuhkan 3 perkalian dan 2 penjumlahan per piksel dengan rasio komputasi terhadap volume data yang rendah (intensitas aritmatika 1,25 FLOP/bita).
2. Penghalusan Citra Gaussian Blur 3×3: Merupakan filter lolos-rendah (low-pass filter) berbasis konvolusi spasial dua dimensi dengan radius k = 1 pada ketiga kanal warna RGB. Setiap piksel luaran dihitung dari konvolusi matriks kernel Gaussian diskret berbobot normalisasi 1/16, menghasilkan 51 operasi aritmatika per piksel dengan transfer data IPC sebesar 6 bita per piksel.
3. Deteksi Tepi Sobel 3×3: Merupakan filter diferensial spasial tingkat pertama yang menghitung aproksimasi gradien intensitas citra pada arah horizontal (Gx) dan vertikal (Gy). Menggunakan konvensi hitungan tanpa tap bernilai nol (mengeliminasi kolom tengah Gx dan baris tengah Gy), setiap koordinat piksel memerlukan 12 perkalian koefisien, 10 penjumlahan, 2 pemangkatan kuadrat, 1 penjumlahan kuadrat gradien, dan 1 kalkulasi akar kuadrat untuk menghasilkan magnitudo gradien (total 26 operasi aritmatika per piksel).

Tabel 2.2 Karakteristik Algoritma Filter Spasial yang Diuji



| Nama Filter | Dimensi Kernel | Operasi Aritmatika per Piksel | Bita IPC per Piksel | Intensitas Aritmatika | Karakteristik Komputasi |
| --- | --- | --- | --- | --- | --- |
| Grayscale<br>(ITU-R BT.601) | 1 × 1<br>(Titik) | 3 perkalian bobot,<br>2 penjumlahan kanal<br>(5 operasi/piksel) | 3 masuk + 1 keluar<br>= 4 bita/piksel | 5 / 4<br>= 1,25 op/bita | Operasi titik linier;<br>kecenderungan memory-bound; intensitas kalkulasi rendah. |
| Gaussian Blur<br>3×3 | 3 × 3<br>(Spasial) | 9 perkalian koefisien,<br>8 penjumlahan per kanal × 3 kanal = 51 operasi/piksel | 3 masuk + 3 keluar<br>= 6 bita/piksel | 51 / 6<br>= 8,50 op/bita | Konvolusi simetris;<br>beban transfer data memori 3 kanal tinggi. |
| Sobel 3×3<br>(Gradien Gx dan Gy) | 2 × (3 × 3)<br>(Diferensial) | Hitungan tanpa tap nol:<br>12 kali, 10 tambah, 2 kuadrat, 1 tambah, 1 akar<br>(26 operasi/piksel) | 3 masuk + 1 keluar<br>= 4 bita/piksel | 26 / 4<br>= 6,50 op/bita | Konvolusi ganda non-linier;<br>kecenderungan compute-bound; intensitas kalkulasi tinggi. |


Hierarki rancangan ketiga algoritma filter pada Tabel 2.2 memungkinkan pemetaan komparatif yang komprehensif, mulai dari operasi titik berintensitas aritmatika rendah dengan kecenderungan terikat memori (memory-bound), hingga operasi konvolusi diferensial non-linier yang membutuhkan instruksi aritmatika intensif dengan kecenderungan terikat komputasi (compute-bound).


## Komputasi Paralel dan Multiprocessing Python

Komputasi paralel adalah paradigma pemrosesan informasi yang membagi satu beban kalkulasi terpadu menjadi beberapa sub-tugas independen yang dieksekusi secara simultan pada unit pemrosesan fisik yang berbeda (Pacheco & Malensek, 2022). Tujuannya adalah mereduksi waktu eksekusi total dan meningkatkan efisiensi pemanfaatan sumber daya perangkat keras prosesor modern.


### Paradigma Data Parallelism dan Dekomposisi Domain Spasial

Dalam taksonomi komputasi paralel, terdapat dua strategi pemecahan masalah utama: task parallelism dan data parallelism (Pacheco & Malensek, 2022). Task parallelism mendistribusikan fungsi komputasi yang berbeda ke beberapa prosesor, sedangkan data parallelism mendistribusikan elemen-elemen data berukuran besar ke beberapa unit pemrosesan yang menjalankan rantai instruksi algoritma yang serupa secara serentak. Pengolahan filter citra digital merupakan contoh representatif dari persoalan paralel mandiri (embarrassingly parallel), karena sebagian besar wilayah spasial citra dapat dihitung secara terpisah tanpa memerlukan sinkronisasi nilai perantara antar-pekerja (Cremel & Arruda, 2026).

Dekomposisi domain spasial pada penelitian ini diterapkan melalui metode pembagian baris horizontal (horizontal row partitioning). Matriks citra berdimensi H × W × C dibagi secara merata sepanjang sumbu vertikal menjadi P potongan blok berdimensi (H/P) × W × C untuk didistribusikan ke P proses pekerja. Pada seluruh matriks uji yang dirancang, dimensi tinggi citra H (512, 1024, 2048, dan 4096 piksel) habis dibagi oleh jumlah proses pekerja P (1, 2, 4, dan 8 proses), sehingga pembagian beban kerja antar-proses pekerja bersifat seimbang sempurna tanpa adanya baris sisa yang dapat memicu ketimpangan beban kerja (load imbalance).

Tantangan utama dekomposisi spasial pada operasi konvolusi terletak pada ketergantungan data lokal di area tepi perbatasan blok. Piksel-piksel yang berada pada baris batas atas dan baris batas bawah potongan membutuhkan informasi intensitas piksel tetangga di luar area bloknya sejauh radius spasial k = 1. Untuk mengatasi ketergantungan ini, setiap blok potongan diperluas secara fisik dengan menambahkan k baris piksel tetangga di sisi atas dan bawah yang disebut sebagai baris batas (boundary halo). Potongan interior menerima satu baris batas atas dan satu baris batas bawah, menghasilkan potongan masukan berukuran ((H/P) + 2k) × W × C, sedangkan potongan tepi citra terluar hanya menerima penambahan baris batas pada satu sisi.

Mekanisme baris batas ini menjamin keamanan konkurensi data karena baris batas hanya dibaca secara mandiri oleh pekerja tanpa adanya operasi penulisan balik ke ruang memori proses lain, sehingga meniadakan potensi terjadinya kondisi balapan (race condition). Setelah komputasi filter selesai dieksekusi, setiap pekerja melakukan pemotongan pembuangan (halo stripping) terhadap baris batas tersebut sebelum mengembalikan blok luaran ke proses utama, sehingga dimensi matriks hasil pemrosesan kembali tepat berukuran (H/P) × W untuk digabungkan kembali secara sekuensial melalui fungsi numpy.vstack().


### Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC

CPython, implementasi referensi standar bahasa pemrograman Python, mengandalkan mekanisme manajemen memori berbasis pencacah referensi (reference counting). Untuk mencegah korupsi memori internal dan konflik alokasi objek saat beberapa utas berjalan serentak, CPython menerapkan Global Interpreter Lock (GIL) (Python Software Foundation, n.d.-a; Tanenbaum & Bos, 2022). GIL adalah mekanisme kunci biner (mutex) yang membatasi bahwa hanya satu utas yang diizinkan mengeksekusi bytecode Python murni pada satu waktu. Akibatnya, pustaka threading standar Python tidak mampu memanfaatkan kapasitas multi-core secara efektif pada beban kerja komputasi murni yang ditulis dalam bahasa Python (Gultom & Sarumaha, 2025). Perlu dicatat secara metodologis bahwa pustaka numerik berbasis C seperti NumPy secara internal melepas GIL (releases the GIL) pada banyak operasi kalkulasi larik berukuran besar. Oleh karena itu, pemilihan paradigma multiprocessing dalam penelitian ini merupakan batasan ruang lingkup rancangan sistem untuk mengevaluasi isolasi proses independen dan beban koordinasi IPC, bukan pernyataan bahwa multithreading pasti gagal pada seluruh implementasi operasi berbasis NumPy.

Modul bawaan multiprocessing pada Python dirancang untuk melangkahi restriksi GIL dengan menerapkan arsitektur konkurensi berbasis proses independen (Python Software Foundation, n.d.-b). Alih-alih membuat utas ringan di dalam ruang proses yang sama, modul ini meluncurkan proses sistem operasi baru yang terpisah. Masing-masing proses pekerja memiliki ruang alamat memori fisik independen (isolated address space) dan instansiasi interpreter CPython mandiri (Tanenbaum & Bos, 2022). Pendekatan ini memungkinkan eksekusi instruksi komputasi berjalan secara paralel sesungguhnya (true hardware parallelism) pada setiap inti prosesor fisik yang tersedia.

Namun demikian, isolasi ruang alamat memori pada arsitektur proses menimbulkan konsekuensi berupa beban tambahan komunikasi antar-proses (inter-process communication / IPC). Karena memori tidak dapat diakses secara langsung antar-proses, data larik citra masukan harus diubah ke dalam bentuk deretan bita melalui proses serialisasi (pickling), dikirimkan melalui saluran pipa (pipes) atau antrean (queues) sistem operasi, dan dide-serialisasi kembali (unpickling) di ruang memori proses pekerja penerima. Beban penalti transmisi memori ini tumbuh sebanding dengan membesarnya dimensi data citra yang ditransfer dan menjadi komponen dominan dari beban tambahan paralel (parallel overhead).

Aspek kritis lain dalam ekosistem Python adalah model tata letak memori larik NumPy. Pustaka NumPy mengorganisasikan larik multidimensi dalam urutan berbasis baris (row-major order) atau tata letak memori C-contiguous (Pacheco & Malensek, 2022). Dalam representasi ini, elemen-elemen piksel pada baris horizontal yang sama menempati lokasi alamat memori fisik yang berurutan secara linier. Karakteristik ini memberikan keunggulan lokalitas spasial (spatial locality) yang tinggi ketika dekomposisi data dilakukan melalui pemotongan baris horizontal, karena setiap proses pekerja menerima satu segmen blok memori yang kontinu tanpa fragmentasi pointer alamat.


### Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache

Evolusi arsitektur mikroprosesor modern telah bergeser dari peningkatan frekuensi kerja tunggal menuju integrasi banyak inti prosesor (multi-core architecture) pada satu keping silikon (Pacheco & Malensek, 2022). Pada generasi prosesor Intel Core ke-13 (nama sandi Raptor Lake-H), diterapkan mikroarsitektur hibrida (hybrid architecture) yang memadukan dua kategori mikroarsitektur inti komputasi dengan karakteristik daya dan instruksi per siklus (IPC) yang berbeda (Intel Corporation, 2023):
1. Performance-Cores (P-Cores, arsitektur turunan Golden Cove pada prosesor Core i5-13420H): Didesain untuk mengeksekusi beban kerja komputasi sekuensial dan latensi rendah dengan frekuensi turbo hingga 4,6 GHz serta mendukung Simultaneous Multithreading (SMT / Hyper-Threading 2 threads per inti fisik).
2. Efficient-Cores (E-Cores, arsitektur Gracemont): Didesain untuk memaksimalkan efisiensi energi dan keluaran beban kerja throughput tinggi multi-proses dengan frekuensi turbo hingga 3,4 GHz tanpa SMT (1 thread per inti fisik).

Penjadwalan alokasi proses pada mikroprosesor hibrida didukung oleh mekanisme umpan balik perangkat keras (Intel Thread Director) yang secara dinamis memantau karakteristik instruksi eksekusi proses dan memberikan rekomendasi penjadwalan kepada sistem operasi (Intel Corporation, 2023).

Di samping diferensiasi inti komputasi, hierarki subsistem memori prosesor memainkan peran penentu dalam membatasi atau mengoptimalkan laju aliran data komputasi konvolusi matriks:
1. Cache Level 1 (L1): Terdiri atas 80 KB per P-Core dan 96 KB per E-Core dengan latensi akses tercepat (1 hingga 2 siklus clock prosesor).
2. Cache Level 2 (L2): Bersifat privat berkapasitas 1,25 MB per P-Core serta 2 MB terbagi bersama (shared) per kluster empat E-Core (Intel Corporation, 2023).
3. Cache Level 3 (L3 / Intel Smart Cache): Berkapasitas 12 MB yang terbagi secara bersama (shared cache) untuk seluruh inti prosesor.

Interaksi antara volume data matriks citra dan kapasitas hierarki memori cache memunculkan fenomena performa yang tidak linier. Pada matriks citra berdimensi kecil (512 × 512 piksel berukuran sekitar 768 KB), data citra masukan beserta potongan bloknya termuat secara utuh di dalam 12 MB L3 Cache bersama. Efek percepatan superlinear yang teramati pada operasi intensif seperti Sobel 512 dipengaruhi oleh kapasitas L2 Cache privat (1,25 MB per P-Core), sehingga setiap proses pekerja menerima irisan blok sekitar 192 KB yang termuat penuh di dalam L2 Cache privatnya, menghasilkan tingkat keberhasilan akses (cache hit rate) yang tinggi dan meniadakan penalti latensi bus memori utama. Sebaliknya, pada citra beresolusi 2048 × 2048 piksel (volume data RGB mentah mencapai ~12,58 MB) dan 4096 × 4096 piksel (~48 MB), ukuran data melampaui kapasitas 12 MB L3 Cache bersama. Kondisi ini memicu kegagalan pemuatan kapasitas (capacity misses) dan memaksa prosesor melakukan transfer data berulang ke memori utama (RAM DDR5 5200 MT/s), sehingga batas performa komputasi bergeser menuju saturasi lebar pita memori (DRAM bandwidth saturation).


## Metrik Evaluasi Kinerja dan Model Skalabilitas

Untuk mengukur, menganalisis, dan memvalidasi efektivitas komputasi paralel secara kuantitatif, digunakan serangkaian parameter kinerja baku dan model matematis skalabilitas yang terstandarisasi dalam literatur rekayasa komputasi paralel.


### Metrik Kinerja Dasar: Waktu Eksekusi, Speedup, Efisiensi, dan Overhead Paralel

Evaluasi kinerja komputasi bertumpu pada perbandingan durasi waktu pemrosesan antara varian program serial murni satu inti prosesor (T_serial) terhadap durasi pemrosesan pada arsitektur paralel dengan alokasi P proses pekerja (T_paralel).

Rasio percepatan (speedup) mengukur seberapa banyak kelipatan percepatan komputasi yang dihasilkan oleh sistem paralel dibandingkan eksekusi serial pada kondisi data yang identik (Pacheco & Malensek, 2022). Mengacu pada formulasi standar, rasio percepatan S dirumuskan pada Persamaan (2.2):


$$
S = T_serial / T_paralel \quad (2.2)
$$

Keterangan:

* S : Nilai rasio percepatan (speedup) komputasi (rasio tanpa satuan).
* T_serial : Waktu eksekusi pemrosesan citra pada skrip serial murni (detik).
* T_paralel : Waktu eksekusi pemrosesan citra secara paralel pada alokasi P proses pekerja (detik).
Efisiensi paralel (parallel efficiency) mengukur fraksi pemanfaatan kapasitas komputasi dari setiap unit proses pekerja yang dialokasikan dalam eksekusi paralel (Pacheco & Malensek, 2022). Efisiensi paralel E dirumuskan pada Persamaan (2.3):


$$
E = (S / P) × 100% = (T_serial / (P · T_paralel)) × 100% \quad (2.3)
$$

Keterangan:

* E : Persentase efisiensi komputasi paralel (%).
* S : Nilai rasio percepatan yang diperoleh dari Persamaan (2.2).
* P : Jumlah proses pekerja yang dialokasikan dalam eksekusi paralel.
Beban tambahan paralel (parallel overhead) merepresentasikan selisih waktu antara durasi eksekusi paralel aktual terhadap waktu eksekusi paralel ideal tanpa biaya koordinasi (Pacheco & Malensek, 2022). Formulasi beban tambahan paralel T_overhead dinyatakan pada Persamaan (2.4):


$$
T_overhead = T_paralel - (T_serial / P) \quad (2.4)
$$

Keterangan:

* T_overhead : Durasi beban tambahan sistem paralel akibat koordinasi sistem (detik).
* T_paralel : Waktu eksekusi paralel aktual yang terukur (detik).
* T_serial / P : Waktu eksekusi paralel ideal secara teoretis tanpa penalti koordinasi (detik).
* T_serial : Waktu eksekusi serial baseline (detik).
* P : Jumlah proses pekerja yang dialokasikan.
Parameter T_overhead mencakup spektrum biaya koordinasi sistem, termasuk latensi transmisi pipa IPC, serialisasi dan deserialisasi objek data (pickling/unpickling), replikasi baris batas (boundary halo), penggabungan kembali matriks luaran (numpy.vstack), ketimpangan beban kerja (load imbalance), serta kontensi lebar pita memori utama. Parameter T_overhead secara empiris dapat bernilai negatif apabila terjadi akselerasi superlinear yang dipicu oleh efisiensi pemanfaatan L2 Cache privat pada blok data berdimensi kecil.


### Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp–Flatt

Batas percepatan maksimum suatu sistem komputasi paralel pada ukuran masalah konstan (strong scaling) dibatasi oleh fraksi kode yang harus dieksekusi secara sekuensial, sebagaimana dirumuskan dalam Hukum Amdahl (Amdahl, 1967). Rasio percepatan teoretis Amdahl S_Amdahl dinyatakan pada Persamaan (2.5):


$$
S_Amdahl = 1 / ((1 - f) + (f / P)) \quad (2.5)
$$

Keterangan:

* S_Amdahl : Percepatan teoretis maksimum pada alokasi P proses pekerja.
* f : Fraksi beban komputasi yang dapat diparalelkan (0 ≤ f ≤ 1).
* (1 - f) : Fraksi serial efektif yang tidak mengalami paralelisasi.
* P : Jumlah proses pekerja yang dialokasikan.
Ketika alokasi prosesor ditingkatkan menuju tak hingga (P → ∞), rasio percepatan teoretis Amdahl mendekati batas asimtotik S_max = 1 / (1 - f). Formulasi ini menunjukkan bahwa keberadaan komponen sekuensial sekecil apa pun membatasi percepatan maksimum secara asimtotik.

Hukum Amdahl mengasumsikan bahwa fraksi serial bersifat konstan dan mengabaikan beban koordinasi komunikasi antar-proses. Untuk memeriksa apakah keterbatasan skalabilitas empiris bersumber dari keterbatasan sekuensial murni ataukah dipicu oleh membengkaknya beban tambahan koordinasi paralel, Karp dan Flatt (1990) merumuskan metrik fraksi serial eksperimental (experimentally determined serial fraction) e pada Persamaan (2.6):


$$
e = ((1 / S) - (1 / P)) / (1 - (1 / P)) \quad (2.6)
$$

Keterangan:

* e : Fraksi serial eksperimental (metrik Karp–Flatt).
* S : Rasio percepatan empiris yang terukur pada alokasi P proses pekerja.
* P : Jumlah proses pekerja yang dialokasikan (P > 1).
Metrik Karp–Flatt memberikan tiga indikasi diagnostik perilaku sistem komputasi paralel seiring penambahan proses pekerja P:
1. Jika nilai e meningkat secara konsisten seiring bertambahnya P, hal ini mengindikasikan bahwa keterbatasan skalabilitas terutama dipicu oleh pembengkakan beban tambahan koordinasi paralel (overhead IPC, kontensi memori, dan latensi sinkronisasi).
2. Jika nilai e relatif konstan terhadap P, hal ini mengindikasikan bahwa pembatas skalabilitas didominasi oleh fraksi kode sekuensial inheren algoritma atau beban koordinasi tetap. Perlu dicatat bahwa metrik ini tidak memisahkan fraksi sekuensial inheren dari biaya tetap komunikasi IPC.
3. Jika nilai e menurun seiring bertambahnya P, hal ini mengindikasikan adanya efek superlinearitas lokalitas memori cache privat (karena pembagian data membuat setiap sub-blok termuat penuh dalam cache berkecepatan tinggi) atau performa baseline serial yang mengalami degradasi penalti akses memori.


### Analisis Statistik Pengukuran dan Evaluasi Batas Derau Sistem (Kontrol A/A)

Akurasi pengukuran kinerja pada sistem komputer riil dipengaruhi oleh fluktuasi derau interupsi sistem operasi, penjadwalan latar belakang, dan dinamika termal perangkat keras (Pacheco & Malensek, 2022). Untuk meredam bias derau temporal, seluruh kombinasi perlakuan dieksekusi sebanyak 30 kali repetisi terkontrol yang dijalankan secara berselang-seling (interleaved execution) antara pengukuran serial dan paralel.

Data durasi waktu eksekusi pada sistem komputer umumnya memiliki distribusi yang menjulur ke kanan (right-skewed distribution) akibat adanya nilai pencilan (outliers) berkala dari interupsi sistem. Oleh karena itu, representasi pemusatan data mengutamakan statistik non-parametrik yang tangguh terhadap pencilan (robust statistics), yaitu nilai median dan rentang antarkuartil (IQR, [Q25 - Q75]), sedangkan nilai rerata sampel (x̄) dan simpangan baku (s) tetap dilaporkan sebagai parameter penunjang.

Untuk memberikan estimasi presisi statistik pada nilai rerata parameter kinerja, dihitung selang kepercayaan 95% (confidence interval) menggunakan distribusi t-Student. Penerapan distribusi t-Student pada data komputasi didasarkan pada Teorema Limit Pusat (Central Limit Theorem / CLT) untuk ukuran sampel n = 30 repetisi, didukung oleh verifikasi independensi observasi melalui estimasi koefisien autokorelasi lag-1 yang mendekati nol (ρ1 ≈ 0). Formulasi selang kepercayaan 95% dinyatakan pada Persamaan (2.7):


$$
CI_95% = x̄ ± t_(n-1, α/2) · (s / √n) \quad (2.7)
$$

Keterangan:

* CI_95% : Selang kepercayaan 95% (confidence interval) nilai rerata populasi.
* x̄ : Nilai rerata sampel dari n = 30 repetisi pengujian.
* s : Simpangan baku sampel.
* n : Ukuran sampel repetisi pengujian (n = 30, derajat kebebasan df = n - 1 = 29).
* t_(n-1, α/2) : Nilai kritis distribusi t-Student pada tingkat signifikansi α = 0,05 (t_(29; 0,025) = 2,04523).
Pengujian signifikansi perbedaan performa antar-alokasi proses pekerja paralel riil dievaluasi melalui uji hipotesis non-parametrik Kruskal–Wallis untuk variasi alokasi P = 2, 4, dan 8 proses pekerja, serta uji Mann–Whitney U untuk perbandingan dua kelompok perlakuan independen dengan taraf signifikansi α = 0,05. Pada analisis komparasi berpasangan ganda (multiple pairwise comparisons), diterapkan koreksi signifikansi (seperti koreksi Holm atau Bonferroni) guna menjaga laju kesalahan keluarga perlakuan (family-wise error rate).

Sebagai instrumen kendali mutu pengukuran, dijalankan kontrol A/A pada alokasi P = 1, yaitu dua pengukuran serial independen yang disisipkan secara berselang-seling pada protokol pengujian yang sama. Karena kedua pengukuran mengeksekusi instruksi kode yang identik pada unit pemrosesan yang sama, nilai rasio percepatan S teoretis bernilai 1,00. Simpangan nilai S empiris dari 1,00 difungsikan sebagai estimasi batas derau sistem (system noise floor) dan memverifikasi ketiadaan bias urutan (order effect). Pengujian kontrol A/A ini tidak mengukur biaya struktural komunikasi IPC.


# DAFTAR PUSTAKA (RUJUKAN BAB 2)

Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. In Proceedings of the April 18–20, 1967, Spring Joint Computer Conference (pp. 483–485). ACM. https://doi.org/10.1145/1465482.1465560

Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). Multi-directional Sobel operator kernel on GPUs. arXiv. https://doi.org/10.48550/arXiv.2305.00515

Cremel, G. D., & Arruda, L. F. M. (2026). High-performance parallel acceleration of image processing filters on multicore CPUs using OpenMP. Anais do XVII Computer on the Beach, 14–21. https://periodicos.univali.br/index.php/acotb/article/view/22235

Gonzalez, R. C., & Woods, R. E. (2018). Digital image processing (4th ed.). Pearson.

Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. Journal of Informatics, Computer Science, Data Science and Artificial Intelligence, 3(2), 1–8.

Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021) (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179

Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.

International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.

Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614

Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.

Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock

Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html

Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.

Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. Journal of Imaging, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298
