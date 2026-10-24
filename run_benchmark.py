"""
Modul: run_benchmark.py
Deskripsi: Master Orchestrator untuk menjalankan eksperimen benchmark komputasi paralel
           secara otomatis, berbasis 1 citra acuan master multiresolusi center-crop
           dengan 30 repetisi perlakuan (memenuhi Central Limit Theorem), tervalidasi
           100% bit-identik, dan terintegrasi langsung dengan modul visualisasi 300 DPI.
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
from src.image_generator import generate_all_test_images, prepare_reference_multires_images
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


def get_dataset_mapping(
    use_reference_image: bool = True,
    use_real_30: bool = False,
    samples_limit: int = 30
) -> Dict[int, List[Tuple[str, str]]]:
    """
    Mengembalikan mapping resolusi ke daftar pasangan (image_name, absolute_path).
    Prioritas:
    1. Citra acuan tunggal center-crop (img_01.png master) jika use_reference_image=True.
    2. Dataset 30 citra fotografi nyata jika use_real_30=True.
    3. Fallback citra sintetis standar.
    """
    res_dict = {}

    if use_reference_image:
        master_path = os.path.join("data", "dataset_30", "4096", "img_01.png")
        input_dir = os.path.join("data", "input")
        # Pastikan citra reference sudah siap
        all_ready = all(
            os.path.exists(os.path.join(input_dir, f"reference_{r}.png"))
            for r in [512, 1024, 2048, 4096]
        )
        if not all_ready and os.path.exists(master_path):
            prepare_reference_multires_images(master_path=master_path, output_dir=input_dir)

        for res in [512, 1024, 2048, 4096]:
            ref_path = os.path.join(input_dir, f"reference_{res}.png")
            if os.path.exists(ref_path):
                res_dict[res] = [(f"ref_img_01_{res}px", os.path.abspath(ref_path))]
            else:
                p = os.path.join(input_dir, f"input_{res}.png")
                if not os.path.exists(p):
                    generate_all_test_images(output_dir=input_dir)
                res_dict[res] = [(f"synthetic_{res}.png", os.path.abspath(p))]
        return res_dict

    for res in [512, 1024, 2048, 4096]:
        dir_path = os.path.join("data", "dataset_30", str(res))
        if use_real_30 and os.path.exists(dir_path):
            files = sorted(glob.glob(os.path.join(dir_path, "*.png")))[:samples_limit]
            if files:
                res_dict[res] = [(os.path.basename(f), os.path.abspath(f)) for f in files]
                continue

        # Fallback ke dataset sintetis
        p = os.path.join("data", "input", f"input_{res}.png")
        if not os.path.exists(p):
            generate_all_test_images(output_dir="data/input")
        res_dict[res] = [(f"synthetic_{res}.png", os.path.abspath(p))]

    return res_dict


def run_single_experiment(
    image: np.ndarray,
    filter_info: dict,
    p_workers: int,
    existing_pool: multiprocessing.Pool = None
) -> dict:
    """
    Menjalankan 1 perlakuan pengujian eksperimen terkontrol:
    1. Mengukur Serial Baseline secara segar per iterasi (interleaved measurement)
    2. Menjalankan Paralel dengan pemantauan CPU latar belakang (mendukung pre-warmed pool)
    3. Memvalidasi keidentikan bit-per-bit hasil
    4. Menghitung metrik performa (Speedup, Efisiensi, Overhead)
    """
    filter_func = filter_info["func"]
    k_radius = filter_info["k_radius"]

    # 1. Serial Baseline Execution (Segar per iterasi untuk variansi riil)
    res_serial, t_serial = run_serial(image, filter_func)

    # 2. Parallel Execution dengan Pemantauan CPU
    monitor = CPUMonitor(interval=0.02)
    monitor.start()

    if p_workers == 1:
        # B0: Mode Serial (Baseline) - run kedua independen
        res_parallel, t_parallel = run_serial(image, filter_func)
    else:
        res_parallel, t_parallel = run_parallel(
            image,
            filter_func,
            p_processes=p_workers,
            kernel_radius=k_radius,
            existing_pool=existing_pool
        )

    cpu_stats = monitor.stop()

    # 3. Validasi Keidentikan Bit Piksel Mutlak
    is_valid, max_diff = validate_results(res_serial, res_parallel)

    # 4. Perhitungan Metrik Saintifik
    metrics = calculate_metrics(t_serial, t_parallel, p_workers)

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


def execute_full_benchmark(
    repetitions: int = 30,
    quick_mode: bool = False,
    use_reference_image: bool = True,
    use_real_30: bool = False,
    samples_limit: int = 30
) -> pd.DataFrame:
    """
    Mengeksekusi matriks benchmark komputasi paralel:
    - Skenario A: Variasi Resolusi (512, 1024, 2048, 4096 px) pada P = 4
    - Skenario B: Skalabilitas Worker (P = 1, 2, 4, 8) pada Resolusi 2048 px
    - Skenario C: Analisis Kompleksitas 3 Filter pada 2048 px & P = 4
    Setiap perlakuan diulang sebanyak `repetitions` kali (default: 30x).
    """
    reps = 3 if quick_mode and repetitions == 30 else repetitions

    print("\n" + "="*85)
    print("   MASTER BENCHMARK ORCHESTRATOR: KOMPUTASI PARALEL MULTIPROCESSING")
    print(f"   Metodologi: 1 Citra Acuan Master Center-Crop | Repetisi Pengujian: {reps}x Putaran")
    print("="*85)

    dataset_dict = get_dataset_mapping(
        use_reference_image=use_reference_image,
        use_real_30=use_real_30,
        samples_limit=samples_limit
    )

    resolutions_a = [512, 1024] if quick_mode else [512, 1024, 2048, 4096]
    workers_b = [1, 2] if quick_mode else [1, 2, 4, 8]
    base_res_b = 1024 if quick_mode else 2048

    records = []

    # Inisialisasi Pre-warmed Pools untuk Windows (P = 2, 4, 8)
    pools = {p: multiprocessing.Pool(processes=p) for p in [2, 4, 8]}
    for p_val, pool in pools.items():
        _ = pool.map(abs, range(p_val))

    # ==========================================================================
    # 1. SKENARIO A: Variasi Resolusi Matriks Citra (P = 4)
    # ==========================================================================
    print("\n" + "-"*85)
    print(f">>> [1/3] SKENARIO A: PENGARUH RESOLUSI CITRA (P = 4 Inti Pekerja, {reps} Repetisi)")
    print(f"    Resolusi: {resolutions_a}")
    print("-"*85)

    pool_4 = pools[4]

    for res in resolutions_a:
        img_list = dataset_dict[res]
        print(f"\n[+] Mengeksekusi Resolusi {res}x{res} px ({reps} repetisi per filter):")

        for f_info in FILTERS_CONFIG:
            f_name = f_info["name"]
            print(f"    -> Filter {f_name:<14}: [", end="", flush=True)

            img_name, img_path = img_list[0]
            img_rgb = load_image_rgb(img_path)

            for it in range(1, reps + 1):
                res_data = run_single_experiment(
                    image=img_rgb,
                    filter_info=f_info,
                    p_workers=4,
                    existing_pool=pool_4
                )

                records.append({
                    "scenario": "A",
                    "filter": f_name,
                    "resolution": res,
                    "image_id": img_name,
                    "iteration": it,
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

            print(f"] Selesai ({reps} iterasi)")

    # ==========================================================================
    # 2. SKENARIO B: Skalabilitas Jumlah Proses Pekerja (P = 1, 2, 4, 8)
    # ==========================================================================
    print("\n" + "-"*85)
    print(f">>> [2/3] SKENARIO B: SKALABILITAS WORKER P IN {workers_b} (Resolusi {base_res_b}x{base_res_b}, {reps} Repetisi)")
    print("-"*85)

    img_b_list = dataset_dict[base_res_b]
    img_name_b, img_path_b = img_b_list[0]
    img_rgb_b = load_image_rgb(img_path_b)

    for p in workers_b:
        print(f"\n[*] Menguji Alokasi P = {p} Worker Proses ({reps} repetisi per filter):")
        pool_p = pools.get(p, None)

        for f_info in FILTERS_CONFIG:
            f_name = f_info["name"]
            print(f"    -> Filter {f_name:<14} (P={p}): [", end="", flush=True)

            for it in range(1, reps + 1):
                res_data = run_single_experiment(
                    image=img_rgb_b,
                    filter_info=f_info,
                    p_workers=p,
                    existing_pool=pool_p
                )

                records.append({
                    "scenario": "B",
                    "filter": f_name,
                    "resolution": base_res_b,
                    "image_id": img_name_b,
                    "iteration": it,
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

    # 2. Simpan Ringkasan Statistik Empiris
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
        f_fraction=None,
        output_path=os.path.join(plots_dir, "skenario_b_amdahl.png")
    )
    plot_scenario_c(
        csv_path=raw_csv,
        output_path=os.path.join(plots_dir, "skenario_c_kompleksitas.png")
    )

    print("[+] Seluruh grafik visualisasi berhasil di-generate!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Benchmark Orchestrator - Komputasi Paralel")
    parser.add_argument("--repetitions", type=int, default=30, help="Jumlah repetisi pengujian per perlakuan (default: 30x)")
    parser.add_argument("--quick", action="store_true", help="Jalankan uji coba cepat (3 repetisi, resolusi 512-1024, P 1-2)")
    parser.add_argument("--synthetic", action="store_true", help="Gunakan citra sintetis alih-alih citra acuan fotografi")
    parser.add_argument("--dataset-30", action="store_true", help="Gunakan mode lama 30 berkas citra berbeda")
    args = parser.parse_args()

    use_ref = not args.synthetic and not args.dataset_30
    use_real = args.dataset_30

    t_start_total = time.perf_counter()
    benchmark_df = execute_full_benchmark(
        repetitions=args.repetitions,
        quick_mode=args.quick,
        use_reference_image=use_ref,
        use_real_30=use_real
    )
    save_and_visualize(benchmark_df, output_csv="results/benchmark_results.csv")
    t_total = time.perf_counter() - t_start_total

    print("\n" + "="*85)
    print(f"   SELURUH RANGKAIAN BENCHMARK SELESAI DALAM {t_total:.2f} DETIK!")
    print(f"   Total Baris Data Terkumpul: {len(benchmark_df)} baris")
    print("="*85 + "\n")
