---
name: ads-manager
description: |
  Manage paid advertising campaigns across Meta, Google, LinkedIn, and TikTok
  through the Partners in Biz platform API. Connect ad accounts, build
  campaigns / ad sets / ads, manage custom + saved audiences (5 subtypes per
  platform), upload creatives (images + videos), pull insights at any level
  (campaign/adset/ad) with cross-platform breakdowns, configure pixels +
  Conversions API for server-side event tracking, set cross-platform budget
  caps with pacing + auto-pause, and run A/B experiments with statistical
  significance + auto-winner declaration. Use this skill whenever the user
  mentions anything related to paid ads or media buying, including but not
  limited to: "create an ad campaign", "launch a campaign on Meta", "run
  Facebook ads", "Instagram ads", "Google Ads", "LinkedIn ads", "TikTok
  ads", "create a custom audience", "upload customer list", "lookalike
  audience", "retargeting audience", "create a Performance Max campaign",
  "YouTube TrueView", "Smart Shopping", "upload conversion data", "set up
  pixel", "Conversions API", "CAPI", "server-side tracking", "send
  conversion event", "set a budget", "monthly ad spend cap", "pace my
  spend", "auto-pause when exhausted", "spend alert", "ROAS report", "ad
  insights", "campaign performance", "compare creatives", "A/B test",
  "split test", "experiment", "winner declaration", "approve ad",
  "client approval", "submit for review", "ad-review queue", "ads pending
  approval", "pause ad", "resume campaign", "archive ad set", "import
  offline conversions", "bulk CSV conversions", "connect ad account",
  "disconnect ad account", "Meta Ads", "Google Ads", "LinkedIn Campaign
  Manager", "TikTok For Business", "ad account OAuth", "ad creative upload",
  "video ad", "image ad", "responsive search ad", "display ad", "keyword
  targeting", "conversion tracking", "Insight Tag", "LinkedIn matched
  audience", "TikTok pixel", "Meta pixel", "Google tag", "remarketing list",
  "customer match", "engagement audience", "app audience", "website
  audience", "budget cap", "pacing alert", "daily budget", "monthly budget",
  "campaign budget", "platform cap", "org-wide cap", "auto-resume on
  rollover", "experiment significance", "test variant", "control group",
  "declare winner", "auto-winner", "ad comment", "bulk approve ads",
  "push notification ads", "activity feed ads". If in doubt, trigger.
---

# ads-manager — Partners in Biz Platform API

You are the agent's interface to the PiB ads module. The platform spans 4 ad networks (Meta, Google, LinkedIn, TikTok) with a unified canonical model + per-platform extensions. All endpoints live under `https://partnersinbiz.online/api/v1/`.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## Quick reference

**Auth:** interactive runs use the user-delegation Bearer token (`pib_dlg_…`) + `X-Org-Id: <orgId>` (see `## Auth (mandatory)` above); `Authorization: Bearer <AI_API_KEY>` + `X-Org-Id: <orgId>` is cron/system only.

**Envelope:** all responses follow `{ success, data }` or `{ success, error }`. Unwrap with:
```javascript
const body = await res.json();
if (!body.success) throw new Error(body.error);
const data = body.data ?? body;
```

**Base URL:** `https://partnersinbiz.online/api/v1`

**AI_API_KEY:** read from `process.env.AI_API_KEY`. Get current value from Vercel dashboard → project `partnersinbiz-web` → Settings → Environment Variables if 401s start appearing.

---

## Known Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Missing `X-Org-Id` | `"X-Org-Id header is required for AI agent requests"` | Add header to every call |
| Multi-step flows — ID not persisted | 404 on adset/ad create | Capture `data.id` from each step and pass to the next |
| LinkedIn APP audience | 400 "not supported" | LinkedIn has no native APP audience equivalent — use WEBSITE or ENGAGEMENT instead |
| CAPI tokens in response | Masked / not returned | `capiTokenEnc` stored encrypted; only masked state shown in admin UI |
| Currency is cents | `capCents: 100000` = $1000 | All budget amounts are integer cents |
| Firestore indexes | 25+ pending `firebase deploy --only firestore:indexes` | Some list queries may be slow until deployed |
| Cron endpoints | 401 if `CRON_SECRET` not set | Set `CRON_SECRET` env var in Vercel; pass as `?secret=<CRON_SECRET>` |

---

## Supported Ad Networks

| Network | OAuth Env Vars | Status |
|---|---|---|
| Meta | `META_APP_ID`, `META_APP_SECRET` | Connected; App Review pending for `ads_management` scope |
| Google | `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_DEVELOPER_TOKEN` | Connected; dev token write access pending for prod |
| LinkedIn | `LINKEDIN_ADS_CLIENT_ID`, `LINKEDIN_ADS_CLIENT_SECRET` | LMDP application pending |
| TikTok | `TIKTOK_ADS_CLIENT_ID`, `TIKTOK_ADS_CLIENT_SECRET` | TFB Marketing API app pending |

---

## 1. Connections (per-platform OAuth)

```
GET    /api/v1/ads/connections                                — list all connections for org
POST   /api/v1/ads/connections/[platform]/authorize          — start OAuth; returns { authorizeUrl }
DELETE /api/v1/ads/connections/[platform]                    — disconnect
```

`[platform]` = `meta` | `google` | `linkedin` | `tiktok`

**Post-OAuth account picker** (admin must call after callback):
```
GET   /api/v1/ads/google/customers?connectionId=...          — list Google customer accounts
GET   /api/v1/ads/linkedin/accounts?connectionId=...         — list LinkedIn ad accounts
GET   /api/v1/ads/tiktok/accounts?connectionId=...           — list TikTok advertiser accounts

PATCH /api/v1/ads/google/connections/[id]/customer           { "loginCustomerId": "..." }
PATCH /api/v1/ads/linkedin/connections/[id]/account          { "selectedAdAccountUrn": "urn:li:sponsoredAccount:..." }
PATCH /api/v1/ads/tiktok/connections/[id]/account            { "selectedAdvertiserId": "..." }
```

Meta: account ready immediately after callback — no picker step needed.

**Google connect — use the Google-namespaced OAuth routes** (the admin UI does this):
```
POST  /api/v1/ads/google/oauth/authorize                     — returns { authorizeUrl }
GET   /api/v1/ads/google/oauth/callback                      — handled automatically
GET   /api/v1/ads/google/customers?connectionId=...          — picker (existing accounts)
PATCH /api/v1/ads/google/connections/[id]/customer           — select the customer/MCC
```
The generic `POST /api/v1/ads/connections/google/authorize` also works (the
`googleProvider` is wired, not a stub), but the Google-namespaced routes are
canonical because they surface developer-token/customer errors to the operator.

**Create a NEW subaccount under the MCC** (when the client's account does not
exist yet — `customers:createCustomerClient`, distinct from the discovery picker):
```
POST  /api/v1/ads/google/connections/[id]/create-client
      { "descriptiveName": "AHS Law", "currencyCode": "ZAR", "timeZone": "Africa/Johannesburg", "managerCustomerId"?: "..." }
      → { resourceName, customerId, managerCustomerId }
```
`managerCustomerId` defaults to the connection's `loginCustomerId` / selected
customer. After creation, select the returned `customerId` via the customer PATCH
above. Requires a connected MCC + a developer token with write access.

---

## 2. Campaign Hierarchy

PiB uses a canonical 3-tier model. Platform-specific entity names:

| PiB canonical | Meta | Google | LinkedIn | TikTok |
|---|---|---|---|---|
| Campaign | Campaign | Campaign | Campaign Group | Campaign |
| AdSet | AdSet | AdGroup | Campaign | AdGroup |
| Ad | Ad | Ad (RSA/RDA/Video) | Creative | Ad |

All routes dispatch by `body.platform`. Multi-step: persist `id` from each response before calling the next tier.

### Campaigns

```
GET    /api/v1/ads/campaigns                                  — list (query: orgId, platform, status)
POST   /api/v1/ads/campaigns                                  — create
GET    /api/v1/ads/campaigns/[id]                             — get one
PATCH  /api/v1/ads/campaigns/[id]                             — update
DELETE /api/v1/ads/campaigns/[id]                             — archive
POST   /api/v1/ads/campaigns/[id]/launch                      — flip ACTIVE locally + remote
POST   /api/v1/ads/campaigns/[id]/pause                       — pause (best-effort remote sync)
POST   /api/v1/ads/campaigns/[id]/submit-for-review           — flip reviewState → 'awaiting' (portal approval)
```

**Campaign body — required per platform:**
- All: `{ orgId, name, platform, objective? }`
- Google extra: `{ googleAds: { campaignType: 'SEARCH'|'DISPLAY'|'SHOPPING'|'VIDEO'|'PERFORMANCE_MAX'|'SMART_SHOPPING', dailyBudgetMajor?, networkSettings?, targetingExpansion? } }`
- LinkedIn extra: `{ linkedinAds: { totalBudgetMajor?, currencyCode? } }` (campaign group level)
- TikTok extra: `{ tiktokAds: { budgetMajor?, budgetMode? } }`

### AdSets

```
GET    /api/v1/ads/ad-sets                                    — list (query: campaignId)
POST   /api/v1/ads/ad-sets                                    — create
GET    /api/v1/ads/ad-sets/[id]
PATCH  /api/v1/ads/ad-sets/[id]
DELETE /api/v1/ads/ad-sets/[id]
```

**AdSet body — required per platform:**
- Google extra: `{ googleAds: { cpcBidMajor?, targetCpa?, targetRoas? } }`
- LinkedIn extra: `{ linkedinAds: { campaignType?, costType?, dailyBudgetMajor? } }` (LinkedIn campaign level)
- TikTok extra: `{ tiktokAds: { optimizationGoal?, billingEvent?, bidType?, bidMajor?, startTime?, endTime?, targeting?: { locations[], ageGroups[], genders[], interests[] } } }`

### Ads

```
GET    /api/v1/ads/ads                                        — list (query: adSetId)
POST   /api/v1/ads/ads                                        — create
GET    /api/v1/ads/ads/[id]
PATCH  /api/v1/ads/ads/[id]
DELETE /api/v1/ads/ads/[id]
```

**Ad body — required per platform:**
- Meta: canonical fields + `creativeId` (from creatives endpoint)
- Google: `{ googleAds: { type: 'RESPONSIVE_SEARCH'|'RESPONSIVE_DISPLAY'|'VIDEO', headlines?, descriptions?, finalUrls? } }`
- LinkedIn: `{ linkedinAds: { referenceUrn: 'urn:li:ugcPost:...' } }` — required; the Share URN of the creative
- TikTok: `{ tiktokAds: { identityId, identityType, adText, callToAction, landingPageUrl, imageIds?: [], videoId?: string } }` — all required

---

## 3. Creatives

Canonical asset store in Firebase Storage at `orgs/{orgId}/ad_creatives/{id}/source.{ext}`. Per-platform sync is separate.

```
GET    /api/v1/ads/creatives                                  — list (query: orgId, platform)
POST   /api/v1/ads/creatives                                  — create canonical creative record
GET    /api/v1/ads/creatives/[id]
DELETE /api/v1/ads/creatives/[id]

POST   /api/v1/ads/creatives/[id]/sync/meta                   — push creative to Meta (returns adImageHash / adVideoId)
POST   /api/v1/ads/tiktok/creatives/upload                    — multipart upload to TikTok (image/video); returns { assetId }
POST   /api/v1/ads/google/video-assets                        — { youtubeVideoId } → create YouTube video asset in Google Ads
```

LinkedIn uses Firebase Storage-resident assets referenced via Share URN — upload the asset to Firebase Storage first, then use the storage URL as the `referenceUrn` input when creating ads.

---

## 4. Custom Audiences (5 subtypes per platform)

PiB unified subtypes: `CUSTOMER_LIST` | `WEBSITE` | `LOOKALIKE` | `APP` | `ENGAGEMENT`

```
GET    /api/v1/ads/custom-audiences                           — list (query: orgId, platform, type)
POST   /api/v1/ads/custom-audiences                          — create (body.platform dispatches)
GET    /api/v1/ads/custom-audiences/[id]
DELETE /api/v1/ads/custom-audiences/[id]                     — archive + cascade-delete platform-side

POST   /api/v1/ads/custom-audiences/[id]/upload-list         — multipart CSV (raw email/phone — server SHA-256 hashes per platform)
POST   /api/v1/ads/custom-audiences/[id]/sync/[platform]     — push audience to a specific platform (meta|google|linkedin|tiktok)
POST   /api/v1/ads/custom-audiences/[id]/refresh-size        — pull approximate member count from platform
```

**Saved targeting templates** (reusable across campaigns):
```
GET    /api/v1/ads/saved-audiences                           — list
POST   /api/v1/ads/saved-audiences                          — create template
GET    /api/v1/ads/saved-audiences/[id]
PATCH  /api/v1/ads/saved-audiences/[id]
DELETE /api/v1/ads/saved-audiences/[id]
```

**Platform notes:**
- LinkedIn APP type: returns 400 — no native equivalent. Use WEBSITE or ENGAGEMENT instead.
- CUSTOMER_LIST CSV: columns `email` and/or `phone` (raw — API hashes). `external_id` optional.
- LOOKALIKE: requires an existing `sourceAudienceId` and `country` in the body.
- WEBSITE: requires pixel configured (see Section 7) before the audience can populate.

---

## 5. Insights (cross-platform metrics)

```
GET    /api/v1/ads/insights                                  — query metrics collection
       query params: platform, level (campaign|adset|ad), entityId, since (YYYY-MM-DD), until (YYYY-MM-DD)

POST   /api/v1/ads/insights/refresh                          — manual refresh pull
       body: { platform, level, entityId, daysBack? }

GET    /api/v1/ads/cron/daily-insights-pull                  — auto-runs 00:30 UTC daily (pass ?secret=<CRON_SECRET>)
```

**Metrics Firestore shape:**
```
{ orgId, source: '{platform}_ads', level, dimensionId, date, metric, value }
```

**Common metrics:** `impressions`, `clicks`, `spend_cents`, `conversions`, `ctr`, `cpc_cents`, `cpm_cents`, `reach`, `landing_page_clicks`, `video_views`

**ROAS:** compute as `conversions_value_cents / spend_cents` client-side; not stored as a single metric.

---

## 6. Conversions API (cross-platform fanout)

### Conversion Actions (configuration)

```
GET    /api/v1/ads/conversion-actions                        — list for org
POST   /api/v1/ads/conversion-actions                        — create canonical conversion action
GET    /api/v1/ads/conversion-actions/[id]
PATCH  /api/v1/ads/conversion-actions/[id]
DELETE /api/v1/ads/conversion-actions/[id]
```

### Real-time event tracking

```
POST   /api/v1/ads/conversions/track
```

Body (`ConversionEventInput`):
```json
{
  "orgId": "org_abc123",
  "conversionActionId": "ca_xyz",
  "eventId": "unique-dedupe-id",
  "eventTime": "2026-05-18T10:00:00Z",
  "user": {
    "email": "user@example.com",
    "phone": "+27821234567",
    "firstName": "Jane",
    "lastName": "Smith",
    "externalId": "crm_123",
    "countryCode": "ZA",
    "postalCode": "4000"
  },
  "value": 99.99,
  "currency": "ZAR",
  "gclid": "...",
  "ttclid": "...",
  "liFatId": "..."
}
```

Response: `{ meta?, google?, linkedin?, tiktok? }` — each field is `'sent'|'failed'|'skipped'` per platform.

Deduplication: `eventId` stored as Firestore doc ID in `ad_conversion_events` — idempotent on retry.

### Offline conversions (bulk CSV)

```
POST   /api/v1/ads/conversions/offline/upload                — multipart: file (CSV) + conversionActionId
GET    /api/v1/ads/conversions/offline/batches               — list batches (query: orgId)
GET    /api/v1/ads/conversions/offline/batches/[id]          — single batch + first 100 rows
POST   /api/v1/ads/conversions/offline/batches/[id]/process  — run batch (streams per-row fanout)
POST   /api/v1/ads/conversions/offline/batches/[id]/retry-failed
```

**CSV column format:**

| Column | Required | Notes |
|---|---|---|
| `event_id` | Yes | Unique per row — deduplication key |
| `event_time_iso` | Yes | ISO 8601 timestamp |
| `email` OR `phone` | One required | Raw — API hashes server-side |
| `value` | No | Decimal, e.g. `99.99` |
| `currency` | No | ISO 4217, e.g. `ZAR` |
| `gclid` | No | Google click ID |
| `ttclid` | No | TikTok click ID |
| `li_fat_id` | No | LinkedIn first-party ad tracking ID |

---

## 7. Pixel Configs (per-platform pixel + CAPI token)

```
GET    /api/v1/ads/pixel-configs                             — list (query: orgId)
GET    /api/v1/ads/pixel-configs/[id]
PATCH  /api/v1/ads/pixel-configs/[id]                       — admin sets pixel + CAPI token
```

**PATCH body** — per-platform fields (all optional; only set what you're configuring):
```json
{
  "meta":     { "pixelId": "1234567890", "capiToken": "EAABwzLixnjYBO...", "testEventCode": "TEST12345" },
  "google":   { "pixelId": "AW-XXXXXXXXXXX/XXXXXXXXXXXXXXXX", "capiToken": null },
  "linkedin": { "pixelId": "1234567", "capiToken": null },
  "tiktok":   { "pixelId": "ABCDE12345", "capiToken": "xxxxxxxxxxxxxxxx" }
}
```

`capiToken` is plaintext on input — encrypted via `SOCIAL_TOKEN_MASTER_KEY` at rest. Never log or expose it. Only masked state is shown in admin UI responses.

---

## 8. Budgets (Sub-4)

```
GET    /api/v1/ads/budgets                                   — list (query: orgId, platform, scope)
POST   /api/v1/ads/budgets                                   — create
GET    /api/v1/ads/budgets/[id]
PATCH  /api/v1/ads/budgets/[id]
DELETE /api/v1/ads/budgets/[id]

POST   /api/v1/ads/budgets/[id]/check                        — manual pacing check
POST   /api/v1/ads/budgets/[id]/reset                        — manual period reset (month rollover etc.)

GET    /api/v1/ads/cron/budget-pacing-check                  — recommend every 6h (pass ?secret=<CRON_SECRET>)
```

**Create body:**
```json
{
  "input": {
    "name": "Q3 Meta cap",
    "scope": "org",
    "platform": "meta",
    "campaignId": "camp_xyz",
    "capCents": 500000,
    "currencyCode": "USD",
    "period": "monthly",
    "alertThresholds": [75, 90, 100],
    "autoPause": true,
    "autoResumeOnRollover": true
  }
}
```

**Field rules:**
- `scope`: `org` | `platform` | `campaign`
- `platform`: required when `scope != 'org'`
- `campaignId`: required when `scope == 'campaign'`
- `capCents`: integer cents (e.g. 500000 = $5,000)
- `period`: `daily` | `weekly` | `monthly`
- `alertThresholds`: array of % integers — fires notification at each threshold
- `autoPause`: pauses all matching campaigns when 100% reached
- `autoResumeOnRollover`: resumes at period start if paused by autoPause

**Pacing logic:** cron checks spend-to-date against capCents × (elapsed-days / period-days). Sends push notification at each alert threshold. Auto-pauses if `autoPause: true` and spend ≥ capCents.

---

## 9. Experiments / A/B Testing (Sub-5)

```
GET    /api/v1/ads/experiments                               — list (query: orgId, platform, status)
POST   /api/v1/ads/experiments                               — create
GET    /api/v1/ads/experiments/[id]
PATCH  /api/v1/ads/experiments/[id]
DELETE /api/v1/ads/experiments/[id]

POST   /api/v1/ads/experiments/[id]/start                    — duplicates source entity per variant
POST   /api/v1/ads/experiments/[id]/stop
POST   /api/v1/ads/experiments/[id]/compute                  — recompute significance now
POST   /api/v1/ads/experiments/[id]/declare-winner           — body: { variantId? } (omit = auto-pick)
       → pauses non-winning entities + flips status to 'completed'

GET    /api/v1/ads/cron/experiment-significance-check        — recommend every 6h (pass ?secret=<CRON_SECRET>)
```

**Create body:**
```json
{
  "input": {
    "name": "Headline A/B test",
    "level": "ad",
    "parentEntityId": "adset_abc",
    "sourceEntityId": "ad_xyz",
    "platform": "meta",
    "variants": [
      { "id": "a", "name": "Control", "trafficPercent": 50 },
      { "id": "b", "name": "New headline", "trafficPercent": 50, "overrides": { "name": "New Headline Ad" } }
    ],
    "successMetric": "ctr",
    "minDays": 7,
    "significanceThreshold": 0.05,
    "autoWinner": false
  }
}
```

**Field rules:**
- `level`: `adset` | `ad`
- `successMetric`: `cpc` | `cpa` | `conv_rate` | `ctr` | `roas`
- `variants[].trafficPercent`: must sum to 100
- `variants[].overrides`: partial entity body to diff from source (e.g. `{ name, tiktokAds: { adText: '...' } }`)
- `autoWinner`: if `true`, cron auto-declares winner once significance reached + `minDays` elapsed
- `significanceThreshold`: p-value threshold (default 0.05 = 95% confidence)

**On `start`:** platform entities are duplicated for each variant; traffic split applied. Significance is computed via z-test on conversion rate (or metric equivalent).

---

## 10. Portal Approval Workflow (Sub-2/2b)

### Admin side

```
POST   /api/v1/ads/campaigns/[id]/submit-for-review          — reviewState: 'awaiting'
```

Admin creates and configures campaigns, then submits for client review. Client sees campaigns at `/portal/ads/campaigns/[id]`.

### Client portal endpoints

```
POST   /api/v1/portal/ads/campaigns/[id]/approve             — client approves → returns to admin to launch
POST   /api/v1/portal/ads/campaigns/[id]/reject              — body: { reason } → flips back to DRAFT
POST   /api/v1/portal/ads/campaigns/bulk-approve              — body: { campaignIds: ['camp_a', 'camp_b'] }
```

### Per-ad comments + notifications

Comments are portal-scoped — only authenticated portal users (clients) can post/edit/delete.
```
GET    /api/v1/portal/ads/ads/[id]/comments                 — list threaded comments
POST   /api/v1/portal/ads/ads/[id]/comments                 — body: { text, anchor? }
PATCH  /api/v1/portal/ads/ads/[id]/comments/[commentId]     — edit comment text
DELETE /api/v1/portal/ads/ads/[id]/comments/[commentId]     — delete comment
```

Push notifications are fanned out per-event (submit, approve, reject, comment) to all org members with the relevant role.

---

## 11. Activity Feed

All ad module activity writes to the `activity` Firestore collection (singular) with field `type` (NOT `kind`).

**Ad activity type prefixes:**
- `ad_campaign.*` — campaign lifecycle events
- `ad_set.*` — adset events
- `ad.*` — ad events
- `ad_creative.*` — creative upload/sync events
- `ad_custom_audience.*` — audience create/upload/refresh events

Activity is surfaced in the admin dashboard activity feed. No direct write endpoint — these are emitted server-side by the API routes.

---

## Workflow Guides

### A. Connect an ad account end-to-end (Meta example)

```
1. POST /api/v1/ads/connections/meta/authorize           → { authorizeUrl }
2. Redirect user to authorizeUrl (browser required — OAuth flow)
3. Platform redirects to callback (handled automatically)
4. GET  /api/v1/ads/connections                          → confirm meta connection active
```

Google/LinkedIn/TikTok add a picker step after step 3 — call the `GET /customers|/accounts` endpoint then the `PATCH /connections/[id]/customer|/account` endpoint to select the ad account.

### B. Create a full Meta campaign → AdSet → Ad

```
1. POST /api/v1/ads/campaigns   { platform: 'meta', name: '...', objective: 'LINK_CLICKS' }
   → { id: 'camp_abc' }

2. POST /api/v1/ads/ad-sets    { platform: 'meta', campaignId: 'camp_abc', name: '...', dailyBudgetMajor: 50, targeting: {...} }
   → { id: 'adset_xyz' }

3. POST /api/v1/ads/creatives  { orgId, name, file (upload) }   or use existing creativeId
   POST /api/v1/ads/creatives/[id]/sync/meta                    → { adImageHash }

4. POST /api/v1/ads/ads        { platform: 'meta', adSetId: 'adset_xyz', creativeId: 'cre_abc', headline: '...', description: '...' }
   → { id: 'ad_123' }

5. POST /api/v1/ads/campaigns/camp_abc/launch                   → campaign goes ACTIVE
```

### C. Upload a customer list + create lookalike audience

```
1. POST /api/v1/ads/custom-audiences  { platform: 'meta', type: 'CUSTOMER_LIST', name: 'Existing Customers' }
   → { id: 'aud_abc' }

2. POST /api/v1/ads/custom-audiences/aud_abc/upload-list
   multipart: file=@customers.csv
   CSV columns: email, phone (raw — API hashes SHA-256)

3. POST /api/v1/ads/custom-audiences/aud_abc/refresh-size       → { approximateCount: 12500 }

4. POST /api/v1/ads/custom-audiences  { platform: 'meta', type: 'LOOKALIKE', name: '1% Lookalike', sourceAudienceId: 'aud_abc', country: 'ZA', ratio: 0.01 }
   → { id: 'aud_lal' }
```

### D. Set up conversion tracking + server-side events

```
1. PATCH /api/v1/ads/pixel-configs/[id]
   { meta: { pixelId: '1234567890', capiToken: 'EAABwz...' } }

2. POST /api/v1/ads/conversion-actions
   { orgId, name: 'Purchase', platform: 'meta', eventType: 'PURCHASE', value: true }
   → { id: 'ca_xyz' }

3. POST /api/v1/ads/conversions/track
   { orgId, conversionActionId: 'ca_xyz', eventId: uuid(), eventTime: now(), user: { email, phone }, value: 99.99, currency: 'ZAR' }
   → { meta: 'sent', google: 'skipped', linkedin: 'skipped', tiktok: 'skipped' }
```

### E. Set a monthly budget cap with auto-pause

```
1. POST /api/v1/ads/budgets
   { input: { name: 'Monthly Meta Cap', scope: 'platform', platform: 'meta', capCents: 1000000, period: 'monthly', alertThresholds: [75, 90, 100], autoPause: true, autoResumeOnRollover: true } }
   → { id: 'bud_abc' }

2. GET /api/v1/ads/cron/budget-pacing-check?secret=<CRON_SECRET>   — trigger manually to test
   (Vercel cron runs this every 6h automatically when wired)
```

### F. Run an A/B experiment with auto-winner

```
1. POST /api/v1/ads/experiments
   { input: { name: 'Headline test', level: 'ad', parentEntityId: 'adset_abc', sourceEntityId: 'ad_xyz',
     platform: 'meta', variants: [{id:'a', name:'Control', trafficPercent:50}, {id:'b', name:'New', trafficPercent:50, overrides:{...}}],
     successMetric: 'ctr', minDays: 7, significanceThreshold: 0.05, autoWinner: true } }
   → { id: 'exp_abc' }

2. POST /api/v1/ads/experiments/exp_abc/start    — duplicates ad per variant, applies traffic split

3. (Wait minDays — cron checks significance every 6h)

4. POST /api/v1/ads/experiments/exp_abc/compute  — manual significance check at any time
   → { significanceReached: true, winner: { variantId: 'b', metric: 'ctr', pValue: 0.021 } }

5. POST /api/v1/ads/experiments/exp_abc/declare-winner  { variantId: 'b' }
   → non-winning variant paused, experiment status: 'completed'
```

### G. Upload offline conversions from CRM export

```
1. POST /api/v1/ads/conversions/offline/upload
   multipart: file=@crm_export.csv, conversionActionId=ca_xyz
   → { batchId: 'batch_abc', rowCount: 500 }

2. POST /api/v1/ads/conversions/offline/batches/batch_abc/process
   → streams per-row fanout; check batch status for failures

3. GET  /api/v1/ads/conversions/offline/batches/batch_abc
   → { processed: 498, failed: 2, rows: [...first 100] }

4. POST /api/v1/ads/conversions/offline/batches/batch_abc/retry-failed
   → retries 2 failed rows
```

### H. Portal approval flow (admin → client → launch)

```
1. Admin builds campaign (create → adsets → ads → creatives)
2. POST /api/v1/ads/campaigns/[id]/submit-for-review        — reviewState: 'awaiting'
3. Client sees campaign at /portal/ads/campaigns/[id]
4. Client POST /api/v1/portal/ads/campaigns/[id]/approve    — OR reject with { reason }
5. Admin receives notification + launches: POST /api/v1/ads/campaigns/[id]/launch
```

---

## Google Ads — Campaign Types

| Type | Use case | Key extra fields |
|---|---|---|
| `SEARCH` | Keyword-targeted text ads (RSA) | `headlines[]`, `descriptions[]`, `finalUrls[]`, keywords |
| `DISPLAY` | Image/responsive display on GDN | `marketingImages[]`, `headlines[]`, `descriptions[]` |
| `SHOPPING` | Product listing ads (Merchant Center) | `merchantCenterAccountId`, `campaignPriority` |
| `VIDEO` | YouTube TrueView in-stream / discovery | `youtubeVideoId`, `adFormat` |
| `PERFORMANCE_MAX` | All Google inventory, ML-optimised | asset group — all creative assets together |
| `SMART_SHOPPING` | Automated Shopping (legacy) | `merchantCenterAccountId` |

Merchant Center endpoints:
```
GET    /api/v1/ads/google/merchant-center/accounts?connectionId=...
POST   /api/v1/ads/google/merchant-center/link                      — { merchantCenterAccountId }
POST   /api/v1/ads/google/merchant-center/product-feed/sync         — trigger feed refresh
```

Keyword management:
```
GET    /api/v1/ads/keywords?adGroupId=...
POST   /api/v1/ads/keywords                 — { keywords: [{ text, matchType: 'BROAD'|'PHRASE'|'EXACT' }] }
PATCH  /api/v1/ads/keywords/[id]
DELETE /api/v1/ads/keywords/[id]
```

---

## Cron Schedule (Peet to wire in Vercel)

| Cron endpoint | Recommended cadence | Purpose |
|---|---|---|
| `/api/v1/ads/cron/daily-insights-pull` | `0 0 30 * * *` (00:30 UTC daily) | Pull metrics from all 4 platforms |
| `/api/v1/ads/cron/budget-pacing-check` | Every 6h | Check spend vs caps, alert, auto-pause |
| `/api/v1/ads/cron/experiment-significance-check` | Every 6h | Compute p-values, auto-declare winner |

All crons require `?secret=<CRON_SECRET>` query param. Set `CRON_SECRET` env var in Vercel.

---

## Conventions you must follow

1. **Always set `X-Org-Id`** from the active workspace org — omitting it returns 401.
2. **Unwrap all responses** — `body.data ?? body` after checking `body.success`.
3. **Multi-step flows** — capture `id` from each create response and pass to the next tier. Never assume IDs.
4. **Audience CSV** — pass raw email/phone. The API hashes SHA-256 + formats per platform. Do not pre-hash.
5. **Budgets in cents** — all `capCents`, `dailyBudgetMajor` (when in cents), `value` in track endpoint use integer cents.
6. **Currency** — budgets follow account currency; conversion track events accept ISO 4217 `currency` field.
7. **Never expose CAPI tokens** — `capiToken` is plaintext on write only; encrypted at rest. Only masked state returned.
8. **Portal clients** — use `/portal/ads/*` endpoints for client-facing approve/reject. Admin endpoints require AI_API_KEY.
9. **Activity collection** — singular `activity`, field `type` not `kind`. Ad prefixes: `ad_campaign.*`, `ad_set.*`, `ad.*`.

---

## Pending Peet hand-offs

These items are required for full production capability but are not blocking for dev/testing:

- **Meta App Review** — `ads_management` scope approval for write access in production
- **Google Ads developer token** — prod WRITE access (currently dev token = read-only or limited)
- **LinkedIn LMDP application** — `LINKEDIN_ADS_CLIENT_ID` + `LINKEDIN_ADS_CLIENT_SECRET` env vars (Marketing Developer Platform approval)
- **TikTok For Business app** — `TIKTOK_ADS_CLIENT_ID` + `TIKTOK_ADS_CLIENT_SECRET` env vars (TFB Marketing API approval)
- **`firebase deploy --only firestore:indexes`** — ~25+ pending composite indexes for ads queries; run from `partnersinbiz-web/`
- **`CRON_SECRET` env var** — set in Vercel; required by all 3 ads cron endpoints
- **Vercel cron schedules** — wire `vercel.json` cron entries for daily-insights-pull, budget-pacing-check, experiment-significance-check

---

## Out of scope — use other skills

| Task | Use instead |
|---|---|
| Organic social posting | `social-media-manager` skill |
| Platform analytics SDK / web property metrics | `analytics` skill |
| Client-facing report documents | `client-documents` skill (feed it insights data) |
| Email + SMS marketing | `email-outreach` skill |
| CRM contact / deal CRUD | `crm-sales` skill |
| SEO sprint management | `seo-sprint-manager` skill |

For competitor, offer, audience, creative, placement, platform, and benchmark research, create or link a structured Research item through the `research-intelligence` skill before producing client-facing reports or campaign recommendations.

---

## Error Reference

| HTTP | Meaning | Fix |
|---|---|---|
| 400 | Validation error / missing required field | Check body shape for platform-specific required fields |
| 400 | LinkedIn APP audience not supported | Use WEBSITE or ENGAGEMENT audience type instead |
| 401 | Unauthorized | Check `AI_API_KEY` + `X-Org-Id` header |
| 403 | Forbidden | Token lacks access to this org |
| 404 | Not found | Verify entity ID + orgId |
| 429 | Rate limited | Retry with exponential backoff; read `Retry-After` |
| 500 | Server error | Check Vercel function logs; verify env vars set |

**Retry pattern:** immediate → 1s → 4s → 16s → give up. Never retry 4xx except 429.
