"""
monitor.py
==========
Modul pengukuran CPU utilization dan kalkulasi metrik komputasi paralel.

Kelas:
    CPUMonitor -- monitor utilisasi CPU berbasis thread latar belakang (daemon).

Fungsi:
    calculate_metrics -- menghitung speedup, efficiency, dan overhead paralel.
"""

import threading
import time
from typing import Optional

import psutil


class CPUMonitor:
    """Monitor utilisasi CPU yang berjalan di thread latar belakang (non-blocking).

    Thread berjalan sebagai daemon sehingga otomatis berhenti ketika proses
    utama selesai, tanpa memblokir eksekusi atau mempengaruhi akurasi
    pengukuran waktu dengan ``time.perf_counter()``.

    Parameters
    ----------
    interval : float, optional
        Interval pencatatan CPU dalam detik (default: 0.05 detik / 50 ms).

    Examples
    --------
    >>> monitor = CPUMonitor(interval=0.05)
    >>> monitor.start()
    >>> # ... jalankan komputasi ...
    >>> metrics = monitor.stop()
    >>> print(metrics["mean_cpu_percent"])
    """

    def __init__(self, interval: float = 0.05) -> None:
        """Inisialisasi CPUMonitor.

        Parameters
        ----------
        interval : float
            Interval antar pencatatan CPU dalam detik. Nilai lebih kecil
            menghasilkan data lebih granular namun menambah sedikit overhead.
        """
        self._interval: float = interval
        self._readings: list[list[float]] = []   # setiap elemen: list utilisasi per core
        self._stop_event: threading.Event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _record_loop(self) -> None:
        """Loop pencatatan utilisasi CPU yang dijalankan di thread latar belakang.

        Menggunakan ``psutil.cpu_percent(interval=None, percpu=True)`` agar
        tidak ada blocking internal di psutil sendiri — blocking diatur oleh
        ``time.sleep`` dengan interval yang sudah ditentukan.
        """
        # Panggilan pertama di sini untuk "menghangatkan" psutil (hasilnya dibuang)
        # agar pembacaan pertama yang disimpan sudah akurat.
        psutil.cpu_percent(interval=None, percpu=True)

        while not self._stop_event.is_set():
            snapshot: list[float] = psutil.cpu_percent(interval=None, percpu=True)
            self._readings.append(snapshot)
            time.sleep(self._interval)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Reset rekaman sebelumnya dan mulai thread pencatatan CPU.

        Aman dipanggil berulang kali; memanggil ``start()`` ulang sebelum
        ``stop()`` akan menghentikan thread lama terlebih dahulu.
        """
        # Hentikan thread lama jika masih berjalan
        if self._thread is not None and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=1.0)

        # Reset state
        self._readings = []
        self._stop_event = threading.Event()

        # Buat dan jalankan thread daemon
        self._thread = threading.Thread(
            target=self._record_loop,
            name="CPUMonitorThread",
            daemon=True,          # Thread mati otomatis saat proses utama selesai
        )
        self._thread.start()
        print(f"[MONITOR] CPUMonitor dimulai (interval={self._interval}s).")

    def stop(self) -> dict:
        """Hentikan thread pencatatan dan hitung statistik utilisasi CPU.

        Returns
        -------
        dict
            Kamus berisi:

            - ``"mean_cpu_percent"`` (float): Rata-rata utilisasi CPU total
              dari semua pembacaan (rerata semua core, semua sampel).
            - ``"per_core_percent"`` (list[float]): Rata-rata utilisasi
              per inti fisik/logis prosesor selama periode pemantauan.
            - ``"sample_count"`` (int): Jumlah sampel yang berhasil direkam.

        Notes
        -----
        Jika tidak ada sampel yang terekam (periode terlalu singkat),
        semua nilai numerik dikembalikan sebagai 0.0.
        """
        # Sinyal berhenti ke thread
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)

        sample_count: int = len(self._readings)

        if sample_count == 0:
            print("[MONITOR] Peringatan: Tidak ada sampel CPU yang terekam.")
            return {
                "mean_cpu_percent": 0.0,
                "per_core_percent": [],
                "sample_count": 0,
            }

        # Hitung rata-rata per core di seluruh sampel
        num_cores: int = len(self._readings[0])
        per_core_percent: list[float] = [
            round(
                sum(sample[core] for sample in self._readings) / sample_count,
                4,
            )
            for core in range(num_cores)
        ]

        # Rata-rata total (rerata semua core dan semua sampel)
        mean_cpu_percent: float = round(
            sum(sum(sample) for sample in self._readings) / (sample_count * num_cores),
            4,
        )

        result = {
            "mean_cpu_percent": mean_cpu_percent,
            "per_core_percent": per_core_percent,
            "sample_count": sample_count,
        }

        print(
            f"[MONITOR] CPUMonitor dihentikan. "
            f"Sampel={sample_count}, "
            f"Mean CPU={mean_cpu_percent:.2f}%, "
            f"Per-core={[f'{v:.1f}%' for v in per_core_percent]}"
        )
        return result


# ---------------------------------------------------------------------------
# Fungsi kalkulasi metrik paralel
# ---------------------------------------------------------------------------

def calculate_metrics(
    t_serial: float,
    t_parallel: float,
    p_processes: int,
) -> dict:
    """Hitung metrik performa komputasi paralel: speedup, efficiency, overhead.

    Definisi metrik:
    - **Speedup (S)**: seberapa besar percepatan paralel dibanding serial.
      ``S = T_serial / T_parallel``
    - **Efficiency (E)**: persentase utilisasi efektif tiap proses.
      ``E = (S / p) * 100``
    - **Overhead (O)**: waktu ekstra paralel dibanding waktu serial ideal.
      ``O = T_parallel - (T_serial / p)``

    Parameters
    ----------
    t_serial : float
        Waktu eksekusi komputasi serial dalam detik (dari ``time.perf_counter()``).
    t_parallel : float
        Waktu eksekusi komputasi paralel dalam detik (dari ``time.perf_counter()``).
    p_processes : int
        Jumlah proses paralel yang digunakan.

    Returns
    -------
    dict
        Kamus dengan kunci:

        - ``"t_serial"`` (float): Waktu serial (detik), dibulatkan 4 desimal.
        - ``"t_parallel"`` (float): Waktu paralel (detik), dibulatkan 4 desimal.
        - ``"p_processes"`` (int): Jumlah proses.
        - ``"speedup"`` (float): Nilai speedup, dibulatkan 4 desimal.
        - ``"efficiency"`` (float): Efisiensi paralel (%), dibulatkan 4 desimal.
        - ``"overhead"`` (float): Overhead waktu (detik), dibulatkan 4 desimal.

    Examples
    --------
    >>> calculate_metrics(t_serial=8.0, t_parallel=2.5, p_processes=4)
    {
        't_serial': 8.0,
        't_parallel': 2.5,
        'p_processes': 4,
        'speedup': 3.2,
        'efficiency': 80.0,
        'overhead': 0.5
    }
    """
    # Speedup
    speedup: float = (t_serial / t_parallel) if t_parallel > 0 else 0.0

    # Efficiency (dalam persen)
    efficiency: float = (speedup / p_processes) * 100.0 if p_processes > 0 else 0.0

    # Overhead (waktu paralel dikurangi waktu serial ideal per proses)
    overhead: float = (
        t_parallel - (t_serial / p_processes) if p_processes > 0 else 0.0
    )

    metrics = {
        "t_serial": round(t_serial, 4),
        "t_parallel": round(t_parallel, 4),
        "p_processes": p_processes,
        "speedup": round(speedup, 4),
        "efficiency": round(efficiency, 4),
        "overhead": round(overhead, 4),
    }

    print(
        f"[MONITOR] Metrik — "
        f"Speedup: {metrics['speedup']}x | "
        f"Efficiency: {metrics['efficiency']}% | "
        f"Overhead: {metrics['overhead']}s"
    )
    return metrics
