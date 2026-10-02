"""
CloudSentry AI — Base Rule
==========================
Every security rule inherits from BaseRule.
This enforces a consistent interface: evaluate(resource) → RuleResult.
"""

from abc import ABC, abstractmethod
from app.models import CloudResource, RuleResult


class BaseRule(ABC):
    """
    Abstract base class for all security rules.

    Subclasses must define:
      - rule_id       (e.g., "PUBLIC_S3_RULE")
      - rule_name     (e.g., "Public S3 Bucket")
      - severity      ("CRITICAL", "HIGH", "MEDIUM", "LOW")
      - description   (what it checks)
      - why_dangerous (impact)
      - recommendation (how to fix)
      - reference     (CIS/NIST citation)

    And implement:
      - evaluate(resource) → RuleResult
    """

    rule_id: str = "BASE_RULE"
    rule_name: str = "Base Rule"
    severity: str = "MEDIUM"
    description: str = ""
    why_dangerous: str = ""
    recommendation: str = ""
    reference: str = ""

    @abstractmethod
    def evaluate(self, resource: CloudResource) -> RuleResult:
        """Return a RuleResult with status PASS or FAIL."""
        raise NotImplementedError

    # ───────────────────────────────────────────────
    # Helper: quickly build PASS result
    # ───────────────────────────────────────────────

    def pass_result(self, resource: CloudResource, reason: str = "") -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            status="PASS",
            severity=self.severity,
            evidence={},
            reason=reason or "Resource passed the check.",
        )

    # ───────────────────────────────────────────────
    # Helper: quickly build FAIL result
    # ───────────────────────────────────────────────

    def fail_result(self, resource: CloudResource, evidence: dict, reason: str = "") -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            status="FAIL",
            severity=self.severity,
            evidence=evidence,
            reason=reason or self.why_dangerous,
        )