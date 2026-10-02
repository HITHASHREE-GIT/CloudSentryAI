"""
CloudSentry AI — Rule: Root Account MFA Disabled
==================================================
Detects if the AWS root account has MFA enabled.

Note: Since our simulated environment doesn't yet have a root account JSON,
we check the IAM user 'launchnest-admin' as a proxy — this is a demo simplification.
In a real AWS scan, this would check the account's root MFA setting via IAM API.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class RootMFARule(BaseRule):
    rule_id = "ROOT_MFA_RULE"
    rule_name = "Root Account MFA Disabled"
    severity = "CRITICAL"
    description = "Detects missing MFA on the AWS root account."
    why_dangerous = (
        "The root account has unrestricted access to all AWS resources and "
        "billing. Without MFA, a stolen root password grants an attacker full control."
    )
    recommendation = (
        "Enable MFA on the root account immediately. Consider removing root "
        "access keys and using IAM roles for day-to-day operations."
    )
    reference = "CIS AWS 1.5 — Ensure MFA is enabled for the root user"

    def evaluate(self, resource: CloudResource) -> RuleResult:
        # Only check the admin identity as our root proxy
        if resource.resource_type != "IDENTITY" or resource.service != "iam":
            return self.pass_result(resource, "Not an IAM identity.")

        # Treat 'launchnest-admin' as root proxy
        if resource.resource_id != "launchnest-admin":
            return self.pass_result(resource, "Not the root/admin account.")

        raw = resource.raw
        mfa = raw.get("mfa_enabled", False)

        if not mfa:
            evidence = {
                "account": resource.resource_id,
                "mfa_enabled": False,
            }
            return self.fail_result(
                resource,
                evidence,
                reason=f"Root/admin account '{resource.resource_id}' does not have MFA enabled.",
            )

        return self.pass_result(
            resource,
            reason=f"Root/admin account '{resource.resource_id}' has MFA enabled.",
        )