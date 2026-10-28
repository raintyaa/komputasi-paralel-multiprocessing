def create_horizontal_partitions(
    image: np.ndarray, num_workers: int, filter_func: Callable, kernel_radius: int = 1
) -> List[Tuple[np.ndarray, Callable, int, int]]:
    height = image.shape[0]
    chunk_height = height // num_workers
    tasks = []

    for i in range(num_workers):
        start_y = i * chunk_height
        end_y = (i + 1) * chunk_height if i < num_workers - 1 else height

        # Tentukan baris boundary halo (k = 1 untuk filter spasial 3x3)
        halo_top = kernel_radius if (i > 0 and kernel_radius > 0) else 0
        halo_bottom = kernel_radius if (i < num_workers - 1 and kernel_radius > 0) else 0

        # Ekstraksi submatriks baris dengan penambahan baris halo fisik
        sub_chunk = image[start_y - halo_top : end_y + halo_bottom]
        tasks.append((sub_chunk, filter_func, halo_top, halo_bottom))

    return tasks