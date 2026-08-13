<!-- ASD-STE100: Use short sentences. Max 25 words per sentence. Use active voice. One instruction per sentence. -->
<!-- Title must be Conventional Commits: type(scope): description  e.g. feat(funds): MCDS-033 slice 1 — data/service -->
<!-- This template implements the MCDS-033/034/035 Epic slice model: https://gist.github.com/twilson63/1b9bb838da806958cc1a11579c9d4a5d -->

# Pull Request — Context-Boundary Slices

## 1. Title (Conventional Commits)

> Use `type(scope): description`. Add `BREAKING CHANGE:` footer when you change API or Zod. Add `Closes #<slice-issue>` and `Part of #<epic>`.

**PR Title:** `<!-- e.g. feat(funds): MCDS-033 slice 1 — data/service -->`

**Related Issues:** Closes #___  Part of #___ (epic)

## 2. Summary (ASD-STE100)

> Write in Simplified Technical English. Max 25 words per sentence. Use approved verbs. Do not use idioms. Define each abbreviation.

This PR does ____. It changes ____. It uses ____. It verifies ____.

Abbreviations:
- E2E = End-to-End
- DoD = Definition of Done
- STE = Simplified Technical English (ASD-STE100)

Before STE (if rewritten): <!-- paste long sentence -->
After STE: <!-- paste short sentences -->

## 3. Context-Boundary Slices

> One row per boundary. Check DoD for each slice. Link branches. Slice 1 blocks 2–3. Slice 4 gates the epic.

| Slice | Boundary | Branch | Commit scope | Depends on | DoD checked | Unit gate | E2E gate |
|---|---|---|---|---|---|---|---|
| 1 | `data` + `service` | `<!-- e.g. mcds-033-1-data -->` | `feat(data)` / `feat(service)` | — | [ ] Prisma model/migration + Zod in `packages/types` (`z.infer` only) <br> [ ] `data/` only place with `prisma` (`{tx?}`) <br> [ ] `services/` uses `withTransaction(SERIALIZABLE, P2034×3+jitter)` + freeze/balance checks <br> [ ] Errors `OrderValidationError` / `InsufficientFundsError` / `TransactionConcurrencyError(409)` | [ ] `data/*.test.ts` mocked `tx` + `services/*.test.ts` retries — cmd: `pnpm --filter @repo/db --filter @repo/types test` | [ ] `pnpm check-types` green — log: `___` |
| 2 | `api` routes | `<!-- e.g. mcds-033-2-api -->` | `feat(api)` | Slice 1 | [ ] Thin handlers `validateInput → service → respond → c.json(201|200)`; no Prisma <br> [ ] `requireJwtSession → loadUserRoles → requirePermission('<perm>')` (+ `requirePinVerification`) <br> [ ] `authenticatedRateLimit` + `requireFacilityAccess` on `/:code/*` <br> [ ] `error-handler.ts` maps Zod 400, `PIN_REQUIRED 403`, `P2002→409` | [ ] Hono `app.request` mocked service + `testErrorHandler` — cmd: `pnpm --filter @repo/api test` | [ ] `turbo build` per-layer gate green — log: `___` |
| 3 | `admin` / kiosk UI | `<!-- e.g. mcds-033-3-ui -->` | `feat(admin)` or `feat(ui)` | Slice 1 | [ ] Mantine `useForm+zodResolver(Schema)` → TanStack Query hooks <br> [ ] `usePermissions().hasPermission` + wildcard + `System Admin` bypass <br> [ ] Freeze/block disabled states surfaced | [ ] Vitest `jsdom` + `setupFiles` — cmd: `pnpm --filter @repo/admin test` | [ ] Snapshot/disabled-state pass — file: `___` |
| 4 | `integration` / seed / audit | `<!-- e.g. mcds-033-4-int -->` | `chore(seed)` / `feat(audit)` | Slices 1–3 | [ ] `prisma/seeds/*` + `facilities.ts` for `1147/7000/7001`, `batches`, `journalEntries` <br> [ ] `pnpm db:seed` + `db:reset` green <br> [ ] `docs/` + `planning` updated | [ ] n/a (E2E only) | [ ] `POST /admin/facility/:code/... →201` + cents check + `GET /logs` audit — cmd: `pnpm test:e2e` or `pytest -m e2e` — log: `___` |

Collapsed to one PR? Check this and keep all 4 DoD rows: [ ] `Skip linked slices — size justifies single PR` (only if `<4 files`, `<2 days`, single facility, no freeze/balance, `≤3 devs`).

## 4. Commits (Conventional Commits)

> Every commit on the branch must match `^(feat|fix|docs|chore|refactor|test|build|ci)(\(.+\))?!?: .+`

```
feat(data): add JournalEntry model and TransferFundsSchema
feat(api): add POST /admin/facility/:code/transfer route
feat(admin): add transfer form with permission gate
chore(seed): add 1147 fund seeds and batches

Part of #<epic>
Closes #<slice-issue>
```

Actual commits in this PR:

- `<!-- paste git log --oneline -->`

## 5. Test Evidence (required for automated pr-review)

> A slice cannot merge if it has no unit evidence and no E2E evidence. Paste commands and evidence paths.

### Unit tests

- Command: `<!-- e.g. pnpm --filter @repo/db test -- data/transfer.test.ts -->`
- Evidence: `<!-- e.g. test-results/unit-slice-1.xml or log excerpt -->`
- Result: [ ] pass

- Command: `<!-- e.g. pnpm --filter @repo/api test -->`
- Evidence: `<!-- log -->`
- Result: [ ] pass

### E2E / route tests

- Command: `<!-- e.g. pnpm test:e2e or pytest -m e2e -->`
- Request: `curl -X POST /admin/facility/1147/transfer -H "Authorization: Bearer $TOKEN" -d '{"amountCents": 12345}'`
- Expected: `201` + `balance.cents == 12345` + `GET /logs` contains `JournalEntry`
- Log excerpt: `<!-- paste -->`
- Result: [ ] pass

### Validation gates run

- [ ] `python3 scripts/validate_skill.py` — log: `___`
- [ ] `python3 scripts/validate_pr_slices.py` — log: `___`
- [ ] `pytest -q` — log: `___`
- [ ] `pytest -m e2e` or `pnpm test:e2e` — log: `___`
- [ ] `pnpm check-types` / `turbo test` — log: `___`

## 6. Automated Review Checklist (pr-review must verify)

- [ ] Title is Conventional Commit
- [ ] Each slice row has branch + scope + DoD + unit gate + E2E gate
- [ ] PR summary uses STE (each sentence ≤25 words, active voice, one instruction per sentence)
- [ ] No Prisma in `routes/` or `services/` (`grep -R "from '@/utils/prisma'" --include="*.ts" | grep -v "^data/"` is empty)
- [ ] No regex in prod code
- [ ] DB uses `cents (int)`, dollars only at boundary (`validateInput → respond`)
- [ ] `withTransaction(SERIALIZABLE, P2034×3+jitter)` present and tested
- [ ] `error-handler.ts` maps Zod 400, `PIN_REQUIRED 403`, `P2002→409` with `Macs2-Language`
- [ ] Redis permission cache (5-min TTL) invalidated on role change; `System Admin` bypass preserved (if permissions changed)
- [ ] Unit gate green for slices 1–3
- [ ] E2E gate green for slice 4 (201 + cents + audit)
- [ ] `docs/` and `planning` updated; `permissions:generate` synced if needed

## 7. Screenshots / Logs

> Paste form states, disabled-state, audit log entry.

## 8. Risks & Rollback

- Risk: `<!-- ___ -->`
- Rollback: `<!-- revert commit SHA or seed reset -->`

---
*Template version: MCDS-033/034/035 + LFG §3a. Keep this template. Do not delete checklist items. Mark not-applicable with `n/a` and reason.*
