# KERANGKA LAPORAN AKHIR PRAKTIKUM KOMPUTASI PARALEL
**STANDAR BUKU PANDUAN TUGAS AKHIR PRODI REKAYASA SISTEM KOMPUTER FMIPA UNTAN 2022**

---

## BAGIAN AWAL (FRONT MATTER)
- **HALAMAN SAMPUL (COVER)**
- **HALAMAN JUDUL (COVER DALAM)**
- **HALAMAN PERNYATAAN KEASLIAN**
- **HALAMAN PENGESAHAN**
- **HALAMAN PERSEMBAHAN**
- **KATA PENGANTAR**
- **ABSTRAK (BAHASA INDONESIA)**
- **ABSTRACT (BAHASA INGGRIS)**
- **DAFTAR ISI**
- **DAFTAR GAMBAR**
- **DAFTAR TABEL**
- **DAFTAR KODE PROGRAM**
- **DAFTAR SIMBOL DAN SINGKATAN**
- **DAFTAR LAMPIRAN**

---

## BAB 1 PENDAHULUAN
- **1.1 Latar Belakang**
- **1.2 Rumusan Masalah**
- **1.3 Batasan Masalah**
- **1.4 Tujuan Penelitian**
- **1.5 Manfaat Penelitian**
- **1.6 Sistematika Penulisan**

---

## BAB 2 LANDASAN TEORI
- **2.1 Perbandingan Terhadap Penelitian Terdahulu**
- **2.2 Pengolahan Citra Digital dan Operasi Filter Spasial**
  - **2.2.1 Representasi Citra Digital dan Operasi Konvolusi 2D**
  - **2.2.2 Karakteristik Algoritma Filter Spasial yang Diuji**
- **2.3 Komputasi Paralel dan Multiprocessing Python**
  - **2.3.1 Paradigma Data Parallelism dan Dekomposisi Domain Spasial**
  - **2.3.2 Mekanisme GIL, Multiprocessing Python, dan Overhead Serialisasi IPC**
  - **2.3.3 Arsitektur Prosesor Multi-Core, Arsitektur Hibrida, dan Hierarki Cache**
- **2.4 Metrik Evaluasi Kinerja dan Model Skalabilitas**
  - **2.4.1 Metrik Kinerja Dasar: Waktu Eksekusi, Speedup, Efisiensi, dan Overhead Paralel**
  - **2.4.2 Batas Skalabilitas Teoretis: Hukum Amdahl dan Metrik Karp–Flatt**
  - **2.4.3 Analisis Statistik Pengukuran dan Evaluasi Batas Derau Sistem (Kontrol A/A)**

---

## BAB 3 METODOLOGI PENELITIAN
- **3.1 Tahapan Penelitian**
- **3.2 Pengumpulan dan Standardisasi Data Citra Master**
- **3.3 Alat dan Bahan Penelitian**
  - **3.3.1 Perangkat Keras dan Kondisi Operasional**
  - **3.3.2 Perangkat Lunak dan Pustaka Komputasi**
  - **3.3.3 Alat Ukur dan Instrumentasi Kinerja**
- **3.4 Desain Eksperimen**
- **3.5 Prosedur Pengukuran dan Pengujian**
  - **3.5.1 Protokol Pemanasan Awal (Pre-Warming Worker Pool)**
  - **3.5.2 Protokol Jeda Dingin (Cool-Down Buffer) dan Isolasi Noise Sistem**
  - **3.5.3 Pengujian Berselang-seling (Interleaved Execution 30 Repetisi) dan Kontrol A/A**
- **3.6 Teknik Analisis Data**

---

## BAB 4 PERANCANGAN SISTEM
- **4.1 Deskripsi Sistem Pemrosesan Citra Paralel**
- **4.2 Perancangan Algoritma Filter Spasial**
- **4.3 Perancangan Arsitektur Paralel**
  - **4.3.1 Pembagian Blok Baris Horizontal**
  - **4.3.2 Penanganan Baris Batas (Boundary Halo)**
  - **4.3.3 Distribusi Tugas dan Sinkronisasi Proses**
  - **4.3.4 Rekonstruksi Citra Utuh**
- **4.4 Perancangan Pengukuran dan Pencatatan Telemetri**
- **4.5 Perancangan Verifikasi Integritas Citra Bit-Identik**

---

## BAB 5 IMPLEMENTASI, PENGUJIAN DAN PEMBAHASAN
- **5.1 Implementasi Sistem Pemrosesan Citra Paralel**
- **5.2 Validasi Integritas Data dan Keterulangan Pengujian**
  - **5.2.1 Evaluasi Integritas Luaran Citra Bit-Identik**
  - **5.2.2 Evaluasi Kontrol Dasar A/A (P = 1) dan Batas Derau Sistem**
  - **5.2.3 Evaluasi Keterulangan Antar-Blok Pengujian (Repeatability Drift)**
- **5.3 Hasil Pengujian Sistem dan Analisis Kinerja**
  - **5.3.1 Skenario A: Pengaruh Skalabilitas Resolusi Matriks Citra**
  - **5.3.2 Skenario B: Pengaruh Skalabilitas Alokasi Proses Kerja (Worker)**
  - **5.3.3 Skenario C: Pengaruh Variasi Kompleksitas Algoritma Filter**
- **5.4 Pencocokan Model Teoretis Skalabilitas**
  - **5.4.1 Estimasi Parameter Fraksi Paralel Hukum Amdahl**
  - **5.4.2 Diagnostik Beban Koordinasi Berdasarkan Metrik Karp–Flatt**
- **5.5 Pembahasan Temuan dan Keterbatasan Penelitian**
  - **5.5.1 Dinamika Resolusi Citra dan Hipotesis Efek L3 Cache pada Sobel 512**
  - **5.5.2 Karakteristik Skalabilitas Worker, Arsitektur Hibrida, dan Diminishing Returns**
  - **5.5.3 Karakteristik Beban Tambahan (Overhead) Serialisasi IPC dan Utilisasi CPU**
  - **5.5.4 Komparasi Temuan terhadap Penelitian Terdahulu**
  - **5.5.5 Sintesis Jawaban Rumusan Masalah dan Keterbatasan Penelitian**

---

## BAB 6 PENUTUP
- **6.1 Kesimpulan**
- **6.2 Saran**

---

## BAGIAN AKHIR (BACK MATTER)
- **DAFTAR PUSTAKA**
- **LAMPIRAN**
  - **Lampiran A: Data Mentah Hasil Pengujian Benchmark (810 Iterasi × 15 Kolom)**
  - **Lampiran B: Tabel Ringkasan Metrik Kinerja Lengkap (49 Kolom × 27 Kondisi)**
  - **Lampiran C: Kode Program Implementasi Engine Pemrosesan Citra Paralel**
  - **Lampiran D: Kode Program Skrip Pengujian Otomatis dan Visualisasi Data**
  - **Lampiran E: Log Spesifikasi Lingkungan Perangkat Keras dan Perangkat Lunak**
