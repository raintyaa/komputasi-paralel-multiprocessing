"""
Modul Mesin Eksekusi Serial Baseline (P = 1)
Deskripsi: Menjalankan filter citra secara serial murni pada 1 inti CPU 
           tanpa pembentukan worker pool untuk dijadikan baseline pembanding.
"""

import time
from typing import Callable, Tuple
import numpy as np


def run_serial(image: np.ndarray, filter_func: Callable[[np.ndarray], np.ndarray]) -> Tuple[np.ndarray, float]:
    """
    Mengeksekusi fungsi filter secara sekuensial murni.

    Parameter:
        image: Array citra masukan berdimensi (H, W, 3) atau (H, W).
        filter_func: Fungsi filter yang akan dieksekusi (apply_grayscale, dll).

    Return:
        tuple (result_image, duration_seconds):
            - result_image: Array citra hasil filter.
            - duration_seconds: Waktu eksekusi komputasi murni (detik).
    """
    # Rekam stempel waktu awal
    t_start = time.perf_counter()

    # Eksekusi filter secara serial murni
    result_image = filter_func(image)

    # Rekam stempel waktu akhir
    t_stop = time.perf_counter()

    duration_seconds = t_stop - t_start
    return result_image, duration_seconds
