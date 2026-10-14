"""
Script Pengujian Komprehensif untuk Modul Farrel Nathannael:
1. src/validator.py
2. src/monitor.py
"""

import time
import numpy as np
import psutil
from src.validator import validate_results
from src.monitor import CPUMonitor, calculate_metrics
from src.serial_engine import run_serial
from src.parallel_engine import run_parallel


def dummy_point_filter(img: np.ndarray) -> np.ndarray:
    """Filter point grayscale dummy untuk pengujian integrasi."""
    if len(img.shape) == 2:
        return img
    # Bobot standar ITU-R BT.601
    gray = (
        0.299 * img[:, :, 0].astype(np.float32) +
        0.587 * img[:, :, 1].astype(np.float32) +
        0.114 * img[:, :, 2].astype(np.float32)
    )
    return np.clip(gray, 0, 255).astype(np.uint8)


def test_validator():
    print(">>> 1. Menguji src/validator.py...")

    # Kasus 1: Array identik 2D
    a = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    b = a.copy()
    valid, diff = validate_results(a, b)
    assert valid is True, "Kasus 1 gagal: harus True"
    assert diff == 0.0, "Kasus 1 gagal: diff harus 0.0"
    print("   [+] Kasus 1 (Identik 2D): OK!")

    # Kasus 2: Array identik 3D (RGB)
    a_rgb = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    b_rgb = a_rgb.copy()
    valid, diff = validate_results(a_rgb, b_rgb)
    assert valid is True, "Kasus 2 gagal: harus True"
    assert diff == 0.0, "Kasus 2 gagal: diff harus 0.0"
    print("   [+] Kasus 2 (Identik 3D): OK!")

    # Kasus 3: Beda 1 nilai piksel
    b_rgb_modified = a_rgb.copy()
    b_rgb_modified[10, 10, 0] = (int(b_rgb_modified[10, 10, 0]) + 15) % 256
    valid, diff = validate_results(a_rgb, b_rgb_modified)
    assert valid is False, "Kasus 3 gagal: harus False"
    assert diff > 0.0, "Kasus 3 gagal: diff harus > 0.0"
    print(f"   [+] Kasus 3 (Ada selisih piksel, max_diff={diff}): OK!")

    # Kasus 4: Shape mismatch
    c = np.zeros((100, 50), dtype=np.uint8)
    d = np.zeros((100, 60), dtype=np.uint8)
    valid, diff = validate_results(c, d)
    assert valid is False, "Kasus 4 gagal: harus False"
    assert diff == -1.0, "Kasus 4 gagal: diff harus -1.0"
    print("   [+] Kasus 4 (Shape mismatch): OK!")


def test_monitor():
    print("\n>>> 2. Menguji src/monitor.py (CPUMonitor & calculate_metrics)...")

    # A. Uji calculate_metrics
    m = calculate_metrics(t_serial=10.0, t_parallel=2.5, p_processes=4)
    assert m["speedup"] == 4.0, f"Speedup salah: {m['speedup']}"
    assert m["efficiency"] == 100.0, f"Efficiency salah: {m['efficiency']}"
    assert m["overhead"] == 0.0, f"Overhead salah: {m['overhead']}"
    print("   [+] calculate_metrics (Ideal case): OK!")

    m_overhead = calculate_metrics(t_serial=10.0, t_parallel=3.0, p_processes=4)
    assert m_overhead["speedup"] == round(10.0 / 3.0, 4)
    assert m_overhead["overhead"] == round(3.0 - (10.0 / 4), 4)
    print("   [+] calculate_metrics (With overhead): OK!")

    # B. Uji CPUMonitor background thread
    monitor = CPUMonitor(interval=0.03)
    monitor.start()

    # Jalankan beban komputasi CPU selama ~0.2 detik
    t_start = time.perf_counter()
    while time.perf_counter() - t_start < 0.2:
        _ = [x**2 for x in range(50000)]

    stats = monitor.stop()
    assert "mean_cpu_percent" in stats, "Kunci mean_cpu_percent tidak ditemukan"
    assert "per_core_percent" in stats, "Kunci per_core_percent tidak ditemukan"
    assert "sample_count" in stats, "Kunci sample_count tidak ditemukan"
    assert stats["sample_count"] > 0, "Harus merekam minimal 1 sampel CPU"
    assert len(stats["per_core_percent"]) == psutil.cpu_count(logical=True), "Jumlah core tidak sesuai"
    print(f"   [+] CPUMonitor (Sampel={stats['sample_count']}, Cores={len(stats['per_core_percent'])}, Mean CPU={stats['mean_cpu_percent']}%): OK!")


def test_integration():
    print("\n>>> 3. Uji Integrasi Monitor + Validator dengan Parallel Engine...")
    test_img = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)

    # Serial
    res_serial, t_serial = run_serial(test_img, dummy_point_filter)

    # Parallel dengan monitoring
    monitor = CPUMonitor(interval=0.02)
    monitor.start()

    res_parallel, t_parallel = run_parallel(test_img, dummy_point_filter, p_processes=4, kernel_radius=0)

    cpu_stats = monitor.stop()

    # Validasi kesamaan bit
    is_valid, max_diff = validate_results(res_serial, res_parallel)
    assert is_valid is True, "Hasil serial dan paralel harus identik"
    assert max_diff == 0.0, "Max difference harus 0.0"

    # Kalkulasi metrik
    metrics = calculate_metrics(t_serial, t_parallel, p_processes=4)
    print(f"   [+] Validasi bit-identik: {is_valid} (Diff: {max_diff})")
    print(f"   [+] Metrik: Speedup={metrics['speedup']}x, Overhead={metrics['overhead']}s, CPU={cpu_stats['mean_cpu_percent']}%")
    print("   [+] Uji Integrasi: OK!")


if __name__ == "__main__":
    test_validator()
    test_monitor()
    test_integration()
    print("\n" + "="*66)
    print("  >>> [AUDIT SUKSES] KEDUA MODUL FARREL BEKERJA 100% SEMPURNA! <<<")
    print("="*66)
