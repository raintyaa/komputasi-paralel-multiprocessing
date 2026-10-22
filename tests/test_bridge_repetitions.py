import unittest
import sys
from pathlib import Path

UTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(UTS_DIR))
sys.path.insert(0, str(UTS_DIR / "web"))

from backend.services import bridge


class TestBridgeRepetitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Backup CSV benchmark riil agar tidak tertimpa eksekusi unit test
        cls.csv_backup = None
        if bridge.BENCH_CSV_PATH.exists():
            cls.csv_backup = bridge.BENCH_CSV_PATH.read_bytes()

    @classmethod
    def tearDownClass(cls):
        # Restore CSV benchmark riil setelah pengujian selesai
        if cls.csv_backup is not None:
            bridge.BENCH_CSV_PATH.write_bytes(cls.csv_backup)

    def test_stream_benchmark_events_repetitions(self):
        # Run stream with basis="single_image", quick=True, repetitions=2
        events = list(bridge.stream_benchmark_events(
            basis="single_image",
            mode="quick",
            scenarios=["A"],
            repetitions=2
        ))

        # Cari event dengan type == "progress"
        progress_events = [e for e in events if e.get("type") == "progress"]
        self.assertGreater(len(progress_events), 0, "Harus ada minimal satu event progress")

        # Cek apakah setiap record memiliki field iteration
        records = [e["record"] for e in progress_events if "record" in e]
        self.assertTrue(all("iteration" in r for r in records), "Setiap record harus memiliki field 'iteration'")

        iterations_found = {r["iteration"] for r in records}
        self.assertIn(1, iterations_found)
        self.assertIn(2, iterations_found)

    def test_stream_benchmark_events_cooldown(self):
        # Quick run on single_image with 1 rep and cool_down_seconds > 0 to verify time.sleep
        events = list(bridge.stream_benchmark_events(
            basis="single_image",
            mode="quick",
            scenarios=["A"],
            repetitions=1,
            cool_down_seconds=0.01
        ))
        cooldown_events = [e for e in events if e.get("type") == "cooldown"]
        self.assertGreater(len(cooldown_events), 0, "Harus ada minimal satu event cooldown saat cool_down_seconds > 0")
        complete_events = [e for e in events if e.get("type") == "complete"]
        self.assertEqual(len(complete_events), 1, "Harus ada satu event complete tanpa exception")


if __name__ == "__main__":
    unittest.main()
