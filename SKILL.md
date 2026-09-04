---
name: lfg
version: "2.2.0"
description: Bounded research, planning, implementation, validation, and review loop for complex coding tasks. Use when the user says lfg or lets-fucking-go, or wants a written plan with per-step acceptance criteria.
tags:
  - agent-workflows
  - planning
  - code-review
  - validation
---

# LFG

Run when the user wants an implementation driven by explicit research, a written plan, and a review/repair loop. The loop is bounded: it stops when acceptance criteria are met, a blocker needs the user, or repairs are exhausted. Prefer simple, cohesive, idiomatic changes over clever or sprawling ones.

## Triage first

- **Full loop** — default for broad, ambiguous, design-sensitive, or security-sensitive work. Research → define → plan → plan-review gate → implement stepwise → evaluate → implementation-review gate → repair → report, with PRD + progress docs.
- **Fast path** — only when ALL hold: roughly ≤30 lines across ≤3 files; no trust-boundary surface; no UX/copy/architecture impact; an obvious validation command. Skip the docs, make the change, validate, do one explicit self-review against the user's stated goal, and say you took the fast path.
- Never fast-path work that crosses a trust boundary: authentication or authorization, privilege or process boundaries, input and path validation, deserialization, subprocess or shell execution, secret handling. When unsure, use the full loop.

## Artifacts

Coordinate through files, not chat memory. Default paths (follow better repo conventions):

- `docs/<task-slug>-prd.html` — project-specific definition; goals/non-goals; constraints (especially security/privacy); step plan with acceptance criteria and required evidence per step; validation commands; judge rubric; overall acceptance target.
- `docs/<task-slug>-progress.html` — status (`planned` / `in-progress` / `repairing` / `blocked` / `complete`); per-step checklist with evidence and pass/fail; changed-file links; validation results; reviewer findings; residual risks and final outcome.

Rules: self-contained HTML (inline CSS/JS only; no external scripts, styles, or fetches — must render from `file://`; escape code inside `<code>`/`<pre>`); visible `created` and `last updated` ISO 8601 timestamps, updating the latter on every change; relative cross-links between the two, plus any handoff file and reference material. Copy any subagent plan or review findings into these files — chat history is not coordination. Optionally include one small inline force-directed `<canvas>` diagram of the loop (≤12 nodes, no libraries, no network; mark the active step in the progress doc).

### Handoff file

At each milestone (`begin`, `plan-approved`, `step-N-done`, `complete`, `blocked`), append one timestamped line to `docs/<task-slug>-handoff.md`: task slug, step, status, evidence pointer. On re-entry or after compaction, recover state from the handoff file and docs instead of replaying chat. Optional only on the fast path. Never store secrets, keys, prompt contents, or raw command output in artifacts — summarize.

## Workflow

1. **Inspect.** Check branch and working tree; preserve unrelated changes and untracked files; read project instructions and the files/docs relevant to the request. Append the `begin` handoff line.
2. **Define.** Before any code, state the core concept in project-specific terms: what it means here, what it explicitly does not mean, security/privacy implications, measurable success criteria.
3. **Plan.** Produce (via the planner subagent when available) a plan where **every step has acceptance criteria and the concrete evidence required to prove each** — test command, diff inspection, screenshot, log excerpt, reviewer note, or manual check. Include definition of done, coverage of every user requirement and constraint, open questions resolved or explicitly marked as user-blockers, non-goals, validation commands, and taste/originality criteria for design-sensitive work. Write it into the PRD and initialize the progress doc.
4. **Plan gate.** Have the plan reviewed (plan reviewer subagent, or manually). Implementation may not start until: every step has acceptance criteria + required evidence; definition of done exists; requirements and open questions are addressed; both docs exist; and the review has no `fail` findings. Then append `plan-approved`.
5. **Implement stepwise.** For each step: read PRD/progress → implement only that step → gather its evidence → update the progress doc (files changed, validation output, criterion status) → evaluate against every criterion → advance only when all pass.
6. **Repair boundedly.** On a failed criterion (or taste/originality <4 for design-sensitive work): diagnose from the evidence first, record the diagnosis, and produce a revised approach — never a blind retry of the same fix. Escalate to the user only on a true blocker: missing dependency/permission, an ambiguous requirement, or the same failure after 3 distinct replans of that step. Never commit while a step is `repairing`.
7. **Implementation gate.** Review the actual diff (implementation reviewer subagent, or manually) against the PRD and progress docs. Unmet required criteria or blocking rubric findings → repair the failing step and re-gate.
8. **Validate.** Run the project's canonical check — discover it from package.json scripts or project AGENTS.md (e.g. `npm run check`, `cargo check`, `pytest -q`). Targeted checks are for iterating inside a step; the full suite runs at least once on the final step. Change size is the wrong axis: repositories carry cross-cutting invariant tests (schema-derived checks, source pins, whole-tree lint) whose expectations derive from repo state, not the diff — a new table, route, or provider row can break one while every feature-local test passes. If the suite is genuinely too slow to run whole, run the invariant/meta-test files for every artifact kind touched and disclose in the report which invariant surfaces were left uncovered. Fix findings and re-run failing validation until green.
9. **Report.** Concise summary: definition used, implementation summary, files changed, validation run and result — scope stated explicitly (full suite with counts, or named targeted checks plus uncovered invariant surfaces), reviewer findings addressed, residual risks and follow-ups. Append the `complete` handoff line and note durable decisions so the next session inherits context.

Do not edit generated `build/`/`dist/` output; edit sources and rebuild.

## Multi-layer work: slice PRs by boundary

If an epic spans ≥2 context boundaries (e.g. `db` / `service` / `api` / `ui` / `integration`) or ≥4 files, plan it as boundary slices: each slice gets its own branch, conventional-commit scope (`feat(data)`, `feat(api)`, …), definition of done, and unit + E2E test gates runnable in CI; note inter-slice dependencies in the plan. Collapse to a single PR only when the whole change is <4 files, a couple of days of work, and one scope — and say so in the PR description. PRs: title and body in Conventional Commit form; `BREAKING CHANGE` footer when API contracts change; `Closes #<issue>` / `Part of #<epic>` footers; list each slice's test commands and evidence paths so automated review can verify the gates. Per-slice gates are targeted evidence; the full-suite rule (step 8) still applies once on the final slice's final step. Project-specific slice tables and PR checklists belong in that project's AGENTS.md, not here.

## Commit cadence

Commit only if the user asked for commits, a branch, or a PR; otherwise leave the work in the tree and say so in the report. When committing, scale with loop length: short loop (≤3 steps or fast path) → one commit at `complete`; medium (4–8 steps) → commit at each `step-N-done`; long (>8) → per step plus `complete`, optionally `plan-approved`. Commit only intended files. If the user asked for a branch/PR, push and include the URL.

## Subagent roles

If this harness exposes subagents, use three advisory roles; if not, perform each role yourself and say so. List available agents first; prefer read-only/analysis agents; pass the role's directives in the task text; prefer fork/snapshot context for reviewers so they judge stable state; note the chosen agent in the progress doc. Subagents are critics, never owners.

- **Planner** (step 3): skeptical product-minded architect. Returns text only — a step plan with per-step acceptance criteria and required evidence, risks, non-goals, taste/originality criteria where relevant. Never edits files or docs.
- **Plan reviewer** (step 4): strict gatekeeper over the PRD. Marks each area `pass` / `fail` / `uncertain`: project-specific definition, definition of done, goal coverage, research evidence, open questions resolved-or-blocked, criteria + evidence per step, validation commands, taste criteria. Missing required items = `fail` = implementation blocked.
- **Implementation reviewer** (step 7): judges the diff against PRD + progress. Per step, marks every criterion `pass` / `fail` / `uncertain` with evidence, scores taste/originality 1–5, and lists blocking fixes. Returns findings only; never edits unless explicitly asked.

Judge all roles against this rubric: correctness, acceptance coverage, security/privacy (no leaked secrets, prompt contents, raw command output, or user data), simplicity, taste, originality, maintainability, validation.

Taste/originality scale: **5** distinctive and clearly better than the generic solution · **4** polished with some fresh thinking · **3** acceptable but conventional · **2** bland, clunky, or poorly integrated · **1** generic, incoherent, or product-damaging. For design-sensitive work, a score below 4 triggers a repair pass unless the user prefers speed over polish.