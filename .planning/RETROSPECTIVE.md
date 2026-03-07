# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-07
**Phases:** 9 | **Plans:** 27 | **Timeline:** 7 days (2026-02-28 → 2026-03-07)

### What Was Built

- Immutable 4-stage pipeline (Parser → Normalizer → Matcher → Differ) with typed frozen dataclasses throughout
- C14N canonicalization + GUID/timestamp stripping normalization layer that eliminates all Alteryx XML noise sources
- Two-pass node matcher: exact ToolID lookup first, then Hungarian algorithm (scipy) with 0.8 cost threshold for ToolID-regeneration scenarios
- Field-level diff engine (DeepDiff) with full before/after values; connection diffs via frozenset symmetric difference on 4-tuple anchors
- Self-contained HTML report with Jinja2 template, lazy-load diff data via JSON-in-script-tag, embedded vis-network 9.1.4 graph (702KB vendored UMD, no CDN)
- ALCOA+ governance footer (`<details>` with SHA-256 hashes, file paths, timestamp) for audit compliance
- `acd diff` Typer CLI with exit codes 0/1/2, `--json`, `--include-positions`, `--canvas-layout` flags
- 105 tests (27 plans × fixture-per-plan pattern); 1 intentional xfail (GUID stub)

### What Worked

- **Fixture-per-phase ToolID allocation** — allocating ToolID ranges per phase (Phase 1: 1-100, Phase 2: 1-2, Phase 3: 101-201, etc.) prevented collision across all test files without coordination overhead
- **Frozen dataclasses throughout** — `frozen=True, kw_only=True, slots=True` on all pipeline types caught mutation bugs at type-check time; zero runtime mutation errors across 9 phases
- **gsd-tools plan/execute loop** — clear boundary between plan (PLAN.md) and execute (code) with SUMMARY.md completion signal meant each plan was independently atomic; no incomplete half-states
- **Vendoring vis-network early** — deciding in Phase 8 to vendor the UMD bundle instead of CDN was the right call; self-contained HTML output is the core deliverable value
- **Hexagonal architecture from day one** — CLI built last as 15-line adapter over `pipeline.run()` confirmed the architecture. REST API path is genuinely zero rearchitecting.

### What Was Inefficient

- **JSONRenderer schema divergence** — Phase 6 built a `JSONRenderer` with one schema; Phase 9 built `_cli_json_output()` with a different schema. Both cover CLI-03, but two divergent contracts exist. Should have wired JSONRenderer into CLI from the start.
- **GUID_VALUE_KEYS left empty** — `patterns.py` ships with an empty frozenset. The normalization mechanism is in place but untested against real `.yxmd` files. This will cause false-positive config_hash differences if Alteryx embeds session GUIDs in tool configs. Should have sourced a real `.yxmd` file before Phase 3 execution.
- **Phase 3 cross-phase dependency** — NORM-04 (`--include-positions`) required Phase 5 differ + Phase 9 CLI. The requirement was correctly marked "partial" in Phase 3 but generated audit noise. Cleaner to own the flag in Phase 9's requirements from the start.

### Patterns Established

- **Fixture ToolID allocation:** Phase N uses ToolID range `(N-1)*100 + 1` → `N*100`. Prevents cross-phase fixture collision.
- **Renderer pattern:** Each renderer is a class in `renderers/<name>_renderer.py`, re-exported from `renderers/__init__.py`. Fragment renderers (GraphRenderer) produce HTML fragments; HTMLRenderer owns the document wrapper.
- **JSON-in-script-tag:** Lazy-loading diff data via `<script type="application/json" id="diff-data">` + `JSON.parse()` avoids innerHTML security issues and enables DOM-API lazy-load.
- **Pre-commit mypy hook additional_dependencies:** Every runtime dep without stubs needs `mypy --strict` overrides in `pyproject.toml` AND entry in `additional_dependencies` of `.pre-commit-config.yaml`. Forgetting either causes hook failures.

### Key Lessons

1. **Validate against real files before building stripping logic.** `GUID_VALUE_KEYS` should be populated from real `.yxmd` inspection before Phase 3 execution, not left as a post-ship task.
2. **Decide JSON schema ownership before building two renderers.** JSONRenderer (Phase 6) and `_cli_json_output()` (Phase 9) diverged because ownership wasn't explicit. Pick one schema and wire everything to it from Phase 6.
3. **Vendoring beats CDN for self-contained output.** Air-gap requirement makes CDN non-negotiable to exclude. Decide vendor vs. CDN at architecture stage (Phase 1 constraints), not at implementation stage (Phase 8).
4. **`slots=True` incompatibility with `@property` is a Python 3.11 footgun.** Document the exception for `DiffResult` in the architecture decision table, not just in code comments.

### Cost Observations

- Sessions: ~7–9 across 9 phases
- Notable: Phase 5 (diff engine) and Phase 8 (visual graph) had the most plan revision cycles — highest architectural complexity. Phases 3-4 were fastest (2-4 min/plan) due to clear algorithmic specifications.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 MVP | 9 | 27 | Initial GSD process; fixture-per-phase pattern established |

### Cumulative Quality

| Milestone | Tests | xfail | Notes |
|-----------|-------|-------|-------|
| v1.0 MVP | 105 | 1 | 1 intentional xfail (GUID_VALUE_KEYS stub) |

### Top Lessons (Verified Across Milestones)

1. Validate against real input files before building normalization/stripping logic — don't ship empty key registries.
2. Decide JSON contract ownership before implementing multiple renderers — divergent schemas become tech debt immediately.
