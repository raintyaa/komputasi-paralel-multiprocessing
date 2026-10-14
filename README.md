# Analisis Kinerja dan Skalabilitas pada Operasi Filter Citra Digital Menggunakan Komputasi Paralel Berbasis Multiprocessing

Repositori proyek tugas akhir mata kuliah **Komputasi Paralel** (Semester 5, Program Studi Rekayasa Sistem Komputer, Fakultas MIPA, Universitas Tanjungpura).

---

## 👥 Tim Peneliti / Pengembang
1. **Muhammad Zaki Rakha Bahy** (NIM: ...) — *Lead Architect & Concurrency Engine* (`src/parallel_engine.py`, `run_benchmark.py`, `app.py`)
2. **Ahmad Dzaky** (NIM: ...) — *Filter Algorithm Specialist* (`src/filters.py`)
3. **Farrel Nathannael** (NIM: ...) — *Hardware Profiling & Quality Assurance* (`src/monitor.py`, `src/validator.py`)
4. **Guido Marco Silvio** (NIM: ...) — *Data Engineering & Visualization* (`src/image_generator.py`, `src/visualizer.py`)

---

## 📁 Struktur Direktori
```text
UTS/
├── data/
│   ├── input/                     # Citra masukan standar (512x512 s.d. 4096x4096)
│   └── output/                    # Citra hasil filter (Grayscale, Blur, Sobel)
├── panduan_tugas_anggota/         # Panduan spesifikasi & prompt AI untuk tiap anggota
│   ├── PANDUAN_AHMAD_FILTERS.md
│   ├── PANDUAN_FARREL_PROFILING.md
│   └── PANDUAN_GUIDO_VISUALISASI.md
├── results/
│   ├── raw_benchmark.csv          # Log data empiris hasil pengujian
│   └── plots/                     # Gambar grafik analitis (300 DPI)
├── src/
│   ├── filters.py                 # Algoritma filter murni NumPy
│   ├── image_generator.py         # Pembuat dataset citra sintetis
│   ├── monitor.py                 # Profiling CPU (psutil) & perhitungan metrik
│   ├── parallel_engine.py         # Partisi baris horizontal + boundary halo
│   ├── validator.py               # Uji kesetaraan bit-identik (np.array_equal)
│   └── visualizer.py              # Generator kurva komparatif & Amdahl
├── requirements.txt               # Daftar pustaka dependensi
├── run_benchmark.py               # Runner utama pengujian Skenario A, B, C
└── app.py                         # Web Dashboard Interaktif (Streamlit)
```

---

## 🚀 Panduan Instalasi & Eksekusi

### 1. Kloning Repositori & Pasang Dependensi
```bash
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

### 2. Eksekusi Pengujian Otomatis (Headless Benchmark)
```bash
python run_benchmark.py
```

### 3. Menjalankan Dashboard Presentasi (Streamlit)
```bash
streamlit run app.py
```
