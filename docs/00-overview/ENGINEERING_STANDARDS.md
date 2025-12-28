# Engineering Standards

These standards exist to keep the sprint fast **without** creating garbage.
If a tradeoff is required, optimize for **reliability + clarity** over cleverness.

## Core principles
- Deterministic workflow first; isolate any “smart” step.
- Small diffs; no drive-by refactors.
- Clear interfaces (schemas/contracts) between components.
- Fail loudly and observably.

## Python baseline
- Python: 3.11+
- Use type hints on all non-trivial functions and all public module APIs.
- Use Pydantic models for all API request/response bodies and internal boundary objects.

## FastAPI standards
- One clear `app` entrypoint.
- Explicit routers per domain (health, products, prices, alerts).
- No business logic inside route handlers; handlers call services.
- Validate inputs and return meaningful HTTP errors (no generic 500s).
- Never log secrets.

## Frontend standards
- UI reads from API/services; avoid embedding core logic in the UI.
- Handle API failure states gracefully (clear error messages).
- Keep state management explicit and minimal.

## Data + database
- Postgres is the system of record.
- Schema changes must be reproducible (migrations, not manual edits).
- Store timestamps in UTC.
- Prefer idempotent writes for ingestion (avoid duplicates).

## Logging + observability
- Use structured logging where feasible (key/value).
- Log: request ids / run ids, key events, failures, timings.
- Never log API keys, auth headers, or sensitive payloads.

## Error handling
- No bare `except`.
- Raise typed exceptions or return explicit error objects.
- Validate assumptions at boundaries (incoming data, external responses).

## Testing requirements (minimum bar)
- Unit tests for:
  - deal detection logic (thresholds, edge cases)
  - parsing/normalization logic (input variations)
- Tests must be deterministic (no network calls).
- If external calls exist, mock them.

## Formatting + linting (enforced)
- Use a formatter + linter (exact tooling decided in setup).
- Code must be consistently formatted before merging to `prod`.

## Repo hygiene
- No secrets in repo. Ever.
- No large binaries in git history.
- No OS junk files (e.g., `.DS_Store`).
- README must include:
  - what it does
  - how to run locally
  - how to configure env vars
  - deployment links (once live)

## Git workflow (required)
- `prod` is linear history only.
- Work on `feature/*` or `chore/*` branches.
- Rebase onto `origin/prod`, squash to 1 commit, PR → merge → delete branch.
