# 🏗️ CloudSentry AI — Architecture

Deep-dive into the system design, data flow, and component responsibilities.

---

## 1. System Overview

CloudSentry AI is a **full-stack CSPM platform** with four independent services:

| Service | Purpose | Port |
|---------|---------|------|
| CloudSentry Backend | Security scanning + rules + ML | 8001 |
| CloudSentry Frontend | Security dashboard (React) | 5173 |
| LaunchNest Backend | Customer SaaS API | 8000 |
| LaunchNest Frontend | Customer SaaS UI (React) | 5174 |

**Runtime dependency:** All four services must be running for the complete demo.

---

## 2. High-Level Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                      END USER (Browser)                          │
└────────────┬─────────────────────────────────────┬──────────────┘
             │                                     │
             │ CloudSentry UI                      │ LaunchNest UI
             ▼                                     ▼
    ┌─────────────────┐                  ┌─────────────────┐
    │ React :5173     │                  │ React :5174     │
    │ Security Dash   │                  │ Customer SaaS   │
    └────────┬────────┘                  └────────┬────────┘
             │ HTTP/JSON                          │ HTTP/JSON
             ▼                                    ▼
    ┌─────────────────┐                  ┌─────────────────┐
    │ FastAPI :8001   │                  │ FastAPI :8000   │
    │ CloudSentry API │                  │ LaunchNest API  │
    └────────┬────────┘                  └────────┬────────┘
             │                                    │
             ├─► Adapters ─► Normalizer            ├─► JWT Auth
             ├─► Rules (8)                         ├─► SQLAlchemy
             ├─► Risk Engine                       └─► SQLite DB
             └─► ML Predictor
                       │
                       ▼
             ┌─────────────────┐
             │ Simulated AWS   │
             │ (8 JSON files)  │
             │ 13 resources    │
             └─────────────────┘
3. CloudSentry — Detailed Flow
3.1 Scan Pipeline
text

POST /scan
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ 1. ADAPTER LAYER                                     │
│    - Reads JSON files from launchnest/simulated_aws/ │
│    - Returns raw dicts per service                   │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 2. NORMALIZER LAYER                                  │
│    - Converts provider-specific data                 │
│    - Into common CloudResource model                 │
│    - Generic fields: public_access, encryption, etc. │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 3. RULE ENGINE (8 rules)                             │
│    - Each rule: evaluate(resource) → PASS/FAIL       │
│    - Deterministic, testable, explainable            │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 4. RISK ENGINE                                       │
│    - Formula: severity × exposure × confidence       │
│    - Output: 0-100 score per finding                 │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 5. ML PREDICTOR                                      │
│    - Extracts 9 features per finding                 │
│    - Runs XGBoost model                              │
│    - Output: ml_priority + confidence                │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ 6. RESPONSE                                          │
│    - JSON with all findings + evidence + ML          │
└──────────────────────────────────────────────────────┘

4. Rule Engine Design
Base Rule Class

Every rule inherits from BaseRule:
python

class BaseRule(ABC):
    rule_id: str
    rule_name: str
    severity: str
    description: str
    why_dangerous: str
    recommendation: str
    reference: str

    @abstractmethod
    def evaluate(self, resource: CloudResource) -> RuleResult: ...

Rule Registry

All rules registered in app/rules/__init__.py:
python

ALL_RULES = [
    PublicS3Rule,
    ExcessiveIAMRule,
    SSHExposedRule,
    RootMFARule,
    StaleAccessKeyRule,
    UnusedUserRule,
    CloudTrailDisabledRule,
    UnencryptedStorageRule,
]

The 8 Rules
Rule ID	Detects	Severity
PUBLIC_S3_RULE	S3 with public access	CRITICAL
EXCESSIVE_IAM_RULE	AdministratorAccess/PowerUser	CRITICAL
SSH_EXPOSED_RULE	SSH 22 from 0.0.0.0/0	HIGH
ROOT_MFA_RULE	No MFA on root/admin	CRITICAL
STALE_KEY_RULE	Access keys >90 days	HIGH
UNUSED_USER_RULE	Users inactive >90 days	MEDIUM
CLOUDTRAIL_DISABLED_RULE	Logging off	HIGH
UNENCRYPTED_STORAGE_RULE	No encryption at rest	HIGH
5. Risk Engine
Formula
text

risk_score = severity_weight × exposure_weight × confidence_weight × 100

Weights

Severity:
Level	Weight
CRITICAL	1.00
HIGH	0.75
MEDIUM	0.50
LOW	0.25

Exposure:
Context	Weight
PUBLIC_INTERNET	1.00
PUBLIC_PARTIAL	0.70
INTERNAL	0.50
PRIVATE	0.30

Confidence:
Level	Weight
HIGH (deterministic)	1.00
MEDIUM	0.85
LOW	0.70
Example Calculation

Public S3 Bucket:

    Severity: CRITICAL (1.00)

    Exposure: PUBLIC_INTERNET (1.00)

    Confidence: HIGH (1.00)

    Score: 1.00 × 1.00 × 1.00 × 100 = 100

Stale Access Key:

    Severity: HIGH (0.75)

    Exposure: INTERNAL (0.50)

    Confidence: HIGH (1.00)

    Score: 0.75 × 0.50 × 1.00 × 100 = 38

6. ML Pipeline
6.1 Data Generation

ml_workspace/scripts/generate_data.py generates 1,500 synthetic cloud configs with 9 features:

    public_access (bool)

    encryption_enabled (bool)

    logging_enabled (bool)

    mfa_enabled (bool)

    internet_exposed (bool)

    iam_privilege (0-3)

    resource_criticality (1-5)

    resource_age_days (1-1000)

    change_frequency (0-50)

6.2 Label Function

Each row labeled deterministically using weighted severity logic (mirrors rule engine semantics):
python

score = 0
if public_access:      score += 40
if internet_exposed:   score += 20
if not mfa_enabled:    score += 20
if iam_privilege == 3: score += 40   # AdministratorAccess
if not encryption:     score += 25
if not logging:        score += 15
if age > 365:          score += 15

# Map score → class (0=LOW, 1=MED, 2=HIGH, 3=CRIT)

6.3 Training

ml_workspace/scripts/train_models.py:

    Trains 3 models on 80/20 split

    Compares F1, ROC-AUC

    Selects best by weighted F1

    Saves best_model.pkl

6.4 Deployed Model
Model	F1 Score
Gradient Boosting	0.896
Random Forest	0.937
XGBoost	0.940 ✅
6.5 Inference

cloudsentry/backend/app/ml/predictor.py:

    Rule-specific feature extraction

    Loads best_model.pkl + scaler.pkl

    Returns ml_priority, ml_priority_score, ml_confidence

7. LaunchNest Database Schema
Tables

users
Column	Type	Notes
user_id	INTEGER PK	Auto-increment
name	VARCHAR(100)	
email	VARCHAR(150)	Unique, indexed
password_hash	VARCHAR(255)	bcrypt
role	VARCHAR(20)	admin/developer/intern
created_at	TIMESTAMP	

projects
Column	Type	Notes
project_id	INTEGER PK	
name	VARCHAR(150)	
description	TEXT	
owner_id	FK users	
status	VARCHAR(20)	active/planning
progress	INTEGER	0-100
created_at	TIMESTAMP	

tasks
Column	Type	Notes
task_id	INTEGER PK	
project_id	FK projects	
title	VARCHAR(200)	
assigned_to	FK users	
status	VARCHAR(20)	todo/in_progress/completed
priority	VARCHAR(20)	low/medium/high

documents
Column	Type	Notes
document_id	INTEGER PK	
project_id	FK projects	
filename	VARCHAR(255)	
s3_key	VARCHAR(255)	

activity
Column	Type	Notes
activity_id	INTEGER PK	
user_id	FK users	
action	VARCHAR(255)	
timestamp	TIMESTAMP	
8. LaunchNest Authentication Flow
text

POST /api/auth/login
    │
    ├─► Verify email + password (bcrypt)
    ├─► Generate JWT (HS256, 24h expiry)
    └─► Return { access_token, user }
             │
             ▼
    Frontend stores token in localStorage
             │
             ▼
    Every subsequent request: Authorization: Bearer <token>
             │
             ▼
    Backend validates JWT → get_current_user

9. Simulated AWS Environment

Located at launchnest/simulated_aws/:
text

simulated_aws/
├── s3/                   3 S3 buckets (1 insecure)
├── iam/                  3 IAM users (2 insecure)
├── ec2/
│   ├── instances.json    2 instances (secure)
│   └── security_groups   1 insecure SG (SSH)
├── rds/                  1 database (secure)
└── cloudtrail/           1 trail (insecure)

13 resources, 7 misconfigurations → 10 findings (some resources trigger multiple rules).
10. Deployment Topology
Local Development (Current)

4 separate processes running on localhost:
text

Terminal 1: uvicorn main:app --port 8001  (CloudSentry API)
Terminal 2: npm run dev                    (CloudSentry UI)
Terminal 3: uvicorn main:app --port 8000  (LaunchNest API)
Terminal 4: npm run dev                    (LaunchNest UI)

Future Production (Proposed)

    Docker Compose for orchestration

    PostgreSQL instead of SQLite

    Redis for caching + background jobs

    Nginx as reverse proxy

    Real AWS connector using Boto3 (read-only IAM role)

    HTTPS + Let's Encrypt for TLS

    CI/CD via GitHub Actions

11. Design Decisions
Decision	Rationale
FastAPI	Type-safe, async, auto-generates OpenAPI docs
SQLite	Zero-config for demo; easy to swap for PostgreSQL
Pydantic	Runtime validation + IDE autocomplete
JWT	Stateless auth; no server-side session storage
bcrypt	Industry-standard password hashing
React + Vite	Modern frontend; fast HMR during dev
XGBoost	Won model comparison (F1=0.94)
Two frontends	Demonstrates real customer-vendor separation
Simulated AWS	Safe for demo; no AWS account needed
Rule engine first, ML second	Deterministic detection is explainable; ML is a hint
12. Future Extensions
Near-term

    Persist findings in a database (replace in-memory cache)

    Scheduled scans (cron-like background worker)

    Email/Slack alerts for critical findings

Mid-term

    Real AWS read-only connector (Boto3)

    Azure adapter (same normalization model)

    Attack path analysis

Long-term

    Multi-tenant SaaS with strict isolation

    Automated remediation with approval workflow

    Compliance reporting (CIS, NIST, SOC 2)