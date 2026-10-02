"""
CloudSentry AI — Rule Runner
=============================
Executes all registered rules against all normalized resources.
Produces a comprehensive scan result.
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
    print("=" * 70)
    print("🛡️  CLOUDSENTRY SCAN RESULT")
    print("=" * 70)
    print(f"  Resources scanned : {stats['resources_count']}")
    print(f"  Rules evaluated   : {stats['rules_count']}")
    print(f"  Total checks      : {stats['total_checks']}")
    print(f"  ✅ PASSED         : {stats['passed']}")
    print(f"  ❌ FAILED         : {stats['failed']}")
    print("=" * 70)
    print()

    if findings:
        print("🚨 FINDINGS:")
        print("-" * 70)
        for i, f in enumerate(findings, 1):
            print(f"\n  [{i}] {f.severity} — {f.rule_name}")
            print(f"      Resource  : {f.resource_id}")
            print(f"      Service   : {f.service}")
            print(f"      Evidence  : {f.evidence}")
            print(f"      Fix       : {f.recommendation[:70]}...")
        print()
        print("-" * 70)
        print(f"  Total findings: {len(findings)}")
    else:
        print("✅ No findings — all resources passed.")

    print()