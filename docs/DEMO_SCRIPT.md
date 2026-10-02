# 🎬 CloudSentry AI — Demo Script

A 5-minute walkthrough of the complete project. Practice until it's smooth.

---

## Before You Start (Setup)

### 1. Start all 4 services

Double-click `launcher/start_all.bat` (or start manually):

```bash
# Terminal 1 - CloudSentry Backend
cd cloudsentry/backend && venv\Scripts\activate && uvicorn main:app --reload --port 8001

# Terminal 2 - CloudSentry Frontend
cd cloudsentry/frontend && npm run dev

# Terminal 3 - LaunchNest Backend
cd launchnest/backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000

# Terminal 4 - LaunchNest Frontend
cd launchnest/frontend && npm run dev
2. Verify all 4 services are up
bash

curl http://localhost:8001/health   # CloudSentry API
curl http://localhost:8000/health   # LaunchNest API

3. Open browser tabs (in order)
Tab	URL
1	http://localhost:5174 (LaunchNest)
2	http://localhost:5173 (CloudSentry)
3	http://localhost:8001/docs (CloudSentry API)
4. Close unrelated windows

    Minimize email, chat, music

    Zoom browser to 100%

    Full-screen the browser for the demo

🎬 The Demo (5 Minutes)
Minute 0–1: Introduce the Problem

Say:

    "I built CloudSentry AI — a Cloud Security Posture Management platform for small SaaS companies. My demo customer is a fictional company called LaunchNest — a 20-person startup that uses AWS for their project-management SaaS but has no dedicated security team."

Then:

    "CloudSentry scans their AWS environment, finds misconfigurations, prioritizes them, and tells them exactly what to fix first."

Minute 1–2: Show the Customer (LaunchNest)

Switch to Tab 1 (http://localhost:5174)

Say:

    "This is LaunchNest — the customer's SaaS app. It's a project-management platform with 12 projects, 29 tasks, and 8 team members."

Do:

    Point at the dashboard stats

    Show the Projects page briefly (click sidebar)

    Show the Team page briefly

Say:

    "LaunchNest uses AWS for storage, compute, databases, and identity. CloudSentry scans that AWS environment."

Minute 2–3: Switch to CloudSentry (Security Dashboard)

Switch to Tab 2 (http://localhost:5173)

Say:

    "This is CloudSentry's dashboard — the security platform. Here's LaunchNest's security posture."

Point at:

    Security Score: 52/100 — "Over half their controls are misconfigured."

    Findings by severity chart:

        🔴 3 critical

        🟠 5 high

        🟡 2 medium

    Top 5 Risks panel — "Sorted by weighted risk score. Public S3 bucket is at 100 — highest priority."

Say:

    "Let's open the top finding."

Minute 3–4: Deep-Dive into a Finding

Click "Public S3 Bucket" (the top risk item)

You're now on the Finding Detail page.

Point at each section:

    Three badges at the top:

        [CRITICAL] — the rule's severity

        [Risk 100/100] — computed risk score

        [🤖 ML: CRITICAL 100%] — ML prediction

    Say: "We show three signals: the rule severity from CIS benchmarks, a computed risk score, and an ML-predicted priority."

    Overview section:

        Resource: launchnest-public-assets

        Rule ID: PUBLIC_S3_RULE

        ML Prediction: CRITICAL with 100% confidence

    Say: "Every finding links to a specific cloud resource and rule."

    Evidence section:

        Shows "public_access": true, "raw_acl": "public-read", "public_access_block": false

    Say: "The evidence shows exactly what's misconfigured — proof from the cloud config."

    Why This Is Dangerous:

        Read it aloud

    Say: "Plain-English explanation — no jargon."

    Remediation:

        Read it aloud

    Say: "Step-by-step fix guidance."

    Reference:

        CIS AWS 2.1.5

    Say: "Every rule maps to a CIS AWS benchmark control, so it's grounded in industry standards."

Minute 4–4:30: Show the API

Switch to Tab 3 (http://localhost:8001/docs)

Say:

    "CloudSentry is powered by a FastAPI backend. Here's the auto-generated API documentation."

Point at:

    GET /health — "Health check"

    POST /scan — "Triggers a full scan"

    GET /findings — "Returns all findings"

    GET /findings/{id} — "Returns one finding"

Optional: Click POST /scan → "Try it out" → Execute → show the JSON response.

Say:

    "The API returns structured findings with evidence, remediation, and ML predictions. It's ready to be consumed by any client — the React dashboard is one."

Minute 4:30–5: Wrap Up

Say:

    "To summarize: I built a full-stack CSPM platform with:

        8 security rules aligned with CIS AWS Benchmarks

        A transparent risk engine using severity × exposure × confidence

        An ML model (XGBoost) trained on 1,500 synthetic configs — XGBoost won by measured F1, not by popularity

        Two React frontends — one for the customer, one for security

        A demo customer (LaunchNest) with realistic AWS resources and 10 actual misconfigurations

    The system detects 10 findings in ~1 second, including 3 critical issues.

    The architecture is provider-neutral — Azure support would only require a new adapter, not a rewrite.

    Thank you."

📋 Backup Plan (If Something Crashes)
If a service is down

    Restart it in a terminal

    Re-verify with curl http://localhost:<port>/health

    Say: "Let me restart that service" — demonstrates debugging skill

If the browser freezes

    Switch to another tab

    Refresh with Ctrl + Shift + R

    Worst case: open docs/screenshots/ and show the expected output

If the ML prediction fails

    Rule severity still shows

    Risk score still shows

    Say: "The ML is a supplementary signal; the rule-based detection is authoritative"

🎯 Common Questions During Demo
"Why 52/100?"

A: "Security score = 100 − average risk score. Our 10 findings have an average risk of 48, so the score is 52. It's not perfect — we lost 48 points to misconfigurations."
"Why is risk score 100 for Public S3 but 38 for Stale Key?"

A: "Public S3 has CRITICAL severity × PUBLIC_INTERNET exposure × HIGH confidence. That's 1.0 × 1.0 × 1.0 = 100. Stale Key is HIGH severity × INTERNAL exposure × HIGH confidence = 0.75 × 0.50 × 1.00 = 38. Public-facing issues rank higher."
"Why does the ML prediction say CRITICAL? Isn't the rule already CRITICAL?"

A: "The ML provides an independent signal. When they agree, confidence is higher. When they disagree, we show both and let the rule severity remain authoritative. This is how real CSPM platforms work — multiple signals, transparent to the user."
"Can this scan real AWS?"

A: "Not yet — the current demo uses a simulated AWS environment. But the architecture is ready: we'd add a real AWS adapter that uses Boto3 with read-only IAM permissions. The rules and risk engine wouldn't change at all."
"How many customers could it handle?"

A: "In its current form, single-tenant. To scale: swap SQLite for PostgreSQL, add Redis for background jobs, add multi-tenant isolation. The core architecture already supports it — we just need production infrastructure."
🎬 Timing Tips
Section	Time	Focus
Intro	0:00–1:00	Problem + Customer
LaunchNest	1:00–2:00	Show customer SaaS
CloudSentry Dashboard	2:00–3:00	Show security posture
Finding Deep-Dive	3:00–4:00	Show 3 signals + evidence
API Docs	4:00–4:30	Show backend
Wrap-up	4:30–5:00	Summary + future

Total: 5 minutes — practice until you hit this timing.
🎯 Phrases to Practice

    "Let me show you..."

    "This finding is interesting because..."

    "Notice how the ML prediction aligns with..."

    "To summarize the architecture..."

Avoid:

    "Um, I think..." — pause, think, then answer

    "I don't know" — say "Let me check" and verify

    "It's just a demo" — it's a real project, treat it as such

📸 Fallback Screenshots

If live demo fails at any point, show these from docs/screenshots/:

    01-cs-overview.png — CloudSentry dashboard

    02-cs-findings.png — Findings table

    03-cs-detail.png — Finding detail with ML badge

    06-ln-dashboard.png — LaunchNest dashboard

Say: "Let me show the screenshot of what we saw earlier."
After the Demo

    Wait for questions

    Refer to VIVA_NOTES.md if needed

    Be ready to show ARCHITECTURE.md if asked about design