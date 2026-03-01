# Feature Research

**Domain:** XML workflow diff tool — visual programming comparison for Alteryx .yxmd files
**Researched:** 2026-02-28
**Confidence:** MEDIUM (primary sources: Simulink docs HIGH; Alteryx community MEDIUM; XML diff tools MEDIUM; governance requirements MEDIUM)

---

## Research Basis

Sources consulted:
- Alteryx built-in Compare Workflows (official docs + community)
- KNIME Workflow Comparison feature (community forum)
- Simulink Comparison Tool (MathWorks official docs, R2025a)
- DeltaXML XML Compare (official docs)
- xmldiff library (PyPI/GitHub)
- Beyond Compare XML mode (community forums)
- Regulated industry audit trail requirements (21 CFR Part 11, GxP, SOX)
- Graph visualization patterns (Cytoscape.js docs)
- Git CI integration patterns (GitHub Actions ecosystem)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features any workflow diff tool must have. Missing these = product feels broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Tool addition/removal detection | Core definition of "diff" — every diff tool does this | LOW | Alteryx built-in does this; ACD must match at minimum |
| Configuration change detection | Users care about WHAT changed in a tool, not just THAT it changed | MEDIUM | Alteryx built-in does this at surface level; ACD must go deeper (expression text, field lists, filter logic) |
| Connection change detection | Rewiring is a functional change; missing it = missed critical diffs | MEDIUM | Alteryx built-in flags connection mismatches; ACD must detect add/remove/rewire with anchor port identity |
| Color-coded summary by change type | Every diff tool since `diff` uses color: green=add, red=remove, yellow=modify | LOW | Standard industry convention; deviating confuses users |
| Noise filtering / normalization | Position drift, whitespace, attribute reorder = top complaint in every visual-programming diff tool community | HIGH | This is the hardest table-stakes feature. Simulink defaults to hiding nonfunctional changes. Alteryx community explicitly cites this as why raw Git diffs are useless. |
| Human-readable output (not raw XML) | Raw XML diffs are unreadable to analytics developers without deep XML knowledge | MEDIUM | All competitors (Simulink, KNIME, Alteryx built-in) produce readable reports, not deltas |
| Graceful error handling for malformed input | Users will run this on partially-saved or corrupted files | LOW | Descriptive error messages required; silent failures destroy trust |
| Performance acceptable for large workflows | Workflows with 100-500 tools exist in production; users will not wait 60 seconds | MEDIUM | PROJECT.md targets <5s for 500 tools; Simulink and DeltaXML both handle large files |
| Summary view before detail view | Users need to scan "is this a big change or small change" before reading details | LOW | Simulink, KNIME, and DeltaXML all lead with a summary/overview before per-item details |
| CLI invocation with two file arguments | This is a developer tool; GUI-only tools get bypassed in scripts and pipelines | LOW | Primary interface per PROJECT.md |

### Differentiators (Competitive Advantage)

Features that set ACD apart. None of the existing tools fully deliver these for the Alteryx context.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Interactive graph visualization using canvas X/Y coordinates | Existing tools (Simulink, KNIME, Alteryx built-in) open the host application. ACD produces a standalone, self-contained HTML with an interactive graph — no Alteryx Designer required. Governance teams reviewing diffs do NOT have Alteryx licenses. | HIGH | Confirmed gap: Alteryx built-in requires Designer open. Simulink comparison requires MATLAB. ACD's HTML graph is genuinely differentiated. |
| Hover/click on graph node to see inline config diff | Every competitor shows the diff in a separate panel or requires clicking through a tree view. Inline detail on the graph itself creates a single mental model for reviewing changes. | HIGH | Simulink shows changes "highlighted in yellow" in the editor; ACD's click-to-expand in the graph itself goes further. |
| False-positive-zero normalization (GUID, timestamp, whitespace, attribute order) | Alteryx community explicitly documents that position drift and GUID regeneration make raw XML diffs useless. No existing Alteryx-specific diff tool has solved this comprehensively. | HIGH | This is the #1 reason ACD exists. KNIME comparison has known bugs (not listing all changes). DeltaXML solves this for generic XML but is not Alteryx-aware. |
| Secondary ToolID matching (type + position fallback) | When Alteryx regenerates ToolIDs on save (documented behavior), pure ID-based diff produces false add/remove pairs. No existing Alteryx tool handles this. | HIGH | Confirmed Alteryx-specific problem from PROJECT.md and community. DeltaXML's orderless comparison hints at the algorithm pattern needed. |
| Self-contained HTML report (no server, no Alteryx, no dependencies) | Report can be emailed, attached to a JIRA ticket, committed to Git as an artifact, or posted as a PR comment. Every competitor requires either the authoring tool or a server. | MEDIUM | DeltaXML's side-by-side HTML requires a server for JS assets. ACD's report should embed all CSS/JS. This enables governance use case without tool installation. |
| JSON output for machine-readable consumption | CI pipelines, Git hooks, and Alteryx Server integrations need structured output, not HTML parsing. No existing Alteryx diff tool produces JSON. | MEDIUM | git-diff-action and similar CI tools demonstrate that JSON export is the standard for pipeline integration. Enables Phase 3 API layer with no changes to core engine. |
| `--include-positions` opt-in flag | Users sometimes DO want to see positional changes (e.g., when reviewing intentional canvas reorganizations). Most tools either always show or always hide position changes. Explicit opt-in is more powerful. | LOW | Simulink R2025a added Quick Filters for nonfunctional changes — same insight, but Simulink buries it in the UI. ACD's CLI flag makes it explicit and scriptable. |
| Governance-ready report structure with timestamp and file identity | Regulated industries (pharma, finance) using Alteryx require ALCOA+ compliance: attributable, contemporaneous, accurate records of what changed. Reports must include compared file paths, file hashes, and diff timestamp. | MEDIUM | GxP/21 CFR Part 11/SOX requirements documented. No existing Alteryx diff tool produces audit-ready output. This is a genuine gap for pharma/finance Alteryx users. |

### Anti-Features (Commonly Requested, Often Problematic)

Features to explicitly NOT build in Phase 1 — and why.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Three-way merge capability | Users coming from Git tools expect merge; Simulink has it | Merge requires understanding of semantic equivalence for Alteryx configs — an unsolved problem. A bad merge silently corrupts workflows. Ship reliable diff first; merge requires 10x the validation effort. | Document that ACD is diff-only. Point to Alteryx Designer's own merge UX for conflict resolution. |
| Real-time overlay inside Alteryx Designer | Dream feature in community requests | Requires Alteryx plugin SDK, which is undocumented and unsupported. Ties the tool to Alteryx's release cycle. Destroys the "no Alteryx license required" governance use case. | The HTML report IS the overlay. Governance teams open the HTML; developers reference it while working in Designer. |
| Macro recursion parsing (nested macros) | Workflows frequently call macros; users want recursive diffs | Macros are separate .yxmd files with their own paths. Recursive parsing requires path resolution, which breaks when file paths differ between environments (dev/prod). Creates O(n) file I/O with unclear boundaries. | Phase 2 feature. Phase 1: detect macro calls as tool configurations (the macro path IS a config value), flag when a macro tool's path or input mapping changes. |
| Web upload UI for drag-and-drop comparison | Non-technical governance users want a UI | Adds server infrastructure, authentication, file storage, and security concerns in Phase 1 when the diff engine itself isn't validated. Classic premature UX investment. | Phase 3 feature. Phase 1 CLI output is sufficient for developers. Self-contained HTML covers governance reviewers. |
| AI-generated natural language change summary | "Describe what changed in plain English" — compelling pitch | AI summaries for workflow configs are high-hallucination risk. A wrong AI summary ("this change is cosmetic") on a functional change in a regulated pipeline is worse than no summary. | Phase 3+ feature after diff quality is validated. Add only when false-positive rate is demonstrably near-zero. Human-readable structured output (tool name, change type, before/after values) is sufficient and accurate. |
| Bi-directional merge / cherry-pick | Power users want to pick individual changes from each version | Requires a three-panel UI and semantic understanding of which Alteryx config values are safe to merge independently. Scope is 10x Phase 1. | Defer entirely to Phase 3+. Current scope is read-only analysis, not mutation. |
| Workflow execution trace / runtime diff | Some users want to compare outputs, not structure | Fundamentally different product (data quality testing, not code review). Requires running both workflows, which needs Alteryx Server licenses and real data. | Out of scope permanently for ACD. Different tool category. |

---

## Feature Dependencies

```
[XML Parsing + Validation]
    └──required by──> [Normalization Layer]
                          └──required by──> [Diff Engine]
                                                ├──required by──> [Tool Diff (add/remove/modify)]
                                                ├──required by──> [Connection Diff]
                                                └──required by──> [Config Change Detection]

[Tool Diff] ──feeds──> [HTML Report Generator]
[Connection Diff] ──feeds──> [HTML Report Generator]
[Config Change Detection] ──feeds──> [HTML Report Generator]

[HTML Report Generator]
    ├──required by──> [Color-coded Summary]
    ├──required by──> [Per-tool Detail Sections]
    └──required by──> [Interactive Graph Visualization]

[Interactive Graph Visualization]
    └──enhanced by──> [Hover/Click Inline Config Diff]

[Diff Engine] ──parallel output──> [JSON Summary Export]

[Secondary ToolID Matching] ──required by──> [Diff Engine]
    (without this, ToolID regeneration causes false add/remove pairs)

[Normalization Layer] ──conflicts with──> [--include-positions flag]
    (positions suppressed by default; flag disables position normalization only)

[JSON Summary Export] ──enables (Phase 3)──> [CI/CD GitHub Action]
[JSON Summary Export] ──enables (Phase 3)──> [REST API / Alteryx Server webhook]
```

### Dependency Notes

- **Normalization Layer requires XML Parsing:** Cannot normalize what isn't parsed into a structured model. The object model (ToolID, type, position, config, connections) must be clean before normalization can identify what's noise vs. signal.
- **Secondary ToolID Matching requires Diff Engine:** The fallback matching (type + position heuristic) is part of the diff algorithm, not the parser. It activates when ID-based matching fails to find a counterpart.
- **Interactive Graph requires HTML Report:** The graph is embedded IN the HTML report — not a separate artifact. Pyvis or D3.js is bundled into the HTML output.
- **JSON Export is independent of HTML:** Both can be generated from the same diff result object. JSON adds no complexity once the diff engine exists; it's a second serializer.
- **`--include-positions` conflicts with normalization:** The normalization layer strips position attributes by default. The flag must bypass only the position-stripping step, not all normalization (GUIDs and whitespace normalization remain active regardless).

---

## MVP Definition

### Launch With (v1)

Minimum viable product — what validates the core diff engine and report quality.

- [ ] XML parsing and validation with descriptive errors on malformed input — without this, nothing works
- [ ] Normalization layer: strip GUIDs, timestamps, whitespace, attribute reordering — without this, every Git commit produces hundreds of false positives
- [ ] Secondary ToolID matching by type + position fallback — without this, any Alteryx save that regenerates IDs produces false add/remove pairs
- [ ] Tool diff: detect additions, removals, and modifications with before/after config values — core diff output
- [ ] Connection diff: detect additions, removals, and anchor rewirings — functional change detection
- [ ] HTML report with color-coded summary section — green/red/yellow convention; scannable at a glance
- [ ] HTML report with expandable per-tool detail sections — detail on demand
- [ ] Interactive graph visualization using canvas X/Y coordinates, color-coded by change type — the key differentiator; makes the report a visual tool review rather than XML reading
- [ ] Hover/click on graph nodes for inline config diff — completes the "see it in context" use case
- [ ] Self-contained HTML (all JS/CSS embedded) — enables email/attach/commit without server
- [ ] `--include-positions` flag — gives users opt-in control, prevents the "why doesn't it show position changes?" support question
- [ ] Performance target: <5 seconds for 500-tool workflows — validates production viability

### Add After Validation (v1.x)

Add once core diff quality is confirmed accurate in real workflows.

- [ ] JSON summary output (`--json` flag) — trigger: first user asks to integrate with a Git hook or CI script; adding this is a second serializer with no engine changes
- [ ] Governance-ready report metadata (file paths, file hashes, timestamp) — trigger: first regulated-industry team uses ACD for audit; adds 10 lines to the report template
- [ ] Configurable noise rules (user-defined attributes to ignore) — trigger: users encounter Alteryx-version-specific metadata that ACD doesn't normalize by default

### Future Consideration (v2+)

Defer until product-market fit is established.

- [ ] Macro recursion parsing — defer because path resolution across environments is complex; validate that single-workflow diff solves 80% of the use case first
- [ ] REST API / Alteryx Server webhook integration — defer because it requires server infrastructure and auth; validate CLI value proposition first (PROJECT.md explicitly Phase 3)
- [ ] Git PR comment bot — defer because it requires GitHub Actions wrapper + hosted service; validate JSON output value first
- [ ] Web upload UI — defer because it requires server, auth, file storage; CLI + HTML covers current users
- [ ] AI natural language change summary — defer because hallucination risk is unacceptable for regulated workflows; requires validated near-zero false-positive rate first

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| XML parsing + normalization | HIGH | MEDIUM | P1 |
| Secondary ToolID matching | HIGH | MEDIUM | P1 |
| Tool diff (add/remove/modify) | HIGH | LOW | P1 |
| Connection diff | HIGH | LOW | P1 |
| Color-coded HTML summary | HIGH | LOW | P1 |
| Interactive graph with canvas coords | HIGH | HIGH | P1 |
| Hover/click inline config diff | HIGH | MEDIUM | P1 |
| Self-contained HTML output | HIGH | LOW | P1 |
| `--include-positions` flag | MEDIUM | LOW | P1 |
| Performance <5s for 500 tools | HIGH | MEDIUM | P1 |
| JSON output flag | MEDIUM | LOW | P2 |
| Governance metadata in report | MEDIUM | LOW | P2 |
| Configurable noise rules | MEDIUM | MEDIUM | P2 |
| Macro recursion parsing | HIGH (long-term) | HIGH | P3 |
| REST API layer | HIGH (long-term) | HIGH | P3 |
| Web upload UI | MEDIUM | HIGH | P3 |
| Three-way merge | LOW (Phase 1) | HIGH | Defer |
| AI natural language summary | LOW (risky) | MEDIUM | Defer |

**Priority key:**
- P1: Must have for launch — validates core value proposition
- P2: Should have — add after first internal validation cycle
- P3: Nice to have — future phase (Phase 2/3 per PROJECT.md)
- Defer: Explicitly out of scope; document the deliberate choice

---

## Competitor Feature Analysis

| Feature | Alteryx Built-in Compare | Simulink Comparison Tool | KNIME Workflow Compare | DeltaXML XML Compare | ACD (our approach) |
|---------|--------------------------|--------------------------|------------------------|----------------------|-------------------|
| Detects tool add/remove | Yes | Yes | Yes | Yes (element level) | Yes |
| Detects config changes | Yes (surface) | Yes (block params) | Partial (known bugs) | Yes (attribute level) | Yes (expression/filter text) |
| Detects connection changes | Yes | Yes | Partial | Yes (element structure) | Yes (with port identity) |
| Hides position noise by default | No (shows all) | Yes (nonfunctional filter) | Unknown | Configurable | Yes (default; opt-in flag) |
| ToolID regeneration handling | No | N/A (different problem) | N/A | N/A | Yes (secondary matching) |
| GUID/timestamp normalization | No | N/A | Unknown | Configurable | Yes (always on) |
| Standalone HTML output | No (requires Designer) | No (requires MATLAB) | No (requires KNIME) | Yes (but JS assets external) | Yes (fully self-contained) |
| Interactive graph visualization | Yes (requires Designer) | Yes (requires MATLAB) | Yes (requires KNIME) | No | Yes (embedded in HTML) |
| Hover/click inline detail | Requires Designer UI | Requires MATLAB UI | Requires KNIME UI | No | Yes (in HTML report) |
| JSON machine-readable output | No | No | No | Yes (DeltaV2 XML delta) | Yes (Phase 1.x) |
| CLI invocation | Yes (`/diff` flag) | No | No | Yes | Yes (primary interface) |
| Governance metadata in report | No | No | No | Partial | Yes (Phase 1.x) |
| Macro/nested workflow handling | No | Partial (library blocks) | Partial (components) | N/A | Phase 2 |
| No license required to view report | No | No | No | Depends on output | Yes (HTML only) |

**Key insight from competitor analysis:** The gap ACD fills is specifically "governance team wants to review what changed before workflow promotion, without Alteryx Designer installed." Every existing tool requires the authoring environment to view a meaningful diff. ACD's self-contained HTML report is the only approach that works for license-limited reviewers.

---

## What the PRD May Have Missed

Based on research findings not explicitly called out in PROJECT.md:

1. **Governance metadata in the report header**: The PRD specifies the report format (color-coded summary, expandable tool sections, graph) but does not mention including file hashes, compared file paths, and report generation timestamp. Regulated-industry users require this for audit trails. Low complexity to add; high compliance value.

2. **Port/anchor identity in connection diffs**: "Connection added/removed/rewired" is stated, but connection diffs require identifying WHICH anchor port changed (e.g., Input #1 vs. Input #2 for a Join tool). A rewiring where the connection endpoint moves from the Left input to the Right input is a major functional change. The diff engine needs to capture source tool + source anchor + destination tool + destination anchor as the connection identity tuple.

3. **Before/after values, not just "modified"**: The PRD says "detect configuration-level changes" but the report value is showing the BEFORE and AFTER values side-by-side. "Filter expression changed" is not actionable. "Filter expression changed FROM `[Revenue] > 1000` TO `[Revenue] > 5000`" is. This must be a first-class output requirement for the HTML report.

4. **Configuring what "noise" means**: Different Alteryx versions inject different metadata. A future-proofing mechanism (even just a list of always-ignored XPath patterns) prevents the tool from breaking when Alteryx updates its save format.

5. **The `--include-positions` flag needs documentation**: Users WILL ask "why doesn't it show that I moved this tool?" The flag must be discoverable in `--help` output with a clear explanation of WHY positions are excluded by default.

---

## Sources

- [Alteryx Compare Workflows — Official Docs](https://help.alteryx.com/current/en/designer/workflows/compare-workflows.html) — MEDIUM confidence
- [Simulink Model Comparison — MathWorks Docs](https://www.mathworks.com/help/simulink/ug/understand-model-comparison-results.html) — HIGH confidence
- [DeltaXML Output Formats](https://docs.deltaxignia.com/xml-compare/16.1/output-formats) — HIGH confidence
- [DeltaXML Features and Properties](https://docs.deltaxml.com/xml-compare/latest/features-and-properties) — HIGH confidence (403 on direct fetch; inferred from search snippet)
- [KNIME Workflow Comparison Feature](https://forum.knime.com/t/the-workflow-comparison-feature/39087) — MEDIUM confidence (community forum)
- [Alteryx Version Control Challenges — phData](https://www.phdata.io/blog/version-control-in-alteryx/) — MEDIUM confidence
- [Alteryx Community Workflow Compare Request](https://community.alteryx.com/t5/Alteryx-Designer-Ideas/Workflow-Compare-Tool/idi-p/10678) — LOW confidence (page content not loaded)
- [GxP Audit Trail Requirements — 21 CFR Part 11](https://www.fdaguidelines.com/21-cfr-part-11-audit-trail-requirements-explained-for-gxp-systems/) — MEDIUM confidence
- [Cytoscape.js Interactive Graph](https://js.cytoscape.org) — HIGH confidence (official docs)
- [xmldiff PyPI/GitHub](https://github.com/Shoobx/xmldiff) — HIGH confidence (official repo)
- [Alteryx Metadata Parser](https://github.com/shiv-io/Alteryx-Metadata-Parser) — MEDIUM confidence (community tool)
- [SimDiff — Simulink Diff tool comparison](https://www.ensoftcorp.com/products/simdiff) — LOW confidence (vendor claims only)

---

*Feature research for: Alteryx Canvas Diff (ACD) — XML workflow diff tool for .yxmd files*
*Researched: 2026-02-28*
