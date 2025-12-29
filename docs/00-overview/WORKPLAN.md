# Workplan — Deal Hawk (48-hour sprint)

## Objective
Produce a Build First submission that demonstrates:
- user-centered discovery under tight time constraints
- clear prioritization based on measurable impact
- a functional prototype that proves the approach
- production-grade hygiene (repo, docs, tests, deploy)

## Progress Summary (as of 2025-12-28)

**Completed:**
- ✅ Discovery phase: 1 stakeholder interview, workflow map, pain points quantified
- ✅ Synthesis phase: 10 insights, 12 opportunities ranked, MVP scope locked
- ✅ Build phase: Full end-to-end implementation (DB, services, UI, tests)
- ✅ MVP acceptance criteria met: 10 products × 3 retailers, price tracking, delta computation, alert triggers
- ✅ Deployment: Backend and frontend deployed to Railway with public URLs
- ✅ CI/CD: GitHub Actions pipeline with automated testing and build validation
- ✅ Push Deal feature: Wizard-of-Oz workflow simulation for demo purposes
- ✅ Frozen demo database: Deterministic data for consistent demos

**In progress:**
- 🔄 Demo video creation
- 🔄 Final documentation polish

**Blockers:** None

**Next milestones:** Record demo video, finalize submission package

## Workstreams
### A) Discovery (Problem Mining) ✅ **COMPLETE**
**Outputs** (delivered)
- ✅ lightweight as-is workflow map (`docs/01-discovery/process-maps/As-Is-Purchasing-Cycle.pdf`)
- ✅ 1 stakeholder interview (Exec-01) with transcript (`docs/01-discovery/interview/Int_Exec_1.md`)
- ✅ list of pains/bottlenecks with quantified signals (`docs/02-synthesis/INSIGHTS.md`)
- ✅ constraints & risks identified (ToS compliance, data access, vendor skepticism)

**Method**
- Start interviews with: role → excited about AI → skeptical about AI
- Walk through day-to-day / workflow step-by-step
- Quantify impact and prior attempts to solve

### B) Synthesis (Turn unstructured → structured) ✅ **COMPLETE**
**Outputs** (delivered)
- ✅ consolidated pain points (`docs/02-synthesis/INSIGHTS.md` — 10 key insights)
- ✅ opportunity list (ranked) (`docs/02-synthesis/OPPORTUNITY_ID.md` — O1–O12)
- ✅ ROI hypothesis per opportunity (`docs/02-synthesis/ROI_PRIORITIZATION.md`)
- ✅ selection rationale for the sprint MVP (`docs/02-synthesis/MVP_DECISION.md`)

### C) MVP Definition (Scope + success metrics) ✅ **COMPLETE**
**Outputs** (delivered)
- ✅ one-sentence MVP scope: "Track ~10 products across ≥3 retailers, record price snapshots over time, show price deltas over the last X hours, and demonstrate a simulated 'alert trigger' flow"
- ✅ explicit success metrics: Coverage (≥10 products × ≥3 retailers), History (UI shows last X hours), Alert proof (tests + UI preview)
- ✅ acceptance criteria defined (`docs/02-synthesis/MVP_DECISION.md`)
- ✅ cut list defined (real-time guarantee, multi-channel integrations, ToS-violating scraping)

### D) Build + Integrate (Execution) ✅ **COMPLETE**
**Outputs** (delivered)
- ✅ functional prototype meeting acceptance criteria (10 products × 3 retailers)
- ✅ integrations validated end-to-end (seed → ingest → pricing → alerts → UI)
- ✅ dataset is synthetic/public/permissible (fixture-based Apple products)
- ✅ comprehensive test suite (seed integrity, pricing, alerts)
- ✅ idempotent operations (seed preserves history, ingest appends)

### E) Ship (Deploy + proof it works) ✅ **COMPLETE**
**Outputs** (delivered)
- ✅ deployed demo links (frontend + backend on Railway)
- ✅ reproducible local run steps (documented in README)
- ✅ smoke test checklist (CI/CD pipeline validates builds)
- ✅ Database auto-initialization on startup
- ✅ CORS configuration for production frontend
- ✅ Root-level import wrapper for Railway auto-detection

### F) Demo Package (Submission-ready) 🔄 **IN PROGRESS**
**Outputs**
- ⏳ <10 min demo video script
- ⏳ final demo recording (unlisted YouTube)
- ⏳ YouTube description includes repo + live link(s)
- ✅ final README polish (this update)

## Timeline (48 hours)
### Phase 1: Set up + Discovery ✅ **COMPLETE**
- ✅ repo + docs scaffolding
- ✅ interview guide finalized
- ✅ 1 interview completed + transcribed (Exec-01)
- ✅ initial workflow map + quantified pain points

### Phase 2: Synthesis + MVP selection ✅ **COMPLETE**
- ✅ synthesize insights (10 insights documented)
- ✅ rank opportunities by ROI and feasibility (O1 ranked #2, MVP wedge selected)
- ✅ lock MVP scope + acceptance criteria (Price Monitoring POC)

### Phase 3: Build + validate ✅ **COMPLETE**
- ✅ implemented MVP incrementally (DB, services, connectors, UI)
- ✅ validated integration paths (seed → ingest → pricing → alerts → UI)
- ✅ added tests for core logic (seed integrity, alerts, pricing)
- ✅ React frontend running locally with full functionality

**Deliverables completed:**
- `backend/db.py`: SQLite schema with WAL mode, foreign keys, indexes
- `backend/services/`: ingest, pricing, alerts (stateless service layer)
- `backend/connectors/fixtures.py`: deterministic fixture-based pricing
- `scripts/seed_db.py`: idempotent seeding with 10 products × 3 retailers
- `scripts/run_ingest.py`: ingestion cycle runner
- `frontend/`: React + TypeScript UI (overview, detail, alerts)
- `tests/`: test_seed_integrity.py, test_pricing.py, test_alerts.py
- `requirements.txt`: fastapi, pydantic, pytest

### Phase 4: Deploy + demo ✅ **COMPLETE**
- ✅ deploy + smoke test (Railway deployment, CI/CD pipeline)
- ✅ finalize README + docs (comprehensive documentation)
- ⏳ record demo video + submit (final step)

## Quality gates (must pass)
- No secrets committed (ever)
- No sensitive data in repo (anonymized only)
- Clean git history on `prod` (linear, squashed merges)
- Tests exist for core logic
- Demo is reliable (no “works on my machine”)
- Documentation tells a coherent story from discovery → decision → build → impact
