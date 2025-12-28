# ROI Prioritization

## Purpose

Rank the opportunity hypotheses identified in `OPPORTUNITY_ID.md` using a lightweight ROI heuristic so we can **select one sprint MVP** with a defensible “why this, why now” rationale. This matches the sprint expectation: **clear prioritization based on measurable impact**, plus ROI hypotheses and MVP selection rationale.  

## Inputs (Discovery artifacts)

* Opportunity backlog: `OPPORTUNITY_ID.md` (O1–O12) 
* Interview: `Int_Exec_1.md` (explicit constraints: speed in identifying opportunities + notifying buyers; comms doesn’t scale; automation appetite)  
* Process map: `As-Is-Purchasing-Cycle.pdf` (bottlenecks + optimization opportunities) 

---

## Scoring rubric (1–5)

### Criteria

* **Impact (35%)**: Expected effect on top business goal (increase deals/day, win deal window, activate buyers, retain buyers).  
* **Speed-to-Value (25%)**: Can I demo something meaningful in 48 hours? (see also: feasibility)
* **Feasibility (25%)**: Within constraints (public/permissible data; ToS compliance; integrations we can validate) and buildable with production-grade hygiene.  Also... technical finesse needed.... 
* **Risk (15%)**: Lower risk scores higher (compliance risk, ops change risk, dependency risk). Not super concerned ab this at this stage. 

**Weighted score =** 0.35*Impact + 0.25*Speed + 0.25*Feasibility + 0.15*Risk

> Note: These are **relative** scores used to force a decision. Baseline metrics (e.g., current deals/day, current minutes-to-post) will be measured during MVP build validation. 

## Ranked opportunities (ROI heuristic)

| Rank | Opp | Impact | Speed | Feas | Risk | Weighted | ROI rationale (grounded to discovery)                                                                                                                                |
| ---: | :-: | :----: | :---: | :--: | :--: | -------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    1 |  O4 |    3   |   5   |   5  |   5  |     4.30 | Fastest win: posting templates/rules compress time in the deal window; low integration risk; bundles well into MVP. Phase 1 lag explicitly hurts the window.         |
|    2 |  O1 |    5   |   4   |   4  |   3  |     4.20 | Directly attacks the stated growth constraint: “finding the deals” + manual monitoring caps throughput/day. Some ToS risk if scraping—must stay compliant.           |
|    3 | O11 |    4   |   3   |   5  |   5  |     4.15 | Cross-cutting enabler: deterministic automation reduces human input and avoids “AI vaporware” skepticism; also aligns with engineering standards.                    |
|    4 |  O3 |    4   |   4   |   4  |   4  |     4.00 | Connects scouting → posting: turns signals into “candidate deal ready to post,” addressing the explicit speed constraint (identify → notify).                        |
|    5 |  O7 |    3   |   4   |   4  |   5  |     3.80 | Comms scalability is explicitly called out (200–500 hard; goal 25k). Low-risk improvements possible via message reuse/policy clarity.                                |
|    6 |  O5 |    4   |   4   |   3  |   4  |     3.75 | Multi-channel distribution is required to win the deal window; current execution “not doing a great job.” Integration feasibility depends on tooling but demoable.   |
|    7 |  O2 |    3   |   3   |   4  |   4  |     3.40 | Helpful but secondary: independence from buyer tips improves quality; doesn’t directly prove the speed loop alone.                                                   |
|    8 |  O6 |    3   |   3   |   3  |   4  |     3.15 | Measurement layer (“who saw what, when”) matters, but adds complexity; best as an add-on if time remains.                                                            |
|    9 |  O8 |    3   |   2   |   3  |   4  |     2.90 | Valuable, but commitment systems start touching operational data and require downstream integration to prove ROI in sprint.                                          |
|   10 | O10 |    3   |   2   |   3  |   4  |     2.90 | Retention lever (payout speed), but proving it requires finance/payout integration or time-based observation beyond sprint.                                          |
|   11 |  O9 |    3   |   1   |   2  |   3  |     2.25 | Warehouse matching/exceptions are real, but too operational/integration-heavy for the demo timebox.                                                                  |
|   12 | O12 |    4   |   1   |   1  |   2  |     2.20 | Strategic, but not a sprint MVP: replacing third-party platform is a roadmap theme, not a 48-hour proof.                                                             |

## MVP selection (why this, why now)

### Recommended sprint MVP wedge

**MVP = O1 + O3 + O4 + O5 (implemented with O11 principles).**  
>> confirms prelim hypothesis !!!

**Why this wedge is defensible from discovery**

* Exec explicitly states the constraint is **speed in identifying purchase opportunities + notifying buyers fast enough**. 
* The As-Is map flags the exact bottlenecks this wedge hits: **manual monitoring caps deals/day** and **posting + broadcast latency loses the deal window**. 
* It is demoable end-to-end in a timebox with public/synthetic data if we keep integrations minimal and deterministic.  

### ROI hypothesis (investment vs return)

* **Investment (sprint):** Build a deterministic pipeline that:

  1. ingests permissible deal signals (synthetic/public)
  2. normalizes to a candidate deal object (basically, compared to a defined base price, is this product on sale?)
  3. produces a “ready-to-post” listing (templates/rules) (TO BE: specific text format, confirmed by follow up question to EXEC 1)
  4. triggers distribution events (at least one channel in demo... mock text?).  
* **Return (ideal north star metrics):**

  * higher **candidate deals/hour** vs baseline manual loop,
  * lower **minutes-to-post** per deal (template-driven),
  * lower **time-to-broadcast** from deal detection to buyer notification event.  

## Key risks + mitigations (explicit)

* **Retailer ToS / robots constraints:** prefer permissible sources/APIs; no aggressive scraping; mock external calls for tests.  
>> biggest concern
* **“AI vendor skepticism”:** keep the pipeline deterministic and observable; any “smart” step is isolated and optional.  
>> classic case of "does this rlly need AI or just a smart pipeline"
