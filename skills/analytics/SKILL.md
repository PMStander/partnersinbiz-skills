---
name: analytics
description: >
  Product analytics for Partners in Biz: event ingestion, sessions, funnel analysis, user
  timelines, cohort retention, live event stream, and the @partnersinbiz/analytics-js browser SDK.
  Use this skill whenever the user mentions anything analytics-related, including: "track event",
  "ingest event", "analytics", "funnel", "conversion rate", "sessions", "pageview", "identify user",
  "browser SDK", "analytics SDK", "install analytics", "events table", "event count",
  "session detail", "funnel results", "funnel steps", "conversion window", "distinct ID",
  "session ID", "UTM tracking", "device detection", "IP hash", "rate limit", "ingest key",
  "property ID analytics", "product_events", "product_sessions", "product_funnels",
  "user timeline", "retention curve", "cohort", "cohort analysis", "live events", "live stream",
  "GDPR purge", "delete user data", "erase user". If in doubt, trigger.
---

# Analytics — Partners in Biz

Product analytics module: event collection, session tracking, funnel analysis, user timelines,
cohort retention, live event stream, and browser SDK.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## Architecture overview

```
Browser SDK (@partnersinbiz/analytics-js)
    │
    │  POST /api/v1/analytics/ingest   (public, ingest-key auth)
    ▼
product_events  ←→  product_sessions  ←→  product_funnels
    │
Admin API (all require Bearer auth)
    ├── GET  /api/v1/analytics/events
    ├── GET  /api/v1/analytics/events/count
    ├── GET  /api/v1/analytics/sessions
    ├── GET  /api/v1/analytics/sessions/[id]
    ├── GET/POST /api/v1/analytics/funnels
    ├── GET/PUT/DELETE /api/v1/analytics/funnels/[id]
    ├── GET  /api/v1/analytics/funnels/[id]/results
    ├── GET  /api/v1/analytics/users
    ├── GET  /api/v1/analytics/users/[distinctId]      (timeline)
    ├── DELETE /api/v1/analytics/users/[distinctId]    (GDPR purge)
    ├── GET  /api/v1/analytics/retention
    └── GET  /api/v1/analytics/live
```

Each `property` (from the Properties module) has one `ingestKey` — a 64-char hex string.  
The ingest endpoint is public (no Bearer). Query endpoints accept the user-delegation Bearer token (`pib_dlg_…`) for interactive runs (see `## Auth (mandatory)` above) or `Authorization: Bearer <AI_API_KEY>` for cron/system jobs.

---

## Ingest endpoint

### `POST /api/v1/analytics/ingest` — public, ingest-key auth

Header: `x-pib-ingest-key: <ingestKey>`

Body:
```json
{
  "propertyId": "prop_abc",
  "events": [
    {
      "event": "$pageview",
      "distinctId": "uuid-v4",
      "sessionId": "uuid-v4",
      "timestamp": 1713350400000,
      "properties": {
        "$current_url": "https://example.com/pricing",
        "$pathname": "/pricing",
        "$referrer": "https://google.com",
        "$utm_source": "google",
        "$utm_medium": "cpc",
        "$device_type": "desktop"
      }
    }
  ]
}
```

Constraints:
- Max 50 events per batch → 400 if exceeded
- `event`, `distinctId`, `sessionId` required per event → rejected with reason in `errors[]`
- Rate limit: 100 req/min per ingest key → 429
- Wrong/missing key → 401

Response:
```json
{ "accepted": 1, "rejected": 0, "errors": [] }
```

Session upsert: one `product_sessions` doc per unique `sessionId`, updated with event counts, last-seen time, device/country/UTM fields from the first event that provides them.

---

## Events API

### `GET /api/v1/analytics/events` — auth: admin

Query params:
- `propertyId` (required)
- `event` — filter by event name
- `from` / `to` — ISO date strings
- `distinctId` — filter to a specific user
- `limit` — max 500, default 100

Response:
```json
{ "events": [
    { "id": "evt_abc", "propertyId": "prop_abc", "event": "$pageview",
      "distinctId": "uuid", "sessionId": "uuid", "timestamp": 1713350400000,
      "properties": { "$current_url": "..." }, "serverTime": "2026-04-17T..." }
  ],
  "total": 1 }
```

### `GET /api/v1/analytics/events/count` — auth: admin

Same filters as above (except `limit`). Returns grouped counts:

```json
{ "counts": [
    { "event": "$pageview", "count": 342 },
    { "event": "signup", "count": 41 }
  ] }
```

---

## Sessions API

### `GET /api/v1/analytics/sessions` — auth: admin

Query params: `propertyId` (required), `from`, `to`. Max 200 results.

Response:
```json
{ "sessions": [
    { "id": "ses_abc", "propertyId": "prop_abc", "sessionId": "uuid",
      "distinctId": "uuid", "startedAt": "...", "lastEventAt": "...",
      "eventCount": 12, "pageviewCount": 5, "durationSeconds": 183,
      "device": "desktop", "country": "ZA",
      "utmSource": "google", "utmMedium": "cpc", "utmCampaign": null,
      "entryUrl": "https://...", "exitUrl": "https://..." }
  ],
  "total": 1 }
```

### `GET /api/v1/analytics/sessions/[id]` — auth: admin

Returns session metadata + up to 1000 events for that session, sorted by timestamp:

```json
{
  "session": { ...session doc... },
  "events": [ ...up to 1000 events... ]
}
```

---

## Funnels API

### `GET /api/v1/analytics/funnels` — auth: admin

Query: `propertyId` (required).

Response: `{ "funnels": [...] }`

### `POST /api/v1/analytics/funnels` — auth: admin

Body:
```json
{
  "propertyId": "prop_abc",
  "name": "Signup funnel",
  "steps": [
    { "event": "$pageview" },
    { "event": "signup_started" },
    { "event": "signup_completed" }
  ],
  "window": "24h"
}
```

`steps`: minimum 2 required.  
`window`: `"1h"` | `"24h"` | `"7d"` | `"30d"` | `"session"` (default `"24h"`).

Response (201): full funnel doc.

### `GET/PUT/DELETE /api/v1/analytics/funnels/[id]` — auth: admin

PUT updatable: `name`, `steps`, `window`.  
DELETE is hard delete.

### `GET /api/v1/analytics/funnels/[id]/results` — auth: admin

Query: `from` + `to` (both required, ISO date strings). Loads up to 10k events and runs the funnel compute.

Response:
```json
{
  "funnel": { "id": "...", "name": "Signup funnel", "window": "24h", ... },
  "results": {
    "steps": [
      { "event": "$pageview", "count": 342, "conversionFromPrev": null },
      { "event": "signup_started", "count": 87, "conversionFromPrev": 25.44 },
      { "event": "signup_completed", "count": 41, "conversionFromPrev": 47.13 }
    ],
    "totalEntered": 342,
    "totalConverted": 41
  }
}
```

`conversionFromPrev`: percentage (0–100, 2 decimal places). `null` for step 0.

---

## Funnel compute rules

- Groups events by `distinctId`, sorted by `timestamp`
- Greedy left-to-right: once a user completes step N, look for step N+1 in subsequent events
- Window enforcement:
  - `session`: steps must share the same `sessionId`
  - All others: each step must occur within `windowMs` of the *previous step* (not the funnel start)
- `FunnelStep.filters` is reserved for future property-filter implementation — currently a no-op

---

## Browser SDK

### Install

The SDK lives at `packages/analytics-js/`. It is linked into the Next.js app via:
```json
// package.json
"@partnersinbiz/analytics-js": "file:./packages/analytics-js"
```
```ts
// next.config.ts
transpilePackages: ['@partnersinbiz/analytics-js']
```

### Usage

```ts
import { init, track, identify, page } from '@partnersinbiz/analytics-js'

// On app boot
init({
  propertyId: 'prop_abc',
  ingestKey: 'your-ingest-key',
  apiUrl: 'https://partnersinbiz.online',  // optional, defaults to production
})

// Track custom events
track('signup_started', { plan: 'pro' })
track('signup_completed', { plan: 'pro', method: 'email' })

// Identify a user (fires $identify event)
identify('user_123', { email: 'user@example.com', name: 'Alice' })

// Manual pageview (init() fires the first one automatically)
page({ title: 'Pricing' })
```

### Auto-tracking

`init()` automatically:
- Fires `$pageview` on load
- Intercepts `history.pushState` and `popstate` for SPA navigation → fires `$pageview` on each route change
- Attaches `pagehide` listener for flush-on-unload (uses `keepalive: true`)

### Batching

Events queue locally and flush:
- Every 5 seconds (if queue non-empty)
- When queue reaches 10 events
- On `pagehide`

### Identity persistence

| Key | Storage | Purpose |
|-----|---------|---------|
| `_pib_did` | localStorage | `distinctId` — stable cross-session user identity |
| `_pib_sid` | localStorage | `sessionId` — rotates after 30min inactivity |
| `_pib_last` | localStorage | Last event timestamp for session rotation |

---

## Env vars

| Var | Required | Purpose |
|-----|----------|---------|
| `ANALYTICS_IP_SALT` | **Yes (production)** | Salt for SHA-256 IP hashing. Generate with `openssl rand -hex 32`. Never change after data exists — it breaks historical consistency. The fallback `'pib-analytics-default-salt'` is public and enables rainbow table attacks. |

---

## Admin UI

Located at `/portal/analytics/`:

| Route | Description |
|-------|-------------|
| `/portal/analytics/events` | Events table with property/event/date filters |
| `/portal/analytics/sessions` | Sessions list with user/device/UTM columns |
| `/portal/analytics/sessions/[id]` | Session detail — metadata grid + event timeline |
| `/portal/analytics/funnels` | Funnel list, create form, inline results |
| `/portal/analytics/users` | Users list with event counts + first/last seen |
| `/portal/analytics/users/[distinctId]` | Full event timeline for one user |
| `/portal/analytics/retention` | Cohort retention heatmap (day/week granularity) |
| `/portal/analytics/live` | Real-time event feed (polls every 5s, last 5 min) |

---

## Firestore collections

| Collection | Description |
|------------|-------------|
| `product_events` | Individual events, one doc per event |
| `product_sessions` | One doc per session (upserted on ingest) |
| `product_funnels` | Funnel definitions |
| `analytics_rate_limits` | Rate limit buckets — internal, `allow read, write: if false` |

All collections: `allow read, write: if false` in `firestore.rules` — all access via Admin SDK.

---

## Key files

| File | Purpose |
|------|---------|
| `lib/analytics/types.ts` | All shared types |
| `lib/analytics/ip-hash.ts` | Salted SHA-256 IP hashing |
| `lib/analytics/device.ts` | UA → DeviceType detection |
| `lib/analytics/ingest-rate-limit.ts` | Rate limiter (Firestore transaction) |
| `lib/analytics/funnel-compute.ts` | Pure funnel computation |
| `lib/analytics/retention-compute.ts` | Pure cohort retention computation (ISO 8601 week) |
| `packages/analytics-js/src/index.ts` | Browser SDK |
| `app/api/v1/analytics/ingest/route.ts` | Public ingest endpoint |
| `app/api/v1/analytics/users/route.ts` | Users list |
| `app/api/v1/analytics/users/[distinctId]/route.ts` | User timeline + GDPR purge |
| `app/api/v1/analytics/retention/route.ts` | Cohort retention endpoint |
| `app/api/v1/analytics/live/route.ts` | Live event feed |
| `components/admin/AnalyticsNav.tsx` | 6-tab nav shared across all analytics pages |

---

## Error reference

| HTTP | Cause |
|------|-------|
| 400 | Missing required fields, >50 events, invalid date format |
| 401 | Missing or wrong ingest key |
| 404 | Property/session/funnel/user not found |
| 422 | Funnel requires ≥2 steps |
| 429 | Rate limit exceeded (100 req/min per key) |

---

## Users API (P1)

### `GET /api/v1/analytics/users` — auth: admin

Query: `propertyId` (required), `limit` (max 500, default 200).

Returns aggregated user list from `product_events`:
```json
{ "users": [
    { "distinctId": "uuid", "userId": null,
      "firstSeen": "2026-04-01T...", "lastSeen": "2026-04-17T...", "eventCount": 42 }
  ], "total": 1 }
```

### `GET /api/v1/analytics/users/[distinctId]` — auth: admin

Query: `propertyId` (required), `limit` (max 2000, default 500).

Returns full event + session timeline:
```json
{ "distinctId": "uuid", "events": [...up to 2000 events...], "sessions": [...up to 50 sessions...] }
```

Returns 404 if no events found for this distinctId in this property.

### `DELETE /api/v1/analytics/users/[distinctId]` — auth: admin

Query: `propertyId` (required).

GDPR right-to-erasure. Paginated loop — deletes ALL events and sessions (not capped at 500). Batches in 490-doc chunks.

Response: `{ deleted: { events: N, sessions: M } }`

---

## Retention API (P1)

### `GET /api/v1/analytics/retention` — auth: admin

Query params:
- `propertyId` (required)
- `cohortEvent` — event that defines cohort entry (default `$pageview`)
- `returnEvent` — event that counts as a return (default `$pageview`)
- `from` / `to` — ISO date strings (both required)
- `granularity` — `day` or `week` (default `day`)

Response:
```json
{
  "result": {
    "granularity": "week",
    "cohortEvent": "signup",
    "returnEvent": "$pageview",
    "maxPeriods": 4,
    "rows": [
      {
        "cohortLabel": "2026-W14",
        "cohortStart": 1712707200000,
        "cohortSize": 87,
        "periods": [100, 62, 41, 28]
      }
    ]
  }
}
```

`periods[0]` is always 100. `null` means insufficient time has elapsed for that period (incomplete data).

**Retention compute rules:**
- Groups users by first occurrence of `cohortEvent` within `[from, to]`
- Cohort period = the day/week of their first cohort event
- Each period offset = days/weeks since cohort period start
- Week uses ISO 8601 Thursday-based year ownership
- Loads up to 20k events from Firestore (date-filtered at query level)

---

## Live API (P1)

### `GET /api/v1/analytics/live` — auth: admin

Query: `propertyId` (required).

Returns events from the last 5 minutes (max 100), newest first:
```json
{ "events": [...], "since": "2026-04-17T12:00:00.000Z" }
```

Admin UI polls this every 5 seconds. No WebSocket — Vercel-compatible polling approach.
