"""
CloudSentry AI — Findings endpoint.
Runs a scan and returns only the findings list, sorted by risk score.
"""

from fastapi import APIRouter, Query

from app.adapters.simulated_aws import SimulatedAWSAdapter
from app.normalizer.normalizer import Normalizer
from app.rules.runner import RuleRunner
from app.risk.risk_engine import RiskEngine

router = APIRouter(tags=["Findings"])


@router.get("/findings")
def list_findings(
    severity: str | None = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    min_risk: int | None = Query(None, description="Minimum risk score (0-100)"),
):
    adapter = SimulatedAWSAdapter()
    normalizer = Normalizer()
    runner = RuleRunner()
    engine = RiskEngine()

    resources = normalizer.normalize_all(adapter.get_all_resources())
    report = runner.run(resources)
    findings = report["findings"]
    engine.score_all(findings)

    # Sort by risk score desc
    findings = sorted(findings, key=lambda f: f.risk_score or 0, reverse=True)

    # Filters
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
    adapter = SimulatedAWSAdapter()
    normalizer = Normalizer()
    runner = RuleRunner()
    engine = RiskEngine()

    resources = normalizer.normalize_all(adapter.get_all_resources())
    report = runner.run(resources)
    findings = report["findings"]
    engine.score_all(findings)

    for f in findings:
        if f.finding_id == finding_id:
            return f.model_dump()

    return {"error": "Finding not found", "finding_id": finding_id}