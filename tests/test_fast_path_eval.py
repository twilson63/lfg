"""Offline tests of corpus coverage, request privacy and evaluation scoring.

These tests do not execute coding agents or claim the skill improves tasks.
"""
import importlib.util
import json
from pathlib import Path
import urllib.error

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("evaluate_triage", ROOT / "scripts/evaluate_triage.py")
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


@pytest.fixture
def cases():
    return evaluation.load_cases(ROOT / "tests/fixtures/fast_path_cases.json")


def response_for(cases):
    return {"model": "offline-test-double", "answers": {
        f"{policy}_{case['id']}": {"type": "choice", "choice": case["expected"], "confidence": 0.95}
        for policy in ("baseline", "candidate") for case in cases
    }}


def test_corpus_covers_categories_and_dynamic_escalations(cases):
    assert len(cases) == 11
    assert {case["category"] for case in cases} == evaluation.CATEGORIES
    by_id = {case["id"]: case for case in cases}
    for name in ("tiny_security", "tiny_contract", "ambiguous", "discovered_scope", "unresolved_check", "missing_artifact"):
        assert by_id[name]["expected"] == "full_loop"
    assert by_id["specified_copy"]["expected"] == "fast_path"
    assert len(by_id["local_multi_file"]["scenario"]["files"]) > 3


def test_request_withholds_expected_labels(cases):
    payload = evaluation.build_request(cases, "candidate policy", "candidate")
    assert payload["state"]["cases"] == [case["scenario"] for case in cases]
    assert all("expected" not in case and "baseline_expected" not in case
               for case in payload["state"]["cases"])
    assert "baseline_expected" not in json.dumps(payload)
    assert len(payload["questions"]) == len(cases)
    for i, case in enumerate(cases):
        assert f"`cases[{i}]`" in payload["questions"][f"candidate_{case['id']}"]["instructions"]


def test_policy_excerpt_excludes_rubric_and_api_example():
    excerpt = evaluation.policy_excerpt((ROOT / "SKILL.md").read_text())
    assert "### Evaluation rubric" not in excerpt
    assert "api.typesafe.ai" not in excerpt
    assert "## Optional: Jev judge gates" not in excerpt
    assert "## Project artifacts bootstrap" in excerpt
    with pytest.raises(ValueError):
        evaluation.policy_excerpt("# Truncated skill")


def test_scorer_passes_correct_mock_not_real_behavior(cases):
    report = evaluation.score_response(cases, response_for(cases))
    assert report["candidate_pass"]
    assert report["results"]["candidate"]["correct"] == len(cases)
    assert "no task implementation" in report["scope"]


def test_missed_escalation_and_unnecessary_full_loop_are_separate(cases):
    response = response_for(cases)
    response["answers"]["candidate_tiny_security"]["choice"] = "fast_path"
    response["answers"]["candidate_specified_copy"]["choice"] = "full_loop"
    report = evaluation.score_response(cases, response)
    assert not report["candidate_pass"]
    assert report["results"]["candidate"]["missed_escalations"] == 1
    assert report["results"]["candidate"]["unnecessary_full_loop"] == 1


def test_uncertain_is_not_pass(cases):
    response = response_for(cases)
    response["answers"]["candidate_bug"]["confidence"] = 0.79
    report = evaluation.score_response(cases, response)
    assert not report["candidate_pass"]
    assert report["results"]["candidate"]["uncertain"] == 1
    response["answers"]["candidate_bug"]["confidence"] = 0.8
    assert evaluation.score_response(cases, response)["candidate_pass"]


@pytest.mark.parametrize("confidence", [True, None, "0.9", -0.1, 1.1, float("nan"), float("inf")])
def test_invalid_confidence_rejected(cases, confidence):
    response = response_for(cases)
    response["answers"]["candidate_bug"]["confidence"] = confidence
    with pytest.raises(ValueError):
        evaluation.score_response(cases, response)


def test_incomplete_response_is_not_a_pass(cases):
    response = response_for(cases)
    del response["answers"]["candidate_bug"]
    with pytest.raises(KeyError):
        evaluation.score_response(cases, response)


def test_default_cli_never_calls_api(monkeypatch, capsys):
    def forbidden(*args):
        pytest.fail("Default fixture checks must not call a remote model")
    monkeypatch.setattr(evaluation, "call_api", forbidden)
    assert evaluation.main([]) == 0
    assert "NOT RUN" in capsys.readouterr().out


def test_missing_key_is_not_success(monkeypatch, capsys):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    assert evaluation.main(["--live"]) == 2
    assert "NOT RUN" in capsys.readouterr().err


def test_api_error_redacts_body_and_key(monkeypatch, capsys):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-secret-do-not-print")
    monkeypatch.setattr(evaluation.subprocess, "check_output", lambda *a, **k: (ROOT / "SKILL.md").read_text())
    def fail(*args):
        raise urllib.error.HTTPError("https://example.invalid", 401, "test-secret-do-not-print", {}, None)
    monkeypatch.setattr(evaluation, "call_api", fail)
    assert evaluation.main(["--live"]) == 2
    output = capsys.readouterr()
    assert "HTTP 401" in output.err
    assert "test-secret-do-not-print" not in output.err + output.out


def test_duplicate_case_ids_rejected(cases, tmp_path):
    cases[1]["id"] = cases[0]["id"]
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(cases))
    with pytest.raises(ValueError):
        evaluation.load_cases(path)


def test_requests_do_not_mix_baseline_and_candidate_policy(cases):
    baseline = evaluation.build_request(cases, "old numeric policy", "baseline")
    candidate = evaluation.build_request(cases, "new risk policy", "candidate")
    assert "new risk policy" not in json.dumps(baseline)
    assert "old numeric policy" not in json.dumps(candidate)
    assert "file count alone" not in json.dumps(baseline)
    with pytest.raises(ValueError):
        evaluation.build_request(cases, "policy", "unknown")


def test_live_main_pins_model_and_writes_only_summary(monkeypatch, capsys, tmp_path, cases):
    monkeypatch.setenv("TYPESAFE_API_KEY", "private-test-token")
    monkeypatch.setattr(evaluation.subprocess, "check_output", lambda *a, **k: (ROOT / "SKILL.md").read_text())
    requests = []
    def fake_api(payload, key):
        assert key == "private-test-token"
        assert key not in json.dumps(payload)
        requests.append(payload)
        return {"model": "pinned-model", "answers": {
            qid: {"type": "choice", "choice": case["expected"], "confidence": 0.95}
            for qid, case in zip(payload["questions"], cases)
        }}
    monkeypatch.setattr(evaluation, "call_api", fake_api)
    output = tmp_path / "report.json"
    assert evaluation.main(["--live", "--output", str(output)]) == 0
    assert len(requests) == 2
    assert requests[0]["model"] == "jev-latest"
    assert requests[1]["model"] == "pinned-model"
    report = json.loads(output.read_text())
    assert report["candidate_pass"] and report["request_count"] == 2
    assert report["policy_sha256"]["candidate"]
    assert report["evaluated_at"]
    assert "private-test-token" not in output.read_text() + capsys.readouterr().out


def test_model_mismatch_is_incomplete(monkeypatch, cases, capsys):
    monkeypatch.setenv("TYPESAFE_API_KEY", "private-test-token")
    monkeypatch.setattr(evaluation.subprocess, "check_output", lambda *a, **k: (ROOT / "SKILL.md").read_text())
    models = iter(["first-model", "different-model"])
    monkeypatch.setattr(evaluation, "call_api", lambda *a: {"model": next(models), "answers": {}})
    assert evaluation.main(["--live"]) == 2
    assert "incomplete" in capsys.readouterr().err
