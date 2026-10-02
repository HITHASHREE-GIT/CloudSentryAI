# 🎓 CloudSentry AI — Viva Preparation Notes

Answers to likely viva/examiner questions. Practice saying these aloud.

---

## Part 1 — Project Overview

### Q1: What is CloudSentry AI?

**A:** CloudSentry AI is a **Cloud Security Posture Management (CSPM)** platform that scans cloud environments for security misconfigurations, prioritizes findings using deterministic rules + ML, and helps organizations understand and fix their security posture.

We built it as a full-stack platform with:
- A security scanner (Python + FastAPI)
- A dashboard (React)
- A demo customer SaaS called **LaunchNest** with its own backend and frontend
- An ML pipeline that trains and compares 3 models

---

### Q2: Why did you choose CSPM as your project?

**A:** Three reasons:
1. **Relevance** — Cloud misconfigurations are one of the top causes of data breaches (per Verizon DBIR).
2. **Well-defined scope** — CSPM has clear, testable objectives (detect misconfigs) unlike vague "AI security" projects.
3. **Combines skills** — Cloud, security, backend, frontend, ML, DevOps. It's a full-stack learning journey.

---

### Q3: Who is the target customer?

**A:** Small SaaS companies and cloud-native startups (15–30 employees) that:
- Use AWS but don't have a dedicated cloud-security engineer
- Can't afford enterprise CSPM tools (Wiz, Orca, Prisma Cloud start at ~$50k/year)
- Need plain-English explanations and prioritized fixes

**Why this segment?** They're cloud-dependent but security-light. A lightweight, affordable CSPM fills a real gap.

---

### Q4: What problem does CloudSentry solve?

**A:** Small cloud teams face two problems:

1. **Visibility** — They don't know what's misconfigured across their AWS account.
2. **Prioritization** — Even when they know, there are too many findings to fix at once.

CloudSentry solves both:
- **Detection** — 8 deterministic rules aligned with CIS AWS Benchmarks
- **Prioritization** — Transparent 0-100 risk score + ML prediction
- **Explanation** — Plain-English "why dangerous" + "how to fix"

---

## Part 2 — Architecture

### Q5: Walk me through the architecture.

**A:** Four services:
CloudSentry Backend (FastAPI :8001) ← Security scanning
CloudSentry Frontend (React :5173) ← Security dashboard
LaunchNest Backend (FastAPI :8000) ← Customer SaaS API
LaunchNest Frontend (React :5174) ← Customer SaaS UI
text


**Data flow:**
1. User clicks "Scan" in CloudSentry dashboard
2. Frontend calls `POST /scan` on the backend
3. Backend reads simulated AWS from `launchnest/simulated_aws/`
4. Adapter → Normalizer → 8 Rules → Risk Engine → ML Predictor
5. Returns JSON with 10 findings
6. Frontend renders the findings table

---

### Q6: Why did you build LaunchNest as a separate app?

**A:** To make the demo realistic. Without a customer, CloudSentry would just be scanning mock JSON files.

LaunchNest gives us:
- **A concrete story** — "Here's a real SaaS company that uses AWS"
- **Realistic cloud resources** — S3, IAM, EC2, RDS tied to actual app features (projects, documents)
- **A separation of concerns** — Customer app vs Security app, like real-world SaaS
- **A demo narrative** — "LaunchNest's developer accidentally made a bucket public → CloudSentry detected it"

**In viva:** You can demonstrate BOTH apps — the customer app AND the security platform that protects it.

---

### Q7: What is the Normalizer and why does it exist?

**A:** The Normalizer converts **provider-specific data** into a **common model**.

Example:
- AWS S3 has `bucket_name`, `public_access_block`
- Azure Blob will have `container_name`, `allow_blob_public_access`

If rules talked directly to these, we'd need separate rules for each cloud.

**Solution:** The normalizer maps both to a common shape:

```python
CloudResource(
    resource_id="...",
    resource_type="STORAGE",
    provider="aws",
    public_access=True,       # ← generic field
    encryption_enabled=False, # ← generic field
    logging_enabled=False,
    ...
)

Result: Rules check resource.public_access without knowing if it's AWS or Azure. This is how CloudSentry is Azure-ready.
Q8: Why read-only access for real AWS (future)?

A: Three reasons:

    Least privilege — A monitoring tool shouldn't be able to modify customer infrastructure.

    Safety — If our credentials leak, attackers can only view, not damage.

    Trust — Customers are more willing to grant read-only access.

The roadmap: start with scheduled read-only scans; later add optional remediation with explicit approval.
Part 3 — Rules & Detection
Q9: How do rules work?

A: Each rule inherits from BaseRule and implements evaluate(resource) → RuleResult.

Example — the Public S3 rule:
python

def evaluate(self, resource):
    if resource.resource_type != "STORAGE":
        return self.pass_result(resource)
    if resource.public_access is True:
        return self.fail_result(resource, evidence={...})
    return self.pass_result(resource)

Rules are:

    Deterministic — Same input → same output

    Testable — Unit test with mock resources

    Explainable — Evidence attached to each finding

Q10: What are the 8 rules based on?

A: CIS AWS Foundations Benchmark v1.5:
Rule	CIS Control
Public S3	2.1.5
Excessive IAM	1.16
SSH exposed	5.2
Root MFA	1.5
Stale keys	1.14
Unused users	1.12
CloudTrail	3.1
Unencrypted storage	2.1.1

Every finding references its CIS control. This grounds our rules in industry-standard security guidance, not arbitrary opinions.
Q11: Why not just let ML detect everything?

A: Because deterministic rules are better for detection when the security requirement is well-defined:
Aspect	Rules	ML
Explainability	✅ Evidence-based	❌ Black box
Testability	✅ Unit tests	⚠️ Statistical
Precision on known issues	✅ 100% recall	⚠️ ~90%
Adapts to new patterns	❌ Fixed	✅ Learns

Our design:

    Rules = detection (authoritative)

    ML = prioritization (supplementary signal)

    Risk engine = quantification (0-100 score)

This division mirrors production CSPM platforms.
Part 4 — Risk Engine
Q12: How does the risk score work?

A: Formula:
text

risk_score = severity_weight × exposure_weight × confidence_weight × 100

Weights:
Severity	Weight		Exposure	Weight
CRITICAL	1.00		PUBLIC_INTERNET	1.00
HIGH	0.75		PUBLIC_PARTIAL	0.70
MEDIUM	0.50		INTERNAL	0.50
LOW	0.25		PRIVATE	0.30

Example — Public S3:

    CRITICAL (1.00) × PUBLIC_INTERNET (1.00) × HIGH (1.00) × 100 = 100/100

Example — Stale Key:

    HIGH (0.75) × INTERNAL (0.50) × HIGH (1.00) × 100 = 38/100

Why this formula? It's transparent — a reviewer can see exactly why a score is what it is. No hidden weights, no random numbers.
Q13: Is the risk score independent of severity?

A: Yes — deliberately. Severity is a fixed property of the rule (set by CIS guidelines). Risk score is computed per finding, factoring in exposure and confidence.

This separation matters:

    An internal high-severity finding may score lower than a public medium-severity one

    Users see both views: raw severity AND weighted risk

Part 5 — ML
Q14: Why did you use ML at all?

A: For prioritization — not detection.

Rules detect what's wrong. ML helps answer "what should we fix first?"

In real CSPM platforms, ML is used for:

    Anomaly detection (unusual behavior)

    Finding prioritization

    Noise reduction

    Attack path prediction

Our use case: Given a rule-based finding, ML predicts a priority class (LOW/MEDIUM/HIGH/CRITICAL), which is a supplementary signal alongside severity.
Q15: Which ML model did you use and why?

A: We tested three models and selected by measured F1:
Model	F1	Accuracy
Gradient Boosting	0.896	0.897
Random Forest	0.937	0.937
XGBoost	0.940	0.940

XGBoost won by 0.003 — a small but real margin. We didn't choose it because it's popular — we chose it because it won.

Key principle: "Model chosen by evidence, not hype."
Q16: How did you train the models?

A:

    Generated 1,500 synthetic cloud configurations with realistic feature distributions

    Labeled them deterministically using a function that mirrors our rule engine's severity logic

    Split 80/20 (train/test) with stratification

    Trained 3 models with consistent preprocessing

    Compared F1, ROC-AUC on held-out test set

    Selected XGBoost by best weighted F1

    Saved model + scaler as .pkl files

The full pipeline lives in ml_workspace/scripts/.
Q17: What features does the model use?

A: 9 features:

    public_access — bool

    encryption_enabled — bool

    logging_enabled — bool

    mfa_enabled — bool

    internet_exposed — bool

    iam_privilege — 0-3

    resource_criticality — 1-5

    resource_age_days — int

    change_frequency — int

Rule-specific extraction: Each rule sets the features that best describe its misconfiguration type. E.g., STALE_KEY_RULE sets resource_age_days from key age; EXCESSIVE_IAM_RULE sets iam_privilege.
Q18: What are the limitations of your ML model?

A: Honest limitations:

    Synthetic training data — Not labeled from real findings. Real data would improve accuracy.

    Not perfectly aligned — ML predictions match rule severity in ~70% of cases. Some rules (STALE_KEY, UNUSED_USER) have unique semantics that don't map cleanly.

    Small dataset — 1,500 rows; production would use 100k+.

    No temporal features — We don't use historical patterns.

Why this is OK: ML is a supplementary signal, not the authoritative detector. Rules remain the source of truth.

Documented as future work: Use labeled production findings to retrain.
Q19: How do you handle the ML/rules disagreement?

A: We show both to the user:
text

[CRITICAL]  [Risk 100/100]  [🤖 ML: CRITICAL 100%]

Rules = authoritative. ML = hint.

If they disagree:

    The user sees both signals

    Rules-based severity decides the finding's severity

    ML confidence shows how "sure" the model is

Real CSPM platforms use this pattern — multiple signals, transparent to the user.
Part 6 — Technology Choices
Q20: Why FastAPI over Flask or Django?

A: FastAPI gives us:

    Automatic OpenAPI docs at /docs — huge for demo

    Pydantic validation — type-safe request/response

    Async support — future-proof for concurrent scans

    Modern Python — async/await, type hints

Django would be overkill (we don't need admin UI, ORM-heavy features). Flask would need more boilerplate for validation and docs.
Q21: Why SQLite over PostgreSQL?

A: For demo simplicity:

    Zero installation

    Single-file database

    Easy to reset and reseed

    Perfect for a single-user demo

Migration to PostgreSQL is trivial — same SQLAlchemy ORM code. Just change the connection string.

In production: Definitely PostgreSQL for concurrency, reliability, and features.
Q22: Why two frontends?

A: To demonstrate product thinking:

    LaunchNest Frontend — the customer's SaaS product (project management)

    CloudSentry Frontend — the security platform's dashboard

In real life, these are different products by different companies. Separating them makes the demo realistic:

    LaunchNest's developer logs into their app

    CloudSentry's security engineer logs into their dashboard

They don't share a codebase — just like real SaaS.
Q23: Why React + Vite?

A:

    React — Component-based, huge ecosystem, industry standard

    Vite — 10x faster than Webpack, HMR out-of-the-box, modern defaults

    Vite + React = fastest dev loop for demos

Alternative (Next.js) would add SSR complexity we don't need.
Part 7 — Challenges & Learning
Q24: What was the hardest part?

A: ML label design.

We iterated 4 times on the synthetic label function because the model kept predicting LOW for HIGH-severity findings. The core challenge: translating rule semantics into numeric labels.

What we learned:

    Labels are more important than algorithms

    Feature engineering matters more than model choice on small tabular data

    "Directional correctness" is acceptable when you document limitations

Q25: What would you do differently?

A: Three things:

    Persist findings in a database — Currently the scan cache lives in memory. A real CSPM would persist findings for history/comparison.

    Use real labeled data for ML — Synthetic data is a starting point. Real findings would improve alignment.

    Start with a smaller MVP — We built 8 rules + ML + 2 frontends. A 3-rule MVP would have shipped faster and validated the concept sooner.

Q26: What did you learn from this project?

A: Five key lessons:

    Full-stack integration is hard — 4 services + shared data model + API contracts

    ML is 80% data, 20% modeling — Label quality determines results

    Architecture matters — The adapter/normalizer pattern makes Azure easy later

    Documentation compounds — Screenshots + ARCHITECTURE.md make the work presentable

    Security is not one tool — Rules + ML + risk scoring + remediation guidance = a system

Part 8 — Demo
Q27: Demo your project.

A: 5-minute flow:

    Start LaunchNest (customer SaaS) — show login hira@gmail.com / demo123

    Show LaunchNest dashboard — 12 projects, 29 tasks, 8 team members

    Switch to CloudSentry — security dashboard

    Point to security score — 52/100

    Show findings table — 10 findings sorted by risk

    Click Public S3 Bucket — show:

        CRITICAL severity + Risk 100/100 + ML CRITICAL 100%

        Evidence JSON

        Why dangerous

        Remediation

        CIS reference

    Open API docs — localhost:8001/docs

    Narrate: "CloudSentry scanned LaunchNest's cloud and found 10 misconfigurations. It's now easy to see what to fix first."

Q28: What if the demo crashes?

A: Fallbacks:

    All services documented in README.md — restart any service with 1 command

    Launcher script — launcher/start_all.bat starts everything

    Screenshots backup — 10 screenshots in docs/screenshots/ show the expected behavior

    Terminal logs — every service prints clear errors

In viva: If a service fails, restart it live and explain — this demonstrates debugging skill.
Part 9 — Advanced
Q29: How would you scale this to 10,000 customers?

A: Changes needed:

    Database: SQLite → PostgreSQL (multi-tenant)

    Queue: Add Redis + Celery for background scans

    Storage: Findings in S3/PostgreSQL, not memory

    Auth: Add OAuth/SSO for enterprise

    CSPM rules: Expand from 8 → 100+ rules

    Multi-cloud: Add Azure, GCP adapters

    Rate limiting: Per-tenant quotas

    Observability: Logging, metrics, tracing

Architecture is already prepared — the adapter pattern means new clouds don't break the core.
Q30: What about real AWS integration?

A: The roadmap (from day 1):

Phase 1 (done): Simulated AWS — safe demo
Phase 2 (future): Read-only real AWS connector

    IAM role with ReadOnlyAccess

    Boto3 to call real AWS APIs

    Same adapter interface — just swap the implementation

Data flow stays identical: Real AWS → Adapter → Normalizer → Rules → Findings.

Why read-only first? Safety + trust + least privilege.
Q31: Is this project "AI" or just "ML"?

A: ML only — deliberately.

    ✅ We use supervised ML (XGBoost) for prioritization

    ❌ We don't claim "AI" generically — no LLMs, no neural networks, no agentic behaviors

Why this restraint?

    Tree-based models are optimal for tabular security data

    Simpler models = more explainable + testable

    We avoid AI buzzword marketing

Honest positioning: CloudSentry is a rule-based CSPM with ML-prioritized findings.
Part 10 — Cheat Sheet
Numbers to Remember
Metric	Value
Simulated AWS resources	13
Security rules	8
Total checks	104
Findings detected	10
Critical findings	3
Security score	52/100
Demo users	8
Demo projects	12
Demo tasks	29
ML dataset size	1,500
XGBoost F1	0.940
Git commits	12+
URLs to Remember
Service	URL
CloudSentry UI	localhost:5173
CloudSentry API	localhost:8001/docs
LaunchNest UI	localhost:5174
LaunchNest API	localhost:8000/docs
Login Credentials
text

hira@gmail.com
demo123

The 8 Rules (memorize)

    Public S3 Bucket (CRITICAL)

    Excessive IAM (CRITICAL)

    SSH Exposed (HIGH)

    Root MFA Disabled (CRITICAL)

    Stale Access Key (HIGH)

    Unused IAM User (MEDIUM)

    CloudTrail Disabled (HIGH)

    Unencrypted Storage (HIGH)

Practice Tips

    Read these aloud before the viva

    Record yourself answering 5 random questions

    Time yourself — aim for 30 seconds per answer

    Be honest about limitations — it shows maturity

    If you don't know, say: "I'd need to check the code, but my understanding is..."

