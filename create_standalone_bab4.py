# -*- coding: utf-8 -*-
"""
Script to create standalone BAB 4 PERANCANGAN SISTEM document (.docx and .md)
directly extracted from the master document, without artificial bibliography
(as per Buku Panduan Tugas Akhir Prodi RSK FMIPA UNTAN 2022).
"""

import sys
import os
import shutil
from copy import deepcopy
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.stdout.reconfigure(encoding='utf-8')

MASTER_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
STANDALONE_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_4_PERANCANGAN_SISTEM.docx"
STANDALONE_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_4_PERANCANGAN_SISTEM.docx"
STANDALONE_MD_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_4_PERANCANGAN_SISTEM.md"
STANDALONE_MD_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_4_PERANCANGAN_SISTEM.md"

def create_standalone_bab4():
    print("=== Extracting BAB 4 to Standalone DOCX ===")
    master = docx.Document(MASTER_DOCX_LOCAL)
    standalone = docx.Document()
    
    # Page setup
    for sec in standalone.sections:
        sec.top_margin = Cm(3.0)
        sec.bottom_margin = Cm(3.0)
        sec.left_margin = Cm(4.0)
        sec.right_margin = Cm(3.0)
        
    master_body = master.element.body
    master_elements = list(master_body)
    
    in_bab4 = False
    extracted_elements = []
    
    for el in master_elements:
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(el, master)
            txt = p.text.strip()
            if p.style.name.startswith("Heading 1") and "PERANCANGAN SISTEM" in txt:
                in_bab4 = True
            elif in_bab4 and p.style.name.startswith("Heading 1") and "IMPLEMENTASI" in txt:
                in_bab4 = False
                break
                
        if in_bab4:
            extracted_elements.append(el)
            
    # Remove trailing page break paragraph if any
    while extracted_elements:
        last_el = extracted_elements[-1]
        if last_el.tag.split('}')[-1] == 'p':
            p_last = docx.text.paragraph.Paragraph(last_el, master)
            if not p_last.text.strip() and '<w:br' in last_el.xml:
                extracted_elements.pop()
                continue
        break
        
    print(f"Extracted {len(extracted_elements)} elements from Bab 4.")
    
    st_body = standalone.element.body
    if len(st_body) > 0 and st_body[0].tag.split('}')[-1] == 'p':
        p_def = docx.text.paragraph.Paragraph(st_body[0], standalone)
        if not p_def.text:
            st_body.remove(st_body[0])
            
    for el in extracted_elements:
        cloned = deepcopy(el)
        st_body.append(cloned)
        
    standalone.save(STANDALONE_DOCX_LOCAL)
    print(f"Saved standalone docx to: {STANDALONE_DOCX_LOCAL}")
    
    try:
        shutil.copy2(STANDALONE_DOCX_LOCAL, STANDALONE_DOCX_ONEDRIVE)
        print(f"Mirrored standalone docx to: {STANDALONE_DOCX_ONEDRIVE}")
    except Exception as e:
        print("Notice on OneDrive copy (docx):", e)

def create_standalone_bab4_md():
    print("=== Generating BAB 4 Standalone Markdown ===")
    md_content = """# BAB 4 PERANCANGAN SISTEM

## 4.1 Deskripsi Sistem Pemrosesan Citra Paralel

Sistem pemrosesan citra paralel pada penelitian ini dirancang dengan menerapkan paradigma dekomposisi data (*data parallelism*) guna mempercepat eksekusi operasi filter spasial pada citra digital beresolusi tinggi. Alur kerja sistem memadukan pengelolaan struktur larik multidimensi pustaka NumPy, orkestrasi proses paralel modul bawaan Python multiprocessing, serta pemanfaatan pustaka OpenCV yang dibatasi hanya untuk operasi pembacaan dan penyimpanan berkas citra masukan dan luaran (*file I/O*). Guna memastikan bahwa akselerasi pemrosesan bersumber dari alokasi proses pekerja paralel tanpa campur tangan utas internal OpenCV, konkurensi internal pustaka dinonaktifkan melalui pengaturan parameter `cv2.setNumThreads(1)`.

Berkas citra digital berformat RGB dibaca ke dalam memori utama menggunakan fungsi `cv2.imread()` dan direpresentasikan sebagai matriks piksel tiga dimensi berukuran $H \\times W \\times C$, dengan $H$ merepresentasikan tinggi matriks (jumlah baris piksel), $W$ merepresentasikan lebar matriks (jumlah kolom piksel), dan $C$ menyatakan jumlah kanal warna (tiga kanal untuk format warna RGB). Struktur larik NumPy dialokasikan dalam memori mengikuti urutan berbasis baris (*row-major order* atau tata letak memori *C-contiguous*), sehingga seluruh elemen piksel yang berada pada baris horizontal yang sama menempati alamat ruang memori fisik yang berurutan secara linier. Susunan pengalamatan memori ini dirancang guna mendukung derajat lokalitas spasial (*spatial locality*) dan meminimalkan kegagalan pemuatan memori cache (*cache misses*) saat baris-baris piksel diakses secara berurutan oleh unit pemrosesan prosesor.

## 4.2 Perancangan Algoritma Filter Spasial

Perancangan algoritma filter spasial citra pada penelitian ini mencakup tiga tingkatan kompleksitas komputasi: konversi derajat keabuan (Grayscale ITU-R BT.601-7) sebagai representasi operasi titik (*point-wise*) berbeban ringan, penghalusan citra (Gaussian Blur $3 \\times 3$) sebagai representasi konvolusi spasial berbeban moderat pada tiga kanal warna, serta ekstraksi tepi (Sobel $3 \\times 3$) sebagai representasi konvolusi gradien ganda intensif komputasi. Seluruh algoritma dirancang menggunakan kalkulasi larik NumPy tanpa percabangan kondisional (*data-independent execution*) guna memastikan stabilitas instruksi siklus pemrosesan per piksel.

### 4.2.1 Algoritma Filter Grayscale (Operasi Titik)

Konversi citra digital berwarna RGB menjadi derajat keabuan dirancang berdasarkan rekomendasi standar penyiaran ITU-R BT.601-7. Operasi ini menghitung nilai intensitas luma monokrom $Y'$ dari kombinasi linier terbobot tiga komponen kanal warna masukan (Merah $R'$, Hijau $G'$, dan Biru $B'$ ter-gamma) pada setiap koordinat spasial piksel $(x, y)$. Formulasi matematis konversi dinyatakan pada Persamaan (4.1):

$$Y'(x, y) = \\operatorname{round}(0{,}299 \\cdot R'(x, y) + 0{,}587 \\cdot G'(x, y) + 0{,}114 \\cdot B'(x, y)) \\quad (4.1)$$

Keterangan:
- $Y'(x, y)$ : Nilai intensitas luma derajat keabuan pada koordinat $(x, y)$ $[0, 255]$.
- $R'(x, y)$ : Nilai intensitas kanal warna Merah (*Red*) masukan ter-gamma $[0, 255]$.
- $G'(x, y)$ : Nilai intensitas kanal warna Hijau (*Green*) masukan ter-gamma $[0, 255]$.
- $B'(x, y)$ : Nilai intensitas kanal warna Biru (*Blue*) masukan ter-gamma $[0, 255]$.

Operasi ini memiliki radius ketetanggaan kernel $k = 0$, karena kalkulasi setiap piksel bersifat independen secara spasial dan tidak membutuhkan informasi nilai piksel di sekitarnya. Pada implementasi program, larik citra masukan bertipe `uint8` dikonversi sementara ke tipe data `float64` oleh NumPy untuk mengalikan bobot koefisien desimal guna mencegah galat pembulatan dini. Nilai hasil kemudian dibulatkan dan dipotong pada batas saturasi rentang $[0, 255]$ menggunakan fungsi `numpy.clip` sebelum dikembalikan ke tipe data `uint8`. Transformasi ini menghasilkan luaran matriks dua dimensi berukuran $H \\times W$ dari citra masukan tiga dimensi berukuran $H \\times W \\times 3$.

### 4.2.2 Algoritma Filter Gaussian Blur $3 \\times 3$

Penghalusan citra (*image smoothing*) dirancang menggunakan konvolusi spasial linear dengan kernel Gaussian $3 \\times 3$ berbasis pendekatan koefisien binomial diskret ternormalisasi. Kernel ini merupakan aproksimasi diskret berbobot bilangan bulat dari fungsi sebaran normal bivariat simetris yang setara dengan parameter deviasi standar $\\sigma \\approx 0{,}85$. Matriks kernel pembobotan simetris dua dimensi $\\mathbf{K}_{\\text{Gauss}}$ dengan faktor normalisasi $1/16$ didefinisikan pada Persamaan (4.2):

$$\\mathbf{K}_{\\text{Gauss}} = \\frac{1}{16} \\begin{bmatrix} 1 & 2 & 1 \\\\ 2 & 4 & 2 \\\\ 1 & 2 & 1 \\end{bmatrix} \\quad (4.2)$$

Operasi konvolusi spasial diskret diterapkan secara independen pada setiap kanal warna $c \\in \\{R, G, B\\}$ dengan radius ketetanggaan kernel $k = 1$. Secara matematis, kernel Gaussian dapat dipisahkan (*separable*) menjadi dua vektor satu dimensi, namun pada rancangan implementasi penelitian ini konvolusi dieksekusi secara langsung melalui akumulasi konvolusi 2D 9-tap per piksel. Formulasi nilai intensitas piksel keluaran terfilter $I_{\\text{blur}}(x, y, c)$ dinyatakan pada Persamaan (4.3):

$$I_{\\text{blur}}(x, y, c) = \\sum_{i=-1}^{1} \\sum_{j=-1}^{1} \\mathbf{K}_{\\text{Gauss}}(i + 1, j + 1) \\cdot I(x + i, y + j, c) \\quad (4.3)$$

Kalkulasi dilakukan dalam representasi data presisi `float64` dengan menjumlahkan perkalian antara intensitas piksel lokal dan bobot kernel, diikuti pembulatan, pemotongan saturasi rentang $[0, 255]$ melalui `numpy.clip`, dan konversi akhir ke tipe data `uint8`. Karena konvolusi diaplikasikan pada masing-masing kanal warna RGB secara terpisah, keluaran filter Gaussian Blur mempertahankan dimensi larik tiga dimensi yang identik dengan masukan, yaitu $H \\times W \\times 3$.

### 4.2.3 Algoritma Filter Sobel $3 \\times 3$

Ekstraksi kontur dan tepi citra dirancang menggunakan operator diferensial Sobel $3 \\times 3$. Citra masukan yang diterima oleh sistem berformat warna RGB. Pada alur paralel, potongan citra RGB dikirimkan ke setiap proses pekerja melalui saluran IPC. Konversi ke derajat keabuan (Grayscale) dieksekusi secara lokal di dalam masing-masing proses pekerja sebelum perhitungan gradien dimulai. Selanjutnya, diaplikasikan dua matriks kernel konvolusi ortogonal, yaitu kernel horizontal $\\mathbf{K}_x$ untuk mendeteksi perubahan gradien intensitas pada sumbu mendatar (kolom) dan kernel vertikal $\\mathbf{K}_y$ untuk sumbu tegak (baris), sebagaimana dirumuskan pada Persamaan (4.4):

$$\\mathbf{K}_x = \\begin{bmatrix} -1 & 0 & 1 \\\\ -2 & 0 & 2 \\\\ -1 & 0 & 1 \\end{bmatrix}, \\quad \\mathbf{K}_y = \\begin{bmatrix} -1 & -2 & -1 \\\\ 0 & 0 & 0 \\\\ 1 & 2 & 1 \\end{bmatrix} \\quad (4.4)$$

Komponen gradien spasial mendatar $G_x(x, y)$ dan tegak $G_y(x, y)$ dihitung secara terpisah melalui konvolusi matriks derajat keabuan $Y$ dengan radius kernel $k = 1$ pada Persamaan (4.5) dan Persamaan (4.6):

$$G_x(x, y) = \\sum_{i=-1}^{1} \\sum_{j=-1}^{1} \\mathbf{K}_x(i + 1, j + 1) \\cdot Y(x + i, y + j) \\quad (4.5)$$

$$G_y(x, y) = \\sum_{i=-1}^{1} \\sum_{j=-1}^{1} \\mathbf{K}_y(i + 1, j + 1) \\cdot Y(x + i, y + j) \\quad (4.6)$$

Magnitudo gradien total $G(x, y)$ yang merepresentasikan kekuatan tepi citra dihitung menggunakan formulasi jarak Euclidean (norma L2) pada Persamaan (4.7):

$$G(x, y) = \\sqrt{G_x(x, y)^2 + G_y(x, y)^2} \\quad (4.7)$$

Nilai magnitudo gradien $G(x, y)$ dipotong pada batas rentang $[0, 255]$ via `numpy.clip` dan dikonversi kembali ke tipe data `uint8`. Hasil akhir komputasi filter Sobel menghasilkan larik matriks dua dimensi berukuran $H \\times W$ (atau $(H/P) \\times W$ pada masing-masing proses pekerja) yang merepresentasikan peta kontur tepi citra.

### 4.2.4 Penanganan Tepi Lokal pada Partisi Submatriks

Dalam arsitektur pemrosesan paralel, penanganan batas tepi matriks memiliki dua tingkatan: batas global (tepi terluar citra asli) dan batas lokal (sambungan antar-blok pekerja). Untuk batas lokal antar-pekerja, sistem menerapkan mekanisme penambahan baris batas (*boundary halo*) yang dibahas pada Subbab 4.3. Sedangkan pada level eksekusi fungsi filter di dalam masing-masing submatriks, penanganan tepi dilakukan secara seragam menggunakan metode replikasi batas (*edge replication padding*) selebar $k = 1$ piksel melalui fungsi `numpy.pad(..., mode='edge')`. Konfigurasi lebar bantalan diterapkan secara spesifik pada sumbu spasial, yaitu `((1, 1), (1, 1))` untuk citra dua dimensi atau `((1, 1), (1, 1), (0, 0))` untuk citra RGB tanpa menambahkan bantalan pada sumbu kanal warna. Metode replikasi ini menduplikasi nilai piksel terluar ke area bantalan batas, sehingga menghasilkan konsistensi matematis yang identik antara eksekusi serial dan paralel serta mencegah timbulnya distorsi penggelapan piksel (*zero-padding darkening artifact*) pada garis sambungan batas potongan citra saat direkonstruksi kembali.

## 4.3 Perancangan Arsitektur Paralel

Arsitektur sistem pemrosesan citra paralel dirancang dengan membagi beban komputasi spasial ke seluruh unit proses pekerja melalui tahapan dekomposisi domain spasial horizontal, penambahan baris batas (*boundary halo*), transmisi tugas antar-proses, dan rekonstruksi kembali matriks luaran utuh. Diagram blok arsitektur sistem pemrosesan citra paralel disajikan secara skematis pada Gambar 4.1.

*(Gambar 4.1 Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel tersemat pada dokumen master)*

### Pembagian Blok Baris Horizontal

Dekomposisi matriks citra masukan dilakukan dengan menerapkan metode pembagian baris horizontal (*horizontal row partitioning*). Matriks citra berdimensi $H \\times W \\times C$ dipotong secara merata sepanjang sumbu vertikal ke sejumlah $P$ proses pekerja, sehingga setiap unit pekerja menerima blok data irisan citra berukuran $(H/P) \\times W \\times C$. Dimensi resolusi citra yang dipilih berbasis bilangan pangkat dua ($2^k$, yaitu 512, 1024, 2048, dan 4096 piksel) dan alokasi jumlah proses pekerja $P$ (1, 2, 4, dan 8 proses) memiliki sifat habis dibagi ($H \\pmod P = 0$). Karakteristik keterbagian ini menghasilkan pembagian jumlah baris dasar yang setara antar-pekerja, meskipun beban komputasi riil memiliki variasi kecil karena blok interior memproses dua baris batas halo tambahan dan inti prosesor hibrida memiliki karakteristik frekuensi kerja yang berbeda.

### Penanganan Baris Batas (Boundary Halo)

Operasi konvolusi matriks spasial (seperti Gaussian Blur $3 \\times 3$ dan Sobel $3 \\times 3$) membutuhkan informasi intensitas piksel tetangga di sekeliling piksel target dengan radius spasial $k = 1$. Pada saat citra dipartisi menjadi potongan-potongan baris independen, piksel-piksel yang berada pada baris tepi atas dan bawah dari setiap potongan kehilangan akses terhadap baris tetangga aslinya. Untuk mengatasi ketergantungan data lokal tersebut tanpa menimbulkan konflik akses memori, setiap blok irisan citra diperluas dengan menambahkan $k$ baris tetangga fisik di sisi atas dan bawah yang disebut sebagai baris batas (*boundary halo*). Untuk blok interior (blok pekerja di antara batas citra terluar), ditambahkan satu baris batas atas dari blok sebelumnya dan satu baris batas bawah dari blok sesudahnya, menghasilkan potongan masukan berukuran $((H/P) + 2k) \\times W \\times C$. Adapun untuk blok pertama (paling atas), penambahan baris batas hanya dilakukan pada sisi bawah, dan untuk blok terakhir (paling bawah), penambahan baris batas hanya dilakukan pada sisi atas, masing-masing berukuran $((H/P) + k) \\times W \\times C$. Baris batas ini dibaca secara mandiri oleh proses pekerja tanpa adanya operasi penulisan balik ke proses lain, sehingga meniadakan potensi terjadinya kondisi balapan (*race condition*). 

Volume transmisi data yang dialirkan melalui saluran IPC per pekerja pada fase distribusi dinyatakan oleh $V_{\\text{in}} = ((H/P) + 2k) \\times W \\times C_{\\text{in}} \\times \\text{sizeof(uint8)}$, sedangkan pada fase pengembalian hasil dinyatakan oleh $V_{\\text{out}} = (H/P) \\times W \\times C_{\\text{out}} \\times \\text{sizeof(uint8)}$. Sebagai contoh, pada resolusi $4096 \\times 4096$ piksel dengan alokasi $P = 8$, blok interior Gaussian dan Sobel menerima $V_{\\text{in}} = (512 + 2) \\times 4096 \\times 3 \\text{ bita} \\approx 6{,}32\\text{ MB}$, dan mengembalikan $V_{\\text{out}} \\approx 6{,}29\\text{ MB}$ untuk Gaussian ($C_{\\text{out}} = 3$) atau $V_{\\text{out}} \\approx 2{,}10\\text{ MB}$ untuk Sobel ($C_{\\text{out}} = 1$).

### Distribusi Tugas dan Sinkronisasi Proses

Distribusi tugas komputasi memanfaatkan modul bawaan Python `multiprocessing`. Modul ini dipilih untuk mengatasi kendala *Global Interpreter Lock* (GIL) pada CPython yang membatasi eksekusi *multithreading* pada beban kerja intensif komputasi (*CPU-bound*) sehingga hanya menghasilkan percepatan marjinal sekitar 1,05 kali. Modul `multiprocessing` melangkahi hambatan GIL dengan menciptakan proses sistem operasi yang independen, dengan setiap proses pekerja memiliki ruang alamat memori (*address space*) dan instansiasi interpreter mandiri. Mekanisme ini tidak berbagi GIL antar-proses, sehingga memungkinkan terjadinya eksekusi paralel pada inti fisik prosesor *multi-core*. Seluruh blok irisan citra yang telah dilengkapi baris batas dibungkus ke dalam pasangan argumen (*tuple payload*) bersama parameter filter, kemudian didistribusikan secara simultan ke kolam pekerja (*worker pool*) melalui fungsi pemetaan `multiprocessing.Pool.map()`. Setiap proses pekerja mengeksekusi algoritma filter yang ditugaskan secara serentak pada blok memorinya masing-masing tanpa interupsi komunikasi antar-pekerja selama fase komputasi berlangsung.

### Rekonstruksi Citra Utuh

Setelah setiap proses pekerja menyelesaikan eksekusi filter pada blok masing-masing, langkah berikutnya adalah mengembalikan dimensi blok terfilter ke ukuran murni aslinya. Setiap proses pekerja melakukan pemotongan pembuangan (*halo stripping*) terhadap baris batas atas dan baris batas bawah yang sebelumnya ditambahkan, sehingga ukuran matriks hasil kembali tepat berukuran $(H/P) \\times W$ (atau $(H/P) \\times W \\times C$ untuk operasi yang mempertahankan kanal warna). Blok-blok luaran yang bersih dari baris batas tersebut kemudian dikirimkan kembali ke proses utama (*master process*) melalui saluran komunikasi antre pipa IPC (*Inter-Process Communication*). Proses utama selanjutnya menyatukan kembali potongan-potongan blok luaran secara sekuensial sepanjang sumbu vertikal menggunakan fungsi penggabungan larik `numpy.vstack()`. Rekonstruksi ini menghasilkan matriks citra utuh berukuran $H \\times W$ yang siap divalidasi dan disimpan.

## 4.4 Perancangan Pengukuran dan Pencatatan Telemetri

Pengukuran durasi waktu eksekusi komputasi dirancang dengan penempatan titik instrumentasi pewaktu berbasis fungsi monotonik `time.perf_counter()` dari pustaka standar Python. Sebagaimana dijelaskan pada Subbab 3.5.1, inisialisasi kolam proses pekerja dan prosedur pemanasan awal (*pre-warming*) dieksekusi sebelum jendela waktu pengukuran dimulai guna mengeliminasi penalti inisialisasi proses. Titik stempel waktu awal (*start timestamp*, $t_{\\text{start}}$) dicatat tepat sesaat sebelum proses partisi matriks citra dan penambahan baris batas dimulai. Seluruh fase pemrosesan paralel—mencakup dekomposisi baris horizontal, serialisasi objek data (*pickle*), transmisi melalui saluran pipa IPC, eksekusi komputasi filter pada kolam proses pekerja, pemangkasan baris batas (*halo stripping*), transmisi pengembalian hasil parsial, hingga rekonstruksi citra utuh melalui `numpy.vstack`—berada di dalam jendela pengukuran waktu komputasi. Stempel waktu akhir (*stop timestamp*, $t_{\\text{stop}}$) dicatat segera setelah matriks citra utuh berhasil disusun kembali pada memori proses utama. Selisih $t_{\\text{stop}} - t_{\\text{start}}$ ditetapkan sebagai waktu eksekusi paralel aktual ($T_{\\text{paralel}}$). Secara simetris, durasi waktu eksekusi serial ($T_{\\text{serial}}$) diukur dari sesaat sebelum fungsi filter dipanggil (mencakup replikasi batas tepi dan kalkulasi konvolusi) hingga matriks hasil selesai terbentuk pada memori. Operasi pembacaan citra awal dari media penyimpanan (`cv2.imread`) dan penyimpanan berkas luaran ke media penyimpanan (`cv2.imwrite`) diisolasi di luar rentang stempel waktu tersebut, sehingga durasi yang tercatat mencerminkan performa komputasi dan beban tambahan (*overhead*) koordinasi paralel sistem.

Pemantauan beban kerja prosesor dirancang secara asinkron menggunakan kelas `CPUMonitor` yang berjalan pada *thread daemon* latar belakang mandiri. Kelas ini melakukan percontohan (*sampling*) persentase utilisasi CPU setiap interval 20 milidetik (0,02 detik) melalui pemanggilan `psutil.cpu_percent(interval=None, percpu=True)` tanpa memblokir kalkulasi pada proses utama. Sebelum jendela eksekusi dimulai, fungsi tersebut dipanggil satu kali untuk mengosongkan riwayat pembacaan internal psutil. Pemantau CPU dimulai tepat sebelum eksekusi komputasi dan dihentikan segera setelah rekonstruksi citra utuh selesai (sebelum prosedur verifikasi bit-identik), sehingga nilai rata-rata utilisasi CPU yang dihimpun merefleksikan aktivitas prosesor selama jendela komputasi berlangsung.

Guna mendukung keterlacakan data (*data traceability*) dan keterulangan pengujian, seluruh data hasil pengukuran dari 810 pasangan repetisi eksperimen disimpan ke dalam berkas telemetri berformat *Comma-Separated Values* (CSV). Setiap baris rekaman merepresentasikan satu iterasi pengujian terperinci dengan 15 atribut parameter kinerja. Struktur skema data telemetri dirangkum pada Tabel 4.1.

**Tabel 4.1 Skema Struktur Data Telemetri Kinerja CSV (15 Kolom Rekaman)**

| No. | Nama Atribut (Kolom CSV) | Tipe Data | Satuan / Format | Deskripsi dan Peran Metodologis |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `timestamp` | `str` | YYYY-MM-DD HH:MM:SS | Stempel waktu penanda eksekusi awal blok perlakuan eksperimen. |
| 2 | `scenario` | `str` | Kategori (A, B, C) | Kode blok skenario eksperimen yang sedang dieksekusi. |
| 3 | `filter` | `str` | Nama Filter | Algoritma filter spasial yang diuji (Grayscale, Gaussian Blur, Sobel). |
| 4 | `resolution` | `int64` | Piksel (px) | Dimensi panjang dan lebar sisi matriks citra bujur sangkar (512, 1024, 2048, 4096). |
| 5 | `image_id` | `str` | Identifier Teks | Identitas berkas citra acuan master yang diproses (misal: *ref_img_01_512px*). |
| 6 | `iteration` | `int64` | Indeks (1 s.d. 30) | Nomor urut repetisi pengujian berpasangan serial-paralel. |
| 7 | `p` | `int64` | Unit Pekerja | Alokasi jumlah proses pekerja pada kolam pemrosesan ($P \\in \\{1, 2, 4, 8\\}$). |
| 8 | `t_serial` | `float64` | Detik (s) | Durasi waktu eksekusi komputasi serial satu inti prosesor (nilai acuan *baseline*). |
| 9 | `t_parallel` | `float64` | Detik (s) | Durasi waktu eksekusi komputasi paralel murni (atau pengukuran serial kedua independen pada $P = 1$). |
| 10 | `speedup` | `float64` | Nirdimensi | Rasio kelipatan percepatan komputasi empiris ($S = T_{\\text{serial}} / T_{\\text{paralel}}$). |
| 11 | `efficiency` | `float64` | Persen (%) | Persentase efisiensi pemanfaatan kapasitas unit proses pekerja ($E = (S / P) \\times 100\\%$, dicatat matematis pada semua baris termasuk $P = 1$, namun dianalisis formal untuk $P > 1$). |
| 12 | `overhead` | `float64` | Detik (s) | Durasi penalti beban tambahan koordinasi paralel ($T_{\\text{overhead}} = T_{\\text{paralel}} - (T_{\\text{serial}} / P)$, dicatat matematis pada semua baris termasuk $P = 1$, namun dianalisis formal untuk $P > 1$). |
| 13 | `cpu_utilization` | `float64` | Persen (%) | Rata-rata persentase beban utilisasi prosesor sistem yang direkam oleh *thread daemon* latar belakang. |
| 14 | `is_identical` | `bool` | Boolean | Status keidentikan bit piksel: *True* jika $\\Delta_{\\max} = 0$; *False* jika terjadi perbedaan piksel. |
| 15 | `max_diff` | `float64` | Intensitas Piksel | Nilai selisih absolut maksimum intensitas piksel antara citra paralel dan serial ($\\Delta_{\\max}$). |

Data telemetri mentah yang dihimpun pada berkas `benchmark_results.csv` mencakup 810 baris pengamatan individual (720 pasangan serial-paralel dan 90 pasangan kontrol A/A). Pada baris pengamatan kontrol A/A ($P = 1$), nilai efisiensi dan *overhead* tetap dicatat secara matematis oleh skrip sebagai indikator batas derau sistem, namun dieksklusikan dari pemodelan kurva skalabilitas komputasi paralel. Untuk memfasilitasi analisis komparatif dan pemodelan kurva skalabilitas pada Bab 5, sistem secara otomatis melakukan agregasi statistik (menghitung nilai median, rentang antarkuartil IQR, nilai rerata, simpangan baku, dan selang kepercayaan 95% per kelompok perlakuan) dan menyimpannya ke dalam berkas ikhtisar 49 kolom `benchmark_results_summary.csv`. Berkas data mentah dan ringkasan telemetri ini dilampirkan secara lengkap pada Lampiran A dan Lampiran B sebagai wujud transparansi ilmiah.

## 4.5 Perancangan Verifikasi Integritas Citra Bit-Identik

Perancangan verifikasi integritas citra bertujuan menjaga keabsahan luaran hasil komputasi paralel agar identik hingga level bit (*bit-identical*) terhadap citra hasil komputasi serial acuan (*ground truth baseline*). Dekomposisi domain spasial berbasis partisi baris horizontal, serialisasi data antar-proses melalui saluran pipa *Inter-Process Communication* (IPC), penambahan baris batas (*boundary halo*), hingga rekonstruksi matriks utuh melalui `numpy.vstack` membawa risiko timbulnya artefak spasial, distorsi pergeseran baris, maupun diskontinuitas nilai piksel antarsubmatriks apabila batas partisi tidak ditangani secara tepat. Verifikasi bit-identik memastikan bahwa luaran paralel bernilai setara secara deterministik piksel-per-piksel terhadap hasil serial acuan pada citra uji, sehingga selisih waktu eksekusi tidak dapat dikaitkan dengan perbedaan luaran komputasi. Prosedur verifikasi ini diterapkan pada seluruh 720 pasangan pengujian serial-paralel dan 90 pasangan kontrol A/A (mencakup 810 pasangan pengujian secara individual).

Alur kerja verifikasi integritas citra dirancang melalui dua tahapan inspeksi berurutan. Tahap pertama adalah verifikasi keselarasan geometri matriks, yaitu memeriksa kesesuaian atribut dimensi (*shape*) matriks citra keluaran paralel ($I_{\\text{paralel}}$) terhadap matriks serial ($I_{\\text{serial}}$), mencakup tinggi matriks ($H$), lebar matriks ($W$), dan jumlah kanal warna ($C$). Apabila dimensi tidak cocok, pengujian langsung dinyatakan gagal. Tahap kedua adalah evaluasi kesetaraan seluruh elemen matriks secara deterministik menggunakan fungsi `numpy.array_equal(I_paralel, I_serial)`. Apabila fungsi tersebut mengembalikan nilai *True*, kondisi disparitas absolut maksimum terpenuhi tanpa perbedaan piksel ($\\Delta_{\\max} = 0$), atribut `is_identical` dicatat bernilai *True*, dan `max_diff` bernilai 0,0. Sebaliknya, apabila terdeteksi perbedaan (*False*), matriks citra dikonversi ke tipe data bilangan riil presisi ganda (`float64`) guna mencegah anomali luapan bawah (*modulo wraparound*) pada format `uint8` saat menghitung nilai selisih absolut maksimum ($\\Delta_{\\max}$), atribut `is_identical` dicatat *False*, dan iterasi ditandai sebagai anomali komputasi.

Disparitas absolut maksimum ($\\Delta_{\\max}$) dihitung guna mendeteksi deviasi nilai piksel paling ekstrem di seluruh koordinat spasial citra, sebagaimana diformulasikan pada Persamaan (4.8):

$$\\Delta_{\\max} = \\max_{x, y} |I_{\\text{paralel}}(x, y) - I_{\\text{serial}}(x, y)| \\quad (4.8)$$

Kriteria kelulusan integritas citra ditetapkan secara biner tanpa toleransi deviasi numerik ($\\Delta_{\\max} = 0$). Evaluasi deterministik ini mengonfirmasi kesetaraan nilai numerik piksel pada citra hasil pengujian secara objektif. Pada 90 pasangan pengujian kontrol A/A ($P = 1$), prosedur verifikasi menghasilkan keidentikan bit piksel yang konsisten sebagai verifikasi dasar bahwa dua pemanggilan serial independen menghasilkan nilai yang identik.

Seluruh prosedur verifikasi integritas citra bit-identik ditempatkan secara terisolasi di luar jendela pengukuran waktu komputasi, yaitu setelah stempel waktu akhir ($t_{\\text{stop}}$) dicatat oleh fungsi pewaktu `time.perf_counter()`. Melalui arsitektur isolasi ini, beban komputasi tambahan yang timbul akibat konversi tipe data ke `float64`, pengurangan matriks piksel, dan pemindaian nilai ekstrem tidak membebani catatan durasi waktu eksekusi paralel ($T_{\\text{paralel}}$) maupun metrik percepatan komputasi yang dihimpun pada sistem telemetri.
"""
    with open(STANDALONE_MD_LOCAL, 'w', encoding='utf-8') as f:
        f.write(md_content.strip() + "\n")
    print(f"Saved standalone markdown to: {STANDALONE_MD_LOCAL}")
    
    try:
        shutil.copy2(STANDALONE_MD_LOCAL, STANDALONE_MD_ONEDRIVE)
        print(f"Mirrored standalone markdown to: {STANDALONE_MD_ONEDRIVE}")
    except Exception as e:
        print("Notice on OneDrive copy (md):", e)

if __name__ == '__main__':
    create_standalone_bab4()
    create_standalone_bab4_md()
