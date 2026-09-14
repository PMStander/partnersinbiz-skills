---
name: properties
description: >
  Properties module for Partners in Biz: create and manage deployed marketing sites or apps
  (e.g. scrolledbrain.com) that PiB tracks and controls. A Property holds runtime config
  (App Store URLs, Play Store URLs, kill switches, feature flags), an ingestKey for the
  analytics SDK, integration connections to revenue/ad networks, and a linked email sequence.
  Use this skill whenever the user mentions: "property", "properties", "micro-site",
  "ingest key", "rotate ingest key", "kill switch", "feature flags", "runtime config",
  "RevenueCat connection", "AdMob connection", "AdSense connection", "App Store Connect",
  "Play Console connection", "GA4 connection", "Google Ads connection",
  "Firebase Analytics connection", "integration", "connect provider", "pull metrics",
  "property config", "property domain", "property type", "web property", "ios property",
  "android property". If in doubt, trigger.
---

# Properties — Partners in Biz

Properties are the central registry for every deployed site or app PiB manages. Each Property
links the analytics SDK (via `ingestKey`), runtime config, and external revenue/ad integrations
into one record.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## Concepts

| Concept | Description |
|---------|-------------|
| **Property** | A deployed web, iOS, Android, or universal app PiB tracks (e.g. `scrolledbrain.com`) |
| **ingestKey** | 64-char hex string. The analytics SDK sends events with this key. Rotate if leaked. |
| **config** | Key-value blob served to the micro-site at runtime — App Store URL, Play Store URL, kill switch, feature flags, etc. Fetched by the site using only the ingestKey (no Bearer auth). |
| **connections** | Per-provider integration records (RevenueCat, AdMob, AdSense, GA4, Google Ads, App Store Connect, Play Console, Firebase Analytics). Each holds encrypted credentials and pulls daily metrics into the unified `metrics` collection. |

---

## Base URL & auth

```
Base: https://partnersinbiz.online/api/v1

Admin endpoints: Authorization: Bearer <pib_dlg_...> (interactive) or <AI_API_KEY> (cron/system only)
Public config:   x-pib-ingest-key: <ingestKey>   (no Bearer)
```

---

## Property CRUD

### `GET /api/v1/properties` — auth: admin

List all non-deleted properties for an org.

Query params:
- `orgId` (required)
- `status` — filter: `draft` | `active` | `paused` | `archived`
- `type` — filter: `web` | `ios` | `android` | `universal`
- `limit` — 1–200, default 50
- `offset` — default 0

Response:
```json
[
  {
    "id": "prop_abc",
    "orgId": "org_123",
    "name": "Scrolled Brain",
    "domain": "scrolledbrain.com",
    "type": "web",
    "status": "active",
    "config": {
      "siteUrl": "https://scrolledbrain.com",
      "killSwitch": false,
      "featureFlags": { "newOnboarding": true }
    },
    "conversionSequenceId": "seq_xyz",
    "emailSenderDomain": "scrolledbrain.com",
    "creatorLinkPrefix": "https://scrolledbrain.com/ref/",
    "ingestKey": "a1b2c3...",
    "ingestKeyRotatedAt": { "_seconds": 1713350400, "_nanoseconds": 0 },
    "createdAt": { "_seconds": 1713350400, "_nanoseconds": 0 },
    "createdBy": "user_abc",
    "createdByType": "user"
  }
]
```

---

### `POST /api/v1/properties` — auth: admin

Create a new property. An `ingestKey` is generated automatically.

Body:
```json
{
  "orgId": "org_123",
  "name": "Scrolled Brain",
  "domain": "scrolledbrain.com",
  "type": "web",
  "status": "draft",
  "config": {
    "siteUrl": "https://scrolledbrain.com",
    "appStoreUrl": "https://apps.apple.com/app/id1234567890",
    "playStoreUrl": "https://play.google.com/store/apps/details?id=com.example",
    "primaryCtaUrl": "https://scrolledbrain.com/download",
    "killSwitch": false,
    "featureFlags": { "newOnboarding": true },
    "revenue": {
      "currency": "USD",
      "timezone": "Africa/Johannesburg",
      "revenueCatProjectId": "rc_proj_abc",
      "revenueCatAppId": "rc_app_abc",
      "appStoreAppId": "1234567890",
      "playPackageName": "com.example.app",
      "ga4PropertyId": "123456789",
      "googleAdsCustomerId": "123-456-7890"
    }
  },
  "conversionSequenceId": "seq_xyz",
  "emailSenderDomain": "scrolledbrain.com",
  "creatorLinkPrefix": "https://scrolledbrain.com/ref/"
}
```

Required: `orgId`, `name`, `domain`, `type`.  
`status` defaults to `"draft"` if omitted.

Response (201): full property doc including generated `ingestKey`.

---

### `GET /api/v1/properties/:id` — auth: admin

Fetch a single property by ID.

Response: same shape as a list item.  
Returns 404 if not found or soft-deleted.

---

### `PUT /api/v1/properties/:id` — auth: admin

Update any combination of updatable fields. Omit fields you don't want to change.

Updatable fields: `name`, `domain`, `type`, `status`, `config`, `conversionSequenceId`,
`emailSenderDomain`, `creatorLinkPrefix`.

Body:
```json
{
  "status": "active",
  "config": {
    "killSwitch": false,
    "featureFlags": { "newOnboarding": true, "darkMode": false }
  }
}
```

Response: updated property doc.

---

### `DELETE /api/v1/properties/:id` — auth: admin

Soft-delete. Sets `deleted: true` and `status: "archived"`. Not reversible via API.

Response:
```json
{ "id": "prop_abc", "deleted": true }
```

---

## Public config endpoint

### `GET /api/v1/properties/:id/config` — auth: ingest-key only

Used by micro-sites to fetch their runtime config at boot. No Bearer token required.  
CDN-cached: `public, s-maxage=60, stale-while-revalidate=300`.

Header: `x-pib-ingest-key: <ingestKey>`

Normal response (200):
```json
{
  "siteUrl": "https://scrolledbrain.com",
  "appStoreUrl": "https://apps.apple.com/app/id1234567890",
  "playStoreUrl": "https://play.google.com/store/apps/details?id=com.example",
  "primaryCtaUrl": "https://scrolledbrain.com/download",
  "killSwitch": false,
  "featureFlags": { "newOnboarding": true },
  "revenue": { "currency": "USD", "timezone": "Africa/Johannesburg" }
}
```

Kill-switch active (503, `no-store`):
```json
{ "killSwitch": true, "message": "This site is temporarily unavailable." }
```

Note: when `config.killSwitch` is `true`, the response is 503 with `Cache-Control: no-store`
so CDN does not cache the outage state. Set it back to `false` to restore the site.

---

## Rotate ingest key

### `POST /api/v1/properties/:id/rotate-ingest-key` — auth: admin

Generates a new `ingestKey` and replaces the old one. The old key is immediately invalid.  
Deploy the new key to the micro-site before rotating if zero-downtime is required.

Response:
```json
{ "id": "prop_abc", "ingestKey": "new64hexstring..." }
```

---

## Property Analytics

All analytics endpoints accept `?propertyId=<id>` to scope results to a single property.

## Provider webhooks

These webhook routes live outside `/api/v1` because they are called directly by external providers:

- `POST /api/integrations/revenuecat/webhook/[propertyId]` — RevenueCat webhook receiver.
- `POST /api/integrations/play_console/webhook/[propertyId]` — Google Play Console webhook receiver.
Auth is `Authorization: Bearer $AI_API_KEY`. Base: `https://partnersinbiz.online`.

### `GET /api/v1/analytics/sessions?propertyId=<id>&limit=100` — auth: admin

Returns an array of session objects. Each session has fields:
`distinctId`, `device`, `country`, `referrer`, `eventCount`, `startedAt`, `lastActivityAt`.

```bash
curl -s "https://partnersinbiz.online/api/v1/analytics/sessions?propertyId=$PROPERTY_ID&limit=100" \
  -H "Authorization: Bearer $AI_API_KEY"
```

### `GET /api/v1/analytics/live?propertyId=<id>` — auth: admin

Live event stream — events from the last **5 minutes**, capped at **100 events**.

```bash
curl -s "https://partnersinbiz.online/api/v1/analytics/live?propertyId=$PROPERTY_ID" \
  -H "Authorization: Bearer $AI_API_KEY"
```

### `GET /api/v1/analytics/events?propertyId=<id>&limit=200&event=<optional>` — auth: admin

Raw events for a property. Pass `event=<name>` to filter to a single event type.

```bash
curl -s "https://partnersinbiz.online/api/v1/analytics/events?propertyId=$PROPERTY_ID&limit=200" \
  -H "Authorization: Bearer $AI_API_KEY"
```

### `GET /api/v1/analytics/users?propertyId=<id>` — auth: admin

Distinct users (by `distinctId`) seen for this property.

```bash
curl -s "https://partnersinbiz.online/api/v1/analytics/users?propertyId=$PROPERTY_ID" \
  -H "Authorization: Bearer $AI_API_KEY"
```

### Common queries

- **Sessions in the last 7 days** — fetch sessions and filter client-side:
  ```js
  const cutoff = Date.now() - 7 * 24 * 60 * 60 * 1000;
  const recent = sessions.filter(s => new Date(s.startedAt).getTime() >= cutoff);
  ```
- **Unique users in the last 7 days**:
  ```js
  const uniques = new Set(recent.map(s => s.distinctId)).size;
  ```
- **Conversion events** — use the events endpoint with an `event` filter:
  ```bash
  curl -s "https://partnersinbiz.online/api/v1/analytics/events?propertyId=$PROPERTY_ID&event=conversion&limit=200" \
    -H "Authorization: Bearer $AI_API_KEY"
  ```

---

## Conversion Sequence

A property can be linked to an email sequence via the `conversionSequenceId` field.
The sequence is what enrolled users go through when they hit a conversion event on this property.

### Linking a sequence

```bash
curl -s -X PUT "https://partnersinbiz.online/api/v1/properties/$PROPERTY_ID" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "conversionSequenceId": "seq_xyz" }'
```

### Unlinking

Pass `null` to detach:

```bash
curl -s -X PUT "https://partnersinbiz.online/api/v1/properties/$PROPERTY_ID" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "conversionSequenceId": null }'
```

### Reading the linked sequence + enrollment summary

There is no server-side aggregation endpoint yet — fetch both resources in parallel and
aggregate counts client-side:

```bash
curl -s "https://partnersinbiz.online/api/v1/sequences/$SEQUENCE_ID" \
  -H "Authorization: Bearer $AI_API_KEY"

curl -s "https://partnersinbiz.online/api/v1/sequence-enrollments?sequenceId=$SEQUENCE_ID" \
  -H "Authorization: Bearer $AI_API_KEY"
```

```js
const [sequence, enrollments] = await Promise.all([getSeq(id), getEnrollments(id)]);
const total = enrollments.length;
const active = enrollments.filter(e => e.status === "active").length;
const completed = enrollments.filter(e => e.status === "completed").length;
const summary = { sequence: sequence.name, total, active, completed };
```

---

## Creator Links

Creator/affiliate links can be attributed to a property via the `propertyId` field on each
link. This is the source of truth for attribution — the property's `creatorLinkPrefix` is
only a UX hint for naming new slugs.

### List links for a property

```bash
curl -s "https://partnersinbiz.online/api/v1/links?propertyId=$PROPERTY_ID&limit=100" \
  -H "Authorization: Bearer $AI_API_KEY"
```

### Create a link

`shortCode` is optional — a random one is generated if omitted, and slug clashes are
auto-retried on the server.

```bash
curl -s -X POST "https://partnersinbiz.online/api/v1/links" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "originalUrl": "https://scrolledbrain.com/download",
    "propertyId": "'"$PROPERTY_ID"'",
    "shortCode": "alex",
    "utmSource": "creator",
    "utmMedium": "social",
    "utmCampaign": "launch"
  }'
```

### Update a link

Accepts any subset of `{ propertyId, originalUrl, utmSource, utmMedium, utmCampaign, utmTerm, utmContent }`.
Pass `propertyId: null` to detach from the property.

```bash
curl -s -X PUT "https://partnersinbiz.online/api/v1/links/$LINK_ID" \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "utmCampaign": "spring-sale" }'
```

### Delete a link

```bash
curl -s -X DELETE "https://partnersinbiz.online/api/v1/links/$LINK_ID" \
  -H "Authorization: Bearer $AI_API_KEY"
```

The property's `creatorLinkPrefix` field is now a UX hint for naming new link slugs —
`propertyId` is the actual source of truth for attribution.

---

## Connections

Integration connections live under each property. Credentials are AES-256-GCM encrypted
at rest. The `credentialsEnc` field is never returned by the API — all responses replace it
with `hasCredentials: boolean`.

### Providers

| Provider | Auth kind | What it pulls |
|----------|-----------|---------------|
| `revenuecat` | `api_key` | MRR, ARR, active subscriptions, churn, subscription revenue |
| `admob` | `oauth2` | Ad requests, impressions, estimated earnings, CTR, RPM |
| `adsense` | `oauth2` | Page RPM, impressions, clicks, earnings |
| `app_store_connect` | `jwt` | Daily installs, IAP revenue, total revenue from Apple Sales Reports |
| `play_console` | `service_account` | Daily installs, uninstalls, IAP/subscription revenue, ratings |
| `google_ads` | `oauth2` | Spend, clicks, impressions, conversions |
| `ga4` | `oauth2` | Sessions, users, pageviews, engagement |
| `firebase_analytics` | `oauth2` | Firebase app analytics via the GA4 Data API (activeUsers, newUsers, screenPageViews, sessions). Thin GA4 alias — uses the Firebase-linked GA4 property (`firebaseAnalyticsPropertyId` in property config, falls back to `ga4PropertyId`). |

---

### `GET /api/v1/properties/:id/connections` — auth: admin

List all connections for a property.

Response:
```json
{
  "ok": true,
  "connections": [
    {
      "id": "revenuecat",
      "provider": "revenuecat",
      "propertyId": "prop_abc",
      "orgId": "org_123",
      "authKind": "api_key",
      "status": "connected",
      "hasCredentials": true,
      "meta": { "projectId": "rc_proj_abc", "appId": "rc_app_abc" },
      "scope": [],
      "lastPulledAt": null,
      "lastSuccessAt": null,
      "lastError": null,
      "consecutiveFailures": 0,
      "backfilledThrough": null,
      "createdAt": { "_seconds": 1713350400, "_nanoseconds": 0 },
      "updatedAt": { "_seconds": 1713350400, "_nanoseconds": 0 }
    }
  ]
}
```

---

### `GET /api/v1/properties/:id/connections/:provider` — auth: admin

Fetch a single connection. Returns 404 if not yet connected.

Response: `{ "ok": true, "connection": { ...same shape as above... } }`

---

### `PUT /api/v1/properties/:id/connections/:provider` — auth: admin

Connect or update a **non-OAuth** provider (API key, JWT, service account).  
OAuth providers (`admob`, `adsense`, `google_ads`, `ga4`, `firebase_analytics`) must use
the `/authorize` flow instead — this endpoint returns 400 for them.

Body:
```json
{
  "payload": { ...provider-specific shape... },
  "meta": { ...optional extra meta... }
}
```

**RevenueCat payload:**
```json
{
  "payload": {
    "apiKey": "sk_live_...",
    "projectId": "rc_proj_abc",
    "appId": "rc_app_abc",
    "webhookSecret": "whsec_..."
  }
}
```

**App Store Connect payload:**
```json
{
  "payload": {
    "keyId": "X9Y8Z7W6V5",
    "issuerId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
    "vendorNumber": "12345678"
  }
}
```

**Play Console payload:**
```json
{
  "payload": {
    "serviceAccountJson": "{\"type\":\"service_account\",...}",
    "packageName": "com.example.app"
  }
}
```

Response: `{ "ok": true, "connection": { ...connection doc, hasCredentials: true... } }`

---

### `PATCH /api/v1/properties/:id/connections/:provider` — auth: admin

Change connection status (pause/unpause/mark error).

Body:
```json
{ "status": "paused" }
```

Valid statuses: `connected` | `paused` | `reauth_required` | `error`

Response: `{ "ok": true }`

---

### `DELETE /api/v1/properties/:id/connections/:provider` — auth: admin

Disconnect a provider. Calls the adapter's `revoke` method if defined (e.g. for OAuth
token revocation), then deletes the connection record.

Response: `{ "ok": true }`

---

## OAuth connection flow

For OAuth providers (`admob`, `adsense`, `google_ads`, `ga4`, `firebase_analytics`):

### Step 1 — get authorize URL

`GET /api/v1/properties/:id/connections/:provider/authorize` — auth: admin

Response:
```json
{ "ok": true, "authorizeUrl": "https://accounts.google.com/o/oauth2/auth?..." }
```

Redirect the admin user to `authorizeUrl` in their browser.

### Step 2 — callback (handled automatically)

`GET /api/v1/properties/:id/connections/:provider/callback`

This is the OAuth redirect target. The platform handles CSRF state validation, code exchange,
and credential persistence. On success, redirects to:
```
/portal/properties/:id/connections?provider=<provider>&result=ok
```
On error:
```
/portal/properties/:id/connections?provider=<provider>&result=error&msg=<reason>
```

The state token is a 48-char hex nonce, stored in Firestore with a 10-minute TTL.

---

### `POST /api/v1/properties/:id/connections/:provider/pull` — auth: admin

Trigger a one-shot data pull for a connected provider. Useful for backfill, debugging,
or the admin "Refresh now" button. Times out after 60 seconds.

Response:
```json
{
  "ok": true,
  "from": "2026-05-06",
  "to": "2026-05-06",
  "metricsWritten": 12,
  "notes": ["Pulled 3 products, 12 rows"]
}
```

Returns 404 if the provider is not connected.

---

### `POST /api/v1/properties/:id/connections/:provider/backfill` — auth: admin

Backfill the last **90 days** of metrics for a connected provider in one call
(yesterday back to day-90, single ranged pull — GA4/AdMob/RevenueCat all accept
native date ranges). Idempotent: metrics upsert on deterministic doc ids, so
re-running overwrites instead of duplicating. Also exposed as the
"Backfill 90 days" button on the admin property connections page.

Response:
```json
{
  "ok": true,
  "from": "2026-04-03",
  "to": "2026-07-01",
  "metricsWritten": 1080,
  "notes": ["Pulled 90 days"]
}
```

Returns 404 if the provider is not connected, 501 if it has no pull adapter,
502 with `lastError` recorded when the provider call fails.

---

## Property config fields

### Top-level `config` fields

| Field | Type | Description |
|-------|------|-------------|
| `appStoreUrl` | string | Full App Store URL — served to micro-site and mobile deep links |
| `playStoreUrl` | string | Full Play Store URL |
| `primaryCtaUrl` | string | Primary CTA button target (download / signup) |
| `siteUrl` | string | Canonical site URL |
| `killSwitch` | boolean | `true` → site returns 503, CDN does not cache |
| `featureFlags` | `Record<string, boolean\|string>` | Arbitrary feature toggles for the micro-site |
| `customConfig` | `Record<string, unknown>` | Freeform key-value store for site-specific config |
| `revenue` | object | Integration identifiers and currency/timezone settings |

### `config.revenue` fields

| Field | Type | Description |
|-------|------|-------------|
| `currency` | `ZAR\|USD\|EUR\|GBP\|AUD\|CAD\|NZD\|JPY` | Invoiced/IAP/subscription currency |
| `timezone` | string | IANA timezone for daily metric bucketing (e.g. `Africa/Johannesburg`) |
| `adsenseClientId` | string | `ca-pub-XXXXXXXX` |
| `adsenseAdClient` | string | AdSense ad-client unit |
| `admobAppId` | string | `ca-app-pub-XXXX~YYYY` |
| `revenueCatProjectId` | string | RevenueCat org-level project id |
| `revenueCatAppId` | string | RevenueCat per-platform app id |
| `appStoreAppId` | string | Apple numeric app id, e.g. `1234567890` |
| `playPackageName` | string | Play package name, e.g. `com.example.app` |
| `googleAdsCustomerId` | string | Google Ads customer id `XXX-XXX-XXXX` |
| `ga4PropertyId` | string | GA4 numeric property id (no `properties/` prefix) |

---

## Property types and statuses

| Type | Use |
|------|-----|
| `web` | Marketing website / web app |
| `ios` | iOS mobile app |
| `android` | Android mobile app |
| `universal` | Multi-platform (web + mobile) |

| Status | Meaning |
|--------|---------|
| `draft` | Not yet live — default on create |
| `active` | Live and tracked |
| `paused` | Tracking suspended |
| `archived` | Soft-deleted |

---

## Practical examples

### Create a property for a new micro-site

```bash
POST /api/v1/properties
Authorization: Bearer $AI_API_KEY

{
  "orgId": "org_123",
  "name": "Scrolled Brain",
  "domain": "scrolledbrain.com",
  "type": "web",
  "config": {
    "siteUrl": "https://scrolledbrain.com",
    "killSwitch": false,
    "revenue": {
      "currency": "USD",
      "timezone": "Africa/Johannesburg"
    }
  }
}
```

Take the returned `id` and `ingestKey` and set them as env vars on the micro-site:
```
PIB_PROPERTY_ID=prop_abc
PIB_INGEST_KEY=a1b2c3...
```

The micro-site calls `/api/v1/properties/prop_abc/config` with `x-pib-ingest-key` to get
its runtime config on boot.

---

### Connect RevenueCat

```bash
PUT /api/v1/properties/prop_abc/connections/revenuecat
Authorization: Bearer $AI_API_KEY

{
  "payload": {
    "apiKey": "sk_live_...",
    "projectId": "rc_proj_abc",
    "appId": "rc_app_abc"
  }
}
```

Then trigger an immediate pull to verify the connection:

```bash
POST /api/v1/properties/prop_abc/connections/revenuecat/pull
Authorization: Bearer $AI_API_KEY
```

---

### Connect App Store Connect

```bash
PUT /api/v1/properties/prop_abc/connections/app_store_connect
Authorization: Bearer $AI_API_KEY

{
  "payload": {
    "keyId": "X9Y8Z7W6V5",
    "issuerId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
    "vendorNumber": "12345678"
  }
}
```

---

### Connect Play Console

```bash
PUT /api/v1/properties/prop_abc/connections/play_console
Authorization: Bearer $AI_API_KEY

{
  "payload": {
    "serviceAccountJson": "{\"type\":\"service_account\",\"project_id\":\"my-project\",...}",
    "packageName": "com.example.app"
  }
}
```

The service account needs **View Financial Data** and **View App Statistics** roles in
Google Play Console.

---

### Start OAuth flow for AdMob

```bash
GET /api/v1/properties/prop_abc/connections/admob/authorize
Authorization: Bearer $AI_API_KEY
```

Response includes `authorizeUrl`. Redirect the admin there. After consent, Google redirects
to the callback URL, which PiB handles automatically.

---

### Activate kill switch

```bash
PUT /api/v1/properties/prop_abc
Authorization: Bearer $AI_API_KEY

{
  "config": { "killSwitch": true }
}
```

The micro-site will start returning 503 within 60 seconds (CDN cache TTL).  
To restore, set `killSwitch: false`.

---

### Rotate ingest key after a leak

```bash
POST /api/v1/properties/prop_abc/rotate-ingest-key
Authorization: Bearer $AI_API_KEY
```

Returns the new `ingestKey`. Update it on the micro-site before rotating to avoid downtime.

---

## Key files

| File | Purpose |
|------|---------|
| `lib/properties/types.ts` | All shared types: `Property`, `PropertyConfig`, `PropertyRevenueConfig`, `CreatePropertyInput`, `UpdatePropertyInput` |
| `lib/integrations/types.ts` | `IntegrationAdapter`, `Connection`, `ALL_PROVIDERS`, `ConnectionStatus` |
| `lib/integrations/connections.ts` | `getConnection`, `upsertConnection`, `listConnectionsForProperty`, `setConnectionStatus`, `deleteConnection` |
| `lib/integrations/registry.ts` | `registerAdapter`, `getAdapter` |
| `lib/integrations/dispatch.ts` | `dispatchOne` — used by the pull endpoint |
| `lib/integrations/crypto.ts` | AES-256-GCM credential encryption |
| `lib/properties/ingest-key.ts` | `generateIngestKey` — 64-char random hex |
| `app/api/v1/properties/route.ts` | List + create |
| `app/api/v1/properties/[id]/route.ts` | Get, update, delete |
| `app/api/v1/properties/[id]/config/route.ts` | Public config endpoint |
| `app/api/v1/properties/[id]/rotate-ingest-key/route.ts` | Ingest key rotation |
| `app/api/v1/properties/[id]/connections/route.ts` | List connections |
| `app/api/v1/properties/[id]/connections/[provider]/route.ts` | Get, upsert, patch, delete connection |
| `app/api/v1/properties/[id]/connections/[provider]/authorize/route.ts` | Begin OAuth |
| `app/api/v1/properties/[id]/connections/[provider]/callback/route.ts` | OAuth callback |
| `app/api/v1/properties/[id]/connections/[provider]/pull/route.ts` | Manual data pull |

---

## Error reference

| HTTP | Cause |
|------|-------|
| 400 | Missing required field, invalid `type` or `status` value, OAuth provider sent to PUT, non-OAuth provider sent to `/authorize` |
| 401 | Missing or wrong `x-pib-ingest-key` on `/config` |
| 404 | Property or connection not found (or soft-deleted) |
| 501 | Provider adapter not registered |
| 503 | Property kill switch is active |

---

## Firestore structure

```
properties/{propertyId}                — Property doc
properties/{propertyId}/connections/{provider}  — Connection sub-collection
oauth_state/{state}                    — Short-lived OAuth CSRF tokens (10-min TTL)
```

All collections use Admin SDK only. `allow read, write: if false` in `firestore.rules`.
