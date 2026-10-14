"""
Modul Pembuat Dataset Citra Sintetis Deterministik
Penanggung Jawab: Guido Marco Silvio
Deskripsi: Menghasilkan citra uji masukan RGB berformat PNG tanpa kompresi pada 4 resolusi.
"""

import numpy as np

def generate_synthetic_image(width: int, height: int) -> np.ndarray:
    """Membuat citra sintetis RGB beresolusi (height, width, 3) dengan pola tekstur deterministik."""
    raise NotImplementedError("Modul ini akan diisi oleh Guido Marco Silvio sesuai PANDUAN_GUIDO_VISUALISASI.md")

def generate_all_test_images(output_dir: str = "data/input") -> dict[int, str]:
    """Menghasilkan dan menyimpan berkas citra masukan pada resolusi 512, 1024, 2048, dan 4096."""
    raise NotImplementedError("Modul ini akan diisi oleh Guido Marco Silvio sesuai PANDUAN_GUIDO_VISUALISASI.md")
