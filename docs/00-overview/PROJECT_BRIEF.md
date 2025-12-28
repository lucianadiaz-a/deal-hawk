# Project Brief 

## What this is
**Deal Hawk** is a timeboxed Build First sprint to demonstrate a Tenex-style approach:
- fast, user-centered discovery
- ruthless prioritization
- clean delivery of a small but real workflow

**Status:** Discovery and synthesis complete. MVP selected. Ready for build phase.

## INITIAL HYPOTHESIS
We believe a meaningful bottleneck exists in the company’s buying/resale operations and their 
management of staff-level of sellers, given their business model. 
## Confirmed hypothesis (from discovery)
The business's growth is mechanically constrained by deal volume, which is constrained by **scouting speed**. The primary bottleneck is **manual deal monitoring** and the lack of speed in identifying purchase opportunities, then notifying buyers fast enough to catch the deal window.

**Evidence:** Exec stakeholder explicitly states: "We are held back by the lack of speed in identifying purchase opportunities, and then... notifying a wide network of... buyers fast enough." Deal scouting is the throughput ceiling; even with alerts, monitoring remains largely manual.

## Discovery outcomes (completed)
✅ **Workflow mapping:** As-is purchasing cycle mapped with bottlenecks identified  
✅ **Stakeholder interviews:** Exec-01 interview completed and synthesized  
✅ **Pain quantification:** Speed constraint identified as primary bottleneck; opportunity cost framed as lost revenue  
✅ **MVP selection:** Price Monitoring POC selected (see `docs/02-synthesis/MVP_DECISION.md`)

## Selected MVP
**Price Monitoring POC** — Track ~10 products across ≥3 retailers, record price snapshots over time, show price deltas, and demonstrate simulated "alert trigger" flow. This validates the highest-leverage bottleneck: automated deal scouting → normalized price history → detectable change → alertable event.

**Full scope:** See `docs/02-synthesis/MVP_DECISION.md`  
**ROI rationale:** See `docs/02-synthesis/ROI_PRIORITIZATION.md`

## Target users (confirmed from discovery)
- **Primary:** Exec stakeholders with end-to-end visibility (Exec-01 interviewed)
- **Secondary:** Single operator (EMPLOYEE A) who bridges scouting → posting → buyer comms (key-person bottleneck identified)

All user artifacts stored in-repo are anonymized and redacted.

## Output goals (Build First submission)
A functional, deployed prototype demonstrating:
- a real workflow improvement (measurable outcome)
- end-user centric design choices
- production-grade engineering hygiene (tests, structure, security)

## Decisions already locked for this sprint
- Fast iteration, "least that delivers the most"
- FastAPI backend
- React frontend for demo UI
- SQLite for POC (Postgres for production)
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

