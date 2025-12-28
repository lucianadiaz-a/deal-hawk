# Roadmap

This roadmap documents what we will build now (POC) and what “graduation” would require later, based on discovery + MVP decision.

## Now — Price Monitoring POC (selected MVP)

**Goal**
Prove the core mechanism: automated monitoring → normalized price history → detectable change → alertable event.

**In scope**
- Seed ~10 products across ≥3 retailers (fixtures allowed)
- Store price snapshots over time
- Compute deltas over a configurable window (e.g., last X hours)
- Generate an `AlertEvent` when a rule triggers (simulated trigger + tests)
- Streamlit UI:
  - current prices + deltas
  - snapshot history (per listing/product)
  - alert log + alert preview

**Out of scope**
- External alert delivery (email/Slack/Discord/Zapier)
- Any ToS/robots-violating scraping
- Multi-user hosting, auth, background workers

**Success criteria**
- Coverage: ≥10×≥3 visible and updating
- History: snapshots + deltas viewable in UI
- Proof: deterministic tests for alert trigger + UI shows created alert events

## Next — “Graduation” to Pilot (not built now)

- ToS-safe sourcing (approved APIs/feeds, rate limiting, retries)
- Larger catalog + normalization/scoring
- Distribution workflows + segmentation
- Observability + failure handling + scheduling
- API boundary (FastAPI) + deployable runtime
