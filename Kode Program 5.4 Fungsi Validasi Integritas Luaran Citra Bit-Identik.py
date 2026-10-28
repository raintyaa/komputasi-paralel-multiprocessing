def validate_results(serial_result: np.ndarray, parallel_result: np.ndarray) -> tuple[bool, float]:
    # Tahap 1: Verifikasi keselarasan dimensi geometris matriks
    if serial_result.shape != parallel_result.shape:
        return False, -1.0

    # Tahap 2: Evaluasi deterministik kesetaraan bit piksel
    is_identical = np.array_equal(serial_result, parallel_result)

    # Kalkulasi disparitas absolut maksimum pada presisi float64 (bebas wraparound)
    serial_f64 = serial_result.astype(np.float64)
    parallel_f64 = parallel_result.astype(np.float64)
    max_diff = float(np.max(np.abs(serial_f64 - parallel_f64)))

    return is_identical, max_diff