"""
validator.py
============
Modul verifikasi kebenaran data matriks piksel untuk proyek Komputasi Paralel.

Fungsi utama:
    validate_results -- membandingkan hasil serial vs paralel dan menghitung selisih maksimum.
"""

import numpy as np


def validate_results(
    serial_result: np.ndarray,
    parallel_result: np.ndarray,
) -> tuple[bool, float]:
    """Verifikasi kebenaran hasil komputasi paralel terhadap hasil serial (ground truth).

    Pengecekan dilakukan dalam dua tahap:
    1. Kesamaan dimensi/shape antara kedua array.
    2. Keidentikan bit-per-bit menggunakan ``np.array_equal``.

    Selisih absolut maksimum piksel selalu dihitung (dalam presisi float64)
    sebagai metrik diagnostik, bahkan saat hasil dinyatakan identik (nilai = 0.0).

    Parameters
    ----------
    serial_result : np.ndarray
        Array matriks piksel hasil komputasi serial (referensi / ground truth).
    parallel_result : np.ndarray
        Array matriks piksel hasil komputasi paralel yang akan diverifikasi.

    Returns
    -------
    tuple[bool, float]
        - ``is_valid`` (bool): ``True`` jika shape identik **dan** seluruh nilai
          piksel bit-identik; ``False`` jika salah satu kondisi tidak terpenuhi.
        - ``max_diff`` (float): Selisih absolut maksimum antar piksel (float64).
          Bernilai ``-1.0`` jika shape tidak cocok (perbandingan tidak mungkin).

    Examples
    --------
    >>> import numpy as np
    >>> a = np.array([[100, 150], [200, 250]], dtype=np.uint8)
    >>> b = np.array([[100, 150], [200, 250]], dtype=np.uint8)
    >>> validate_results(a, b)
    (True, 0.0)

    >>> c = np.array([[100, 151], [200, 250]], dtype=np.uint8)
    >>> validate_results(a, c)
    (False, 1.0)
    """
    # --- Tahap 1: Cek kesamaan shape/dimensi ---
    if serial_result.shape != parallel_result.shape:
        print(
            f"[VALIDATOR] Shape mismatch: "
            f"serial={serial_result.shape}, parallel={parallel_result.shape}"
        )
        return False, -1.0

    # --- Tahap 2: Cek keidentikan bit-per-bit ---
    is_identical: bool = np.array_equal(serial_result, parallel_result)

    # --- Kalkulasi selisih absolut maksimum (dalam float64) ---
    serial_f64 = serial_result.astype(np.float64)
    parallel_f64 = parallel_result.astype(np.float64)
    max_diff: float = float(np.max(np.abs(serial_f64 - parallel_f64)))

    if is_identical:
        print(f"[VALIDATOR] [OK] Hasil identik. Max absolute diff = {max_diff:.6f}")
    else:
        print(
            f"[VALIDATOR] [FAIL] Hasil TIDAK identik. "
            f"Max absolute diff = {max_diff:.6f}"
        )

    return is_identical, max_diff
