"""
CloudSentry AI — Rule: Unencrypted Storage
===========================================
Detects storage resources without encryption at rest enabled.
"""

from app.rules.base import BaseRule
from app.models import CloudResource, RuleResult


class UnencryptedStorageRule(BaseRule):
    rule_id = "UNENCRYPTED_STORAGE_RULE"
    rule_name = "Unencrypted Storage"
    severity = "HIGH"
    description = "Detects storage resources without encryption at rest."
    why_dangerous = (
        "Unencrypted storage exposes data if the physical media is compromised, "
        "or if an attacker gains read access to the underlying storage layer."
    )
    recommendation = (
        "Enable default encryption on the storage bucket. Use SSE-S3 or SSE-KMS. "
        "Encrypt existing objects by enabling default encryption and running a re-encryption job."
    )
    reference = "CIS AWS 2.1.1 — Ensure S3 bucket encryption is enabled"

    def evaluate(self, resource: CloudResource) -> RuleResult:
        if resource.resource_type != "STORAGE":
            return self.pass_result(resource, "Not a storage resource.")

        if resource.encryption_enabled is False:
            evidence = {
                "bucket_name": resource.resource_id,
                "encryption_enabled": False,
                "encryption": resource.raw.get("encryption"),
            }
            return self.fail_result(
                resource,
                evidence,
                reason=f"Storage '{resource.resource_id}' does not have encryption enabled.",
            )

        return self.pass_result(
            resource,
            reason=f"Storage '{resource.resource_id}' has encryption enabled.",
        )