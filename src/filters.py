"""
Modul Algoritma Filter Citra Digital (NumPy Murni)
Penanggung Jawab: Ahmad Dzaky
Deskripsi: Berisi implementasi operasi Grayscale, Gaussian Blur 3x3, dan Deteksi Tepi Sobel.
"""

import numpy as np

def apply_grayscale(image: np.ndarray) -> np.ndarray:
    """Mengonversi citra RGB ke Grayscale menggunakan bobot luminansi (0.299R + 0.587G + 0.114B)."""
    raise NotImplementedError("Modul ini akan diisi oleh Ahmad Dzaky sesuai PANDUAN_AHMAD_FILTERS.md")

def apply_gaussian_blur(image: np.ndarray) -> np.ndarray:
    """Menerapkan filter penghalus Gaussian Blur 3x3 (k=1) dengan konvolusi matriks NumPy."""
    raise NotImplementedError("Modul ini akan diisi oleh Ahmad Dzaky sesuai PANDUAN_AHMAD_FILTERS.md")

def apply_sobel(image: np.ndarray) -> np.ndarray:
    """Menerapkan filter deteksi tepi Sobel 3x3 (Gx, Gy, dan magnitudo gradien)."""
    raise NotImplementedError("Modul ini akan diisi oleh Ahmad Dzaky sesuai PANDUAN_AHMAD_FILTERS.md")
