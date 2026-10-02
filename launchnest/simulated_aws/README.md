# 🌩️ LaunchNest — Simulated AWS Environment

> **This is a FAKE AWS environment for demo purposes only.**
> It is NOT connected to a real AWS account.

---

## 📌 Purpose

This folder contains **JSON files** that simulate the AWS cloud environment of our demo customer **LaunchNest**.

CloudSentry AI reads these files (instead of calling real AWS APIs) to detect security misconfigurations.

---

## 📁 Structure

```text
simulated_aws/
├── s3/                 S3 buckets
├── iam/                IAM users, roles, policies
├── ec2/                EC2 instances, security groups
├── rds/                RDS databases
├── vpc/                VPCs, subnets, route tables
└── cloudtrail/         CloudTrail audit trails
🎯 Files Overview
File	Resource	Status	Findings
s3/launchnest-documents.json	Documents bucket	✅ Secure	0
s3/launchnest-backups.json	Backups bucket	✅ Secure	0
s3/launchnest-public-assets.json	Public assets bucket	❌ Insecure	1
iam/users.json	IAM users	❌ Insecure	4
ec2/instances.json	EC2 instances	✅ Secure	0
ec2/security_groups.json	Security groups	❌ Insecure	1
rds/databases.json	RDS database	✅ Secure	0
cloudtrail/trails.json	CloudTrail trail	❌ Insecure	1

Expected Total Findings: 7 (Rule 8 adds 1 more)
🚨 Intentional Misconfigurations
#	Resource	Issue	Rule
1	launchnest-public-assets	Public access enabled, no encryption	Rule 1 + Rule 8
2	launchnest-admin (IAM)	Has AdministratorAccess	Rule 2
3	Root account	MFA disabled	Rule 4
4	launchnest-developer	Access key 400 days old	Rule 5
5	launchnest-intern	500 days inactive	Rule 6
6	sg-web	SSH (port 22) open to 0.0.0.0/0	Rule 3
7	launchnest-trail	CloudTrail logging disabled	Rule 7
🔗 How CloudSentry Uses These Files
text

CloudSentry Scanner
        ↓
Reads JSON files (simulated AWS API responses)
        ↓
Normalizes to common data model
        ↓
Runs security rules
        ↓
Generates findings
        ↓
Calculates risk scores
        ↓
Displays on dashboard

⚠️ Important Notes

    NOT real AWS — This is local simulation only

    No credentials needed — Files are read locally

    Safe to modify — Change files to test edge cases

    Version controlled — Git tracks every change

    For education/demo — Not for production use

🔮 Future: Real AWS

In Phase 19 of the roadmap, this simulated environment will be replaced by a real AWS read-only connection using Boto3.

The scanner interface will remain the same — only the adapter changes.