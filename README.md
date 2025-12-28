# Deal Hawk

**Deal Hawk** is a price monitoring proof-of-concept (POC) that tracks products across multiple retailers, records price snapshots over time, computes price deltas, and demonstrates simulated deal alert triggers. This project addresses the primary growth constraint identified in discovery: **manual deal monitoring** and the lack of speed in identifying purchase opportunities, which caps deal volume and revenue throughput. (See `docs/00-overview/PROJECT_BRIEF.md` for full context.)

## Current Status

**Status:** MVP build complete. App is functional and running. Ready for deployment and demo preparation. (See `docs/00-overview/WORKPLAN.md` for timeline.)

This is a timeboxed Build First sprint (48 hours) to demonstrate a Tenex-style approach: fast discovery, ruthless prioritization, and clean delivery of a small but real workflow improvement.

**What's working:**
- ✅ SQLite database with full schema (products, retailers, listings, price_snapshots, alert_events)
- ✅ Seed data: 10 products across 3 retailers (Amazon, Best Buy, Target)
- ✅ Idempotent seeding (preserves price history on re-runs)
- ✅ Price ingestion with fixture-based connectors (deterministic pricing)
- ✅ Delta computation over configurable time windows
- ✅ Alert evaluation and event creation with deduplication
- ✅ Streamlit UI with overview, detail views, and alert log
- ✅ Test suite covering seed integrity, alert logic, and pricing calculations

## MVP Scope (Current Build)

The Price Monitoring POC validates the core mechanism: **automated monitoring → normalized price history → detectable change → alertable event**. (See `docs/02-synthesis/MVP_DECISION.md` for full rationale.)

**In scope:**
- Seed ~10 products across ≥3 retailers (fixtures allowed)
- Store price snapshots over time in SQLite
- Compute deltas over a configurable window (e.g., last X hours)
- Generate `AlertEvent` records when a rule triggers (simulated trigger + tests)
- Streamlit UI showing:
  - Current prices + deltas
  - Snapshot history (per listing/product)
  - Alert log + alert preview

**Out of scope:**
- External alert delivery (email/Slack/Discord/Zapier)
- Any ToS/robots-violating scraping
- Multi-user hosting, auth, background workers

**Success criteria:**
- Coverage: ≥10 products × ≥3 retailers visible and updating
- History: snapshots + deltas viewable in UI
- Proof: deterministic tests for alert trigger + UI shows created alert events

## Repository Structure

```
deal-hawk/
├── app/                    # Streamlit web app (UI)
├── backend/               # Domain + DB + services (Python package)
│   ├── db.py              # SQLite connection + schema
│   ├── connectors/        # Retailer connectors (fixtures for POC)
│   └── services/          # Business logic (ingest, pricing, alerts)
├── data/                  # Seed data and synthetic datasets
│   └── synthetic/         # Synthetic/public data only
├── docs/                  # Project documentation
│   ├── 00-overview/       # Project brief, workplan, standards
│   ├── 01-discovery/      # Interviews, process maps (complete)
│   ├── 02-synthesis/      # Insights, opportunities, MVP decision (complete)
│   └── 03-roadmap/        # Build plan, demo plan, roadmap
├── infra/                 # Deployment/infrastructure configs (TBD)
├── scripts/               # Utility scripts
│   ├── seed_db.py         # Seed products/retailers/listings (idempotent)
│   └── run_ingest.py      # Run price ingestion cycle
└── tests/                 # Unit tests (TBD)
```

## Quickstart

### Prerequisites

- **Python:** 3.11+ (see `docs/00-overview/ENGINEERING_STANDARDS.md`)
- **Dependencies:** See `requirements.txt`
- **Database:** SQLite (local file, no setup required)

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd deal-hawk
   ```

2. **Create a virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python -m backend.db init
   ```

5. **Seed data:**
   ```bash
   python scripts/seed_db.py
   ```

   This populates the database with ~10 products across ≥3 retailers from `data/seed_listings.json`. The seed script is **idempotent**: running it multiple times will not create duplicate products or listings, and it preserves existing price history.

   **Verification:** Re-running seed should NOT change listing count or delete snapshots. Verify with:
   ```bash
   sqlite3 data/deal_hawk.sqlite3 "SELECT COUNT(*) FROM listings;"
   sqlite3 data/deal_hawk.sqlite3 "SELECT COUNT(*) FROM price_snapshots;"
   ```
   These counts should remain unchanged after re-seeding. (See `docs/03-roadmap/BUILD_PLAN.md` section 2.)

### Run Price Ingestion Cycle

```bash
python scripts/run_ingest.py
```

Each ingest cycle writes `price_snapshots` for all seeded listings. Retailer connectors start as fixtures (see `docs/03-roadmap/BUILD_PLAN.md` section 3).

### Run Streamlit App

```bash
streamlit run app/main.py
```

The UI should show:
- Overview table (current prices + deltas + last updated)
- Detail view (snapshot history per product/listing)
- Alert log (events + preview)

### Run Tests

```bash
pytest -q
```

The test suite includes `tests/test_seed_integrity.py`, which verifies that seeding is idempotent and does not delete price history. This test serves as a guardrail to ensure:
- Seed operations do not decrease `price_snapshots` or `alert_events` counts
- Seed operations do not increase `products`, `retailers`, or `listings` counts
- Listing IDs remain stable across seed runs
- Ingest operations create exactly one snapshot per active listing
- Products table enforces uniqueness constraints

Minimum test coverage: deal detection logic (thresholds, edge cases) and parsing/normalization logic. Tests must be deterministic (no network calls). (See `docs/00-overview/ENGINEERING_STANDARDS.md`.)

## Architecture Overview

```
┌─────────────┐
│ Streamlit   │  UI layer (app/)
│   App       │  - Overview table
└──────┬──────┘  - Detail views
       │         - Alert log
       │
┌──────▼──────┐
│  Backend    │  Domain + services (backend/)
│  Services   │  - ingest.py (price collection)
│             │  - pricing.py (delta computation)
│             │  - alerts.py (alert evaluation)
└──────┬──────┘
       │
┌──────▼──────┐
│   SQLite    │  System of record
│   Database  │  - products, retailers, listings
│             │  - price_snapshots
│             │  - alert_events
└──────┬──────┘
       │
┌──────▼──────┐
│ Connectors  │  Retailer data sources
│ (Fixtures)  │  - fixtures.py (POC)
└─────────────┘  - Swap for real APIs later
```

**Data model (SQLite):**
- `products` — Product catalog
- `retailers` — Retailer list
- `listings` — Product-retailer pairs (product_id, retailer_id, url)
- `price_snapshots` — Historical prices (listing_id, price_cents, currency, captured_at)
- `alert_events` — Triggered alerts (listing_id, triggered_at, prev_price_cents, new_price_cents, rule_name, message_preview)

(See `docs/03-roadmap/BUILD_PLAN.md` for full architecture and data model.)

**Note:** The project brief mentions Postgres as the system of record (`docs/00-overview/PROJECT_BRIEF.md`), but the build plan specifies SQLite for the POC (`docs/03-roadmap/BUILD_PLAN.md`). SQLite is used for local development; Postgres would be used for production deployment.

## Demo Instructions

See `docs/03-roadmap/DEMO_PLAN.md` for the full demo script.

**Quick demo clickpath (2–4 minutes):**
1. Open Streamlit overview: show 10×≥3 coverage, "last updated" timestamps
2. Click a product/listing: show snapshot history + delta window
3. Trigger "Run ingest now": show timestamp and/or price changes update
4. Trigger "Simulate drop": show an `AlertEvent` created
5. Open alert log: show alert preview + event record

**Pre-demo setup:**
1. Seed DB
2. Run 1–2 ingest cycles
3. Run simulation once to force an alert

## Contributing / Development Notes

**Engineering standards:** See `docs/00-overview/ENGINEERING_STANDARDS.md` for:
- Python 3.11+ with type hints
- Pydantic models for API boundaries
- Deterministic tests (no network calls)
- Structured logging (no secrets)
- Formatting + linting (exact tooling TBD)

**Git workflow:**
- `prod` is linear history only
- Work on `feature/*` or `chore/*` branches
- Rebase onto `origin/prod`, squash to 1 commit, PR → merge → delete branch

**Constraints:**
- No secrets in repo (ever)
- No sensitive data (synthetic/public/permissible only)
- Respect retailer ToS/robots (prefer APIs/feeds, no aggressive scraping)

## Documentation

- **Project overview:** `docs/00-overview/`
- **Discovery artifacts:** `docs/01-discovery/` (complete)
- **Synthesis & MVP decision:** `docs/02-synthesis/` (complete)
- **Build plan & roadmap:** `docs/03-roadmap/`

See `docs/00-overview/INDEX.md` for the full documentation index.

## License

See `LICENSE` file.

---

## Next Steps

**Immediate priorities:**
1. **Deployment:** Set up hosting (e.g., Streamlit Community Cloud, Fly.io, or Railway)
2. **Demo video:** Record <10 minute walkthrough demonstrating the full workflow
3. **Documentation polish:** Final pass on README and docs for submission

**Future enhancements (post-MVP):**
- Replace fixture connectors with real retailer integrations (APIs or RSS feeds)
- Add external alert delivery (email, Slack, Discord, Zapier)
- Implement background scheduling for automated ingestion
- Add multi-user support with authentication
- Migrate from SQLite to Postgres for production scale
