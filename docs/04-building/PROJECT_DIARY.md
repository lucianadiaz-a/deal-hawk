# Project Diary

Running notes during the live build. Not formal tradeoffs—just breadcrumbs to preserve intent, sequence, and “why” decisions while moving fast.

Capture here:
- mental models / framing
- rationale for build order
- gotchas + fixes
- TODOs worth remembering

---

## 2025-12-28 — Baseline POC framing

**Goal:** Prove the core mechanism end-to-end with minimal failure modes.

**Must prove**
1) Catalog representation (products × retailers)
2) Persistent price snapshots over time
3) Delta computation over a configurable window
4) Alert event creation from deltas
5) UI can render all of the above reliably

**Explicitly not proving yet**
- Live retailer scraping / network sourcing
- Real-time streaming
- External notifications (email/Slack/Discord)
- Production-grade architecture

If (1)–(4) aren’t deterministic and repeatable, everything else is theater.

---

## 2025-12-28 — Why fixtures + SQLite first

**Fixture connector** is intentional:
- removes ToS/network fragility while validating schema + logic
- provides deterministic price movement for repeatable demos/tests
- keeps focus on the core pipeline: seed → ingest → history → delta → alert

**SQLite** is the simplest persistent store that supports time-window queries with trivial setup.

---

## 2025-12-28 — Idempotent seeding

Made `scripts/seed_db.py` safe to run repeatedly without multiplying products/listings.

**Approach**
- Products: `INSERT OR IGNORE`, then fetch existing/new IDs
- Retailers: already idempotent (`UNIQUE(name)` + `INSERT OR IGNORE`)
- Listings: upsert behavior (must avoid destructive REPLACE semantics)

**Reasoning**
Prefered idempotent seeding over a “reset DB” workflow so reruns preserve accumulated `price_snapshots` and `alert_events`, and keep usage simple (`python scripts/seed_db.py` anytime).

---

## 2025-12-28 — Seed/ingest integrity guardrail (pytest)

Added `tests/test_seed_integrity.py` as a regression net to ensure:
- seed is non-destructive and idempotent
- ingest appends snapshots exactly as expected

**Invariants enforced**
- A: `price_snapshots` / `alert_events` never decrease after seed
- B: `products` / `retailers` / `listings` never increase after seed
- C: listing IDs remain stable across seed runs
- D: ingest adds exactly 1 snapshot per active listing
- E: products uniqueness is enforced (unique index present)
- F: no duplicate products exist after seed

**Notes**
- The test is pytest-native (`pytest -q`) but can also run directly.
- This became the “quality gate” before merges.

---

## 2025-12-28 — DB uniqueness + migration reality

Attempting to enforce product uniqueness surfaced a common SQLite gotcha:
- Updating `CREATE TABLE IF NOT EXISTS` does not retrofit constraints onto an existing DB.
- Existing duplicates can prevent adding a unique index.

**Resolution**
- Ensure uniqueness is enforced via a UNIQUE index.
- If legacy duplicates exist, handle repair so the index can be created (without wiping history).

(Keep repair logic explicit and well-scoped—avoid “surprise migrations” during normal runs.)

---

## 2025-12-28 — Core pipeline services

Established a clean, testable service layer (stateless functions over a DB connection):

- **`ingest.py`**: for each active listing, compute fixture price and write a snapshot (1 per listing per run)
- **`pricing.py`**: compute delta over a window:
  - current = latest snapshot
  - window start = earliest snapshot within window
- **`alerts.py`**: create `alert_events` when `delta_pct <= -threshold_pct`, with basic dedupe to prevent spam

**Reasoning**
Stateless services + dataclass outputs keep dependencies explicit, make testing straightforward, and avoid coupling UI to SQL.

---

## 2025-12-28 — Fixture connector deterministic pricing

Implemented `backend/connectors/fixtures.py` for deterministic offline prices:

**Formula**
`price = base + step * (snapshot_count % period)`

**Why**
- reproducible price motion across runs
- easy to trigger alerts (negative step)
- no network calls, no ToS risk, no flaky scraping

---

## 2025-12-28 — Streamlit UI baseline

Built `app/main.py` to complete the end-to-end proof in a demoable UI.

**UI structure**
- **Overview**: all active listings + current, window start, delta, delta%
- **Listing detail**: metrics + snapshot history + per-listing alert events
- **Alert log**: all alert events across listings

**Controls**
- window hours
- alert threshold
- “Run ingest”
- “Evaluate alerts”

**Reasoning**
Streamlit is the fastest path to an interactive demo. UI queries are kept behind the service layer (no scattered SQL in UI).

---

## 2025-12-28 — DB connection + performance basics

Implemented `backend/db.py` with:
- context-managed connections + transaction handling
- pragmas (`foreign_keys`, WAL, etc.)
- schema + indexes for time-window queries

**Why**
Keeps DB access safe and consistent; supports the core use case (latest + window-start lookups) without premature complexity.
