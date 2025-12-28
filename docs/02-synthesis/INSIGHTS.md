### 1. Growth is mechanically constrained by “deal volume,” and deal volume is constrained by scouting speed

**Insight**
The business’s near-term growth strategy is straightforward: recruit more buyers → requires posting more deals → therefore the primary lever is expanding purchasing capability by increasing the rate of deal discovery.

**Why it matters**
This makes “deal scouting throughput” the highest-leverage workflow moment: improvements here propagate downstream (posting frequency, buyer activation, revenue).

**Evidence (quotes)**

* “We need to grow our buying group… to attract those buyers, we need to post a lot of deals.”
* “We are trying to improve our scouting of the deals… willing to invest in anything that allows us to expand our purchasing capability, because this is the main restriction holding back our growth.”

### 2. Deal discovery is multi-source, but buyer-supplied leads are explicitly unreliable due to cherry-picking incentives

**Insight**
Deal leads come from (1) buyers, (2) other buying groups, and (3) retailers/marketplaces. But buyer tips are structurally biased (buyers optimize for themselves), so the org wants independent, real-time scouting.

**Why it matters**
Your MVP should not depend on buyer-submitted deals as the primary signal. It should treat buyer tips as *optional enrichment*, not the core ingestion path.

**Evidence (quotes)**

* “The first front of deal info is direct information from the buyers… But we don’t like to depend on the buyers, because the buyers will cherry pick whatever it will be more convenient for them.”
* “We are looking into… tools that will help us scout the deals and… give us the information real time.”
* “Then we go to other groups… we look at what they’re buying… [and] the merchants directly… they post and advertise these deals… on their own websites.”

### 3. “Alerts exist,” but the operating reality is still manual monitoring (and fragile)

**Insight**
Even with alerts, scouting is still largely manual. This suggests an automation gap not at the “notification exists” layer, but at the “turn signals into structured candidate deals” layer.

**Why it matters**
A winning workflow improvement is likely: ingestion → normalization → candidate scoring → “ready-to-post” output (not just “more alerts”).

**Evidence (quotes)**

* “We have alerts… but it’s pretty much… a manual.”

### 4. A single operator is bridging scouting → posting → buyer comms (key-person bottleneck)

**Insight**
One person (EMPLOYEE A) is doing deal collection, posting to the platform, and managing communications across buyers. That concentrates throughput and quality risk into one role.

**Why it matters**
This is exactly the kind of “human throughput ceiling” automation should relieve: reduce context switching, reduce copy/paste, standardize deal objects, and make distribution repeatable.

**Evidence (quotes)**

* “We have EMPLOYEE A she’s responsible for collecting information about deals… [and] post the deals… and at the same time, she will manage the communication within the multiple buyers.”

### 5. Distribution is multi-channel, but execution quality is inconsistent, and scaling comms is a core blocker

**Insight**
Buyers *should* receive emails when deals are posted, plus chat/Discord/social—yet they explicitly say they “were not doing a great job” at alerts. Scaling comms is described as hard even at 200–500 buyers (target is 10×+ growth).

**Why it matters**
This points to an “activation funnel” problem: it’s not enough to post a deal; they need fast, reliable broadcast + some notion of reach/acknowledgement.

**Evidence (quotes)**

* “They are supposed to get an email… and then we have a community chat… discord… social media… We were not doing a great job in terms of sending emails and putting alerts out.”
* “It’s very hard to communicate with 25,000 people, even with 200 or 500.”
* “Our buyer base is growing, but the ambition is that we need to multiply it by 10.”

### 6. The “speed problem” is specifically: identify purchase opportunities fast, then notify buyers fast enough to catch the deal window

**Insight**
They describe the main constraint as end-to-end speed across two adjacent steps: (1) identifying purchase opportunities and (2) notifying a wide buyer network in time.

**Why it matters**
This is a clean, demoable MVP boundary: compress “time-to-candidate-deal” and “time-to-broadcast” with explicit timestamps and measurable deltas.

**Evidence (quotes)**

* “We’re held back by the lack of speed in identifying purchase opportunities, and then… notifying a wide network of… buyers fast enough.”

### 7. Delay has an explicit economic framing: opportunity cost (lost revenue) and competitive benchmarking

**Insight**
They frame latency as lost revenue opportunity and benchmark themselves against other groups at higher scale.

**Why it matters**
Your synthesis can anchor ROI without inventing numbers: the stakeholder already ties speed → volume → revenue. Your MVP success metrics should directly measure speed and throughput.

**Evidence (quotes)**

* “It’s an opportunity cost, because you’re losing the opportunity of selling more products.”
* “At the end of the day, what you lose is… generating more revenue.”

### 8. Buyer loyalty is not a given; “pays faster / pays better” is a major selection driver (so payout policy comms matters)

**Insight**
Buyers aren’t exclusive; they choose groups based on payout speed/quality and incentives. This means the system’s ability to clearly communicate payout policies and execute reliably impacts growth.

**Why it matters**
Even if your MVP focuses upstream (scouting + distribution), the broadcast payload should include clear payout terms and reduce confusion. Longer-term, payout speed/transparency is a differentiation axis.

**Evidence (quotes)**

* “They’re not exclusive… The reality is they will go to the groups that will pay faster… and will pay better.”
* “We put incentives… crypto and travel rewards… to attract these buyers.”

### 9. There’s strong appetite for automation, but prior vendor attempts created skepticism (needs credibility + deterministic workflow)

**Insight**
They want “automatic processes” to reduce constant manual input. They tried a vendor claiming AI capability and churned due to lack of proven expertise/results.

**Why it matters**
Your demo needs to feel production-minded: deterministic pipeline, observable outputs, minimal “AI magic,” and a clear proof loop (inputs → outputs → metrics).

**Evidence (quotes)**

* “We are trying to create automatic processes where we don’t need to humanly input everything… that’s one of the limitations that we have today.”
* “We hired a guy… promised… AI tools… but… he didn’t really had a proven concept… so we decide to just not continue.”

### 10. Tooling/platform dependence is costly; they’re open to proprietary tooling and want to stop paying for a third-party distro platform

**Insight**
Their distribution platform is a third-party service provider they pay heavily for; longer-term they expect they may need their own ERP/platform. They also explicitly like the idea of building proprietary tools for buyers.

**Why it matters**
This supports an MVP positioning: start with a narrow workflow wedge (scouting + structured deal objects + alerts) that can later become internal platform capability.

**Evidence (quotes)**

* “We… use third party service provider… We pay him a stupid amount of money every year… it would be cool to not do that.”
* “If we can find tools that we can give to buyers, that will be amazing… we will love to develop something… proprietary.”