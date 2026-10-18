"""
web.backend.routes
==================
Definisi endpoint API aplikasi dashboard komputasi paralel.

Router:
- ``system``   : GET  /api/system/specs
- ``live``     : GET  /api/live/config, GET /api/live/dataset/{resolution}, POST /api/live/process
- ``benchmark``: konfigurasi, eksekusi SSE, hasil, dan ekspor CSV benchmark.
"""
