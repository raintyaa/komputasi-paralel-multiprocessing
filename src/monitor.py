"""
Modul Hardware Profiling & Penghitungan Metrik Kinerja Paralel
Penanggung Jawab: Farrel Nathannael
Deskripsi: Mengukur utilisasi CPU dengan psutil dan menghitung Speedup, Efisiensi, serta Overhead.
"""

import psutil
import threading
import time

class CPUMonitor:
    """Pemantau utilisasi CPU non-blocking di latar belakang."""
    def __init__(self, interval: float = 0.05):
        self.interval = interval
        self._running = False
        self._thread = None
        self._records = []

    def start(self):
        """Memulai pemantauan CPU."""
        raise NotImplementedError("Modul ini akan diisi oleh Farrel Nathannael sesuai PANDUAN_FARREL_PROFILING.md")

    def stop(self) -> dict:
        """Menghentikan pemantauan dan mengembalikan statistik CPU."""
        raise NotImplementedError("Modul ini akan diisi oleh Farrel Nathannael sesuai PANDUAN_FARREL_PROFILING.md")

def calculate_metrics(t_serial: float, t_parallel: float, p_processes: int) -> dict:
    """Menghitung Speedup, Efisiensi (%), dan Overhead Paralel (detik)."""
    raise NotImplementedError("Modul ini akan diisi oleh Farrel Nathannael sesuai PANDUAN_FARREL_PROFILING.md")
