"""
CloudSentry AI — Simulated AWS Adapter
=======================================
Reads the local simulated AWS environment (JSON files inside
`launchnest/simulated_aws/`) and returns raw provider data.

This is the "cloud connector" for the demo.
Later, a real AWS adapter using Boto3 will implement the same interface.
"""

import json
from pathlib import Path
from typing import Any

from app.config import SIMULATED_AWS_PATH, SIMULATED_AWS_SERVICES


class SimulatedAWSAdapter:
    """
    Reads JSON files from the simulated AWS environment.

    Each public method returns a list of raw dicts — one per resource.
    """

    def __init__(self, base_path: Path = SIMULATED_AWS_PATH):
        self.base_path = base_path

    # ───────────────────────────────────────────────
    # INTERNAL HELPERS
    # ───────────────────────────────────────────────

    def _load_json(self, file_path: Path) -> Any:
        """Load a JSON file, return empty list if missing."""
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_service_folder(self, service: str) -> dict[str, Any]:
        """Load all JSON files in a service folder, keyed by filename."""
        service_path = self.base_path / service
        if not service_path.exists():
            return {}

        loaded: dict[str, Any] = {}
        for file in sorted(service_path.glob("*.json")):
            loaded[file.name] = self._load_json(file)
        return loaded

    # ───────────────────────────────────────────────
    # PUBLIC METHODS — one per AWS service
    # ───────────────────────────────────────────────

    def get_s3_buckets(self) -> list[dict]:
        """Return a list of raw S3 bucket dicts."""
        service = self._load_service_folder("s3")
        return list(service.values())

    def get_iam_users(self) -> list[dict]:
        """Return raw IAM users (users.json is already a list)."""
        users = self._load_json(self.base_path / "iam" / "users.json")
        return users if isinstance(users, list) else []

    def get_ec2_instances(self) -> list[dict]:
        """Return raw EC2 instances."""
        data = self._load_json(self.base_path / "ec2" / "instances.json")
        return data if isinstance(data, list) else []

    def get_security_groups(self) -> list[dict]:
        """Return raw security groups."""
        data = self._load_json(self.base_path / "ec2" / "security_groups.json")
        return data if isinstance(data, list) else []

    def get_rds_databases(self) -> list[dict]:
        """Return raw RDS databases."""
        data = self._load_json(self.base_path / "rds" / "databases.json")
        return data if isinstance(data, list) else []

    def get_cloudtrail_trails(self) -> list[dict]:
        """Return raw CloudTrail trails."""
        data = self._load_json(self.base_path / "cloudtrail" / "trails.json")
        return data if isinstance(data, list) else []

    # ───────────────────────────────────────────────
    # CONVENIENCE — collect everything
    # ───────────────────────────────────────────────

    def get_all_resources(self) -> dict[str, list[dict]]:
        """Return a dict of every supported service and its raw resources."""
        return {
            "s3": self.get_s3_buckets(),
            "iam": self.get_iam_users(),
            "ec2": self.get_ec2_instances(),
            "security_groups": self.get_security_groups(),
            "rds": self.get_rds_databases(),
            "cloudtrail": self.get_cloudtrail_trails(),
        }

    def count_resources(self) -> dict[str, int]:
        """Return a count of resources per service (for reporting)."""
        all_res = self.get_all_resources()
        return {service: len(items) for service, items in all_res.items()}


# ───────────────────────────────────────────────
# QUICK SELF-TEST (run with: python -m app.adapters.simulated_aws)
# ───────────────────────────────────────────────

if __name__ == "__main__":
    adapter = SimulatedAWSAdapter()
    counts = adapter.count_resources()

    print("📂 Simulated AWS Environment")
    print("=" * 40)
    for service, count in counts.items():
        print(f"  {service:18s} → {count} resources")
    print("=" * 40)
    print(f"  TOTAL            → {sum(counts.values())} resources")