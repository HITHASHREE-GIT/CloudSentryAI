"""
CloudSentry AI — Scan endpoint.
Explicitly runs a fresh scan and updates the cache.
"""

from fastapi import APIRouter

from app.cache import ScanCache
from app.models import ScanResponse, ScanSummary

router = APIRouter(tags=["Scan"])


@router.post("/scan", response_model=ScanResponse)
def run_scan():
    cache = ScanCache.get()
    summary_dict = cache.refresh()

    summary = ScanSummary(**summary_dict)

    return ScanResponse(
        scan_id=summary_dict["scan_id"],
        status="completed",
        summary=summary,
    )