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

For broad, ambiguous, design-sensitive, or security-sensitive work, the skill requires:

1. Research of the existing project and constraints.
2. A project-specific definition of the problem.
3. An HTML PRD and progress log with step-level acceptance criteria.
4. A plan review before implementation when subagents are available.
5. Focused implementation loops with evidence and replanning on failure.
6. An implementation review against the plan and validation output.

Small, obvious, low-risk changes can use its documented fast path.

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
```

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
