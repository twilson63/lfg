---
name: lfg
version: "2.6.0"
description: Bounded research, planning, implementation, validation, and review loop for complex coding tasks. Use when the user says lfg or lets-fucking-go, or wants a written plan with per-step acceptance criteria.
tags:
  - agent-workflows
  - planning
  - code-review
  - validation
---

# LFG

Use this when the user wants an implementation backed by research, a written plan, and a review/repair loop. Build one step, check the evidence, and fix what fails before moving on. Stop when the acceptance criteria are met or a blocker needs the user. For a repeated failure, escalate after three distinct replans of that step, as described in step 6.

Simple, cohesive, idiomatic changes win. Don't get clever. Nobody likes a clever PR at 2am.

## Project artifacts bootstrap

Run this pre-check before task research, definition, planning, or implementation, including fast-path work. The three core artifacts are architecture, feature map, and design. All three core artifacts are required for every task. Developer setup and the SRE runbook remain standing artifacts when the task touches those areas.

| Artifact | Path (default) | What it holds |
|---|---|---|
| Architecture | `docs/architecture.md` | The system in project-specific terms: components, data flow, key decisions and why, trust boundaries, non-goals. |
| Feature map | `docs/features-map.md` | One table row per feature: behaviour, where it lives (source paths), how it is proven (tests, checks). |
| Design | `docs/design.md` | Product and interaction decisions: user flows, UI/UX conventions, accessibility, and visual constraints. For non-UI projects, document API/CLI interactions or other applicable design constraints and explain why visual design is not applicable. |
| Developer setup | `docs/development.md` | What to install, how to run locally, test/lint/typecheck commands with expected results, branch/commit conventions. |
| SRE runbook | `docs/sre.md` | How it is deployed, where logs/alarms/dashboards live, what breaks first, one remediation line per known failure mode. |

### Required pre-check

1. Resolve the three core paths in the table. Existing equivalent files are allowed only when you explicitly map each role to its actual path.
2. Read each core artifact and verify it exists, is readable, and contains project-specific content rather than an empty file or placeholder. Check it against the current repository; repair stale sections needed by the task.
3. If a core artifact is missing or inadequate, do only the repository inspection and clarification needed to bootstrap or repair these artifacts. This prerequisite work is not task research or implementation planning. Cite real source paths and verified commands. Mark unknown details `(unverified)`; do not invent requirements or design decisions. Ask the user when required information is unavailable.
4. Record each resolved path and its `pass` or `blocked` status in the task's progress doc, or in the response for fast-path work. If any core artifact cannot be completed or verified, stop and report `blocked`. Do not start task research, planning, or coding until all three pass. A placeholder or an unverified required decision does not pass.

Hard rules:

- **Missing? Bootstrap first.** Core artifacts follow the required pre-check above regardless of task scope. If developer setup or the SRE runbook is missing and your task touches that area, inspect the codebase and write the missing doc before task research or planning. Cite real paths and commands you actually found. If you can't verify something, mark it `(unverified)` and say what would confirm it. No secrets, ever.
- **Never fast-path past a missing, load-bearing artifact.** If a task depends on undocumented architecture, write the needed artifact in the same loop. Write the section you need, not a novel. Forty honest lines beats four hundred generic ones.
- **Stale? Update in the same PR.** If your change breaks an existing doc (renamed component, new service, changed test command), fix the doc in the same PR and call it out in the report. Leave untouched sections alone.
- **Accurate? Cite it.** Reference the artifact paths in your plan. If the repo already uses different names (like `ARCHITECTURE.md`), use those and map them to the roles above.
- **Forge note:** when automation builds or reviews this repo, these docs are the context it doesn't have. Keep them in the repo, not buried in tool config.

## Triage first

Complete the project-artifact pre-check before choosing either path. Use the full loop for broad, ambiguous, design-sensitive, or security-sensitive work. For changes that are small in risk and scope, use the fast path below. Do not decide based on line or file count alone. Several files can form one local change; one line can cross a trust boundary.

### Fast-path eligibility

Use fast path only when ALL of these are true:

- The requested outcome and expected behavior are clear and checkable without substantial discovery or an unresolved design decision.
- The change is localized and reasonably reversible. It does not alter architecture, shared contracts, or behavior across unrelated areas.
- The change does not touch a security or trust boundary: authentication, authorization, privilege or process boundaries, input validation, path validation, deserialization, subprocess or shell execution, secret handling, approvals, IPC/preload bridges, browser risk routing, or untrusted Markdown/file rendering.
- There is a concrete acceptance check: a focused test, a project check, or an observable manual check.

A specified, contained UI or copy change can qualify. An open-ended redesign cannot. Several files do not disqualify a change if they form one localized, low-risk change. Never fast-path past a missing, load-bearing artifact; the bootstrap rules still apply. Fast path does not bypass approvals or required project checks. If Jev is available, run its triage gate first.

### Fast-path procedure

1. State the intended change in one sentence before implementation.
2. Name the acceptance check and its observable expected result before implementation.
3. Make the smallest coherent change.
4. Run the relevant focused test or check. Add broader validation when shared behavior or project invariants require it. The full-suite rule in Workflow step 8 still applies to fast path.
5. Review the diff against the request and acceptance check; confirm no unrelated changes slipped in.
6. Report that you used fast path, what changed, what you checked, actual results, and anything not checked. Never claim an unrun or failing check passed. If no useful automated check exists, record the manual check and its actual result.

Skip task PRD/progress HTML, planner, and plan-review gate. Standing project-artifact requirements still apply.

### Escalation

Switch to the full loop if discovery reveals broader impact, ambiguous requirements, unresolved design decisions, unclear validation, or risk the fast path cannot address. Failed checks must be diagnosed and repaired, never waved through; escalate when they remain unresolved or reveal broader impact. Never fast-path security-sensitive boundaries or shared-contract changes. When unsure, use the full loop.

### Evaluation rubric

Evaluate work quality AND workflow choice. Speed alone is not a pass. Compare baseline and candidate on the same starting state and acceptance checks, using these representative task categories:

- A straightforward bug fix with an obvious focused test.
- A test-only change.
- A documentation-only change.
- A specified, localized UI or copy change.
- A multi-file change that remains localized and low-risk.
- A deceptively small security, trust-boundary, or shared-contract change.
- A task whose unclear requirements, discovered scope, or unresolved failed checks require escalation.

For each task, record pass/fail/uncertain for correct routing and escalation, intent plus a checkable result stated before edits, acceptance criteria met, relevant checks actually run and accurately reported, and diff review for request coverage and unrelated changes. Uncertain is not a pass. Track quality failures, missed escalations, unnecessary full-loop use, and elapsed time or tool calls. A speed gain fails the rubric if it skips a needed check or ships an incorrect change.

Static contract tests protect these instructions; routing-only model checks test policy interpretation. Neither proves completed-task quality or speed. Use actual isolated task runs with acceptance evidence before claiming end-to-end improvement. See [the evaluation protocol](docs/evaluation/fast-path.md) for a repeatable comparison.

## Artifacts

Coordinate through files. Not chat memory. Chat disappears; files stay. Default paths below, but follow whatever conventions the repo already has:

- `docs/<task-slug>-prd.html` defines the task. Include goals, non-goals, constraints (especially security/privacy), step-by-step plan with acceptance criteria and the evidence you need to prove each step, validation commands, a judge rubric, and the overall acceptance target.
- `docs/<task-slug>-progress.html` records live status: `planned` / `in-progress` / `repairing` / `blocked` / `complete`. Per-step checklist with evidence and pass/fail. Links to changed files. Validation results. Reviewer findings. Residual risks and final outcome.

Rules for these docs: self-contained HTML, inline CSS/JS only, no external scripts, styles, or fetches. Must render from `file://`. Escape code inside `<code>`/`<pre>`. Show `created` and `last updated` timestamps in ISO 8601, updating the latter every time you touch the doc. Use relative cross-links between the PRD and progress doc, plus any handoff file and references. Copy subagent plans and review findings into these files. Chat history is not coordination. If you're feeling fancy, you can add a small inline force-directed `<canvas>` diagram of the workflow loop (max 12 nodes, no libraries, no network; mark the active step in the progress doc).

### Handoff file

At every milestone (`begin`, `plan-approved`, `step-N-done`, `complete`, `blocked`), append one timestamped line to `docs/<task-slug>-handoff.md`: task slug, step, status, evidence pointer. When you come back after a break or a context compaction, recover state from the handoff file and the docs. Don't replay chat. The fast path can skip this. Never put secrets, keys, prompt contents, or raw command output in artifacts. Summarize instead.

## Workflow

1. **Inspect.** Check your branch and working tree. Preserve unrelated changes and untracked files. Read project instructions and anything relevant to the request. Complete the project-artifact pre-check before task research or planning. Verify all three core artifacts, then check developer setup and the SRE runbook for any task-relevant gaps. Append the `begin` handoff line.

2. **Define.** Before you write a single line of code, state the core concept in project-specific terms. What it actually means here. What it explicitly does NOT mean. Security and privacy implications. Measurable success criteria. If you can't define it, you can't build it.

3. **Plan.** Produce a plan (planner subagent if you have one) where **every step has acceptance criteria and the concrete evidence required to prove it**. Name a test command, a diff inspection, a screenshot, a log excerpt, a reviewer note, or a manual check. Include a definition of done, coverage of every user requirement and constraint, open questions either resolved or explicitly marked as user-blockers, non-goals, validation commands, and taste/originality criteria if this is design-sensitive work. Write it into the PRD and initialize the progress doc.

4. **Plan gate.** Have the plan reviewed (plan reviewer subagent, or do it yourself). Implementation does not start until: every step has acceptance criteria plus required evidence; a definition of done exists; requirements and open questions are addressed; both docs exist; and the review has no `fail` or unresolved `uncertain` findings (including the Jev plan gate, if available). Then append `plan-approved`.

5. **Implement stepwise.** For each step: read the PRD and progress doc, implement ONLY that step, gather its evidence, update the progress doc (files changed, validation output, criterion status), evaluate against every criterion (plus the Jev evidence gate, if available), and advance only when everything passes. `uncertain` is not a pass. Stop and fix.

6. **Repair boundedly.** When a criterion fails (or taste/originality scores below 4 on design work): diagnose from the evidence first, record the diagnosis, and come up with a revised approach. Never just retry the same fix and hope. The Jev repair gate, if available, checks exactly this. Escalate to the user only on a true blocker: missing dependency or permission, an ambiguous requirement, or the same failure after three distinct replans of that step. Don't commit while a step is `repairing`.

7. **Implementation gate.** Review the actual diff (implementation reviewer subagent, or manually) against the PRD and progress docs. Re-run the Jev evidence gate on the final evidence if available. Unmet required criteria, unresolved `uncertain` verdicts, or blocking rubric findings mean you repair the failing step and re-gate. No exceptions.

8. **Validate.** Run the project's canonical check. Find it in package.json scripts or AGENTS.md (stuff like `npm run check`, `cargo check`, `pytest -q`). Targeted checks are fine for iterating inside a step, but the full suite runs at least once on the final step. Don't judge by change size alone. Repos have cross-cutting invariant tests (schema checks, source pins, whole-tree lint) that break when repo state changes, even if your feature-local tests all pass. A new table, route, or provider row can trip these. If the full suite is genuinely too slow, run the invariant/meta-test files for every artifact kind you touched, and disclose in the report which invariant surfaces you left uncovered. Fix findings and re-run until green.

9. **Report.** Keep it concise. Definition you used, what you actually built, files changed, validation run and result. State the scope explicitly: full suite with counts, or named targeted checks plus any uncovered invariant surfaces. Note reviewer findings you addressed, residual risks, and follow-ups. Say what happened to the standing artifacts: bootstrapped (which ones), updated (which sections), or cited (paths). Append the `complete` handoff line. Note durable decisions so the next session isn't starting from zero.

Never edit generated `build/`/`dist/` output. Edit sources and rebuild.

## Multi-layer work: slice PRs by boundary

If an epic crosses two or more context boundaries (think `db` / `service` / `api` / `ui` / `integration`), plan it as boundary slices. File count alone does not require slices: a localized, low-risk multi-file change that meets fast-path eligibility can stay in one PR. Each slice gets its own branch, a conventional-commit scope (`feat(data)`, `feat(api)`, etc.), a definition of done, and unit plus E2E test gates that can run in CI. Note inter-slice dependencies in the plan. A full-loop change can stay in one PR when it is localized, a couple days of work, and one coherent scope. Explain that decision in the PR description; never use it to hide independent boundary work.

PR format: title and body in Conventional Commit form. `BREAKING CHANGE` footer when API contracts shift. `Closes #<issue>` / `Part of #<epic>` footers. List each slice's test commands and evidence paths so automated review can verify the gates. Per-slice gates are targeted evidence, but the full-suite rule in step 8 still applies once on the final slice's final step. Project-specific slice tables and PR checklists belong in that project's AGENTS.md, not here.

**Bootstrap slices.** If you're bootstrapping missing standing artifacts and it's large enough to need review, make it its own slice/PR. Usually do this first, so later slices can cite it and the review establishes shared vocabulary. Task work can't land on a branch that leaves an artifact half-written. Finish the required sections before task work proceeds. Never skip a core artifact; if it cannot pass the pre-check, report the blocker.

## Commit cadence

Only commit if the user asked for commits, a branch, or a PR. Otherwise leave the work in the tree and say so in the report. When you do commit, scale with loop length: short loop (three or fewer steps, or fast path) gets one commit at `complete`. Medium loop (four to eight steps) commits at each `step-N-done`. Long loop (more than eight) commits per step plus at `complete`, and optionally at `plan-approved`. Commit only the files you meant to change. If the user wanted a branch/PR, push it and include the URL.

## Subagent roles

If your harness has subagents, use three advisory roles. If not, perform each role yourself and say so. List available agents first. Prefer read-only or analysis agents. Pass the role's directives in the task text. For reviewers, prefer fork/snapshot context so they judge a stable state. Note which agent you picked in the progress doc. Subagents are critics, never owners.

- **Planner** (step 3): skeptical product-minded architect. Returns text only. A step plan with per-step acceptance criteria and required evidence, risks, non-goals, taste/originality criteria where relevant. Never edits files or docs.
- **Plan reviewer** (step 4): strict gatekeeper over the PRD. Marks each area `pass` / `fail` / `uncertain`: project-specific definition, definition of done, goal coverage, research evidence, open questions resolved-or-blocked, criteria and evidence per step, validation commands, taste criteria. Missing required items equals `fail`, which means implementation is blocked.
- **Implementation reviewer** (step 7): judges the diff against PRD and progress. Per step, marks every criterion `pass` / `fail` / `uncertain` with evidence, scores taste/originality 1 to 5, and lists blocking fixes. Returns findings only. Never edits unless explicitly asked.

**`uncertain` is never a pass.** At every gate, whoever is performing the role resolves each `uncertain` before the gate opens. Gather stronger evidence and re-judge, or rule `pass` / `fail` with a written reason in the progress doc. If only the user can settle it, that's a blocker. Record it and escalate. Don't advance around it.

Judge all roles against this rubric: correctness, acceptance coverage, security/privacy (no leaked secrets, prompt contents, raw command output, or user data), simplicity, taste, originality, maintainability, validation.

Taste/originality scale: **5** is distinctive and clearly better than the generic solution. **4** is polished with some fresh thinking. **3** is acceptable but conventional. **2** is bland, clunky, or poorly integrated. **1** is generic, incoherent, or actively product-damaging. For design-sensitive work, a score below 4 triggers a repair pass unless the user explicitly prefers speed over polish.

## Optional: Jev judge gates

If `TYPESAFE_API_KEY` is set in the environment (test for presence only, never print or store it), add [Jev](https://docs.typesafe.ai/llms.txt) as a second opinion at the gates below. TypeSafe's calibrated judgment model returns typed answers with probabilities instead of prose, which works well for narrow "does this text meet this condition" checks. If the key is missing, the project forbids sending content to external services, or a call errors out or times out, skip Jev. Continue with reviewer-only gates and note it in the progress doc. Never block on Jev. If a TypeSafe skill is installed, load it and follow the live docs. Otherwise the request shape below is enough.

Why Jev matters: the author and reviewer subagents are usually the same model, so self-review tends to wave through vague criteria and thin evidence. Jev is independent. It doesn't reason over code, though. Reviewers still own correctness, security, simplicity, and taste. Commands still own validation.

**Ratchet rule:** Jev only tightens. It can downgrade a `pass` to `uncertain` or `fail`. It never upgrades a `fail`, overrides a failing command, or replaces a reviewer.

One request per gate. Ask all of that gate's questions together over one small `state`:

- **Triage gate** (before any fast path). State: the user's request and the files to be touched. One Noul per security/trust-boundary category from Triage ("does the change touch …"), one for architecture/shared-contract or unrelated-area impact, and one for unresolved design decisions or unclear acceptance checks. A specified, contained UI or copy change with a concrete check is not an unresolved design decision. Use `false` criteria for such changes and mechanical fixes; use `true` criteria for open-ended redesigns. Missing load-bearing artifacts still require the full loop. Any answer ≥ 0.3 means full loop. Jev can force the full loop, never the fast path.
- **Plan gate** (step 4). State: `{requirements: [...], steps: [{id, criteria, evidence}]}`. Per step, two Nouls: is every criterion in `steps[i].criteria` an observable outcome rather than an intention; does `steps[i].evidence` name a concrete, checkable artifact. Per requirement, a Choice over the step ids plus `none`: which step covers `requirements[j]`. A Noul below 0.7 means `uncertain`, resolved under the same rule. `none` means `fail` on goal coverage.
- **Evidence gate** (steps 5 and 7). State: `{criteria: [{criterion, evidence}]}`, where evidence is the summarized artifact itself (command and result line, diff summary), not your claim that it passed. Per criterion, a Choice: `proves` / `contradicts` / `insufficient`. `proves` with confidence ≥ 0.8 corroborates the pass. `contradicts` means `fail`. Anything else means `uncertain`, resolved under the `uncertain` rule in Subagent roles (re-ask Jev after gathering stronger evidence).
- **Repair gate** (step 6). State: `{failure, previous_approach, revised_approach}`. Noul: is `revised_approach` a materially different approach rather than the same fix retried with minor changes. Below 0.5 means replan before spending the attempt.

```json
POST https://api.typesafe.ai/v1/systemone   (Authorization: Bearer $TYPESAFE_API_KEY)
{"model": "jev-latest",
 "state": {"criteria": [{"criterion": "`pytest -q` exits 0", "evidence": "pytest -q -> 41 passed, 2 failed (exit 1)"}]},
 "questions": {"c0": {"type": "choice", "instructions": "How does `criteria[0].evidence` relate to `criteria[0].criterion`?",
   "criteria": {"proves": "Directly demonstrates the criterion is met", "contradicts": "Shows the criterion is not met", "insufficient": "Does not address the criterion, or too vague to tell"}}}}
```

Answers return under the same ids: Noul gives `noul` (probability of yes); Choice gives `choice`, `probabilities`, `confidence`.

Question rules: Jev reads literally, so write the exact condition and ask one judgment per question. Reference state by backticked path. Send only the fields a question needs, never the whole PRD or diff. Keep counts, exit codes, and date math in code. State follows the artifact rule: summaries only. No secrets, user data, raw command output, or prompt contents. The thresholds above are conservative starting points, not tuned values. Record each gate's question ids, answers, and the response `model` in the progress doc, and state in the report whether Jev gates ran.
