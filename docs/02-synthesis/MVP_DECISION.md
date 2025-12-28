# MVP Decision (POC scope)

## Decision
We will build a **Price Monitoring POC** that tracks a small fixed set of products across multiple retailers, persists price history, visualizes recent price movement, and demonstrates (via simulation + tests) how “deal alerts” would trigger.

This POC is intentionally scoped to validate the highest-leverage bottleneck identified in discovery: **manual deal scouting / lack of speed in identifying purchase opportunities** (OPPORTUNITY_ID: O1).

## One-sentence MVP scope
Track ~10 products across **≥3 retailers**, record price snapshots over time, show price deltas over the last X hours, and demonstrate a simulated “alert trigger” flow (UI + tests).

## Why this MVP (why this, why now)
- Discovery indicates the growth constraint is upstream: **scouting speed** and **manual monitoring** (OPPORTUNITY_ID: O1).
- This POC proves the core mechanism: **automated monitoring → normalized price history → detectable change → alertable event**.
- It is feasible in a couple hours while still meeting the sprint’s “small but real workflow” and “tests for core logic” bar.

## Opportunity trace
### Included (from OPPORTUNITY_ID.md)
- **O1:** Automate deal scouting into structured candidate signals  
  *POC translation:* product+retailer price signals become structured “PriceSnapshot” + “PriceChange” objects.

## IN SCOPE

### Functionality
1) **Product set**
   - Seed a fixed list of ~10 products with links/identifiers for ≥3 retailers.

2) **Price collection (polling)**
   - Run a fetch cycle that collects current price per product/retailer and writes `PriceSnapshot` rows.
   - “Live” proof is: the fetch cycle runs on demand and produces fresh timestamps; historical movement is shown over the last X hours based on stored snapshots.

3) **Visualization**
   - React dashboard shows:
     - current price per retailer
     - delta over last X hours
     - simple trend view (table + optional chart) per product

4) **Alert simulation**
   - Implement alert evaluation logic (e.g., % drop or absolute threshold).
   - Provide:
     - deterministic unit tests that simulate snapshots and verify alert triggering
     - a UI “simulate trigger” action (or seeded historical data) that produces an `AlertEvent`
   - Output is an “alert preview” card showing what would be sent (message template), without actually integrating email/Discord.

## Out of scope (hard cuts)
- Real-time guarantee of catching a *live* price drop during the demo window.
- Multi-channel integrations (email/Discord/Zapier). Only “preview + event log” in this POC. MAYBE ACHIEVABLE??? TBD
- Any scraping that violates retailer ToS/robots. If a retailer requires an API key or disallows automated access, that connector is stubbed with fixtures and clearly labeled “simulated.”

## Success metrics (ideal demo-measurable)
- **Coverage:** ≥10 products × ≥3 retailers seeded and visible in the UI
- **History:** UI shows last X hours of snapshots and computed deltas
- **Alert proof:** tests demonstrate alert triggering from controlled price movements; UI shows alert preview/event creation

## Graduation path (what a Tenex-backed pilot would add)
This POC graduates into a production pilot by adding:
- scalable product catalog management (hundreds/thousands SKUs)
- robust data sourcing (permissible APIs/feeds, rate limiting, ToS-safe connectors)
- candidate deal scoring and normalization (O3)
- publish-ready deal objects and posting workflows (O4)
- real distribution + segmentation + acknowledgement telemetry (O5/O6/O7)
- full observability, retries, and alert routing via Zapier/webhooks


