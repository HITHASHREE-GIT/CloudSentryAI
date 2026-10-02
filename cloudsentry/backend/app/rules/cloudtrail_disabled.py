"""
CloudSentry AI — Rule: CloudTrail Disabled
===========================================
Detects CloudTrail trails with logging disabled.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class CloudTrailDisabledRule(BaseRule):
    rule_id = "CLOUDTRAIL_DISABLED_RULE"
    rule_name = "CloudTrail Logging Disabled"
    severity = "HIGH"
    description = "Detects CloudTrail trails that are not actively logging."
    why_dangerous = (
        "Without CloudTrail logging, security incidents can't be investigated. "
        "Attackers can operate without leaving any audit trail."
    )
    recommendation = (
        "Enable CloudTrail logging. Configure multi-region trail with log file "
        "validation and CloudWatch integration for real-time alerts."
    )
    reference = "CIS AWS 3.1 — Ensure CloudTrail is enabled in all regions"

    def evaluate(self, resource: CloudResource) -> RuleResult:
        if resource.resource_type != "LOGGING":
            return self.pass_result(resource, "Not a logging resource.")

        raw = resource.raw
        is_logging = raw.get("is_logging", False)

        if not is_logging:
            evidence = {
                "trail_name": resource.resource_id,
                "is_logging": False,
                "stop_logging_time": raw.get("stop_logging_time"),
            }
            return self.fail_result(
                resource,
                evidence,
                reason=f"CloudTrail '{resource.resource_id}' is not logging events.",
            )

        return self.pass_result(
            resource,
            reason=f"CloudTrail '{resource.resource_id}' is logging.",
        )