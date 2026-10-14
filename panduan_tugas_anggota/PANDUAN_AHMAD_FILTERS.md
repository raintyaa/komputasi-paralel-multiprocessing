# PANDUAN PENGERJAAN MODUL: ALGORITMA FILTER CITRA (FILTERS.PY)
**Penanggung Jawab:** Ahmad Dzaky  
**Target Berkas:** `src/filters.py`  
**Target Pengujian:** Lolos skrip `test_filters_ahmad.py`

---

## 1. Deskripsi Tugas
Tugas Anda adalah membuat berkas `src/filters.py` yang berisi implementasi **3 fungsi filter citra digital** menggunakan komputasi matriks murni pustaka **NumPy**:
1. **Konversi Grayscale:** Operasi titik matematis ($1 \times 1$) per piksel.
2. **Gaussian Blur (3 × 3):** Operasi konvolusi matriks ketetanggaan kernel penghalusan.
3. **Deteksi Tepi Sobel:** Operasi konvolusi gradien turunan ganda ($G_x$ dan $G_y$) dan magnitudo tepi.

> [!CAUTION]
> **ATURAN KERAS (BATASAN ILMIAH):**
> * **DILARANG KERAS** menggunakan fungsi instan seperti `cv2.cvtColor()`, `cv2.GaussianBlur()`, `cv2.Sobel()`, atau fungsi dari pustaka `scipy.ndimage`!
> * Mengapa? Karena penelitian kita menguji efisiensi komputasi CPU paralel murni di Python. Jika memakai pustaka OpenCV/SciPy, fungsi tersebut secara otomatis menjalankan C++ multithreading di belakang layar yang akan merusak keabsahan data penelitian kita.
> * **WAJIB** menggunakan operasi matriks murni **NumPy** (`np.ndarray`).

---

## 2. Kontrak Fungsi yang Wajib Dipatuhi

Berkas `src/filters.py` Anda wajib memiliki 3 fungsi dengan nama, parameter, dan keluaran persis seperti berikut:

```python
import numpy as np

def apply_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Mengonversi citra RGB ke Grayscale menggunakan bobot luminansi standar.
    Rumus: Gray = 0.299*R + 0.587*G + 0.114*B
    
    Parameter:
        image: np.ndarray berdimensi (H, W, 3) bertipe uint8.
    Return:
        np.ndarray berdimensi (H, W) bertipe uint8.
    """
    pass

def apply_gaussian_blur(image: np.ndarray) -> np.ndarray:
    """
    Menerapkan filter Gaussian Blur berukuran kernel 3x3 (radius k=1).
    Kernel Gaussian 3x3 ternormalisasi:
        [[1, 2, 1],
         [2, 4, 2],
         [1, 2, 1]] / 16.0
    
    Parameter:
        image: np.ndarray berdimensi (H, W, 3) atau (H, W) bertipe uint8.
    Return:
        np.ndarray berdimensi sama dengan input bertipe uint8.
    """
    pass

def apply_sobel(image: np.ndarray) -> np.ndarray:
    """
    Menerapkan filter deteksi tepi Sobel 3x3 dengan gradien turunan parsial ganda.
    Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    Gy = [[-1, -2, -1], [ 0,  0,  0], [ 1,  2,  1]]
    Magnitudo: G = sqrt(Gx^2 + Gy^2) di-clip ke rentang [0, 255].
    
    Parameter:
        image: np.ndarray berdimensi (H, W, 3) atau (H, W) bertipe uint8.
    Return:
        np.ndarray citra tepi 2D berdimensi (H, W) bertipe uint8.
    """
    pass
```

---

## 3. PROMPT SIAP SALIN (Copy-Paste ke AI Anda: ChatGPT / Claude / Gemini)

Salin seluruh teks di dalam kotak berikut, lalu tempelkan (*paste*) langsung ke AI langganan Anda:

```text
Halo AI, saya adalah mahasiswa Rekayasa Sistem Komputer yang sedang mengerjakan proyek mata kuliah Komputasi Paralel tentang pemrosesan citra digital dengan multiprocessing di Python.

Tugas saya adalah membuat modul `filters.py` yang berisi implementasi matematis murni menggunakan pustaka NumPy. 

Tolong buatkan kode lengkap untuk file `src/filters.py` yang memenuhi spesifikasi ketat berikut:

1. BATASAN MUTLAK:
   - HANYA boleh menggunakan pustaka `numpy` (import numpy as np).
   - DILARANG menggunakan OpenCV (cv2) atau scipy untuk melakukan filtering/konvolusi!
   - Semua kalkulasi konvolusi dan perkalian matriks harus murni berbasis NumPy array.

2. TIGA FUNGSI YANG WAJIB DIIMPLEMENTASIKAN:
   a. `apply_grayscale(image: np.ndarray) -> np.ndarray`
      - Input: Array RGB berukuran (H, W, 3), dtype uint8.
      - Rumus luminansi standar ITU-R BT.601: 0.299 * R + 0.587 * G + 0.114 * B.
      - Output: Array 2D berukuran (H, W), dtype uint8.

   b. `apply_gaussian_blur(image: np.ndarray) -> np.ndarray`
      - Input: Array citra (H, W, 3) atau (H, W), dtype uint8.
      - Kernel Gaussian 3x3 (k=1) bernilai:
        [[1, 2, 1],
         [2, 4, 2],
         [1, 2, 1]] / 16.0
      - Operasikan konvolusi 2D pada setiap kanal warna secara efisien (gunakan slicing/vectorization NumPy yang cepat atau nested loop teroptimasi).
      - Tangani padding batas tepi dengan 'edge' replication (mengulang piksel terluar) agar ukuran output tetap sama dengan input (H, W).
      - Pastikan hasil akhir di-clip pada rentang 0-255 dan dikonversi kembali ke dtype uint8.

   c. `apply_sobel(image: np.ndarray) -> np.ndarray`
      - Input: Array citra (H, W, 3) atau (H, W), dtype uint8.
      - Jika input memiliki 3 kanal (RGB), konversikan dulu ke grayscale secara internal.
      - Gunakan kernel Sobel horizontal dan vertikal:
        Gx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
        Gy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)
      - Lakukan konvolusi spasial untuk memperoleh gradien Gx dan Gy.
      - Hitung magnitudo tepi: G = np.sqrt(Gx**2 + Gy**2).
      - Clip nilai ke rentang [0, 255] dan konversi ke dtype uint8.
      - Output: Array 2D berukuran (H, W), dtype uint8.

Tolong berikan kode Python yang rapi, cepat, berdokumen docstring lengkap, dan bebas error!
```

---

## 4. Cara Pengujian Mandiri di Laptop Anda

Setelah AI Anda memberikan kode `filters.py`:
1. Simpan kodenya di dalam folder proyek: `src/filters.py`.
2. Buat file penguji singkat bernama `test_filters_ahmad.py` di folder utama dengan isi berikut:

```python
import numpy as np
from src.filters import apply_grayscale, apply_gaussian_blur, apply_sobel

# Buat citra dummy RGB 100x100
dummy_img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

print("Menguji apply_grayscale...")
gray = apply_grayscale(dummy_img)
assert gray.shape == (100, 100), f"Dimensi salah: {gray.shape}"
assert gray.dtype == np.uint8, "Dtype bukan uint8"

print("Menguji apply_gaussian_blur...")
blur = apply_gaussian_blur(dummy_img)
assert blur.shape == (100, 100, 3), f"Dimensi salah: {blur.shape}"
assert blur.dtype == np.uint8, "Dtype bukan uint8"

print("Menguji apply_sobel...")
sobel = apply_sobel(dummy_img)
assert sobel.shape == (100, 100), f"Dimensi salah: {sobel.shape}"
assert sobel.dtype == np.uint8, "Dtype bukan uint8"

print("\n>>> [PASSED] 100% SUKSES! Modul filters.py siap diunggah ke GitHub! <<<")
```

3. Jalankan: `python test_filters_ahmad.py`.
4. Jika muncul tulisan `[PASSED] 100% SUKSES!`, buka browser GitHub kelompok $\rightarrow$ masuk ke folder `src/` $\rightarrow$ klik **Add file** $\rightarrow$ **Upload files** $\rightarrow$ upload file `filters.py`. Selesai!
