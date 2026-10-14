# PANDUAN PENGERJAAN MODUL: HARDWARE PROFILING & VALIDATOR (MONITOR.PY & VALIDATOR.PY)
**Penanggung Jawab:** Farrel Nathannael  
**Target Berkas:** `src/monitor.py` dan `src/validator.py`  
**Target Pengujian:** Lolos skrip `test_profiling_farrel.py`

---

## 1. Deskripsi Tugas
Tugas Anda adalah membuat **dua berkas**:
1. **`src/monitor.py`:** Modul untuk mengukur utilisasi CPU (*CPU utilization*) menggunakan pustaka `psutil` selama kalkulasi berlangsung, serta menghitung metrik kinerja paralel: *Speedup*, Efisiensi, dan *Overhead* ($T_{overhead} = T_{paralel} - \frac{T_{serial}}{P}$).
2. **`src/validator.py`:** Modul verifikasi kualitas (*Quality Assurance*) untuk memastikan secara ilmiah bahwa hasil pemrosesan paralel **identik 100% (bit-for-bit)** dengan hasil serial murni menggunakan `numpy.array_equal`.

> [!NOTE]
> Modul ini sangat penting untuk sidang/presentasi, karena dosen pasti akan bertanya: *"Bagaimana kalian membuktikan bahwa hasil paralel tidak cacat pada baris perbatasan (boundary halo)?"* dan *"Berapa persen CPU yang terpakai pada core P dan core E?"*

---

## 2. Kontrak Fungsi yang Wajib Dipatuhi

### A. Kontrak Berkas `src/validator.py`:
```python
import numpy as np

def validate_results(serial_result: np.ndarray, parallel_result: np.ndarray) -> tuple[bool, float]:
    """
    Memvalidasi apakah citra hasil paralel identik dengan hasil serial.
    
    Parameter:
        serial_result: Array citra dari pemrosesan serial baseline.
        parallel_result: Array citra dari pemrosesan multiprocessing.
    Return:
        tuple (is_identical: bool, max_diff: float)
        - is_identical: True jika numpy.array_equal bernilai True.
        - max_diff: Selisih absolut maksimum piksel (np.max(np.abs(...))).
    """
    pass
```

### B. Kontrak Berkas `src/monitor.py`:
```python
import psutil
import threading
import time

class CPUMonitor:
    """
    Pemantau utilisasi CPU di latar belakang (background thread) 
    agar tidak mengganggu atau memperlambat eksekusi komputasi utama.
    """
    def __init__(self, interval: float = 0.05):
        pass
        
    def start(self):
        """Memulai pemantauan CPU di thread terpisah."""
        pass
        
    def stop(self) -> dict:
        """
        Menghentikan pemantauan dan mengembalikan statistik utilisasi CPU.
        Return dict:
            {
                "mean_cpu_percent": float,      # Rata-rata beban CPU keseluruhan (%)
                "per_core_percent": list[float] # Rata-rata pemakaian tiap core (%)
            }
        """
        pass

def calculate_metrics(t_serial: float, t_parallel: float, p_processes: int) -> dict:
    """
    Menghitung parameter kinerja paralel mengacu pada rumus Pacheco & Malensek (2022).
    - Speedup (S) = T_serial / T_parallel
    - Efficiency (E) = (S / P) * 100%
    - Overhead (T_overhead) = T_parallel - (T_serial / P)
    
    Return dict:
        {
            "speedup": float,
            "efficiency": float,
            "overhead": float
        }
    """
    pass
```

---

## 3. PROMPT SIAP SALIN (Copy-Paste ke AI Anda: ChatGPT / Claude / Gemini)

Salin seluruh teks di dalam kotak berikut, lalu tempelkan (*paste*) langsung ke AI langganan Anda:

```text
Halo AI, saya mahasiswa Rekayasa Sistem Komputer yang sedang mengerjakan proyek penelitian Komputasi Paralel dengan Python multiprocessing.

Tugas saya adalah membuat 2 modul penunjang kualitas dan performa sistem:
1. `src/validator.py` (untuk verifikasi kebenaran data matriks piksel)
2. `src/monitor.py` (untuk pengukuran CPU utilization dengan psutil dan kalkulasi metrik paralel)

Tolong buatkan kode Python lengkap untuk kedua file tersebut dengan ketentuan berikut:

A. FILE: `src/validator.py`
- Fungsi: `validate_results(serial_result: np.ndarray, parallel_result: np.ndarray) -> tuple[bool, float]`
- Lakukan pengecekan kesamaan dimensi/shape.
- Gunakan `np.array_equal(serial_result, parallel_result)` untuk memastikan data bit-identik.
- Hitung juga selisih absolut maksimum piksel: `np.max(np.abs(serial_result.astype(np.float64) - parallel_result.astype(np.float64)))`.
- Kembalikan tuple (True/False, max_diff).

B. FILE: `src/monitor.py`
- Pustaka: `psutil`, `threading`, `time`.
- Kelas: `CPUMonitor`
  - Harus berjalan di thread latar belakang (threading.Thread, daemon=True) agar NON-BLOCKING dan tidak mengganggu waktu time.perf_counter() komputasi utama.
  - Setiap interval tertentu (default 0.05 detik), catat `psutil.cpu_percent(interval=None, percpu=True)`.
  - Metode `start()`: reset rekaman dan mulai thread pencatatan.
  - Metode `stop() -> dict`: hentikan thread dan hitung rata-rata utilisasi CPU total (`mean_cpu_percent`) serta rata-rata tiap inti fisik prosesor (`per_core_percent`).
- Fungsi: `calculate_metrics(t_serial: float, t_parallel: float, p_processes: int) -> dict`
  - Menghitung:
    * speedup = t_serial / t_parallel jika t_parallel > 0 else 0.0
    * efficiency = (speedup / p_processes) * 100.0 jika p_processes > 0 else 0.0
    * overhead = t_parallel - (t_serial / p_processes) jika p_processes > 0 else 0.0
  - Kembalikan dictionary dengan pembulatan 4 desimal.

Berikan kode lengkap yang rapi, ber-docstring jelas, siap pakai, dan mudah diimpor oleh modul lain.
```

---

## 4. Cara Pengujian Mandiri di Laptop Anda

Setelah AI Anda memberikan kode `validator.py` dan `monitor.py`:
1. Simpan masing-masing di:
   * `src/validator.py`
   * `src/monitor.py`
2. Pastikan pustaka `psutil` terpasang di laptop Anda (`pip install psutil`).
3. Buat file penguji singkat bernama `test_profiling_farrel.py` di folder utama dengan isi berikut:

```python
import numpy as np
import time
from src.validator import validate_results
from src.monitor import CPUMonitor, calculate_metrics

print("Menguji validator.py...")
a = np.ones((50, 50), dtype=np.uint8) * 128
b = np.ones((50, 50), dtype=np.uint8) * 128
is_same, diff = validate_results(a, b)
assert is_same is True and diff == 0.0, "Validator gagal pada array identik"

print("Menguji monitor.py (CPUMonitor)...")
monitor = CPUMonitor(interval=0.02)
monitor.start()
# Buat beban kerja dummy 0.3 detik
dummy = [x**2 for x in range(1000000)]
stats = monitor.stop()

print(f"Beban CPU terukur: {stats['mean_cpu_percent']}%")
assert "mean_cpu_percent" in stats, "Key mean_cpu_percent hilang"
assert "per_core_percent" in stats, "Key per_core_percent hilang"

print("Menguji calculate_metrics...")
metrik = calculate_metrics(t_serial=10.0, t_parallel=3.0, p_processes=4)
print(f"Hasil Metrik: {metrik}")
assert metrik["speedup"] > 3.0, "Perhitungan speedup salah"
assert metrik["efficiency"] > 70.0, "Perhitungan efisiensi salah"

print("\n>>> [PASSED] 100% SUKSES! Modul monitor.py & validator.py siap diunggah ke GitHub! <<<")
```

4. Jalankan: `python test_profiling_farrel.py`.
5. Jika muncul tulisan `[PASSED] 100% SUKSES!`, buka browser GitHub kelompok $\rightarrow$ masuk ke folder `src/` $\rightarrow$ klik **Add file** $\rightarrow$ **Upload files** $\rightarrow$ unggah `monitor.py` dan `validator.py`. Selesai!
