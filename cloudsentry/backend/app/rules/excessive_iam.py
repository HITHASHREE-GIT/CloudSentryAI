"""
CloudSentry AI — Rule: Excessive IAM Permissions
==================================================
Detects IAM users with overly broad permissions like AdministratorAccess
or PowerUserAccess.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class ExcessiveIAMRule(BaseRule):
    rule_id = "EXCESSIVE_IAM_RULE"
    rule_name = "Excessive IAM Permissions"
    severity = "CRITICAL"
    description = "Detects IAM users with overly broad permissions."
    why_dangerous = (
        "Users with AdministratorAccess or PowerUserAccess can modify any "
        "resource. If their credentials are compromised, the attacker gets "
        "full control of the AWS account."
    )
    recommendation = (
        "Apply least privilege. Replace AdministratorAccess with a scoped "
        "policy. Use IAM roles and temporary credentials instead of long-lived users."
    )
    reference = "CIS AWS 1.16 — Ensure IAM policies are attached only to groups or roles"

    EXCESSIVE_POLICIES = {"AdministratorAccess", "PowerUserAccess"}

    def evaluate(self, resource: CloudResource) -> RuleResult:
        if resource.resource_type != "IDENTITY" or resource.service != "iam":
            return self.pass_result(resource, "Not an IAM resource.")

        raw = resource.raw
        policies = raw.get("attached_policies", [])
        bad_policies = [
            p.get("policy_name") for p in policies
            if p.get("policy_name") in self.EXCESSIVE_POLICIES
        ]

        if bad_policies:
            evidence = {
                "user_name": resource.resource_id,
                "excessive_policies": bad_policies,
            }
            return self.fail_result(
                resource,
                evidence,
                reason=f"User '{resource.resource_id}' has excessive policies: {bad_policies}",
            )

        return self.pass_result(
            resource,
            reason=f"User '{resource.resource_id}' has appropriately scoped policies.",
        )