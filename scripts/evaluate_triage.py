#!/usr/bin/env python3
"""Opt-in live semantic routing comparison, not completed-task or speed proof.

Only public policy excerpts and synthetic scenarios go to TypeSafe. Expected
labels are withheld from the request. Normal CI validates fixtures and tests the
scorer offline; it never needs a key or a network call. No agent edits code here.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "bug", "test-only", "documentation-only", "localized-ui-copy",
    "localized-multi-file", "tiny-security-shared-boundary", "escalation",
}
ROUTES = {"fast_path", "full_loop"}


def load_cases(path):
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not cases or len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Cases need unique IDs and must not be empty")
    if {case["category"] for case in cases} != CATEGORIES:
        raise ValueError("Cases must cover all seven rubric categories")
    for case in cases:
        if case["expected"] not in ROUTES or case["baseline_expected"] not in ROUTES:
            raise ValueError("Unknown expected route")
        if not case["scenario"].get("summary"):
            raise ValueError("Each case needs a synthetic scenario")
    return cases


def policy_excerpt(text):
    """Exclude unrelated prose, credentials and the API example."""
    headings = list(re.finditer(r"^## (.+)$", text, re.MULTILINE))
    wanted = {"Project artifacts bootstrap", "Triage first",
              "Multi-layer work: slice PRs by boundary"}
    selected = []
    for i, match in enumerate(headings):
        if match.group(1) in wanted:
            end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
            section = text[match.start():end]
            # Evaluation guidance is not routing policy and can bias the test.
            section = section.split("### Evaluation rubric", 1)[0]
            selected.append(section)
    if len(selected) != len(wanted):
        raise ValueError("Policy is missing a required routing section")
    return "\n".join(selected)


def build_request(cases, policy_text, label):
    if label not in {"baseline", "candidate"}:
        raise ValueError("Unknown policy label")
    questions = {}
    for i, case in enumerate(cases):
        questions[f"{label}_{case['id']}"] = {
            "type": "choice",
            "instructions": (
                f"Under `policy`, which workflow is required for `cases[{i}]` "
                "at its stated stage? Apply every eligibility, bootstrap, and "
                "escalation constraint, including any explicit limits. "
                "Do not assume missing acceptance evidence."
            ),
            "criteria": {
                "fast_path": "Every fast-path condition is met; a shorter workflow is allowed.",
                "full_loop": "A required condition fails, risk is uncertain, or escalation/bootstrap is needed.",
            },
        }
    return {"model": "jev-latest", "state": {
        "policy": policy_text,
        "cases": [case["scenario"] for case in cases],
    }, "questions": questions}


def score_response(cases, response, threshold=0.8):
    if not response.get("model"):
        raise ValueError("Response must identify the actual model")
    results = {}
    for policy in ("baseline", "candidate"):
        rows = []
        for case in cases:
            qid = f"{policy}_{case['id']}"
            answer = response["answers"][qid]
            route, confidence = answer["choice"], answer["confidence"]
            if answer.get("type") != "choice" or route not in ROUTES:
                raise ValueError("Invalid routing answer")
            if (isinstance(confidence, bool) or not isinstance(confidence, (int, float))
                    or not math.isfinite(confidence) or not 0 <= confidence <= 1):
                raise ValueError("Invalid confidence")
            uncertain = confidence < threshold
            rows.append({"id": case["id"], "question_id": qid, "expected": case["expected"],
                         "choice": route, "confidence": confidence,
                         "status": "uncertain" if uncertain else
                         "pass" if route == case["expected"] else "fail"})
        results[policy] = {
            "cases": rows,
            "correct": sum(row["status"] == "pass" for row in rows),
            "uncertain": sum(row["status"] == "uncertain" for row in rows),
            "missed_escalations": sum(row["expected"] == "full_loop" and row["choice"] == "fast_path" for row in rows),
            "unnecessary_full_loop": sum(row["expected"] == "fast_path" and row["choice"] == "full_loop" for row in rows),
            "policy_agreement": sum(
                row["choice"] == (case["baseline_expected"] if policy == "baseline" else case["expected"])
                and row["status"] != "uncertain" for row, case in zip(rows, cases)
            ),
        }
    return {
        "scope": "semantic routing only; no task implementation, quality or speed measurement",
        "model": response["model"], "case_count": len(cases),
        "confidence_threshold": threshold, "results": results,
        "candidate_pass": results["candidate"]["correct"] == len(cases),
        "usage": response.get("usage", {}),
    }


def call_api(payload, key):
    request = urllib.request.Request(
        "https://api.typesafe.ai/v1/systemone",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send public synthetic cases to TypeSafe")
    parser.add_argument("--baseline-ref", default="2660db786e26aafc651cf9dd8b08efffb7deb717")
    parser.add_argument("--output", type=Path, help="Write a summary, never request headers or secrets")
    args = parser.parse_args(argv)
    try:
        cases = load_cases(ROOT / "tests/fixtures/fast_path_cases.json")
        if not args.live:
            print(f"Validated {len(cases)} synthetic cases across seven categories. Live evaluation NOT RUN.")
            return 0
        key = os.environ.get("TYPESAFE_API_KEY")
        if not key:
            print("Live evaluation NOT RUN: TYPESAFE_API_KEY is absent.", file=sys.stderr)
            return 2
        baseline_text = subprocess.check_output(
            ["git", "show", f"{args.baseline_ref}:SKILL.md"], cwd=ROOT, text=True)
        baseline = policy_excerpt(baseline_text)
        candidate = policy_excerpt((ROOT / "SKILL.md").read_text(encoding="utf-8"))
        # Separate calls prevent the new eligibility wording contaminating the
        # baseline. Pin the candidate call to the baseline's actual model.
        baseline_response = call_api(build_request(cases, baseline, "baseline"), key)
        candidate_request = build_request(cases, candidate, "candidate")
        candidate_request["model"] = baseline_response["model"]
        candidate_response = call_api(candidate_request, key)
        if candidate_response["model"] != baseline_response["model"]:
            raise ValueError("Comparison requires the same actual model")
        response = {
            "model": baseline_response["model"],
            "answers": {**baseline_response["answers"], **candidate_response["answers"]},
            "usage": {label: result.get("usage", {}) for label, result in
                      (("baseline", baseline_response), ("candidate", candidate_response))},
        }
        report = score_response(cases, response)
        report["request_count"] = 2
        report["policy_sha256"] = {
            "baseline": hashlib.sha256(baseline.encode()).hexdigest(),
            "candidate": hashlib.sha256(candidate.encode()).hexdigest(),
        }
        report["cases_sha256"] = hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest()
        report["baseline_ref"] = args.baseline_ref
        report["evaluated_at"] = datetime.now(timezone.utc).isoformat()
        rendered = json.dumps(report, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered)
        return 0 if report["candidate_pass"] else 1
    except urllib.error.HTTPError as error:
        print(f"Live evaluation incomplete: HTTP {error.code}. No result claimed.", file=sys.stderr)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        # Never echo an HTTP body, auth header, key or arbitrary server response.
        print(f"Evaluation incomplete: {type(error).__name__}; input, transport or response validation failed.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
