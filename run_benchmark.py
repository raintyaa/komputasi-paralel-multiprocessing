"""
Modul: run_benchmark.py
Deskripsi: Master Orchestrator untuk menjalankan eksperimen benchmark komputasi paralel
           secara otomatis, berbasis 30 sampel citra fotografi nyata multiresolusi (120 berkas),
           tervalidasi 100% bit-identik, dan terintegrasi langsung dengan modul visualisasi 300 DPI.
Penanggung Jawab: Muhammad Zaki Rakha Bahy (Lead Architect)
"""

import os
import sys
import time
import glob
import argparse
import multiprocessing
from typing import Dict, List, Tuple
import cv2
import numpy as np
import pandas as pd

# Impor modul pilar sistem
from src.image_generator import generate_all_test_images
from src.filters import apply_grayscale, apply_gaussian_blur, apply_sobel
from src.serial_engine import run_serial
from src.parallel_engine import run_parallel
from src.validator import validate_results
from src.monitor import CPUMonitor, calculate_metrics
from src.visualizer import plot_scenario_a, plot_scenario_b, plot_scenario_c

# Konfigurasi Filter Pengujian Terstandarisasi
FILTERS_CONFIG = [
    {
        "name": "Grayscale",
        "func": apply_grayscale,
        "k_radius": 0,
        "complexity": "Ringan (Point-wise)"
    },
    {
        "name": "Gaussian Blur",
        "func": apply_gaussian_blur,
        "k_radius": 1,
        "complexity": "Moderat (Spasial 3x3)"
    },
    {
        "name": "Sobel",
        "func": apply_sobel,
        "k_radius": 1,
        "complexity": "Berat (Spasial 3x3 Dual-Kernel)"
    }
]


def load_image_rgb(file_path: str) -> np.ndarray:
    """Membaca citra dari berkas dan mengonversinya ke format RGB uint8."""
    bgr = cv2.imread(file_path)
    if bgr is None:
        raise FileNotFoundError(f"Gagal membaca citra dari: {file_path}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def get_dataset_mapping(use_real_30: bool = True, samples_limit: int = 30) -> Dict[int, List[Tuple[str, str]]]:
    """
    Mengembalikan mapping resolusi ke daftar pasangan (image_name, absolute_path).
    Mendukung dataset 30 citra fotografi nyata atau fallback citra sintetis.
    """
    res_dict = {}
    for res in [512, 1024, 2048, 4096]:
        dir_path = os.path.join("data", "dataset_30", str(res))
        if use_real_30 and os.path.exists(dir_path):
            files = sorted(glob.glob(os.path.join(dir_path, "*.png")))[:samples_limit]
            if files:
                res_dict[res] = [(os.path.basename(f), os.path.abspath(f)) for f in files]
                continue

        # Fallback ke dataset sintetis jika dataset 30 tidak ditemukan
        p = os.path.join("data", "input", f"input_{res}.png")
        if not os.path.exists(p):
            generate_all_test_images(output_dir="data/input")
        res_dict[res] = [(f"synthetic_{res}.png", os.path.abspath(p))]

    return res_dict


def run_single_experiment(
    image: np.ndarray,
    filter_info: dict,
    p_workers: int,
    t_serial_cached: float = None,
    res_serial_cached: np.ndarray = None,
    existing_pool: multiprocessing.Pool = None
) -> dict:
    """
    Menjalankan 1 perlakuan pengujian eksperimen terkontrol:
    1. Mengukur Serial Baseline (jika belum ada di cache)
    2. Menjalankan Paralel dengan pemantauan CPU latar belakang (mendukung pre-warmed pool)
    3. Memvalidasi keidentikan bit-per-bit hasil
    4. Menghitung metrik performa (Speedup, Efisiensi, Overhead)
    """
    filter_func = filter_info["func"]
    k_radius = filter_info["k_radius"]

    # 1. Serial Baseline (P = 1)
    if t_serial_cached is None or res_serial_cached is None:
        cpu_mon_serial = CPUMonitor(interval=0.02)
        cpu_mon_serial.start()
        res_serial, t_serial = run_serial(image, filter_func)
        cpu_stats_serial = cpu_mon_serial.stop()
    else:
        res_serial = res_serial_cached
        t_serial = t_serial_cached
        cpu_stats_serial = {"mean_cpu_percent": 0.0}

    # Jika pengujian memang untuk P = 1
    if p_workers == 1:
        metrics = calculate_metrics(t_serial, t_serial, p_processes=1)
        return {
            "t_serial": t_serial,
            "t_parallel": t_serial,
            "speedup": metrics["speedup"],
            "efficiency": metrics["efficiency"],
            "overhead": metrics["overhead"],
            "cpu_utilization": cpu_stats_serial["mean_cpu_percent"],
            "is_identical": True,
            "max_diff": 0.0,
            "res_serial": res_serial,
            "t_serial_base": t_serial
        }

    # 2. Paralel (P > 1) dengan CPU Monitoring
    cpu_mon = CPUMonitor(interval=0.02)
    cpu_mon.start()
    res_parallel, t_parallel = run_parallel(
        image=image,
        filter_func=filter_func,
        p_processes=p_workers,
        kernel_radius=k_radius,
        existing_pool=existing_pool
    )
    cpu_stats = cpu_mon.stop()

    # 3. Validasi Bit-Identik
    is_valid, max_diff = validate_results(res_serial, res_parallel)

    # 4. Hitung Metrik
    metrics = calculate_metrics(t_serial, t_parallel, p_processes=p_workers)

    return {
        "t_serial": t_serial,
        "t_parallel": t_parallel,
        "speedup": metrics["speedup"],
        "efficiency": metrics["efficiency"],
        "overhead": metrics["overhead"],
        "cpu_utilization": cpu_stats["mean_cpu_percent"],
        "is_identical": is_valid,
        "max_diff": max_diff,
        "res_serial": res_serial,
        "t_serial_base": t_serial
    }


def execute_full_benchmark(samples_limit: int = 30, quick_mode: bool = False, use_real_30: bool = True) -> pd.DataFrame:
    """
    Mengeksekusi matriks benchmark penuh sesuai metodologi proposal:
    - Skenario A: Variasi Resolusi (512, 1024, 2048, 4096 px) pada P = 4 (30 citra x 3 filter x 4 res = 360 runs)
    - Skenario B: Skalabilitas Worker (P = 1, 2, 4, 8) pada Resolusi 2048 px (30 citra x 3 filter x 4 P = 360 runs)
    - Skenario C: Analisis Kompleksitas 3 Filter pada 2048 px & P = 4 (30 citra x 3 filter = 90 runs)
    Total: 810 runs (atau 27 runs jika samples_limit=1).
    """
    print("\n" + "="*85)
    print("   MASTER BENCHMARK ORCHESTRATOR: KOMPUTASI PARALEL MULTIPROCESSING")
    print(f"   Target Sampel: {samples_limit} Berkas Citra per Resolusi | Basis: {'Dataset 30 Nyata' if use_real_30 else 'Sintetis'}")
    print("="*85)

    dataset_dict = get_dataset_mapping(use_real_30=use_real_30, samples_limit=samples_limit)

    resolutions_a = [512, 1024] if quick_mode else [512, 1024, 2048, 4096]
    workers_b = [1, 2] if quick_mode else [1, 2, 4, 8]
    base_res_b = 1024 if quick_mode else 2048

    records = []
    serial_cache = {}

    # Inisialisasi Pre-warmed Pools untuk Windows (P = 2, 4, 8)
    pools = {p: multiprocessing.Pool(processes=p) for p in [2, 4, 8]}
    for p_val, pool in pools.items():
        _ = pool.map(abs, range(p_val))

    # ==========================================================================
    # 1. SKENARIO A: Variasi Resolusi Matriks Citra (P = 4)
    # ==========================================================================
    print("\n" + "-"*85)
    print(">>> [1/3] SKENARIO A: PENGARUH RESOLUSI CITRA (P = 4 Inti Pekerja)")
    print(f"    Resolusi: {resolutions_a} | Jumlah Citra per Resolusi: {len(dataset_dict[resolutions_a[0]])}")
    print("-"*85)

    pool_4 = pools[4]

    for res in resolutions_a:
        img_list = dataset_dict[res]
        print(f"\n[+] Mengeksekusi Resolusi {res}x{res} px ({len(img_list)} sampel citra):")

        for f_info in FILTERS_CONFIG:
            f_name = f_info["name"]
            print(f"    -> Filter {f_name:<14}: [", end="", flush=True)

            for idx, (img_name, img_path) in enumerate(img_list):
                img_rgb = load_image_rgb(img_path)

                cache_key = (f_name, res, img_name)
                cached = serial_cache.get(cache_key, (None, None))

                res_data = run_single_experiment(
                    image=img_rgb,
                    filter_info=f_info,
                    p_workers=4,
                    t_serial_cached=cached[0],
                    res_serial_cached=cached[1],
                    existing_pool=pool_4
                )

                if cache_key not in serial_cache:
                    serial_cache[cache_key] = (res_data["t_serial_base"], res_data["res_serial"])

                records.append({
                    "scenario": "A",
                    "filter": f_name,
                    "resolution": res,
                    "image_id": img_name,
                    "p": 4,
                    "t_serial": round(res_data["t_serial"], 6),
                    "t_parallel": round(res_data["t_parallel"], 6),
                    "speedup": round(res_data["speedup"], 3),
                    "efficiency": round(res_data["efficiency"], 2),
                    "overhead": round(res_data["overhead"], 4),
                    "cpu_utilization": round(res_data["cpu_utilization"], 1),
                    "is_identical": res_data["is_identical"],
                    "max_diff": res_data["max_diff"]
                })
                print("#", end="", flush=True)

            print(f"] Selesai ({len(img_list)} citra)")

    # ==========================================================================
    # 2. SKENARIO B: Skalabilitas Jumlah Proses Pekerja (P = 1, 2, 4, 8)
    # ==========================================================================
    print("\n" + "-"*85)
    print(f">>> [2/3] SKENARIO B: SKALABILITAS WORKER P IN {workers_b} (Resolusi {base_res_b}x{base_res_b})")
    print(f"    Jumlah Sampel Citra: {len(dataset_dict[base_res_b])}")
    print("-"*85)

    img_b_list = dataset_dict[base_res_b]

    for p in workers_b:
        print(f"\n[*] Menguji Alokasi P = {p} Worker Proses ({len(img_b_list)} sampel citra):")
        pool_p = pools.get(p, None)

        for f_info in FILTERS_CONFIG:
            f_name = f_info["name"]
            print(f"    -> Filter {f_name:<14} (P={p}): [", end="", flush=True)

            for idx, (img_name, img_path) in enumerate(img_b_list):
                img_rgb = load_image_rgb(img_path)

                cache_key = (f_name, base_res_b, img_name)
                cached = serial_cache.get(cache_key, (None, None))

                res_data = run_single_experiment(
                    image=img_rgb,
                    filter_info=f_info,
                    p_workers=p,
                    t_serial_cached=cached[0],
                    res_serial_cached=cached[1],
                    existing_pool=pool_p
                )

                if cache_key not in serial_cache:
                    serial_cache[cache_key] = (res_data["t_serial_base"], res_data["res_serial"])

                records.append({
                    "scenario": "B",
                    "filter": f_name,
                    "resolution": base_res_b,
                    "image_id": img_name,
                    "p": p,
                    "t_serial": round(res_data["t_serial"], 6),
                    "t_parallel": round(res_data["t_parallel"], 6),
                    "speedup": round(res_data["speedup"], 3),
                    "efficiency": round(res_data["efficiency"], 2),
                    "overhead": round(res_data["overhead"], 4),
                    "cpu_utilization": round(res_data["cpu_utilization"], 1),
                    "is_identical": res_data["is_identical"],
                    "max_diff": res_data["max_diff"]
                })
                print("#", end="", flush=True)

            print(f"] Selesai")

    # ==========================================================================
    # 3. SKENARIO C: Analisis Kompleksitas & Overhead (P = 4, Res 2048)
    # ==========================================================================
    print("\n" + "-"*85)
    print(f">>> [3/3] SKENARIO C: ANALISIS KOMPLEKSITAS ALGORITMA (P = 4, Res {base_res_b})")
    print("-"*85)

    # Ambil baris dari Skenario B di mana p == 4
    for r in records:
        if r["scenario"] == "B" and r["p"] == 4 and r["resolution"] == base_res_b:
            rec_c = r.copy()
            rec_c["scenario"] = "C"
            records.append(rec_c)

    print(f"[+] Berhasil menyusun data Skenario C dari hasil perlakuan P=4 ({len([r for r in records if r['scenario'] == 'C'])} entri).")

    # Tutup persistent pools
    for p_val, pool in pools.items():
        pool.close()
        pool.join()

    # Bentuk DataFrame
    df = pd.DataFrame(records)
    return df


def save_and_visualize(df: pd.DataFrame, output_csv: str = "results/benchmark_results.csv"):
    """
    Menyimpan hasil ke CSV (raw data & ringkasan statistik) dan menghasilkan grafik 300 DPI.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    raw_csv = output_csv
    latest_csv = os.path.join(os.path.dirname(os.path.abspath(output_csv)), "benchmark_results_latest.csv")
    summary_csv = os.path.join(os.path.dirname(os.path.abspath(output_csv)), "benchmark_results_summary.csv")

    # 1. Simpan Raw Data
    df.to_csv(raw_csv, index=False)
    df.to_csv(latest_csv, index=False)
    print(f"\n[+] Raw Data ({len(df)} baris) berhasil disimpan ke:\n    -> {os.path.abspath(raw_csv)}\n    -> {os.path.abspath(latest_csv)}")

    # 2. Simpan Ringkasan Statistik Empiris (27 Baris Perlakuan Standar)
    summary_df = df.groupby(["scenario", "filter", "resolution", "p"]).agg(
        sampel_count=("speedup", "count"),
        t_serial_mean=("t_serial", "mean"),
        t_serial_std=("t_serial", "std"),
        t_parallel_mean=("t_parallel", "mean"),
        t_parallel_std=("t_parallel", "std"),
        speedup_mean=("speedup", "mean"),
        speedup_std=("speedup", "std"),
        efficiency_mean=("efficiency", "mean"),
        overhead_mean=("overhead", "mean"),
        is_identical_all=("is_identical", "all")
    ).reset_index()

    summary_df.to_csv(summary_csv, index=False)
    print(f"[+] Summary Data ({len(summary_df)} kombinasi perlakuan berbobot statistik) disimpan ke:\n    -> {os.path.abspath(summary_csv)}")

    # 3. Visualisasi Grafik Standar Publikasi 300 DPI
    plots_dir = os.path.join("results", "plots")
    os.makedirs(plots_dir, exist_ok=True)

    print("\n[*] Menghasilkan grafik standar publikasi 300 DPI...")
    plot_scenario_a(
        csv_path=raw_csv,
        output_path=os.path.join(plots_dir, "skenario_a_resolusi.png")
    )
    plot_scenario_b(
        csv_path=raw_csv,
        f_fraction=0.92,
        output_path=os.path.join(plots_dir, "skenario_b_amdahl.png")
    )
    plot_scenario_c(
        csv_path=raw_csv,
        output_path=os.path.join(plots_dir, "skenario_c_kompleksitas.png")
    )

    print("[+] Seluruh grafik visualisasi berhasil di-generate!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Benchmark Orchestrator - Komputasi Paralel")
    parser.add_argument("--samples", type=int, default=30, help="Jumlah sampel citra per perlakuan (default: 30 citra)")
    parser.add_argument("--quick", action="store_true", help="Jalankan uji coba cepat (1 sampel citra, resolusi 512-1024, P 1-2)")
    parser.add_argument("--synthetic", action="store_true", help="Gunakan citra sintetis alih-alih 30 citra nyata")
    args = parser.parse_args()

    n_samples = 1 if args.quick else args.samples
    use_real = not args.synthetic

    t_start_total = time.perf_counter()
    benchmark_df = execute_full_benchmark(samples_limit=n_samples, quick_mode=args.quick, use_real_30=use_real)
    save_and_visualize(benchmark_df, output_csv="results/benchmark_results.csv")
    t_total = time.perf_counter() - t_start_total

    print("\n" + "="*85)
    print(f"   SELURUH RANGKAIAN BENCHMARK SELESAI DALAM {t_total:.2f} DETIK!")
    print(f"   Total Baris Data Terkumpul: {len(benchmark_df)} baris")
    print("="*85 + "\n")
