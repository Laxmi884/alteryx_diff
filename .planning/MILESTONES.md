# Milestones

## v1.0 MVP (Shipped: 2026-03-07)

**Phases completed:** 9 phases, 27 plans
**Timeline:** 2026-02-28 → 2026-03-07 (7 days)
**Lines of code:** ~5,844 LOC Python (src/ + tests/)
**Tests:** 105 passing, 1 xfailed (intentional GUID stub)
**Git commits:** 114

**Delivered:** A CLI tool (`acd diff`) that compares two Alteryx `.yxmd` files and produces a self-contained HTML report with color-coded diff summary, expandable per-tool configuration changes, and an embedded interactive workflow graph — with zero false positives from canvas layout noise.

**Key accomplishments:**
1. Immutable 4-stage pipeline (Parser → Normalizer → Matcher → Differ) with typed frozen dataclasses across all stages
2. lxml-based parser with typed `ParseError` exception hierarchy that rejects malformed `.yxmd` files before any processing
3. C14N canonicalization + GUID/timestamp stripping eliminates all Alteryx XML noise false positives (whitespace, attribute ordering, auto-generated metadata)
4. Two-pass node matcher (ToolID exact lookup + Hungarian algorithm fallback with 0.8 cost threshold) prevents phantom add/remove pairs on ToolID regeneration
5. Field-level diff engine using DeepDiff with full before/after values; connection diffs via frozenset symmetric difference on 4-tuple anchors
6. Self-contained HTML report (Jinja2, inline CSS/JS, ALCOA+ governance footer) with embedded vis-network 9.1.4 interactive graph — no CDN, air-gap capable
7. `acd diff` Typer CLI with predictable exit codes (0/1/2), `--json`, `--include-positions`, `--canvas-layout` flags

**Requirements:** 24/24 v1 requirements satisfied
**Audit:** tech_debt — no critical blockers; 6 deferred browser-UX and GUID verification items

**Archive:**
- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`

---
