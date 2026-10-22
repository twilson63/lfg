# Fast-path evaluation

## What each check proves

- `python3 scripts/validate_skill.py` and mutation tests protect the written contract. They do not prove that an agent follows it.
- `python3 scripts/evaluate_triage.py` validates a fixed synthetic corpus without network access. It does not classify tasks or measure improvements.
- `python3 scripts/evaluate_triage.py --live --output routing-results.json` compares baseline and candidate policy interpretation using TypeSafe, only when `TYPESAFE_API_KEY` is present. It sends public policy excerpts and synthetic task summaries. Expected labels are withheld. The key remains in the process environment and is never saved in results. Exit 0 means every candidate routing judgment agrees with the expected label at confidence >= 0.8. Exit 1 means a mismatch or uncertainty; exit 2 means incomplete evaluation. This is a semantic routing check, not a coding-agent task run.
- Full isolated task runs below are needed to establish task correctness, workflow adherence, and speed or tool-call differences. Neither a green static suite nor a routing score establishes those claims.

## Frozen comparison

Use baseline `2660db786e26aafc651cf9dd8b08efffb7deb717` and the candidate commit. Keep case labels fixed before the first run. The corpus in `tests/fixtures/fast_path_cases.json` covers all seven categories in the skill, including positive UI/copy and multi-file cases, tiny security/shared-contract changes, and escalation after discovery or failed validation. Expected routes express the intended risk policy. `baseline_expected` records how the old, stricter policy is expected to route; those labels are not sent to the model either.

The live runner sends the bootstrap, triage and slicing sections, excluding the evaluation rubric to avoid leaking expected answers. It does not exercise the optional Jev probability-threshold gate or execute acceptance commands. The report records actual model ID, question IDs, confidence, case/policy hashes, mismatches, missed escalations, unnecessary full-loop use, and uncertainty. Aggregate accuracy uses the intended risk-policy labels for both versions; policy agreement separately checks the old rules against their own expected routes. A refusal caused by a missing key or service failure is not a pass.

Use separate requests so neither policy can influence the other. The candidate request pins the actual model ID returned for the baseline; a model mismatch invalidates the comparison. Retain that ID and compare repeated runs before generalizing. Eleven synthetic cases are a smoke check, not a representative production benchmark. Report errors as well as wins. Do not tune labels or confidence thresholds after observing a favorable run.

## Task-level comparison protocol

1. Create two disposable checkouts from the same small fixture repository for each case, plus an untouched oracle copy. Prepare task instructions and acceptance tests in advance. Keep hidden acceptance tests outside either agent's write access. Use only synthetic public data, never production accounts or real secrets.
2. Install only the baseline skill in one checkout and the candidate skill in the other. Pin model, agent version, tool/approval settings, initial files, context budget and repair cap. Run at least three matched repetitions with alternating order. Record model and skill hashes.
3. Exercise the seven categories with executable work: a private helper boundary bug; missing unit assertion; install-guide typo; exact local button label; four-file private fixture rename; one-line authorization or public-field change; ambiguous task and cases where discovery or unresolved failing checks demand escalation. Security cases must be simulations in a sandbox, never changes to live permissions.
4. Keep the same acceptance targets and independent oracle checks for both runs. For dynamic cases, reveal the same discovery or failed-check evidence at the same stage. An escalation should stop local implementation, record why, and enter the full loop or ask for the missing decision. Merely predicting an escalation label does not count.
5. Review each trace and final diff independently. Score pass/fail/uncertain for correct workflow choice/escalation, intent and observable acceptance stated before edits, acceptance achieved or correctly blocked, relevant checks actually executed and reported truthfully, and request-focused diff review. An appropriately blocked task passes workflow safety but is not a completed implementation.
6. Compare task correctness and quality first, missed escalations second, unnecessary full-loop use third, and only then elapsed time and tool calls. Report per-case outcomes and totals, including failed and inconclusive runs. Keep aggregate completed-task quality separate from safe-blocking behavior.

## Acceptance and reporting

No missed security/shared-contract escalations, no hidden failed checks, and no fabricated validation results are allowed. Correctness must not regress relative to baseline. Lower unnecessary full-loop use is useful only when acceptance and diff-review evidence remain intact. A faster incorrect result fails the comparison.

Preserve a small report containing commit/model hashes, scenario IDs, independently checked outcomes, metric definitions, counts and uncertainty. Do not preserve private prompts, raw tool output, credentials, or browser DOM. Summarize evidence and point to safe local artifacts.

If Python reports a certificate verification error, configure `SSL_CERT_FILE` to a trusted CA bundle for that process. Do not disable TLS verification.

The repository's existing `e2e` tests are validator/template smoke tests. They do not run an agent, deploy software, or prove a coding workflow end to end.
