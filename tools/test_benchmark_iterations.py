import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from run_benchmark import execute_full_benchmark

if __name__ == "__main__":
    # Test execute_full_benchmark with 2 repetitions in quick mode
    df = execute_full_benchmark(repetitions=2, quick_mode=True, use_reference_image=True)

    assert "iteration" in df.columns, "Kolom 'iteration' tidak ditemukan di DataFrame"
    assert len(df[df["iteration"] == 1]) > 0, "Iterasi 1 kosong"
    assert len(df[df["iteration"] == 2]) > 0, "Iterasi 2 kosong"
    print("VERIFIKASI ITERASI BENCHMARK SUKSES")
