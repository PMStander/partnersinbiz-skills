---
name: platform-ops
description: >
  Cross-cutting platform primitives on Partners in Biz: API key management, platform health,
  global search, dashboard stats, activity feed, briefings, file uploads and library,
  Workspace OS folders/artifacts, Workspace Broker jobs, the unified workspace inbox,
  notifications, outbound webhooks with delivery history and replay, the agent manifest,
  workspace mailbox operations, unified chat conversations, and the canonical reference for
  collaboration primitives (idempotency, actor tagging, unified comments, mentions) that all
  other skills use. For agent/Hermes runtime administration, Platform Users staff management,
  and Reports, see the related skills below instead. Use this skill whenever the user
  mentions anything operational or cross-cutting, including: "dashboard stats",
  "platform stats", "global search", "search across everything", "find a doc",
  "find a contact", "API key", "create API key", "rotate key", "revoke key", "list keys",
  "upload a file", "file library", "list files", "find file", "delete file",
  "workspace artifact", "workspace folder", "Google Drive folder", "create Google Doc",
  "create Google Sheet", "export artifact", "share artifact", "permission audit",
  "system health", "uptime", "platform health", "my inbox", "workspace inbox",
  "what needs my attention", "assigned to me", "pending approvals", "overdue items",
  "mentions", "mark as read", "snooze notification", "notifications", "mark all read",
  "create webhook", "outbound webhook", "subscribe to events", "HMAC verify",
  "webhook delivery", "webhook history", "test webhook", "replay failed webhook",
  "disable webhook", "agent manifest", "what can the agent do", "leave a comment",
  "@mention teammate", "activity feed", "audit log", "recent activity". If in doubt, trigger.
---

# Platform Ops — Partners in Biz Platform API

Cross-cutting platform operations, plus the canonical reference for the collaboration primitives every other skill uses.

## Related skills

This mega-skill was split. If the request is about one of these, use that skill instead:

- `agent-runtime-ops` — Hermes profile links/controls, agent registry/admin, agent memory lookup/reindex, Loop Engine internals, runtime/provider health, linked computers
- `platform-admin-users` — Platform Users (staff) super-admin CRUD, onboard/offboard
- `reports` — snapshot reports + ad-hoc query reports (revenue, pipeline, outstanding, client-value, expense-summary, activity-summary, team-utilization)
- `billing-finance` — FX rates now live there (short reference + auth pointer)
- `book-studio-ops` — Book Studio production engine + Creative Canvas bridge
- `youtube-studio-ops` — YouTube Studio pipeline + Creative Canvas bridge
- `creative-canvas-ops` — canvas node graphs/runs/exports + BYOK provider connections
- `system-auth` — auth/delegation mint & resolve rules

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

- Call `GET /api/v1/oauth/whoami` first. If `memberRole` is not owner/admin (or super-admin for staff routes), say so and stop. On 403 print the API `error` — do not retry with `AI_API_KEY`.


## Base URL & Authentication

```
https://partnersinbiz.online/api/v1
```

```
Authorization: Bearer <AI_API_KEY>
```

Prefer the user-delegation Bearer token (`pib_dlg_…`) or `pib-skills login` / `pib_usr_` personal token for interactive work. Per-agent `pib_ag_...` keys and workspace `pib_ak_` keys are cron/system only. On 403, print the API error and stop.

For AI/agent bearer requests to tenant-scoped routes, also send:

```
X-Org-Id: <orgId>
```

Some routes have stricter delegation rules than ordinary admin-style agent access. Agent memory and mailbox operations must prove the requesting user context unless the agent has an explicit system permission.

### Browser auth and guest session routes

These routes are for browser sign-in/session cookies, not agent bearer automation:

| Method | Path | Auth | Use |
|---|---|---|---|
| POST | `/auth/magic-link/send` | public, rate-limited | Sends a single-use magic link. Body: `{ email, redirectUrl?, context?, docTitle? }`. Always returns `{ sent: true }` when accepted so account existence is not leaked. |
| GET | `/auth/magic-link/verify` | public token link | Consumes the magic-link token, creates/finds the guest user, mints a Firebase custom token, and redirects to `/auth/magic-link/verify`. |
| POST | `/auth/session` | public with Firebase ID token | Exchanges an ID token for the `__session` cookie and bootstraps `users/{uid}`. |
| POST/DELETE | `/api/auth/session` | public with Firebase ID token or cookie | Legacy browser session create/delete route. |
| GET/POST | `/api/auth/verify` | browser cookie/session-cookie helper | Verifies session and returns uid, role, email/name, and super-admin state. |
| GET/POST | `/api/auth/logout` | browser | Clears the session cookie and redirects to `/`. |

Do not use these for server-to-server agent calls. Agent work should use API keys, platform sessions, or delegated user evidence depending on the route.

## Collaboration primitives (canonical reference)

Every resource across all skills follows these primitives:

### Actor tagging

Every create/update records:
```json
{ "createdBy": "uid_or_agent_id", "createdByType": "user" | "agent" | "system",
  "updatedBy": "...", "updatedByType": "...", "updatedAt": "..." }
```

Agents and humans leave symmetric audit trails. `system` is reserved for cron-originated writes.

### Idempotency keys

Pass `Idempotency-Key: <uuid>` header on any `POST` that creates billable/notifiable resources. Same key replays the cached response for 24h.

Required for: `POST /invoices`, `POST /expenses`, `POST /quotes`, `POST /email/send`, `POST /tasks`, `POST /time-entries`, `POST /calendar/events`, `POST /forms`, `POST /organizations`, `POST /webhooks`.

Optional (but supported) everywhere else.

### Unified comments

Leave notes on any resource. Supported `resourceType`:
- `invoice`, `quote`, `contact`, `deal`, `project`, `task`
- `expense`, `time_entry`, `form_submission`, `calendar_event`, `client_org`

```json
POST /comments
{ "orgId": "org_abc", "resourceType": "invoice", "resourceId": "inv_xyz",
  "body": "Client wants to extend due date. @user:uid123 please review.",
  "parentCommentId": null, "attachments": ["file_abc"] }
```

`@user:<uid>` and `@agent:<id>` in body auto-create mention notifications. A denormalised `mentionIds: string[]` field on each comment enables fast inbox lookups.

### Unified workspace inbox

**Not the same as `/api/v1/social/inbox`** (which is social engagement).

The workspace inbox aggregates everything needing attention — notifications, mentions, assignments, pending approvals, overdue invoices — in one endpoint.

### Assignments

`assignedTo: { type: 'user' | 'agent', id }` works on tasks and calendar events. Creates a notification on assignment.

### Notifications

First-class notification feed. Types include: `task.assigned`, `invoice.paid`, `invoice.overdue`, `mention`, `form.submitted`, `expense.submitted`, `expense.approved`, `expense.rejected`, `member.invited`, `brand.updated`, `contact.created`, `deal.stage_changed`.

---

## API Reference

### Platform API keys

#### `GET /platform/api-keys` — auth: admin
List keys (hashes not returned; only `keyPrefix`).

#### `POST /platform/api-keys` — auth: admin
Body:
```json
{ "name": "Hermes production agent", "role": "agent", "orgId": "org_abc",
  "expiresAt": "2027-01-01" }
```

`role`: `admin` (prefix `pib_ak_`) or `agent` (prefix `pib_ag_`). Returns the raw key **once** in `keyOnce` — store it immediately. Subsequent GETs only show `keyPrefix`.

Response (201): `{ id, keyOnce, keyPrefix }`.

#### `GET/PUT/DELETE /platform/api-keys/[id]` — auth: admin
`DELETE` revokes.

### Global search

#### `GET /search?q=...` — auth: admin
Query: `q` (min 2 chars), `limit` (default 5, max 20).

Searches across: `contacts`, `projects`, `tasks`, `invoices`.

Response:
```json
[ { "id": "...", "type": "contact" | "project" | "task" | "invoice",
    "title": "...", "subtitle": "...", "url": "/admin/..." } ]
```

### Dashboard

#### `GET /dashboard/stats` — auth: admin
Top-line metrics:
```json
{ "contacts": { "total": 142 },
  "deals": { "total": 23, "pipelineValue": 120000, "wonValue": 45000 },
  "email": { "sent": 312, "opened": 180 },
  "sequences": { "active": 4, "activeEnrollments": 67 } }
```

#### `GET /dashboard/email-stats` — auth: admin
Email-specific metrics: sent, delivered, opened, clicked, bounced over last 30 days.

#### `GET /dashboard/activity` — auth: admin
Recent activity feed for dashboard widgets.

### Activity feed

#### `GET /activity` — auth: admin
Full activity feed (audit log). Filters: `orgId`, `type`, `resourceType`, `resourceId`, `from`, `to`, `page`, `limit`.

### Briefings

Briefings aggregate current account/project/CRM/document/social/support signals into a scannable action feed. Use these when the user asks what needs attention, asks for an account pulse, or wants to mark/read/defer briefing cards.

| Method | Path | Auth | Use |
|---|---|---|---|
| GET | `/briefings/feed` | client | Build the current briefing feed for the authenticated user's active scope. |
| POST | `/briefings/items/[itemId]/state` | client | Save per-user state for a briefing item (read/dismissed/snoozed/etc., based on route body). |
| POST | `/briefings/reports` | client | Create a durable briefing snapshot/report. |

Recent guardrail: urgent `task.agent_done` notification cards can be review work even when the task is already done. Inspect the source task state before calling something blocked; for project tasks, `columnId=done`, `agentStatus=done`, and `reviewStatus=approved` means the action is review/open-source, not unblock.

### Platform utility and cron routes

These routes are cross-cutting infrastructure. Use them for platform health, setup, session-safe public metadata, push-token registration, and scheduled workers.

| Method | Path | Auth | Use |
|---|---|---|---|
| GET | `/firebase-config` | public/client | Browser Firebase config bootstrap. |
| GET | `/org-dashboard` | client | Organization dashboard summary. |
| GET/PUT | `/settings/domain` | admin | Domain-related platform settings. |
| GET/PATCH | `/settings/features` | admin | Feature flags/settings. |
| GET/PATCH | `/settings/integrations` | admin | Integration settings. |
| POST | `/push-tokens` | client | Register mobile/web push token. |
| DELETE | `/push-tokens/[token]` | client | Remove a push token. |
| GET/PUT | `/orgs/[orgId]/chat-config` | admin/client with org access | Configure visible agents/chat behavior for an org. |
| GET | `/orgs/[orgId]/contacts` | client | Org-scoped contact lookup helper. |
| GET | `/orgs/[orgId]/visible-agents` | client | Visible agents for chat/portal context. |
| GET | `/llms.txt` | public | Public AI crawler/discovery metadata. |
| GET | `/llms-full.txt` | public | Expanded public AI crawler/discovery metadata. |

Current cron routes:

| Method | Path | Use |
|---|---|---|
| POST | `/api/cron/agent-memory-index` | Incremental agent memory indexing (see `agent-runtime-ops`). |
| GET | `/api/cron/anomalies` | Scheduled anomaly checks. |
| GET | `/api/cron/conversation-runs` | Unified chat/Hermes run finalization. |
| GET | `/api/cron/crm-integrations` | CRM integration syncs. |
| GET | `/api/cron/integrations` | Generic property/integration dispatch. |
| GET | `/api/cron/loop-review` | Scheduled agent-evolution and business-insight review loop (see `agent-runtime-ops`). |
| GET | `/api/cron/project-playbooks` | Scheduled project playbook jobs. |
| GET | `/api/cron/reports` | Scheduled report generation/sending (see `reports`). |
| GET | `/api/cron/seo-daily` | SEO daily loop. |
| GET | `/api/cron/seo-weekly` | SEO weekly optimization loop. |
| GET | `/api/cron/social-analytics` | Social analytics pull. |
| GET | `/api/cron/social-inbox-poll` | Social inbox polling. |
| GET | `/api/cron/social-rss` | RSS social auto-posting. |
| GET | `/api/cron/webhooks` | Outbound webhook queue processing. |

### Ads activity types (Phase 7)

Ad lifecycle events emit to the same `activity` collection with these types:

- `ad_campaign.{created|launched|paused|edited|deleted}`
- `ad_set.{created|launched|paused|edited|deleted}`
- `ad.{created|launched|paused|edited|deleted}`
- `ad_creative.{uploaded|archived|synced}`
- `ad_custom_audience.{created|list_uploaded|deleted}`

Each entry has `entityId` + `entityType` + `entityTitle` for cross-linking to the relevant ads admin page.

### Files

#### `POST /upload` — auth: admin
**multipart/form-data** with fields:
- `file` (required)
- `folder` (default `uploads`)
- `orgId`
- `relatedToType` + `relatedToId` (for linking)

Saves to Firebase Storage + writes metadata doc to `uploads` collection.

Response: `{ id, url, name, mimeType, size }`.

#### `GET /files` — auth: admin
List uploaded files. Filters: `orgId` (required), `type` (mime prefix, e.g. `image/`), `search` (filename contains), `relatedToType`, `relatedToId`, `page`, `limit`.

#### `GET /files/[id]` — auth: admin
Metadata including `url`, `mimeType`, `size`, `relatedTo`.

#### `DELETE /files/[id]` — auth: admin
Soft-delete (metadata). `?force=true` hard-deletes the Firestore doc (storage blob is NOT deleted — delete manually if needed).

### Workspace folders and Drive sync policy

For client/workspace assets, prefer the workspace folder registry over ad-hoc uploaded-file paths. A workspace or resource can have many linked folders, each with its own hierarchy, tags, sort order, Drive folder id/url, VPS/local sync targets, visibility, sync mode/state, and conflict/audit status.

V1 operating rules:
- Google Drive is canonical for binary/source assets.
- Obsidian/wiki remains markdown and lightweight text knowledge only; do not put PDFs, video, images, design exports, or other binaries in the vault.
- Folder visibility is per folder: `admin_only`, `admin_agents`, or `admin_agents_clients`.
- PiB roles/visibility decide what the app and agents can read; Drive ACLs must not accidentally expose admin/agent-only folders to clients.
- Sync targets can include both VPS and Peet's local Cowork environment; full file sync is expected for linked asset folders, not metadata-only sync.
- Conflicts must be preserved and audited. Do not use blind last-writer-wins.

Runbook: `docs/deploy/workspace-folder-sync-v1.md`.

#### Workspace OS API surface

Current route inventory from `partnersinbiz-web@origin/development`:

| Method | Path | Auth | Use |
|---|---|---|---|
| GET/POST | `/workspace-folders` | client | List or create linked workspace folders for an org/resource. |
| GET/PATCH/DELETE | `/workspace-folders/[id]` | client | Read, update, or disconnect a linked folder. |
| POST | `/workspace-folders/[id]/resync` | client | Request a resync for a linked folder. |
| GET | `/workspace-artifacts` | client | List artifacts the caller can read. |
| GET/PATCH/DELETE | `/workspace-artifacts/[id]` | client | Read, update, or request deletion/removal for an artifact record. |
| POST | `/workspace-artifacts/link-existing` | client | Register an existing Drive/file artifact against the workspace. |
| GET/POST | `/workspace-connections` | client | List or create connected external workspace accounts. |
| GET/PATCH/DELETE | `/workspace-connections/[id]` | client | Manage connected external workspace accounts. |
| POST | `/workspace-connections/[id]/reconnect` | client | Restart a broken connection flow. |
| POST | `/workspace-connections/[id]/review` | client | Record review/approval of a connection. |
| GET | `/agent/workspace-folders` | admin/agent | Agent lookup for readable workspace folders by org/resource/tag. |
| GET | `/agent/workspace-artifacts` | client/agent | Agent lookup for readable artifacts by org/resource/project/task/folder/type/status/q. |

Workspace artifacts are capability-scoped. `canReadWorkspaceArtifact` gates reads by org membership, role, visibility, and linked folder/resource policy. Do not bypass these APIs with raw Drive URLs unless Peet explicitly gives a direct file link.

#### Knowledge note proxy

| Method | Path | Auth | Use |
|---|---|---|---|
| GET/POST | `/admin/knowledge` | admin | Read or save markdown notes through Pip's knowledge backend. Supports `scope: shared|agent`, `section: index|wiki|raw|logs`, `agent`, `path`, and `content` for writes. |

Use this route for platform-mediated Obsidian/wiki persistence. For client-agent knowledge, pass the client knowledge agent/domain as `agent`; the route resolves aliases and rejects unsafe names.

#### Workspace Broker API surface

Use Workspace Broker when the agent needs the platform to create/copy/export Google workspace assets on behalf of the authenticated user/org.

For direct service-account Drive/Docs/Sheets work, use the `google-workspace` skill and the
`/google/drive/*`, `/google/docs/create`, and `/google/sheets/*` proxy endpoints. Use Workspace
Broker when you need a durable broker job, approval/review trail, or workspace artifact record;
use the direct Google proxy for straightforward list/upload/download/share/search/doc/sheet calls
that already have the required PiB auth and org scope.

| Method | Path | Auth | Use |
|---|---|---|---|
| POST | `/workspace-broker/docs/create` | admin | Create a Google Doc and record a broker job. |
| POST | `/workspace-broker/docs/copy-template` | admin | Copy a Google Doc template. |
| POST | `/workspace-broker/sheets/create` | admin | Create a Google Sheet and record a broker job. |
| POST | `/workspace-broker/sheets/copy-template` | admin | Copy a Google Sheet template. |
| POST | `/workspace-broker/folders/create` | admin | Create a Google Drive folder. |
| POST | `/workspace-broker/artifacts/[id]/export` | admin | Export an artifact. |
| POST | `/workspace-broker/artifacts/[id]/permission-audit` | admin | Audit artifact sharing/ACL state. |
| POST | `/workspace-broker/artifacts/[id]/request-share` | admin | Request or apply sharing changes. |
| POST | `/workspace-broker/artifacts/[id]/request-delete` | admin | Request deletion/removal through the broker. |
| GET | `/workspace-broker/jobs` | admin | List broker jobs. |
| GET/PATCH | `/workspace-broker/jobs/[id]` | admin | Read or update a broker job. |

Broker routes create durable `workspace-broker` jobs. After a broker call, poll `/workspace-broker/jobs/[id]` instead of assuming synchronous completion.

### Health

#### `GET /health` — auth: admin
```json
{ "ok": true, "timestamp": "...", "services": { "firestore": "ok", "auth": "ok", "storage": "ok" } }
```

For Hermes/model-provider runtime health (systemd, profile health, model canary), see `agent-runtime-ops`.

### Workspace inbox

#### `GET /inbox` — auth: admin
Unified inbox aggregating:
- `notification` items (from `notifications`)
- `mention` items (from `comments` where `mentionIds` contains current user/agent)
- `assignment` items (tasks assigned to current user/agent, status `todo`|`in_progress`)
- `approval` items (expenses `status=submitted`, social posts `status=pending_approval`)
- `overdue_invoice` items (invoices `status=overdue`)

Query: `orgId` (required), `for` (`me`|`agent`|`all`, default `me`), `unread` (default `true`), `limit` (default 50, max 200), `cursor` (ISO timestamp for keyset pagination).

Response:
```json
{ "items": [
    { "id": "inbox_X", "itemType": "mention", "resourceType": "invoice", "resourceId": "inv_xyz",
      "title": "Pip mentioned you", "body": "Client wants to extend due date...",
      "priority": "normal", "link": "/portal/invoicing/inv_xyz", "createdAt": "..." }
  ],
  "nextCursor": "2026-04-15T09:00:00Z" }
```

#### `POST /inbox/read` — auth: admin
Body: `{ itemIds: string[] }`. Marks notification items read. Non-notification items are marked read by interacting with their resource.

Response: `{ marked: count }`.

#### `POST /inbox/snooze` — auth: admin
Body: `{ itemId, until: ISO }`. Only for notifications.

### Notifications

#### `GET /notifications` — auth: admin
Filters: `orgId` (required), `status` (default `unread`), `userId`, `agentId`, `type`, `limit`, `cursor`.

Item shape:
```json
{ "id": "...", "orgId": "...", "userId": "uid_or_null", "agentId": "aid_or_null",
  "type": "task.assigned", "title": "...", "body": "...", "link": "/admin/tasks/...",
  "data": {...}, "priority": "normal", "status": "unread",
  "snoozedUntil": null, "readAt": null, "createdAt": "..." }
```

#### `POST /notifications` — auth: admin
Body: notification fields. Required: `orgId`, `type`, `title`. At least one of `userId`/`agentId` (or both null for org-wide).

#### `GET/PATCH/DELETE /notifications/[id]` — auth: admin
PATCH updatable: `status`, `snoozedUntil`, `priority`. `status='read'` sets `readAt`.

#### `POST /notifications/read-all` — auth: admin
Body: `{ userId?, agentId?, orgId }`. Marks all unread for that recipient read.

### Outbound webhooks (durable queue)

#### Architecture overview

```
your-api-call → dispatchWebhook() → writes to webhook_queue
                                          │
                                   (every 1 min Vercel cron)
                                          ↓
                                   processPendingWebhooks()
                                          │
                                   POSTs to webhook.url with HMAC signature
                                          │
                                   on success → webhook_deliveries (audit)
                                   on failure → retry with backoff [0s, 30s, 2m, 10m, 1h, 6h]
                                                 max 6 attempts; auto-disable after 10 failures
```

#### `GET /webhooks` — auth: admin
Filters: `orgId` (required), `active`, pagination. Secret is redacted as `***`.

#### `POST /webhooks` — auth: admin (idempotent)
Body:
```json
{
  "orgId": "org_abc",
  "name": "Slack notifier",
  "url": "https://hooks.slack.com/...",
  "events": ["invoice.paid", "deal.won", "form.submitted"],
  "secret": "<optional — auto-generated if omitted>"
}
```

URL must be `https://` in production (dev can allow http via env). Events must be from the allowed list (see below).

Response (201): `{ id, secretOnce, secret: '***' }`. **`secretOnce` is only returned on create** — store it immediately.

#### `GET/PUT/DELETE /webhooks/[id]` — auth: admin
PUT updatable: `name`, `url`, `events`, `active`. See `/rotate-secret` for secret rotation.
DELETE soft-deletes.

#### `POST /webhooks/[id]/rotate-secret` — auth: admin
Rotates the HMAC secret. Returns the new secret once in `secretOnce` — store it immediately. All future deliveries sign with the new secret, so update consumer verification code **before** rotating.

Response (201): `{ id, secretOnce: "new_secret_hex", secret: "***" }`.

#### `POST /webhooks/[id]/test` — auth: admin
Queues a test event bypassing subscription filter. Returns `{ queued: true, queueItemId }`.

#### `POST /webhooks/[id]/enable` / `POST /webhooks/[id]/disable` — auth: admin
Manual enable/disable. Enable clears `autoDisabledAt` + `failureCount`.

#### `GET /webhooks/[id]/deliveries` — auth: admin
Query: `limit` (default 20, max 100), `cursor` (doc id). Sorted `deliveredAt desc`.

Delivery shape:
```json
{ "id": "dl_abc", "webhookId": "wh_xyz", "queueItemId": "wq_abc", "event": "invoice.paid",
  "payloadHash": "sha256...", "responseStatus": 200, "responseHeaders": {...},
  "responseBody": "ok (truncated 2KB)", "durationMs": 142, "attemptNumber": 1,
  "deliveredAt": "...", "error": null }
```

#### `POST /webhooks/[id]/deliveries/[deliveryId]/replay` — auth: admin
Re-queues a fresh `webhook_queue` item copying the original event + payload. Original record untouched.

#### `GET /webhooks/queue-stats` — auth: admin
Global observability snapshot. Optional `?orgId=X` scope. Returns:
```json
{ "byStatus": { "pending": N, "delivering": N, "failed": N, "deliveredLast24h": N },
  "oldestPendingAgeSeconds": N | null,
  "stuckDeliveringCount": N,
  "webhooks": { "total": N, "active": N, "autoDisabled": N },
  "timestamp": "ISO" }
```

`stuckDeliveringCount` = items claimed more than 5 minutes ago and still in `delivering`. Non-zero means a worker died mid-flight — investigate.

#### `GET /webhooks/[id]/queue` — auth: admin
Queue items for a specific webhook (debug view).

Query: `status` (pending|delivering|delivered|failed), `limit` (default 20, max 100), `cursor` (doc id from previous page).

Response: `{ items: [...], nextCursor: string | null }`.

#### Webhook event reference

| Event | Payload fields |
|-------|----------------|
| `invoice.created` | `id, invoiceNumber, total, currency, clientOrgId, dueDate` |
| `invoice.sent` | `id, invoiceNumber, total, currency, clientEmail, dueDate, publicViewUrl` |
| `invoice.paid` | `id, invoiceNumber, total, paymentMethod, paymentReference, paidAmount` |
| `invoice.overdue` | `id, invoiceNumber, total, dueDate, daysOverdue` |
| `quote.created` | `id, quoteNumber, total, currency, clientOrgId` |
| `quote.accepted` / `quote.rejected` | `id, quoteNumber, clientOrgId` |
| `contact.created` / `contact.updated` | `id, name, email, company, source` (orgId in metadata) |
| `deal.created` | `id, title, value, stage, contactId` |
| `deal.stage_changed` | `id, fromStage, toStage, value` |
| `deal.won` / `deal.lost` | `id, value, contactId` |
| `form.submitted` | `formId, slug, submissionId, contactId, data` |
| `payment.received` | `invoiceId, invoiceNumber, amount, paymentMethod, reference` |
| `expense.submitted` | `id, amount, currency, category, userId, submittedBy` |
| `task.completed` | `id, title, projectId, completedBy` |

#### Webhook signature verification (consumer code)

Every request includes:
- `X-PIB-Event` — event name
- `X-PIB-Delivery-Id` — unique delivery id
- `X-PIB-Timestamp` — ms since epoch
- `X-PIB-Signature` — `sha256=<hex>` HMAC of `${timestamp}.${rawBody}` using webhook secret

Node verifier:
```js
import crypto from 'crypto'

function verifyWebhook(req, rawBody, secret) {
  const timestamp = req.headers['x-pib-timestamp']
  const signature = req.headers['x-pib-signature']
  if (!timestamp || !signature) return false

  // Reject if timestamp is more than 5 min old (replay protection)
  if (Math.abs(Date.now() - Number(timestamp)) > 5 * 60 * 1000) return false

  const expected = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(`${timestamp}.${rawBody}`)
    .digest('hex')

  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))
}
```

### Agent manifest

#### `GET /agent` — auth: admin
Returns a manifest of agent-accessible endpoints with examples. Use this to discover capabilities programmatically.

#### `GET /agent/inbox` — auth: admin
Legacy agent-specific inbox — superseded by `/inbox` for new work.

#### Agent email work queue

Current route inventory:

| Method | Path | Auth | Use |
|---|---|---|---|
| GET | `/agent/email` | client/agent | Agent email capability overview. |
| GET | `/agent/email/accounts` | client/agent | List connected Gmail/SMTP accounts for a user (no secrets). |
| GET | `/agent/email/messages` | client/agent | List delegated messages available to the agent. |
| POST | `/agent/email/drafts` | client/agent | Draft outbound email for human review; returns `contextRef` + `open_context` uiActions. |
| POST | `/agent/email/replies` | client/agent | Prepare a reply draft for human review; returns `contextRef` + `open_context` uiActions. |
| POST | `/agent/email/send-requests` | client/agent | Create an auditable send request. |

Mailbox/email operations are stricter than ordinary admin-like agent access. The route must prove the requesting user/delegation context unless the agent has explicit system permission.

### Workspace mailbox operations

Mailbox routes manage connected Gmail/Google mailbox accounts and messages. Use `email-outreach` for marketing sends, sequences, broadcasts, templates, and analytics. Use this section for operational inbox work, delegated mailbox triage, account sync, and support replies.

#### Admin mailbox

| Method | Path | Auth | Use |
|---|---|---|---|
| GET/POST | `/admin/mailbox/accounts` | admin | List/connect admin mailbox accounts. |
| DELETE/PATCH | `/admin/mailbox/accounts/[id]` | admin | Disconnect/update a mailbox account. |
| POST | `/admin/mailbox/accounts/[id]/sync` | admin | Trigger account sync. |
| GET | `/admin/mailbox/google/authorize` | admin | Start Google OAuth authorization. |
| GET | `/admin/mailbox/google/callback` | admin | Google OAuth callback. |
| GET/POST | `/admin/mailbox/messages` | admin | List/send admin mailbox messages. |
| DELETE/PATCH | `/admin/mailbox/messages/[id]` | admin | Delete/update a mailbox message. |

#### Portal mailbox

| Method | Path | Auth | Use |
|---|---|---|---|
| GET/POST | `/portal/email/accounts` | client | List/connect portal mailbox accounts. |
| DELETE/PATCH | `/portal/email/accounts/[id]` | client | Disconnect/update a portal mailbox account. |
| POST | `/portal/email/accounts/[id]/sync` | client | Trigger portal account sync. |
| GET | `/portal/email/google/authorize` | client | Start Google OAuth authorization. |
| GET | `/portal/email/google/callback` | client | Google OAuth callback. |
| GET/POST | `/portal/email/messages` | client | List/send portal mailbox messages. |
| DELETE/PATCH | `/portal/email/messages/[id]` | client | Delete/update a portal mailbox message. |

Agents should not treat mailbox messages as marketing broadcasts. Respect delegated user context and keep outbound replies auditable via `/agent/email/*` or the mailbox message routes, depending on the requested workflow.

#### Connected mailbox first (operational Gmail / SMTP)

Messages injects a `[Mailbox connections]` block when the acting user has authenticated Google/SMTP accounts.

1. If the prompt says `status: connected`, call `GET /agent/email/accounts` then `GET /agent/email/messages?summarize=true&q=...` with the injected `pib_dlg_…` Bearer token from **this turn** **before** asking the user to paste email content. Use only that token. If mailbox returns 401/403 with delegation-evidence, the platform remints once and retries silently — do not ask the human to send a chat message. If it still fails, say the mailbox call failed and stop. Never fall back to `AI_API_KEY`.
2. Never claim you cannot access their email when the mailbox block shows a connected account — use `/agent/email/*`.
3. Portal `/portal/email/*` is browser/session only. Hermes must use `/agent/email/*`.
4. Message reads auto-refresh stale Google sync (≈5 min) and, when `q` is set, also run a **live Gmail search** that imports matches before filtering. Prefer short queries (`rs@ahslaw.co.za`, `Rikus Stander July 20`) — not full Gmail UI sentences.
5. `summarize=true` returns `bodyPreview` (up to 8k). For full text use `GET /agent/email/messages/{id}`. If connected + hits exist, **never** ask the user to paste the email.
6. After drafting, echo returned `uiActions`/`contextRef` so Messages opens the email side canvas. Humans **Approve & send**; do not auto-send.

### Admin operations utility routes

For the Hermes agent registry, admin agent config/health/logs/skills/cron, and Hermes profile links/controls, see `agent-runtime-ops`. For Platform Users (staff) CRUD and password/reset routes, see `platform-admin-users`.

| Method | Path | Auth | Use |
|---|---|---|---|
| GET | `/admin/notification-preferences` | admin | Read/update admin notification preferences (GET/PATCH). |
| GET | `/admin/support` | admin | List support tickets. |
| PATCH | `/admin/support/[id]` | admin | Update support ticket status/metadata. |
| GET/POST | `/admin/support/[id]/messages` | admin | List/add support ticket messages. |

### Unified chat conversations

These routes back the in-app admin/client/agent chat surface. They are distinct from `/communications/*`, which is the customer-channel inbox for WhatsApp/SMS/email/in-app/social DMs.

| Method | Path | Auth | Use |
|---|---|---|---|
| GET/POST | `/conversations` | client | List or create a unified chat conversation for an org. `POST` requires `orgId` and `participants`. Valid scopes: `general`, `project`, `task`, `campaign`. |
| GET/PATCH | `/conversations/[convId]` | participant or admin/ai | Fetch conversation or update `title`/`archived`. |
| DELETE | `/conversations/[convId]` | admin | Permanently delete a conversation. |
| GET/POST | `/conversations/[convId]/messages` | participant or admin/ai | List messages or add a user message/attachments/slash command; agent participants dispatch Hermes runs. |
| POST | `/conversations/[convId]/attachments` | participant or admin/ai | Upload an attachment up to 10MB. Allowed: common image types, PDF, text/markdown/csv/json, docx, xlsx. |
| PATCH | `/conversations/[convId]/context` | participant or admin/ai | Add/remove/clear structured context references. Body action is `add`, `remove`, or `clear`. |
| POST | `/conversations/[convId]/messages/[msgId]/finalize` | participant or admin/ai | Poll Hermes and write a run result back into the pending assistant message. Requires `runId` and `agentId`. |
| POST | `/conversations/[convId]/messages/[msgId]/stop` | admin | Stop an in-flight agent run through the agent gateway and mark the message failed. |
| POST | `/admin/agents/[agentId]/runs/[runId]/actions` | admin | Send a rich-message action back to a Hermes run. Approval/denial reuses the run approval endpoint; clarify/model-picker/choose/retry/open/copy/download/custom actions are proxied to the run actions endpoint. |

Conversation participant rules:
- Client callers may start conversations only with people in their org or platform admins.
- Admin/AI callers may include visible agents. When multiple agents are selected, Pip is inserted as orchestrator when available.
- Client org context and attached context refs are injected into the Hermes prompt. Do not manually paste unrelated client context into a conversation.

Rich chat output contract:
- Hermes events and final run payloads may include `richParts`/`rich_parts` and `uiActions`/`ui_actions`. The PiB chat normalizer and finalizer preserve those fields instead of flattening them into text.
- Supported `richParts` include `markdown`, `code`, `table`, `image`, `gallery`, `file`, `audio`, `video`, `tool_output`, `status`, `approval`, `clarify`, and `model_picker`.
- Supported `uiActions` include `approve`, `deny`, `choose`, `retry`, `stop`, `open`, `open_context`, `copy`, `download`, and `custom`. Prefer stable `id` plus `action_id`/`actionId` values so the web UI can round-trip choices to Hermes.
- Telegram inline keyboards are adapter-specific; the web chat equivalent is a `uiActions` array. If a Hermes payload only contains a Telegram-style `reply_markup.inline_keyboard`, PiB will derive button actions as a fallback, but agents should emit web-native `uiActions` when possible.
- After `POST /agent/email/drafts` or `/agent/email/replies`, echo the returned `uiActions` / `contextRef` into the assistant message. Messages treats `open_context` with `{ kind: "email", id }` as attach-and-open for the email draft canvas. Humans review/edit there and use **Approve & send**; do not auto-send.
- After creating or preparing a content-engine `campaign` or a `social_posts` row for human review in Messages, emit `open_context` with `{ kind: "campaign", id }` or `{ kind: "social", id }`. Messages attaches the ref and opens the Context Dock with platform-faithful preview cards (Instagram/LinkedIn/Facebook/X/YouTube/blog). Still link the cockpit (`/portal/campaigns/[id]`) or social review workspace for full approve/schedule flows.
- After creating an invoice (`POST /invoices`) or quote (`POST /quotes`) for human review in Messages, emit `open_context` with `{ kind: "invoice", id }` or `{ kind: "quote", id }`. Messages opens the Context Dock with the print-friendly document HTML (`GET /invoices/[id]/html` / `GET /quotes/[id]/html`). Still link the admin/portal workspace; do not send or convert until the human confirms.
- For approval, clarify, and model picker prompts, send a visible rich part and matching actions. The in-app UI renders those controls in `MessageBubble` and posts the chosen action through the admin agent run action route.

#### Context reference search

| Method | Path | Auth | Use |
|---|---|---|---|
| GET | `/context-references/search` | client | Search attachable context references by `type`, `q`, `orgId`, optional `projectId`, `contextType`, `contextId`, and `limit`. |

Use this before adding references to conversations, comments, research items, or project artifacts. Context refs are tenant-scoped and access-filtered by the resolver; do not fabricate refs from raw IDs unless the resolver can see them.

### Reports (cross-cutting)

Moved to the `reports` skill — see `GET /reports/activity-summary` and `GET /reports/pipeline` there for the cross-cutting query reports, plus the full snapshot-report CRUD.

### Comments (full reference)

Listed in "Collaboration primitives" above. Full API:

#### `GET /comments?orgId=X&resourceType=...&resourceId=...` — auth: admin
Sorted `createdAt asc`. Default limit 100. `?includeDeleted=true` to include soft-deleted.

#### `POST /comments` — auth: admin
Creates + parses mentions + notifies mentioned users/agents (async). Response: `{ id, mentions }`.

#### `GET/PATCH/DELETE /comments/[id]` — auth: admin
PATCH: update `body` (re-parses mentions but **does not re-notify**), toggle `agentPickedUp`, update `attachments`.
DELETE soft by default; `?force=true` hard.

---

## Workflow guides

### 1. Set up a new AI agent

```bash
# Issue a scoped API key for the agent
POST /platform/api-keys
{ "name": "Sales follow-up agent", "role": "agent", "orgId": "org_abc",
  "expiresAt": "2027-01-01" }
# → { id, keyOnce: "pib_ag_...", keyPrefix: "pib_ag_abcd" }

# Discover available endpoints
GET /agent
```

### 2. Agent daily loop

```bash
# 1. Pull my inbox
GET /inbox?orgId=org_abc&for=me&unread=true

# 2. Process each item
#    - mention → GET the resource, read context, POST a reply comment
#    - assignment → do the task, then POST /tasks/[id]/complete
#    - overdue_invoice → GET /invoices/[id], POST follow-up email

# 3. Mark handled notifications read
POST /inbox/read
{ "itemIds": ["inbox_a", "inbox_b"] }
```

### 3. Subscribe to events

```bash
# Create webhook
POST /webhooks
{ "orgId": "org_abc", "name": "Slack", "url": "https://hooks.slack.com/...",
  "events": ["deal.won", "invoice.paid", "form.submitted"] }
# → { id: "wh_xyz", secretOnce: "abc...", secret: "***" }

# Test it
POST /webhooks/wh_xyz/test

# Check delivery history
GET /webhooks/wh_xyz/deliveries

# Replay a specific failed delivery
POST /webhooks/wh_xyz/deliveries/dl_abc/replay
```

### 4. Upload + attach a file to a comment

```bash
# 1. Upload
POST /upload   (multipart: file, orgId=org_abc, relatedToType=invoice, relatedToId=inv_xyz)
# → { id: "file_abc", url: "https://..." }

# 2. Attach to a comment
POST /comments
{ "orgId": "org_abc", "resourceType": "invoice", "resourceId": "inv_xyz",
  "body": "Updated quote attached.", "attachments": ["file_abc"] }
```

### 5. Find anything via search

```bash
GET /search?q=acme
# Returns top matching contacts, projects, tasks, invoices
```

### 6. Generate weekly activity summary

See the `reports` skill for the full request/response shape:

```bash
GET /reports/activity-summary?orgId=org_abc&from=2026-04-07&to=2026-04-13
```

### 7. Verify a webhook delivery

On the consumer side: parse headers, verify signature, check timestamp freshness. Sample Node code above.

On sender side: check deliveries for status:
```bash
GET /webhooks/wh_xyz/deliveries?limit=50
```

## Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `q must be at least 2 characters` | Lengthen search query |
| 400 | `Idempotency-Key required` (rare) | Pass the header |
| 401 | Unauthorized | Check `AI_API_KEY` or key expiry |
| 403 | Forbidden | Key lacks org access |
| 404 | `Webhook not found` | Verify id |
| 409 | Duplicate action | Check resource state |
| 429 | Rate limited | Respect `Retry-After` header |

## Agent patterns

1. **Poll `/inbox` as your work queue** — it's the unified view. For humans this is their dashboard; for agents it's the daily loop trigger.
2. **Comment before you act** — leave a comment stating what the agent is about to do, then execute, then update the comment with the result. Humans can trust and verify.
3. **Pass `Idempotency-Key` on creates** — especially in retry loops. A UUIDv4 per logical operation is ideal.
4. **Subscribe to webhooks instead of polling** — cheaper, faster, more reliable.
5. **Use `X-PIB-Timestamp` freshness check** — reject webhook payloads older than 5 minutes.
6. **Prefer soft-delete** — `DELETE` is soft by default; only use `?force=true` when you're certain.
7. **Search is eventually consistent** — freshly-created items may not appear for ~1 min.
8. **Activity log everything** — use `POST /activity` (auto-written by most routes) for a durable audit trail.
