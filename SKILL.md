---
name: lfg
version: "1.0.0"
description: Bounded research, planning, implementation, validation, and review loop for complex coding tasks.
tags:
  - agent-workflows
  - planning
  - code-review
  - validation
---

# LFG — Lets Fucking Go

Use this skill when the user wants an implementation driven by explicit research, a written plan, and a review/repair loop.

Coordination should happen mainly through files, especially:

- an HTML PRD document that contains the definition, constraints, plan, step-level acceptance criteria, judge rubric, and final acceptance target;
- an HTML progress document that records step status, evidence, reviewer findings, repair loops, validation output, and final result.

## Core Definition

LFG is a bounded workflow:

1. **Research** — understand the codebase, existing behavior, constraints, security model, and user intent.
2. **Define** — state the key concept in project-specific terms before changing code.
3. **Plan with a planner subagent** — when subagents are available, spawn a planning-focused subagent to challenge assumptions, propose steps, and attach acceptance criteria to every step.
4. **Coordinate through HTML files** — write/update the PRD HTML and progress HTML so humans and subagents share the same source of truth.
5. **Implement** — make focused changes for one planned step at a time.
6. **Evaluate** — compare the completed step against its acceptance criteria using evidence from code review, tests, or runtime checks.
7. **Repeat or advance** — if the step does not meet its acceptance criteria, repair and repeat that same step; only advance once it passes.
8. **Review with an LLM-as-judge subagent** — when subagents are available, spawn a reviewer/judge subagent to score correctness, criteria coverage, taste, and originality.
9. **Repair** — fix review/test findings, then re-run relevant validation.
10. **Report** — summarize changed files, validation evidence, residual risks, and follow-ups.

The loop is not an open-ended autonomous process. Stop when all step-level and overall acceptance criteria are met, when a blocker needs user input, or after a bounded repair pass (see below).

## Triage: when to use the full loop

Run the full PRD HTML + progress HTML + planner + dual reviewer loop for **broad, ambiguous, design-sensitive, or security-sensitive** work. For small, well-scoped changes, use a fast path and say so explicitly:

- **Full loop** (default for the triggers above): PRD HTML, progress HTML, planner subagent, plan-review gate, per-step acceptance criteria, implementation-review gate.
- **Fast path** (use only when *all* are true): the change touches roughly ≤30 lines across ≤3 files, has no security/IPC/approval/path/browser surface, has no UX/copy/architecture impact, and has an obvious validation command. In fast path: skip the PRD HTML and progress HTML, skip the planner and plan-review gate, make the change directly, run validation, and do a single self-review against the user's stated goal. Still run an implementation-review pass if a reviewer subagent is cheap and the change is non-trivial.
- Never silently use the fast path for security-sensitive boundaries (approvals, IPC handlers, preload bridge, path validation, browser risk routing, Markdown/file rendering, shell protection). If unsure, default to the full loop.

## File coordination

Prefer file-based coordination over hidden conversational state. The parent agent, planner subagent, reviewer subagent, and human should all be able to inspect the same artifacts.

**Why HTML (not Markdown).** Rendered HTML gives real structure — sections, tables, status chips, and links to changed files — and opens directly in a browser without a separate viewer, so the PRD and progress docs double as a human-readable dashboard. Markdown would collapse this to flat text. Keep the HTML well-formed and self-contained (inline minimal CSS, no external scripts, no remote fetches) so it renders from `file://` and stays safe to share. Escape any code/output snippets inside `<code>`/`<pre>` to avoid breaking markup.

Default artifact names:

- `docs/<task-slug>-prd.html` — the product/implementation requirements document.
- `docs/<task-slug>-progress.html` — the live progress and evidence log.

Use another directory if the repo has a better convention, but keep both files in the project unless the user asks for temporary artifacts.

### PRD HTML requirements

The PRD document should be human-readable HTML, not only Markdown, so it can be opened directly in a browser. It should include:

- task title and short summary;
- project-specific definition of the core concept/problem;
- goals and non-goals;
- constraints, especially privacy/security constraints;
- step-by-step plan;
- acceptance criteria for every step;
- evidence required for every acceptance criterion;
- validation commands;
- LLM-as-judge rubric, including taste and originality where relevant;
- final overall acceptance criteria.

### Progress HTML requirements

The progress document should be the running coordination log. Update it after each step and after every reviewer/judge pass. It should include:

- current status: `planned`, `in-progress`, `blocked`, `repairing`, `escalated`, or `complete`;
- checklist of planned steps;
- for each step: acceptance criteria, evidence gathered, pass/fail/uncertain status, and repair attempts;
- links or paths to changed files;
- validation commands and results;
- reviewer/judge findings;
- taste/originality scores when relevant;
- residual risks and final outcome.

Do not rely on chat history alone for coordination. If a subagent produces a plan or review, copy the important decisions/findings into the PRD or progress HTML.

## Session durability (tape and memory)

A bounded loop can outlive a single conversation (compaction, handoff, re-entry). Use the harness's durable-state tools so the work survives:

- **Tape anchors.** Record a `tape_handoff` anchor at loop start (`task/begin`), a `task/plan-approved` anchor once the plan-review gate passes, a `task/step-N-done` anchor as each step meets its criteria, and a `task/complete` anchor at the end. Each anchor's summary should name the task slug, current step, and status. On re-entry, read forward from the last anchor to recover state instead of replaying chat.
- **File fallback when tape is unavailable.** If the tape tool is not present in this harness, mirror the same checkpoints into a small handoff file (default `docs/<task-slug>-handoff.md`) or an append-only section of the progress HTML: one timestamped line per checkpoint (`begin` / `plan-approved` / `step-N-done` / `complete` / `blocked`) carrying the task slug, step, status, and a pointer to evidence. The parent and any re-entering session read that file the same way they would read anchors. Do not duplicate it into chat.
- **Memory.** At loop completion (or when a durable decision/risk is discovered), write a short memory file capturing the definition used, key decisions, non-goals, residual risks, and follow-ups — so the next session inherits the context. Use the project memory-write skill if available; otherwise note the durable facts in the final report.
- **Skip only when cheap and short.** For the fast path (see Triage), tape/memory handoff is optional. For the full loop it is recommended, not optional.

Never put secrets, private keys, prompt contents, or raw browser DOM into tape anchors or memory files — summarize, never copy.

## Subagent roles

Use subagents as advisory critics, not as unbounded autonomous owners. Before invoking subagents, list available agents with the subagent tool and choose executable, non-disabled agents. If no suitable planner/reviewer exists, use the closest worker/reviewer-style agent and include these directives in the task. If no subagents are available, perform the same role manually and say so.

### Choosing agents by traits

Prefer agents whose declared traits match the role; if none match exactly, pick the closest and inject the role directives via the task string.

| Role | Preferred traits | Acceptable fallback | Avoid |
| --- | --- | --- | --- |
| Planner | read-only/no-edit, analysis/architecture posture, fresh context, can read project files | any code-analysis or advisory agent; pass the planner directives in the task | agents that auto-edit; fork-context clones inheriting in-flight edits |
| Reviewer (plan gate) | read-only, strict/critic posture, fork context (judges a snapshot) | a second analysis agent with a critic prompt | the same agent that wrote the plan |
| Reviewer (impl gate) | read-only, can read diffs + run validation, fork context | a code-review or test-focused agent | agents with edit access unless you explicitly want self-repair |

In all cases: pass the role-specific directives from this skill in the task, confirm the agent is executable and not disabled, and prefer `fork` context for reviewers so they judge a stable snapshot. If the harness exposes a packaged planner/reviewer (e.g. a `pi-subagents` review/critique agent), prefer it over a generic worker. Note the chosen agent's name and trait match in the progress HTML so re-entry knows what to re-invoke.

### Planner subagent attributes

Spawn before implementation for broad or design-sensitive work.

Directives for the planner:

- Act as a skeptical product-minded architect, not a code generator.
- Restate the project-specific definition and constraints.
- Produce a step-by-step plan with **acceptance criteria for every step**, returned as text for the parent agent to write into the PRD HTML. Do not write or update the PRD HTML yourself; the planner returns a plan and risk review only.
- Include evidence required for each criterion: test command, diff inspection, screenshot, log excerpt, reviewer note, or manual check.
- Specify what the progress HTML should track for each step.
- Call out security/privacy risks and non-goals.
- For UI, UX, copy, docs, product, or architecture work, include **taste and originality acceptance criteria**.
- Prefer simple, cohesive, idiomatic changes over clever or sprawling ones.
- Do not edit files; return a plan and risk review only.

Planner task template:

```text
Act as the lfg planner for this task. Define the core concept in project-specific terms, then produce a step-by-step plan for the PRD HTML. Every step must include acceptance criteria and required evidence. Include privacy/security constraints, non-goals, progress HTML tracking requirements, and taste/originality criteria where applicable. Do not implement.
```

### Reviewer / LLM-as-judge subagent attributes

Spawn twice when useful: once before implementation to review the plan, and again after implementation to review the actual diff and validation evidence.

Plan-review directives for the reviewer/judge:

- Act as a strict but constructive plan gatekeeper.
- Evaluate the PRD HTML before implementation begins.
- Confirm the plan defines the goal in project-specific terms and includes a clear **definition of done**.
- Confirm the plan addresses every user goal requirement and constraint.
- Confirm proper research was performed: relevant files/docs were inspected, existing behavior was understood, and security/privacy implications were considered.
- Confirm open questions, ambiguities, and assumptions are explicitly listed and either answered, resolved, or marked as blockers requiring user input.
- Confirm every planned step has acceptance criteria and required evidence.
- Confirm the plan includes validation commands and a final acceptance target.
- Confirm taste/originality criteria are present for design-sensitive work.
- Mark plan items as `pass`, `fail`, or `uncertain`; any missing required item blocks implementation.

Implementation-review directives for the reviewer/judge:

- Act as a strict but constructive implementation judge.
- Evaluate each planned step separately against its acceptance criteria using the PRD HTML and progress HTML as the source of truth.
- Mark each criterion as `pass`, `fail`, or `uncertain` with evidence.
- Treat unmet required criteria as blockers.
- Include a taste/originality rubric when relevant.
- Do not edit files unless explicitly asked; return findings only.

LLM-as-judge rubric:

| Area | Required judgment |
| --- | --- |
| Correctness | Does the change solve the stated problem without regressions? |
| Acceptance coverage | Does every planned criterion have evidence? |
| Security/privacy | Are secrets, credentials, private keys, prompt contents, command output, and any approval-gated effects handled safely (and DOM/UI-state, where the project exposes it)? |
| Simplicity | Is the design cohesive, idiomatic, and not over-engineered? |
| Taste | Does the UX/API/copy/architecture feel polished, restrained, and product-appropriate? |
| Originality | Does the solution avoid generic, cookie-cutter output while staying consistent with the project? |
| Maintainability | Will future contributors understand and extend it? |
| Validation | Were the right tests/checks/manual verifications run? |

Taste/originality scoring:

- `5`: distinctive, elegant, cohesive, and clearly better than the obvious generic solution.
- `4`: polished and project-appropriate with some fresh thinking.
- `3`: acceptable but conventional.
- `2`: bland, clunky, over-familiar, or poorly integrated.
- `1`: generic, incoherent, or aesthetically/product-wise harmful.

A score below `4` on taste or originality should trigger a repair loop for design-sensitive work unless the user explicitly prefers speed over polish.

Plan-review task template:

```text
Act as the lfg LLM-as-judge plan reviewer. Review the PRD HTML before implementation. Verify that the plan has a project-specific definition, clear definition of done, complete goal coverage, proper research evidence, answered or explicitly blocked open questions, step-level acceptance criteria, required evidence for every criterion, validation commands, and taste/originality criteria where relevant. Mark each area pass/fail/uncertain and list blockers. Do not edit.
```

Implementation-review task template:

```text
Act as the lfg LLM-as-judge implementation reviewer. Review the diff and validation evidence against the PRD HTML and progress HTML. For every planned step, mark each acceptance criterion pass/fail/uncertain with evidence. Score taste and originality from 1-5 where relevant, and list blocking fixes before merge. Do not edit.
```

## Workflow

### 1. Inspect context

- Check the current branch and working tree.
- Preserve unrelated user changes and untracked files.
- Read project instructions and the files relevant to the request.
- If the request concerns Pi itself, read the relevant Pi docs before implementation.
- For the full loop, record a `tape_handoff` anchor (`task/begin`) summarizing the task slug and intent so the loop survives compaction or re-entry (or append a `begin` line to `docs/<task-slug>-handoff.md` if tape is unavailable).

### 2. Define the concept first

Before writing code, define the core term in this project's language. Include:

- what it means here;
- what it explicitly does not mean;
- privacy/security implications;
- measurable success criteria.

For example, for HyperDesk "observability" means local, structured, privacy-preserving diagnostics — not remote telemetry or product analytics.

### 3. Write or update a plan

For broad, ambiguous, design-sensitive, or architecture-sensitive work, invoke the planner subagent first and use its output to shape the plan. Create or update the PRD HTML and initialize the progress HTML before implementation. Then invoke the reviewer/judge subagent to review the plan before implementation. The plan should include:

- phases or steps;
- explicit acceptance criteria for every step;
- evidence needed to prove each step is complete;
- definition of done;
- coverage of every user goal requirement and constraint;
- research evidence and files/docs inspected;
- open questions, assumptions, and their answers or blocker status;
- non-goals;
- validation commands;
- risks and privacy/security constraints;
- taste and originality criteria when the work touches UX, UI, copy, architecture, docs, or product feel.

Each planned step should use this shape:

```markdown
- Step N: <action>
  - Acceptance criteria:
    - <observable condition that must be true>
    - <test/review/doc evidence required>
  - Validation/evidence: <command, file diff, screenshot, reviewer note, etc.>
```

Do not start implementation until the planned steps have acceptance criteria, the plan has a definition of done, goal requirements and open questions are addressed, both the PRD HTML and progress HTML exist, and the plan-review pass has no blocking findings. (For lightweight changes, see Triage: use the fast path instead of this full gate.) When the plan-review gate passes, record a `task/plan-approved` tape anchor (or a `plan-approved` line in the handoff file) so re-entry can resume from implementation.

### 4. Implement in focused step loops

For each planned step:

1. Read the PRD HTML and current progress HTML.
2. Implement only the current step.
3. Gather the step's required evidence.
4. Update the progress HTML with changed files, validation output, criterion status, and notes.
5. Compare the result against every acceptance criterion for that step.
6. If any criterion is unmet, mark the step `repairing`, repair, update progress HTML, and repeat the same step.
7. Advance to the next step only after the current step meets its criteria.

**Bounded repair with replanning.** On any step failure (or a taste/originality <4 for design-sensitive work), do not blindly retry the same fix. First evaluate the failure: read the error/evidence, update the progress HTML with the diagnosis, and produce a *better plan for that step* (revised approach, smaller sub-step, or new acceptance evidence) before re-attempting. The loop should continue for **at least 15 repair/replan iterations across the whole task** before escalating to a human, and each iteration must carry a fresh plan, not a repeat. Escalate to the user earlier only on a true blocker: a missing dependency/permission, an ambiguous requirement needing user input, or the *same* failure with no new plan available after 3 distinct replans of that one step. This is what makes the loop genuinely bounded yet persistent.

Implementation guidance:

- Prefer small modules and explicit integration points.
- Avoid logging or exposing secrets, prompts, command output, browser DOM, private keys, or credentials unless the task explicitly requires it.
- Keep security-sensitive approval, IPC, path, and browser boundaries intact.
- Use exact edit tools for targeted edits.
- Do not edit generated `build/`/`dist/` output; edit sources and rebuild.
- As each step meets its criteria, record a `task/step-N-done` tape anchor (or a `step-N-done` line in the handoff file) summarizing what passed and the evidence path, so progress is recoverable.

### 5. Review loop

If subagents are available, run the reviewer / LLM-as-judge subagent for two gates: first on the PRD plan before implementation, then on the implementation after changes. First list agents with the subagent tool, then choose an executable reviewer/critic agent if present. Ask it to review the plan for definition of done, goal coverage, research completeness, open questions, acceptance criteria, validation, and taste/originality where relevant. After implementation, ask it to review the uncommitted diff for correctness, security/privacy, test coverage, plan compliance, and taste/originality where relevant. Do not let the reviewer edit unless explicitly desired.

If the judge marks any required acceptance criterion as `fail` or gives taste/originality below `4` for design-sensitive work, repair and repeat the relevant implementation step before finalizing.

If no suitable subagent exists, perform the same checklist manually.

### 6. Validate and repair

Run the project's canonical build/lint/check command — the architecture-equivalent of `npm run check` (e.g. `cargo check`, `go build ./...`, `pytest -q`, `gleam check`, `npm test`). Discover it from `package.json` scripts, the project's AGENTS.md, or the nearest task runner. For smaller changes, run targeted syntax/smoke checks first; for larger ones, run the full suite. Fix findings and re-run the failing validation until green.

Example (HyperDesk): `npm run check` then `npm test`.

### 7. Final report

Return a concise summary with:

- definition used;
- implementation summary;
- files changed;
- validation run and result;
- reviewer findings addressed;
- residual risks or follow-ups.

Record a `task/complete` tape anchor (or a `complete` line in the handoff file) and write a concise memory file (or note durable facts in the report if no memory tool is available) capturing the definition used, key decisions, non-goals, and residual risks, so the next session inherits the context. Do not store secrets, private keys, prompt contents, or raw browser DOM in anchors or memory.

**Commit cadence.** Commit frequency should scale with loop length, not happen ad hoc:

- Short loop (≤3 steps / fast path): one commit at `task/complete`.
- Medium loop (4–8 steps): commit at each `step-N-done` checkpoint.
- Long loop (>8 steps): commit at each `step-N-done` and again at `complete`; consider a commit at `plan-approved` too.

Never commit mid-repair (while a step is `repairing`). Before committing, verify the working tree has no unrelated changes and that no autoresearch `log_experiment` auto-commit is racing this loop — if it is, let autoresearch own commits and skip manual commits here. Commit only intended files, plus the PRD/progress/handoff artifacts if the user wants them tracked; leave unrelated untracked files untouched.

If the user asked for a branch/PR, push the branch and include the PR URL.
