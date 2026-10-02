"""
CloudSentry AI — Data Models
==============================
Pydantic models describing the core objects used by CloudSentry.

Models:
- CloudResource    : a normalized representation of a cloud resource
- Finding          : a security issue discovered by a rule
- RuleResult       : the PASS/FAIL output from evaluating a single rule
- ScanSummary      : summary of an entire scan
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════
# NORMALIZED CLOUD RESOURCE
# ═══════════════════════════════════════════════════════

class CloudResource(BaseModel):
    """
    A normalized representation of a cloud resource.

    The adapter fetches raw provider data (S3 JSON, IAM JSON).
    The normalizer converts it into this common model.
    Rules only see this model — never provider-specific fields.
    """

    resource_id: str = Field(..., description="Unique identifier (e.g., bucket name, user name)")
    resource_type: str = Field(..., description="Generic type: STORAGE, IDENTITY, COMPUTE, DATABASE, LOGGING, NETWORK")
    provider: str = Field(..., description="Cloud provider: aws, azure")
    service: str = Field(..., description="Service name: s3, iam, ec2, rds, cloudtrail")
    region: str = Field(default="us-east-1", description="Cloud region")

    # Security-relevant attributes (generic across providers)
    public_access: Optional[bool] = Field(None, description="Is the resource publicly accessible?")
    encryption_enabled: Optional[bool] = Field(None, description="Is encryption at rest enabled?")
    logging_enabled: Optional[bool] = Field(None, description="Is audit logging enabled?")
    mfa_enabled: Optional[bool] = Field(None, description="Is MFA enabled (identity resources)?")

    # Original provider-specific fields (for evidence & audit)
    raw: dict[str, Any] = Field(default_factory=dict, description="Original provider data")

    # Metadata
    tags: dict[str, str] = Field(default_factory=dict, description="Resource tags")


# ═══════════════════════════════════════════════════════
# RULE EVALUATION RESULT
# ═══════════════════════════════════════════════════════

class RuleResult(BaseModel):
    """
    The result of running a single security rule against a single resource.
    Status is PASS or FAIL. Additional details explain why.
    """

    rule_id: str = Field(..., description="Rule identifier, e.g., PUBLIC_S3_RULE")
    rule_name: str = Field(..., description="Human-readable rule name")
    resource_id: str = Field(..., description="Resource that was checked")
    resource_type: str = Field(..., description="Resource type")
    status: str = Field(..., description="PASS or FAIL")
    severity: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Proof of the finding")
    reason: str = Field(default="", description="Explanation of why it passed or failed")


# ═══════════════════════════════════════════════════════
# FINDING
# ═══════════════════════════════════════════════════════

class Finding(BaseModel):
    """
    A security finding — produced when a rule fails.
    Findings are what users see on the dashboard.
    """

    finding_id: str = Field(..., description="Unique finding ID")
    rule_id: str = Field(..., description="Rule that detected this")
    rule_name: str = Field(..., description="Human-readable rule name")
    severity: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")

    resource_id: str = Field(..., description="Affected resource")
    resource_type: str = Field(..., description="Resource type")
    service: str = Field(..., description="AWS service: s3, iam, ec2 ...")
    region: str = Field(default="us-east-1")

    description: str = Field(..., description="What was detected")
    why_dangerous: str = Field(..., description="Why this is a security issue")
    recommendation: str = Field(..., description="How to fix it")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Raw evidence")

    reference: str = Field(default="", description="CIS/NIST reference")

    # Risk score is filled in later by the risk engine
    risk_score: Optional[int] = Field(None, ge=0, le=100)

    # ML prediction (filled in by predictor)
    ml_priority: Optional[str] = Field(None, description="ML-predicted priority: LOW, MEDIUM, HIGH, CRITICAL")
    ml_priority_score: Optional[int] = Field(None, ge=0, le=3, description="ML priority as int: 0-3")
    ml_confidence: Optional[float] = Field(None, ge=0, le=1, description="ML confidence score")

    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ═══════════════════════════════════════════════════════
# SCAN SUMMARY
# ═══════════════════════════════════════════════════════

class ScanSummary(BaseModel):
    """
    High-level summary returned after a scan completes.
    """

    scan_id: str
    started_at: str
    finished_at: str

    total_resources: int
    total_rules: int
    total_checks: int          # resources × rules

    passed: int
    failed: int

    findings: list[Finding] = Field(default_factory=list)

    severity_counts: dict[str, int] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════
# API RESPONSE WRAPPERS
# ═══════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    """Response for GET /health"""
    status: str
    service: str
    version: str


class ScanRequest(BaseModel):
    """Optional body for POST /scan"""
    provider: str = Field(default="aws", description="Cloud provider to scan")
    services: Optional[list[str]] = Field(default=None, description="Limit to specific services")


class ScanResponse(BaseModel):
    """Response for POST /scan"""
    scan_id: str
    status: str
    summary: ScanSummary