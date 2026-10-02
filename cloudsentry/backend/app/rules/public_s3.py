"""
CloudSentry AI — Rule: Public S3 Bucket
========================================
Detects S3 storage buckets that allow public access.

This is the FIRST and most critical rule in CloudSentry.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class PublicS3Rule(BaseRule):
    """Detects storage resources with public access enabled."""

    rule_id = "PUBLIC_S3_RULE"
    rule_name = "Public S3 Bucket"
    severity = "CRITICAL"
    description = "Detects S3 storage buckets that are publicly accessible."
    why_dangerous = (
        "Public S3 buckets can expose sensitive files to anyone on the internet. "
        "This is one of the most common causes of cloud data breaches."
    )
    recommendation = (
        "Enable 'Block Public Access' on the bucket. Review the bucket policy "
        "and ACL. If public access is truly required, restrict it to specific "
        "IP ranges or use CloudFront with signed URLs."
    )
    reference = "CIS AWS 2.1.5 — Ensure S3 Block Public Access is enabled"

    def evaluate(self, resource: CloudResource) -> RuleResult:
        # Only check STORAGE resources on AWS
        if resource.resource_type != "STORAGE":
            return self.pass_result(resource, "Not a storage resource.")

        if resource.public_access is True:
            evidence = {
                "public_access": True,
                "bucket_name": resource.resource_id,
                "raw_acl": resource.raw.get("acl"),
                "public_access_block": resource.raw.get("public_access_block"),
            }
            return self.fail_result(
                resource,
                evidence,
                reason=(
                    f"Bucket '{resource.resource_id}' has public access enabled. "
                    "Data may be exposed to unauthorized parties."
                ),
            )

        return self.pass_result(
            resource,
            reason=f"Bucket '{resource.resource_id}' has public access blocked.",
        )


# ───────────────────────────────────────────────
# SELF-TEST: python -m app.rules.public_s3
# ───────────────────────────────────────────────

if __name__ == "__main__":
    from app.adapters.simulated_aws import SimulatedAWSAdapter
    from app.normalizer.normalizer import Normalizer

    adapter = SimulatedAWSAdapter()
    normalizer = Normalizer()
    resources = normalizer.normalize_all(adapter.get_all_resources())

    rule = PublicS3Rule()
    print(f"📏 Running rule: {rule.rule_id}")
    print("=" * 70)

    findings_count = 0
    for r in resources:
        result = rule.evaluate(r)
        icon = "❌" if result.status == "FAIL" else "✅"
        print(f"  {icon}  {result.status:4s} | {r.service:10s} | {r.resource_id}")
        if result.status == "FAIL":
            findings_count += 1
            print(f"         └─ {result.reason}")
            print(f"         └─ evidence: {result.evidence}")

    print("=" * 70)
    print(f"  Findings: {findings_count}")