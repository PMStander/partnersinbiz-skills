---
name: life-os-ops
description: >
  Partners in Biz Life OS: personal daily check-ins, an AI coach workflow, self-experiments,
  reminder preferences/scheduling, weekly reviews, and admin-only data retention. Owner: pip.
  Use this skill whenever the user mentions Life OS check-ins, the Life OS coach, personal
  experiments, reminders, or reviews.
---

# Life OS Ops — Partners in Biz Platform API

## Owner & scope

- Owner: `pip`
- Allowed: `pip` (all routes); `admin`/`super_admin` roles can read/write any `ownerId` within their org; retention is `admin`-only
- Risk: low (personal data; no spend/publish surface) — retention run is a data-governance action, treat `mode: "commit"` as sensitive
- Base path: `https://partnersinbiz.online/api/v1/life-os` (retention lives under `/api/v1/admin/life-os`)
- Related: `system-auth`, `project-management`, `ceo-on-demand-gather`

Every non-admin route is scoped to `orgId` (required query param or body field) **and** `ownerId` (defaults to the caller's own `uid`). A regular user can only read/write their own `ownerId`; `admin`/`super_admin` can act on any owner in an org they can access.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Route map (shipped)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/life-os/check-ins?orgId=&ownerId=&limit=` | List daily check-ins for an org (optionally one owner), newest `localDate` first, capped at 200 |
| POST | `/life-os/check-ins` | Create a daily check-in (`orgId` required; `ownerId` defaults to caller) — validated/shaped by `buildDailyCheckIn` |
| GET | `/life-os/experiments?orgId=&ownerId=&limit=` | List self-experiments, newest `startDate` first |
| POST | `/life-os/experiments` | Create a self-experiment with tracked outcomes — shaped by `buildLifeExperiment` |
| GET | `/life-os/reviews?orgId=&ownerId=&limit=` | List weekly reviews, newest `periodStart` first |
| POST | `/life-os/reviews` | Create a weekly review — shaped by `buildWeeklyReview` |
| POST | `/life-os/coach` | Run the AI coach workflow: takes `orgId`, optional `ownerId`, recent `dailyCheckIns`/`weeklyReviews` (server re-filters to the exact org+owner), returns plan suggestions + experiment recommendations. **Crisis safety boundary**: if `workflow.safetyBoundary.level === 'crisis'`, `planSuggestions`/`experimentRecommendations` are stripped from the response — never fabricate or backfill them client-side |
| GET | `/life-os/reminders?orgId=&ownerId=&limit=` | Get the owner's reminder preferences **and** their scheduled reminders (soonest `scheduledFor` first) |
| PATCH | `/life-os/reminders` | Update reminder preferences (`optedIn`, `channels`, `quietHours`, `enabledKinds`) — merges onto existing prefs, does not replace wholesale |
| POST | `/life-os/reminders` | Submit reminder `candidates[]` to be evaluated against preferences/quiet-hours; each candidate is either created (idempotent by derived id) or `suppressed` with a reason — response separates `created`/`suppressed` |
| POST | `/admin/life-os/retention` | **Admin-only.** Run the Life OS data-retention job for one `orgId`+`ownerUid`. `mode: "dry-run"` (default) reports what would happen; `mode: "commit"` actually anonymizes/deletes and **requires** a non-empty `approvalEvidence` string — the route hard-400s a commit without it |

## Agent patterns

### Log a check-in and confirm it landed
1. `POST /life-os/check-ins` with `{ orgId, ownerId, ...fields }` → capture `id` from the response (the created record is also echoed inline).
2. `GET /life-os/check-ins?orgId=...&ownerId=...&limit=5` and confirm the new `id`/`localDate` is present before telling the human it's logged.

### Reminder scheduling with suppression awareness
1. `GET /life-os/reminders?orgId=...` to read current preferences (quiet hours, opted-in channels/kinds) before scheduling anything.
2. `POST /life-os/reminders` with `candidates`. Read the response's `suppressed` array — a candidate can be silently dropped (quiet hours, opted-out kind, duplicate). Report suppressions to the user; never claim a suppressed reminder was scheduled.
3. `GET /life-os/reminders?orgId=...` again to read back the `reminders` list and confirm the expected ids now exist.

### Retention: dry-run before commit, always
1. `POST /admin/life-os/retention` with `{ orgId, ownerUid, mode: "dry-run" }` and read the report.
2. Only call again with `mode: "commit"` + `approvalEvidence` (e.g. an approval task id/link) after a human has reviewed the dry-run — this is a destructive/anonymizing operation and should sit behind the platform's approval-gate convention even though the pack manifest doesn't yet list a formal `approvalGates` entry for it.

## Success gate

After any create/update above:
1. `GET` the relevant list (check-ins, experiments, reviews, or reminders+preferences) scoped to the same `orgId`/`ownerId`.
2. Assert the new/changed record is present with the expected fields.
3. For `/life-os/coach`, treat a `crisis` safety boundary as a hard stop — surface it to the human, don't keep generating plan content.
4. Surface exact API `error` strings on 4xx — do not retry with a different `ownerId` to bypass a 403.

## Source of truth

Route implementations live under `app/api/v1/life-os/**` and `app/api/v1/admin/life-os/**`. Record shaping lives in `lib/self-improvement/*`; retention logic in `lib/privacy/life-os-retention*`. If this skill and the route disagree, the route wins — update this skill immediately.

## Cross-references

- `project-management` — personal task overlap with Life OS experiments/reviews
- `ceo-on-demand-gather` — cross-agent status digest that may surface Life OS state
- `system-auth` — token/credential minting doctrine
