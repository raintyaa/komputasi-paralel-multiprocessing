"""
web.backend
===========
Paket lapisan presentasi & orkestrasi HTTP aplikasi Parallel Vision Workbench.

Berisi:
- ``server``        : inisialisasi aplikasi FastAPI (CORS, static mount, lifespan).
- ``routes``        : definisi endpoint REST/SSE (system, live, benchmark).
- ``services.bridge``: jembatan aman ke modul komputasi internal ``src/``.
"""
