# Epic — Sliced Delivery Template (MCDS-033/034/035 pattern)

> Copy this template for each epic that spans multiple context boundaries. Source: https://gist.github.com/twilson63/1b9bb838da806958cc1a11579c9d4a5d — One Epic, 4 linked slices.

## Epic

**Title:** `<!-- e.g. Funds Movement — MCDS-033/034/035 -->`
**Epic issue:** `#___`
**Facility codes:** `<!-- e.g. 1147 primary, 7000/7001 test -->`
**Permission seeds:** `<!-- e.g. transfer:inmate:funds, create:deposits:*, transfer:phone:funds -->`
**Related:** `MCDS-021 Freeze/Block precedence, MCDS-014 Account Balance Rules, MCDS-019 Roles & Permissions`

## Epic user story

**As a** ___,
**I want to** ___,
**So that** ___.

**Epic acceptance (all slices done):**
- [ ] All flows hit `withTransaction(SERIALIZABLE, P2034×3+jitter)` and return `ApiErrorResponseSchema` via `error-handler.ts` + `Macs2-Language`
- [ ] `cents (int)` in DB, dollars at boundary — validated by `validateInput → respond`
- [ ] Redis permission cache (5-min TTL) invalidated on role change; `System Admin` bypass preserved
- [ ] Audit: every funded move writes `JournalEntry` + `listJournalEntries` readable under `view:facility:logs`

## Dependency graph

```
data/service (slice-1) ─┬─► api routes (slice-2)
                         ├─► admin/kiosk UI (slice-3)
                         └─► blocked by 021 Freeze + 014 MinBalance + 019 permissions
integration (slice-4) ◄── all of above + seeds/batches/journals
```

## Slice breakdown — Definition of Done per AGENTS.md

### Slice 1 — data + service (BLOCKS 2–3)

**Branch:** `<scope>-<id>-1-data` e.g. `mcds-033-1-data`
**Commit scope:** `feat(data)`, `feat(service)`
- [ ] Prisma model/migration (if needed) + Zod schemas in `packages/types` — `z.infer` only
- [ ] `data/` only place with `prisma` — take `{tx?}`, `Zod.parse` result, no business logic
- [ ] `services/` owns `withTransaction(async (tx) => …)`, freeze/balance/indigent checks, `OrderValidationError` / `InsufficientFundsError` / `TransactionConcurrencyError(409)`
- [ ] Tests: `data/*.test.ts` (mocked `tx`) + `services/*.test.ts` (retries)
- [ ] `pnpm check-types` + `pnpm --filter @repo/db --filter @repo/types test` green

### Slice 2 — api routes

**Branch:** `<scope>-<id>-2-api`
**Commit scope:** `feat(api)`
- [ ] Thin handlers: `validateInput → service → respond → c.json(201|200)` — no Prisma
- [ ] Auth: `requireJwtSession → loadUserRoles → requirePermission('<perm>')` (+ `requirePinVerification` where needed)
- [ ] Rate-limit `authenticatedRateLimit` + `requireFacilityAccess` on `/:code/*`
- [ ] `utils/error-handler.ts` mapping verified (Zod 400, `PIN_REQUIRED 403`, `P2002→409`)
- [ ] Tests: Hono `app.request` with mocked service + `testErrorHandler`

### Slice 3 — admin / kiosk UI

**Branch:** `<scope>-<id>-3-ui`
**Commit scope:** `feat(admin)` or `feat(ui)`
- [ ] Mantine `useForm + zodResolver(Schema)` → `hooks/api/*` via TanStack Query
- [ ] Permission-gated UI: `usePermissions().hasPermission('<perm>')` + wildcard, `System Admin` bypass visual
- [ ] Freeze/block/disabled states surfaced (e.g. `Blocked`/`FREEZE_ALL` blocks form)
- [ ] Tests: Vitest `jsdom` + `setupFiles` for Mantine

### Slice 4 — integration / seed / audit

**Branch:** `<scope>-<id>-4-int`
**Commit scope:** `chore(seed)` or `feat(audit)`
- [ ] `prisma/seeds/*` + `facilities.ts` updated, `pnpm db:seed` + `db:reset` green (fallback when `seed-fake-*`)
- [ ] E2E/route test: `POST /admin/facility/:code/... →201` + balance `cents` + `GET /logs` audit entry
- [ ] `docs/` + `planning` updated, `pnpm check-types` + `turbo test` + `permissions:generate` synced

## When to collapse to ONE issue/PR

Collapse only if **all** true: `<4 files`, `<2 days`, single facility scope, no freeze/balance precedence branch, `≤3 devs` with no parallel benefit. Add to PR description: `Skip linked slices — size justifies single PR` and keep all 4 DoD checklists in that one PR.

## How to create in GitHub

1. Create Epic issue from this template (labels: `epic`, `<area>`)
2. Create 4 linked slice issues from DoD sections, each `Blocked by #<slice-1>` + `Part of #<epic>`
3. Branches: `mcds-033-1-data → PR → mcds-033-2-api` (rebases on 1) etc. — keeps diffs reviewable and per-layer gate green
4. Close Epic only when Slice 4 E2E is green on `dev`

## PR submission (LFG §3a) — Conventional Commits + ASD-STE100 + Automated review

- **Title:** Conventional Commit (`feat(funds): MCDS-033 slice 1 — data/service`). Each commit scope matches slice: `feat(data)`, `feat(api)`, `feat(admin)`, `chore(seed)`.
- **Documentation:** Write PR summary in ASD-STE100 — max 25 words per sentence, active voice, one instruction per sentence, approved verbs only (`do`, `make`, `use`, `check`, `send`, `show`, `write`, `update`, `test`, `verify`).
- **Testability:** Each slice lists unit command + evidence and E2E command + evidence. Slices 1–3 need unit gate green; slice 4 needs E2E gate green (`201 + cents + audit`).
- **Automated checklist:** Use `.github/pull_request_template.md` — all boxes must be checkable by CI (`validate_pr_slices.py`, `pytest -q`, `pytest -m e2e`).

## Checklist — Epic is DONE

- [ ] All 4 slices merged to `dev` (not just `main`)
- [ ] `Adam / admin_2026` @ `1147` can complete each flow via UI + via `curl` against `/admin/facility/:code/...`
- [ ] `OrderValidation / InsufficientFunds / Concurrency 409` errors return localized `error` + stable `code` per `error-handler.ts`
- [ ] No Prisma in `routes/` or `services` (grep `from '@/utils/prisma'` only in `data/`), no regex in prod code
