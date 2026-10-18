# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Mahasiswa & Peneliti Komputasi Paralel**: Mengeksekusi pengujian empiris, memvalidasi integritas numerik bit-identik (=1$ halo seam), dan mengevaluasi metrik skalabilitas (*Speedup*, *Efficiency*, *Overhead*).
- **Dosen Penguji & Asisten Laboratorium**: Memeriksa validitas metodologi saintifik, memverifikasi tidak adanya fabrikasi data, dan menguji pemahaman arsitektur prosesor heterogen.

## Product Purpose

Platform evaluasi dan demonstrasi interaktif komputasi paralel pengolahan citra digital berbasis dekomposisi domain baris horizontal (*horizontal row domain decomposition*) dan pertukaran batas halo (*boundary halo mechanism*, =1$). Platform ini membuktikan bahwa paralelisasi algoritma spasial dapat mempercepat waktu pemrosesan secara nyata pada citra beresolusi tinggi tanpa menghasilkan artefak garis batas (*seam artifacts*).

## Positioning

Berbeda dengan simulator komputasi teoretis abstrak, **Parallel Vision Workbench** adalah konsol laboratorium empiris riil yang mengeksekusi komputasi paralel langsung pada CPU laptop pengujian (Intel Core i5-13420H), mencatat waktu eksekusi presisi tinggi (perf_counter), memverifikasi keidentikan bit dengan eksekusi serial secara absolut ($\Delta_{\\max} = 0.000000$), dan menyediakan visualisasi matriks selisih piksel serta kurva Hukum Amdahl reaktif.

## Operating Context

- **Perangkat Keras Uji**: Laptop Acer Aspire 5 dengan prosesor Intel Core i5-13420H (generasi ke-13 Raptor Lake) yang memiliki 4 Performance Cores (P-Cores, clock hingga 4.6 GHz, 8 logical threads) dan 4 Efficient Cores (E-Cores, clock hingga 3.4 GHz, 4 logical threads), total 12 logical threads, RAM 16 GB DDR4.
- **Sistem Operasi**: Windows 11 Home 64-bit (arsitektur proses multiprocessing menggunakan metode spawn).
- **Tumpukan Teknologi**: Python 3.14, NumPy, OpenCV, Streamlit, Matplotlib, psutil.
- **Konteks Evaluasi**: Tugas Ujian Tengah Semester (UTS) mata kuliah Komputasi Paralel, Program Studi Rekayasa Sistem Komputer, Jurusan Sistem Komputer, Fakultas Matematika dan Ilmu Pengetahuan Alam, Universitas Tanjungpura (FMIPA UNTAN).

## Capabilities and Constraints

- **Preservasi Logika Komputasi**: Algoritma konvolusi paralel, serial, dan rekonstruksi halo di src/parallel_engine.py dan src/serial_engine.py harus tetap deterministik dan bit-identik 100%.
- **Kejujuran Data Ilmiah**: Dilarang menggunakan metrik palsu (seperti cpu_utilization = 0.0). Seluruh data yang diekspor ke CSV harus berasal dari pengukuran empiris riil (CPUMonitor).
- **Efisiensi Memori (Zero OOM)**: Pemuatan dataset citra multiresolusi (512px hingga 4096px) harus dikelola secara berurutan (*streaming per resolution*) agar tidak membebani RAM 16 GB secara serentak.
- **Lifecycle Matplotlib**: Setiap objek figur plot harus ditutup secara eksplisit setelah dirender untuk mencegah kebocoran memori pada browser.

## Brand Commitments

- **Identitas**: *Parallel Vision Workbench — Laboratorium Komputasi Paralel FMIPA UNTAN*.
- **Monogram**: PV dengan aksen kilat petir (*Parallel Velocity*).
- **Palet Warna**: *Modern Executive White Dashboard* berlatar Slate-100 (#F1F5F9), permukaan kartu putih bersih (#FFFFFF), aksen primer *Royal Blue* (#1D4ED8), dan status verifikasi *Emerald Green* (#059669).
- **Bahasa**: Bahasa Indonesia baku akademik formal untuk seluruh label, metrik, dan keterangan ilmiah.

## Evidence on Hand

- Dataset citra fotografi nyata: 120 berkas PNG (data/dataset_30/ pada resolusi 512, 1024, 2048, dan 4096 px).
- Berkas riwayat pengujian empiris: 
esults/benchmark_results.csv (810 runs mentah) dan 
esults/benchmark_results_summary.csv (27 kombinasi perlakuan proposal).
- Grafik saintifik publikasi 300 DPI: 
esults/plots/skenario_a_resolusi.png, 
esults/plots/skenario_b_amdahl.png, dan 
esults/plots/skenario_c_kompleksitas.png.

## Product Principles

1. **Integritas Kebenaran Data (Empirical Truth First)**: Setiap angka, waktu, dan metrik utilisasi yang ditampilkan atau diekspor ke CSV adalah hasil pengukuran riil, bukan estimasi atau fabrikasi.
2. **Keterverifikasian Bit-Identik (Zero Visual Artifacts)**: Hasil komputasi paralel wajib dibuktikan secara matematis sama persis dengan komputasi serial ($\Delta_{\\max} = 0.000000$).
3. **Kejelasan Hierarki Kognitif (Clarity & Readability)**: Tampilan dasbor memisahkan zona kontrol input, telemetri sistem, dan viewport visual secara proporsional dengan kontras tinggi (WCAG AA/AAA).

## Accessibility & Inclusion

- Memenuhi standar WCAG AA (rasio kontras teks body $\\ge 4.5:1$, navigasi tab $\\ge 6:1$, tombol $\\ge 5:1$).
- Setiap gambar hasil komputasi wajib menyertakan deskripsi teks alternatif (*accessible caption*) yang dapat diakses oleh pembaca layar (*screen reader*).
- Kontrol form dapat dioperasikan penuh menggunakan navigasi keyboard dengan cincin fokus (*focus visible ring*) yang jelas.
