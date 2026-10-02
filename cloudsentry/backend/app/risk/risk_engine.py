"""
CloudSentry AI — Risk Engine
=============================
Converts a security finding into a transparent 0-100 risk score.

Formula (documented and reproducible):
    risk_score = severity_weight × exposure_weight × confidence_weight × 100

Weights are documented so the user can see WHY a finding is scored high/low.
"""

from app.models import Finding


# ═══════════════════════════════════════════════════════
# WEIGHTS
# ═══════════════════════════════════════════════════════

SEVERITY_WEIGHTS = {
    "CRITICAL": 1.00,
    "HIGH": 0.75,
    "MEDIUM": 0.50,
    "LOW": 0.25,
}

# Exposure: how publicly reachable is the resource?
EXPOSURE_WEIGHTS = {
    "PUBLIC_INTERNET": 1.00,   # 0.0.0.0/0 exposure
    "PUBLIC_PARTIAL": 0.70,    # Public but restricted
    "INTERNAL": 0.50,          # Internal network only
    "PRIVATE": 0.30,           # Not exposed
    "UNKNOWN": 0.50,
}

# Confidence: how sure are we this is a real issue?
CONFIDENCE_WEIGHTS = {
    "HIGH": 1.00,     # Deterministic rule, no ambiguity
    "MEDIUM": 0.85,   # Rule requires interpretation
    "LOW": 0.70,      # Heuristic
}


# ═══════════════════════════════════════════════════════
# ENGINE
# ═══════════════════════════════════════════════════════

class RiskEngine:
    """Assigns a 0-100 risk score to findings."""

    def score(self, finding: Finding) -> dict:
        """Compute risk score and return breakdown."""
        severity = SEVERITY_WEIGHTS.get(finding.severity.upper(), 0.5)
        exposure = self._infer_exposure(finding)
        confidence = self._infer_confidence(finding)

        raw = severity * exposure * confidence
        score = round(raw * 100)

        # Clamp 0-100
        score = max(0, min(100, score))

        # Save on the finding object
        finding.risk_score = score

        return {
            "score": score,
            "breakdown": {
                "severity": {
                    "value": finding.severity,
                    "weight": severity,
                },
                "exposure": exposure,
                "confidence": confidence,
            },
            "explanation": (
                f"Score = severity({finding.severity}) "
                f"× exposure({exposure}) "
                f"× confidence({confidence}) "
                f"× 100 = {score}"
            ),
        }

    def score_all(self, findings: list[Finding]) -> list[dict]:
        """Score every finding and return the breakdowns."""
        return [self.score(f) for f in findings]

    # ───────────────────────────────────────────────
    # INFERENCE RULES
    # ───────────────────────────────────────────────

    def _infer_exposure(self, finding: Finding) -> float:
        """Determine exposure weight from evidence."""
        evidence = finding.evidence or {}

        # Public S3 or SSH 0.0.0.0/0
        if evidence.get("public_access") is True:
            return EXPOSURE_WEIGHTS["PUBLIC_INTERNET"]
        if evidence.get("source") == "0.0.0.0/0":
            return EXPOSURE_WEIGHTS["PUBLIC_INTERNET"]

        # If resource is IAM/identity (internal)
        if finding.resource_type == "IDENTITY":
            return EXPOSURE_WEIGHTS["INTERNAL"]

        # Logging resources are internal
        if finding.resource_type == "LOGGING":
            return EXPOSURE_WEIGHTS["INTERNAL"]

        # Default: internal
        return EXPOSURE_WEIGHTS["INTERNAL"]

    def _infer_confidence(self, finding: Finding) -> float:
        """All our rules are deterministic — high confidence."""
        return CONFIDENCE_WEIGHTS["HIGH"]


# ───────────────────────────────────────────────
# SELF-TEST
# ───────────────────────────────────────────────

if __name__ == "__main__":
    from app.adapters.simulated_aws import SimulatedAWSAdapter
    from app.normalizer.normalizer import Normalizer
    from app.rules.runner import RuleRunner

    adapter = SimulatedAWSAdapter()
    normalizer = Normalizer()
    resources = normalizer.normalize_all(adapter.get_all_resources())

    runner = RuleRunner()
    report = runner.run(resources)
    findings = report["findings"]

    engine = RiskEngine()
    engine.score_all(findings)

    print()
    print("=" * 80)
    print("🎯 RISK-ENGINE SCORED FINDINGS")
    print("=" * 80)

    # Sort by risk score descending
    findings_sorted = sorted(findings, key=lambda f: f.risk_score or 0, reverse=True)

    for i, f in enumerate(findings_sorted, 1):
        print(f"\n  [{i}] Risk Score: {f.risk_score}/100")
        print(f"      Rule     : {f.rule_name}")
        print(f"      Resource : {f.resource_id}")
        print(f"      Severity : {f.severity}")
    print()
    print("=" * 80)