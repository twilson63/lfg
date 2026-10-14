"""Unit tests for the LFG skill — pure-logic checks + validator gates.

The slice-invariant string checks live in scripts/validate_pr_slices.py (the
no-dependency CI gate); this suite does NOT re-assert them. It owns:
- the pure-logic unit checks (Conventional Commit regex, ASD-STE100 word count)
- the "validators pass" gate (runs both no-dep validators as subprocesses)
"""
import re
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"

CC_RE = re.compile(r"^(feat|fix|docs|chore|refactor|test|build|ci)(\(.+\))?!?: .+")


def test_conventional_commit_regex():
    assert CC_RE.match("feat(funds): MCDS-033 slice 1 — data/service")
    assert CC_RE.match("feat(api): add transfer route")
    assert CC_RE.match("chore(seed): add 1147 seeds")
    assert CC_RE.match("fix(admin): correct permission gate")
    assert not CC_RE.match("bad commit message")
    assert not CC_RE.match("feat:")  # needs a description


def test_ste_sentence_length():
    """ASD-STE100: every example sentence must be <=25 words."""
    example = ("This PR adds the data slice. It creates the JournalEntry model. "
              "It validates funds in cents. It uses withTransaction. "
              "It writes audit entries.")
    for sent in [s.strip() for s in example.split(".") if s.strip()]:
        assert len(sent.split()) <= 25, f"STE example too long: {sent}"


def _run_validator(script):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script)],
                          capture_output=True, text=True)


def test_skill_validator_passes():
    r = _run_validator("validate_skill.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "passed" in r.stdout.lower()


def test_pr_slices_validator_passes():
    r = _run_validator("validate_pr_slices.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "passed" in r.stdout.lower()


# Exercise the real CI validator, not a duplicated implementation of its rules.
# These mutations reproduce deletions, altered limits, and weakened permissions
# seen in prose refactors. Intentional contract changes must update these cases.
@pytest.fixture
def contract_repo(tmp_path):
    copy = tmp_path / "lfg"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", ".git", ".pi-subagents"))
    return copy


def _validate_candidate(root, text):
    (root / "SKILL.md").write_text(text, encoding="utf-8")
    return subprocess.run([sys.executable, str(root / "scripts" / "validate_skill.py")],
                          capture_output=True, text=True)


@pytest.mark.parametrize("old,new,expected", [
    ("# LFG", "# LFG\u2014", "zero em dashes"),
    ("## Commit cadence", "## Commit notes", "required sections"),
    ("8. **Validate.**", "8. **Check.**", "nine ordered workflow steps"),
    ("Stop when the acceptance criteria are met or a blocker needs the user.",
     "Stop after three repair attempts.", "global three-repair"),
    ("Never fast-path past a missing, load-bearing artifact",
     "Skip a missing, load-bearing artifact", "load-bearing artifacts"),
    ("<=30 lines across <=3 files", "<=300 lines across <=3 files", "triage size limits"),
    ("privilege or process boundaries", "privilege boundaries", "process-boundary protection"),
    ("authentication, authorization", "auth, authorization", "authentication protection"),
    ("authentication, authorization", "authentication, permissions", "authorization protection"),
    ("8. **Validate.**", "9. **Validate.**", "nine ordered workflow steps"),
    ("privilege or process boundaries", "process boundaries", "privilege-boundary protection"),
    ("input validation", "input processing", "input validation protection"),
    ("path validation", "path handling", "path validation protection"),
    ("deserialization", "decoding", "deserialization protection"),
    ("subprocess or shell execution", "command handling", "shell execution protection"),
    ("secret handling", "configuration handling", "secret handling protection"),
    ("Implementation does not start until", "Implementation starts immediately", "plan before implementation"),
    ("review has no `fail` or unresolved `uncertain` findings", "review can have unresolved findings", "plan rejects unresolved findings"),
    ("advance only when everything passes", "advance before checks pass", "stepwise evidence gate"),
    ("Unmet required criteria, unresolved `uncertain` verdicts, or blocking rubric findings", "Only optional comments", "implementation rejects unresolved findings"),
    ("If the key is missing", "If the key is present", "missing-key fallback"),
    ("relative cross-links", "cross-links", "relative artifact links"),
    ("no external scripts, styles, or fetches", "external styles are allowed", "self-contained artifacts"),
    ("Never put secrets, keys, prompt contents, or raw command output",
     "Put secrets, keys, prompt contents, or raw command output", "artifact privacy"),
    ("same failure after three distinct replans of that step",
     "any failure after three attempts", "per-step failure escalation"),
    ("Don't commit while a step is `repairing`", "Commit while a step is `repairing`", "no mid-repair commits"),
    ("full suite runs at least once on the final step", "targeted checks are sufficient", "full-suite validation"),
    ("Never edit generated `build/`/`dist/` output", "Edit generated `build/`/`dist/` output", "generated-output protection"),
    ("unit plus E2E test gates", "unit test gates", "slice test gates"),
    ("title and body in Conventional Commit form", "free-form title and body", "slice commit convention"),
    ("Only commit if the user asked for commits, a branch, or a PR",
     "Commit whenever work is done", "commit authorization"),
    ("Never edits files or docs", "May edit files or docs", "read-only planner"),
    ("Never edits unless explicitly asked", "May edit at will", "reviewer edit authorization"),
    ("`uncertain` is never a pass", "`uncertain` counts as a pass", "uncertainty rule"),
    ("resolves each `uncertain` before the gate opens", "resolves uncertainty later", "uncertainty resolution"),
    ("score below 4 triggers a repair pass", "score below 2 triggers a repair pass", "taste repair threshold"),
    ("test for presence only", "print the key", "key presence only"),
    ("never print or store it", "print and store it", "key confidentiality"),
    ("project forbids sending content to external services", "project has other preferences", "no-egress fallback"),
    ("errors out or times out", "returns a response", "API failure fallback"),
    ("Never block on Jev", "Block on Jev", "optional judge fallback"),
    ("If a TypeSafe skill is installed, load it and follow the live docs",
     "Use only the embedded example", "installed TypeSafe instructions"),
    ("never upgrades a `fail`, overrides a failing command, or replaces a reviewer",
     "may upgrade a `fail` and override a failing command", "judge only tightens gates"),
    ("Any answer ≥ 0.3", "Any answer ≥ 0.9", "triage probability threshold"),
    ("A Noul below 0.7", "A Noul below 0.1", "plan probability threshold"),
    ("confidence ≥ 0.8", "confidence ≥ 0.2", "evidence confidence threshold"),
    ("Below 0.5 means replan", "Below 0.1 means replan", "repair probability threshold"),
    ("No secrets, user data, raw command output, or prompt contents",
     "Send the full prompt and command output", "judge state privacy"),
    ("**Repair gate**", "**Repair hint**", "missing Jev gate: Repair"),
])
def test_contract_rejects_regressions(contract_repo, old, new, expected):
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert old in text, f"Update this mutation for an intentional contract change: {old}"
    result = _validate_candidate(contract_repo, text.replace(old, new, 1))
    assert result.returncode == 1, result.stdout + result.stderr
    assert expected in result.stdout, result.stdout + result.stderr


def test_contract_rejects_truncated_tail(contract_repo):
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    result = _validate_candidate(contract_repo, text.split("Never edit generated", 1)[0])
    assert result.returncode == 1
    for expected in ("required sections", "commit authorization", "uncertainty rule",
                     "installed TypeSafe instructions", "missing Jev gate: Evidence"):
        assert expected in result.stdout, result.stdout


def test_contract_checks_rules_in_their_owning_section(contract_repo):
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    text = text.replace("privilege or process boundaries", "privilege boundaries", 1)
    # Mentioning a rule elsewhere must not mask its deletion from triage.
    result = _validate_candidate(contract_repo, text + "\nprocess boundaries\n")
    assert result.returncode == 1
    assert "process-boundary protection" in result.stdout


def test_jev_api_example_preserved():
    """Pin the published 2.4.0 example, not prose or version metadata.

    An intentional API example change needs its own compatibility review and
    an updated digest. The tone-only rewrite must preserve it byte-for-byte.
    """
    text = SKILL.read_text(encoding="utf-8")
    blocks = re.findall(r"^```[^\n]*\n.*?^```", text, re.MULTILINE | re.DOTALL)
    example = [block for block in blocks if "api.typesafe.ai/v1/systemone" in block]
    assert len(example) == 1
    assert hashlib.sha256(example[0].encode()).hexdigest() == (
        "1f4ebeb63bd7ac7726e6d53085c291893b6300cb7514275699a8b60e021e7861")
