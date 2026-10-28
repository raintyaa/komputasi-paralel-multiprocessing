def _worker_filter_task(task_args: Tuple[np.ndarray, Callable, int, int]) -> np.ndarray:
    sub_image_with_halo, filter_func, halo_top, halo_bottom = task_args

    # 1. Eksekusi filter spasial pada submatriks ber-halo secara lokal
    filtered_block = filter_func(sub_image_with_halo)

    # 2. Pangkas baris batas tambahan (halo stripping) sebelum data dikembalikan
    h = filtered_block.shape[0]
    end_idx = h - halo_bottom if halo_bottom > 0 else h
    trimmed_result = filtered_block[halo_top:end_idx]

    return trimmed_result

# Pada proses utama: distribusi tugas via IPC dan rekonstruksi vertikal
with multiprocessing.Pool(processes=p_processes) as pool:
    processed_chunks = pool.map(_worker_filter_task, tasks)
reconstructed_image = np.vstack(processed_chunks)