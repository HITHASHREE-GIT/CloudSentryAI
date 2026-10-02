"""
CloudSentry AI — Scan endpoint.
Runs the full scan: adapter → normalizer → rules → risk engine.
"""

from fastapi import APIRouter
from datetime import datetime
import uuid

from app.adapters.simulated_aws import SimulatedAWSAdapter
from app.normalizer.normalizer import Normalizer
from app.rules.runner import RuleRunner
from app.risk.risk_engine import RiskEngine
from app.models import ScanResponse, ScanSummary

router = APIRouter(tags=["Scan"])


@router.post("/scan", response_model=ScanResponse)
def run_scan():
    started = datetime.utcnow().isoformat()
    scan_id = str(uuid.uuid4())[:8]

    # 1. Read simulated AWS
    adapter = SimulatedAWSAdapter()
    raw = adapter.get_all_resources()

    # 2. Normalize
    normalizer = Normalizer()
    resources = normalizer.normalize_all(raw)

    # 3. Run rules
    runner = RuleRunner()
    report = runner.run(resources)

    # 4. Score findings
    findings = report["findings"]
    engine = RiskEngine()
    engine.score_all(findings)

    # 5. Summarize
    finished = datetime.utcnow().isoformat()
    severity_counts = {}
    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

    summary = ScanSummary(
        scan_id=scan_id,
        started_at=started,
        finished_at=finished,
        total_resources=report["stats"]["resources_count"],
        total_rules=report["stats"]["rules_count"],
        total_checks=report["stats"]["total_checks"],
        passed=report["stats"]["passed"],
        failed=report["stats"]["failed"],
        findings=findings,
        severity_counts=severity_counts,
    )

    return ScanResponse(
        scan_id=scan_id,
        status="completed",
        summary=summary,
    )