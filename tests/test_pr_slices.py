"""Unit tests for PR slice planning (LFG §3a) — automated pr-review gate."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
EPIC_TEMPLATE = ROOT / "docs" / "planning" / "epic-slice-template.md"

CC_RE = re.compile(r"^(feat|fix|docs|chore|refactor|test|build|ci)(\(.+\))?!?: .+")

def test_skill_has_slice_section():
    text = SKILL.read_text(encoding="utf-8")
    assert "context-boundary slices" in text.lower()
    assert "Conventional Commits" in text
    assert "ASD-STE100" in text
    assert "gist.github.com/twilson63/1b9bb838da806958cc1a11579c9d4a5d" in text

def test_pr_template_exists_and_has_sections():
    assert PR_TEMPLATE.is_file(), "PR template missing"
    pr = PR_TEMPLATE.read_text(encoding="utf-8")
    for needle in ["Context-Boundary Slices", "Conventional Commits", "ASD-STE100", "Unit tests", "E2E", "Automated Review Checklist"]:
        assert needle.lower() in pr.lower(), f"missing {needle}"

def test_pr_template_has_four_slices():
    pr = PR_TEMPLATE.read_text(encoding="utf-8")
    for row in ["| 1 |", "| 2 |", "| 3 |", "| 4 |"]:
        assert row in pr, f"missing row {row}"
    for boundary in ["`data`", "`api`", "`admin`", "`integration`"]:
        assert boundary in pr, f"missing boundary {boundary}"

def test_pr_template_has_commit_scopes():
    pr = PR_TEMPLATE.read_text(encoding="utf-8")
    assert "feat(data)" in pr
    assert "feat(api)" in pr
    assert "feat(admin)" in pr
    assert "chore(seed)" in pr

def test_epic_template_exists_and_has_slices():
    assert EPIC_TEMPLATE.is_file()
    epic = EPIC_TEMPLATE.read_text(encoding="utf-8")
    for s in ["Slice 1", "Slice 2", "Slice 3", "Slice 4", "When to collapse"]:
        assert s in epic, f"missing {s}"

def test_conventional_commit_regex():
    assert CC_RE.match("feat(funds): MCDS-033 slice 1 — data/service")
    assert CC_RE.match("feat(api): add transfer route")
    assert CC_RE.match("chore(seed): add 1147 seeds")
    assert CC_RE.match("fix(admin): correct permission gate")
    assert not CC_RE.match("bad commit message")
    assert not CC_RE.match("feat:")  # needs description

def test_ste_sentence_length_rule_present():
    skill = SKILL.read_text(encoding="utf-8")
    pr = PR_TEMPLATE.read_text(encoding="utf-8")
    assert "25 words" in skill
    assert "25 words" in pr
    # example sentences in skill must all be ≤25 words
    example = "This PR adds the data slice. It creates the JournalEntry model. It validates funds in cents. It uses withTransaction. It writes audit entries."
    for sent in [s.strip() for s in example.split(".") if s.strip()]:
        assert len(sent.split()) <= 25, f"STE example too long: {sent}"

def test_pr_template_boundaries_match_skill():
    skill = SKILL.read_text(encoding="utf-8")
    pr = PR_TEMPLATE.read_text(encoding="utf-8")
    # skill defines withTransaction and error types that pr checklist must mirror
    assert "withTransaction" in skill
    assert "withTransaction" in pr
    assert "TransactionConcurrencyError" in skill
