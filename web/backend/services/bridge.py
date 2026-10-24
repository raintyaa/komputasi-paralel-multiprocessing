"""
bridge.py
=========
Jembatan (service layer) antara aplikasi web FastAPI dan modul komputasi
internal proyek ``src/`` (parallel_engine, serial_engine, filters, monitor,
validator, image_generator).

Semua logika bisnis komputasi paralel dikemas di sini agar:
1. Route tetap tipis (hanya validasi & HTTP semantics).
2. Modul ``src/`` tidak pernah diimpor langsung oleh route.
3. Perilaku identik dengan aplikasi Streamlit ``app.py`` yang lama.

Author: Tim Komputasi Paralel FMIPA UNTAN
"""

import base64
import datetime
import glob
import gc
import logging
import multiprocessing
import os
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import cv2
import numpy as np
import pandas as pd
import psutil

# Pastikan root proyek (folder UTS) ada di sys.path sebelum mengimpor src/
ROOT_DIR: Path = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.filters import (  # noqa: E402
    apply_gaussian_blur,
    apply_grayscale,
    apply_sobel,
)
from src.image_generator import (  # noqa: E402
    generate_synthetic_image,
    prepare_reference_multires_images,
)
from src.monitor import CPUMonitor, calculate_metrics  # noqa: E402
from src.parallel_engine import run_parallel  # noqa: E402
from src.serial_engine import run_serial  # noqa: E402
from src.validator import validate_results  # noqa: E402

logger = logging.getLogger("pvwb.bridge")

# ---------------------------------------------------------------------------
# Konstanta path & konfigurasi domain
# ---------------------------------------------------------------------------
DATA_DIR = ROOT_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
DATASET_DIR = DATA_DIR / "dataset_30"
RESULTS_DIR = ROOT_DIR / "results"
BENCH_CSV_PATH = RESULTS_DIR / "benchmark_results_latest.csv"

RESOLUTIONS: List[int] = [512, 1024, 2048, 4096]
ALLOWED_WORKERS: List[int] = [1, 2, 4, 8, 12]
CPU_MODEL = "Intel Core i5-13420H"
ENGINE_VERSION = "v2.4"

FILTERS_CONFIG: List[Dict[str, Any]] = [
    {
        "key": "grayscale",
        "name": "Grayscale",
        "func": apply_grayscale,
        "k_radius": 0,
        "complexity": "Ringan (Point-wise)",
    },
    {
        "key": "gaussian",
        "name": "Gaussian Blur",
        "func": apply_gaussian_blur,
        "k_radius": 1,
        "complexity": "Moderat (Spasial 3x3)",
    },
    {
        "key": "sobel",
        "name": "Sobel",
        "func": apply_sobel,
        "k_radius": 1,
        "complexity": "Berat (Spasial 3x3 Dual-Kernel)",
    },
]
FILTER_BY_KEY: Dict[str, Dict[str, Any]] = {f["key"]: f for f in FILTERS_CONFIG}

# Cache citra sintetis agar tidak regenerasi berulang (per-proses server).
_synthetic_cache: Dict[int, np.ndarray] = {}
_synthetic_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Spesifikasi sistem
# ---------------------------------------------------------------------------
def system_specs() -> Dict[str, Any]:
    """Info perangkat keras host untuk chip telemetri navbar."""
    logical = multiprocessing.cpu_count()
    physical = psutil.cpu_count(logical=False) or logical
    ram = psutil.virtual_memory()
    return {
        "cpu_model": CPU_MODEL,
        "physical_cores": physical,
        "logical_threads": logical,
        "ram_total_gb": round(ram.total / (1024 ** 3), 1),
        "dataset_images": dataset_image_count(),
        "engine_version": ENGINE_VERSION,
    }


# ---------------------------------------------------------------------------
# Dataset & citra
# ---------------------------------------------------------------------------
def available_resolutions() -> List[int]:
    return list(RESOLUTIONS)


def filter_by_key(filter_key: str) -> Dict[str, Any]:
    """Ambil metadata filter berdasarkan key (ValueError jika tak dikenal)."""
    cfg = FILTER_BY_KEY.get(filter_key)
    if cfg is None:
        raise ValueError(f"Filter tidak dikenal: {filter_key!r}")
    return cfg


def get_dataset_images(resolution: int) -> List[Path]:
    """Daftar path PNG dataset nyata pada resolusi tertentu (terurut)."""
    target = DATASET_DIR / str(resolution)
    if not target.is_dir():
        return []
    return sorted(Path(p) for p in glob.glob(str(target / "*.png")))


def dataset_image_count() -> int:
    """Total jumlah citra PNG dataset nyata (semua resolusi)."""
    return len(glob.glob(str(DATASET_DIR / "*" / "*.png")))


def dataset_counts_per_resolution() -> Dict[int, int]:
    return {r: len(get_dataset_images(r)) for r in RESOLUTIONS}


def _read_rgb(path: str) -> np.ndarray:
    bgr = cv2.imread(path)
    if bgr is None:
        raise FileNotFoundError(f"Gagal memuat citra: {path}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def load_image_rgb(path: Path) -> np.ndarray:
    """Membaca citra RGB uint8 dari disk."""
    return _read_rgb(str(path))


def get_or_generate_synthetic(resolution: int) -> np.ndarray:
    """Muat (cache) atau generate citra sintetis standar beresolusi tertentu."""
    file_path = INPUT_DIR / f"input_{resolution}.png"
    with _synthetic_lock:
        cached = _synthetic_cache.get(resolution)
    if cached is not None:
        return cached
    if file_path.exists():
        img = _read_rgb(str(file_path))
    else:
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        img = generate_synthetic_image(resolution, resolution)
        cv2.imwrite(str(file_path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    with _synthetic_lock:
        _synthetic_cache[resolution] = img
    return img


def get_reference_image(resolution: int) -> Path:
    """Path berkas citra acuan tunggal master center-crop (siapkan otomatis bila belum ada)."""
    ref_path = INPUT_DIR / f"reference_{resolution}.png"
    if not ref_path.exists():
        master_path = DATASET_DIR / "4096" / "img_01.png"
        if master_path.exists():
            prepare_reference_multires_images(
                master_path=str(master_path), output_dir=str(INPUT_DIR)
            )
        if not ref_path.exists():
            return get_synthetic_image_path(resolution)
    return ref_path


def resolve_live_image(source: Dict[str, Any]) -> Tuple[np.ndarray, str]:
    """
    Resolve citra masukan dari request /api/live/process.

    Param ``source``:
        - {"type": "dataset", "resolution": int, "image": nama-file.png}
        - {"type": "synthetic", "resolution": int}
        - {"type": "upload", "resolution": int, "b64": <dataURL|base64>}

    Returns:
        (image_rgb, label_nama_citra)
    """
    kind = source.get("type", "synthetic")
    resolution = int(source.get("resolution", 1024))
    if resolution not in RESOLUTIONS:
        raise ValueError(f"Resolusi harus salah satu dari {RESOLUTIONS}")

    if kind == "dataset":
        name = str(source.get("image", "")).strip()
        if not name or "/" in name or "\\" in name or name.startswith("."):
            raise ValueError("Nama berkas dataset tidak valid")
        path = DATASET_DIR / str(resolution) / name
        if not path.exists():
            raise FileNotFoundError(f"Citra dataset tidak ditemukan: {name}")
        return load_image_rgb(path), f"Dataset Nyata ({name} @ {resolution}px)"

    if kind == "upload":
        b64 = str(source.get("b64", ""))
        if not b64:
            raise ValueError("Unggahan kosong: kirim kolom b64")
        if "," in b64:  # strip data URL prefix
            b64 = b64.split(",", 1)[1]
        try:
            buf = np.frombuffer(base64.b64decode(b64), dtype=np.uint8)
            bgr = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        except Exception as exc:  # binascii, dll.
            raise ValueError(f"B64 citra tidak dapat didekode: {exc}") from exc
        if bgr is None:
            raise ValueError("Format citra unggahan tidak dikenali")
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), "Unggahan (citra mandiri)"

    img = get_or_generate_synthetic(resolution)
    return img, f"Sintetis Standar {resolution}x{resolution}"


# ---------------------------------------------------------------------------
# Enkod & visualisasi citra
# ---------------------------------------------------------------------------
def _downscale(arr: np.ndarray, max_side: int = 2048) -> np.ndarray:
    """Skala citra agar sisi terpanjang <= max_side (hemat payload HTTP)."""
    h, w = arr.shape[:2]
    longest = max(h, w)
    if longest <= max_side:
        return arr
    scale = max_side / float(longest)
    nh, nw = max(1, int(round(h * scale))), max(1, int(round(w * scale)))
    return cv2.resize(arr, (nw, nh), interpolation=cv2.INTER_AREA)


def encode_image(arr: np.ndarray, max_side: int = 2048) -> bytes:
    """Enkod array (H,W | H,W,3) menjadi PNG bytes, dengan downscale aman."""
    small = _downscale(arr, max_side)
    if small.ndim == 2:
        small = np.clip(small, 0, 255).astype(np.uint8)
    else:
        small = np.clip(small, 0, 255).astype(np.uint8)
    ok, png = cv2.imencode(".png", small)
    if not ok:
        raise ValueError("Encoding PNG gagal")
    return png.tobytes()


def to_data_url(arr: np.ndarray, max_side: int = 2048) -> str:
    """Array citra -> data URL PNG base64 (untuk <img src=...>)."""
    return "data:image/png;base64," + base64.b64encode(
        encode_image(arr, max_side)
    ).decode("ascii")


def compute_diff_image(res_serial: np.ndarray, res_parallel: np.ndarray) -> np.ndarray:
    """Matriks selisih absolut piksel (uint8, siap ditampilkan)."""
    diff = np.abs(
        res_serial.astype(np.float64) - res_parallel.astype(np.float64)
    )
    return np.clip(diff * 255.0, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Pool proses pre-warmed (persistent)
# ---------------------------------------------------------------------------
class WarmPoolManager:
    """
    Pengelola multiprocessing.Pool persistent pre-warmed yang dapat dipakai
    ulang antar-request untuk menghindari penalti cold-spawn Windows.

    Penggunaan:
        manager.acquire(p) sebagai ctx manager -> mengunci pool tsb (thread-safe),
        sehingga request paralel tidak bercampur pada Pool.map() yang sama.
    """

    def __init__(self) -> None:
        self._pools: Dict[int, multiprocessing.Pool] = {}
        self._locks: Dict[int, threading.Lock] = {}
        self._master = threading.Lock()

    @contextmanager
    def acquire(self, p: int) -> Iterator[multiprocessing.Pool]:
        with self._master:
            if p not in self._pools:
                pool = multiprocessing.Pool(processes=p)
                pool.map(abs, range(p))  # warmup spawn-context
                self._pools[p] = pool
                self._locks[p] = threading.Lock()
                logger.info("Pre-warmed pool P=%d dibuat & dihangatkan", p)
            pool, lock = self._pools[p], self._locks[p]
        with lock:
            yield pool

    def close_all(self) -> None:
        with self._master:
            for p, pool in list(self._pools.items()):
                try:
                    pool.close()
                    pool.join()
                except Exception:  # noqa: BLE001 - shutdown best effort
                    try:
                        pool.terminate()
                    except Exception:
                        pass
                self._pools.pop(p, None)
                self._locks.pop(p, None)
            gc.collect()
            logger.info("Semua pre-warmed pool ditutup")


warm_pools = WarmPoolManager()


# ---------------------------------------------------------------------------
# Uji interaktif (Live): satu citra, serial vs paralel
# ---------------------------------------------------------------------------
def run_live_compare(
    image: np.ndarray,
    filter_key: str,
    p_workers: int,
    warm_pool: bool = True,
) -> Dict[str, Any]:
    """
    Eksekusi serial vs paralel untuk satu citra + verifikasi bit-identik.

    Returns:
        Kamus metrik tanpa gambar: t_serial, t_parallel, speedup, efficiency,
        overhead, cpu_utilization, is_identical, max_diff, res_serial,
        res_parallel.
    """
    if p_workers not in ALLOWED_WORKERS:
        raise ValueError(f"Jumlah worker harus salah satu dari {ALLOWED_WORKERS}")
    cfg = filter_by_key(filter_key)
    func, k_rad = cfg["func"], cfg["k_radius"]

    # 1. Serial (baseline single-core)
    res_serial, t_serial = run_serial(image, func)

    # 2. Paralel dengan pemantauan CPU nyata
    monitor = CPUMonitor(interval=0.02)
    monitor.start()
    try:
        if p_workers == 1:
            # P=1 ekuivalen serial murni (definisi benchmark Skenario B)
            t_parallel = t_serial
            res_parallel = res_serial
        elif warm_pool:
            with warm_pools.acquire(p_workers) as pool:
                res_parallel, t_parallel = run_parallel(
                    image=image,
                    filter_func=func,
                    p_processes=p_workers,
                    kernel_radius=k_rad,
                    existing_pool=pool,
                )
        else:
            res_parallel, t_parallel = run_parallel(
                image=image,
                filter_func=func,
                p_processes=p_workers,
                kernel_radius=k_rad,
            )
        cpu_stats = monitor.stop()
    except BaseException:
        # Pastikan thread pencatat CPU berhenti sebelum exception naik
        try:
            monitor.stop()
        except Exception:  # noqa: BLE001 - monitor hanya telemetri
            pass
        raise

    cpu_util = cpu_stats.get("mean_cpu_percent", 0.0)
    if cpu_util == 0.0:
        cpu_util = psutil.cpu_percent(interval=None)

    # 3. Verifikasi keidentikan bit + metrik
    is_identical, max_diff = validate_results(res_serial, res_parallel)
    metrics = calculate_metrics(t_serial, t_parallel, p_processes=p_workers)

    return {
        "t_serial": float(metrics["t_serial"]),
        "t_parallel": float(metrics["t_parallel"]),
        "speedup": float(metrics["speedup"]),
        "efficiency": float(metrics["efficiency"]),
        "overhead": float(metrics["overhead"]),
        "cpu_utilization": round(float(cpu_util), 2),
        "is_identical": bool(is_identical),
        "max_diff": float(max_diff),
        "res_serial": res_serial,
        "res_parallel": res_parallel,
    }


# ---------------------------------------------------------------------------
# Benchmark terorkestrasi (Zero-OOM streaming)
# ---------------------------------------------------------------------------
SCENARIO_LABELS: Dict[str, str] = {
    "A": "Skenario A - Variasi Resolusi 512-4096 px @ P=4",
    "B": "Skenario B - Variasi Worker P=1,2,4,8 pada 2048px",
    "C": "Skenario C - Kompleksitas 3 Filter pada 2048px @ P=4",
}
BENCH_CSV_COLUMNS = [
    "timestamp", "scenario", "filter", "resolution", "image_id", "iteration", "p",
    "t_serial", "t_parallel", "speedup", "efficiency", "overhead",
    "cpu_utilization", "is_identical", "max_diff",
]

# ---------------------------------------------------------------------------
# Pembatalan kooperatif run benchmark (thread-safe)
# ---------------------------------------------------------------------------
# Generator SSE berjalan di threadpool Starlette, sedangkan handler request
# berjalan di event loop, sehingga flag cancel WAJIB thread-safe (Event).
_benchmark_cancel = threading.Event()
_benchmark_running = threading.Event()


def request_benchmark_cancel() -> bool:
    """
    Minta penghentian kooperatif run benchmark yang sedang berjalan.

    Returns:
        True bila ada run yang sedang berjalan saat permintaan diterima,
        False bila tidak ada run aktif. Permintaan tetap dicatat; state basi
        dibersihkan di awal ``stream_benchmark_events`` sehingga run berikutnya
        tidak pernah mulai dalam keadaan ter-cancel.
    """
    active = _benchmark_running.is_set()
    _benchmark_cancel.set()
    return active


def cancel_requested() -> bool:
    """True bila pembatalan run benchmark telah diminta (thread-safe)."""
    return _benchmark_cancel.is_set()


def _begin_benchmark_run() -> None:
    """Tandai run benchmark mulai & buang permintaan cancel yang basi."""
    _benchmark_cancel.clear()
    _benchmark_running.set()


def _end_benchmark_run() -> None:
    """Tandai run benchmark selesai (dipanggil di blok ``finally``)."""
    _benchmark_running.clear()


def _load_target_image(res: int, path: Optional[Path]) -> np.ndarray:
    """Muat citra streaming (file nyata) atau fallback sintetis."""
    if path is not None and path.exists():
        return load_image_rgb(path)
    return get_or_generate_synthetic(res)


def _build_execution_queue(
    basis: str, quick: bool, scenarios: List[str], repetitions: Optional[int] = None
) -> List[Tuple[str, int, Dict[str, Any], int, str, Optional[Path], int]]:
    """
    Susun antrean eksekusi metadata (BEBAS data piksel - Zero-OOM design).
    Item: (scenario, resolution, filter_cfg, p, image_name, image_path, iteration)
    """
    if repetitions is not None and repetitions > 0:
        reps = repetitions
    else:
        reps = 3 if quick else 30

    resolutions_needed = set()
    if "A" in scenarios:
        resolutions_needed.update(RESOLUTIONS)
    if "B" in scenarios or "C" in scenarios:
        resolutions_needed.add(2048)

    target_meta: Dict[int, List[Tuple[str, Optional[Path]]]] = {}
    for r in resolutions_needed:
        meta_list: List[Tuple[str, Optional[Path]]] = []
        if basis == "single_image":
            meta_list.append((f"ref_img_01_{r}px", get_reference_image(r)))
        elif basis == "dataset":
            files = get_dataset_images(r)[: (1 if quick else 30)]
            if not files:
                meta_list.append((f"syn_{r}.png", None))
            else:
                meta_list = [(f.name, f) for f in files]
        else:
            meta_list.append((f"synthetic_{r}.png", None))
        target_meta[r] = meta_list

    queue: List[Tuple[str, int, Dict[str, Any], int, str, Optional[Path], int]] = []
    if "A" in scenarios:
        for r in RESOLUTIONS:
            for f_cfg in FILTERS_CONFIG:
                for name, path in target_meta.get(r, []):
                    if basis in ("single_image", "synthetic"):
                        for it in range(1, reps + 1):
                            queue.append(("A", r, f_cfg, 4, name, path, it))
                    else:
                        queue.append(("A", r, f_cfg, 4, name, path, 1))
    if "B" in scenarios:
        for p in [1, 2, 4, 8]:
            for f_cfg in FILTERS_CONFIG:
                for name, path in target_meta.get(2048, []):
                    if basis in ("single_image", "synthetic"):
                        for it in range(1, reps + 1):
                            queue.append(("B", 2048, f_cfg, p, name, path, it))
                    else:
                        queue.append(("B", 2048, f_cfg, p, name, path, 1))
    # C hanya bila B tidak dipilih (saat B ikut dijalankan, C didefinisikan
    # sebagai duplikasi baris B dengan P=4 di akhir - sesuai app.py).
    if "C" in scenarios and "B" not in scenarios:
        for f_cfg in FILTERS_CONFIG:
            for name, path in target_meta.get(2048, []):
                if basis in ("single_image", "synthetic"):
                    for it in range(1, reps + 1):
                        queue.append(("C", 2048, f_cfg, 4, name, path, it))
                else:
                    queue.append(("C", 2048, f_cfg, 4, name, path, 1))
    return queue


def stream_benchmark_events(
    basis: str = "single_image",
    mode: str = "full",
    scenarios: Optional[List[str]] = None,
    repetitions: Optional[int] = None,
    quick: Optional[bool] = None,
    append_results: bool = False,
    cool_down_seconds: float = 0.0,
) -> Iterator[Dict[str, Any]]:
    """
    Generator streaming eksekusi benchmark - menghasilkan event dict:

    - {"type": "start", "total": n, "basis":..., "mode":..., "scenarios":[...]}
    - {"type": "progress", "index": i, "total": n, "iteration": k, "record": {...baris CSV...}}
    - {"type": "cancelled", "rows": n, "completed": k, "total": n, "csv_path": "..."}
    - {"type": "complete", "rows": n, "csv_path": "...", "summary_rows": n}
    - {"type": "error", "message": "..."}

    Memelihara perilaku identik dengan blok benchmark app.py: pre-warmed pool
    (P=2,4,8), cache serial, muat citra streaming satu-per-satu, duplikasi
    Skenario C dari B@P=4, dan penulisan CSV ``benchmark_results_latest.csv``.

    Pembatalan bersifat kooperatif: ``cancel_requested()`` diperiksa di awal
    setiap iterasi sehingga treatment yang sedang berjalan tidak pernah
    dipotong, dan rekaman yang sudah terukur tetap disimpan sebelum stream
    ditutup dengan event ``cancelled``.
    """
    _begin_benchmark_run()  # run baru tak pernah mulai dalam keadaan ter-cancel

    pools: Dict[int, multiprocessing.Pool] = {}
    new_records: List[Dict[str, Any]] = []
    # Streaming citra: hanya 1 citra aktif di RAM pada satu waktu (Zero-OOM)
    current_img: Optional[np.ndarray] = None
    current_key: Optional[Tuple[int, str]] = None

    try:
        if quick is None:
            quick = mode == "quick"
        if scenarios is None:
            scenarios = ["A", "B", "C"]
        scenarios = [s for s in scenarios if s in SCENARIO_LABELS]
        if not scenarios:
            raise ValueError("Minimal satu skenario harus dipilih")

        yield {
            "type": "start",
            "basis": basis,
            "quick": quick,
            "repetitions": repetitions,
            "scenarios": scenarios,
        }

        queue = _build_execution_queue(basis, quick, scenarios, repetitions=repetitions)
        yield {"type": "queued", "total": len(queue)}

        if not queue:
            raise RuntimeError("Antrean eksekusi kosong: cek ketersediaan dataset")

        pools = {p: multiprocessing.Pool(processes=p) for p in [2, 4, 8]}
        for p_val, pool in pools.items():
            pool.map(abs, range(p_val))  # warmup
        logger.info("Pools benchmark pre-warmed: %s", sorted(pools))

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total = len(queue)
        cancelled = False
        for idx, (scen, res, f_cfg, p, img_name, img_path, it) in enumerate(queue):
            # Cek cancel di AWAL iterasi: treatment yang sudah jalan tak dipotong
            if cancel_requested():
                cancelled = True
                break

            img_key = (res, img_name)
            if current_img is None or current_key != img_key:
                del current_img
                gc.collect()
                current_img = _load_target_image(res, img_path)
                current_key = img_key

            func = f_cfg["func"]
            k_rad = f_cfg["k_radius"]

            # 1. Serial Run (diukur segar per iterasi untuk baseline independen & akurat)
            res_serial, t_serial = run_serial(current_img, func)

            # 2. Paralel Run + Pemantauan CPU
            monitor = CPUMonitor(interval=0.02)
            monitor.start()
            if p == 1:
                # Skenario B0 (1 Proses): run serial kedua independen agar variansi terukur nyata
                res_parallel, t_parallel = run_serial(current_img, func)
            else:
                res_parallel, t_parallel = run_parallel(
                    image=current_img,
                    filter_func=func,
                    p_processes=p,
                    kernel_radius=k_rad,
                    existing_pool=pools.get(p),
                )
            cpu_stats = monitor.stop()
            cpu_util = cpu_stats.get("mean_cpu_percent", 0.0)
            if cpu_util == 0.0:
                cpu_util = psutil.cpu_percent(interval=None)

            is_identical, max_diff = validate_results(res_serial, res_parallel)
            metrics = calculate_metrics(t_serial, t_parallel, p_processes=p)

            record = {
                "timestamp": now_str,
                "scenario": scen,
                "filter": f_cfg["name"],
                "resolution": res,
                "image_id": img_name,
                "iteration": it,
                "p": p,
                "t_serial": round(t_serial, 6),
                "t_parallel": round(t_parallel, 6),
                "speedup": round(metrics["speedup"], 3),
                "efficiency": round(metrics["efficiency"], 2),
                "overhead": round(metrics["overhead"], 4),
                "cpu_utilization": round(cpu_util, 2),
                "is_identical": bool(is_identical),
                "max_diff": round(float(max_diff), 6),
            }
            new_records.append(record)
            del res_parallel

            yield {
                "type": "progress",
                "index": idx + 1,
                "total": total,
                "iteration": it,
                "scenario": scen,
                "filter": f_cfg["name"],
                "resolution": res,
                "p": p,
                "image": img_name,
                "record": record,
            }

            # Jeda pendinginan termal (Cool-down) antar-filter atau saat berganti blok
            if cool_down_seconds > 0 and (idx + 1) < total:
                next_scen, next_res, next_cfg, next_p, _, _, next_it = queue[idx + 1]
                if next_cfg["name"] != f_cfg["name"] or next_scen != scen or next_res != res:
                    yield {
                        "type": "cooldown",
                        "seconds": cool_down_seconds,
                        "message": f"Pendinginan termal CPU ({cool_down_seconds}s) sebelum {next_cfg['name']}...",
                    }
                    time.sleep(cool_down_seconds)

        if cancelled:
            # Persist rekaman yang benar-benar terukur (tanpa fabrikasi baris C)
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            df_new = pd.DataFrame(new_records, columns=BENCH_CSV_COLUMNS)
            if not df_new.empty:
                if append_results and BENCH_CSV_PATH.exists():
                    try:
                        df_old = pd.read_csv(BENCH_CSV_PATH)
                        df_final = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(
                            subset=["scenario", "filter", "resolution", "p", "iteration"], keep="last"
                        )
                    except Exception:
                        df_final = df_new
                else:
                    df_final = df_new
                df_final.to_csv(BENCH_CSV_PATH, index=False)
            logger.info(
                "Benchmark dibatalkan pada %d/%d eksekusi (%d baris tersimpan)",
                len(new_records), total, len(new_records),
            )
            yield {
                "type": "cancelled",
                "rows": len(new_records),
                "completed": len(new_records),
                "total": total,
                "csv_path": str(BENCH_CSV_PATH.relative_to(ROOT_DIR)),
            }
            return

        # Definisi C = duplikasi B@P=4 (saat B ikut dijalankan)
        if "C" in scenarios and "B" in scenarios:
            for rec in list(new_records):
                if rec["scenario"] == "B" and rec["p"] == 4 and rec["resolution"] == 2048:
                    rec_c = dict(rec)
                    rec_c["scenario"] = "C"
                    new_records.append(rec_c)

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        df_new = pd.DataFrame(new_records)

        # Penggabungan bertahap (Incremental Append) untuk mode bertahap
        if append_results and BENCH_CSV_PATH.exists():
            try:
                df_old = pd.read_csv(BENCH_CSV_PATH)
                # Hilangkan baris lama yang skenarionya sama persis agar tidak terduplikasi
                scenarios_in_new = set(df_new["scenario"].unique())
                df_filtered = df_old[~df_old["scenario"].isin(scenarios_in_new)]
                df_final = pd.concat([df_filtered, df_new], ignore_index=True)
            except Exception:
                df_final = df_new
        else:
            df_final = df_new

        df_final.to_csv(BENCH_CSV_PATH, index=False)
        df_summary = aggregate_summary(df_final)

        yield {
            "type": "complete",
            "rows": len(df_final),
            "csv_path": str(BENCH_CSV_PATH.relative_to(ROOT_DIR)),
            "summary_rows": int(len(df_summary)),
        }
    finally:
        _end_benchmark_run()
        for pool in pools.values():
            try:
                pool.close()
                pool.join()
            except Exception:  # noqa: BLE001
                pool.terminate()
        current_img = None
        del current_img
        gc.collect()


# ---------------------------------------------------------------------------
# Akses hasil & agregasi CSV benchmark
# ---------------------------------------------------------------------------
def load_results_csv() -> Optional[pd.DataFrame]:
    """Muat CSV hasil benchmark terbaru (None jika belum ada)."""
    if not BENCH_CSV_PATH.exists():
        return None
    try:
        return pd.read_csv(BENCH_CSV_PATH)
    except Exception:  # noqa: BLE001
        logger.exception("Gagal membaca CSV hasil benchmark")
        return None


def aggregate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Agregasi statistik per (scenario, filter, resolution, p)."""
    grouped = (
        df.groupby(["scenario", "filter", "resolution", "p"])
        .agg(
            Sampel=("speedup", "count"),
            Ts_Mean=("t_serial", "mean"),
            Ts_Std=("t_serial", "std"),
            Tp_Mean=("t_parallel", "mean"),
            Tp_Std=("t_parallel", "std"),
            Speedup_Mean=("speedup", "mean"),
            Speedup_Std=("speedup", "std"),
            Efisiensi_Mean=("efficiency", "mean"),
            CPU_Util_Mean=("cpu_utilization", "mean"),
        )
        .reset_index()
    )
    grouped["Ts_Std"] = grouped["Ts_Std"].fillna(0.0)
    grouped["Tp_Std"] = grouped["Tp_Std"].fillna(0.0)
    grouped["Speedup_Std"] = grouped["Speedup_Std"].fillna(0.0)
    return grouped.round(4)
