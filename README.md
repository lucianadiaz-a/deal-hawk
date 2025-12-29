# Deal Hawk

## Executive Summary

- **What it is:** Price monitoring proof-of-concept (POC) that tracks products across multiple retailers, records price snapshots, computes deltas, and demonstrates simulated deal alert triggers
- **Why it exists:** Addresses manual deal monitoring bottleneck identified in discovery—lack of speed in identifying purchase opportunities caps deal volume and revenue throughput
- **What the MVP demonstrates:** Automated monitoring → normalized price history → detectable change → alertable event workflow
- **Status:** MVP build complete and deployed. App is functional and running in production. Ready for demo submission
- **Tech stack:** FastAPI backend, React + TypeScript frontend, SQLite database, fixture-based retailer connectors (deterministic pricing for POC)
- **Where to look next:** See `docs/00-overview/INDEX.md` for full documentation index

## Objectives & Scope (MVP)

**In scope:**
- Seed ~10 products across ≥3 retailers (fixtures allowed)
- Store price snapshots over time in SQLite
- Compute deltas over configurable time windows
- Generate `AlertEvent` records when rules trigger (simulated trigger + tests)
- React UI: current prices + deltas, snapshot history, alert log

**Out of scope:**
- External alert delivery (email/Slack/Discord/Zapier)
- ToS/robots-violating scraping
- Multi-user hosting, auth, background workers

**Success criteria:**
- Coverage: ≥10 products × ≥3 retailers visible and updating
- History: snapshots + deltas viewable in UI
- Proof: deterministic tests for alert trigger + UI shows created alert events

## Strategic Prework (What's Already Done)

- **Discovery completed:** Interviews and process maps documented in `docs/01-discovery/`
- **Synthesis completed:** Insights, opportunities, and MVP decision rationale in `docs/02-synthesis/` (see `docs/02-synthesis/MVP_DECISION.md` for full context)
- **MVP decision:** Price Monitoring POC validates core mechanism—automated monitoring → normalized price history → detectable change → alertable event
- **Project brief:** Full context on growth constraint and project rationale in `docs/00-overview/PROJECT_BRIEF.md`
- **Build plan:** Architecture, data model, and implementation approach in `docs/03-roadmap/BUILD_PLAN.md`
- **Demo plan:** Full demo script and clickpath in `docs/03-roadmap/DEMO_PLAN.md`
- **Engineering standards:** Python 3.11+, type hints, Pydantic models, deterministic tests documented in `docs/00-overview/ENGINEERING_STANDARDS.md`
- **Documentation index:** Complete navigation in `docs/00-overview/INDEX.md`

## Quickstart

### Prerequisites
- Python 3.11+ (see `docs/00-overview/ENGINEERING_STANDARDS.md`)
- SQLite (local file, no setup required)

### Setup

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m backend.db init
python scripts/seed_db.py  # Idempotent: preserves price history on re-runs
```

### Run Backend

```bash
uvicorn backend.api.main:app --reload --port 8000
```

API available at `http://localhost:8000` with docs at `http://localhost:8000/docs`

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend available at `http://localhost:5173` (proxies `/api/*` to `http://localhost:8000`)

### Run Both (Recommended)

```bash
bash scripts/dev.sh
```

Starts FastAPI at `http://localhost:8000` and React at `http://localhost:5173`. Automatically uses frozen demo DB (`data/demo.sqlite3`) for stable demos.

### Run Price Ingestion

```bash
python scripts/run_ingest.py
```

### Run Tests

```bash
pytest -q
```

Test suite covers seed integrity, alert logic, pricing calculations, and demo DB regression.

## Demo

**Quick demo clickpath (2–4 minutes):**
1. Open React overview: show 10×≥3 coverage, "last updated" timestamps
2. Click product/listing: show snapshot history + delta window
3. Trigger "Run ingest now": show timestamp and/or price changes update
4. Trigger "Simulate drop": show `AlertEvent` created
5. Open alert log: show alert preview + event record

**Frozen demo database:**
- **What it guarantees:** Static data (prices never change), complete coverage (all products × all retailers), rich history (24 snapshots per listing), consistent charts
- **Build it:** `python scripts/build_demo_db.py` (creates `data/demo.sqlite3` with deterministic prices and fixed timestamps)
- **Use it:** `dev.sh` automatically uses it, or set `export DEAL_HAWK_DB_PATH=data/demo.sqlite3`
- **Customize:** `python scripts/build_demo_db.py --snapshot-count 48 --snapshot-interval-minutes 30 --output data/custom_demo.sqlite3`

See `docs/03-roadmap/DEMO_PLAN.md` for full demo script.

## Repo Structure

```
deal-hawk/
├── backend/          # Domain + DB + services (Python package)
├── data/             # Seed data (seed_listings.json)
├── docs/             # Project documentation
├── frontend/         # React + TypeScript frontend (Vite)
├── scripts/          # Utility scripts (seed, ingest, demo DB)
└── tests/            # Unit tests
```

## Architecture

**Layers:**
- React frontend (UI: overview, product detail, alert log)
- FastAPI API layer (endpoints: `/api/overview`, `/api/products`, `/api/listings/{id}/price-history`)
- Backend services (ingest, pricing, alerts)
- SQLite database (system of record)
- Fixture connectors (retailer data sources for POC)

**Data model (SQLite):**
- `products` — Product catalog
- `retailers` — Retailer list
- `listings` — Product-retailer pairs (product_id, retailer_id, url)
- `price_snapshots` — Historical prices (listing_id, price_cents, currency, captured_at)
- `alert_events` — Triggered alerts (listing_id, triggered_at, prev_price_cents, new_price_cents, rule_name, message_preview)

See `docs/03-roadmap/BUILD_PLAN.md` for full architecture details.

## Deployment

**Production URLs:**
- Frontend: https://deal-hawk-frontend-production.up.railway.app
- Backend API: https://deploy-demo-production-bcaf.up.railway.app
- API Docs: https://deploy-demo-production-bcaf.up.railway.app/docs

**Platform:** Railway (separate services for backend and frontend)
- Backend: Python service with `main.py` entry point
- Frontend: Static site serving Vite-built React app
- Database: SQLite file (auto-initialized on first startup)

**CI/CD:** GitHub Actions (`.github/workflows/ci.yml`) runs on push to `main` and `deploy-2`:
- Backend tests (pytest)
- Frontend build validation (Vite)
- Code quality checks (Ruff linting, mypy type checking)
- Railway "Wait for CI" integration

**Environment variables:**
- `DEAL_HAWK_DB_PATH`: Override default database path (default: `data/deal_hawk.sqlite3`)
- `PORT`: Railway-provided port for backend service
- `VITE_API_URL`: Frontend environment variable for backend API URL

**Deployment notes:** Database auto-creates on first run. Do NOT commit `data/deal_hawk.sqlite3` to version control. Seed after deployment using CLI scripts.

## Documentation

- **Project overview:** `docs/00-overview/`
- **Discovery artifacts:** `docs/01-discovery/` (complete)
- **Synthesis & MVP decision:** `docs/02-synthesis/` (complete)
- **Build plan & roadmap:** `docs/03-roadmap/`

See `docs/00-overview/INDEX.md` for the full documentation index.

## License

See `LICENSE` file.

## Next Steps

**Immediate priorities:**
- Demo video: Record <10 minute walkthrough demonstrating the full workflow
- Final submission: Prepare demo package with video, repo link, and live deployment URLs

**Future enhancements (post-MVP):**
- Replace fixture connectors with real retailer integrations (APIs or RSS feeds)
- Add external alert delivery (email, Slack, Discord, Zapier)
- Implement background scheduling for automated ingestion
- Add multi-user support with authentication
- Migrate from SQLite to Postgres for production scale
