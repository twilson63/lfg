# Contributing to LFG

## Scope

LFG is a procedural skill, not an agent runtime. Contributions should make its planning, evidence, validation, repair, or review behavior clearer and more portable.

## Before opening a pull request

1. Keep the canonical skill in the root [`SKILL.md`](./SKILL.md). This repository intentionally exposes one skill.
2. Preserve YAML frontmatter with a stable `name` and a concise `description`.
3. Make instructions actionable. Name expected evidence, fallback behavior, and stopping conditions.
4. Do not add credentials, private keys, personal data, raw browser DOM, or tool output that could contain secrets.
5. Run `python3 scripts/validate_skill.py`.

## Style

- Prefer direct language and short, observable requirements.
- Do not promise that every tool, subagent, or checkpointing mechanism exists; describe a fallback.
- Keep examples generic and safe to copy into any repository.
- Update the version in `SKILL.md` when behavior changes materially.

## Pull requests

Explain the user problem, the changed behavior, validation evidence, and compatibility impact. Small focused pull requests are easier to review.
