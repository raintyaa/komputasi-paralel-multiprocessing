"""
run_server.py
=============
Entry point aplikasi web Parallel Vision Workbench.

Cara pakai:
    python web/run_server.py            # default http://127.0.0.1:8000
    python web/run_server.py --port 8080
    python web/run_server.py --host 0.0.0.0

Skrip ini:
1. Menambahkan direktori web/ dan root proyek (UTS) ke sys.path.
2. Mengimpor aplikasi FastAPI dari backend.server.
3. Menjalankan Uvicorn single-process (diperlukan agar multiprocessing.Pool
   internal mesin paralel berefisien tanpa multi-worker).
"""

import argparse
import sys
from pathlib import Path

# Tambahkan direktori web/ (agar 'backend' dapat diimpor) dan root proyek
# (agar 'src/' dan 'data/' dapat diakses mesin komputasi).
THIS_DIR = Path(__file__).resolve().parent          # .../web
PROJECT_ROOT = THIS_DIR.parent                      # .../UTS
for _p in (str(THIS_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import uvicorn  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Menjalankan web server Parallel Vision Workbench (FastAPI)."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host binding server")
    parser.add_argument("--port", type=int, default=8000, help="Port HTTP server")
    args = parser.parse_args()

    print("=" * 72)
    print("Parallel Vision Workbench v2.4")
    print("Laboratorium Komputasi Paralel & Pemrosesan Citra - FMIPA UNTAN")
    print(f"URL Dashboard : http://{args.host}:{args.port}")
    print(f"Docs API      : http://{args.host}:{args.port}/docs")
    print("=" * 72)

    # Import dilakukan setelah sys.path siap & CLI ter-parse
    from backend.server import app  # noqa: PLC0415

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
        reload=False,  # multiprocessing.Pool aman pada mode single-process
    )


if __name__ == "__main__":
    main()
