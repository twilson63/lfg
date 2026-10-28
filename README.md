# LFG

[![skills.sh](https://skills.sh/b/twilson63/lfg)](https://skills.sh/twilson63/lfg)

A disciplined workflow skill for coding agents: **research → define → plan → implement → validate → review → repair → report**.

LFG makes complex work inspectable. It asks the agent to put the plan, acceptance criteria, evidence, and review findings in project files rather than leaving the important decisions in chat history.

## Install

```bash
npx skills add twilson63/lfg
```

Choose `lfg` if the installer detects multiple skills. The repository deliberately keeps one canonical skill at the root: [`SKILL.md`](./SKILL.md).

The Skills CLI installs to the agent/tooling locations it detects. For a manual install, copy this repository's `SKILL.md` to the directory your agent uses for skills (for example, `.claude/skills/lfg/SKILL.md` or `~/.pi/agent/skills/lfg/SKILL.md`).

## Use it

Ask your agent to use LFG, or start a task with one of these prompts:

```text
lfg: add role-based access control to this API
lets-fucking-go: plan and ship the database migration safely
Use the LFG workflow to review and harden this authentication change.
```

Before task research or planning, LFG verifies `docs/architecture.md`, `docs/features-map.md`, and `docs/design.md`, or explicitly mapped equivalents. All three must contain readable, project-specific content. Missing or inadequate artifacts must be bootstrapped first using limited repository inspection and clarification. If required information cannot be verified, LFG reports a blocker instead of continuing. This pre-check also applies to fast-path work.

For broad, ambiguous, design-sensitive, or security-sensitive work, the skill requires:

1. Research of the existing project and constraints.
2. A project-specific definition of the problem before any code.
3. An HTML PRD and progress log with step-level acceptance criteria and required evidence.
4. A plan review before implementation — subagent when available, manual otherwise.
5. Focused implementation loops with evidence per criterion and bounded repair: diagnose, replan, then retry.
6. An implementation review against the plan and validation output.
7. A handoff file with milestone checkpoints, so work survives compaction, re-entry, or a new session.
8. Boundary-sliced PRs for multi-layer epics crossing two or more context boundaries, each slice with its own definition of done and test gates. File count alone does not force slicing.

Clear, localized, reversible, low-risk changes can use its documented fast path, including specified UI/copy edits and multi-file changes. Security boundaries, shared-contract changes, unresolved design decisions, and missing load-bearing project artifacts still require the full loop. See the [fast-path evaluation protocol](docs/evaluation/fast-path.md) for the rubric and the limits of routing-only checks.

## Versioning

`SKILL.md` follows semver. The current version is **2.6.0**, which adds a mandatory architecture, feature-map, and design pre-check before task research or planning, with explicit evidence and blocking behavior. v2.5.0 replaces line/file limits with risk-based fast-path eligibility, an explicit acceptance/check/review procedure, escalation rules, and a task-evaluation rubric. It preserves v2.4.0 project-artifact bootstrap and reconciles Jev triage and PR slicing with the new eligibility. v2.3.0 added optional [Jev](https://docs.typesafe.ai) judge gates — an independent, calibrated second opinion at the triage, plan, evidence, and repair gates, used only when `TYPESAFE_API_KEY` is present and never able to loosen a gate. It also closes a gap in the reviewer gates: an `uncertain` verdict is never a pass and must be resolved or escalated before a gate opens. v2.2.0 added the full-suite validation rule. v2.1.0 keeps the skill portable: it replaces project-specific security examples with general trust-boundary categories, makes commits conditional on the user asking for them, and treats the force-directed flow diagram as optional. Compared with 1.x, v2.0.0 compresses the skill for models that follow complex instructions well, moves project-specific conventions (slice tables, PR checklists, STE rules) into project AGENTS.md and PR templates, replaces harness-specific checkpointing with the portable handoff file, and re-scopes the repository validators to assert only portable invariants.

## What it does not do

- It does not replace engineering judgment, tests, or code review.
- It does not authorize risky actions or bypass approval gates.
- It does not guarantee a particular agent's tool availability.
- It does not promise that a task will finish without user input when requirements or permissions are genuinely blocked.

## skills.sh discovery

This is a public GitHub skill repository with a root `SKILL.md`, the layout recognized by the [Skills CLI](https://skills.sh/docs/cli). The CLI command above is the canonical install path.

skills.sh does **not** use a manual “submit this repo” listing flow. Its [FAQ](https://skills.sh/docs/faq) says skills appear on the leaderboard automatically through anonymous telemetry when users run `npx skills add <owner/repo>`. The badge will become useful once installation activity is recorded; publication alone does not guarantee immediate visibility or a ranking.

## Reference material

The original deep dives and v3 extraction are preserved under [`docs/reference/`](./docs/reference/). They are background reading; the installable contract is the root [`SKILL.md`](./SKILL.md).

## Development

Validate the frontmatter and repository invariants without dependencies:

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_pr_slices.py
```

Run the test suites (requires [pytest](https://pytest.org)):

```bash
python3 -m pip install pytest
python3 -m pytest --strict-markers -q

# Exact CI selections:
python3 -m pytest --strict-markers -q -m "not e2e"
python3 -m pytest tests/test_e2e_pr_slices.py -q -m e2e
```

CI runs both validators, all unit/contract tests, and the e2e smoke suite on every pull request and push to `main` (see `.github/workflows/validate.yml`).

To test CLI discovery from a clean temporary directory after the repository is public:

```bash
mkdir /tmp/lfg-smoke && cd /tmp/lfg-smoke
npx skills add twilson63/lfg --list
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Please keep the skill portable: name real capabilities with fallbacks, do not assume one proprietary agent runtime, and never add secrets or credentials to examples.

## Security

Report potential security issues privately as described in [SECURITY.md](./SECURITY.md). Do not open a public issue for a vulnerability that could put users, credentials, or repositories at risk.

## License

[MIT](./LICENSE)
