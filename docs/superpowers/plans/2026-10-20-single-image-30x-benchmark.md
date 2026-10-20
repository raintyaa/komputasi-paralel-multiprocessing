# Single Reference Image Center-Crop & 30x Iteration Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengganti pengujian 30 berkas citra multiresolusi yang berbeda menjadi sistem pengujian berbasis 1 citra master acuan (`img_01.png` 4096px) dengan metode *center-crop* ke 4 resolusi target (512, 1024, 2048, 4096 px) dan dieksekusi sebanyak 30 kali iterasi pengulangan (*repetitions*) per kombinasi skenario dan filter untuk memenuhi kaidah statistik ilmiah (*Central Limit Theorem*).

**Architecture:** Modul `src/image_generator.py` menghasilkan citra acuan *center-crop* deterministik; `run_benchmark.py` dan `web/backend/services/bridge.py` mengorkestrasi perulangan 30 iterasi per skenario/filter dengan pre-warmed pool proses; antarmuka web menerima event SSE dengan informasi nomor iterasi dan menyajikan agregasi statistik (Mean $\pm$ Std, Speedup, Efisiensi).

**Tech Stack:** Python 3.14, NumPy, OpenCV, FastAPI, Uvicorn, SSE (Server-Sent Events), Chart.js, Pandas.

**Spec:** Rekomendasi dosen penguji Komputasi Paralel FMIPA UNTAN dan konsensus arsitektur sistem UTS.

## Global Constraints

- **Citra Master Acuan**: `data/dataset_30/4096/img_01.png` sebagai sumber piksel utama (4096 $\times$ 4096 RGB uint8).
- **Metode Pemotongan Resolusi**: *Center-Crop* murni tanpa interpolasi resampling (`[(4096-R)//2 : (4096+R)//2, (4096-R)//2 : (4096+R)//2]`), tersimpan di `data/input/reference_{R}.png`.
- **Integritas Numerik**: Validasi bit-identik serial vs paralel harus tetap $\Delta_{\max} = 0.000000$ dan `is_identical = True` pada seluruh 30 iterasi.
- **Jumlah Iterasi**: Default `repetitions = 30` untuk Full Benchmark, dan `repetitions = 3` untuk Quick Mode demo.
- **Skema Data**: Menambahkan kolom `iteration` (1 s.d. 30) pada hasil raw CSV, dan menghitung `mean` serta `std` pada summary CSV/JSON.

## Review Focus

1. **Center-crop dimension drift**: Pemotongan pada resolusi ganjil atau pembulatan yang salah bisa menyebabkan dimensi citra bergeser $\pm 1$ piksel. Harus dipastikan dimensi tepat `(R, R, 3)`.
2. **Cold cache vs warm cache run 1**: Iterasi 1 biasanya memiliki overhead inisialisasi modul atau memory paging. Agregasi statistik harus mencatat semua iterasi secara transparan.
3. **Memory leak over 30 iterations**: Pengulangan 30x pada citra 4096px berpotensi menimbun array di memori jika referensi tidak dilepas. Modul harus memastikan array hasil setiap iterasi segera direduksi atau di-overwrite.
4. **SSE timeout / buffer stall**: Streaming 30 iterasi berturut-turut pada 4096px memakan waktu ~10-15 detik per filter. Event SSE harus memancarkan heartbeat progress per iterasi agar koneksi browser tidak terputus.
5. **Format JSON non-compliant**: Nilai `np.float64` atau `np.nan` dari kalkulasi pandas std pada 1 sampel dapat merusak serialisasi JSON di FastAPI. Wajib dikonversi via helper `_to_native()`.

---

### Task 1: Module Center-Crop Generator (`src/image_generator.py`)

**Files:**
- Modify: `src/image_generator.py`
- Test: `tests/test_center_crop.py`

**Interfaces:**
- Consumes: `cv2.imread`, `data/dataset_30/4096/img_01.png`
- Produces: `prepare_reference_multires_images(master_path: str, output_dir: str) -> Dict[int, str]`

- [ ] **Step 1: Write the failing test**

Buat file `tests/test_center_crop.py`:
```python
import os
import cv2
import numpy as np
import pytest
from src.image_generator import prepare_reference_multires_images

def test_prepare_reference_multires_images():
    master_path = "data/dataset_30/4096/img_01.png"
    if not os.path.exists(master_path):
        pytest.skip("Master dataset img_01.png tidak tersedia")
    res_dict = prepare_reference_multires_images(master_path=master_path, output_dir="data/input")
    for res in [512, 1024, 2048, 4096]:
        assert res in res_dict
        p = res_dict[res]
        assert os.path.exists(p)
        img = cv2.imread(p)
        assert img is not None
        assert img.shape == (res, res, 3)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_center_crop.py`  
Expected: FAIL with `ImportError: cannot import name 'prepare_reference_multires_images'`

- [ ] **Step 3: Implement `prepare_reference_multires_images` in `src/image_generator.py`**

Tambahkan fungsi pemotongan *center-crop* ke `src/image_generator.py`:
```python
def prepare_reference_multires_images(
    master_path: str = "data/dataset_30/4096/img_01.png",
    output_dir: str = "data/input"
) -> Dict[int, str]:
    """
    Menyiapkan citra acuan tunggal multiresolusi (512, 1024, 2048, 4096)
    dengan teknik center-crop murni dari citra master 4096px.
    """
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/test_center_crop.py`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/image_generator.py tests/test_center_crop.py
git commit -m "feat(dataset): implement center-crop generator from 4096px master image"
```

---

### Task 2: Core Orchestrator Iteration Engine (`run_benchmark.py`)

**Files:**
- Modify: `run_benchmark.py`
- Test: `tools/test_benchmark_iterations.py`

**Interfaces:**
- Consumes: `src.image_generator.prepare_reference_multires_images`, `run_single_experiment`
- Produces: `execute_full_benchmark(repetitions: int = 30, quick_mode: bool = False, use_reference_image: bool = True) -> pd.DataFrame`

- [ ] **Step 1: Write the failing test**

Buat skrip `tools/test_benchmark_iterations.py`:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_benchmark.py import execute_full_benchmark

# Jalankan skenario ringkas 2 repetisi untuk verifikasi
df = execute_full_benchmark(repetitions=2, quick_mode=True, use_reference_image=True)
assert "iteration" in df.columns
assert len(df[df["iteration"] == 1]) > 0
assert len(df[df["iteration"] == 2]) > 0
print("VERIFIKASI ITERASI BENCHMARK SUKSES")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe tools/test_benchmark_iterations.py`  
Expected: FAIL / Error karena argumen `repetitions` atau `use_reference_image` belum ada.

- [ ] **Step 3: Update `run_benchmark.py` to support 30 iterations on single reference image**

- Perbarui parser CLI `argparse`: tambahkan flag `--repetitions 30` (default 30), `--quick` (3 repetisi).
- Ubah pemuatan citra: muat 1 citra acuan *center-crop* per resolusi.
- Ubah loop pengujian di Skenario A, B, C: lakukan iterasi `for it in range(1, repetitions + 1):` dan simpan nomor iterasi pada kolom `iteration`.
- Simpan riwayat lengkap ke `results/benchmark_results_latest.csv` dan kalkulasi ringkasan statistik (mean & std).

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe tools/test_benchmark_iterations.py`  
Expected: PASS dengan output `VERIFIKASI ITERASI BENCHMARK SUKSES`.

- [ ] **Step 5: Commit**

```bash
git add run_benchmark.py tools/test_benchmark_iterations.py
git commit -m "feat(benchmark): add 30-iteration repetition engine on single reference image"
```

---

### Task 3: Backend Bridge & SSE Streaming Update (`web/backend/services/bridge.py` & `routes/benchmark.py`)

**Files:**
- Modify: `web/backend/services/bridge.py`
- Modify: `web/backend/routes/benchmark.py`
- Test: `tools/test_bench_sse.py`

**Interfaces:**
- Consumes: `BenchmarkRunRequest.repetitions: int = 30`, `_build_execution_queue`
- Produces: Server-Sent Events dengan payload `{..., "iteration": it, "total_iterations": N, ...}`

- [ ] **Step 1: Write test for SSE repetitions in `tools/test_bench_sse.py`**

Perbarui skrip `tools/test_bench_sse.py` untuk memverifikasi payload SSE mengandung kolom `iteration` saat meminta mode `repetitions=3`.

- [ ] **Step 2: Run test to verify it fails**

Run: `.\.venv\Scripts\python.exe tools/test_bench_sse.py`  
Expected: FAIL karena bridge belum menghasilkan field `iteration`.

- [ ] **Step 3: Update `bridge.py` and `benchmark.py`**

- Di `BenchmarkRunRequest`: tambahkan field `repetitions: int = Field(30, ge=1, le=100)`.
- Di `_build_execution_queue`: saat basis adalah `single_image` (default), buat antrean yang mengulang setiap perlakuan sebanyak `repetitions` kali.
- Di `stream_benchmark_events`: sertakan `iteration` pada event progress `run_update`.
- Di `aggregate_summary`: kelompokkan data berdasarkan `(scenario, resolution, filter, p)` dan hitung:
  - `t_serial_mean`, `t_serial_std`
  - `t_parallel_mean`, `t_parallel_std`
  - `speedup_mean`, `efficiency_mean`, `overhead_mean`

- [ ] **Step 4: Run test to verify it passes**

Run: `.\.venv\Scripts\python.exe tools/test_bench_sse.py`  
Expected: PASS (seluruh event SSE terkirim lengkap dengan field `iteration`).

- [ ] **Step 5: Commit**

```bash
git add web/backend/services/bridge.py web/backend/routes/benchmark.py tools/test_bench_sse.py
git commit -m "feat(web): add repetition-aware SSE streaming and statistical aggregation"
```

---

### Task 4: Web Dashboard UI Integration (`web/templates/index.html` & `web/static/js/benchmark.js`)

**Files:**
- Modify: `web/templates/index.html`
- Modify: `web/static/js/benchmark.js`

**Interfaces:**
- Consumes: Radio selector basis data, input iterasi pengujian
- Produces: Request POST `/api/benchmark/run` dengan `basis: "single_image"`, `repetitions: 30`, dan visualisasi progress "Iterasi X / Y".

- [ ] **Step 1: Update UI controls di `web/templates/index.html`**

- Jadikan **"Citra Acuan Tunggal (img_01.png Center-Crop)"** sebagai opsi default pertama pada kartu konfigurasi benchmark Tab 2.
- Tambahkan pilihan iterasi: radio/pill untuk **"30x Iterasi (Standar Ilmiah Penuh)"** dan **"3x Iterasi (Mode Demo Cepat)"**, serta input kustom jika diinginkan.

- [ ] **Step 2: Update logika pengiriman data & tampilan progres di `web/static/js/benchmark.js`**

- Tangkap nilai `repetitions` dan kirimkan ke endpoint `/api/benchmark/run`.
- Pada kartu status live progress, tampilkan badge iterasi: e.g. `Iterasi 14/30 • Resolusi 2048px • Sobel • P=4`.
- Perbarui tabel hasil agar menampilkan kolom `Iterasi` dan tabel summary menampilkan `Mean ± Std`.

- [ ] **Step 3: Verifikasi tampilan di browser**

Buka `http://localhost:8000`, jalankan mode Quick (3x iterasi), dan amati update kartu progress dan grafik Chart.js.

- [ ] **Step 4: Commit**

```bash
git add web/templates/index.html web/static/js/benchmark.js
git commit -m "feat(ui): update benchmark dashboard controls for single-image 30x repetitions"
```

---

### Task 5: End-to-End Verification & Documentation Update

**Files:**
- Modify: `README.md`
- Modify: `PRODUCT.md`
- Modify: `RENCANA_PENGEMBANGAN_SISTEM.md`
- Test: `tools/verify_web.py`

- [ ] **Step 1: Run comprehensive verification script**

Run: `.\.venv\Scripts\python.exe tools/verify_web.py`  
Expected: Seluruh endpoint web dan integrasi komputasi mengembalikan status 200 OK.

- [ ] **Step 2: Update project documentation**

Perbarui dokumentasi proyek untuk menjelaskan metodologi baru: pengujian menggunakan 1 citra acuan master (`img_01.png` center-crop) dengan pengulangan 30 kali per perlakuan demi kepatuhan statistik *Central Limit Theorem*.

- [ ] **Step 3: Final Commit**

```bash
git add README.md PRODUCT.md RENCANA_PENGEMBANGAN_SISTEM.md
git commit -m "docs: document single-image center-crop and 30x repetition benchmarking methodology"
```
