"""
CloudSentry AI — Rule: Unused IAM User
=======================================
Detects IAM users that have not been active for more than 90 days.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class UnusedUserRule(BaseRule):
    rule_id = "UNUSED_USER_RULE"
    rule_name = "Unused IAM User"
    severity = "MEDIUM"
    description = "Detects IAM users inactive for over 90 days."
    why_dangerous = (
        "Unused users are stale identities that increase attack surface. "
        "If compromised, they may not be noticed because nobody monitors them."
    )
    recommendation = (
        "Disable or delete inactive users. If they need occasional access, "
        "use temporary credentials with an expiration."
    )
    reference = "CIS AWS 1.12 — Ensure credentials unused for 90 days are disabled"

    MAX_INACTIVE_DAYS = 90

    def evaluate(self, resource: CloudResource) -> RuleResult:
        if resource.resource_type != "IDENTITY" or resource.service != "iam":
            return self.pass_result(resource, "Not an IAM identity.")

        raw = resource.raw
        last_activity = raw.get("last_activity_days_ago", 0)

        if last_activity > self.MAX_INACTIVE_DAYS:
            evidence = {
                "user_name": resource.resource_id,
                "last_activity_days_ago": last_activity,
            }
            return self.fail_result(
                resource,
                evidence,
                reason=f"User '{resource.resource_id}' inactive for {last_activity} days.",
            )

        return self.pass_result(
            resource,
            reason=f"User '{resource.resource_id}' has recent activity.",
        )