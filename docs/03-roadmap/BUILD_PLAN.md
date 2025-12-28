# Build Plan (POC)

This is the implementation plan for the Price Monitoring POC (deal hawk)

## Architecture (MVP)
- Streamlit UI in `app/`
- Domain + DB + services as a small Python package in `backend/`
- SQLite as the system of record (local file)
- Retailer “connectors” start as fixtures (swap later)

See `docs/00-overview/TRADEOFFS.md` for decision rationale.

## Data model (SQLite)
- `products`
- `retailers`
- `listings` (product_id, retailer_id, url)
- `price_snapshots` (listing_id, price_cents, currency, captured_at)
- `alert_events` (listing_id, triggered_at, prev_price_cents, new_price_cents, rule_name, message_preview)

## Work breakdown

### 1) DB + schema
**Deliverables**
- `backend/db.py` (connection + migrations/init)
- schema creation function (idempotent)

**Acceptance**
- local sqlite file created
- tables exist
- basic insert/query works

### 2) Seed data
**Deliverables**
- `data/seed_listings.json` (10 products × ≥3 retailers)
- `scripts/seed_db.py`

**Acceptance**
- running seed populates products/retailers/listings deterministically

### 3) Price ingestion
**Deliverables**
- `backend/connectors/fixtures.py`
- `backend/services/ingest.py` (writes `price_snapshots`)
- `scripts/run_ingest.py`

**Acceptance**
- each ingest cycle writes snapshots for all seeded listings
- timestamps update; history grows

### 4) Delta computation
**Deliverables**
- `backend/services/pricing.py` (current price + delta over window)

**Acceptance**
- returns correct deltas given controlled snapshot data

### 5) Alert evaluation + simulation
**Deliverables**
- `backend/services/alerts.py` (creates `alert_events`)
- simulation mechanism (fixture override or script)

**Acceptance**
- deterministic alert trigger using controlled price movement
- event stored with preview text

### 6) Streamlit UI
**Deliverables**
- overview table (current + delta + last updated)
- detail view (history)
- alert log (events + preview)

**Acceptance**
- demo clickpath is stable and repeatable

### 7) Tests
**Deliverables**
- tests for delta math
- tests for alert trigger

**Acceptance**
- `pytest` passes locally with fixtures connector + sqlite