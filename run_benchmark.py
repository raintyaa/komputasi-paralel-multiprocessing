"""
Modul: run_benchmark.py
Deskripsi: Master Orchestrator untuk menjalankan eksperimen benchmark komputasi paralel
           secara otomatis, deterministik (1x run), tervalidasi bit-identik,
           dan terintegrasi langsung dengan modul visualisasi 300 DPI.
Penanggung Jawab: Muhammad Zaki Rakha Bahy (Lead Architect)
"""

import os
import sys
import time
import argparse
import cv2
import numpy as np
import pandas as pd

# Impor seluruh modul pilar sistem
from src.image_generator import generate_all_test_images
from src.filters import apply_grayscale, apply_gaussian_blur, apply_sobel
from src.serial_engine import run_serial
from src.parallel_engine import run_parallel
from src.validator import validate_results
from src.monitor import CPUMonitor, calculate_metrics
from src.visualizer import plot_scenario_a, plot_scenario_b, plot_scenario_c


# Konfigurasi Filter Pengujian
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


def ensure_input_dataset(input_dir: str = "data/input") -> dict[int, str]:
    """
    Memastikan seluruh citra uji sintetis standar (512, 1024, 2048, 4096)
    telah tersedia di folder input_dir. Jika belum, lakukan generate otomatis.
    """
    os.makedirs(input_dir, exist_ok=True)
    required_resolutions = [512, 1024, 2048, 4096]
    dataset_paths = {}

    missing = False
    for res in required_resolutions:
        p = os.path.join(input_dir, f"input_{res}.png")
        if not os.path.exists(p):
            missing = True
            break
        dataset_paths[res] = os.path.abspath(p)

    if missing:
        print("[*] Dataset citra sintetis belum lengkap. Memanggil image_generator...")
        dataset_paths = generate_all_test_images(output_dir=input_dir)
    else:
        print("[+] Seluruh dataset citra sintetis standar telah tersedia di disk.")

    return dataset_paths


def load_image_rgb(file_path: str) -> np.ndarray:
    """Membaca citra dari berkas dan mengonversinya ke format RGB uint8."""
    bgr = cv2.imread(file_path)
    if bgr is None:
        raise FileNotFoundError(f"Gagal membaca citra dari: {file_path}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb


def run_single_experiment(
    image: np.ndarray,
    filter_info: dict,
    p_workers: int,
    t_serial_cached: float = None,
    res_serial_cached: np.ndarray = None
) -> dict:
    """
    Menjalankan 1 perlakuan pengujian eksperimen terkontrol:
    1. Mengukur Serial Baseline (jika belum ada di cache)
    2. Menjalankan Paralel dengan pemantauan CPU latar belakang
    3. Memvalidasi keidentikan bit-per-bit hasil
    4. Menghitung metrik performa (Speedup, Efisiensi, Overhead)
    """
    filter_name = filter_info["name"]
    filter_func = filter_info["func"]
    k_radius = filter_info["k_radius"]

    # 1. Serial Baseline (P = 1)
    if t_serial_cached is None or res_serial_cached is None:
        # Jika p_workers == 1, kita monitor juga CPU pada mode serial
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
        kernel_radius=k_radius
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


def execute_full_benchmark(quick_mode: bool = False) -> pd.DataFrame:
    """
    Mengeksekusi seluruh matriks benchmark:
    - Skenario A: Variasi Resolusi (512, 1024, 2048, 4096) pada P = 4
    - Skenario B: Variasi Worker (P = 1, 2, 4, 8) pada Resolusi 2048
    - Skenario C: Analisis Overhead & CPU pada Resolusi 2048 & P = 4
    """
    print("\n" + "="*80)
    print("   MASTER BENCHMARK ORCHESTRATOR: KOMPUTASI PARALEL MULTIPROCESSING")
    print("="*80)

    # Pastikan dataset citra tersedia
    dataset_paths = ensure_input_dataset("data/input")

    resolutions_a = [512, 1024] if quick_mode else [512, 1024, 2048, 4096]
    workers_b = [1, 2] if quick_mode else [1, 2, 4, 8]
    base_res_b = 1024 if quick_mode else 2048

    records = []

    # Cache untuk menghindari kalkulasi ulang serial pada citra dan filter yang sama
    serial_cache = {}

    # ==========================================================================
    # 1. SKENARIO A: Variasi Resolusi Matriks Citra (P = 4)
    # ==========================================================================
    print("\n" + "-"*80)
    print(">>> MENJALANKAN SKENARIO A: PENGARUH RESOLUSI CITRA (P = 4 Inti Pekerja)")
    print("-"*80)

    for res in resolutions_a:
        img_path = dataset_paths[res]
        print(f"\n[+] Memuat citra resolusi {res}x{res} piksel dari disk...")
        img_rgb = load_image_rgb(img_path)

        for f_info in FILTERS_CONFIG:
            f_name = f_info["name"]
            print(f"    -> Menguji Filter: {f_name:<14} | Resolusi: {res}x{res} | P = 4...", end=" ", flush=True)

            cache_key = (f_name, res)
            cached = serial_cache.get(cache_key, (None, None))

            res_data = run_single_experiment(
                image=img_rgb,
                filter_info=f_info,
                p_workers=4,
                t_serial_cached=cached[0],
                res_serial_cached=cached[1]
            )

            # Simpan cache serial
            if cache_key not in serial_cache:
                serial_cache[cache_key] = (res_data["t_serial_base"], res_data["res_serial"])

            records.append({
                "scenario": "A",
                "filter": f_name,
                "resolution": res,
                "p": 4,
                "t_serial": res_data["t_serial"],
                "t_parallel": res_data["t_parallel"],
                "speedup": res_data["speedup"],
                "efficiency": res_data["efficiency"],
                "overhead": res_data["overhead"],
                "cpu_utilization": res_data["cpu_utilization"],
                "is_identical": res_data["is_identical"],
                "max_diff": res_data["max_diff"]
            })

            status_str = "IDENTIK" if res_data["is_identical"] else "FAIL"
            print(f"Selesai! Ts={res_data['t_serial']:.4f}s | Tp={res_data['t_parallel']:.4f}s | Speedup={res_data['speedup']:.2f}x | Valid: {status_str}")

    # ==========================================================================
    # 2. SKENARIO B: Skalabilitas Jumlah Proses Pekerja (P = 1, 2, 4, 8 pada Res 2048)
    # ==========================================================================
    print("\n" + "-"*80)
    print(f">>> MENJALANKAN SKENARIO B: SKALABILITAS WORKER P IN {workers_b} (Resolusi {base_res_b}x{base_res_b})")
    print("-"*80)

    img_b_path = dataset_paths[base_res_b]
    img_b_rgb = load_image_rgb(img_b_path)

    for f_info in FILTERS_CONFIG:
        f_name = f_info["name"]
        print(f"\n[*] Filter: {f_name}")

        cache_key = (f_name, base_res_b)
        cached = serial_cache.get(cache_key, (None, None))

        for p in workers_b:
            print(f"    -> P = {p} Proses Pekerja...", end=" ", flush=True)

            res_data = run_single_experiment(
                image=img_b_rgb,
                filter_info=f_info,
                p_workers=p,
                t_serial_cached=cached[0],
                res_serial_cached=cached[1]
            )

            if cache_key not in serial_cache:
                serial_cache[cache_key] = (res_data["t_serial_base"], res_data["res_serial"])
                cached = serial_cache[cache_key]

            records.append({
                "scenario": "B",
                "filter": f_name,
                "resolution": base_res_b,
                "p": p,
                "t_serial": res_data["t_serial"],
                "t_parallel": res_data["t_parallel"],
                "speedup": res_data["speedup"],
                "efficiency": res_data["efficiency"],
                "overhead": res_data["overhead"],
                "cpu_utilization": res_data["cpu_utilization"],
                "is_identical": res_data["is_identical"],
                "max_diff": res_data["max_diff"]
            })

            status_str = "IDENTIK" if res_data["is_identical"] else "FAIL"
            print(f"Selesai! Tp={res_data['t_parallel']:.4f}s | Speedup={res_data['speedup']:.2f}x | CPU={res_data['cpu_utilization']:.1f}% | Valid: {status_str}")

    # ==========================================================================
    # 3. SKENARIO C: Analisis Kompleksitas & Overhead (P = 4, Res 2048)
    # ==========================================================================
    print("\n" + "-"*80)
    print(f">>> MENYUSUN DATA SKENARIO C: ANALISIS OVERHEAD VS UTILISASI CPU (P = 4, Res {base_res_b})")
    print("-"*80)

    # Ambil baris dari Skenario B di mana p == 4
    for r in records:
        if r["scenario"] == "B" and r["p"] == 4 and r["resolution"] == base_res_b:
            rec_c = r.copy()
            rec_c["scenario"] = "C"
            records.append(rec_c)
            print(f"    -> Filter: {rec_c['filter']:<14} | Overhead: {rec_c['overhead']:.4f}s | CPU: {rec_c['cpu_utilization']:.1f}% | Speedup: {rec_c['speedup']:.2f}x")

    # Bentuk DataFrame
    df = pd.DataFrame(records)
    return df


def save_and_visualize(df: pd.DataFrame, output_csv: str = "results/benchmark_results.csv"):
    """Menyimpan hasil ke CSV dan memicu pembuatan grafik ilmiah 300 DPI."""
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"\n[+] Seluruh data benchmark berhasil disimpan ke: {os.path.abspath(output_csv)}")

    # Visualisasi
    plots_dir = os.path.join("results", "plots")
    os.makedirs(plots_dir, exist_ok=True)

    print("\n[*] Menghasilkan grafik standar publikasi 300 DPI...")
    plot_scenario_a(
        csv_path=output_csv,
        output_path=os.path.join(plots_dir, "skenario_a_resolusi.png")
    )
    plot_scenario_b(
        csv_path=output_csv,
        f_fraction=0.90,
        output_path=os.path.join(plots_dir, "skenario_b_amdahl.png")
    )
    plot_scenario_c(
        csv_path=output_csv,
        output_path=os.path.join(plots_dir, "skenario_c_kompleksitas.png")
    )

    print("[+] Seluruh grafik visualisasi berhasil di-generate!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Benchmark Orchestrator - Komputasi Paralel")
    parser.add_argument("--quick", action="store_true", help="Jalankan pengujian cepat (resolusi 512-1024, P 1-2)")
    args = parser.parse_args()

    t_start_total = time.perf_counter()
    benchmark_df = execute_full_benchmark(quick_mode=args.quick)
    save_and_visualize(benchmark_df, output_csv="results/benchmark_results.csv")
    t_total = time.perf_counter() - t_start_total

    print("\n" + "="*80)
    print(f"   SELURUH RANGKAIAN BENCHMARK SELESAI DALAM {t_total:.2f} DETIK!")
    print("="*80 + "\n")
