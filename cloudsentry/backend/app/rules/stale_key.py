"""
CloudSentry AI — Rule: Stale Access Key
========================================
Detects IAM access keys older than 90 days.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class StaleAccessKeyRule(BaseRule):
    rule_id = "STALE_KEY_RULE"
    rule_name = "Stale IAM Access Key"
    severity = "HIGH"
    description = "Detects access keys older than the 90-day rotation policy."
    why_dangerous = (
        "Long-lived access keys increase the risk window if leaked. "
        "Many organizations require 90-day rotation for compliance."
    )
    recommendation = (
        "Rotate the access key. Prefer IAM roles with temporary credentials. "
        "Delete unused keys and enable key age monitoring."
    )
    reference = "CIS AWS 1.14 — Ensure access keys are rotated every 90 days or less"

    MAX_KEY_AGE_DAYS = 90

    def evaluate(self, resource: CloudResource) -> RuleResult:
        if resource.resource_type != "IDENTITY" or resource.service != "iam":
            return self.pass_result(resource, "Not an IAM identity.")

        raw = resource.raw
        keys = raw.get("access_keys", [])
        stale_keys = [
            k for k in keys
            if k.get("status") == "Active" and k.get("created_days_ago", 0) > self.MAX_KEY_AGE_DAYS
        ]

        if stale_keys:
            evidence = {
                "user_name": resource.resource_id,
                "stale_keys": [
                    {
                        "key_id": k.get("key_id"),
                        "created_days_ago": k.get("created_days_ago"),
                    }
                    for k in stale_keys
                ],
            }
            return self.fail_result(
                resource,
                evidence,
                reason=f"User '{resource.resource_id}' has {len(stale_keys)} key(s) older than {self.MAX_KEY_AGE_DAYS} days.",
            )

        return self.pass_result(
            resource,
            reason=f"User '{resource.resource_id}' has no stale access keys.",
        )