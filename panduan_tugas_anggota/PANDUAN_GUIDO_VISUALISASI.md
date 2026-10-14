# PANDUAN PENGERJAAN MODUL: DATA ENGINEERING & VISUALISASI (IMAGE_GENERATOR.PY & VISUALIZER.PY)
**Penanggung Jawab:** Guido Marco Silvio  
**Target Berkas:** `src/image_generator.py` dan `src/visualizer.py`  
**Target Pengujian:** Lolos skrip `test_visualisasi_guido.py`

---

## 1. Deskripsi Tugas
Tugas Anda adalah membuat **dua berkas**:
1. **`src/image_generator.py`:** Membuat dataset citra masukan RGB sintetis berformat tanpa kompresi pada 4 variasi dimensi ($512\times512$, $1024\times1024$, $2048\times2048$, $4096\times4096$). Citra ini dirancang deterministik (berisi gradien warna, lingkaran, dan pola geometris bertekstur) agar realistis saat difilter oleh Sobel dan Gaussian Blur.
2. **`src/visualizer.py`:** Membuat grafik analisis kinerja ilmiah berkualitas tinggi (300 DPI) menggunakan pustaka **Matplotlib** berdasarkan data hasil benchmark (`raw_benchmark.csv`), mencakup kurva perbandingan terhadap **Batas Teoretis Hukum Amdahl**.

---

## 2. Kontrak Fungsi yang Wajib Dipatuhi

### A. Kontrak Berkas `src/image_generator.py`:
```python
import numpy as np

def generate_synthetic_image(width: int, height: int) -> np.ndarray:
    """
    Membuat citra sintetis RGB beresolusi (height, width, 3) bertipe uint8
    dengan pola deterministik (gradien warna, lingkaran, kotak bertekstur tepi).
    """
    pass

def generate_all_test_images(output_dir: str = "data/input") -> dict[int, str]:
    """
    Membuat dan menyimpan 4 citra uji standar:
    - input_512.png  (512 x 512)
    - input_1024.png (1024 x 1024)
    - input_2048.png (2048 x 2048)
    - input_4096.png (4096 x 4096)
    
    Return:
        dict {512: "path/to/512.png", 1024: ..., 2048: ..., 4096: ...}
    """
    pass
```

### B. Kontrak Berkas `src/visualizer.py`:
```python
import matplotlib.pyplot as plt

def plot_scenario_a(csv_path: str, output_path: str = "results/plots/skenario_a_resolusi.png"):
    """
    Membuat grafik Skenario A: Pengaruh Resolusi Citra vs Speedup (P = 4 proses).
    Menampilkan kurva 3 filter (Grayscale, Gaussian Blur, Sobel).
    """
    pass

def plot_scenario_b(csv_path: str, f_fraction: float = 0.90, output_path: str = "results/plots/skenario_b_amdahl.png"):
    """
    Membuat grafik Skenario B: Skalabilitas Proses (P = 1, 2, 4, 8) pada citra 2048x2048.
    Wajib memuat:
    1. Kurva speedup empiris 3 filter (Grayscale, Gaussian, Sobel).
    2. Kurva Batas Teoretis Hukum Amdahl: S_Amdahl = 1 / ((1 - f) + (f / P)).
    3. Garis referensi percepatan ideal linear (S = P).
    """
    pass

def plot_scenario_c(csv_path: str, output_path: str = "results/plots/skenario_c_kompleksitas.png"):
    """
    Membuat grafik Skenario C: Perbandingan Tingkat Kompleksitas Filter 
    terhadap Overhead Paralel dan Utilisasi CPU.
    """
    pass
```

---

## 3. PROMPT SIAP SALIN (Copy-Paste ke AI Anda: ChatGPT / Claude / Gemini)

Salin seluruh teks di dalam kotak berikut, lalu tempelkan (*paste*) langsung ke AI langganan Anda:

```text
Halo AI, saya mahasiswa Rekayasa Sistem Komputer yang sedang mengerjakan proyek penelitian Komputasi Paralel dengan Python multiprocessing.

Tugas saya adalah membuat 2 modul penunjang data dan visualisasi:
1. `src/image_generator.py` (pembuat dataset citra masukan RGB sintetis standar)
2. `src/visualizer.py` (pembuat grafik publikasi ilmiah dengan Matplotlib dari file CSV)

Tolong buatkan kode Python lengkap untuk kedua file tersebut dengan ketentuan ketat berikut:

A. FILE: `src/image_generator.py`
- Pustaka: `numpy`, `os`, `cv2` (cv2 hanya untuk imwrite menyimpan berkas PNG tanpa kompresi).
- Fungsi: `generate_synthetic_image(width: int, height: int) -> np.ndarray`
  - Buat array RGB (height, width, 3) dtype uint8.
  - Berikan pola kaya tekstur secara matematis: gradien warna horizontal & vertikal, beberapa lingkaran konsentris di tengah, dan kisi-kisi kotak (grid). Pola ini penting agar filter Gaussian Blur dan Sobel memiliki tepi nyata untuk dihitung.
- Fungsi: `generate_all_test_images(output_dir: str = "data/input") -> dict[int, str]`
  - Buat direktori output jika belum ada.
  - Hasilkan 4 file: `input_512.png`, `input_1024.png`, `input_2048.png`, dan `input_4096.png`.
  - Kembalikan dictionary resolusi -> path berkas.

B. FILE: `src/visualizer.py`
- Pustaka: `matplotlib.pyplot`, `pandas` (atau csv bawaan), `numpy`.
- Gunakan style plot yang rapi dan profesional untuk jurnal ilmiah (grid halus, DPI=300, label sumbu jelas, font proporsional, legenda rapi).
- Fungsi 1: `plot_scenario_a(csv_path: str, output_path: str = "results/plots/skenario_a_resolusi.png")`
  - Filter data CSV untuk Skenario A (alokasi proses P=4).
  - Sumbu X: Resolusi matriks citra (512, 1024, 2048, 4096).
  - Sumbu Y: Speedup (S).
  - Tampilkan garis komparasi 3 filter (Grayscale, Gaussian Blur, Sobel) dengan marker yang berbeda.
- Fungsi 2: `plot_scenario_b(csv_path: str, f_fraction: float = 0.90, output_path: str = "results/plots/skenario_b_amdahl.png")`
  - Filter data CSV untuk Skenario B (resolusi 2048x2048 pada proses P = 1, 2, 4, 8).
  - Plot kurva Speedup empiris masing-masing filter.
  - Plot garis batas teoretis Hukum Amdahl dengan rumus: S_Amdahl = 1.0 / ((1.0 - f_fraction) + (f_fraction / P)).
  - Plot garis linear ideal (Speedup = P).
- Fungsi 3: `plot_scenario_c(csv_path: str, output_path: str = "results/plots/skenario_c_kompleksitas.png")`
  - Buat diagram batang ganda (grouped bar chart) yang membandingkan 3 filter (Grayscale = Ringan, Gaussian = Moderat, Sobel = Berat) terhadap durasi Overhead (detik) dan Utilisasi CPU (%).

Berikan kode Python yang rapi, ber-docstring lengkap, robust terhadap file path, dan siap dieksekusi.
```

---

## 4. Cara Pengujian Mandiri di Laptop Anda

Setelah AI Anda memberikan kode `image_generator.py` dan `visualizer.py`:
1. Simpan masing-masing di:
   * `src/image_generator.py`
   * `src/visualizer.py`
2. Pastikan pustaka terpasang (`pip install matplotlib numpy opencv-python`).
3. Buat file penguji singkat bernama `test_visualisasi_guido.py` di folder utama dengan isi berikut:

```python
import os
import csv
from src.image_generator import generate_synthetic_image, generate_all_test_images
from src.visualizer import plot_scenario_a, plot_scenario_b, plot_scenario_c

print("Menguji image_generator.py...")
img = generate_synthetic_image(100, 100)
assert img.shape == (100, 100, 3), "Dimensi citra salah"
print("Ukuran citra uji 100x100 berhasil dibuat.")

print("Membuat file CSV dummy untuk menguji visualizer...")
os.makedirs("results/plots", exist_ok=True)
dummy_csv = "results/dummy_test.csv"
with open(dummy_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["scenario", "resolution", "filter", "processes", "t_serial", "t_parallel", "speedup", "efficiency", "overhead", "cpu_percent"])
    # Dummy Skenario A
    for res, sp in [(512, 1.5), (1024, 2.3), (2048, 3.2), (4096, 3.6)]:
        writer.writerow(["A", res, "Sobel", 4, 1.0, 1.0/sp, sp, (sp/4)*100, 0.05, 85.0])
        writer.writerow(["A", res, "Gaussian Blur", 4, 0.5, 0.5/(sp*0.9), sp*0.9, (sp*0.9/4)*100, 0.04, 75.0])
        writer.writerow(["A", res, "Grayscale", 4, 0.1, 0.1/(sp*0.6), sp*0.6, (sp*0.6/4)*100, 0.03, 60.0])
    # Dummy Skenario B
    for p, sp in [(1, 1.0), (2, 1.9), (4, 3.4), (8, 5.1)]:
        writer.writerow(["B", 2048, "Sobel", p, 1.0, 1.0/sp, sp, (sp/p)*100, 0.05, 80.0])
        writer.writerow(["B", 2048, "Gaussian Blur", p, 0.5, 0.5/(sp*0.9), sp*0.9, (sp*0.9/p)*100, 0.04, 70.0])
        writer.writerow(["B", 2048, "Grayscale", p, 0.1, 0.1/(sp*0.6), sp*0.6, (sp*0.6/p)*100, 0.03, 50.0])

print("Menguji fungsi plot Skenario A, B, C...")
plot_scenario_a(dummy_csv, "results/plots/test_plot_a.png")
plot_scenario_b(dummy_csv, 0.90, "results/plots/test_plot_b.png")
plot_scenario_c(dummy_csv, "results/plots/test_plot_c.png")

assert os.path.exists("results/plots/test_plot_a.png"), "Plot A gagal dibuat"
assert os.path.exists("results/plots/test_plot_b.png"), "Plot B gagal dibuat"
assert os.path.exists("results/plots/test_plot_c.png"), "Plot C gagal dibuat"

print("\n>>> [PASSED] 100% SUKSES! Modul image_generator.py & visualizer.py siap diunggah ke GitHub! <<<")
```

4. Jalankan: `python test_visualisasi_guido.py`.
5. Jika muncul tulisan `[PASSED] 100% SUKSES!`, buka browser GitHub kelompok $\rightarrow$ masuk ke folder `src/` $\rightarrow$ klik **Add file** $\rightarrow$ **Upload files** $\rightarrow$ unggah `image_generator.py` dan `visualizer.py`. Selesai!
