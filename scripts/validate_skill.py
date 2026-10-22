#!/usr/bin/env python3
"""Validate the portable, dependency-free invariants of the LFG skill."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
skill = root / "SKILL.md"
text = skill.read_text(encoding="utf-8")
errors = []

# This is a procedural contract, not a claim that static checks prove model
# behavior. Keep safety and gate rules in their owning sections, so a keyword
# elsewhere cannot conceal an accidentally truncated or weakened instruction.
def validate_contract(text):
    errors = []
    if "\u2014" in text:
        errors.append("SKILL.md must contain zero em dashes.")
    headings = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
    sections = {
        match.group(1): text[match.end():headings[i + 1].start() if i + 1 < len(headings) else len(text)]
        for i, match in enumerate(headings)
    }
    expected = [
        "Project artifacts bootstrap", "Triage first", "Artifacts", "Workflow",
        "Multi-layer work: slice PRs by boundary", "Commit cadence",
        "Subagent roles", "Optional: Jev judge gates",
    ]
    if [match.group(1) for match in headings] != expected:
        errors.append("SKILL.md must preserve all required sections in workflow order.")
    steps = re.findall(r"^(\d+)\. \*\*([^*]+)\*\*", sections.get("Workflow", ""), re.MULTILINE)
    labels = [label for _, label in steps]
    if [number for number, _ in steps] != [str(n) for n in range(1, 10)] or labels != [
        "Inspect.", "Define.", "Plan.", "Plan gate.", "Implement stepwise.",
        "Repair boundedly.", "Implementation gate.", "Validate.", "Report.",
    ]:
        errors.append("SKILL.md must preserve the nine ordered workflow steps.")
    # Do not turn the per-step, same-failure escalation into a global budget.
    if re.search(r"(?:burned|after|exhausted)\s+(?:three|3)\s+repair attempts", text, re.IGNORECASE):
        errors.append("SKILL.md must not impose a global three-repair stopping rule.")
    rules = [
        ("load-bearing artifacts before fast path", "Project artifacts bootstrap", r"never fast-path past a missing, load-bearing artifact"),
        ("risk-based triage", "Triage first", r"do not decide based on line or file count alone"),
        ("all-of eligibility", "Triage first", r"only when ALL of these are true"),
        ("clear checkable outcome", "Triage first", r"clear and checkable without substantial discovery"),
        ("localized reversible scope", "Triage first", r"localized and reasonably reversible"),
        ("shared-contract protection", "Triage first", r"does not alter architecture, shared contracts, or behavior across unrelated areas"),
        ("concrete acceptance check", "Triage first", r"concrete acceptance check"),
        ("specified UI/copy eligibility", "Triage first", r"specified, contained UI or copy change can qualify"),
        ("multi-file eligibility", "Triage first", r"several files do not disqualify a change"),
        ("fast-path validation scope", "Triage first", r"full-suite rule in Workflow step 8 still applies to fast path"),
        ("fast-path honest evidence", "Triage first", r"never claim an unrun or failing check passed"),
        ("fast-path escalation", "Triage first", r"switch to the full loop if discovery reveals broader impact"),
        ("unresolved-check escalation", "Triage first", r"escalate when they remain unresolved or reveal broader impact"),
        ("fast-path safety metrics", "Triage first", r"quality failures, missed escalations, unnecessary full-loop use"),
        ("evaluation evidence limits", "Triage first", r"neither proves completed-task quality or speed"),
        ("slice-count alignment", "Multi-layer work: slice PRs by boundary", r"file count alone does not require slices"),
        ("Jev copy alignment", "Optional: Jev judge gates", r"specified, contained UI or copy change with a concrete check is not an unresolved design decision"),
        ("Jev shared-contract check", "Optional: Jev judge gates", r"one for architecture/shared-contract or unrelated-area impact"),
        ("process-boundary protection", "Triage first", r"process boundaries"),
        ("authentication protection", "Triage first", r"authentication"),
        ("authorization protection", "Triage first", r"authorization"),
        ("privilege-boundary protection", "Triage first", r"privilege"),
        ("input validation protection", "Triage first", r"input validation"),
        ("path validation protection", "Triage first", r"path validation"),
        ("deserialization protection", "Triage first", r"deserialization"),
        ("shell execution protection", "Triage first", r"subprocess or shell execution"),
        ("secret handling protection", "Triage first", r"secret handling"),
        ("plan before implementation", "Workflow", r"implementation does not start until"),
        ("plan rejects unresolved findings", "Workflow", r"review has no `fail` or unresolved `uncertain` findings"),
        ("stepwise evidence gate", "Workflow", r"advance only when everything passes"),
        ("implementation rejects unresolved findings", "Workflow", r"unmet required criteria, unresolved `uncertain` verdicts, or blocking rubric findings"),
        ("relative artifact links", "Artifacts", r"relative cross-links"),
        ("self-contained artifacts", "Artifacts", r"no external scripts, styles, or fetches"),
        ("artifact privacy", "Artifacts", r"never (?:put|store) secrets, keys, prompt contents, or raw command output"),
        ("per-step failure escalation", "Workflow", r"same failure after (?:three|3) distinct replans of that step"),
        ("no mid-repair commits", "Workflow", r"(?:don't|never) commit while a step is `repairing`"),
        ("full-suite validation", "Workflow", r"full suite runs at least once on the final step"),
        ("generated-output protection", "Workflow", r"(?:never|do not) edit generated `build/`/`dist/` output"),
        ("slice test gates", "Multi-layer work: slice PRs by boundary", r"unit (?:plus|\+) E2E test gates"),
        ("slice commit convention", "Multi-layer work: slice PRs by boundary", r"title and body in conventional commit form"),
        ("commit authorization", "Commit cadence", r"(?:only commit|commit only) if the user asked for commits, a branch, or a PR"),
        ("read-only planner", "Subagent roles", r"never edits files or docs"),
        ("reviewer edit authorization", "Subagent roles", r"never edits unless explicitly asked"),
        ("uncertainty rule", "Subagent roles", r"`uncertain` is never a pass"),
        ("uncertainty resolution", "Subagent roles", r"resolves each `uncertain` before the gate opens"),
        ("taste repair threshold", "Subagent roles", r"score below 4 triggers a repair pass"),
        ("key presence only", "Optional: Jev judge gates", r"test for presence only"),
        ("key confidentiality", "Optional: Jev judge gates", r"never print or store it"),
        ("no-egress fallback", "Optional: Jev judge gates", r"project forbids sending content to external services"),
        ("missing-key fallback", "Optional: Jev judge gates", r"if the key is (?:missing|absent),.*?skip Jev"),
        ("API failure fallback", "Optional: Jev judge gates", r"errors(?: out)? or times out"),
        ("optional judge fallback", "Optional: Jev judge gates", r"never block on Jev"),
        ("installed TypeSafe instructions", "Optional: Jev judge gates", r"if a TypeSafe skill is installed, load it and follow the live docs"),
        ("judge only tightens gates", "Optional: Jev judge gates", r"never upgrades a `fail`, overrides a failing command, or replaces a reviewer"),
        ("triage probability threshold", "Optional: Jev judge gates", r"any answer ≥ 0\.3"),
        ("plan probability threshold", "Optional: Jev judge gates", r"Noul (?:<|below)\s*0\.7"),
        ("evidence confidence threshold", "Optional: Jev judge gates", r"confidence ≥ 0\.8"),
        ("repair probability threshold", "Optional: Jev judge gates", r"(?:<|below)\s*0\.5"),
        ("judge state privacy", "Optional: Jev judge gates", r"no secrets, user data, raw command output, or prompt contents"),
    ]
    for label, heading, pattern in rules:
        if not re.search(pattern, sections.get(heading, ""), re.IGNORECASE):
            errors.append(f"SKILL.md missing contract rule: {label}.")
    triage = sections.get("Triage first", "")
    subsections = re.split(r"^### ", triage, flags=re.MULTILINE)
    sub = {part.split("\n", 1)[0]: part.partition("\n")[2] for part in subsections[1:]}
    if list(sub) != ["Fast-path eligibility", "Fast-path procedure", "Escalation", "Evaluation rubric"]:
        errors.append("SKILL.md missing ordered fast-path subsections.")
    procedure = sub.get("Fast-path procedure", "")
    if re.findall(r"^(\d+)\. ", procedure, re.MULTILINE) != list("123456"):
        errors.append("SKILL.md must preserve the six ordered fast-path actions.")
    for label, pattern in [
        ("intent before edits", r"1\. State the intended change.*before implementation"),
        ("acceptance before edits", r"2\. Name the acceptance check.*before implementation"),
        ("minimal coherent change", r"3\. Make the smallest coherent change"),
        ("run relevant checks", r"4\. Run the relevant focused test or check"),
        ("diff self-review", r"5\. Review the diff.*no unrelated changes"),
        ("actual outcome report", r"6\. Report.*actual results, and anything not checked"),
    ]:
        if not re.search(pattern, procedure):
            errors.append(f"SKILL.md missing fast-path action: {label}.")
    rubric = sub.get("Evaluation rubric", "")
    for category in ["bug fix", "test-only", "documentation-only", "UI or copy", "multi-file",
                     "security, trust-boundary, or shared-contract", "unresolved failed checks"]:
        if category not in rubric:
            errors.append(f"SKILL.md missing evaluation category: {category}.")
    for name in ("Triage", "Plan", "Evidence", "Repair"):
        if f"**{name} gate**" not in sections.get("Optional: Jev judge gates", ""):
            errors.append(f"SKILL.md missing Jev gate: {name}.")
    return errors

errors.extend(validate_contract(text))

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

# LFG 2.0.0: the skill teaches the boundary-slicing concept and Conventional
# Commits; project-specific conventions (STE, slice tables, gist templates)
# are delegated to project AGENTS.md and PR templates, which are checked here.
if "boundary slices" not in text.lower() or "conventional commit" not in text.lower():
    errors.append("SKILL.md slice section must teach boundary slices and Conventional Commits.")

if not (root / "docs" / "planning" / "epic-slice-template.md").is_file():
    errors.append("Missing required slice template: docs/planning/epic-slice-template.md.")

# HTML coordination features (LFG Artifacts section) — promised in SKILL.md
for needle in ("created", "last updated", "ISO 8601", "cross-link", "file://"):
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
    # The force-directed <canvas> diagram is optional (see SKILL.md Artifacts).
    # If an artifact includes one, it must be a real animated diagram, not a stub.
    if "<canvas" in html and "requestAnimationFrame" not in html:
        errors.append(f"{artifact} has a <canvas> but no animation loop.")
    # self-contained: no external scripts / stylesheets / remote fetches
    if _re.search(r"<script[^>]+src=|<link[^>]+href=|https?://[^\"'\s]+\.js", html):
        errors.append(f"{artifact} must be self-contained (no external scripts/remote fetches).")

if errors:
    print("LFG skill validation failed:", *[f"- {error}" for error in errors], sep="\n")
    sys.exit(1)
print("LFG skill validation passed.")
