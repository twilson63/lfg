"""Unit tests for the LFG skill — pure-logic checks + validator gates.

The slice-invariant string checks live in scripts/validate_pr_slices.py (the
no-dependency CI gate); this suite does NOT re-assert them. It owns:
- the pure-logic unit checks (Conventional Commit regex, ASD-STE100 word count)
- the "validators pass" gate (runs both no-dep validators as subprocesses)
"""
import re
import subprocess
import sys
from pathlib import Path

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
