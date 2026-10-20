import unittest
import sys
from pathlib import Path

UTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(UTS_DIR))
sys.path.insert(0, str(UTS_DIR / "web"))

from backend.services import bridge


class TestBridgeRepetitions(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
