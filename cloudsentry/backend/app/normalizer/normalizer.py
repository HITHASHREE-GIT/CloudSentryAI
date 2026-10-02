"""
CloudSentry AI — Normalizer
============================
Converts raw provider-specific data (from adapters) into the common
CloudResource model that rules understand.

Why this exists:
- AWS S3 has "bucket_name"; Azure Blob has "container_name"
- Rules shouldn't care about these differences
- The normalizer provides one common shape: CloudResource

Every resource ends up with generic fields like:
- public_access : bool
- encryption_enabled : bool
- logging_enabled : bool
"""

from typing import Any
from app.models import CloudResource


class Normalizer:
    """
    Converts raw AWS JSON into CloudResource objects.
    One method per service, plus a top-level orchestrator.
    """

    def __init__(self, provider: str = "aws"):
        self.provider = provider

    # ───────────────────────────────────────────────
    # S3 BUCKETS
    # ───────────────────────────────────────────────

    def normalize_s3(self, raw: dict) -> CloudResource:
        """Convert a raw S3 bucket dict to a CloudResource."""
        return CloudResource(
            resource_id=raw.get("bucket_name", "unknown-bucket"),
            resource_type="STORAGE",
            provider=self.provider,
            service="s3",
            region=raw.get("region", "us-east-1"),
            public_access=not raw.get("public_access_block", True),
            encryption_enabled=bool(raw.get("encryption", {}).get("enabled", False)),
            logging_enabled=bool(raw.get("logging", {}).get("enabled", False)),
            raw=raw,
            tags=raw.get("tags", {}),
        )

    # ───────────────────────────────────────────────
    # IAM USERS
    # ───────────────────────────────────────────────

    def normalize_iam_user(self, raw: dict) -> CloudResource:
        """Convert a raw IAM user dict to a CloudResource."""
        # Detect excessive privileges: any attached policy in this list
        excessive_policies = {"AdministratorAccess", "PowerUserAccess"}
        has_excessive = any(
            p.get("policy_name") in excessive_policies
            for p in raw.get("attached_policies", [])
        )

        return CloudResource(
            resource_id=raw.get("user_name", "unknown-user"),
            resource_type="IDENTITY",
            provider=self.provider,
            service="iam",
            region=raw.get("region", "global"),
            public_access=False,          # IAM users aren't "public"
            encryption_enabled=None,      # N/A for IAM
            logging_enabled=None,         # N/A for IAM
            mfa_enabled=raw.get("mfa_enabled", False),
            raw=raw,
            tags=raw.get("tags", {}) | {"has_excessive_policy": str(has_excessive)},
        )

    # ───────────────────────────────────────────────
    # EC2 INSTANCES
    # ───────────────────────────────────────────────

    def normalize_ec2_instance(self, raw: dict) -> CloudResource:
        """Convert a raw EC2 instance dict to a CloudResource."""
        return CloudResource(
            resource_id=raw.get("instance_id", "unknown-instance"),
            resource_type="COMPUTE",
            provider=self.provider,
            service="ec2",
            region=raw.get("region", "us-east-1"),
            public_access=bool(raw.get("public_ip")),  # Has public IP?
            encryption_enabled=all(
                vol.get("encrypted", False) for vol in raw.get("ebs_volumes", [])
            ) if raw.get("ebs_volumes") else None,
            logging_enabled=bool(raw.get("monitoring", {}).get("detailed", False)),
            raw=raw,
            tags=raw.get("tags", {}),
        )

    # ───────────────────────────────────────────────
    # SECURITY GROUPS
    # ───────────────────────────────────────────────

    def normalize_security_group(self, raw: dict) -> CloudResource:
        """
        Convert a raw security group dict to a CloudResource.
        We flag "public_access" if SSH (22) is open to 0.0.0.0/0.
        """
        ssh_open = False
        for rule in raw.get("inbound_rules", []):
            if (
                rule.get("port") == 22
                and rule.get("source") == "0.0.0.0/0"
            ):
                ssh_open = True
                break

        return CloudResource(
            resource_id=raw.get("group_id", "unknown-sg"),
            resource_type="NETWORK",
            provider=self.provider,
            service="ec2",
            region=raw.get("region", "us-east-1"),
            public_access=ssh_open,
            encryption_enabled=None,
            logging_enabled=None,
            raw=raw,
            tags=raw.get("tags", {}),
        )

    # ───────────────────────────────────────────────
    # RDS DATABASES
    # ───────────────────────────────────────────────

    def normalize_rds(self, raw: dict) -> CloudResource:
        """Convert a raw RDS database dict to a CloudResource."""
        return CloudResource(
            resource_id=raw.get("db_identifier", "unknown-db"),
            resource_type="DATABASE",
            provider=self.provider,
            service="rds",
            region=raw.get("region", "us-east-1"),
            public_access=raw.get("publicly_accessible", False),
            encryption_enabled=raw.get("storage_encrypted", False),
            logging_enabled=bool(raw.get("logging", {})),
            raw=raw,
            tags=raw.get("tags", {}),
        )

    # ───────────────────────────────────────────────
    # CLOUDTRAIL
    # ───────────────────────────────────────────────

    def normalize_cloudtrail(self, raw: dict) -> CloudResource:
        """Convert a raw CloudTrail trail dict to a CloudResource."""
        return CloudResource(
            resource_id=raw.get("trail_name", "unknown-trail"),
            resource_type="LOGGING",
            provider=self.provider,
            service="cloudtrail",
            region=raw.get("region", "us-east-1"),
            public_access=False,
            encryption_enabled=bool(raw.get("kms_key_id")),
            logging_enabled=raw.get("is_logging", False),
            raw=raw,
            tags=raw.get("tags", {}),
        )

    # ───────────────────────────────────────────────
    # ORCHESTRATOR — normalizes everything from the adapter
    # ───────────────────────────────────────────────

    def normalize_all(self, raw_data: dict[str, list[dict]]) -> list[CloudResource]:
        """
        Takes the output of adapter.get_all_resources()
        and returns a flat list of CloudResource objects.
        """
        resources: list[CloudResource] = []

        for bucket in raw_data.get("s3", []):
            resources.append(self.normalize_s3(bucket))

        for user in raw_data.get("iam", []):
            resources.append(self.normalize_iam_user(user))

        for instance in raw_data.get("ec2", []):
            resources.append(self.normalize_ec2_instance(instance))

        for sg in raw_data.get("security_groups", []):
            resources.append(self.normalize_security_group(sg))

        for db in raw_data.get("rds", []):
            resources.append(self.normalize_rds(db))

        for trail in raw_data.get("cloudtrail", []):
            resources.append(self.normalize_cloudtrail(trail))

        return resources


# ───────────────────────────────────────────────
# SELF-TEST: python -m app.normalizer.normalizer
# ───────────────────────────────────────────────

if __name__ == "__main__":
    from app.adapters.simulated_aws import SimulatedAWSAdapter

    adapter = SimulatedAWSAdapter()
    normalizer = Normalizer()

    raw = adapter.get_all_resources()
    normalized = normalizer.normalize_all(raw)

    print("🔄 Normalized CloudResources")
    print("=" * 60)
    for r in normalized:
        flags = []
        if r.public_access is True:
            flags.append("PUBLIC")
        if r.encryption_enabled is False:
            flags.append("NO-ENC")
        if r.logging_enabled is False:
            flags.append("NO-LOG")
        if r.mfa_enabled is False:
            flags.append("NO-MFA")

        flag_str = f"  ⚠️  {', '.join(flags)}" if flags else "  ✅"
        print(f"  {r.service:15s} | {r.resource_type:10s} | {r.resource_id:35s}{flag_str}")

    print("=" * 60)
    print(f"  Total: {len(normalized)} normalized resources")