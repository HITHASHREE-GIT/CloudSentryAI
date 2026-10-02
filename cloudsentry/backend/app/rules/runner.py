"""
CloudSentry AI — Rule Runner
=============================
Executes all registered rules against all normalized resources.
Produces a comprehensive scan result.

After rules run, the ML predictor assigns an ML priority to each finding.
"""

from typing import List
from app.models import CloudResource, RuleResult, Finding
from app.rules import ALL_RULES
from app.rules.base import BaseRule
import uuid


class RuleRunner:
    """Runs every rule against every resource."""

    def __init__(self):
        self.rules: List[BaseRule] = [rule_cls() for rule_cls in ALL_RULES]

    def run(self, resources: List[CloudResource]) -> dict:
        """
        Returns:
            {
              "results": [RuleResult, ...],
              "findings": [Finding, ...],
              "stats": { "total_checks": int, "passed": int, "failed": int }
            }
        """
        results: List[RuleResult] = []
        findings: List[Finding] = []

        for resource in resources:
            for rule in self.rules:
                result = rule.evaluate(resource)
                results.append(result)

                if result.status == "FAIL":
                    findings.append(self._make_finding(rule, result))

        # ─── ML predictions ───
        self._apply_ml_predictions(findings)

        total = len(results)
        failed = len(findings)
        passed = total - failed

        return {
            "results": results,
            "findings": findings,
            "stats": {
                "total_checks": total,
                "passed": passed,
                "failed": failed,
                "rules_count": len(self.rules),
                "resources_count": len(resources),
            },
        }

    def _make_finding(self, rule: BaseRule, result: RuleResult) -> Finding:
        """Convert a FAIL RuleResult into a Finding."""
        return Finding(
            finding_id=str(uuid.uuid4())[:8],
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            severity=rule.severity,
            resource_id=result.resource_id,
            resource_type=result.resource_type,
            service=self._infer_service(result),
            region="us-east-1",
            description=rule.description,
            why_dangerous=rule.why_dangerous,
            recommendation=rule.recommendation,
            evidence=result.evidence,
            reference=rule.reference,
        )

    def _infer_service(self, result: RuleResult) -> str:
        rid = result.rule_id
        if "S3" in rid or "STORAGE" in rid:
            return "s3"
        if "IAM" in rid or "MFA" in rid or "KEY" in rid or "USER" in rid:
            return "iam"
        if "SSH" in rid:
            return "ec2"
        if "CLOUDTRAIL" in rid:
            return "cloudtrail"
        return "unknown"

    def _apply_ml_predictions(self, findings: List[Finding]) -> None:
        """Attach ML-predicted priority to each finding (best-effort)."""
        try:
            from app.ml.predictor import get_predictor
            predictor = get_predictor()

            for finding in findings:
                prediction = predictor.predict(finding)
                finding.ml_priority = prediction["ml_priority"]
                finding.ml_priority_score = prediction["ml_priority_score"]
                finding.ml_confidence = prediction["ml_confidence"]
        except Exception as e:
            # ML is an additional signal — never fail the scan because of it
            print(f"[ML] Prediction skipped: {e}")


# ───────────────────────────────────────────────
# SELF-TEST: python -m app.rules.runner
# ───────────────────────────────────────────────

if __name__ == "__main__":
    from app.adapters.simulated_aws import SimulatedAWSAdapter
    from app.normalizer.normalizer import Normalizer

    adapter = SimulatedAWSAdapter()
    normalizer = Normalizer()
    resources = normalizer.normalize_all(adapter.get_all_resources())

    runner = RuleRunner()
    report = runner.run(resources)

    stats = report["stats"]
    findings = report["findings"]

    print()
    print("=" * 90)
    print("🛡️  CLOUDSENTRY SCAN RESULT (with ML predictions)")
    print("=" * 90)
    print(f"  Resources : {stats['resources_count']}")
    print(f"  Rules     : {stats['rules_count']}")
    print(f"  Checks    : {stats['total_checks']}")
    print(f"  ✅ PASSED : {stats['passed']}")
    print(f"  ❌ FAILED : {stats['failed']}")
    print("=" * 90)

    if findings:
        print()
        print(f"{'Rule':<32} {'Rule Severity':<14} {'ML Priority':<12} {'Conf':>6}")
        print("-" * 90)
        for f in findings:
            print(
                f"{(f.rule_name or '')[:30]:<32} "
                f"{f.severity:<14} "
                f"{(f.ml_priority or '—'):<12} "
                f"{(f.ml_confidence or 0):>6.3f}"
            )
        print("-" * 90)
        print(f"  Total findings: {len(findings)}")
    else:
        print("✅ No findings.")
    print()