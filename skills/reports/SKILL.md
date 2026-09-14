---
name: reports
description: >
  Reports on Partners in Biz: durable snapshot reports (generate/list/edit/archive/email a
  stored monthly-style report doc with KPIs, executive summary, brand snapshot, public token)
  and live ad-hoc query reports (revenue, pipeline, outstanding invoices, client lifetime
  value, expense summary, activity summary, team utilization) with no persistence. Owner:
  data. Use this skill whenever the user mentions: "generate report", "monthly report",
  "send report", "report snapshot", "archive report", "revenue report", "pipeline report",
  "outstanding invoices report", "client value", "client lifetime value", "expense summary",
  "activity summary", "team utilization", "aged receivables". If in doubt, trigger.
---

# Reports — Partners in Biz Platform API

Two separate report surfaces:

1. **Snapshot reports** (`POST /reports`) — generates and stores a full monthly report doc (with KPIs, executive summary, brand snapshot). Listed via `GET /reports`.
2. **Ad-hoc query reports** (`GET /reports/revenue`, `/pipeline`, etc.) — live queries, no persistence. Use these for dashboard widgets and agent decisions.

## Related skills

- `billing-finance` — invoicing/expenses that feed the revenue/outstanding/expense-summary reports (billing-finance links here instead of duplicating report docs)
- `project-management` — deals/pipeline data that feeds the pipeline report
- `platform-ops` — general platform primitives, activity feed, dashboard stats

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

## Base URL & Authentication

```
https://partnersinbiz.online/api/v1
```

```
Authorization: Bearer <AI_API_KEY>
```

Prefer the user-delegation Bearer token (`pib_dlg_…`) for interactive/human-triggered runs — see `## Auth (mandatory)` above.

## API Reference

### Snapshot reports

#### `GET /reports?orgId=X` — auth: admin

Lists previously generated report documents for an org.

Query: `orgId` (required), `limit` (default 24, max 100).

Response: `{ ok: true, reports: [...] }`.

#### `POST /reports` — auth: admin

Generates and stores a new report. Uses the org's timezone from the `organizations` collection (defaults to UTC).

Body:
```json
{
  "orgId": "org_abc",
  "type": "monthly",
  "month": "2026-04",
  "start": "2026-04-01",
  "end": "2026-04-30",
  "propertyId": "prop_xyz"
}
```

- `type` — `"monthly"` (default) or any `ReportType`.
- `month` — `YYYY-MM` format. Resolved to the org's timezone month boundaries. Defaults to last completed month.
- `start` / `end` — ISO dates for a custom range (overrides `month`).
- `propertyId` — optional property scope; omit for org-wide.

Response: `{ ok: true, report: { id, orgId, type, period, kpis, exec_summary, highlights, status, publicToken, brand, ... } }`.

Note: `maxDuration` is 60s — report generation can be slow.

#### `GET /reports/[id]` — auth: admin

Fetches one report by ID. Returns `404` if not found.

Response: `{ ok: true, report: {...} }`.

#### `PATCH /reports/[id]` — auth: admin

Editable fields on a stored report:
- `exec_summary` (string)
- `highlights` (string array, max 8 items)
- `status` (`"draft"` | `"sent"` | `"archived"`)

Response: `{ ok: true, report: { updated fields... } }`.

#### `DELETE /reports/[id]` — auth: admin

Soft-archives the report by setting `status: "archived"`. The doc is not removed.

Response: `{ ok: true }`.

#### `POST /reports/[id]/send` — auth: admin

Emails the report to one or more recipients via Resend. Sends a branded HTML email with top-level KPI summary and a CTA button linking to the public report page (`/reports/<publicToken>`). Marks the stored report `status: "sent"`.

Body:
```json
{ "to": ["client@example.com", "cfo@example.com"] }
```

Requirements: report must have a `publicToken` and `RESEND_API_KEY` must be configured.

Response: `{ ok: true, link: "https://partnersinbiz.online/reports/<token>", recipients: [...] }`.

Note: `maxDuration` is 30s.

### Ad-hoc query reports

All ad-hoc report endpoints are live queries — no stored state. Returns empty results gracefully when collections don't exist yet.

#### `GET /reports/revenue` — auth: admin

Revenue grouped into time buckets from paid invoices.

Query:
- `orgId` (required)
- `from` (required, ISO date) — inclusive, matched against `paidAt`
- `to` (required, ISO date) — inclusive
- `groupBy` — `"month"` (default) | `"quarter"` | `"week"` | `"day"`

Response:
```json
{
  "from": "2026-01-01T00:00:00.000Z",
  "to": "2026-04-30T23:59:59.000Z",
  "groupBy": "month",
  "buckets": [
    { "label": "2026-01", "total": 45000, "count": 3 },
    { "label": "2026-02", "total": 62000, "count": 5 }
  ],
  "grandTotal": 107000,
  "currency": "ZAR"
}
```

Mixed-currency response includes `"mixed": true` and per-bucket `byCurrency: { "ZAR": N, "USD": N }` instead of top-level `currency`.

Bucket label formats: `YYYY-MM` (month), `YYYY-Www` (week, ISO), `YYYY-Qq` (quarter), `YYYY-MM-DD` (day).

#### `GET /reports/pipeline` — auth: admin

Deal pipeline snapshot grouped by stage.

Query: `orgId` (required).

Response:
```json
{
  "byStage": {
    "prospect":    { "count": 8,  "value": 80000 },
    "proposal":    { "count": 4,  "value": 55000 },
    "negotiation": { "count": 2,  "value": 30000 },
    "won":         { "count": 12, "value": 140000 },
    "lost":        { "count": 3,  "value": 25000 }
  },
  "totalOpen":      165000,
  "totalClosedWon": 140000,
  "totalClosedLost": 25000,
  "winRate": 0.8
}
```

`winRate` = `closedWonCount / (closedWonCount + closedLostCount)`. Excludes deleted deals.

#### `GET /reports/outstanding` — auth: admin

Outstanding (unpaid) invoices aged by `dueDate`. Statuses included: `sent`, `overdue`, `payment_pending_verification`.

Query: `orgId` (required).

Response:
```json
{
  "buckets": {
    "0-30":  { "count": 3, "total": 15000 },
    "31-60": { "count": 1, "total": 8000  },
    "61-90": { "count": 0, "total": 0     },
    "90+":   { "count": 2, "total": 22000 }
  },
  "total": 45000,
  "count": 6,
  "currency": "ZAR"
}
```

Invoices with no `dueDate` are placed in `0-30`. Mixed currencies add `"mixed": true` and remove top-level `currency`.

#### `GET /reports/client-value` — auth: admin

Lifetime paid invoice value ranked by client org.

Query:
- `orgId` (required) — billing org scope
- `limit` (optional, default 20, max 100)

Response:
```json
{
  "clients": [
    {
      "clientOrgId": "org_abc",
      "clientName":  "Acme Corp",
      "lifetimeValue": 185000,
      "invoiceCount": 14,
      "lastInvoiceAt": "2026-04-10T00:00:00.000Z"
    }
  ],
  "total": 185000
}
```

Sorted descending by `lifetimeValue`. `clientName` is sourced from the snapshotted `clientDetails.name` field on each invoice.

#### `GET /reports/expense-summary` — auth: admin

Expenses grouped by category, project, or user within a date window.

Query:
- `orgId` (required)
- `from` (ISO, optional — defaults to 30 days ago)
- `to` (ISO, optional — defaults to now)
- `groupBy` — `"category"` (default) | `"project"` | `"user"`

Response:
```json
{
  "from": "...", "to": "...", "groupBy": "category",
  "buckets": [
    { "label": "travel",    "total": 12000, "count": 5, "billable": 3, "reimbursable": 2 },
    { "label": "software",  "total": 4500,  "count": 2, "billable": 2, "reimbursable": 0 }
  ],
  "grandTotal": 16500,
  "currency": "ZAR"
}
```

`billable` and `reimbursable` are counts (not amounts) of entries in the bucket with those flags set. Sorted descending by `total`. Returns empty buckets if the `expenses` collection doesn't exist.

#### `GET /reports/activity-summary` — auth: admin

Cross-module activity counts over a date window.

Query:
- `orgId` (required)
- `from` (ISO, optional — defaults to 30 days ago)
- `to` (ISO, optional — defaults to now)

Response:
```json
{
  "from": "...", "to": "...",
  "counts": {
    "socialPosts":      12,
    "emailsSent":       84,
    "invoicesCreated":   7,
    "dealsUpdated":     15,
    "contactsAdded":    23,
    "tasksCompleted":   31
  }
}
```

Each sub-collection query is wrapped in `try/catch` — a missing collection or missing index returns `0` for that metric rather than failing the whole response.

#### `GET /reports/team-utilization` — auth: admin

Billable vs non-billable time per user from the `time_entries` collection (owned by the A7 time-tracking module).

Query:
- `orgId` (required)
- `from` (ISO, optional — defaults to 30 days ago)
- `to` (ISO, optional — defaults to now)

Response:
```json
{
  "users": [
    {
      "userId": "uid_abc",
      "totalMinutes": 2400,
      "billableMinutes": 1920,
      "nonBillableMinutes": 480,
      "utilizationPct": 80.0
    }
  ],
  "totalMinutes": 2400,
  "avgUtilizationPct": 80.0
}
```

`utilizationPct` = `billableMinutes / totalMinutes * 100`, rounded to 2 decimal places. Users sorted descending by `totalMinutes`. Returns zeroed totals if `time_entries` doesn't exist yet.

## Workflow guides

### Generate and send a monthly report

```bash
POST /reports
{ "orgId": "org_abc", "type": "monthly", "month": "2026-04" }
# → { report: { id, publicToken, ... } }

POST /reports/<id>/send
{ "to": ["client@example.com"] }
```

### Weekly activity summary

```bash
GET /reports/activity-summary?orgId=org_abc&from=2026-04-07&to=2026-04-13
```

### PiB revenue + client-value snapshot

```bash
GET /reports/revenue?orgId=org_abc&from=2026-01-01&to=2026-04-16&groupBy=month
GET /reports/client-value?orgId=org_abc
```

## Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `orgId is required` | Include `orgId` in query/body |
| 404 | `Report not found` | Verify report id |
| 500 | Report generation timeout | Retry; check `maxDuration` 60s budget |

## Agent patterns

1. **Ad-hoc reports are live queries** — always call fresh; do not cache beyond the current task.
2. **Snapshot reports are the durable, client-facing artifact** — use them when a report needs a stable public link or email delivery.
3. **Check `mixed`/`byCurrency`** on revenue and outstanding responses before summarizing a single total.
4. **Require `publicToken` + `RESEND_API_KEY`** before attempting `POST /reports/[id]/send`.
5. **Cross-check with `billing-finance`** before treating a revenue/outstanding number as final — invoice status changes (paid, cancelled) affect these buckets immediately.
