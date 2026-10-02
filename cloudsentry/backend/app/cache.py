"""
CloudSentry AI — Scan Cache
============================
Stores the latest scan result in memory so finding IDs stay
consistent across multiple API calls.

The scan is re-run only when:
  - The cache is empty (first request)
  - POST /scan is called explicitly
"""

import uuid
from datetime import datetime
from typing import Optional

from app.adapters.simulated_aws import SimulatedAWSAdapter
from app.normalizer.normalizer import Normalizer
from app.rules.runner import RuleRunner
from app.risk.risk_engine import RiskEngine
from app.models import Finding


class ScanCache:
    """Singleton-style in-memory cache of the latest scan."""

    _instance: Optional["ScanCache"] = None

    def __init__(self):
        self._scan_id: Optional[str] = None
        self._findings: list[Finding] = []
        self._started_at: Optional[str] = None
        self._finished_at: Optional[str] = None
        self._stats: dict = {}

    @classmethod
    def get(cls) -> "ScanCache":
        if cls._instance is None:
            cls._instance = ScanCache()
        return cls._instance

    # ───────────────────────────────────────────────
    # RUN A FRESH SCAN
    # ───────────────────────────────────────────────

    def refresh(self) -> dict:
        """Run a new scan and store the result."""
        started = datetime.utcnow().isoformat()
        scan_id = str(uuid.uuid4())[:8]

        adapter = SimulatedAWSAdapter()
        normalizer = Normalizer()
        runner = RuleRunner()
        engine = RiskEngine()

        resources = normalizer.normalize_all(adapter.get_all_resources())
        report = runner.run(resources)
        findings = report["findings"]
        engine.score_all(findings)

        finished = datetime.utcnow().isoformat()

        # Sort by risk desc for consistent output
        findings = sorted(findings, key=lambda f: f.risk_score or 0, reverse=True)

        self._scan_id = scan_id
        self._findings = findings
        self._started_at = started
        self._finished_at = finished
        self._stats = report["stats"]

        return self.get_summary()

    # ───────────────────────────────────────────────
    # GET CACHED DATA (refresh only if empty)
    # ───────────────────────────────────────────────

    def get_findings(self) -> list[Finding]:
        if self._scan_id is None:
            self.refresh()
        return self._findings

    def get_finding(self, finding_id: str) -> Optional[Finding]:
        for f in self.get_findings():
            if f.finding_id == finding_id:
                return f
        return None

    def get_summary(self) -> dict:
        severity_counts: dict[str, int] = {}
        for f in self._findings:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        return {
            "scan_id": self._scan_id,
            "started_at": self._started_at,
            "finished_at": self._finished_at,
            "total_resources": self._stats.get("resources_count", 0),
            "total_rules": self._stats.get("rules_count", 0),
            "total_checks": self._stats.get("total_checks", 0),
            "passed": self._stats.get("passed", 0),
            "failed": self._stats.get("failed", 0),
            "findings": self._findings,
            "severity_counts": severity_counts,
        }