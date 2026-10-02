# 🛡️ CloudSentry AI

> **A lightweight Cloud Security Posture Management (CSPM) platform for small SaaS companies.**

---

## 📌 What Is This Project?

CloudSentry AI is a Cloud Security Posture Management platform that:

- 🔍 **Discovers** AWS cloud resources (S3, IAM, EC2, RDS, CloudTrail, VPC)
- ⚙️ **Collects** security-relevant configuration
- 📏 **Evaluates** deterministic security rules (CIS/NIST-aligned)
- 🎯 **Prioritizes** findings using a transparent risk engine + ML
- 📊 **Displays** actionable findings with evidence and remediation
- 🏢 **Supports** real customer scenarios (see LaunchNest demo below)

---

## 🏢 Demo Customer: LaunchNest

To make the project realistic, we built a **simulated small SaaS customer** called **LaunchNest**:

| Attribute | Value |
|-----------|-------|
| **Type** | Small SaaS / Cloud Startup |
| **Size** | 15–30 employees |
| **Cloud** | AWS |
| **Product** | Online project-management platform |
| **Security Team** | None (no dedicated cloud-security engineer) |

LaunchNest uses AWS for:
- 🗄️ S3 (documents, backups)
- 💻 EC2 (web/API servers)
- 🗃️ RDS (customer database)
- 🔐 IAM (users, roles, policies)
- 📜 CloudTrail (audit logs)

CloudSentry AI scans LaunchNest's **simulated AWS environment** to detect misconfigurations.

---

## 🏗️ Architecture

```text
                    OUR COMPLETE DEMO
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
      🏢 LaunchNest                 🛡️ CloudSentry AI
      Customer SaaS                Security Platform
             │                           │
             ▼                           ▼
      Simulated AWS  ────────→  Scanner + Rules + Risk
             │                           │
             └─────────────┬─────────────┘
                           ▼
                    Findings Dashboard
Project Structure
CloudSentryAI/
├── cloudsentry/          🛡️ Security platform
│   ├── backend/          FastAPI + rules + ML
│   └── frontend/         React dashboard
│
├── launchnest/           🏢 Customer SaaS demo
│   ├── backend/          FastAPI
│   ├── frontend/         React
│   └── simulated_aws/    JSON cloud resources
│
├── ml_workspace/         🧠 ML development
│   ├── datasets/         CSV datasets
│   ├── models/           Trained models
│   ├── notebooks/        Jupyter experiments
│   └── scripts/          Training scripts
│
├── docs/                 📚 Documentation
├── launcher/             ⚡ Helper scripts
└── README.md             📖 This file
🛠️ Tech Stack
Layer	Technology
Backend	Python 3.11 + FastAPI
Frontend	React 18 + Vite
Database	SQLite (dev) → PostgreSQL (prod)
ML	scikit-learn, XGBoost, Pandas
Cloud SDK	Boto3 (future real AWS)
Auth	JWT + bcrypt
Version Control	Git + GitHub
🎯 Initial Security Rules (8 Checks)
#	Rule	Severity
1	Public S3 Bucket	🔴 Critical
2	Excessive IAM Permissions	🔴 Critical
3	SSH Exposed to Internet	🟠 High
4	Root MFA Disabled	🔴 Critical
5	Stale IAM Access Key	🟠 High
6	Unused IAM User	🟡 Medium
7	CloudTrail Disabled	🟠 High
8	Unencrypted Storage	🟠 High
🚦 Status
Phase	Status
Foundation (folders, Git)	✅ Complete
Simulated AWS JSON	⏳ Next
CloudSentry Backend	⏳ Pending
CloudSentry Frontend	⏳ Pending
LaunchNest Backend	⏳ Pending
LaunchNest Frontend	⏳ Pending
ML Workspace	⏳ Pending
Documentation	⏳ Pending
📚 Documentation

Detailed docs live in docs/:

    Architecture overview

    Database schema

    API endpoints

    Viva preparation notes

⚠️ Important Notes

    Simulated AWS — This project uses a simulated AWS environment (JSON files). It is NOT connected to a real AWS account yet.

    Read-only design — Future real AWS integration uses read-only access only.

    ML role — ML is used for prioritization, not as the sole detection layer.

    Rule-based core — Security rules remain the deterministic primary detection layer.

🏆 Final Goal
text

Scratch 0 → Builder → Cloud Security Developer → CSPM Project Hero

One checkbox at a time. ✅