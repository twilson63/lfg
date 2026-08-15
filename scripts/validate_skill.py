#!/usr/bin/env python3
"""Validate the portable, dependency-free invariants of the LFG skill."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
skill = root / "SKILL.md"
text = skill.read_text(encoding="utf-8")
errors = []

if not text.startswith("---\n"):
    errors.append("SKILL.md must start with YAML frontmatter.")
else:
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        errors.append("SKILL.md frontmatter is not closed.")
    else:
        frontmatter = match.group(1)
        required = {
            "name": r"^name:\s*lfg\s*$",
            "version": r'^version:\s*["\']?\d+\.\d+\.\d+["\']?\s*$',
            "description": r"^description:\s*.+$",
        }
        for label, pattern in required.items():
            if not re.search(pattern, frontmatter, re.MULTILINE):
                errors.append(f"Missing or invalid frontmatter field: {label}.")
        if len(re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE).group(1)) > 220:
            errors.append("Description must be 220 characters or fewer.")

for path in ("README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", ".gitignore"):
    if not (root / path).is_file():
        errors.append(f"Missing required repository file: {path}.")

if (root / ".zenbin").exists() and ".zenbin/" not in (root / ".gitignore").read_text(encoding="utf-8"):
    errors.append(".zenbin/ must be ignored.")

# PR slice planning invariants (LFG §3a) — required template and skill section
pr_template = root / ".github" / "pull_request_template.md"
if not pr_template.is_file():
    errors.append("Missing required PR template: .github/pull_request_template.md (LFG §3a).")
else:
    pr_text = pr_template.read_text(encoding="utf-8")
    for needle in (
        "Context-Boundary Slices",
        "Conventional Commits",
        "ASD-STE100",
        "Unit tests",
        "E2E",
        "Automated Review Checklist",
    ):
        if needle.lower() not in pr_text.lower():
            errors.append(f"PR template missing required section: {needle}.")

if "context-boundary slices" not in text.lower():
    errors.append("SKILL.md missing required section: context-boundary slices (LFG §3a).")
if "Conventional Commits" not in text or "ASD-STE100" not in text:
    errors.append("SKILL.md PR slice section must mention Conventional Commits and ASD-STE100.")

if not (root / "docs" / "planning" / "epic-slice-template.md").is_file():
    errors.append("Missing required slice template: docs/planning/epic-slice-template.md.")

# HTML coordination features (LFG File coordination) — required in SKILL.md
for needle in ("date/time", "cross-link", "force-directed", "flow diagram", "inline JavaScript"):
    if needle.lower() not in text.lower():
        errors.append(f"SKILL.md missing HTML coordination feature: {needle}.")

# HTML coordination features (LFG File coordination) — the example artifacts must
# actually implement them, not just be described in SKILL.md. This is the real
# regression guard: a future agent that drops a feature from a generated doc
# will fail here, not just when the requirement is deleted from the skill.
import re as _re
for artifact in ("lfg-skill-repo-prd.html", "lfg-skill-repo-progress.html"):
    path = root / "docs" / "development" / artifact
    if not path.is_file():
        errors.append(f"Missing example artifact: {artifact}.")
        continue
    html = path.read_text(encoding="utf-8")
    if not _re.search(r"Last updated:\s*<code>\d{4}-\d{2}-\d{2}", html):
        errors.append(f"{artifact} missing ISO 8601 'last updated' timestamp.")
    if "Last updated" not in html and "created" not in html.lower():
        errors.append(f"{artifact} missing date/time header.")
    if "href=\"./" not in html:
        errors.append(f"{artifact} missing relative cross-links.")
    if "<canvas" not in html or "requestAnimationFrame" not in html:
        errors.append(f"{artifact} missing force-directed <canvas> flow diagram.")
    # self-contained: no external scripts / stylesheets / remote fetches
    if _re.search(r"<script[^>]+src=|<link[^>]+href=|https?://[^\"'\s]+\.js", html):
        errors.append(f"{artifact} must be self-contained (no external scripts/remote fetches).")

if errors:
    print("LFG skill validation failed:", *[f"- {error}" for error in errors], sep="\n")
    sys.exit(1)
print("LFG skill validation passed.")
