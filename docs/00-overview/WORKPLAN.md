# Workplan — Deal Hawk (48-hour sprint)

## Objective
Produce a Build First submission that demonstrates:
- user-centered discovery under tight time constraints
- clear prioritization based on measurable impact
- a functional prototype that proves the approach
- production-grade hygiene (repo, docs, tests, deploy)

## Workstreams
### A) Discovery (Problem Mining)
**Outputs**
- lightweight as-is workflow map(s)
- 2 stakeholder interviews (Exec-01, MAYBE Exec-02) with transcripts (anonymized)
- list of pains/bottlenecks with quantified signals (time/$/frequency)
- constraints & risks (data access, compliance, change management)

**Method**
- Start interviews with: role → excited about AI → skeptical about AI
- Walk through day-to-day / workflow step-by-step
- Quantify impact and prior attempts to solve

### B) Synthesis (Turn unstructured → structured)
**Outputs**
- consolidated pain points
- opportunity list (ranked)
- ROI hypothesis per opportunity (investment vs return)
- selection rationale for the sprint MVP (why this, why now)

### C) MVP Definition (Scope + success metrics)
**Outputs**
- one-sentence MVP scope
- explicit success metrics (what improves, by how much)
- acceptance criteria for the demo
- cut list (what will NOT be built)

### D) Build + Integrate (Execution)
**Outputs**
- functional prototype meeting acceptance criteria
- integrations validated end-to-end (where applicable)
- dataset is synthetic/public/permissible

### E) Ship (Deploy + proof it works)
**Outputs**
- deployed demo link(s)
- reproducible local run steps
- smoke test checklist

### F) Demo Package (Submission-ready)
**Outputs**
- <10 min demo video script
- final demo recording (unlisted YouTube)
- YouTube description includes repo + live link(s)
- final README polish

## Timeline (48 hours)
### Phase 1: Set up + Discovery
- repo + docs scaffolding
- interview guide finalized
- 1-2 interviews completed + transcribed
- initial workflow map + quantified pain points

### Phase 2: Synthesis + MVP selection
- synthesize insights
- rank opportunities by ROI and feasibility
- lock MVP scope + acceptance criteria

### Phase 3: Build + validate
- implement MVP incrementally
- validate integration paths
- add tests for core logic

### Phase 4: Deploy + demo
- deploy + smoke test
- finalize README + docs
- record demo video + submit

## Quality gates (must pass)
- No secrets committed (ever)
- No sensitive data in repo (anonymized only)
- Clean git history on `prod` (linear, squashed merges)
- Tests exist for core logic
- Demo is reliable (no “works on my machine”)
- Documentation tells a coherent story from discovery → decision → build → impact
