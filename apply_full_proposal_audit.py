
import docx

doc_path = r'd:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Proposal Komputasi Paralel_revisi_audit.docx'
doc = docx.Document(doc_path)

lb_p1 = (
    'Perkembangan kamera digital dan sensor pencitraan terus memperbesar ukuran matriks citra '
    'yang harus diproses oleh sistem visi komputer modern (Cremel & Arruda, 2026). Citra beresolusi '
    'tinggi, yang dalam satu berkas dapat memuat jutaan piksel, telah diterapkan secara luas pada berbagai '
    'bidang strategis, antara lain sistem penunjang diagnosis medis, pemantauan pertanian cerdas berbasis '
    'sensor udara, dan inspeksi visual otomasi industri (Cremel & Arruda, 2026). Setiap elemen piksel pada '
    'matriks tersebut harus diproses melalui operasi spasial seperti konvolusi, yang beban komputasinya tumbuh '
    'seiring peningkatan dimensi citra dan ukuran matriks kernel yang digunakan (Cremel & Arruda, 2026; '
    'Gonzalez & Woods, 2018). Pada operasi deteksi tepi Sobel, nilai intensitas setiap piksel dihitung dari '
    'interaksi piksel ketetanggaannya melalui konvolusi kernel turunan ganda (Gx dan Gy). Karakteristik komputasi '
    'ini menyebabkan beban kalkulasi berbanding lurus dengan jumlah total piksel, sehingga kebutuhan komputasi '
    'bertambah secara kuadratik atau empat kali lipat setiap kali panjang sisi citra digandakan.'
)

lb_p2 = (
    'Di sisi lain, perkembangan arsitektur perangkat keras prosesor modern telah beralih ke integrasi '
    'banyak inti fisik (multi-core processor) yang mampu mengeksekusi instruksi secara serentak '
    '(Pacheco & Malensek, 2022). Akan tetapi, perangkat lunak yang dirancang secara serial konvensional '
    'tidak dapat memanfaatkan ketersediaan inti tambahan tersebut secara otomatis (Pacheco & Malensek, 2022). '
    'Eksekusi program serial hanya membebani satu inti prosesor, sementara inti-inti lainnya berada dalam '
    'kondisi menganggur (idle), sehingga kapasitas daya komputasi terbuang dan latensi pemrosesan memanjang '
    '(computational bottleneck) (Cremel & Arruda, 2026; Pacheco & Malensek, 2022).'
)

lb_p3 = (
    'Berbagai penelitian telah dilakukan untuk menangani akselerasi pengolahan citra digital. Chang et al. '
    '(2023) menunjukkan bahwa penerapan operator Sobel multi-arah berukuran kernel besar mampu menghasilkan '
    'deteksi tepi yang lebih stabil, namun menuntut komputasi intensif yang diatasi melalui akselerasi GPU '
    'dengan pencapaian speedup 6,7 hingga 13 kali lipat dibandingkan pustaka OpenCV-GPU standar. Dari sudut '
    'pandang arsitektur perangkat keras, Vasile et al. (2024) menegaskan bahwa pemrosesan citra beresolusi '
    'tinggi secara real-time memerlukan efisiensi penanganan aliran data yang tinggi, di mana arsitektur CPU '
    'serial konvensional memiliki keterbatasan laten dalam memenuhi ambang batas waktu respons. Pada ranah '
    'prosesor multi-core, Cremel dan Arruda (2026) mengevaluasi percepatan filter spasial citra berbasis '
    'OpenMP dan melaporkan bahwa resolusi citra dan kompleksitas algoritma sangat menentukan rasio percepatan '
    '(speedup) dan efisiensi, dengan kecenderungan efisiensi yang menurun seiring bertambahnya jumlah thread '
    'kerja serta penurunan paling tajam pada deteksi tepi Sobel (mencapai sekitar 24% pada delapan thread). '
    'Ibrahim et al. (2021) turut memperkuat temuan tersebut melalui pengujian konvolusi Gaussian blur paralel '
    'pada CPU multi-core dan GPU. Namun, implementasi komputasi paralel pada CPU menggunakan bahasa pemrograman '
    'Python memiliki tantangan arsitektur khusus berupa Global Interpreter Lock (GIL) pada rilis resmi CPython, '
    'yaitu mekanisme penguncian internal interpreter yang membatasi eksekusi bytecode Python hanya pada satu '
    'thread dalam satu waktu (Python Software Foundation, n.d.-a). Gultom dan Sarumaha (2025) membuktikan secara '
    'empiris bahwa GIL membatasi eksekusi utas serentak pada beban kerja intensif komputasi (CPU-bound), di mana '
    'multithreading hanya menghasilkan speedup marjinal sekitar 1,05 kali. Sebaliknya, paradigma multiprocessing '
    'mampu melipatgandakan kinerja dengan speedup mencapai 3,16 hingga 3,55 kali pada empat proses kerja karena '
    'setiap proses dialokasikan ruang memori (address space) dan interpreter independen (Gultom & Sarumaha, 2025; '
    'Tanenbaum & Bos, 2022).'
)

lb_p4 = (
    'Berdasarkan permasalahan tersebut, penelitian ini menerapkan komputasi paralel berbasis paradigma dekomposisi '
    'data spasial (data parallelism), yaitu strategi pemecahan struktur matriks data untuk didistribusikan ke sejumlah '
    'unit proses pekerja yang mengeksekusi instruksi filter secara bersamaan (Pacheco & Malensek, 2022), memanfaatkan '
    'modul bawaan multiprocessing pada Python (Python Software Foundation, n.d.-b) dengan metode partisi baris '
    'horizontal (horizontal row partitioning). Pendekatan dekomposisi domain ini dipilih karena operasi filter '
    'spasial citra memiliki karakteristik komputasi yang mandiri (embarrassingly parallel), di mana nilai luaran '
    'suatu piksel hanya ditentukan oleh nilai masukan piksel pada area ketetanggaannya (Cremel & Arruda, 2026). '
    'Pada rancangan penelitian ini, ketergantungan data antar-bagian hanya terjadi pada batas tepi partisi, yang '
    'ditangani secara khusus melalui mekanisme baris batas (boundary halo) yang dibaca tanpa operasi penulisan ulang, '
    'sehingga mencegah terjadinya konflik akses data (race condition). Pembagian matriks ke dalam blok horizontal '
    'mendistribusikan beban kerja ke seluruh inti fisik prosesor sekaligus mengeliminasi hambatan GIL.'
)

lb_p5 = (
    'Kajian pustaka memperlihatkan bahwa evaluasi percepatan dan efisiensi filter spasial citra pada prosesor '
    'multi-core selama ini didominasi oleh model komputasi berbasis thread seperti OpenMP (Cremel & Arruda, 2026). '
    'Karakteristik skalabilitas komputasi paralel pada Python yang berbasis proses independen, termasuk beban '
    'tambahan komunikasi antar-proses (inter-process communication overhead) serta dampaknya pada prosesor modern '
    'berarsitektur hibrida (Performance-Core dan Efficient-Core), belum banyak dipetakan secara terukur. Penelitian '
    'ini mengisi celah tersebut melalui serangkaian pengujian terkontrol terhadap tiga variasi filter bertingkat '
    '(Grayscale, Gaussian Blur 3×3, dan Sobel 3×3) pada rentang resolusi 512 × 512 hingga 4096 × 4096 piksel dengan '
    'alokasi proses kerja satu, dua, empat, dan delapan proses. Parameter kinerja yang diukur meliputi waktu eksekusi, '
    'rasio percepatan (speedup), efisiensi, beban tambahan (overhead) paralel, dan pemantauan utilisasi CPU, yang '
    'kemudian dikomparasikan terhadap batas percepatan teoretis Hukum Amdahl (Amdahl, 1967) serta diagnostik fraksi '
    'serial melalui metrik Karp–Flatt (Karp & Flatt, 1990). Hasil penelitian ini diharapkan dapat menjadi tolok '
    'ukur empiris bagi efektivitas dan batas skalabilitas komputasi paralel pada pemrosesan citra digital di sistem '
    'komputer modern.'
)

doc.paragraphs[9].text = lb_p1
doc.paragraphs[10].text = lb_p2
doc.paragraphs[11].text = lb_p3
doc.paragraphs[12].text = lb_p4
doc.paragraphs[13].text = lb_p5

# Update 6.1.2 opening sentence
doc.paragraphs[43].text = (
    'Rasio percepatan (speedup) mengukur seberapa besar komputasi paralel mempercepat penyelesaian '
    'dibandingkan eksekusi serial. Setiap nilai waktu eksekusi (T_serial dan T_paralel) diperoleh melalui '
    '30 kali repetisi pengujian terkontrol secara berselang-seling (interleaved) antara eksekusi serial dan paralel '
    'pada masing-masing tingkatan perlakuan guna mengisolasi fluktuasi derau sistem. Mengacu pada Pacheco dan '
    'Malensek (2022), speedup (S) dirumuskan pada Persamaan (2):'
)

# Update Tahap 3 & 4 in 7.1
doc.paragraphs[66].text = (
    '1. Studi literatur, yaitu pengkajian teori komputasi paralel, mekanisme pengalamatan memori larik NumPy, '
    'arsitektur konkurensi modul Python multiprocessing, batasan Global Interpreter Lock (GIL), serta formulasi '
    'matematis filter spasial citra (Grayscale, Gaussian Blur 3×3, dan Sobel 3×3).\n'
    '2. Perancangan dan pengkodean algoritma, yaitu pengembangan dua versi perangkat lunak pengujian: skrip serial '
    'sebagai baseline dan skrip paralel yang memadukan fungsi partisi matriks horizontal dengan distribusi tugas '
    'melalui multiprocessing.Pool().\n'
    '3. Penyiapan dataset citra uji, yaitu standardisasi citra acuan master fotografi beresolusi tinggi 4K '
    '(4096 × 4096 piksel) yang bersumber dari repositori fotografi terbuka Aesthetic-4K (Aesthetic-4K Dataset, 2025) '
    'berlisensi Creative Commons Attribution 4.0 International (CC-BY 4.0). Citra acuan master tersebut dipotong secara '
    'terpusat (center-crop) tanpa kompresi ke dalam empat tingkatan resolusi spasial: 512 × 512, 1024 × 1024, '
    '2048 × 2048, dan 4096 × 4096 piksel. Waktu eksekusi ketiga filter bersifat tidak bergantung pada isi citra '
    '(data-independent) karena operasi konvolusi matriks tidak memiliki percabangan kondisional berbasis nilai '
    'piksel, sehingga satu citra acuan master memadai untuk meniadakan variabilitas tekstur dan mengisolasi variabilitas '
    'sistem komputasi (penjadwalan sistem operasi, fluktuasi termal, dan alokasi inti heterogen). Seluruh 30 sampel '
    'citra multiresolusi awal tetap diarsipkan sebagai opsi dataset alternatif.\n'
    '4. Eksekusi eksperimen terkontrol, yaitu pengujian algoritma pada sistem operasi tanpa aplikasi latar belakang '
    'yang membebani CPU. Setiap kombinasi perlakuan pengujian dieksekusi sebanyak 30 kali repetisi terkontrol secara '
    'selang-seling (interleaved) antara pengukuran serial dan paralel pada masing-masing tingkatan resolusi guna '
    'memperoleh estimasi parameter statistik yang stabil dan representatif (median, rerata x̄, simpangan baku s, dan '
    'selang kepercayaan 95%). Pengukuran durasi komputasi murni memanfaatkan arsitektur pre-warmed pool untuk meniadakan '
    'penalti inisialisasi proses (cold spawn) pada Windows sesuai aturan proses bawaan CPython (Python Software Foundation, '
    'n.d.-b), serta dilengkapi jeda pendinginan termal CPU (cool-down buffer) antar-filter guna meminimalkan pelambatan '
    'termal (thermal throttling). Pergeseran waktu eksekusi antar-blok pengujian (di mana Skenario A dijalankan pertama '
    'dan memiliki baseline serial sedikit lebih lambat) dicatat sebagai batasan pengujian.\n'
    '5. Pencatatan parameter kinerja, yaitu pengukuran waktu komputasi murni dengan time.perf_counter(), pemantauan '
    'utilisasi CPU diukur pada proses utama menggunakan modul psutil sebagai estimasi tren beban kerja sistem secara '
    'keseluruhan, serta penghitungan speedup, efisiensi, dan overhead paralel.\n'
    '6. Analisis skalabilitas dan penarikan kesimpulan, yaitu penyajian data dalam kurva komparatif, evaluasi kurva '
    'percepatan terhadap batas teoretis Hukum Amdahl, serta penarikan kesimpulan tentang efektivitas komputasi paralel '
    'pada berbagai ukuran data dan kompleksitas filter.'
)

# Update Daftar Pustaka
# Remove existing bibliography paragraphs
# doc.paragraphs[85] is 'DAFTAR PUSTAKA'
# We will delete from 86 to end and add the 13 verified references
p_start = 86
while len(doc.paragraphs) > p_start:
    p = doc.paragraphs[p_start]
    p._element.getparent().remove(p._element)

bib_entries = [
    'Aesthetic-4K Dataset. (2025). Aesthetic-4K: High-resolution uncompressed image repository for visual computing research. Creative Commons CC-BY 4.0. https://huggingface.co/datasets/aesthetic-4k',
    'Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. AFIPS Conference Proceedings, 30, 483–485. https://doi.org/10.1145/1465482.1465560',
    'Chang, Q., Li, X., Li, Y., & Miyazaki, J. (2023). Multi-directional Sobel operator kernel on GPUs. arXiv preprint arXiv:2305.00515. https://doi.org/10.48550/arXiv.2305.00515',
    'Cremel, G. D., & Arruda, L. F. M. (2026). High-performance parallel acceleration of image processing filters on multicore CPUs using OpenMP. Anais do XVII Computer on the Beach, 466–473. https://periodicos.univali.br/index.php/acotb/article/view/22235',
    'Gonzalez, R. C., & Woods, R. E. (2018). Digital image processing (4th ed.). Pearson.',
    'Gultom, M. M. I., & Sarumaha, D. (2025). Empirical performance evaluation of sequential, multithreading, and multiprocessing models for CPU-bound workloads in Python. Journal of Informatics, Computer Science, Data Science and Artificial Intelligence, 3(2), 1–11.',
    'Ibrahim, N. M., ElFarag, A. A., & Kadry, R. (2021). Gaussian blur through parallel computing. In Proceedings of the International Conference on Image Processing and Vision Engineering (IMPROVE 2021) (Vol. 1, pp. 175–179). SCITEPRESS. https://doi.org/10.5220/0010513301750179',
    'Karp, A. H., & Flatt, H. P. (1990). Measuring parallel processor performance. Communications of the ACM, 33(5), 539–543. https://doi.org/10.1145/78607.78614',
    'Pacheco, P. S., & Malensek, M. (2022). An introduction to parallel programming (2nd ed.). Morgan Kaufmann.',
    'Python Software Foundation. (n.d.-a). Global interpreter lock. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/glossary.html#term-global-interpreter-lock',
    'Python Software Foundation. (n.d.-b). multiprocessing — Process-based parallelism. Python 3.14 Documentation. Diakses 20 Oktober 2026, dari https://docs.python.org/3/library/multiprocessing.html',
    'Tanenbaum, A. S., & Bos, H. (2022). Modern operating systems (5th ed.). Pearson.',
    'Vasile, C.-E., Ulmămei, A.-A., & Bîră, C. (2024). Image processing hardware acceleration—A review of operations involved and current hardware approaches. Journal of Imaging, 10(12), Article 298. https://doi.org/10.3390/jimaging10120298'
]

for b in bib_entries:
    p = doc.add_paragraph(b)
    p.style = doc.styles['Normal']

doc.save(doc_path)
doc.save(r'd:\Rakha\File Kuliah\Semester 5\Komputasi Paralel\UTS\Proposal Komputasi Paralel.docx')
print('Successfully updated Proposal docx files!')
