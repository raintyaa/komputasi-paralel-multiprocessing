"""
Modul Mesin Konkurensi Paralel Berbasis Multiprocessing
Deskripsi: Menerapkan dekomposisi spasial baris horizontal (horizontal row partitioning),
           penyisipan batas ketetanggaan (boundary halo), pemrosesan paralel via worker pool,
           pemangkasan halo per-worker, dan rekonstruksi citra utuh via numpy.vstack.
"""

import multiprocessing
import time
from typing import Callable, List, Tuple
import numpy as np


def _worker_filter_task(task_args: Tuple[np.ndarray, Callable[[np.ndarray], np.ndarray], int, int]) -> np.ndarray:
    """
    Fungsi eksekutor pada masing-masing proses pekerja (worker process).
    Fungsi ini berada pada tingkat modul (top-level) agar dapat diserialisasi (pickled) oleh Python multiprocessing di Windows.

    Parameter task_args tuple berisi:
        - sub_image_with_halo: Potongan matriks baris yang telah diperluas dengan baris batas (halo).
        - filter_func: Fungsi operasi filter yang akan diaplikasikan.
        - halo_top: Jumlah baris batas di sisi atas yang harus dipangkas sebelum dikembalikan.
        - halo_bottom: Jumlah baris batas di sisi bawah yang harus dipangkas sebelum dikembalikan.

    Return:
        np.ndarray: Potongan citra terfilter murni (tanpa baris batas ekstra).
    """
    sub_image_with_halo, filter_func, halo_top, halo_bottom = task_args

    # 1. Jalankan filter pada sub-matriks yang memiliki baris batas
    filtered_block = filter_func(sub_image_with_halo)

    # 2. Pangkas baris batas (boundary halo) agar tidak terjadi duplikasi baris saat penggabungan
    h = filtered_block.shape[0]
    end_idx = h - halo_bottom if halo_bottom > 0 else h
    trimmed_result = filtered_block[halo_top:end_idx]

    return trimmed_result


def create_horizontal_partitions(
    image: np.ndarray, 
    num_workers: int, 
    filter_func: Callable[[np.ndarray], np.ndarray],
    kernel_radius: int = 1
) -> List[Tuple[np.ndarray, Callable[[np.ndarray], np.ndarray], int, int]]:
    """
    Membagi matriks citra secara horizontal ke dalam P blok dengan penambahan boundary halo.

    Parameter:
        image: Array citra masukan berdimensi (H, W, 3) atau (H, W).
        num_workers: Jumlah proses pekerja (P).
        filter_func: Fungsi filter yang akan dieksekusi.
        kernel_radius: Radius spasial matriks kernel (k = 1 untuk kernel 3x3, k = 0 untuk operasi titik).

    Return:
        List task_args untuk disalurkan ke pool.map().
    """
    height = image.shape[0]
    chunk_height = height // num_workers
    tasks = []

    for i in range(num_workers):
        start_y = i * chunk_height
        end_y = (i + 1) * chunk_height if i < num_workers - 1 else height

        # Tentukan baris boundary halo (hanya jika kernel_radius > 0)
        halo_top = kernel_radius if (i > 0 and kernel_radius > 0) else 0
        halo_bottom = kernel_radius if (i < num_workers - 1 and kernel_radius > 0) else 0

        # Potong blok dengan perluasan batas halo
        sub_chunk = image[start_y - halo_top : end_y + halo_bottom]

        tasks.append((sub_chunk, filter_func, halo_top, halo_bottom))

    return tasks


def run_parallel(
    image: np.ndarray,
    filter_func: Callable[[np.ndarray], np.ndarray],
    p_processes: int,
    kernel_radius: int = 1,
    existing_pool: multiprocessing.Pool = None
) -> Tuple[np.ndarray, float]:
    """
    Mengeksekusi pemrosesan citra secara paralel berbasis multiprocessing.

    Alur Pengukuran (Sesuai Proposal P038 & P055):
    1. Pencatatan stempel waktu awal (start timestamp).
    2. Partisi matriks horizontal + boundary halo.
    3. Distribusi dan eksekusi tugas via Pool.map().
    4. Pembuangan boundary halo pada masing-masing pekerja.
    5. Rekonstruksi citra utuh melalui numpy.vstack().
    6. Pencatatan stempel waktu akhir (stop timestamp).

    Parameter:
        image: Array citra masukan.
        filter_func: Fungsi filter yang akan diproses.
        p_processes: Jumlah alokasi proses pekerja (2, 4, 8).
        kernel_radius: Radius kernel (k = 1 untuk Gaussian & Sobel 3x3, k = 0 untuk Grayscale).
        existing_pool: Objek multiprocessing.Pool opsional jika menggunakan pre-warmed pool.

    Return:
        tuple (reconstructed_image, duration_seconds)
    """
    # Catat stempel waktu awal SEBELUM matriks dipartisi (sesuai P038)
    t_start = time.perf_counter()

    # 1. Dekomposisi baris horizontal + boundary halo
    tasks = create_horizontal_partitions(
        image=image,
        num_workers=p_processes,
        filter_func=filter_func,
        kernel_radius=kernel_radius
    )

    # 2. Eksekusi paralel via Pool
    if existing_pool is not None:
        processed_chunks = existing_pool.map(_worker_filter_task, tasks)
    else:
        with multiprocessing.Pool(processes=p_processes) as pool:
            processed_chunks = pool.map(_worker_filter_task, tasks)

    # 3. Rekonstruksi citra utuh dengan penggabungan vertikal (numpy.vstack)
    reconstructed_image = np.vstack(processed_chunks)

    # Catat stempel waktu akhir SEGERA setelah citra utuh terbentuk
    t_stop = time.perf_counter()

    duration_seconds = t_stop - t_start
    return reconstructed_image, duration_seconds
