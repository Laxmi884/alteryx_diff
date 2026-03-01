# Project Research Summary

**Project:** Alteryx Canvas Diff (ACD)
**Domain:** Python CLI tool — XML semantic diff, graph analysis, interactive HTML report generation for Alteryx .yxmd workflow files
**Researched:** 2026-02-28
**Confidence:** HIGH (stack verified against PyPI/official docs; architecture patterns well-established; pitfalls confirmed against real Alteryx XML on GitHub)

## Executive Summary

Alteryx Canvas Diff is a CLI-first XML semantic diff tool for Alteryx Designer workflow files (.yxmd). The core problem it solves is real and unsolved: raw XML diffs of Alteryx workflows are useless because Alteryx regenerates ToolIDs, reorders attributes, injects GUID metadata, and shifts canvas positions on every save — producing hundreds of false-positive changes for functionally identical workflows. No existing tool (Alteryx built-in Compare, Simulink, KNIME, DeltaXML) produces a standalone diff report that works without the authoring tool installed. ACD's key differentiator is a self-contained HTML report with an interactive graph visualization — the only format that works for governance reviewers who lack Alteryx Designer licenses.

The recommended implementation is a four-stage immutable pipeline: Parser (lxml 6.0.2) → Normalizer (C14N canonicalization + SHA-256 hashing) → Differ (ID-first matching with Hungarian algorithm fallback via scipy) → Renderer (Jinja2 + pyvis/vis.js inlined). The pipeline is architecturally decoupled from both CLI (Typer 0.24.1) and any future API (FastAPI), following a hexagonal pattern where `pipeline.run(DiffRequest) → DiffResponse` is the single entry point. All stack decisions are verified against current PyPI versions and official documentation with HIGH confidence.

The two make-or-break risks for this project are: (1) ToolID-only node matching, which produces phantom add/remove pairs when Alteryx regenerates IDs — this must be solved in Phase 1 with a two-pass ID-first + similarity-fallback matcher before any diff logic is built on top; and (2) position field leakage into the diff signal, where canvas X/Y coordinates must be strictly separated from the configuration comparison path. Both risks have clear prevention strategies and are addressable in the foundational phase. A third risk — pyvis CDN dependency breaking offline use — is addressable in Phase 2 with a documented workaround (`cdn_resources='in_line'` plus Bootstrap CSS post-processing).

## Key Findings

### Recommended Stack

The stack is Python 3.11+ (required by NetworkX 3.6.1), with lxml 6.0.2 as the sole XML engine. lxml is the decisive choice: it provides C14N 2.0 canonicalization (`etree.canonicalize()`), XPath 1.0, and 5–20x performance over stdlib ElementTree. The canonicalize step solves the attribute-reordering false-positive problem without any custom sorting code. DeepDiff 8.6.1 handles field-level config diffing (after converting tool config XML subtrees to dicts); it is NOT used as the primary diff engine. scipy provides the Hungarian algorithm (`linear_sum_assignment`) for the similarity-based fallback node matching. pyvis 0.3.2 wraps vis.js Network for the graph visualization, with `cdn_resources='in_line'` as the mandatory configuration to produce a self-contained output file. Typer 0.24.1 provides the CLI layer. uv is the package manager; no requirements.txt.

**Core technologies:**
- **Python 3.11+**: Runtime — minimum version driven by NetworkX 3.6.1's hard `>=3.11` requirement
- **lxml 6.0.2**: XML parsing, C14N canonicalization, XPath — eliminates false positives from attribute reordering; 5–20x faster than stdlib
- **networkx 3.6.1**: DiGraph model for workflow connections — nodes carry diff status attributes that pass directly into pyvis node colors
- **scipy**: `linear_sum_assignment` (Hungarian algorithm) — fallback node matching when ToolIDs have regenerated; O(n³) but acceptable at 500 nodes
- **deepdiff 8.6.1**: Field-level config diff — produces human-readable "field X changed from A to B" after dict conversion; actively maintained (Sep 2025 release)
- **pyvis 0.3.2**: Interactive graph visualization — wraps vis.js Network; use `cdn_resources='in_line'` only; disable physics (`physics=False`) and use Alteryx canvas X/Y coordinates directly
- **Jinja2 3.1.6**: HTML report templating — inline all JS/CSS at render time via `{{ content | safe }}` pattern; no CDN references
- **Typer 0.24.1**: CLI — type-hint-first, zero boilerplate for 3–5 flags; built on Click; auto-generates help and shell completion
- **uv**: Package management — 10–100x faster than pip; manages pyproject.toml + uv.lock; `requires-python = ">=3.11"`

**Critical version constraint:** NetworkX 3.6.1 requires Python >=3.11. This is the version floor for the entire project. Do not target Python 3.10.

### Expected Features

The gap ACD fills is specifically: governance teams need to review workflow changes before promotion without Alteryx Designer installed. Every competitor (Alteryx built-in, Simulink, KNIME) requires the authoring environment to view a meaningful diff. ACD's self-contained HTML report is the only format that works for license-limited reviewers. The interactive graph with hover/click inline config diff is a genuine differentiator — no competitor delivers this without the authoring tool open.

**Must have (table stakes) — v1:**
- XML parsing and validation with descriptive errors on malformed input — without this, nothing works
- Normalization layer: strip GUIDs, timestamps, TempFile paths, whitespace, attribute reordering — without this, every Git commit produces hundreds of false positives
- Secondary ToolID matching by type + position fallback — without this, any Alteryx save that regenerates IDs produces false add/remove pairs
- Tool diff: additions, removals, modifications with before/after field-level values — "modified" without showing what changed is not actionable
- Connection diff: additions, removals, anchor rewirings (full 4-tuple: src_tool + src_anchor + dst_tool + dst_anchor) — anchor identity matters for Join tool rewirings
- HTML report with color-coded summary section (green/red/yellow convention)
- HTML report with expandable per-tool detail sections
- Interactive graph visualization using canvas X/Y coordinates, color-coded by change type
- Hover/click on graph nodes for inline config diff
- Self-contained HTML output (all JS/CSS embedded, no CDN references)
- `--include-positions` flag with clear `--help` documentation explaining why positions are excluded by default
- Performance target: <5 seconds for 500-tool workflows

**Should have (competitive) — v1.x after validation:**
- JSON summary output (`--json` flag) — enables CI integration; second serializer with no engine changes
- Governance-ready report metadata (file paths, file hashes, timestamp) — ALCOA+ compliance for pharma/finance users; 10 lines added to template
- Configurable noise rules — handles Alteryx-version-specific metadata that default normalization misses

**Defer (v2+):**
- Macro recursion parsing — path resolution across environments is complex; validate single-workflow diff covers 80% of use cases first
- REST API / Alteryx Server webhook — requires server infrastructure and auth; validate CLI value proposition first
- Git PR comment bot — requires GitHub Actions wrapper + hosted service
- Web upload UI — requires server, auth, file storage
- Three-way merge — requires semantic understanding of which Alteryx config values are safe to merge independently; 10x Phase 1 scope
- AI natural language change summary — hallucination risk is unacceptable for regulated workflows before false-positive rate is demonstrably near-zero

### Architecture Approach

The architecture follows a hexagonal pattern: an immutable four-stage pipeline (`Parser → Normalizer → Differ → Renderer`) exposed through a single entry point `pipeline.run(DiffRequest) → DiffResponse`. The CLI (`cli.py`) and future API (`api/routes.py`) are thin adapters — neither contains any business logic, neither calls sys.exit or opens file handles, and neither knows the stage implementations. This design costs nothing extra in Phase 1 and makes Phase 3 API addition a 15-line adapter. All data structures are frozen dataclasses; no stage mutates its input. The `models/` directory defines `WorkflowDoc`, `AlteryxNode`, `AlteryxConnection`, `DiffResult`, `NodeDiff`, and `EdgeDiff` before any logic is written — all stages communicate through these typed boundaries.

**Major components:**
1. **Parser** (`parser/yxmd_parser.py`) — Load .yxmd XML via lxml, validate structure, emit `WorkflowDoc(nodes, connections)`; respect `<?xml encoding?>` declaration; use `resolve_entities=False` for XXE safety
2. **Normalizer** (`normalizer/normalizer.py`) — Strip positions/GUIDs/TempFile paths/whitespace via C14N, compute SHA-256 config hash per node; positions are retained in a separate field for graph layout but excluded from the hash by default
3. **NodeMatcher** (`differ/node_matcher.py`) — Two-pass: exact ToolID lookup O(n), then `scipy.optimize.linear_sum_assignment` on unmatched nodes using (tool_type + position proximity + config hash similarity) cost function; threshold rejection at cost > 0.8
4. **Differ** (`differ/`) — NodeDiffer produces `ChangeType` per matched pair using config hash fast-path; EdgeDiffer computes symmetric difference on frozensets of connection 4-tuples; outputs `DiffResult`
5. **Renderer** (`renderer/`) — HTMLRenderer embeds diff data as `const DIFF_DATA = {...}` JSON in a `<script>` tag with lazy per-tool expand; JSONRenderer as a second serializer from the same `DiffResult`
6. **Pipeline** (`pipeline.py`) — Orchestrates all stages; `DiffRequest` / `DiffResponse` dataclasses define the interface; both CLI and API call this function

**Recommended build order:** Models → Parser → Normalizer → NodeMatcher → Differ → Pipeline → JSONRenderer → HTMLRenderer → CLI

### Critical Pitfalls

1. **ToolID-only node matching produces phantom add/remove pairs** — Alteryx regenerates ToolIDs on copy-paste and "save as". Pure ID matching makes every such save appear as wholesale tool removal + addition. Prevention: two-pass matching (ID-first, then type + position similarity fallback). Must be built before any diff logic sits on top of it. Recovery if shipped wrong: HIGH cost (matching algorithm redesign + user trust damage).

2. **Position fields leaking into diff detection** — Canvas X/Y drift occurs every time a large workflow is opened and closed. If position is not strictly excluded from the config hash, every routine canvas change generates false "modified" results on every repositioned tool. Prevention: normalization layer must separate `node.position` from `node.config_hash` as distinct data paths — never unified. Test: same workflow saved twice with tools moved must produce zero diffs.

3. **pyvis CDN dependency breaks offline use** — Even `cdn_resources='in_line'` still loads Bootstrap CSS from `cdnjs.cloudflare.com`. Reports fail on air-gapped networks. Prevention: use `cdn_resources='in_line'` for vis.js, then post-process HTML to inline or remove the Bootstrap CDN link. Test with network access disabled before shipping. Recovery if shipped wrong: LOW cost (patch).

4. **Physics-enabled pyvis rendering hangs browser** — pyvis defaults to Barnes-Hut physics simulation. For 150+ node workflows, the browser hangs for 30+ seconds. At 500 nodes, it can crash the tab. Prevention: disable physics entirely (`physics=False`) and render at Alteryx canvas X/Y coordinates. This is also semantically correct — the report canvas should match Designer canvas layout.

5. **CLI logic coupled to pipeline — API extraction becomes a rewrite** — Writing diff logic inside the Typer callback, calling `sys.exit()` inside the differ, or opening file handles inside the renderer makes the pipeline impossible to wrap as an API without a full rewrite. Prevention: enforce from day one that `parser.py`, `differ.py`, and `renderer.py` contain zero calls to `sys.exit`, `print`, or file I/O. Enforce with a unit test that imports and calls the differ without touching CLI. Recovery if shipped wrong: HIGH cost (core refactor).

## Implications for Roadmap

Based on combined research, the natural phase structure follows the pipeline's data flow dependencies and the pitfall-to-phase mapping from PITFALLS.md.

### Phase 1: Foundation — Models, Parser, Normalizer, Node Matching

**Rationale:** Every downstream component depends on correct XML parsing and normalization. The two highest-cost pitfalls (ToolID matching and position leakage) must be solved before any diff logic is built on top. Building models first ensures all stages speak a typed common language. This phase produces no user-visible output but is the load-bearing foundation.

**Delivers:** `WorkflowDoc` model, lxml-based parser, normalization layer with C14N + SHA-256 hashing, two-pass NodeMatcher (ID-first + Hungarian fallback), and a comprehensive fixture-based test suite covering ToolID regeneration, position drift, GUID injection, TempFile paths, CDATA, and namespace variations.

**Addresses:** XML parsing, normalization, secondary ToolID matching (all P1 features from FEATURES.md)

**Avoids:** Pitfalls 1 (ToolID matching), 2 (position leakage), 5 (over-normalization), 6 (namespace comparison), 8 (CDATA loss), 9 (TempFile false diffs), 10 (Graph Edit Distance), 11 (exit codes), 13 (attribute order hashing), 14 (ANSI codes), 15 (Windows encoding), 16 (round-trip stability)

**Needs research:** No — patterns are well-established and stack choices are HIGH confidence. Implement directly.

### Phase 2: Diff Engine + JSON Output

**Rationale:** With a verified normalized model, the diff engine can be built on a stable foundation. JSON renderer is the simpler output format and should be built before HTML — it validates the DiffResult object model without visual complexity. The pipeline orchestrator wires all stages and establishes the `DiffRequest/DiffResponse` interface that CLI and future API share.

**Delivers:** `NodeDiffer`, `EdgeDiffer`, `DiffResult` with full before/after field-level values, `JSONRenderer`, `pipeline.run()` entry point, and integration tests validating all fixture scenarios end-to-end.

**Addresses:** Tool diff (add/remove/modify with before/after values), connection diff (with anchor identity), JSON output, pipeline orchestration (all P1 from FEATURES.md)

**Avoids:** Pitfall 7 (CLI-pipeline coupling — pipeline.run() is entry-point-agnostic from the start)

**Needs research:** No — DeepDiff dict-based field diffing is a well-documented pattern; scipy Hungarian algorithm is HIGH confidence.

### Phase 3: HTML Report + Graph Visualization

**Rationale:** HTML rendering is the highest-complexity output stage and depends on a validated DiffResult object model from Phase 2. Building it last means the template can be designed around real diff data shapes. This phase delivers the key differentiator: a self-contained, interactive graph visualization that governance teams can open without Alteryx installed.

**Delivers:** Jinja2 HTML report with color-coded summary, lazy-loaded per-tool detail sections (JSON-in-script-tag pattern), interactive pyvis graph at Alteryx canvas X/Y coordinates with physics disabled, hover/click inline config diff, and a verified self-contained HTML file (offline rendering test required before shipping).

**Addresses:** HTML report, interactive graph, hover/click inline diff, self-contained output, `--include-positions` flag (all P1 from FEATURES.md)

**Avoids:** Pitfalls 3 (pyvis CDN), 4 (physics hang), 12 (report size bloat)

**Needs research:** Possibly — pyvis Bootstrap CSS post-processing workaround needs implementation verification. Recommend a spike on self-contained HTML output early in this phase before committing to pyvis vs. a custom D3.js template approach. If pyvis post-processing is too brittle, switch to the custom Jinja2 + bundled D3.js approach described in ARCHITECTURE.md.

### Phase 4: CLI Entry Point + Polish

**Rationale:** The CLI is deliberately built last as a thin adapter over `pipeline.run()`. Building it last enforces the architectural discipline — if the CLI is too fat, the pipeline is too thin. This phase also adds exit code standardization, ANSI TTY detection, `--help` documentation, and end-to-end CLI smoke tests.

**Delivers:** `acd diff workflow_v1.yxmd workflow_v2.yxmd` invocation, documented exit codes (0=no diff, 1=diff found, 2=error), ANSI-safe output, `--include-positions` flag, `pyproject.toml` entry point `acd = "alteryx_diff.cli:app"`, and end-to-end performance validation against 500-tool fixture.

**Addresses:** CLI invocation, performance target <5s for 500 tools, `--include-positions` flag documentation (all P1 from FEATURES.md)

**Avoids:** Pitfalls 11 (exit code inconsistency), 14 (ANSI codes in piped output)

**Needs research:** No — Typer patterns are HIGH confidence and well-documented.

### Phase 5: v1.x Enhancements (Post-Validation)

**Rationale:** Add after the core diff quality is confirmed accurate in real workflows. These features add value without touching the diff engine.

**Delivers:** `--json` flag (second serializer from the same DiffResult), governance-ready report metadata (file paths, file hashes, timestamp), configurable noise rules (XPath-pattern exclusion list).

**Addresses:** JSON output, governance metadata, configurable normalization (all P2 from FEATURES.md)

**Needs research:** No — second serializer and metadata additions are straightforward. Configurable noise rules may benefit from a spike on XPath pattern matching ergonomics.

### Phase Ordering Rationale

- **Models before logic:** All four research files converge on defining data structures first. No stage can be tested in isolation without typed boundaries. This is not a design preference — it is a prerequisite.
- **Normalization before diff:** Both PITFALLS.md and ARCHITECTURE.md identify normalization as the dependency gate. Building the differ on unnormalized data bakes in false positives that are expensive to remove later.
- **NodeMatcher in Phase 1 (not Phase 2):** The ToolID regeneration pitfall is rated HIGH recovery cost if shipped wrong. The matcher must be validated with fixture pairs before any diff logic depends on its output.
- **JSON before HTML:** JSON renderer validates the DiffResult shape without visual rendering complexity. If the DiffResult is wrong, it is caught before the HTML template is built around it.
- **CLI last:** Architectural discipline. If `pipeline.run()` cannot be called without the CLI, Phase 3 API addition becomes a rewrite.
- **pyvis physics disabled from day one:** Cannot be retrofitted without regression risk. Set at the start of Phase 3.

### Research Flags

Phases needing deeper research during planning:
- **Phase 3 (HTML/Graph):** Spike recommended on pyvis self-contained HTML reliability. The Bootstrap CDN workaround (GitHub issue #228) is confirmed but implementation details need verification. If post-processing is too fragile, escalate to custom D3.js template — this decision affects report size, maintenance burden, and offline guarantee.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Foundation):** All stack and pattern choices are HIGH confidence. lxml C14N, scipy Hungarian, frozen dataclasses — all are documented and verified.
- **Phase 2 (Diff Engine):** DeepDiff field diffing and symmetric-difference edge comparison are well-established. No research needed.
- **Phase 4 (CLI):** Typer patterns are fully documented and HIGH confidence. No research needed.
- **Phase 5 (Enhancements):** Second serializer and metadata are trivially additive. No research needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All core dependencies verified against current PyPI versions and official docs (lxml 6.0.2, networkx 3.6.1, typer 0.24.1, deepdiff 8.6.1, pytest 9.0.2). Only moderate concern: pyvis last release Feb 2023 — mature but unmaintained. Sufficient for Phase 1-3. |
| Features | MEDIUM | Table stakes and differentiators are well-researched against Simulink (HIGH), DeltaXML (HIGH), Alteryx built-in (MEDIUM), KNIME (MEDIUM). Governance compliance requirements (21 CFR Part 11) are documented but ACD-specific validation requires regulated-industry user testing. |
| Architecture | MEDIUM-HIGH | Pipeline patterns and hexagonal architecture are HIGH confidence. Node matching via Hungarian algorithm is HIGH confidence (scipy official docs). DeepDiff dict representation for config diffing is MEDIUM confidence — well-established pattern but not verified against an Alteryx-specific reference implementation. |
| Pitfalls | MEDIUM-HIGH | XML/Python/pyvis pitfalls are HIGH confidence (verified against official sources, GitHub issues). Alteryx-specific XML behavior (ToolID regeneration, position drift, TempFile paths) is MEDIUM confidence — confirmed via Alteryx community forums and real .yxmd file inspection on GitHub, but not Alteryx official documentation. |

**Overall confidence:** HIGH for stack and architecture decisions. MEDIUM for Alteryx-specific XML behavior assumptions — these should be validated against a real workflow corpus as early as possible in Phase 1.

### Gaps to Address

- **Alteryx XML format assumptions need early validation:** TempFile element structure, GUID field names, position attribute XPath, and ToolID regeneration triggers are inferred from community sources and GitHub file inspection — not Alteryx official documentation. Build the normalization test fixtures from real .yxmd files in Phase 1 to confirm or correct these assumptions before the normalizer contract is finalized.

- **DeepDiff dict representation for config diffing:** Converting lxml element subtrees to Python dicts for DeepDiff comparison is a well-established pattern but has not been verified against a real Alteryx tool configuration. Specifically, the dict representation of nested XML (e.g., multi-level filter expressions) needs testing to confirm DeepDiff produces useful field-level diffs rather than opaque nested dict changes.

- **pyvis Bootstrap CSS post-processing:** GitHub issue #228 confirms that Bootstrap CSS loads externally even with `cdn_resources='in_line'`. The workaround (post-process HTML to inline or remove Bootstrap) is confirmed in principle but the implementation specifics (which Bootstrap selectors are actually used by pyvis output, whether removal breaks the graph layout) need a Phase 3 spike to finalize.

- **Performance target validation:** The <5 second SLA for 500-tool workflows is achievable based on component-level analysis (lxml C14N is fast, scipy Hungarian at 500 nodes is sub-second, NetworkX DiGraph scales to 10K+ nodes). However, end-to-end performance has not been measured. A 500-tool synthetic fixture should be built in Phase 1 and run through each stage incrementally to catch bottlenecks before they are embedded in the architecture.

## Sources

### Primary (HIGH confidence)
- lxml 6.0.2 — https://pypi.org/project/lxml/ and https://lxml.de/api.html — C14N behavior, attribute sorting, performance benchmarks
- networkx 3.6.1 — https://pypi.org/project/networkx/ — Python >=3.11 requirement, DiGraph, topological_sort
- scipy.optimize.linear_sum_assignment — https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linear_sum_assignment.html — Hungarian algorithm
- deepdiff 8.6.1 — https://pypi.org/project/deepdiff/ and https://zepworks.com/deepdiff/current/diff.html — field-level diff API
- typer 0.24.1 — https://pypi.org/project/typer/ — CLI patterns
- jinja2 3.1.6 — https://pypi.org/project/Jinja2/ — template rendering
- pytest 9.0.2 — https://pypi.org/project/pytest/ — testing
- uv — https://docs.astral.sh/uv/concepts/projects/config/ — package management
- Simulink Model Comparison — https://www.mathworks.com/help/simulink/ug/understand-model-comparison-results.html — competitor analysis
- DeltaXML XML Compare — https://docs.deltaxml.com/xml-compare/latest/features-and-properties — competitor analysis
- FastAPI layered architecture — https://sqr-072.lsst.io/ — hexagonal pattern

### Secondary (MEDIUM confidence)
- pyvis 0.3.2 — https://pypi.org/project/pyvis/ and GitHub issue #228 — CDN resources behavior, `in_line` mode
- pyvis GitHub issue #228 — https://github.com/WestHealth/pyvis/issues/228 — Bootstrap CDN workaround confirmed
- Alteryx community — version control position drift — https://community.alteryx.com/t5/Alteryx-Designer-Desktop-Discussions/Alteryx-Workflow-Version-Control/td-p/175046
- Alteryx yxmd XML inspection — https://github.com/jdunkerley/AlteryxFormulaAddOns/blob/master/RunUnitTests.yxmd — TempFile element structure
- KNIME Workflow Comparison — https://forum.knime.com/t/the-workflow-comparison-feature/39087 — competitor analysis
- GxP 21 CFR Part 11 audit trail — https://www.fdaguidelines.com/21-cfr-part-11-audit-trail-requirements-explained-for-gxp-systems/ — governance requirements

### Tertiary (LOW confidence)
- Alteryx community workflow compare request — Alteryx community page not fully loaded; feature gap inferred from phData blog and available community discussion context
- SimDiff Simulink diff tool — vendor claims only; competitor differentiation treated as directional

---
*Research completed: 2026-02-28*
*Ready for roadmap: yes*
