"""
Script Pengujian Komprehensif untuk Modul Ahmad Dzaky (src/filters.py):
1. Unit test fungsi apply_grayscale, apply_gaussian_blur, apply_sobel.
2. Verifikasi kesesuaian tipe data dan dimensi array (H, W, 3) dan (H, W).
3. Uji integrasi kebenaran Serial vs Paralel (P=2, P=4, P=8) menggunakan src/validator.py.
"""

import time
import numpy as np
from src.filters import apply_grayscale, apply_gaussian_blur, apply_sobel
from src.serial_engine import run_serial
from src.parallel_engine import run_parallel
from src.validator import validate_results


def test_unit_filters():
    print(">>> 1. Menguji Unit Test Fungsi Filter di src/filters.py...")

    # Buat citra uji sintetis RGB 128x128
    np.random.seed(42)
    rgb_test = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)

    # 1. Grayscale
    gray = apply_grayscale(rgb_test)
    assert gray.shape == (128, 128), f"Shape grayscale salah: {gray.shape}"
    assert gray.dtype == np.uint8, f"Dtype grayscale salah: {gray.dtype}"
    # Verifikasi bobot manual pada piksel pertama
    expected_p0 = int(round(0.299 * rgb_test[0, 0, 0] + 0.587 * rgb_test[0, 0, 1] + 0.114 * rgb_test[0, 0, 2]))
    assert abs(int(gray[0, 0]) - expected_p0) <= 1, "Kalkulasi nilai piksel grayscale menyimpang"
    print("   [+] apply_grayscale: OK!")

    # 2. Gaussian Blur (RGB)
    blur_rgb = apply_gaussian_blur(rgb_test)
    assert blur_rgb.shape == rgb_test.shape, f"Shape blur RGB salah: {blur_rgb.shape}"
    assert blur_rgb.dtype == np.uint8, f"Dtype blur RGB salah: {blur_rgb.dtype}"
    print("   [+] apply_gaussian_blur (RGB): OK!")

    # Gaussian Blur (Grayscale)
    blur_gray = apply_gaussian_blur(gray)
    assert blur_gray.shape == gray.shape, f"Shape blur Gray salah: {blur_gray.shape}"
    assert blur_gray.dtype == np.uint8, f"Dtype blur Gray salah: {blur_gray.dtype}"
    print("   [+] apply_gaussian_blur (Grayscale): OK!")

    # 3. Sobel (Input RGB)
    sobel_from_rgb = apply_sobel(rgb_test)
    assert sobel_from_rgb.shape == (128, 128), f"Shape Sobel salah: {sobel_from_rgb.shape}"
    assert sobel_from_rgb.dtype == np.uint8, f"Dtype Sobel salah: {sobel_from_rgb.dtype}"
    print("   [+] apply_sobel (dari input RGB): OK!")

    # Sobel (Input Grayscale)
    sobel_from_gray = apply_sobel(gray)
    assert sobel_from_gray.shape == (128, 128), f"Shape Sobel salah: {sobel_from_gray.shape}"
    assert sobel_from_gray.dtype == np.uint8, f"Dtype Sobel salah: {sobel_from_gray.dtype}"
    print("   [+] apply_sobel (dari input Grayscale): OK!")


def test_serial_vs_parallel_conformance():
    print("\n>>> 2. Menguji Kesesuaian Serial vs Paralel (Validasi Bit-Identik)...")

    # Citra uji resolusi realistis 512x512
    np.random.seed(123)
    img_512 = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)

    filters_to_test = [
        ("Grayscale", apply_grayscale, 0),
        ("Gaussian Blur", apply_gaussian_blur, 1),
        ("Sobel", apply_sobel, 1),
    ]

    worker_counts = [2, 4, 8]

    all_passed = True

    for filter_name, filter_func, k_radius in filters_to_test:
        print(f"\n   --- Menguji Filter: {filter_name} (radius halo k={k_radius}) ---")
        
        # Eksekusi serial (Ground Truth)
        res_serial, t_serial = run_serial(img_512, filter_func)

        for p in worker_counts:
            # Eksekusi paralel
            res_parallel, t_parallel = run_parallel(
                image=img_512,
                filter_func=filter_func,
                p_processes=p,
                kernel_radius=k_radius
            )

            is_valid, max_diff = validate_results(res_serial, res_parallel)
            status = "IDENTIK (VALID)" if is_valid else "TIDAK IDENTIK (GAGAL)"
            print(f"       P={p} Inti: {status} | Max Diff = {max_diff:.6f} | Serial: {t_serial:.4f}s | Paralel: {t_parallel:.4f}s")

            if not is_valid:
                all_passed = False

    assert all_passed, "Ada uji validasi Serial vs Paralel yang tidak bit-identik!"
    print("\n   [+] Seluruh filter (Grayscale, Gaussian Blur, Sobel) 100% BIT-IDENTIK pada P=2, 4, 8!")


if __name__ == "__main__":
    test_unit_filters()
    test_serial_vs_parallel_conformance()
    print("\n" + "="*66)
    print("  >>> [AUDIT SUKSES] MODUL FILTERS AHMAD BEKERJA 100% SEMPURNA! <<<")
    print("="*66)
