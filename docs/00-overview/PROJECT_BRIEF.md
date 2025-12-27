# Project Brief 

## What this is
NAME PENDING is a timeboxed Build First sprint to demonstrate a Tenex-style approach:
- fast, user-centered discovery
- ruthless prioritization
- clean delivery of a small but real workflow

This document is intentionally **pre-interview** and will be updated after discovery.

## Current hypothesis (NOT confirmed yet)
We believe a meaningful bottleneck exists in the company’s buying/resale operations and their management of staff-level of sellers, given their business model. 

**This is a hypothesis.** Discovery will confirm the real workflow, users, constraints, and ROI.

## Discovery goals (next 48 hours)
1) Identify and map 1–2 critical workflows (as-is)
2) Select ONE high-leverage “moment of decision” to accelerate
3) Quantify baseline pain (time/week, frequency, estimated $ impact)
4) Define a measurable MVP that improves an outcome

## Target users (initial assumption)
- Exec stakeholders with end-to-end visibility (Exec-01, Exec-02 TIME PERMISSIBLE)

All user artifacts stored in-repo will be anonymized and redacted.

## Output goals (Build First submission)
A functional, deployed prototype demonstrating:
- a real workflow improvement (measurable outcome)
- end-user centric design choices
- production-grade engineering hygiene (tests, structure, security)

## Decisions already locked for this sprint
- Fast iteration, “least that delivers the most”
- FastAPI backend
- Streamlit web app for demo UI
- Postgres database as system of record
- Zapier used for integrations (alerts, scheduling, webhooks)
- Secrets handled via environment variables / platform secret managers (never committed)
- Deployment will be cost-minimized

## Constraints
- Timebox: 48 hours
- Data: synthetic/public/permissible only (no PII, no proprietary pricing sheets)
- Compliance: respect retailer ToS/robots; prefer permissible integrations/APIs
- Repo: public-facing artifact; must remain clean and non-sensitive

## Definition of Done (for sprint)
- Deployed demo link(s) that work reliably
- Repo with clear commit history and readable docs
- README: local run steps + architecture overview + limitations
- Core logic has tests (minimum: deal detection + parsing/normalization)
- No secrets or sensitive data in git history
- Demo video script ready (<10 minutes), aligned to users + ROI

