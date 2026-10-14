"""
Skrip Pengujian Mandiri Mesin Serial & Paralel
Fungsi: Memverifikasi apakah dekomposisi horizontal dan rekonstruksi numpy.vstack
        pada parallel_engine.py menghasilkan citra yang bit-identik dengan serial_engine.py.
"""

import numpy as np
from src.serial_engine import run_serial
from src.parallel_engine import run_parallel


def dummy_filter_point(img: np.ndarray) -> np.ndarray:
    """Filter dummy operasi titik (k=0): Membalik warna citra (Invert)."""
    return 255 - img


def dummy_filter_spatial(img: np.ndarray) -> np.ndarray:
    """
    Filter dummy operasi spasial 3x3 (k=1): 
    Menghitung rata-rata lokal 3x3 menggunakan padding edge.
    """
    if img.ndim == 3:
        padded = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode="edge")
        out = (
            padded[:-2, :-2, :] * 0.1 +
            padded[1:-1, 1:-1, :] * 0.6 +
            padded[2:, 2:, :] * 0.3
        )
    else:
        padded = np.pad(img, ((1, 1), (1, 1)), mode="edge")
        out = (
            padded[:-2, :-2] * 0.1 +
            padded[1:-1, 1:-1] * 0.6 +
            padded[2:, 2:] * 0.3
        )
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    print("=================================================================")
    print("      UJI INTEGRASI MESIN KOMPUTASI PARALEL (SERIAL VS PARALEL)  ")
    print("=================================================================")

    # Buat citra dummy 512x512 RGB
    H, W = 512, 512
    test_image = np.random.randint(0, 256, (H, W, 3), dtype=np.uint8)
    print(f"Dimensi Citra Uji: {test_image.shape}, Dtype: {test_image.dtype}\n")

    # 1. Uji Operasi Titik (Grayscale / Invert, k=0)
    print("--- 1. Menguji Operasi Titik (Radius k = 0) ---")
    res_serial, t_serial = run_serial(test_image, dummy_filter_point)
    print(f"Serial (P=1)  : {t_serial*1000:.2f} ms")

    for p in [2, 4, 8]:
        res_par, t_par = run_parallel(test_image, dummy_filter_point, p_processes=p, kernel_radius=0)
        is_identik = np.array_equal(res_serial, res_par)
        speedup = t_serial / t_par if t_par > 0 else 0
        print(f"Paralel (P={p}) : {t_par*1000:.2f} ms | Speedup: {speedup:.2f}x | Identik: {is_identik}")
        assert is_identik, f"ERROR: Hasil paralel P={p} tidak identik dengan serial!"

    # 2. Uji Operasi Spasial Ketetanggan (Gaussian Blur / Sobel 3x3, k=1)
    print("\n--- 2. Menguji Operasi Spasial dengan Boundary Halo (Radius k = 1) ---")
    res_serial_sp, t_serial_sp = run_serial(test_image, dummy_filter_spatial)
    print(f"Serial (P=1)  : {t_serial_sp*1000:.2f} ms")

    for p in [2, 4, 8]:
        res_par_sp, t_par_sp = run_parallel(test_image, dummy_filter_spatial, p_processes=p, kernel_radius=1)
        is_identik_sp = np.array_equal(res_serial_sp, res_par_sp)
        speedup_sp = t_serial_sp / t_par_sp if t_par_sp > 0 else 0
        print(f"Paralel (P={p}) : {t_par_sp*1000:.2f} ms | Speedup: {speedup_sp:.2f}x | Identik: {is_identik_sp}")
        assert is_identik_sp, f"ERROR: Boundary halo gagal! Hasil paralel P={p} tidak identik dengan serial!"

    print("\n=================================================================")
    print(" >>> [SUKSES BESAR] SEMUA PENGUJIAN IDENTIK 100% BIT-FOR-BIT! <<<")
    print("     Mesin dekomposisi horizontal dan rekonstruksi vstack valid! ")
    print("=================================================================")


if __name__ == "__main__":
    main()
