# -*- coding: utf-8 -*-
"""
Script to create standalone BAB 4 PERANCANGAN SISTEM document (.docx and .md)
from the master document for Claude's audit and independent review.
"""

import sys
import os
import shutil
from copy import deepcopy
import docx
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')

MASTER_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
MASTER_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\Laporan_Akhir_Komparasi_Kinerja_Paralel_Kerangka.docx"
STANDALONE_DOCX_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_4_PERANCANGAN_SISTEM.docx"
STANDALONE_DOCX_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_4_PERANCANGAN_SISTEM.docx"
STANDALONE_MD_LOCAL = r"d:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\BAB_4_PERANCANGAN_SISTEM.md"
STANDALONE_MD_ONEDRIVE = r"C:\Users\User\OneDrive\BAB_4_PERANCANGAN_SISTEM.md"

BAB4_REFERENCES = [
    ("Bradski, G. (2000). The OpenCV Library. Dr. Dobb's Journal of Software Tools, 25(11), 120–125.", 
     [("Bradski, G. (2000). The OpenCV Library. ", False), ("Dr. Dobb's Journal of Software Tools", True), (", 25(11), 120–125.", False)]),
    ("Gonzalez, R. C., & Woods, R. E. (2018). Digital image processing (4th ed.). Pearson.", 
     [("Gonzalez, R. C., & Woods, R. E. (2018). ", False), ("Digital image processing", True), (" (4th ed.). Pearson.", False)]),
    ("Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., ... & Oliphant, T. E. (2020). Array programming with NumPy. Nature, 585(7825), 357–362. https://doi.org/10.1038/s41586-020-2649-2", 
     [("Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., ... & Oliphant, T. E. (2020). Array programming with NumPy. ", False), ("Nature", True), (", 585(7825), 357–362. https://doi.org/10.1038/s41586-020-2649-2", False)]),
    ("Intel Corporation. (2023). 13th Generation Intel Core processor family datasheet: Volume 1 of 2. Intel Corporation.", 
     [("Intel Corporation. (2023). ", False), ("13th Generation Intel Core processor family datasheet: Volume 1 of 2", True), (". Intel Corporation.", False)]),
    ("International Telecommunication Union. (2011). Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios (Recommendation ITU-R BT.601-7). ITU.", 
     [("International Telecommunication Union. (2011). ", False), ("Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios", True), (" (Recommendation ITU-R BT.601-7). ITU.", False)]),
    ("Nixon, M. S., & Aguado, A. S. (2020). Feature extraction and image processing for computer vision (4th ed.). Academic Press. https://doi.org/10.1016/C2017-0-01934-2", 
     [("Nixon, M. S., & Aguado, A. S. (2020). ", False), ("Feature extraction and image processing for computer vision", True), (" (4th ed.). Academic Press. https://doi.org/10.1016/C2017-0-01934-2", False)]),
    ("Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.", 
     [("Pacheco, P. S., & Malensek, M. (2022). ", False), ("An introduction to parallel programming", True), (" (2nd ed.). Morgan Kaufmann.", False)]),
    ("Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", 
     [("Python Software Foundation. (n.d.-a). ", False), ("Global interpreter lock", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock", False)]),
    ("Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", 
     [("Python Software Foundation. (n.d.-b). ", False), ("multiprocessing — Process-based parallelism", True), (". Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html", False)]),
    ("Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.", 
     [("Tanenbaum, A. S., & Bos, H. (2022). ", False), ("Modern operating systems", True), (" (5th ed.). Pearson.", False)])
]

def create_standalone_bab4_docx():
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
            elif in_bab4 and p.style.name.startswith("Heading 1") and "IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN" in txt:
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
    
    # Append to standalone document body
    st_body = standalone.element.body
    # Remove default empty paragraph
    if len(st_body) > 0 and st_body[0].tag.split('}')[-1] == 'p':
        p_def = docx.text.paragraph.Paragraph(st_body[0], standalone)
        if not p_def.text:
            st_body.remove(st_body[0])
            
    for el in extracted_elements:
        cloned = deepcopy(el)
        st_body.append(cloned)
        
    # Add Daftar Pustaka Heading & Items
    p_dp_head = standalone.add_paragraph(style='Heading 1')
    p_dp_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dp_head.paragraph_format.space_before = Pt(24)
    p_dp_head.paragraph_format.space_after = Pt(12)
    p_dp_head.paragraph_format.line_spacing = 1.5
    r_dp = p_dp_head.add_run("DAFTAR PUSTAKA")
    r_dp.font.name = 'Times New Roman'
    r_dp.font.size = Pt(14)
    r_dp.bold = True
    
    for _, runs_spec in BAB4_REFERENCES:
        p_ref = standalone.add_paragraph(style='Normal')
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.first_line_indent = Cm(-1.0)
        p_ref.paragraph_format.left_indent = Cm(1.0)
        for text, italic in runs_spec:
            r = p_ref.add_run(text)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(12)
            r.italic = italic
            
    standalone.save(STANDALONE_DOCX_LOCAL)
    print(f"Saved standalone docx to: {STANDALONE_DOCX_LOCAL}")
    
    try:
        shutil.copy2(STANDALONE_DOCX_LOCAL, STANDALONE_DOCX_ONEDRIVE)
        print(f"Mirrored standalone docx to: {STANDALONE_DOCX_ONEDRIVE}")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

def create_standalone_bab4_md():
    print("=== Generating BAB 4 Standalone Markdown ===")
    md_content = """# BAB IV PERANCANGAN SISTEM

## 4.1 Deskripsi Sistem Pemrosesan Citra Paralel

Sistem pemrosesan citra digital paralel yang dirancang dalam penelitian ini beroperasi pada paradigma komputasi multi-proses (*multiprocessing*) memori terdistribusi secara logis (*process-based parallelism*) untuk mengatasi hambatan *Global Interpreter Lock* (GIL) pada CPython. Lingkungan eksekusi dibangun menggunakan bahasa pemrograman Python 3.14.3 64-bit yang dipadukan dengan pustaka pemrosesan matriks performa tinggi NumPy 2.5.4 serta pustaka visi komputer OpenCV 5.0.0.93. Sistem dirancang untuk menerima masukan berupa citra digital berformat *Lossless* PNG dengan kedalaman warna 24-bit (*True Color* RGB, 8-bit per kanal saluran). 

Alur pemrosesan data dirancang secara terisolasi menjadi tiga subsistem utama: (1) modul pra-pemrosesan citra dan dekomposisi domain spasial (partisi baris horizontal), (2) modul mesin pemrosesan paralel (*parallel compute engine*) berbasis kolam proses pekerja (*worker process pool*), dan (3) modul instrumentasi pewaktuan presisi serta verifikasi integritas luaran citra (*bit-identical validation*). Seluruh operasi pembacaan citra masukan dari media penyimpanan (*disk reading*) dan penyimpanan citra luaran ke media penyimpanan (*disk writing*) diisolasi secara ketat di luar jendela pewaktuan komputasi utama guna memastikan durasi yang terukur merefleksikan performa komputasi murni dan biaya koordinasi antar-proses.

## 4.2 Perancangan Algoritma Filter Spasial

Perancangan algoritma manipulasi citra mencakup tiga tingkat kompleksitas operasi matriks spasial yang berbeda: operasi titik (*point operation*) berintensitas komputasi rendah, operasi konvolusi spasial linear terpisah (*separable linear convolution*) berintensitas komputasi menengah, dan operasi diferensial gradien non-linear berintensitas komputasi tinggi. Ketiga filter dirancang untuk mengeksekusi kalkulasi matematis deterministik tanpa percabangan dinamis berbasis intensitas piksel (*data-independent arithmetic*).

### 4.2.1 Algoritma Filter Grayscale (Operasi Titik)

Konversi citra berwarna RGB menuju citra derajat keabuan (*grayscale*) dirancang berdasarkan model luminansi perseptual standar ITU-R Recommendation BT.601-7. Transformasi ini mereduksi dimensi kanal matriks dari tiga dimensi $H \\times W \\times 3$ menjadi matriks dua dimensi $H \\times W$ dengan menghitung kombinasi linear terbobot dari komponen saluran warna merah ($R$), hijau ($G$), dan biru ($B$) pada setiap piksel spasial $(x, y)$, sebagaimana dinyatakan pada Persamaan (4.1).

$$I_{\\text{gray}}(x, y) = \\operatorname{round}(0{,}299 \\cdot R(x, y) + 0{,}587 \\cdot G(x, y) + 0{,}114 \\cdot B(x, y)) \\quad (4.1)$$

Bobot pembobotan tersebut merefleksikan sensitivitas spektral sistem penglihatan manusia yang paling peka terhadap panjang gelombang warna hijau (58,7%), diikuti warna merah (29,9%), dan warna biru (11,4%). Pada tingkat implementasi perangkat lunak, operasi ini dieksekusi secara tervektorisasi (*vectorized array operation*) menggunakan operasi perkalian matriks NumPy bertipe data bilangan bulat tak bertanda 8-bit (*uint8*). Karena operasi titik bersifat independen secara lokal antar-piksel tanpa membutuhkan nilai piksel tetangga, algoritma Grayscale tidak memerlukan penambahan baris batas (*boundary halo*) pada batas partisi submatriks citra.

### 4.2.2 Algoritma Filter Gaussian Blur $3 \\times 3$ (Operasi Konvolusi Linear Spasial)

Penghalusan citra (*image smoothing*) dirancang menggunakan konvolusi spasial linear dengan kernel pembobotan Gaussian berdimensi $3 \\times 3$. Distribusi bobot spasial kernel Gaussian dua dimensi $G(u, v)$ diturunkan secara analitis melalui fungsi distribusi normal bivariat simetris dengan parameter deviasi standar $\\sigma = 1{,}0$, sebagaimana diformulasikan pada Persamaan (4.2).

$$G(u, v) = \\frac{1}{2\\pi\\sigma^2} \\exp\\left(-\\frac{u^2 + v^2}{2\\sigma^2}\\right) \\quad (4.2)$$

Operasi konvolusi spasial diskret diterapkan secara independen pada setiap kanal warna citra masukan dengan menjumlahkan perkalian antara intensitas piksel lokal dan bobot kernel Gaussian ternormalisasi $\\mathbf{K}_{\\text{gauss}}$, sebagaimana dinyatakan pada Persamaan (4.3).

$$I_{\\text{blur}}(x, y, c) = \\sum_{u=-1}^{1} \\sum_{v=-1}^{1} I(x + u, y + v, c) \\cdot \\mathbf{K}_{\\text{gauss}}(u, v) \\quad (4.3)$$

dengan matriks kernel pembobotan diskret ternormalisasi:

$$\\mathbf{K}_{\\text{gauss}} = \\frac{1}{16} \\begin{bmatrix} 1 & 2 & 1 \\\\ 2 & 4 & 2 \\\\ 1 & 2 & 1 \\end{bmatrix}$$

Faktor pembagi 16 memastikan pelestarian energi total luminansi citra (jumlah seluruh bobot bernilai 1,0), sehingga intensitas rerata citra luaran tetap terpelihara tanpa mengalami pergeseran tingkat kecerahan (*brightness drift*).

### 4.2.3 Algoritma Filter Sobel $3 \\times 3$ (Deteksi Tepi Diferensial Spasial)

Ekstraksi kontur dan tepi citra dirancang menggunakan operator diferensial Sobel orde pertama dengan dua kernel konvolusi terpisah berdimensi $3 \\times 3$. Komponen gradien spasial horizontal $G_x(x, y)$ dan vertikal $G_y(x, y)$ dihitung secara lokal melalui konvolusi matriks citra derajat keabuan $I_{\\text{gray}}$ terhadap kernel diferensial $\\mathbf{K}_x$ dan $\\mathbf{K}_y$, sebagaimana dinyatakan pada Persamaan (4.4) dan Persamaan (4.5).

$$G_x(x, y) = \\sum_{u=-1}^{1} \\sum_{v=-1}^{1} I_{\\text{gray}}(x + u, y + v) \\cdot \\mathbf{K}_x(u, v) \\quad (4.4)$$

$$G_y(x, y) = \\sum_{u=-1}^{1} \\sum_{v=-1}^{1} I_{\\text{gray}}(x + u, y + v) \\cdot \\mathbf{K}_y(u, v) \\quad (4.5)$$

dengan representasi matriks kernel diferensial Sobel terstandarisasi:

$$\\mathbf{K}_x = \\begin{bmatrix} -1 & 0 & 1 \\\\ -2 & 0 & 2 \\\\ -1 & 0 & 1 \\end{bmatrix}, \\quad \\mathbf{K}_y = \\begin{bmatrix} -1 & -2 & -1 \\\\ 0 & 0 & 0 \\\\ 1 & 2 & 1 \\end{bmatrix}$$

Magnitudo vektor gradien total $|\\nabla I(x, y)|$ yang merepresentasikan kekuatan tepi spasial dihitung menggunakan pendekatan magnitudo absolut Euclidean tereduksi guna mengoptimalkan throughput komputasi, sebagaimana didefinisikan pada Persamaan (4.6).

$$|\\nabla I(x, y)| = |G_x(x, y)| + |G_y(x, y)| \\quad (4.6)$$

Nilai magnitudo gradien yang dihasilkan selanjutnya dipetakan kembali ke dalam rentang dinamis citra 8-bit $[0, 255]$ melalui operasi pemotongan rentang (*clipping*) dan kuantisasi pembulatan bilangan bulat, sebagaimana dinyatakan pada Persamaan (4.7).

$$I_{\\text{sobel}}(x, y) = \\operatorname{clip}\\left(\\operatorname{round}(|\\nabla I(x, y)|), 0, 255\\right) \\quad (4.7)$$

### 4.2.4 Penanganan Tepi Lokal pada Partisi Submatriks

Dalam arsitektur pemrosesan paralel, penanganan batas tepi matriks memiliki peran yang sangat penting dalam menjaga integritas data spasial. Operasi konvolusi lingkungan $3 \\times 3$ (Gaussian Blur dan Sobel) memerlukan piksel tetangga spasial sejauh $k = 1$ baris dan kolom. Pada batas terluar citra master asli, perluasan batas dieksekusi menggunakan metode replikasi tepi lokal (*edge replication padding*, `cv2.BORDER_REPLICATE` atau `numpy.pad(..., mode='edge')`). Metode ini menduplikasi nilai intensitas piksel baris dan kolom terluar ke arah luar sejauh 1 piksel tanpa mengintroduksi diskontinuitas nilai intensitas buatan (*black borders*), sehingga menjamin konsistensi matematis yang identik antara eksekusi serial dan paralel.

## 4.3 Perancangan Arsitektur Paralel

Arsitektur sistem pemrosesan citra paralel dirancang dengan membagi beban komputasi spasial citra masukan berdimensi tinggi ke dalam sejumlah proses pekerja independen yang dieksekusi secara konkuren pada multi-core CPU. Skema alur kerja pemrosesan paralel, mulai dari pemuatan citra masukan, penambahan boundary halo, distribusi tugas melalui kolam proses pekerja, hingga rekonstruksi citra utuh dan validasi bit-identik diilustrasikan pada Gambar 4.1.

![Gambar 4.1. Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel](assets/Diagram_Blok_Arsitektur_Sistem_Pengolahan_Citra_Paralel.jpeg)
*Gambar 4.1. Diagram Blok Arsitektur Sistem Pemrosesan Citra Paralel*

### Pembagian Blok Baris Horizontal
Dekomposisi matriks citra masukan dilakukan dengan menerapkan metode partisi domain baris spasial 1D horizontal (1D horizontal slab decomposition). Matriks citra berukuran $H \\times W$ didekomposisi secara merata di sepanjang sumbu tinggi $H$ menjadi sejumlah $P$ submatriks baris, dengan $P$ merepresentasikan jumlah alokasi proses pekerja ($P \\in \\{1, 2, 4, 8\\}$). Tinggi dari setiap partisi submatriks ditentukan sebesar $H_{\\text{sub}} = H / P$. Rancangan penelitian ini memilih dimensi resolusi kelipatan kuadrat ($512, 1024, 2048, 4096$) yang dapat dibagi habis oleh seluruh variasi alokasi pekerja $P$, sehingga menghasilkan beban kerja komputasi spasial yang seimbang sempurna (*perfect load balancing*) antar-pekerja.

### Penanganan Baris Batas (Boundary Halo)
Operasi konvolusi matriks spasial (seperti Gaussian Blur $3 \\times 3$ dan Sobel $3 \\times 3$) membutuhkan informasi intensitas piksel tetangga di sekitar koordinat target. Untuk menghindari terjadinya diskontinuitas atau celah baris (*boundary artifacts*) pada sambungan antarsubmatriks, arsitektur paralel dilengkapi dengan mekanisme penambahan baris batas tumpang-tindih (*boundary halo/ghost cells*) sebesar $k = 1$ baris di sisi atas dan bawah setiap submatriks:
1. Submatriks interior (partisi tengah) menerima tambahan $2k$ baris, yaitu 1 baris tetangga atas dan 1 baris tetangga bawah, sehingga berukuran $((H/P) + 2) \\times W$.
2. Submatriks batas atas (partisi pertama) hanya menerima tambahan 1 baris tetangga bawah ($((H/P) + 1) \\times W$), sedangkan batas atasnya diekspansi menggunakan replikasi tepi lokal.
3. Submatriks batas bawah (partisi terakhir) hanya menerima tambahan 1 baris tetangga atas ($((H/P) + 1) \\times W$), sedangkan batas bawahnya diekspansi menggunakan replikasi tepi lokal.

Setelah proses filter spasial selesai dieksekusi oleh pekerja, baris *boundary halo* yang ditambahkan tersebut dipangkas kembali (*halo stripping*) sebelum data parsial dikembalikan ke proses utama, sehingga dimensi submatriks murni kembali tepat berukuran $(H/P) \\times W$.

### Distribusi Tugas dan Sinkronisasi Proses
Distribusi tugas komputasi memanfaatkan modul bawaan Python `multiprocessing.Pool` dengan metode alokasi `map()`. Model komunikasi antar-proses yang digunakan adalah *Inter-Process Communication* (IPC) berbasis pipa (*pipe*) dan antrean (*queue*) sistem operasi yang menyertakan proses serialisasi dan deserialisasi objek data memori menggunakan protokol `pickle`. Setiap proses pekerja berjalan pada ruang alamat memori virtual yang terisolasi secara mandiri, sehingga terbebas seutuhnya dari restriksi perebutan kunci *Global Interpreter Lock* (GIL) yang melekat pada thread tingkat bahasa Python.

### Rekonstruksi Citra Utuh
Setelah setiap proses pekerja menyelesaikan eksekusi filter pada blok submatriksnya masing-masing, larik hasil parsial dikirimkan kembali melalui saluran IPC menuju proses utama. Proses utama kemudian menyusun dan menggabungkan kembali seluruh submatriks luaran secara berurutan sesuai urutan indeks spasial aslinya menggunakan fungsi konkatenasi vertikal berkecepatan tinggi `numpy.vstack()`. Operasi ini merekonstruksi matriks citra keluaran berukuran utuh $H \\times W$ secara deterministik sebelum dilanjutkan ke tahap verifikasi dan penyimpanan.

## 4.4 Perancangan Pengukuran dan Pencatatan Telemetri

Pengukuran durasi waktu eksekusi komputasi dirancang dengan penempatan titik instrumentasi pewaktu berbasis fungsi monotonik `time.perf_counter()` dari pustaka standar Python. Titik stempel waktu awal (*start timestamp*, $t_{\\text{start}}$) dicatat tepat sesaat sebelum proses partisi matriks citra dan penambahan baris batas dimulai. Seluruh fase pemrosesan paralel—mencakup dekomposisi baris horizontal, serialisasi objek data (*pickle*), transmisi melalui saluran pipa IPC, eksekusi komputasi filter pada kolam proses pekerja, pemangkasan baris batas (*halo stripping*), transmisi pengembalian hasil parsial, hingga rekonstruksi citra utuh melalui `numpy.vstack`—berada di dalam jendela pengukuran waktu komputasi. Stempel waktu akhir (*stop timestamp*, $t_{\\text{stop}}$) dicatat segera setelah matriks citra utuh berhasil disusun kembali pada memori proses utama. Selisih $t_{\\text{stop}} - t_{\\text{start}}$ ditetapkan sebagai waktu eksekusi paralel aktual ($T_{\\text{paralel}}$). Operasi pembacaan citra awal dari media penyimpanan (`cv2.imread`) dan penyimpanan berkas luaran ke media penyimpanan (`cv2.imwrite`) diisolasi di luar rentang stempel waktu tersebut, sehingga durasi yang tercatat mencerminkan performa komputasi murni dan beban tambahan (*overhead*) koordinasi paralel sistem.

Pemantauan beban kerja prosesor dirancang secara asinkron menggunakan kelas `CPUMonitor` yang berjalan pada *thread daemon* latar belakang mandiri. Kelas ini melakukan percontohan (*sampling*) persentase utilisasi CPU setiap interval 20 milidetik (0,02 detik) tanpa memblokir eksekusi komputasi proses utama atau menambah latensi pada pengukuran waktu monotonik. Sebelum siklus kalkulasi dimulai, fungsi `psutil.cpu_percent(interval=None, percpu=True)` dipanggil satu kali untuk mengosongkan riwayat pembacaan internal psutil, sehingga nilai rata-rata utilisasi CPU yang dihimpun merefleksikan aktivitas prosesor selama jendela komputasi berlangsung.

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
| 11 | `efficiency` | `float64` | Persen (%) | Persentase efisiensi pemanfaatan kapasitas unit proses pekerja ($E = (S / P) \\times 100\\%$, $P > 1$). |
| 12 | `overhead` | `float64` | Detik (s) | Durasi penalti beban tambahan koordinasi paralel ($T_{\\text{overhead}} = T_{\\text{paralel}} - (T_{\\text{serial}} / P)$, $P > 1$). |
| 13 | `cpu_utilization` | `float64` | Persen (%) | Rata-rata persentase beban utilisasi prosesor sistem yang direkam oleh *thread daemon* latar belakang. |
| 14 | `is_identical` | `bool` | Boolean | Status keidentikan bit piksel: *True* jika $\\Delta_{\\max} = 0$; *False* jika terjadi perbedaan piksel. |
| 15 | `max_diff` | `float64` | Intensitas Piksel | Nilai selisih absolut maksimum intensitas piksel antara citra paralel dan serial ($\\Delta_{\\max}$). |

Data telemetri mentah yang dihimpun pada berkas `benchmark_results.csv` mencakup 810 baris pengamatan individual. Untuk memfasilitasi analisis komparatif dan pemodelan kurva skalabilitas pada Bab 5, sistem secara otomatis melakukan agregasi statistik (menghitung nilai median, rentang antarkuartil IQR, nilai rerata, dan simpangan baku per kelompok perlakuan) dan menyimpannya ke dalam berkas ikhtisar `benchmark_results_summary.csv`. Berkas data mentah dan ringkasan telemetri ini dilampirkan secara lengkap pada Lampiran A dan Lampiran B sebagai wujud transparansi ilmiah.

## 4.5 Perancangan Verifikasi Integritas Citra Bit-Identik

Perancangan verifikasi integritas citra bertujuan menjaga keabsahan luaran hasil komputasi paralel agar identik hingga level bit (*bit-identical*) terhadap citra hasil komputasi serial acuan (*ground truth baseline*). Dekomposisi domain spasial berbasis partisi baris horizontal, serialisasi data antar-proses melalui saluran pipa *Inter-Process Communication* (IPC), penambahan baris batas (*boundary halo*), hingga rekonstruksi matriks utuh melalui `numpy.vstack` membawa risiko timbulnya artefak spasial, distorsi pergeseran baris, maupun diskontinuitas nilai piksel antarsubmatriks apabila batas partisi tidak ditangani secara tepat. Verifikasi bit-identik membuktikan bahwa kelipatan percepatan komputasi (*speedup*) paralel dicapai murni melalui konkurensi eksekusi perangkat keras, tanpa degradasi kualitas citra, kehilangan informasi spasial, atau kompromi ketepatan numerik. Prosedur verifikasi ini diterapkan pada seluruh 720 pasangan pengujian serial-paralel dan 90 pasangan kontrol A/A (sehingga mencakup 810 pasangan pengujian secara individual).

Alur kerja verifikasi integritas citra dirancang melalui dua tahapan inspeksi berurutan. Tahap pertama adalah verifikasi keselarasan geometri matriks, yaitu memeriksa kesesuaian atribut dimensi (*shape*) matriks citra keluaran paralel ($I_{\\text{paralel}}$) terhadap matriks serial ($I_{\\text{serial}}$), mencakup tinggi matriks ($H$), lebar matriks ($W$), dan jumlah kanal warna ($C$). Ketidaksesuaian dimensi mengindikasikan kegagalan pada mekanisme pemangkasan baris batas (*halo stripping*) atau rekonstruksi partisi domain. Tahap kedua adalah evaluasi disparitas nilai piksel. Karena representasi citra digital menggunakan tipe data bilangan bulat tak bertanda 8-bit (*uint8*), operasi pengurangan langsung $I_{\\text{paralel}} - I_{\\text{serial}}$ rentan mengalami anomali luapan bawah (*integer underflow / modulo wraparound*), seperti nilai intensitas $0 - 1$ yang membungkus menjadi 255 pada format *uint8*. Guna mencegah galat interpretasi tersebut, matriks citra dikonversi terlebih dahulu ke tipe data bilangan riil presisi ganda bertanda (*float64*) sebelum operasi diferensiasi matriks dieksekusi.

Disparitas absolut maksimum ($\\Delta_{\\max}$) dihitung guna mendeteksi deviasi nilai piksel paling ekstrem di seluruh koordinat spasial citra, sebagaimana diformulasikan pada Persamaan (4.8).

$$\\Delta_{\\max} = \\max_{x, y} |I_{\\text{paralel}}(x, y) - I_{\\text{serial}}(x, y)| \\quad (4.8)$$

Kriteria kelulusan integritas citra ditetapkan secara biner tanpa toleransi deviasi numerik ($\\Delta_{\\max} = 0$). Evaluasi kesetaraan seluruh elemen matriks dieksekusi melalui fungsi deterministik `numpy.array_equal(I_paralel, I_serial)`. Apabila kriteria $\\Delta_{\\max} = 0$ terpenuhi, atribut `is_identical` pada rekaman telemetri dicatat bernilai `True` dan atribut `max_diff` bernilai 0,0. Sebaliknya, apabila $\\Delta_{\\max} > 0$, atribut `is_identical` dicatat bernilai `False`, nilai deviasi maksimum direkam pada atribut `max_diff`, dan iterasi tersebut ditandai sebagai anomali komputasi.

Seluruh prosedur verifikasi integritas citra bit-identik ditempatkan secara terisolasi di luar jendela pengukuran waktu komputasi, yaitu setelah stempel waktu akhir ($t_{\\text{stop}}$) dicatat oleh fungsi pewaktu `time.perf_counter()`. Dengan arsitektur isolasi ini, beban komputasi tambahan yang timbul akibat konversi tipe data ke *float64*, pengurangan matriks piksel, dan pemindaian nilai ekstrem tidak membebani catatan durasi waktu eksekusi paralel ($T_{\\text{paralel}}$) maupun metrik percepatan komputasi yang dihimpun pada sistem telemetri.

***

## DAFTAR PUSTAKA

Bradski, G. (2000). The OpenCV Library. *Dr. Dobb's Journal of Software Tools*, 25(11), 120–125.

Gonzalez, R. C., & Woods, R. E. (2018). *Digital image processing* (4th ed.). Pearson.

Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., ... & Oliphant, T. E. (2020). Array programming with NumPy. *Nature*, 585(7825), 357–362. https://doi.org/10.1038/s41586-020-2649-2

Intel Corporation. (2023). *13th Generation Intel Core processor family datasheet: Volume 1 of 2*. Intel Corporation.

International Telecommunication Union. (2011). *Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios* (Recommendation ITU-R BT.601-7). ITU.

Nixon, M. S., & Aguado, A. S. (2020). *Feature extraction and image processing for computer vision* (4th ed.). Academic Press. https://doi.org/10.1016/C2017-0-01934-2

Pacheco, P. S., & Malensek, M. (2022). *An introduction to parallel programming* (2nd ed.). Morgan Kaufmann.

Python Software Foundation. (n.d.-a). *Global interpreter lock*. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock

Python Software Foundation. (n.d.-b). *multiprocessing — Process-based parallelism*. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html

Tanenbaum, A. S., & Bos, H. (2022). *Modern operating systems* (5th ed.). Pearson.
"""
    with open(STANDALONE_MD_LOCAL, 'w', encoding='utf-8') as f:
        f.write(md_content.strip() + "\n")
    print(f"Saved standalone markdown to: {STANDALONE_MD_LOCAL}")
    
    try:
        shutil.copy2(STANDALONE_MD_LOCAL, STANDALONE_MD_ONEDRIVE)
        print(f"Mirrored standalone markdown to: {STANDALONE_MD_ONEDRIVE}")
    except Exception as e:
        print("Notice on OneDrive copy:", e)

if __name__ == '__main__':
    create_standalone_bab4_docx()
    create_standalone_bab4_md()
