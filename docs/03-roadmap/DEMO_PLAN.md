# Demo Plan (POC)

## Demo narrative (what this proves)
- We can continuously track price movements across retailers
- We can compute meaningful deltas over time windows
- We can turn price changes into alertable events (simulated + tested)

---

## Pre-demo setup
1) Seed DB
2) Run 1–2 ingest cycles
3) Run simulation once to force an alert

---

## Live demo clickpath (2–4 minutes)
1) Open React overview: show 10×≥3 coverage, "last updated"
2) Click a product/listing: show snapshot history + delta window
3) Trigger “Run ingest now”: show timestamp and/or price changes update
4) Trigger “Simulate drop”: show an `AlertEvent` created
5) Open alert log: show alert preview + event record

---

## Backup plan
- If live ingest is slow: use pre-seeded snapshots and only demo history + alert simulation
- If one listing breaks: demo with a known-good listing (fixtures are deterministic)

---
