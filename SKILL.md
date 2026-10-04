---
name: lfg
version: "2.4.0"
description: Bounded research, planning, implementation, validation, and review loop for complex coding tasks. Use when the user says lfg or lets-fucking-go, or wants a written plan with per-step acceptance criteria.
tags:
  - agent-workflows
  - planning
  - code-review
  - validation
---

# LFG

Run when the user wants an implementation driven by explicit research, a written plan, and a review/repair loop. The loop is bounded: it stops when acceptance criteria are met, a blocker needs the user, or repairs are exhausted. Prefer simple, cohesive, idiomatic changes over clever or sprawling ones.

## Project artifacts bootstrap

Before any task, check four standing artifacts for the repository. These are the
project's long-lived context — a task loop reads them before planning, and every
future run, reviewer, or operator inherits them:

| Artifact | Path (default) | What it holds |
|---|---|---|
| Architecture | `docs/architecture.md` | The system in project-specific terms: components, data flow, key decisions and why, trust boundaries, non-goals. |
| Feature map | `docs/features-map.md` | One table row per feature: behaviour, where it lives (source paths), how it is proven (tests, checks). |
| Developer setup | `docs/development.md` | What to install, how to run locally, test/lint/typecheck commands with expected results, branch/commit conventions. |
| SRE runbook | `docs/sre.md` | How it is deployed, where logs/alarms/dashboards live, what breaks first, one remediation line per known failure mode. |

Rules:

- **Missing → bootstrap first.** If any artifact is missing and the task touches the area it documents, research the codebase and produce the missing artifact(s) in the task's PR, before implementing the task. A bootstrap artifact must cite real paths and commands discovered in the repo, never invented ones; anything unverifiable is marked `(unverified)` with a note on what would confirm it. Never include secrets in any artifact.
- **Never fast-path past a missing, load-bearing artifact.** A task whose change depends on undocumented architecture needs the artifact written in the same loop; write the section you need, not a whole book — a 40-line honest map beats a 400-line generic one.
- **Stale → update in the same PR.** While implementing, if the change makes an existing artifact wrong (renamed component, new service, changed test command), update the affected section in the same PR and say so in the report. Do not rewrite untouched sections.
- **Present and still accurate → cite it.** The plan references the artifact paths it used. When the repository has its own conventions for these paths (e.g. an existing `ARCHITECTURE.md`), use them instead of the defaults and map the roles.
- **Forge pipelines note:** when the repository is built or reviewed by automation (forge-dev builders, forge-pr reviewers), these artifacts are the standing context those agents lack; keep them accurate in the repo rather than in external tool config.

## Triage first

- **Full loop** — default for broad, ambiguous, design-sensitive, or security-sensitive work. Research → define → plan → plan-review gate → implement stepwise → evaluate → implementation-review gate → repair → report, with PRD + progress docs.
- **Fast path** — only when ALL hold: roughly ≤30 lines across ≤3 files; no trust-boundary surface; no UX/copy/architecture impact; an obvious validation command. Skip the docs, make the change, validate, do one explicit self-review against the user's stated goal, and say you took the fast path. If Jev is available, run its triage gate first.
- Never fast-path work that crosses a trust boundary: authentication or authorization, privilege or process boundaries, input and path validation, deserialization, subprocess or shell execution, secret handling. When unsure, use the full loop.

## Artifacts

Coordinate through files, not chat memory. Default paths (follow better repo conventions):

- `docs/<task-slug>-prd.html` — project-specific definition; goals/non-goals; constraints (especially security/privacy); step plan with acceptance criteria and required evidence per step; validation commands; judge rubric; overall acceptance target.
- `docs/<task-slug>-progress.html` — status (`planned` / `in-progress` / `repairing` / `blocked` / `complete`); per-step checklist with evidence and pass/fail; changed-file links; validation results; reviewer findings; residual risks and final outcome.

Rules: self-contained HTML (inline CSS/JS only; no external scripts, styles, or fetches — must render from `file://`; escape code inside `<code>`/`<pre>`); visible `created` and `last updated` ISO 8601 timestamps, updating the latter on every change; relative cross-links between the two, plus any handoff file and reference material. Copy any subagent plan or review findings into these files — chat history is not coordination. Optionally include one small inline force-directed `<canvas>` diagram of the loop (≤12 nodes, no libraries, no network; mark the active step in the progress doc).

### Handoff file

At each milestone (`begin`, `plan-approved`, `step-N-done`, `complete`, `blocked`), append one timestamped line to `docs/<task-slug>-handoff.md`: task slug, step, status, evidence pointer. On re-entry or after compaction, recover state from the handoff file and docs instead of replaying chat. Optional only on the fast path. Never store secrets, keys, prompt contents, or raw command output in artifacts — summarize.

## Workflow

1. **Inspect.** Check branch and working tree; preserve unrelated changes and untracked files; read project instructions and the files/docs relevant to the request — including the four standing project artifacts (bootstrap any that are missing and load-bearing, per *Project artifacts bootstrap*). Append the `begin` handoff line.
2. **Define.** Before any code, state the core concept in project-specific terms: what it means here, what it explicitly does not mean, security/privacy implications, measurable success criteria.
3. **Plan.** Produce (via the planner subagent when available) a plan where **every step has acceptance criteria and the concrete evidence required to prove each** — test command, diff inspection, screenshot, log excerpt, reviewer note, or manual check. Include definition of done, coverage of every user requirement and constraint, open questions resolved or explicitly marked as user-blockers, non-goals, validation commands, and taste/originality criteria for design-sensitive work. Write it into the PRD and initialize the progress doc.
4. **Plan gate.** Have the plan reviewed (plan reviewer subagent, or manually). Implementation may not start until: every step has acceptance criteria + required evidence; definition of done exists; requirements and open questions are addressed; both docs exist; and the review has no `fail` or unresolved `uncertain` findings (including the Jev plan gate, if available). Then append `plan-approved`.
5. **Implement stepwise.** For each step: read PRD/progress → implement only that step → gather its evidence → update the progress doc (files changed, validation output, criterion status) → evaluate against every criterion (plus the Jev evidence gate, if available) → advance only when all pass; `uncertain` is not a pass.
6. **Repair boundedly.** On a failed criterion (or taste/originality <4 for design-sensitive work): diagnose from the evidence first, record the diagnosis, and produce a revised approach — never a blind retry of the same fix (the Jev repair gate, if available, checks this). Escalate to the user only on a true blocker: missing dependency/permission, an ambiguous requirement, or the same failure after 3 distinct replans of that step. Never commit while a step is `repairing`.
7. **Implementation gate.** Review the actual diff (implementation reviewer subagent, or manually) against the PRD and progress docs, re-running the Jev evidence gate over the final evidence if available. Unmet required criteria, unresolved `uncertain` verdicts, or blocking rubric findings → repair the failing step and re-gate.
8. **Validate.** Run the project's canonical check — discover it from package.json scripts or project AGENTS.md (e.g. `npm run check`, `cargo check`, `pytest -q`). Targeted checks are for iterating inside a step; the full suite runs at least once on the final step. Change size is the wrong axis: repositories carry cross-cutting invariant tests (schema-derived checks, source pins, whole-tree lint) whose expectations derive from repo state, not the diff — a new table, route, or provider row can break one while every feature-local test passes. If the suite is genuinely too slow to run whole, run the invariant/meta-test files for every artifact kind touched and disclose in the report which invariant surfaces were left uncovered. Fix findings and re-run failing validation until green.
9. **Report.** Concise summary: definition used, implementation summary, files changed, validation run and result — scope stated explicitly (full suite with counts, or named targeted checks plus uncovered invariant surfaces), reviewer findings addressed, residual risks and follow-ups. State the standing-artifact outcome: bootstrapped (which), updated (which sections), or cited (paths). Append the `complete` handoff line and note durable decisions so the next session inherits context.

Do not edit generated `build/`/`dist/` output; edit sources and rebuild.

## Multi-layer work: slice PRs by boundary

If an epic spans ≥2 context boundaries (e.g. `db` / `service` / `api` / `ui` / `integration`) or ≥4 files, plan it as boundary slices: each slice gets its own branch, conventional-commit scope (`feat(data)`, `feat(api)`, …), definition of done, and unit + E2E test gates runnable in CI; note inter-slice dependencies in the plan. Collapse to a single PR only when the whole change is <4 files, a couple of days of work, and one scope — and say so in the PR description. PRs: title and body in Conventional Commit form; `BREAKING CHANGE` footer when API contracts change; `Closes #<issue>` / `Part of #<epic>` footers; list each slice's test commands and evidence paths so automated review can verify the gates. Per-slice gates are targeted evidence; the full-suite rule (step 8) still applies once on the final slice's final step. Project-specific slice tables and PR checklists belong in that project's AGENTS.md, not here.

**Bootstrap slices.** A bootstrap of missing standing artifacts (architecture, feature map, dev setup, SRE runbook) large enough for its own review is its own slice/PR — usually the first one, so later slices cite it and its review establishes shared vocabulary. Task work must not land on a branch that leaves the artifact half-written; either finish the section the task needs or omit the artifact and disclose.

## Commit cadence

Commit only if the user asked for commits, a branch, or a PR; otherwise leave the work in the tree and say so in the report. When committing, scale with loop length: short loop (≤3 steps or fast path) → one commit at `complete`; medium (4–8 steps) → commit at each `step-N-done`; long (>8) → per step plus `complete`, optionally `plan-approved`. Commit only intended files. If the user asked for a branch/PR, push and include the URL.

## Subagent roles

If this harness exposes subagents, use three advisory roles; if not, perform each role yourself and say so. List available agents first; prefer read-only/analysis agents; pass the role's directives in the task text; prefer fork/snapshot context for reviewers so they judge stable state; note the chosen agent in the progress doc. Subagents are critics, never owners.

- **Planner** (step 3): skeptical product-minded architect. Returns text only — a step plan with per-step acceptance criteria and required evidence, risks, non-goals, taste/originality criteria where relevant. Never edits files or docs.
- **Plan reviewer** (step 4): strict gatekeeper over the PRD. Marks each area `pass` / `fail` / `uncertain`: project-specific definition, definition of done, goal coverage, research evidence, open questions resolved-or-blocked, criteria + evidence per step, validation commands, taste criteria. Missing required items = `fail` = implementation blocked.
- **Implementation reviewer** (step 7): judges the diff against PRD + progress. Per step, marks every criterion `pass` / `fail` / `uncertain` with evidence, scores taste/originality 1–5, and lists blocking fixes. Returns findings only; never edits unless explicitly asked.

**`uncertain` is never a pass.** At every gate, whoever performs the role resolves each `uncertain` before the gate opens: gather stronger evidence and re-judge, or rule `pass` / `fail` with a written reason in the progress doc. If only the user can settle it, it is a blocker — record it and escalate; do not advance around it.

Judge all roles against this rubric: correctness, acceptance coverage, security/privacy (no leaked secrets, prompt contents, raw command output, or user data), simplicity, taste, originality, maintainability, validation.

Taste/originality scale: **5** distinctive and clearly better than the generic solution · **4** polished with some fresh thinking · **3** acceptable but conventional · **2** bland, clunky, or poorly integrated · **1** generic, incoherent, or product-damaging. For design-sensitive work, a score below 4 triggers a repair pass unless the user prefers speed over polish.

## Optional: Jev judge gates

If `TYPESAFE_API_KEY` is set in the environment (test for presence only — never print or store it), add [Jev](https://docs.typesafe.ai/llms.txt), TypeSafe's calibrated judgment model, as a second opinion at the gates below. If the key is absent, the project forbids sending content to external services, or a call errors or times out, skip Jev, continue with the reviewer-only gates, and note that in the progress doc — never block on Jev. If a TypeSafe skill is installed, load it and follow the live docs; otherwise the request shape below is enough.

Why here: the author and the reviewer subagents are usually the same model, so self-review tends to wave through vague criteria and thin evidence. Jev is an independent model that returns typed answers with probabilities rather than prose, which suits narrow "does this text meet this condition" checks. It does not reason over code: reviewers still own correctness, security, simplicity, and taste, and commands still own validation.

**Ratchet rule:** Jev only tightens a gate. Its verdict may downgrade a `pass` to `uncertain` or `fail`; it never upgrades a `fail`, overrides a failing command, or replaces a reviewer.

One request per gate, all of that gate's questions asked together over one small `state`:

- **Triage gate** (before any fast path). State: the user's request and the files to be touched. One Noul per trust-boundary category from Triage ("does the change touch …"), plus one asking whether the change requires a design decision about product behavior, UI, user-facing wording, or architecture — with `false` criteria naming mechanical changes (typo, version bump, small bug fix), or Jev's literal reading flags every README edit as "copy". Any answer ≥ 0.3 → full loop. Jev can force the full loop, never the fast path.
- **Plan gate** (step 4). State: `{requirements: [...], steps: [{id, criteria, evidence}]}`. Per step, two Nouls: is every criterion in `steps[i].criteria` an observable outcome rather than an intention; does `steps[i].evidence` name a concrete, checkable artifact. Per requirement, a Choice over the step ids plus `none`: which step covers `requirements[j]`. A Noul < 0.7 → `uncertain`, resolved under the same rule; `none` → `fail` on goal coverage.
- **Evidence gate** (steps 5 and 7). State: `{criteria: [{criterion, evidence}]}`, where evidence is the summarized artifact itself (command and result line, diff summary), not your claim that it passed. Per criterion, a Choice — `proves` / `contradicts` / `insufficient`. `proves` with confidence ≥ 0.8 corroborates the pass; `contradicts` → `fail`; anything else → `uncertain`, resolved under the `uncertain` rule in Subagent roles (re-ask Jev after gathering stronger evidence).
- **Repair gate** (step 6). State: `{failure, previous_approach, revised_approach}`. Noul: is `revised_approach` a materially different approach rather than the same fix retried with minor changes. < 0.5 → replan before spending the attempt.

```json
POST https://api.typesafe.ai/v1/systemone   (Authorization: Bearer $TYPESAFE_API_KEY)
{"model": "jev-latest",
 "state": {"criteria": [{"criterion": "`pytest -q` exits 0", "evidence": "pytest -q -> 41 passed, 2 failed (exit 1)"}]},
 "questions": {"c0": {"type": "choice", "instructions": "How does `criteria[0].evidence` relate to `criteria[0].criterion`?",
   "criteria": {"proves": "Directly demonstrates the criterion is met", "contradicts": "Shows the criterion is not met", "insufficient": "Does not address the criterion, or too vague to tell"}}}}
```

Answers return under the same ids: Noul → `noul` (probability of yes); Choice → `choice`, `probabilities`, `confidence`.

Question rules: Jev reads literally, so write the exact condition and ask one judgment per question; reference state by backticked path; send only the fields a question needs, never the whole PRD or diff; keep counts, line/file thresholds, exit codes, and date math in code. State follows the artifact rule — summaries only; no secrets, user data, raw command output, or prompt contents. The thresholds above are conservative starting points, not tuned values. Record each gate's question ids, answers, and the response `model` in the progress doc, and state in the report whether Jev gates ran.
