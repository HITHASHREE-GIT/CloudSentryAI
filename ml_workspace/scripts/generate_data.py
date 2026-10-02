"""
CloudSentry AI — Synthetic Dataset Generator
==============================================
Generates a synthetic dataset of cloud security configurations
with realistic feature distributions and priority labels.

Features:
  - public_access         : bool
  - encryption_enabled    : bool
  - logging_enabled       : bool
  - mfa_enabled           : bool
  - internet_exposed      : bool
  - iam_privilege         : int (0-3)
  - resource_criticality  : int (1-5)
  - resource_age_days     : int (1-1000)
  - change_frequency      : int (0-50)

Target:
  - priority : int (0=Low, 1=Medium, 2=High, 3=Critical)

The label is derived deterministically using realistic severity weights
that mirror CloudSentry's rule severity semantics — so a single high-impact
misconfiguration can reach HIGH, and combinations reach CRITICAL.
"""

import random
import csv
from pathlib import Path

# Reproducibility
random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "datasets"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "synthetic_configs.csv"

N_SAMPLES = 1500


def compute_priority(row: dict) -> int:
    """
    Deterministic labeling function — mirrors CloudSentry's rule severity logic.

    Each misconfiguration contributes a weighted score. Thresholds map
    the total score to a priority class:
      0 = LOW, 1 = MEDIUM, 2 = HIGH, 3 = CRITICAL
    """
    score = 0

    # ─── Public exposure (highest weight) ───
    if row["public_access"]:
        score += 40
    if row["internet_exposed"]:
        score += 20

    # ─── Identity risk ───
    if not row["mfa_enabled"]:
        score += 20
    if row["iam_privilege"] == 3:          # AdministratorAccess
        score += 40
    elif row["iam_privilege"] == 2:        # PowerUserAccess
        score += 25
    elif row["iam_privilege"] == 1:
        score += 10

    # ─── Credential / user staleness (light weight) ───
    if row["resource_age_days"] > 365:
        score += 15
    elif row["resource_age_days"] > 180:
        score += 8
    elif row["resource_age_days"] > 90:
        score += 3

    # ─── Data protection ───
    if not row["encryption_enabled"]:
        score += 25
    if not row["logging_enabled"]:
        score += 15

    # ─── Asset criticality multiplier ───
    multiplier = 1 + (row["resource_criticality"] - 3) * 0.15
    score = int(score * multiplier)

    # Clamp 0-100
    score = max(0, min(100, score))

    # ─── Map score → priority ───
    if score >= 75:
        return 3  # CRITICAL
    elif score >= 45:
        return 2  # HIGH
    elif score >= 20:
        return 1  # MEDIUM
    else:
        return 0  # LOW


def generate_row() -> dict:
    """Generate one synthetic cloud configuration."""
    return {
        "public_access": random.choice([True, False]),
        "encryption_enabled": random.choices([True, False], weights=[0.7, 0.3])[0],
        "logging_enabled": random.choices([True, False], weights=[0.75, 0.25])[0],
        "mfa_enabled": random.choices([True, False], weights=[0.65, 0.35])[0],
        "internet_exposed": random.choices([True, False], weights=[0.25, 0.75])[0],
        "iam_privilege": random.choices([0, 1, 2, 3], weights=[0.4, 0.3, 0.2, 0.1])[0],
        "resource_criticality": random.choices([1, 2, 3, 4, 5], weights=[0.15, 0.2, 0.3, 0.2, 0.15])[0],
        "resource_age_days": random.randint(1, 1000),
        "change_frequency": random.randint(0, 50),
    }


def main():
    rows = []
    for _ in range(N_SAMPLES):
        row = generate_row()
        row["priority"] = compute_priority(row)
        rows.append(row)

    # Write CSV
    fieldnames = list(rows[0].keys())
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    print(f"✅ Generated {N_SAMPLES} rows → {OUTPUT_FILE}")
    print()
    print("Label distribution:")
    from collections import Counter
    counts = Counter(r["priority"] for r in rows)
    for label in sorted(counts):
        pct = counts[label] / N_SAMPLES * 100
        bar = "█" * int(pct / 2)
        print(f"  {label} ({['LOW','MEDIUM','HIGH','CRITICAL'][label]}): "
              f"{counts[label]:4d} ({pct:5.1f}%) {bar}")
    print()
    print(f"Features: {len(fieldnames) - 1}")
    print(f"Target  : priority")


if __name__ == "__main__":
    main()