---
name: lfg
version: "3"
description: Bounded research → plan → implement → review loop for complex coding tasks. Use when the user says lfg, lets-fucking-go, or wants to research then implement with a written plan and per-step acceptance criteria verified by evidence.
---
# LFG — Lets Fucking Go

Give your agent a loop that actually ships.

A local agent can read files, write code, run commands, and respond to prompts. But complex work — architecture decisions, multi-step refactors, security-sensitive changes — needs more than a chat session. It needs a bounded process with evidence, review gates, and a way to keep going when things break.

The LFG skill turns your agent from a code monkey into a disciplined engineer.

Once activated, your agent can:

- Research a codebase and define the problem in project-specific terms before touching code.
- Write a plan with per-step acceptance criteria and required evidence — not guesses.
- Implement step by step, validate each one, and repair failures with fresh plans.
- Run an LLM-as-judge review for correctness, security, simplicity, taste, and originality.
- Keep working across session boundaries with file-based coordination and checkpoints.

No browser hopping. No hidden state in chat. No "let me think about this" loops that never terminate.

Just a disciplined process your agent follows every time.

## What this looks like in practice

Imagine you need to add authentication to an existing API.

Without LFG, your agent jumps straight to writing code. It guesses at the plan, implements in one shot, and hopes the tests pass. If they don't, it retries the same fix. If the auth boundary is wrong, you don't know until deployment.

With LFG, your agent:

1. **Researches** the codebase, finds where auth flows currently live, and notes the security model.
2. **Defines** what "authentication" means in this project — not the generic concept, but the specific tokens, sessions, or OAuth flows already in use.
3. **Plans** with a planner subagent: three steps, each with acceptance criteria and evidence requirements.
4. **Gets reviewed** before implementing: a judge subagent checks the plan for gaps, security risks, and scope creep.
5. **Implements step by step**, validating each one. If step 2 fails, it diagnoses the failure, writes a better plan, and tries again — up to 15 times.
6. **Reviews the diff** with the judge: correctness, security, simplicity, taste.
7. **Reports** what changed, what was validated, what's still risky.

The result isn't just "code that works." It's code that was planned, reviewed, and proven — with a paper trail anyone can inspect.

## The problem

Most agent "loops" drift.

Your agent starts with a goal, writes some code, runs some tests, and calls it done. But the goal was vague. The tests weren't tied to the goal. The agent didn't check whether the change actually solved the problem or just happened to make the tests green.

Worse, the state lives in chat. When the session compacts or restarts, the agent replays from scratch — same mistakes, same guesses, same loops.

LFG fixes this with four principles:

- **Coordination through files.** An HTML PRD and an HTML progress doc are the single source of truth. The agent, subagents, and human all inspect the same artifacts. Chat history is never the plan.
- **Acceptance criteria per step.** Every planned step ships with observable conditions and the evidence required to prove them — before any code is written.
- **Replan, don't just retry.** On failure, diagnose and write a better plan for that step. The loop runs at least 15 repair/replan iterations before escalating.
- **Session checkpoints.** Anchors at `begin` → `plan-approved` → `step-N-done` → `complete` survive compaction and re-entry. Re-entering sessions recover state from the last checkpoint instead of replaying chat.

## Quick reference

Before starting, answer these three questions:

| Question | Full loop | Fast path |
|---|---|---|
| Touches ≤30 lines across ≤3 files? | Maybe | Yes |
| No security / IPC / approval / path / browser surface? | — | Yes |
| No UX / copy / architecture impact? | — | Yes |
| Clear validation command exists? | — | Yes |

If **all** answers say "Yes" → fast path. If any says "Maybe" or "No" → full loop. Security-sensitive boundaries **never** get the fast path.

## The loop

Ten phases, two triage modes, one bounded repair pass.

```
01 Research  →  02 Define  →  03 Plan  →  04 Coordinate  →  05 Implement
                                                                          ↕
06 Evaluate  →  07 Repeat / advance  →  08 Judge  →  09 Repair  →  10 Report
```

## What your agent does through LFG

| Capability | What it enables |
|---|---|
| **Subagent orchestration** | Planner + judge gates — advisory critics, not autonomous owners |
| **Session checkpointing** | Durability across compaction and re-entry |
| **Durable memory write** | Save decisions, non-goals, and risks so the next session inherits context |
| **Project build/check command** | Step validation against the project's own task runner |
| **HTML coordination** | Human-readable PRD and progress docs that open in a browser |
| **LLM-as-judge review** | Correctness, coverage, security, simplicity, taste, originality scoring |

## Install

Place a `SKILL.md` with YAML frontmatter in your agent's skills directory.

**Project scope** (this repo only):

```
mkdir -p .agent/skills/lfg
# save SKILL.md at .agent/skills/lfg/SKILL.md
```

**User scope** (all projects):

```
mkdir -p ~/.agent/skills/lfg
# save SKILL.md at ~/.agent/skills/lfg/SKILL.md
```

Verify frontmatter loads:

```yaml
---
name: lfg
version: "3"
description: Bounded research → plan → implement → review loop …
---
```

The skill triggers on: `lfg`, `lets-fucking-go`, `research-plan-loop`.

### Requirements (optional but recommended)

| Capability | Used for | If absent |
|---|---|---|
| Subagent orchestration | Planner + judge gates | Parent performs both roles manually |
| Session checkpointing | Durability / re-entry | Falls back to `docs/<slug>-handoff.md` |
| Durable memory write | Save decisions at completion | Facts noted in the final report |
| Project build/check command | Step validation | Run whatever the project's task runner exposes |

## Triage: full loop vs fast path

**Full loop** — default for broad, ambiguous, design-sensitive, or security-sensitive work. Runs the complete ceremony: PRD HTML, progress HTML, planner subagent, plan-review gate, per-step acceptance criteria, implementation-review gate.

**Fast path** — only when all three conditions are true:

1. Change touches ≤30 lines across ≤3 files
2. No security/IPC/approval/path/browser/UX/copy/architecture surface
3. An obvious validation command exists

In fast path: skip PRD/progress HTML, skip planner and plan-review gate, make the change directly, run validation, and do a single self-review against the user's stated goal. Run an implementation-review pass if a reviewer subagent is cheap and the change is non-trivial.

**Never** silently use the fast path for security-sensitive boundaries (approvals, IPC handlers, preload bridge, path validation, browser risk routing, Markdown/file rendering, shell protection). When in doubt, default to the full loop.

## File coordination

Prefer file-based coordination over hidden conversational state. The parent agent, planner subagent, reviewer subagent, and human should all be able to inspect the same artifacts.

**Why HTML (not Markdown).** Rendered HTML gives real structure — sections, tables, status chips, and links to changed files — and opens directly in a browser without a separate viewer, so the PRD and progress docs double as a human-readable dashboard. Markdown would collapse this to flat text. Keep the HTML well-formed and self-contained (inline minimal CSS, no external scripts, no remote fetches) so it renders from `file://` and stays safe to share. Escape any code/output snippets inside `<code>`/`<pre>` to avoid breaking markup.

Default artifact names:

- `docs/-prd.html` — the product/implementation requirements document.
- `docs/-progress.html` — the live progress and evidence log.

Use another directory if the repo has a better convention, but keep both files in the project unless the user asks for temporary artifacts.

### PRD HTML structure

```html
<!-- Head -->
<h1>[task title]</h1>
<p><strong>Definition:</strong> [project-specific concept definition]</p>
<p><strong>Non-goals:</strong> [what this does not do]</p>

<!-- Constraints -->
<h2>Constraints</h2>
<ul><li>[privacy/security constraints]</li></ul>

<!-- Plan -->
<h2>Plan</h2>
<table>
  <tr><th>Step</th><th>Acceptance criteria</th><th>Evidence</th></tr>
  <!-- one row per step -->
</table>

<!-- Validation -->
<h2>Validation</h2>
<pre><code>[command]</code></pre>

<!-- Rubric -->
<h2>Judge rubric</h2>
<p>[correctness, coverage, security, simplicity, taste, originality, maintainability]</p>

<!-- Final -->
<h2>Definition of done</h2>
<ul><li>[final acceptance criteria]</li></ul>
```

### Progress HTML structure

Update after each step and every reviewer/judge pass. Include:

- **Status**: `planned` | `in-progress` | `blocked` | `repairing` | `escalated` | `complete`
- **Steps**: acceptance criteria, evidence gathered, pass/fail/uncertain, repair attempts
- **Files**: paths to changed files
- **Validation**: commands and results
- **Judge**: findings and taste/originality scores
- **Risks**: residual risks and final outcome

Do not rely on chat history for coordination. Copy subagent plans and reviews into the PRD or progress HTML.

## Session durability (checkpoints and memory)

A bounded loop can outlive a single conversation (compaction, handoff, re-entry).

- **Session checkpoints.** Record a checkpoint at loop start (`task/begin`), `task/plan-approved` after the plan-review gate passes, `task/step-N-done` as each step meets its criteria, and `task/complete` at the end. Each checkpoint's summary names the task slug, current step, and status. On re-entry, read forward from the last checkpoint to recover state instead of replaying chat.
- **File fallback.** If native checkpointing is unavailable, mirror checkpoints into `docs/-handoff.md` (or an append-only section of the progress HTML): one timestamped line per checkpoint (`begin` / `plan-approved` / `step-N-done` / `complete` / `blocked`) with task slug, step, status, and evidence pointer. The parent and any re-entering session read that file the same way.
- **Memory.** At loop completion, write a memory file capturing the definition used, key decisions, non-goals, residual risks, and follow-ups. Use the agent's durable memory tool if available; otherwise note durable facts in the final report.
- **Fast path exception.** Checkpoint/memory handoff is optional in the fast path. For the full loop it is recommended, not optional.

> **Security note:** Never put secrets, private keys, prompt contents, or raw browser DOM into checkpoints or memory files — summarize, never copy.

## Subagent roles

Use subagents as advisory critics, not as unbounded autonomous owners. List available agents and choose executable, non-disabled ones. If no suitable planner/reviewer exists, use the closest worker/reviewer-style agent and inject the role directives via the task string. If no subagents are available, perform the same role manually and say so.

### Agent selection

| Role | Preferred traits | Acceptable fallback | Avoid |
|---|---|---|---|
| Planner | read-only/no-edit, analysis/architecture posture, fresh context, can read project files | any code-analysis or advisory agent | agents that auto-edit; fork-context clones inheriting in-flight edits |
| Reviewer (plan gate) | read-only, strict/critic posture, fork context | a second analysis agent with a critic prompt | the same agent that wrote the plan |
| Reviewer (impl gate) | read-only, can read diffs + run validation, fork context | a code-review or test-focused agent | agents with edit access unless self-repair is wanted |

Prefer `fork` context for reviewers so they judge a stable snapshot. Note the chosen agent's name and trait match in the progress HTML.

### Planner

Spawn before implementation for broad or design-sensitive work.

**Directives:**

- Act as a skeptical product-minded architect, not a code generator.
- Restate the project-specific definition and constraints.
- Produce a step-by-step plan with **acceptance criteria for every step**, returned as text. Do not write or update the PRD HTML yourself; return a plan and risk review only.
- Include evidence required for each criterion: test command, diff inspection, screenshot, log excerpt, reviewer note, or manual check.
- Specify what the progress HTML should track for each step.
- Call out security/privacy risks and non-goals.
- For UI, UX, copy, docs, product, or architecture work, include **taste and originality acceptance criteria**.
- Prefer simple, cohesive, idiomatic changes over clever or sprawling ones.
- Do not edit files; return a plan and risk review only.

**Planner task template:**

```
Act as the lfg planner for this task. Define the core concept in project-specific terms, then produce a step-by-step plan for the PRD HTML. Every step must include acceptance criteria and required evidence. Include privacy/security constraints, non-goals, progress HTML tracking requirements, and taste/originality criteria where applicable. Do not implement.
```

### Reviewer / LLM-as-judge

Spawn twice when useful: once before implementation to review the plan, and again after implementation to review the actual diff and validation evidence.

**Plan-review directives:**

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

**Implementation-review directives:**

- Act as a strict but constructive implementation judge.
- Evaluate each planned step separately against its acceptance criteria using the PRD HTML and progress HTML as the source of truth.
- Mark each criterion as `pass`, `fail`, or `uncertain` with evidence.
- Treat unmet required criteria as blockers.
- Include a taste/originality rubric when relevant.
- Do not edit files unless explicitly asked; return findings only.

**LLM-as-judge rubric:**

| Area | Required judgment |
|---|---|
| Correctness | Does the change solve the stated problem without regressions? |
| Acceptance coverage | Does every planned criterion have evidence? |
| Security/privacy | Are secrets, credentials, private keys, prompt contents, command output, and any approval-gated effects handled safely (and DOM/UI-state, where the project exposes it)? |
| Simplicity | Is the design cohesive, idiomatic, and not over-engineered? |
| Taste | Does the UX/API/copy/architecture feel polished, restrained, and product-appropriate? |
| Originality | Does the solution avoid generic, cookie-cutter output while staying consistent with the project? |
| Maintainability | Will future contributors understand and extend it? |
| Validation | Were the right tests/checks/manual verifications run? |

**Taste/originality scoring:**

- `5`: distinctive, elegant, cohesive, and clearly better than the obvious generic solution.
- `4`: polished and project-appropriate with some fresh thinking.
- `3`: acceptable but conventional.
- `2`: bland, clunky, over-familiar, or poorly integrated.
- `1`: generic, incoherent, or aesthetically/product-wise harmful.

A score below `4` on taste or originality should trigger a repair loop for design-sensitive work unless the user explicitly prefers speed over polish.

**Plan-review task template:**

```
Act as the lfg LLM-as-judge plan reviewer. Review the PRD HTML before implementation. Verify that the plan has a project-specific definition, clear definition of done, complete goal coverage, proper research evidence, answered or explicitly blocked open questions, step-level acceptance criteria, required evidence for every criterion, validation commands, and taste/originality criteria where relevant. Mark each area pass/fail/uncertain and list blockers. Do not edit.
```

**Implementation-review task template:**

```
Act as the lfg LLM-as-judge implementation reviewer. Review the diff and validation evidence against the PRD HTML and progress HTML. For every planned step, mark each acceptance criterion pass/fail/uncertain with evidence. Score taste and originality from 1-5 where relevant, and list blocking fixes before merge. Do not edit.
```

## Workflow

### 1. Inspect context

- Check the current branch and working tree.
- Preserve unrelated user changes and untracked files.
- Read project instructions and the files relevant to the request.
- For the full loop, record a session checkpoint (`task/begin`) summarizing the task slug and intent.

### 2. Define the concept first

Before writing code, define the core term in this project's language:

- what it means here;
- what it explicitly does not mean;
- privacy/security implications;
- measurable success criteria.

### 3. Write or update a plan

For broad, ambiguous, design-sensitive, or architecture-sensitive work, invoke the planner subagent first. Create or update the PRD HTML and initialize the progress HTML before implementation. Then invoke the reviewer/judge subagent to review the plan before implementation.

Each planned step uses this shape:

```markdown
- Step N: [title]
  - Acceptance criteria:
    - [criterion 1]
    - [criterion 2]
  - Validation/evidence: [how to prove it]
```

Do not start implementation until:

- All planned steps have acceptance criteria
- The plan has a definition of done
- Goal requirements and open questions are addressed
- Both PRD HTML and progress HTML exist
- The plan-review pass has no blocking findings

When the plan-review gate passes, record a `task/plan-approved` checkpoint so re-entry can resume from implementation.

### 4. Implement in focused step loops

For each planned step:

1. Read the PRD HTML and current progress HTML.
2. Implement only the current step.
3. Gather the step's required evidence.
4. Update the progress HTML with changed files, validation output, criterion status, and notes.
5. Compare the result against every acceptance criterion for that step.
6. If any criterion is unmet, mark the step `repairing`, repair, update progress HTML, and repeat the same step.
7. Advance to the next step only after the current step meets its criteria.

**Bounded repair with replanning.** On any step failure (or taste/originality <4 for design-sensitive work), do not blindly retry the same fix. First diagnose:

1. Read the error/evidence.
2. Update the progress HTML with the diagnosis (what failed, why, what was tried).
3. Produce a *better plan* for that step — revised approach, smaller sub-step, or new acceptance evidence.
4. Re-attempt with the new plan.

Continue for **at least 15 repair/replan iterations across the whole task** before escalating. Each iteration must carry a fresh plan, not a repeat.

Escalate earlier only on true blockers:

- Missing dependency or permission
- Ambiguous requirement needing user input
- Same failure with no new plan available after 3 distinct replans of that one step

**Implementation guidance:**

- Prefer small modules and explicit integration points.
- Avoid logging or exposing secrets, prompts, command output, browser DOM, private keys, or credentials.
- Keep security-sensitive approval, IPC, path, and browser boundaries intact.
- Use exact edit tools for targeted edits.
- Do not edit generated `build/`/`dist/` output; edit sources and rebuild.
- As each step meets its criteria, record a `task/step-N-done` checkpoint.

### 5. Review loop

If subagents are available, run the reviewer / LLM-as-judge subagent for two gates:

1. **Plan gate** — review the PRD before implementation (definition of done, goal coverage, research completeness, open questions, acceptance criteria, validation, taste/originality).
2. **Implementation gate** — review the uncommitted diff after changes (correctness, security/privacy, test coverage, plan compliance, taste/originality).

Do not let the reviewer edit unless explicitly desired. If the judge marks any required criterion as `fail` or gives taste/originality below `4` for design-sensitive work, repair and repeat the relevant implementation step before finalizing.

If no suitable subagent exists, perform the same checklist manually.

### 6. Validate and repair

Run the project's canonical build/lint/check command — `cargo check`, `go build ./...`, `pytest -q`, `gleam check`, `npm test`, etc. Discover it from `package.json` scripts, the project's agent instructions, or the nearest task runner. For smaller changes, run targeted syntax/smoke checks first; for larger ones, run the full suite. Fix findings and re-run the failing validation until green.

### 7. Final report

Return a concise summary with:

- definition used;
- implementation summary;
- files changed;
- validation run and result;
- reviewer findings addressed;
- residual risks or follow-ups.

Record a `task/complete` checkpoint and write a memory file (or note durable facts in the report) capturing the definition used, key decisions, non-goals, and residual risks. Do not store secrets, private keys, prompt contents, or raw browser DOM in checkpoints or memory.

**Commit cadence.** Commit frequency should scale with loop length:

- Short loop (≤3 steps / fast path): one commit at `task/complete`.
- Medium loop (4–8 steps): commit at each `step-N-done` checkpoint.
- Long loop (>8 steps): commit at each `step-N-done` and again at `complete`; consider a commit at `plan-approved` too.

Never commit mid-repair (while a step is `repairing`). Before committing, verify the working tree has no unrelated changes. Commit only intended files, plus the PRD/progress/handoff artifacts if the user wants them tracked; leave unrelated untracked files untouched.

If the user asked for a branch/PR, push the branch and include the PR URL.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Loop never terminates | No acceptance criteria defined | Define criteria before starting implementation |
| Same failure repeats | Not replanning, just retrying | Diagnose, write a better plan, try again |
| Subagent ignores directives | Wrong agent selected or directives not passed | Choose agent with matching traits, pass role directives in task |
| Progress HTML not updating | Relying on chat state | Copy subagent outputs into progress HTML explicitly |
| Taste score below 4 | Generic/cookie-cutter solution | Trigger repair loop, ask for more original approach |

## The important shift

LFG changes the role of your agent.

It is no longer limited to writing code in a chat session. It becomes a disciplined engineer that researches, plans with evidence, implements step by step, reviews its work, and repairs failures with fresh plans.

Your harness becomes the operator.

The loop becomes the workforce.

LFG is the line between them.
