"""
Modul Visualisasi Grafik Ilmiah & Kurva Batas Hukum Amdahl
Penanggung Jawab: Guido Marco Silvio
Deskripsi: Menghasilkan gambar grafik publikasi (300 DPI) untuk Skenario A, B, dan C.
"""

import matplotlib.pyplot as plt

def plot_scenario_a(csv_path: str, output_path: str = "results/plots/skenario_a_resolusi.png"):
    """Membuat grafik Skenario A: Pengaruh Resolusi Citra vs Speedup (P = 4 proses)."""
    raise NotImplementedError("Modul ini akan diisi oleh Guido Marco Silvio sesuai PANDUAN_GUIDO_VISUALISASI.md")

def plot_scenario_b(csv_path: str, f_fraction: float = 0.90, output_path: str = "results/plots/skenario_b_amdahl.png"):
    """Membuat grafik Skenario B: Skalabilitas Alokasi Proses vs Batas Teoretis Hukum Amdahl."""
    raise NotImplementedError("Modul ini akan diisi oleh Guido Marco Silvio sesuai PANDUAN_GUIDO_VISUALISASI.md")

def plot_scenario_c(csv_path: str, output_path: str = "results/plots/skenario_c_kompleksitas.png"):
    """Membuat diagram batang ganda Skenario C: Kompleksitas vs Overhead & Utilisasi CPU."""
    raise NotImplementedError("Modul ini akan diisi oleh Guido Marco Silvio sesuai PANDUAN_GUIDO_VISUALISASI.md")
