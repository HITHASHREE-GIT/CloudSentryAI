"""
CloudSentry AI — Configuration
================================
Central configuration for paths, API settings, and constants.

This file is imported by other modules to find:
- Where the simulated AWS JSON files live
- API metadata (title, version)
- Supported cloud providers
"""

from pathlib import Path

# ═══════════════════════════════════════════════════════
# PROJECT PATHS
# ═══════════════════════════════════════════════════════
#
# Folder layout:
#
#   CloudSentryAI/                       ← PROJECT_ROOT
#   ├── cloudsentry/
#   │   └── backend/                     ← BACKEND_DIR
#   │       └── app/                     ← APP_DIR
#   │           └── config.py            ← __file__ (this file)
#   │
#   └── launchnest/
#       └── simulated_aws/               ← SIMULATED_AWS_PATH
#           ├── s3/
#           ├── iam/
#           ├── ec2/
#           ├── rds/
#           ├── vpc/
#           └── cloudtrail/

APP_DIR = Path(__file__).resolve().parent              # .../backend/app
BACKEND_DIR = APP_DIR.parent                            # .../backend
CLOUDSENTRY_DIR = BACKEND_DIR.parent                    # .../cloudsentry
PROJECT_ROOT = CLOUDSENTRY_DIR.parent                   # .../CloudSentryAI

# Where the simulated AWS environment lives
SIMULATED_AWS_PATH = PROJECT_ROOT / "launchnest" / "simulated_aws"

# ═══════════════════════════════════════════════════════
# API METADATA
# ═══════════════════════════════════════════════════════

API_TITLE = "CloudSentry AI"
API_DESCRIPTION = "Cloud Security Posture Management (CSPM) Platform"
API_VERSION = "0.1.0"

# ═══════════════════════════════════════════════════════
# CLOUD PROVIDERS
# ═══════════════════════════════════════════════════════

# Provider currently supported by the adapter
ACTIVE_PROVIDER = "aws"

# Providers planned for future
SUPPORTED_PROVIDERS = ["aws"]        # Later: add "azure"

# ═══════════════════════════════════════════════════════
# SCANNER SETTINGS
# ═══════════════════════════════════════════════════════

# Where to look for JSON files inside simulated_aws/
SIMULATED_AWS_SERVICES = [
    "s3",
    "iam",
    "ec2",
    "rds",
    "cloudtrail",
]

# ═══════════════════════════════════════════════════════
# SEVERITY LEVELS
# ═══════════════════════════════════════════════════════

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_HIGH = "HIGH"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_LOW = "LOW"

SEVERITY_LEVELS = [
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
]

# ═══════════════════════════════════════════════════════
# DEBUG
# ═══════════════════════════════════════════════════════

DEBUG = True