"""
CloudSentry AI — Findings endpoint.
Uses cached scan so finding IDs stay stable across calls.
"""

from fastapi import APIRouter, Query, HTTPException

from app.cache import ScanCache

router = APIRouter(tags=["Findings"])


@router.get("/findings")
def list_findings(
    severity: str | None = Query(None, description="Filter by severity"),
    min_risk: int | None = Query(None, description="Minimum risk score (0-100)"),
):
    cache = ScanCache.get()
    findings = cache.get_findings()

    if severity:
        findings = [f for f in findings if f.severity.upper() == severity.upper()]
    if min_risk is not None:
        findings = [f for f in findings if (f.risk_score or 0) >= min_risk]

    return {
        "count": len(findings),
        "findings": [f.model_dump() for f in findings],
    }


@router.get("/findings/{finding_id}")
def get_finding(finding_id: str):
    cache = ScanCache.get()
    finding = cache.get_finding(finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding.model_dump()