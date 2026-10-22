# Analisis Kinerja dan Skalabilitas pada Operasi Filter Citra Digital Menggunakan Komputasi Paralel Berbasis Multiprocessing

Repositori proyek tugas akhir mata kuliah **Komputasi Paralel** (Semester 5, Program Studi Rekayasa Sistem Komputer, Fakultas MIPA, Universitas Tanjungpura).

---

## 👥 Tim Peneliti / Pengembang
1. **Muhammad Zaki Rakha Bahy** (NIM: ...) — *Lead Architect & Concurrency Engine* (`src/parallel_engine.py`, `run_benchmark.py`, `web/`, `app.py`)
2. **Ahmad Dzaky** (NIM: ...) — *Filter Algorithm Specialist* (`src/filters.py`)
3. **Farrel Nathannael** (NIM: ...) — *Hardware Profiling & Quality Assurance* (`src/monitor.py`, `src/validator.py`)
4. **Guido Marco Silvio** (NIM: ...) — *Data Engineering & Visualization* (`src/image_generator.py`, `src/visualizer.py`)

---

## 📁 Struktur Direktori
```text
UTS/
├── data/
│   ├── dataset_30/                # Citra acuan master 4K (img_01.png) & dataset multiresolusi legasi
│   ├── input/                     # Citra masukan standar
│   └── output/                    # Citra hasil filter (Grayscale, Blur, Sobel)
├── panduan_tugas_anggota/         # Panduan spesifikasi & prompt AI untuk tiap anggota
│   ├── PANDUAN_AHMAD_FILTERS.md
│   ├── PANDUAN_FARREL_PROFILING.md
│   └── PANDUAN_GUIDO_VISUALISASI.md
├── results/
│   ├── benchmark_results_latest.csv # Log data empiris riil hasil pengujian
│   └── plots/                     # Gambar grafik analitis (300 DPI)
├── src/
│   ├── filters.py                 # Algoritma filter spasial murni NumPy
│   ├── image_generator.py         # Pembuat dataset citra sintetis
│   ├── monitor.py                 # Profiling CPU (psutil) & perhitungan metrik
│   ├── parallel_engine.py         # Partisi baris horizontal + boundary halo (k=1)
│   ├── validator.py               # Uji kesetaraan bit-identik (np.array_equal)
│   └── visualizer.py              # Generator kurva komparatif & Amdahl
├── web/                           # Parallel Vision Workbench Web (FastAPI + Tailwind CSS)
│   ├── backend/                   # Service layer, routing API, & bridge komputasi
│   ├── static/                    # CSS tokens, style Milkinside, JS modules, vendor assets
│   ├── templates/                 # Shell HTML5 dengan navigasi sidebar rail kiri
│   └── run_server.py              # Runner server web lokal (FastAPI + Uvicorn)
├── tools/                         # Skrip utilitas verifikasi otomatis (SSE, live, integrity)
├── requirements.txt               # Daftar pustaka dependensi
├── run_benchmark.py               # Runner utama CLI pengujian Skenario A, B, C
└── app.py                         # Web Dashboard Legasi (Streamlit - alternatif)
```

---

## 🚀 Panduan Instalasi & Eksekusi

### 1. Kloning Repositori & Pasang Dependensi
```bash
git clone https://github.com/raintyaa/komputasi-paralel-multiprocessing.git
cd komputasi-paralel-multiprocessing
pip install -r requirements.txt
```

### 2. Menjalankan Dashboard Web Interaktif (FastAPI + Tailwind CSS - Rekomendasi Utama)
Jalankan runner server web lokal:
```bash
python web/run_server.py
```
Dashboard dapat langsung diakses melalui peramban di:
- **URL Dashboard**: [http://localhost:8000](http://localhost:8000) atau [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Dokumentasi Interaktif API**: [http://localhost:8000/docs](http://localhost:8000/docs)

*Fitur Dashboard Web:*
- Desain antarmuka *Milkinside Safe Dashboard white UI* (bento card 20px, capsule pills 9999px).
- Navigasi *Sidebar Rail Kiri* 240px dengan telemetri hardware dan radar status run global.
- **2 Mode Pengujian Ilmiah**:
  1. **Mode Bertahap / Terpandu (*Guided Stepper*)**: Menjalankan pengujian runtut per skenario (Tahap 1 $\rightarrow$ Tahap 2 $\rightarrow$ Tahap 3) dengan penyimpanan akumulatif inkremental untuk mencegah *thermal throttling* dan menjamin akurasi data laporan.
  2. **Mode Otomatis Penuh (*Full Batch Run*)**: Menjalankan seluruh kombinasi skenario secara serentak dalam sekali klik.
- **Metodologi 30x Repetisi Ilmiah**: Menguji 1 citra acuan master fotografi 4K (`img_01.png` center-crop ke 512, 1024, 2048, 4096 px) sebanyak 30x putaran per perlakuan (90 uji per sub-skenario) guna memenuhi kaidah *Central Limit Theorem* (CLT) dengan agregasi $\text{Mean} \pm \text{Std}$.
- **Jeda Pendinginan Termal (*Cool-down Buffer*)**: Jeda 2 detik otomatis antar-filter untuk menjaga suhu CPU dan clock speed tetap optimal.
- Streaming benchmark Server-Sent Events (SSE) dengan pembatalan kooperatif (*graceful cancel*).
- Verifikasi 100% bit-identik ($\Delta_{\max} = 0.000000$) dan visualisasi Chart.js spline + soft gradient fill.
- **Ekspor Visualisasi Grafik Ilmiah**:
  - Tombol unduh langsung gambar Chart.js (PNG dengan latar putih solid anti-transparan) siap disisipkan ke dokumen laporan.
  - Tombol unduhan plot publikasi ilmiah beresolusi tinggi 300 DPI (Matplotlib) per skenario (/api/benchmark/plots/single/{scenario}).
  - Tombol unduh paket bundel arsip ZIP 300 DPI (/api/benchmark/plots/bundle/zip) yang mengompilasi ketiga grafik publikasi secara otomatis.

### 3. Eksekusi Pengujian CLI Mandiri (Headless Benchmark)
Jika ingin menjalankan pengujian benchmark otomatis melalui terminal tanpa antarmuka grafis:
```bash
# Menjalankan pengujian penuh 30x repetisi (standar ilmiah)
python run_benchmark.py --repetitions 30

# Menjalankan pengujian kilat (3 repetisi untuk verifikasi cepat)
python run_benchmark.py --quick
```

### 4. Menjalankan Dashboard Legasi (Streamlit - Opsi Alternatif)
Versi dashboard awal berbasis Streamlit tetap dipertahankan sebagai opsi alternatif:
```bash
streamlit run app.py
```
