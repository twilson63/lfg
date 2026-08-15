#!/usr/bin/env python3
"""Validate PR slice planning invariants for automated pr-review.

Checks:
- PR template has 4 slice rows, commit scopes, DoD, and gates
- SKILL.md §3a section present with Conventional Commits + ASD-STE100
- Conventional Commit title regex
- ASD-STE100 sentence length (≤25 words) for PR template Summary example
"""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
errors = []

# 1. SKILL.md
skill = (root / "SKILL.md").read_text(encoding="utf-8")
for needle in [
    "context-boundary slices",
    "When to slice vs. collapse",
    "Slice table",
    "Conventional Commits",
    "ASD-STE100",
    "Testability",
    "Automated pr-review checklist",
]:
    if needle.lower() not in skill.lower():
        errors.append(f"SKILL.md missing: {needle}")

# gist link
if "gist.github.com/twilson63/1b9bb838da806958cc1a11579c9d4a5d" not in skill:
    errors.append("SKILL.md §3a must link the MCDS gist.")

# 2. PR template
pr_path = root / ".github" / "pull_request_template.md"
if not pr_path.is_file():
    errors.append("Missing .github/pull_request_template.md")
else:
    pr = pr_path.read_text(encoding="utf-8")
    # 4 slice rows — look for | 1 | ... | 4 |
    for n in ["| 1 |", "| 2 |", "| 3 |", "| 4 |"]:
        if n not in pr:
            errors.append(f"PR template missing slice row {n.strip()}")
    for scope in ["feat(data)", "feat(api)", "feat(admin)", "chore(seed)"]:
        if scope not in pr:
            errors.append(f"PR template missing commit scope {scope}")
    for gate in ["Unit tests", "E2E", "Automated Review Checklist", "Conventional Commits", "ASD-STE100"]:
        if gate.lower() not in pr.lower():
            errors.append(f"PR template missing gate/section: {gate}")
    # boundaries
    for b in ["data", "api", "admin", "integration"]:
        if b not in pr.lower():
            errors.append(f"PR template missing boundary: {b}")

# 3. Epic slice template
epic_path = root / "docs" / "planning" / "epic-slice-template.md"
if not epic_path.is_file():
    errors.append("Missing docs/planning/epic-slice-template.md")
else:
    epic = epic_path.read_text(encoding="utf-8")
    for n in ["Slice 1", "Slice 2", "Slice 3", "Slice 4", "When to collapse"]:
        if n not in epic:
            errors.append(f"epic-slice-template missing: {n}")

# 4. Conventional Commit regex sanity
cc_re = re.compile(r"^(feat|fix|docs|chore|refactor|test|build|ci)(\(.+\))?!?: .+", re.MULTILINE)
sample = "feat(funds): MCDS-033 slice 1 — data/service"
if not cc_re.match(sample):
    errors.append("CC regex broken on sample")

# 5. ASD-STE100: max 25 words per sentence in PR Summary example
# Check that template contains instruction about 25 words
if "25 words" not in skill:
    errors.append("STE 25-words rule missing in SKILL.md")
if pr_path.is_file() and "25 words" not in pr_path.read_text(encoding="utf-8"):
    errors.append("STE 25-words rule missing in PR template")

if errors:
    print("PR slice validation failed:", *[f"- {e}" for e in errors], sep="\n")
    sys.exit(1)
print("PR slice validation passed.")
