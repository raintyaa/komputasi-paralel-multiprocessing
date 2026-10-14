"""
Module: image_generator.py
Deskripsi: Pembuat dataset citra masukan RGB sintetis standar untuk penelitian
           komputasi paralel (pengujian filter Grayscale, Gaussian Blur, dan Sobel).
Pustaka: numpy, os, cv2
"""

import os
import cv2
import numpy as np


def generate_synthetic_image(width: int, height: int) -> np.ndarray:
    """
    Menghasilkan citra RGB sintetis dengan pola tekstur matematis yang kaya.

    Pola terdiri dari:
    1. Gradien warna horizontal dan vertikal yang halus.
    2. Pola lingkaran konsentris bertingkat di bagian tengah.
    3. Kisi-kisi kotak (grid lines) berkontras tinggi dengan ketebalan presisi.

    Kombinasi pola ini memberikan gradasi halus untuk diuji pada Gaussian Blur,
    dan tepi-tepi tajam (high-frequency edges) nyata untuk diekstraksi oleh filter Sobel.

    Args:
        width (int): Lebar citra dalam piksel.
        height (int): Tinggi citra dalam piksel.

    Returns:
        np.ndarray: Array citra RGB berdimensi (height, width, 3) bertipe uint8.
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"Dimensi citra harus bernilai positif, didapat width={width}, height={height}")

    # Koordinat ternormalisasi [0.0, 1.0] dengan broadcasting efisien
    y_norm = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]  # Bentuk: (height, 1)
    x_norm = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]   # Bentuk: (1, width)

    # 1. Gradien Warna Horizontal, Vertikal, dan Diagonal
    grad_h = x_norm
    grad_v = y_norm
    grad_diag = (x_norm + y_norm) * 0.5

    # 2. Lingkaran Konsentris di Tengah Citra
    # Pusat di (0.5, 0.5)
    center_x = 0.5
    center_y = 0.5
    dist_from_center = np.sqrt((x_norm - center_x) ** 2 + (y_norm - center_y) ** 2)

    # Frekuensi cincin disesuaikan untuk menghasilkan tepi yang rapat dan kontras
    ring_frequency = 28.0
    # Modulasi sinusoidal halus
    smooth_rings = 0.5 * (1.0 + np.sin(2.0 * np.pi * ring_frequency * dist_from_center))
    # Tepi tajam biner pada cincin untuk menyediakan edge nyata bagi operator Sobel
    sharp_rings = (np.sin(2.0 * np.pi * ring_frequency * dist_from_center) > 0.0).astype(np.float32)

    # 3. Kisi-kisi Kotak (Grid Pattern)
    # Interval grid proporsional atau kelipatan pangkat dua (default: 64 piksel)
    grid_spacing = 64
    line_thickness = max(1, min(width, height) // 512)  # 1px untuk 512, 2px untuk 1024, dst.

    y_indices = np.arange(height, dtype=np.int32)[:, None]
    x_indices = np.arange(width, dtype=np.int32)[None, :]
    grid_mask = ((x_indices % grid_spacing < line_thickness) |
                 (y_indices % grid_spacing < line_thickness))

    # 4. Sintesis Saluran Warna (R, G, B)
    # Channel Red: Dominasi gradien horizontal + cincin lingkaran + aksen tepi cincin
    red_channel = 255.0 * (
        0.45 * grad_h +
        0.35 * smooth_rings +
        0.20 * sharp_rings
    )

    # Channel Green: Dominasi gradien vertikal + diagonal wave + inverse cincin
    green_channel = 255.0 * (
        0.40 * grad_v +
        0.30 * (1.0 - smooth_rings) +
        0.30 * (np.sin(4.0 * np.pi * grad_diag) ** 2)
    )

    # Channel Blue: Gradien silang terbalik + cincin konsentris tajam
    blue_channel = 255.0 * (
        0.40 * (1.0 - grad_h) +
        0.35 * (1.0 - grad_v) +
        0.25 * sharp_rings
    )

    # Terapkan garis grid putih/terang dengan intensitas tinggi untuk tepi tajam
    red_channel = np.where(grid_mask, 255.0, red_channel)
    green_channel = np.where(grid_mask, 255.0, green_channel)
    blue_channel = np.where(grid_mask, 255.0, blue_channel)

    # Gabungkan menjadi array RGB (height, width, 3) bertipe uint8
    image_rgb = np.stack([
        np.clip(red_channel, 0, 255).astype(np.uint8),
        np.clip(green_channel, 0, 255).astype(np.uint8),
        np.clip(blue_channel, 0, 255).astype(np.uint8)
    ], axis=2)

    return image_rgb


def generate_all_test_images(output_dir: str = "data/input") -> dict[int, str]:
    """
    Membuat 4 berkas citra masukan sintetis resolusi standar (512, 1024, 2048, 4096).
    Berkas disimpan dalam format PNG tanpa kompresi (cv2.IMWRITE_PNG_COMPRESSION = 0)
    agar tidak menambah overhead kompresi/dekompresi saat dibaca oleh proses benchmark.

    Args:
        output_dir (str): Direktori tujuan penyimpanan berkas citra.

    Returns:
        dict[int, str]: Pemetaan resolusi citra (int) ke path absolut berkas (str).
    """
    # Pastikan direktori tujuan tersedia
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)

    target_resolutions = [512, 1024, 2048, 4096]
    generated_files: dict[int, str] = {}

    print(f"[*] Memulai pembuatan dataset citra sintetis di: {abs_output_dir}")

    for res in target_resolutions:
        filename = f"input_{res}.png"
        file_path = os.path.join(abs_output_dir, filename)

        print(f"    - Menghasilkan citra {res}x{res} piksel...", end=" ", flush=True)

        # 1. Buat citra RGB sintetis
        image_rgb = generate_synthetic_image(width=res, height=res)

        # 2. Konversi RGB ke BGR sebelum disimpan melalui OpenCV
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # 3. Simpan dengan PNG compression level = 0 (tanpa kompresi, I/O murni)
        cv2_write_flags = [cv2.IMWRITE_PNG_COMPRESSION, 0]
        success = cv2.imwrite(file_path, image_bgr, cv2_write_flags)

        if not success:
            raise IOError(f"Gagal menyimpan citra sintetis ke path: {file_path}")

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        generated_files[res] = file_path
        print(f"Selesai! Ukuran berkas: {file_size_mb:.2f} MB")

    print("[+] Seluruh dataset citra sintetis berhasil dibuat.\n")
    return generated_files


if __name__ == "__main__":
    # Eksekusi langsung pembuatan berkas citra sintetis
    output_directory = os.path.join("data", "input")
    results = generate_all_test_images(output_dir=output_directory)

    print("Hasil pemetaan berkas:")
    for resolution, path in results.items():
        print(f"  - {resolution}x{resolution}: {path}")
