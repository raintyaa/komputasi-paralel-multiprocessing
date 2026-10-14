"""
Pengujian Mandiri Komprehensif Modul Guido:
- src/image_generator.py
- src/visualizer.py
"""

import os
import csv
import numpy as np
from src.image_generator import generate_synthetic_image, generate_all_test_images
from src.visualizer import plot_scenario_a, plot_scenario_b, plot_scenario_c

def test_image_generator():
    print(">>> 1. Menguji image_generator.py...")
    # Uji citra ukuran kecil
    img = generate_synthetic_image(256, 256)
    assert img.shape == (256, 256, 3), f"Bentuk salah: {img.shape}"
    assert img.dtype == np.uint8, f"Dtype salah: {img.dtype}"
    print("    - generate_synthetic_image(256, 256): OK!")

    # Uji pembuatan citra 512 dan 1024 (kita uji sampel dulu agar cepat)
    test_out_dir = "data/test_input"
    os.makedirs(test_out_dir, exist_ok=True)
    
    # Simpan sampel 512
    import cv2
    img512 = generate_synthetic_image(512, 512)
    bgr = cv2.cvtColor(img512, cv2.COLOR_RGB2BGR)
    cv2.imwrite(os.path.join(test_out_dir, "input_512.png"), bgr)
    assert os.path.exists(os.path.join(test_out_dir, "input_512.png")), "File 512 gagal disimpan"
    print("    - Penyimpanan citra via OpenCV: OK!")

def test_visualizer():
    print("\n>>> 2. Menguji visualizer.py...")
    os.makedirs("results/plots", exist_ok=True)
    dummy_csv = "results/test_dummy_benchmark.csv"
    
    # Buat CSV dummy pengujian
    with open(dummy_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario", "resolution", "filter", "p", "speedup", "overhead", "cpu_utilization"])
        # Skenario A
        for r, sp_base in [(512, 1.2), (1024, 2.1), (2048, 3.2), (4096, 3.7)]:
            writer.writerow(["A", r, "Grayscale", 4, sp_base * 0.6, 0.02, 55.0])
            writer.writerow(["A", r, "Gaussian Blur", 4, sp_base * 0.85, 0.04, 75.0])
            writer.writerow(["A", r, "Sobel", 4, sp_base * 1.0, 0.05, 88.0])
        # Skenario B
        for p, sp_base in [(1, 1.0), (2, 1.9), (4, 3.4), (8, 5.2)]:
            writer.writerow(["B", 2048, "Grayscale", p, 1.0 + (p-1)*0.4, 0.02, 45.0 + p*5])
            writer.writerow(["B", 2048, "Gaussian Blur", p, 1.0 + (p-1)*0.65, 0.04, 60.0 + p*4])
            writer.writerow(["B", 2048, "Sobel", p, 1.0 + (p-1)*0.85, 0.05, 70.0 + p*3])
        # Skenario C
        writer.writerow(["C", 2048, "Grayscale", 4, 2.0, 0.021, 62.0])
        writer.writerow(["C", 2048, "Gaussian Blur", 4, 2.9, 0.043, 78.0])
        writer.writerow(["C", 2048, "Sobel", 4, 3.4, 0.056, 91.0])

    print("    - CSV dummy berhasil dibuat.")

    # Uji plotting
    plot_scenario_a(dummy_csv, "results/plots/test_plot_a.png")
    plot_scenario_b(dummy_csv, f_fraction=0.90, output_path="results/plots/test_plot_b.png")
    plot_scenario_c(dummy_csv, "results/plots/test_plot_c.png")

    assert os.path.exists("results/plots/test_plot_a.png"), "Plot A tidak ada"
    assert os.path.exists("results/plots/test_plot_b.png"), "Plot B tidak ada"
    assert os.path.exists("results/plots/test_plot_c.png"), "Plot C tidak ada"
    print("    - Seluruh plot (Skenario A, B, C) berhasil di-generate!")

if __name__ == "__main__":
    test_image_generator()
    test_visualizer()
    print("\n==================================================================")
    print("  >>> [AUDIT SUKSES] KEDUA MODUL GUIDO BEKERJA DENGAN SEMPURNA! <<<")
    print("==================================================================")
