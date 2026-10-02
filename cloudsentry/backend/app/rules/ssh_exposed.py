"""
CloudSentry AI — Rule: SSH Exposed to Internet
================================================
Detects security groups allowing SSH (port 22) from 0.0.0.0/0.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class SSHExposedRule(BaseRule):
    rule_id = "SSH_EXPOSED_RULE"
    rule_name = "SSH Exposed to Internet"
    severity = "HIGH"
    description = "Detects security groups allowing SSH from anywhere on the internet."
    why_dangerous = (
        "SSH open to 0.0.0.0/0 allows brute-force attacks and unauthorized "
        "access attempts from any IP. This is one of the most scanned ports on the internet."
    )
    recommendation = (
        "Restrict SSH to known IP ranges. Use a bastion host, VPN, or AWS "
        "Systems Manager Session Manager instead of opening SSH to the world."
    )
    reference = "CIS AWS 5.2 — Ensure no security groups allow ingress from 0.0.0.0/0 to port 22"

    def evaluate(self, resource: CloudResource) -> RuleResult:
        if resource.resource_type != "NETWORK":
            return self.pass_result(resource, "Not a network resource.")

        raw = resource.raw
        for rule in raw.get("inbound_rules", []):
            if rule.get("port") == 22 and rule.get("source") == "0.0.0.0/0":
                evidence = {
                    "group_id": resource.resource_id,
                    "port": 22,
                    "source": "0.0.0.0/0",
                    "protocol": rule.get("protocol"),
                }
                return self.fail_result(
                    resource,
                    evidence,
                    reason=f"Security group '{resource.resource_id}' allows SSH from anywhere.",
                )

        return self.pass_result(
            resource,
            reason=f"Security group '{resource.resource_id}' does not expose SSH to the internet.",
        )