"""
live.py
=======
Endpoint uji interaktif (Tab 1 - Live Filter Demo).

Endpoint:
    GET  /api/live/config              -> daftar filter, resolusi, opsi worker
    GET  /api/live/dataset/{res}       -> daftar nama berkas citra dataset nyata
    POST /api/live/process             -> eksekusi serial vs paralel satu citra
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ..services import bridge

logger = logging.getLogger("pvwb.routes.live")

router = APIRouter(prefix="/api/live", tags=["live"])


class LiveSource(BaseModel):
    """Sumber citra masukan uji interaktif."""

    type: str = Field(
        "synthetic",
        description="Jenis sumber: dataset | synthetic | upload",
    )
    resolution: int = Field(1024, description="Resolusi persegi (px)")
    image: Optional[str] = Field(
        None, description="Nama berkas citra dataset (type=dataset)"
    )
    b64: Optional[str] = Field(
        None, description="Base64/dataURL citra unggahan (type=upload)"
    )


class LiveProcessRequest(BaseModel):
    """Bodi request eksekusi uji interaktif."""

    source: LiveSource
    filter_key: str = Field("gaussian", description="Key filter: grayscale|gaussian|sobel")
    p_workers: int = Field(4, description="Jumlah worker proses (1,2,4,8,12)")
    warm_pool: bool = Field(True, description="Gunakan pool pre-warmed persistent")


@router.get("/config", summary="Konfigurasi opsi uji interaktif")
async def get_live_config() -> Dict[str, Any]:
    """Metadata filter & opsi parameter untuk membangun form UI."""
    return {
        "ok": True,
        "resolutions": bridge.available_resolutions(),
        "workers": bridge.ALLOWED_WORKERS,
        "filters": [
            {
                "key": f["key"],
                "name": f["name"],
                "k_radius": f["k_radius"],
                "complexity": f["complexity"],
            }
            for f in bridge.FILTERS_CONFIG
        ],
    }


@router.get("/dataset/{resolution}", summary="Daftar citra dataset nyata")
async def list_dataset_images(resolution: int) -> Dict[str, Any]:
    """Nama-nama berkas PNG pada data/dataset_30/{resolution}/."""
    if resolution not in bridge.RESOLUTIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Resolusi {resolution} tidak tersedia; gunakan {bridge.RESOLUTIONS}",
        )
    images = await run_in_threadpool(bridge.get_dataset_images, resolution)
    return {
        "ok": True,
        "resolution": resolution,
        "count": len(images),
        "images": [p.name for p in images],
    }


@router.post("/process", summary="Eksekusi serial vs paralel satu citra")
async def process_live(payload: LiveProcessRequest) -> Dict[str, Any]:
    """
    Alur:
        1. Resolve citra (dataset/sintetis/unggahan).
        2. Jalankan serial & paralel (P worker, pool pre-warmed opsional).
        3. Verifikasi bit-identik + metrik (speedup, efisiensi, overhead, CPU).
        4. Kembalikan citra input/serial/paralel/selisih sebagai data URL.
    """
    try:
        image, image_name = await run_in_threadpool(
            bridge.resolve_live_image, payload.source.model_dump()
        )

        def _run():
            return bridge.run_live_compare(
                image=image,
                filter_key=payload.filter_key,
                p_workers=payload.p_workers,
                warm_pool=payload.warm_pool,
            )

        result = await run_in_threadpool(_run)
        cfg = bridge.filter_by_key(payload.filter_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - jangan biarkan server 500 telanjang
        logger.exception("Gagal eksekusi uji interaktif")
        raise HTTPException(status_code=500, detail=f"Eksekusi gagal: {exc}") from exc

    h, w = image.shape[:2]
    serial_img = result.pop("res_serial")
    parallel_img = result.pop("res_parallel")
    diff_img = bridge.compute_diff_image(serial_img, parallel_img)

    return {
        "ok": True,
        "meta": {
            "name": image_name,
            "width": w,
            "height": h,
            "mem_mb": round(image.nbytes / (1024 * 1024), 2),
        },
        "filter": {
            "key": cfg["key"],
            "name": cfg["name"],
            "k_radius": cfg["k_radius"],
            "complexity": cfg["complexity"],
        },
        "p_workers": payload.p_workers,
        "warm_pool": payload.warm_pool,
        **result,
        "images": {
            "input": bridge.to_data_url(image),
            "serial": bridge.to_data_url(serial_img),
            "parallel": bridge.to_data_url(parallel_img),
            "diff": bridge.to_data_url(diff_img),
        },
    }
