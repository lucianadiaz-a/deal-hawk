### Sources used (Discovery artifacts)

* **Interview:** `Int_Exec_1.md` (GM interview)
* **Process map:** `As-Is-Purchasing-Cycle.pdf` (end-to-end workflow + bottlenecks + opportunities)

### How opportunities were derived (method)

Each opportunity below is:

* anchored to a **workflow phase** in the As-Is map, and
* derived from one or more **Insights (I#)**, and
* backed by at least one **verbatim quote** from the interview and/or a **specific bottleneck statement** in the process map.

> This backlog is not a “feature list.” It is a **rankable set of outcome hypotheses** produced from discovery, to be scored in `ROI_PRIORITIZATION.md`.

----------------------------------------

## Insight → Opportunity trace map 
> I# = Insight # that can be traced back to `INSIGHTS.md`
> O# = The opportunities derived from analyzing that/those specific insights (found below)

* **I1 / I6 / I7** (growth constrained by deal volume; speed is the constraint; delay = opportunity cost) → **O1, O3, O4, O5**
* **I2 / I3** (buyer tips unreliable; monitoring still manual) → **O1, O2, O3**
* **I4 / I5** (single operator bottleneck; comms quality inconsistent; multi-channel) → **O4, O5, O6**
* **I8** (buyers choose groups that pay faster/better) → **O10**
* **I9 / I10** (desire automation + vendor skepticism; open to proprietary tools; third-party platform cost) → **O7, O11**

----------------------------------------

# Opportunity backlog (Outcome hypotheses)

## O1: Automate deal scouting into structured “candidate deals”

* **Workflow phase:** Phase 0 — Deal Scouting
* **Derived from insights:** I1, I2, I3
* **Outcome:** Increase deals/day by converting multi-source signals into a normalized candidate deal object (product + retailer + price window), reducing manual monitoring.
* **Evidence:** Deal scouting is explicitly the throughput ceiling and “manual monitoring caps deal throughput/day.” Stakeholder says the constraint is “finding the deals” and they want tools that scout deals “real time.” Also: “we have alerts… but it’s pretty much… a manual.”

## O2: Reduce dependence on biased buyer tips by prioritizing independent sources

* **Workflow phase:** Phase 0 — Deal Scouting
* **Derived from insights:** I2
* **Outcome:** Improve deal signal quality by treating buyer tips as optional enrichment, and prioritizing retailer sites + other buying groups as primary feeds.
* **Evidence:** “we don’t like to depend on the buyers, because the buyers will cherry pick…” The process map lists inputs as “buyer tips, other buying groups, retailer sites.”

## O3: Candidate deal qualification + “ready-to-post” packaging

* **Workflow phase:** Phase 0 → Phase 1 handoff
* **Derived from insights:** I3, I6
* **Outcome:** Reduce time from “signal detected” → “postable deal” by packaging candidates with required fields + basic validation so posting is fast and consistent.
* **Evidence:** The As-Is map defines the Phase 0 output as “candidate deal ready to post.” Stakeholder frames the bottleneck as speed: “held back by the lack of speed in identifying purchase opportunities… [and] notifying… buyers fast enough.”

## O4: Shrink deal definition & posting time via templates and rules

* **Workflow phase:** Phase 1 — Deal Definition & Posting
* **Derived from insights:** I4, I6
* **Outcome:** Reduce posting latency by standardizing payout terms + ship-to rules + listing templates so a deal can be published with fewer manual steps.
* **Evidence:** Phase 1 lag “compresses buyer response time during the window.” Posting is currently bundled with other responsibilities: Luisa collects deal info, posts deals, and manages buyer comms.

## O5: Multi-channel broadcast automation with reliable delivery

* **Workflow phase:** Phase 2 — Deal Distribution
* **Derived from insights:** I5, I6
* **Outcome:** Reduce time-to-broadcast and improve consistency by automating “publish → distribute” across email + chat/Discord + social + website.
* **Evidence:** Phase 2 job is “notify the right buyers fast + confirm they received it.” Stakeholder lists channels and admits execution issues: “supposed to get an email… community chat… discord… social media… We were not doing a great job…”

## O6: Buyer awareness + acknowledgement tracking (“who saw what, when”)

* **Workflow phase:** Phase 2 — Deal Distribution
* **Derived from insights:** I5, I6
* **Outcome:** Improve distribution effectiveness by logging delivery status per channel + a lightweight acknowledgement signal (enough to measure and iterate).
* **Evidence:** The As-Is map explicitly defines Phase 2 output as a “buyer awareness event (who saw what, when).” Stakeholder states scale problem and need to “effectively communicate… deals, policies, payouts.”

## O7: Communication scalability (policies + payouts) as a first-class workflow requirement

* **Workflow phase:** Cross-cutting (Distribution + Retention)
* **Derived from insights:** I6
* **Outcome:** Reduce comms load and confusion by centralizing and reusing “policy/payout” messaging tied to deals, instead of ad-hoc explanations.
* **Evidence:** “very hard to communicate with 25,000 people… even with 200 or 500… if we are able to effectively communicate… our deals, our policies, our payouts, that’s going to help.” The As-Is map also flags comms scalability directly.

## O8: Commitment capture integrity to reduce downstream matching issues

* **Workflow phase:** Phase 3 — Buyer Commitment
* **Derived from insights:** (Process-map control point + interview cycle description)
* **Outcome:** Improve matching + payout reliability by enforcing structured commitment records (qty, identity, timestamps) that reliably join to inbound shipments.
* **Evidence:** Phase 3 output is “commitment record used for receiving + payout matching.” Interview confirms commitment precedes receiving and enables pay order creation.

## O9: Receiving scan → automated match + exception routing

* **Workflow phase:** Phase 5 — Receive, Scan, & Intake
* **Derived from insights:** (Process map bottleneck + interview cycle description)
* **Outcome:** Increase warehouse throughput by automating shipment→buyer matching at scan time and routing exceptions with clear next actions.
* **Evidence:** Process map: “Manual match/exception handling slows throughput.” Interview describes scan→pay order creation dependency.

## O10: Payout speed + transparency as a retention lever

* **Workflow phase:** Phase 6 — Issue Payout
* **Derived from insights:** I8
* **Outcome:** Improve buyer retention by increasing payout transparency and reducing uncertainty around payout timing.
* **Evidence:** Buyers choose groups that “pay faster… [and] pay better.” Process map: “Payout timing directly affects buyer retention.”

## O11: Reduce constant human input via deterministic automation (and avoid “AI vaporware”)

* **Workflow phase:** Cross-cutting
* **Derived from insights:** I9
* **Outcome:** Reduce manual work by implementing deterministic automation steps (observable + testable), with any “smart” step isolated and optional.
* **Evidence:** “create automatic processes where we don’t need to humanly input everything…” They previously stopped working with a vendor because the vendor lacked proven capability.

## O12: Long-term FUTURE SELL ON!!: reduce dependency on costly third-party distro platform; build proprietary tools

* **Workflow phase:** Platform strategy
* **Derived from insights:** I10
* **Outcome:** Gradually replace third-party distro platform costs by building modular internal capabilities; eventually deliver proprietary buyer tooling.
* **Evidence:** “we might need to… build our own platform… we just use third party… We pay him a stupid amount of money every year.” Also: desire to “develop something… proprietary.”

