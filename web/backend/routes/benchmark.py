"""
benchmark.py
============
Endpoint orkestrator benchmark (Tab 2) dan analisis hasil (Tab 3).

Endpoint:
    GET  /api/benchmark/config         -> opsi basis data, mode, skenario
    POST /api/benchmark/run            -> eksekusi benchmark (streaming SSE)
    POST /api/benchmark/cancel         -> minta penghentian kooperatif run aktif
    GET  /api/benchmark/results/latest -> riwayat hasil mentah terkini (JSON)
    GET  /api/benchmark/results/summary-> agregasi statistik (JSON)
    GET  /api/benchmark/results/raw-csv-> ekspor CSV data mentah
    GET  /api/benchmark/results/summary-csv -> ekspor CSV ringkasan statistik
"""

import io
import json
import logging
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..services import bridge

logger = logging.getLogger("pvwb.routes.benchmark")

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


class BenchmarkRunRequest(BaseModel):
    """Bodi request eksekusi benchmark."""

    basis: str = Field(
        "single_image",
        description="Basis data uji: single_image (1 citra master acuan) | dataset (30 citra nyata) | synthetic",
    )
    mode: str = Field("full", description="Mode: quick (3 repetisi) | full (30 repetisi)")
    scenarios: List[str] = Field(
        ["A", "B", "C"], description="Skenario yang dipilih: subset [A, B, C]"
    )
    repetitions: Optional[int] = Field(
        None, description="Jumlah repetisi pengujian per perlakuan (default: 30x full, 3x quick)"
    )
    append_results: bool = Field(
        False, description="Simpan akumulatif bertahap tanpa menimpa skenario lain"
    )
    cool_down_seconds: float = Field(
        0.0, description="Jeda istirahat pendinginan CPU antar-filter (detik)"
    )


# ---------------------------------------------------------------------------
# Helper hasil (dipanggil via threadpool karena pembacaan disk / aggregasi)
# ---------------------------------------------------------------------------
def _to_native(value: Any) -> Any:
    """Konversi skalar numpy/pandas ke tipe bawaan Python (JSON-safe)."""
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if value is None or (isinstance(value, float) and value != value):  # NaN
        return None
    return value


def _results_payload() -> Optional[Dict[str, Any]]:
    df = bridge.load_results_csv()
    if df is None or df.empty:
        return None
    preview_cols = [
        "timestamp", "scenario", "filter", "resolution", "image_id", "iteration", "p",
        "t_serial", "t_parallel", "speedup", "efficiency", "overhead",
        "cpu_utilization", "is_identical", "max_diff",
    ]
    cols = [c for c in preview_cols if c in df.columns]
    raw_rows = df[cols].to_dict(orient="records")
    rows = [
        {k: _to_native(v) for k, v in record.items()} for record in raw_rows
    ]
    return {
        "count": int(len(df)),
        "columns": cols,
        "rows": rows,
    }


def _summary_payload() -> Dict[str, Any]:
    df = bridge.load_results_csv()
    if df is None or df.empty:
        raise LookupError("Belum ada data hasil benchmark")
    summary = bridge.aggregate_summary(df)
    rows = [
        {k: _to_native(v) for k, v in record.items()}
        for record in summary.to_dict(orient="records")
    ]
    return {
        "count": int(len(summary)),
        "rows": rows,
    }


def _summary_csv_bytes() -> bytes:
    df = bridge.load_results_csv()
    if df is None or df.empty:
        raise LookupError("Belum ada data hasil benchmark")
    summary = bridge.aggregate_summary(df)
    buf = io.StringIO()
    summary.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------
def _sse_event(data: Dict[str, Any]) -> str:
    """Format satu event SSE standar."""
    return f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


def _sse_generator(payload: BenchmarkRunRequest):
    """
    Generator streaming event benchmark -> protokol text/event-stream.

    Skema event `data:` JSON:
        start -> queued -> progress* -> complete | cancelled | error
    Stream ditutup lebih awal begitu event `error` atau `cancelled` muncul.
    """
    run_info = {
        "basis": payload.basis,
        "mode": payload.mode,
        "scenarios": payload.scenarios,
        "repetitions": payload.repetitions,
        "append_results": payload.append_results,
        "cool_down_seconds": payload.cool_down_seconds,
    }
    try:
        if payload.basis not in ("single_image", "dataset", "synthetic"):
            raise ValueError("basis harus 'single_image', 'dataset', atau 'synthetic'")
        if payload.mode not in ("quick", "full"):
            raise ValueError("mode harus 'quick' atau 'full'")

        logger.info("Benchmark SSE dimulai: %s", run_info)
        for event in bridge.stream_benchmark_events(
            basis=payload.basis,
            mode=payload.mode,
            scenarios=payload.scenarios,
            repetitions=payload.repetitions,
            append_results=payload.append_results,
            cool_down_seconds=payload.cool_down_seconds,
        ):
            if event["type"] in ("error", "cancelled"):
                yield _sse_event(event)
                return
            yield _sse_event(event)
    except Exception as exc:  # noqa: BLE001 - error dikonversi jadi event SSE
        logger.exception("Benchmark gagal total: %s", run_info)
        yield _sse_event({"type": "error", "message": str(exc)})


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/config", summary="Konfigurasi opsi benchmark")
async def get_benchmark_config() -> Dict[str, Any]:
    """Metadata skenario & status ketersediaan dataset per resolusi."""
    counts = await run_in_threadpool(bridge.dataset_counts_per_resolution)
    return {
        "ok": True,
        "bases": [
            {"id": "single_image", "label": "Citra Acuan Master (img_01.png Center-Crop 30x Repetisi)"},
            {"id": "dataset", "label": "Dataset 30 Citra Nyata (Mode Legasi)"},
            {"id": "synthetic", "label": "Dataset Sintetis Standar"},
        ],
        "modes": [
            {"id": "full", "label": "Full Scientific Benchmark (30x Repetisi)"},
            {"id": "quick", "label": "Quick Verification (3x Repetisi)"},
        ],
        "scenarios": [
            {"id": "A", "label": bridge.SCENARIO_LABELS["A"]},
            {"id": "B", "label": bridge.SCENARIO_LABELS["B"]},
            {"id": "C", "label": bridge.SCENARIO_LABELS["C"]},
        ],
        "dataset_counts": {str(k): v for k, v in counts.items()},
    }


@router.post("/run", summary="Jalankan benchmark (streaming SSE)")
async def run_benchmark(payload: BenchmarkRunRequest):
    """
    Streaming Server-Sent Event eksekusi benchmark.

    Skema event `data:` JSON:
        start -> queued -> progress* -> complete | cancelled | error
    Field progress memuat baris rekaman CSV siap ditampilkan logger.
    """
    return StreamingResponse(
        _sse_generator(payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/cancel", summary="Batalkan benchmark yang sedang berjalan")
async def cancel_benchmark() -> Dict[str, Any]:
    """
    Minta penghentian kooperatif run benchmark yang sedang berjalan.

    ``requested=True`` bila ada run aktif saat permintaan diterima, ``False``
    bila tidak ada run yang berjalan. Penghentian bersifat kooperatif:
    treatment yang sedang dieksekusi tetap diselesaikan, rekaman yang sudah
    terukur tetap disimpan ke CSV, lalu stream ditutup dengan event
    ``cancelled``.
    """
    requested = bridge.request_benchmark_cancel()
    return {"ok": True, "requested": bool(requested)}


@router.get("/results/latest", summary="Riwayat hasil benchmark mentah")
async def latest_results() -> Dict[str, Any]:
    """Seluruh baris CSV ``benchmark_results_latest.csv`` terkini."""
    payload = await run_in_threadpool(_results_payload)
    if payload is None:
        raise HTTPException(status_code=404, detail="Belum ada data hasil benchmark")
    return {"ok": True, **payload}


@router.get("/results/summary", summary="Agregasi statistik benchmark")
async def summary_results() -> Dict[str, Any]:
    """Ringkasan mean/std per (skenario, filter, resolusi, worker)."""
    try:
        payload = await run_in_threadpool(_summary_payload)
    except LookupError:
        raise HTTPException(
            status_code=404, detail="Belum ada data hasil benchmark"
        ) from None
    return {"ok": True, **payload}


@router.get("/results/raw-csv", summary="Ekspor CSV data mentah")
async def export_raw_csv():
    """Unduh ``benchmark_results_latest.csv`` apa adanya."""
    if not bridge.BENCH_CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="Belum ada data hasil benchmark")
    return StreamingResponse(
        open(bridge.BENCH_CSV_PATH, "rb"),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                'attachment; filename="benchmark_results_latest.csv"'
            )
        },
    )


@router.get("/results/summary-csv", summary="Ekspor CSV ringkasan statistik")
async def export_summary_csv():
    """Unduh CSV hasil agregasi mean & std per kombinasi uji."""
    try:
        content = await run_in_threadpool(_summary_csv_bytes)
    except LookupError:
        raise HTTPException(
            status_code=404, detail="Belum ada data hasil benchmark"
        ) from None
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                'attachment; filename="benchmark_results_summary.csv"'
            )
        },
    )
