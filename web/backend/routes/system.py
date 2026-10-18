"""
system.py
=========
Endpoint informasi & spesifikasi sistem host.

Endpoint:
    GET /api/system/specs  -> info CPU (Raptor Lake), RAM, jumlah thread, dataset.
"""

import logging
from typing import Any, Dict

import psutil
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from ..services import bridge

logger = logging.getLogger("pvwb.routes.system")

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/specs", summary="Spesifikasi & telemetri host komputasi")
async def get_specs() -> Dict[str, Any]:
    """Info perangkat keras untuk navbar & kartu arsitektur dashboard."""
    specs = await run_in_threadpool(bridge.system_specs)
    return {"ok": True, "specs": specs}


@router.get("/cpu-utilization", summary="Utilisasi CPU per logical core saat ini")
async def get_cpu_utilization() -> Dict[str, Any]:
    """Telemetri penggunaan CPU per-core (untuk grafik Tab Arsitektur)."""
    per_core = await run_in_threadpool(lambda: psutil.cpu_percent(percpu=True))
    logical = len(per_core)
    cores = [
        {"core": f"Core {i + 1}", "role": "P-Core" if i < 8 else "E-Core", "percent": v}
        for i, v in enumerate(per_core)
    ]
    return {"ok": True, "logical_threads": logical, "cores": cores}
