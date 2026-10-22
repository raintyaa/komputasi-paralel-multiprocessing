"""
server.py
=========
Inisialisasi aplikasi FastAPI **Parallel Vision Workbench v2.4**.

Tanggung jawab modul ini:
1. Konfigurasi dokumen OpenAPI + metadata aplikasi.
2. Middleware CORS untuk pengembangan frontend lokal.
3. Mounting folder static (CSS/JS/aset) dan serving template shell index.html.
4. Lifecycle (lifespan): menutup seluruh pre-warmed pool proses saat shutdown.
5. Registrasi seluruh router API: system, live, benchmark.

Menjalankan:
    python web/run_server.py
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routes import benchmark, live, system
from .services.bridge import warm_pools

# ---------------------------------------------------------------------------
# Path resolusi
# ---------------------------------------------------------------------------
WEB_DIR: Path = Path(__file__).resolve().parents[1]
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

logging.basicConfig(
    level=logging.INFO,
    format="[PVWB %(asctime)s] %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("pvwb.server")


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Hook lifecycle FastAPI: shutdown elegan untuk pool multiprocessing."""
    logger.info("Parallel Vision Workbench backend siap (Core UNTAN).")
    yield
    logger.info("Shutdown: menutup seluruh pre-warmed pool proses...")
    warm_pools.close_all()


# ---------------------------------------------------------------------------
# Aplikasi FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Parallel Vision Workbench API",
    version="2.4",
    description=(
        "REST + SSE API dashboard komputasi paralel (pengolahan citra digital "
        "multiprocessing) untuk Mata Kuliah Komputasi Paralel, FMIPA UNTAN."
    ),
    lifespan=lifespan,
)

# CORS longgar khusus lingkungan pengembangan lokal / laboratorium.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_anti_cache_headers(request, call_next):
    """Mencegah browser meng-cache berkas statis (CSS/JS) selama iterasi pengembangan."""
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ---------------------------------------------------------------------------
# Static assets & template shell
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """Serving shell HTML5 dashboard (single-page, tab-strips)."""
    return FileResponse(TEMPLATES_DIR / "index.html", media_type="text/html")


@app.get("/healthz", include_in_schema=False)
async def healthz() -> dict:
    """Probe kesehatan Process sepele untuk cek server hidup."""
    return {"status": "ok", "service": "pvwb-api", "version": "2.4"}


# ---------------------------------------------------------------------------
# Router API
# ---------------------------------------------------------------------------
app.include_router(system.router)
app.include_router(live.router)
app.include_router(benchmark.router)
