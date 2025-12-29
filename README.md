# Deal Hawk

**Deal Hawk** is a price monitoring proof-of-concept (POC) that tracks products across multiple retailers, records price snapshots over time, computes price deltas, and demonstrates simulated deal alert triggers. This project addresses the primary growth constraint identified in discovery: **manual deal monitoring** and the lack of speed in identifying purchase opportunities, which caps deal volume and revenue throughput. (See `docs/00-overview/PROJECT_BRIEF.md` for full context.)

## Current Status

**Status:** MVP build complete and deployed. App is functional and running in production. Ready for demo submission. (See `docs/00-overview/WORKPLAN.md` for timeline.)

This is a timeboxed Build First sprint (48 hours) to demonstrate a Tenex-style approach: fast discovery, ruthless prioritization, and clean delivery of a small but real workflow improvement.

**What's working:**
- ✅ SQLite database with full schema (products, retailers, listings, price_snapshots, alert_events)
- ✅ Seed data: 10 products across 3 retailers (Amazon, Best Buy, Target)
- ✅ Idempotent seeding (preserves price history on re-runs)
- ✅ Price ingestion with fixture-based connectors (deterministic pricing)
- ✅ Delta computation over configurable time windows
- ✅ Alert evaluation and event creation with deduplication
- ✅ React UI with overview, detail views, and alert log
- ✅ Push Deal workflow simulation (Wizard-of-Oz demo feature)
- ✅ Frozen demo database for consistent, repeatable demos
- ✅ Test suite covering seed integrity, alert logic, and pricing calculations
- ✅ CI/CD pipeline with GitHub Actions (backend tests, frontend build validation, linting)
- ✅ Production deployment on Railway (backend + frontend)

## MVP Scope (Current Build)

The Price Monitoring POC validates the core mechanism: **automated monitoring → normalized price history → detectable change → alertable event**. (See `docs/02-synthesis/MVP_DECISION.md` for full rationale.)

**In scope:**
- Seed ~10 products across ≥3 retailers (fixtures allowed)
- Store price snapshots over time in SQLite
- Compute deltas over a configurable window (e.g., last X hours)
- Generate `AlertEvent` records when a rule triggers (simulated trigger + tests)
- React UI showing:
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
├── backend/               # Domain + DB + services (Python package)
│   ├── db.py              # SQLite connection + schema
│   ├── connectors/        # Retailer connectors (fixtures for POC)
│   └── services/          # Business logic (ingest, pricing, alerts)
├── data/                  # Seed data and synthetic datasets
│   ├── seed_listings.json # Product/retailer seed data
│   └── synthetic/         # Synthetic/public data only (placeholder)
├── docs/                  # Project documentation
│   ├── 00-overview/       # Project brief, workplan, standards
│   ├── 01-discovery/      # Interviews, process maps (complete)
│   ├── 02-synthesis/      # Insights, opportunities, MVP decision (complete)
│   ├── 03-roadmap/        # Build plan, demo plan, roadmap
│   └── 04-building/       # Build diary and notes
├── frontend/              # React + TypeScript frontend (Vite)
│   ├── src/               # React components, pages, hooks, API client
│   └── public/            # Static assets
├── scripts/               # Utility scripts
│   ├── seed_db.py         # Seed products/retailers/listings (idempotent)
│   ├── run_ingest.py      # Run price ingestion cycle
│   ├── build_demo_db.py   # Build frozen demo database
│   ├── dev.sh             # Run FastAPI + Vite dev servers
│   ├── verify_demo_db.py  # Verify demo DB integrity
│   ├── verify_all_retailers.py  # Verify retailer coverage
│   └── test_demo_api.py   # Test API endpoints
└── tests/                 # Unit tests
    ├── test_seed_integrity.py  # Seed idempotency tests
    ├── test_demo_db_frozen.py  # Demo DB regression tests
    ├── test_alerts.py     # Alert logic tests
    ├── test_pricing.py    # Pricing calculation tests
    └── test_api.py        # API endpoint tests
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

5. **Bootstrap demo data:**
   - Seed the database, run ingestion cycles, and generate sample alerts using the CLI:
     ```bash
     python scripts/seed_db.py
     ```

   The seed script is **idempotent**: running it multiple times will not create duplicate products or listings, and it preserves existing price history.

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

### Run FastAPI Server

```bash
uvicorn backend.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with:
- **Interactive docs**: `http://localhost:8000/docs` (Swagger UI)
- **Health check**: `GET /health` (returns DB path and status)
- **Overview**: `GET /api/overview` (metrics, recent alerts, near misses)
- **Products list**: `GET /api/products` (with filtering, sorting, pagination)
- **Product detail**: `GET /api/products/{product_id}` (product info with listings)
- **Listing price history**: `GET /api/listings/{listing_id}/price-history`
- **Product alert history**: `GET /api/products/{product_id}/alert-history`

The API automatically connects to the SQLite database.

### Run React Frontend

**Install frontend dependencies:**

```bash
cd frontend
npm install
```

**Run frontend dev server (standalone):**

```bash
cd frontend
npm run dev
```

The React app will be available at `http://localhost:5173` with:
- Overview page at `/` (calls `/api/overview`) — metrics, recent alerts, near misses
- Products list at `/products` (calls `/api/products`) — filterable product grid with pagination
- Product detail at `/products/:id` (calls `/api/products/:id`) — multi-retailer comparison, price charts, alert history

**Note:** The frontend dev server proxies `/api/*` and `/health` to `http://localhost:8000`, so you need the FastAPI server running.

**Run FastAPI + Vite together (recommended for demos):**

```bash
bash scripts/dev.sh
```

This starts both:
- FastAPI at `http://localhost:8000` (with `/docs`)
- React frontend at `http://localhost:5173`

**⚠️ IMPORTANT FOR STABLE DEMOS:** The `dev.sh` script automatically uses a **frozen demo database** (`data/demo.sqlite3`) for stable, deterministic demo behavior. This ensures:
- ✅ **Static data**: Prices and history NEVER change on page refresh
- ✅ **Complete coverage**: Every product has listings for all 3 retailers (Amazon, Best Buy, Target)
- ✅ **Rich history**: Every listing has 24 price snapshots (1 per hour)
- ✅ **Consistent charts**: Product detail pages always show lines for all retailers

The demo DB is created automatically if it doesn't exist. **If you're already running a server, restart it** to use the demo DB.

**Verify the demo DB is being used:**
```bash
curl http://localhost:8000/health
# Should show: {"status":"ok","db_path":".../data/demo.sqlite3","db_exists":true}
```

Press `Ctrl+C` to stop both servers.

### Frozen Demo Database

For stable Wizard-of-Oz demos, the project includes a **frozen demo database** mode that ensures:
- **Deterministic data**: Every product has listings for every retailer
- **Complete history**: Every listing has price snapshots (24 snapshots by default, 1 per hour)
- **No mutations**: API calls are read-only; prices never change across refreshes
- **Consistent charts**: Product detail charts always show lines for all retailers

**Build the demo database:**

```bash
python scripts/build_demo_db.py
```

This creates `data/demo.sqlite3` with:
- All seeded products/retailers/listings
- 24 price snapshots per listing (deterministic prices)
- Fixed timestamps (base time: 2025-01-15T12:00:00)

**Customize the demo DB:**

```bash
python scripts/build_demo_db.py \
  --snapshot-count 48 \
  --snapshot-interval-minutes 30 \
  --base-time "2025-01-20T10:00:00" \
  --output data/custom_demo.sqlite3
```

**Use the demo DB:**

The `scripts/dev.sh` script automatically uses the demo DB. To use it manually:

```bash
export DEAL_HAWK_DB_PATH=data/demo.sqlite3
uvicorn backend.api.main:app --reload --port 8000
```

**Regenerate the demo DB:**

If you need to regenerate the demo database (e.g., after changing seed data):

```bash
rm data/demo.sqlite3
python scripts/build_demo_db.py
```

**Verification:**

The demo DB is validated on creation:
- ✅ 0 listings with 0 snapshots
- ✅ All listings have at least 24 snapshots
- ✅ Deterministic prices (same DB contents every run)

See `tests/test_demo_db_frozen.py` for regression tests that verify the database is truly frozen.

### Run Tests

```bash
pytest -q
```

The test suite includes:
- `tests/test_seed_integrity.py` — Verifies that seeding is idempotent and does not delete price history
- `tests/test_demo_db_frozen.py` — Regression tests for frozen demo database (identical API responses, all listings have history)

Test guardrails ensure:
- Seed operations do not decrease `price_snapshots` or `alert_events` counts
- Seed operations do not increase `products`, `retailers`, or `listings` counts
- Listing IDs remain stable across seed runs
- Ingest operations create exactly one snapshot per active listing
- Products table enforces uniqueness constraints
- Demo DB API responses are identical across multiple calls
- All listings have price history in demo DB

Minimum test coverage: deal detection logic (thresholds, edge cases) and parsing/normalization logic. Tests must be deterministic (no network calls). (See `docs/00-overview/ENGINEERING_STANDARDS.md`.)

## Architecture Overview

```
┌─────────────┐
│   React     │  UI layer (frontend/)
│   Frontend  │  - Overview page
└──────┬──────┘  - Product detail
       │         - Alert log
       │
┌──────▼──────┐
│  FastAPI    │  API layer (backend/api/)
└──────┬──────┘
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

## Deployment

**Production URLs:**
- **Frontend:** https://deal-hawk-frontend-production.up.railway.app
- **Backend API:** https://deploy-demo-production-bcaf.up.railway.app
- **API Docs:** https://deploy-demo-production-bcaf.up.railway.app/docs

**Deployment Platform:** Railway (separate services for backend and frontend)
- Backend: Python service with `main.py` root-level entry point for Railway auto-detection
- Frontend: Static site service serving Vite-built React app
- Database: SQLite file (auto-initialized on first startup)

**CI/CD:** GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push to `main` and `deploy-2` branches:
- Backend tests (pytest)
- Frontend build validation (Vite)
- Code quality checks (Ruff linting, mypy type checking)
- Railway "Wait for CI" integration prevents broken code from deploying

**For cloud deployments:**
1. **Do NOT commit the SQLite database file** (`data/deal_hawk.sqlite3`) to version control.
2. The database will be automatically created on first run via `db_conn()`.
3. Seed the database after deployment using the CLI scripts.
4. The seeding logic is deployment-safe: it works with ephemeral filesystems and does not depend on pre-existing database files.

**Environment variables:**
- `DEAL_HAWK_DB_PATH`: Override default database path (default: `data/deal_hawk.sqlite3`)
- `FRONTEND_URL`: Override frontend URL for CORS (optional, production URL hardcoded)
- `PORT`: Railway-provided port for backend service
- `VITE_API_URL`: Frontend environment variable for backend API URL

## Demo Instructions

See `docs/03-roadmap/DEMO_PLAN.md` for the full demo script.

**Quick demo clickpath (2–4 minutes):**
1. Open React overview: show 10×≥3 coverage, "last updated" timestamps
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
1. **Demo video:** Record <10 minute walkthrough demonstrating the full workflow
2. **Final submission:** Prepare demo package with video, repo link, and live deployment URLs

**Future enhancements (post-MVP):**
- Replace fixture connectors with real retailer integrations (APIs or RSS feeds)
- Add external alert delivery (email, Slack, Discord, Zapier)
- Implement background scheduling for automated ingestion
- Add multi-user support with authentication
- Migrate from SQLite to Postgres for production scale
- Backend persistence for Push Deal workflow (currently session-only)
- Custom domain setup for production URLs
