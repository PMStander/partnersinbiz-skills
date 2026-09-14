---
name: social-media-manager
description: >
  Manage social media for any client through the Partners in Biz platform API. Create, schedule, publish, and analyze
  social posts across X/Twitter, LinkedIn, Facebook, Instagram, TikTok, Pinterest, Reddit, Bluesky, Threads, YouTube,
  Mastodon, and Dribbble. Use this skill whenever the user mentions anything related to social media management,
  including but not limited to: "schedule a post", "draft social content", "publish to LinkedIn", "publish to Twitter",
  "post to Instagram", "post to TikTok", "post to Facebook", "check social analytics", "connect social account",
  "manage social media", "post to social", "social media calendar", "bulk schedule posts", "RSS feed",
  "social media dashboard", "what should I post", "generate social content", "best time to post", "repurpose this post",
  "social media report", "social engagement", "social stats", "queue posts", "auto-post", "content calendar",
  "social campaign", "hashtag suggestions", "AI caption", "write a tweet", "LinkedIn article", "thread post",
  "cross-post", "multi-platform post", "social scheduling", "social queue", "weekly social plan",
  "social media strategy", "post performance", "top performing posts", "social ROI", "audience growth",
  "approve post", "reject post", "pending approval", "social inbox", "generate image", "AI image",
  "reply suggestions", or any mention of posting content to social platforms. Also trigger when the user asks to
  create content for a specific client or organization that should be posted on social media. If in doubt, trigger
  — this skill handles the full social media lifecycle.
---

# Social Media Manager — Partners in Biz Platform API

This skill enables full social media management for any client/organization through the Partners in Biz platform API. It covers the entire lifecycle: connecting accounts, creating content (with AI assistance), scheduling, publishing, approval workflows, inbox management, tracking analytics, managing RSS auto-posting, and repurposing content across platforms.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## Supported Platforms

`twitter` (aliased as `x`), `linkedin`, `facebook`, `instagram`, `tiktok`, `pinterest`, `reddit`, `bluesky`, `threads`, `youtube`, `mastodon`, `dribbble`

Note: The legacy `x` alias maps to `twitter` internally. Prefer `twitter` in new code.

## Auth Levels

- **`client`** — org-scoped user. Can read/create posts and inbox items.
- **`admin`** — platform admin. Required for all single-resource operations (`/[id]`), analytics, media, RSS, bulk, publish, approve, and most write operations.
- **AI/Hermes agents** use a bearer key plus `X-Org-Id`. Prefer the user-delegation Bearer token (`pib_dlg_…`) for interactive/human-triggered runs, or per-agent `pib_ag_...` keys from Firestore `api_keys`; the legacy shared `AI_API_KEY` is a cron/system-only fallback. Current social routes treat AI callers as admin-level for social operations while scoping the request by `X-Org-Id`.

## Messages side-canvas previews

When drafting or preparing posts for a human in Messages, emit:

```json
{
  "id": "open-social-post",
  "type": "open_context",
  "label": "Preview post",
  "payload": { "kind": "social", "id": "<postId>", "label": "<short caption>" }
}
```

Messages opens the Context Dock with the matching platform card (Instagram feed/reels/stories, LinkedIn, Facebook, X, YouTube). For a full Content Engine campaign use `{ "kind": "campaign", "id": "<campaignId>" }` instead. Humans still approve/schedule in the social or campaign workspace; the dock is for WYSIWYG review in chat.

---

## Authentication

All requests require **two** headers for AI agent requests:

```
Authorization: Bearer <PIB_AGENT_OR_AI_API_KEY>
X-Org-Id: <orgId>
```

> **Required for AI/Hermes agents:** The `X-Org-Id` header is mandatory when authenticating with a PiB agent key or the legacy shared `AI_API_KEY`. Omitting it returns `{"success":false,"error":"X-Org-Id header is required for AI agent requests"}` even with a valid token.

On VPS Hermes profiles, read the PiB key from the profile environment, normally `AI_API_KEY`. That value may be a per-agent `pib_ag_...` key or the legacy shared key:

```javascript
const headers = {
  'Authorization': `Bearer ${process.env.AI_API_KEY}`,
  'X-Org-Id': orgId,
  'Content-Type': 'application/json'
};
```

### Auth Troubleshooting

If all endpoints return **401 Unauthorized** with `{"success":false,"error":"Unauthorized"}`:

1. **Wrong/stale PiB credential.** Confirm the Hermes profile's `AI_API_KEY` is a current PiB key, not a model-provider key. Per-agent `pib_ag_...` keys are preferred; legacy shared `AI_API_KEY` can still work as fallback.
2. **Key revoked or expired.** Check Admin Settings -> API Keys / Firestore `api_keys` for the matching `keyPrefix`, expiry, revocation, and org/permission scope.
3. **Legacy token rotated.** If using the shared fallback, get the current `AI_API_KEY` from the Vercel dashboard:
   - Project: `peet-standers-projects-caab22b2/partnersinbiz-web`
   - Settings → Environment Variables → `AI_API_KEY`
4. **Vercel CLI may not work** — local project isn't linked and CLI tends to hang. Use the web dashboard.
5. **Missing tenant header.** A valid PiB key without `X-Org-Id` should fail with a tenant-header error, not a credential `401`.
6. **Update cron jobs.** Any cron prompt or profile env that carries a raw key must be updated after rotation/revocation.
7. **Cron output logs** at `~/.hermes/profiles/<profile>/cron/output/<job_id>/` — check for failure history.

### Base URL

```
https://partnersinbiz.online/api/v1/social
```

Override via `PIB_API_BASE` env var for local dev. Default to production.

> **Exception:** The campaign schedule endpoint lives at `/api/v1/campaigns/[id]/schedule` — outside the `/social` prefix. See the campaigns section.

---

## Known Gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Missing `X-Org-Id` header | `"X-Org-Id header is required for AI agent requests"` | Add `-H "X-Org-Id: <orgId>"` to every curl call when using `AI_API_KEY` |
| Trailing slash on `/accounts` | 308 redirect, empty response | Use `/accounts` not `/accounts/` |
| Campaign schedule wrong base | 404 HTML page | Route is `/api/v1/campaigns/{id}/schedule`, NOT `/api/v1/social/campaigns/{id}/schedule` |
| Bulk endpoint drops `campaignId` | Posts created but not linked to campaign | Use single `POST /posts` per post when `campaignId` must be preserved |

---

## Partners in Biz Own Accounts (orgId: `pib-platform-owner`)

When scheduling content **for Partners in Biz itself** (not a client), use `orgId: pib-platform-owner` and these account IDs:

| Platform | Account ID | Type | Notes |
|---|---|---|---|
| facebook | `l0DPTxi8xGFX4oLwOK8c` | PIB page | "PIB" — the business page. Always use this, not the personal FB. |
| instagram | `kZFWPdCXR7HiZgTJrmJF` | personal | active |
| linkedin | `z6jekgWOpRJs229kbd4I` | personal | company page pending CMA approval — use personal until approved |
| twitter | `I478D32VOu4rm7a2utoS` | personal | @PeetStander |
| bluesky | `rlyjv3dl2Wvdm33fVrpH` | personal | partnersinbiz.bsky.social |
| pinterest | `uTV7yaJEaRyU4GFTJZqR` | business | peetstander0223 |
| youtube | `aGqyvID6ub8nOu8J7owY` | personal | AI Daily Clips — confirm with Peet before scheduling here |

**Stale / wrong-org accounts to ignore:**
- `9UILwCn9bUtiyJbFScAP` (twitter, disconnected)
- `BbxrEsnmq4GGVphenm3l` (facebook "Omni Platform", wrong org)
- `Kod7W9yQ6h6QStYtKcKc` (facebook "Petrus Stander", personal — not for marketing)

### Default campaign platform coverage

When creating a new campaign for Partners in Biz, include **all 6 active marketing platforms** unless a platform is explicitly excluded:

```
platforms: ["facebook", "instagram", "linkedin", "twitter", "bluesky", "pinterest"]
accountIds: [
  "l0DPTxi8xGFX4oLwOK8c",  // Facebook PIB page
  "kZFWPdCXR7HiZgTJrmJF",  // Instagram
  "z6jekgWOpRJs229kbd4I",   // LinkedIn personal (company page pending)
  "I478D32VOu4rm7a2utoS",   // Twitter
  "rlyjv3dl2Wvdm33fVrpH",   // Bluesky
  "uTV7yaJEaRyU4GFTJZqR"   // Pinterest
]
```

### Platform-specific content guidelines (PiB campaigns)

- **Facebook** → business page posts, can be longer form, link previews work well
- **Instagram** → visual-first, captions up to 2200 chars, hashtags important (10–20)
- **LinkedIn** → professional tone, thought leadership, personal Peet voice, max 3000 chars
- **Twitter/X** → punchy, max 280 chars, 1–2 hashtags
- **Bluesky** → conversational, max 300 chars, no algorithm — early-adopter tech audience
- **Pinterest** → image required, keyword-rich description, link to site content

### LinkedIn company page (pending)

LinkedIn company page posting requires `w_organization_social` on **this same LinkedIn app**. Personal connect uses OpenID + `w_member_social` and must keep working while Community Management API is off (`LINKEDIN_CMA_ENABLED` defaults off). When CMA is approved on this app:
1. Turn on `LINKEDIN_CMA_ENABLED` — do not swap `LINKEDIN_CLIENT_ID` / `LINKEDIN_CLIENT_SECRET` and do not create a second app
2. Reconnect LinkedIn via OAuth — company page appears in the picker
3. Add company page accountId to campaigns and update the 21 May 2026 standalone posts

---

## Multi-Tenant Usage

Every endpoint scopes to an org via `orgId`.

- **Admin/AI agents**: pass `orgId` as query param (GET) or body field (POST/PUT/PATCH)
- **Client users**: scoped automatically

If you don't know the `orgId`, look it up from client records first.

---

## Response Format

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": { "total": 50, "page": 1, "limit": 20 }
}
```

Error responses:

```json
{
  "success": false,
  "data": null,
  "error": "Human-readable error message",
  "meta": null
}
```

List endpoints that support pagination use `page` + `limit` (not `offset`).

---

## Current Route Inventory

The base URL section uses `/api/v1/social`, but route references below include `/social/...` so agents can match the platform route inventory exactly.

| Method | Route | Use |
|---|---|---|
| `GET` | `/social/platforms` | List supported social platform metadata. |
| `GET` | `/social/platforms/[platform]` | Read one platform's metadata/capabilities. |
| `GET/POST` | `/social/accounts` | List or connect social accounts. |
| `GET/PUT/DELETE` | `/social/accounts/[id]` | Read, update, or disconnect a social account. |
| `PUT` | `/social/accounts/[id]/set-default` | Make an account the default for its platform/org. |
| `POST` | `/social/accounts/confirm` | Confirm pending OAuth account selections by nonce. |
| `GET` | `/social/oauth/[platform]` | Start OAuth for a platform. |
| `GET` | `/social/oauth/[platform]/callback` | OAuth callback. |
| `GET` | `/social/oauth/pending/[nonce]` | Inspect pending OAuth selections. |
| `GET/POST` | `/social/posts` | List or create posts. |
| `GET/PUT/DELETE` | `/social/posts/[id]` | Read, update, or delete a post. |
| `POST` | `/social/posts/bulk` | Bulk create posts; avoid if campaignId preservation is critical. |
| `GET` | `/social/posts/pending` | Pending approval queue. |
| `POST` | `/social/posts/[id]/approve` | Admin approval. |
| `POST` | `/social/posts/[id]/client-approve` | Client approval. |
| `POST` | `/social/posts/[id]/client-reject` | Client rejection. |
| `POST` | `/social/posts/[id]/qa-approve` | QA approval. |
| `POST` | `/social/posts/[id]/qa-reject` | QA rejection. |
| `POST` | `/social/posts/[id]/submit` | Submit a draft into review/approval flow. |
| `POST` | `/social/posts/[id]/publish` | Publish via connected provider. |
| `POST` | `/social/posts/[id]/regenerate` | Regenerate post content. |
| `GET` | `/social/posts/[id]/download` | Download rendered/exported post asset. |
| `GET/POST` | `/social/posts/[id]/comments` | List or create post comments. |
| `PATCH` | `/social/posts/[id]/comments/[commentId]` | Update or mark a comment. |
| `GET/POST` | `/social/media` | List or register media. |
| `GET/DELETE` | `/social/media/[id]` | Read or remove media. |
| `POST` | `/social/media/upload` | Upload media. |
| `GET` | `/social/analytics` | Org/platform/post analytics summary. |
| `GET/POST` | `/social/analytics/[postId]` | Read or refresh analytics for one post. |
| `GET` | `/social/stats` | Social dashboard stats. |
| `GET` | `/social/health` | Provider/account health. |
| `GET/POST` | `/social/inbox` | List/create social engagement inbox items. |
| `PATCH/DELETE` | `/social/inbox/[id]` | Update/delete inbox item state. |
| `POST` | `/social/inbox/poll` | Poll connected providers for inbox updates. |
| `POST` | `/social/inbox/webhook` | Provider webhook receiver. |
| `GET/POST` | `/social/rss/feeds` | List/create RSS feeds for auto-posting. |
| `GET/PATCH/POST/DELETE` | `/social/rss/feeds/[feedId]` | Manage or run a feed. |
| `GET` | `/social/vault` | Social content vault/library. |
| `GET` | `/social/x/reply-suggestions` | X/Twitter reply suggestions. |
| `GET` | `/social/ai/best-time` | AI best-posting-time helper. |
| `POST` | `/social/ai/generate` | Generate social copy. |
| `POST` | `/social/ai/hashtags` | Generate hashtag suggestions. |
| `POST` | `/social/ai/image` | Generate social image. |
| `GET` | `/social/ai/image-templates` | List AI image templates. |
| `POST` | `/social/ai/repurpose` | Repurpose content across platforms. |
| `POST` | `/portal/social/posts/[id]/publish-now` | Client portal publish-now action for approved posts. |
| `POST` | `/portal/social/posts/[id]/reschedule` | Client portal reschedule action for approved posts. |

---

## API Reference

### Health Check

#### `GET /health/` — auth: admin

Returns queue and account connectivity health for the org.

```bash
curl -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: org_abc123" \
  "https://partnersinbiz.online/api/v1/social/health?orgId=org_abc123"
```

Response:
```json
{
  "queue": { "pending": 3, "processing": 1, "completed": 120, "failed": 2, "stale": 0 },
  "accounts": { "active": 4, "token_expired": 1, "disconnected": 0, "rate_limited": 0, "total": 5 },
  "timestamp": "2026-04-15T10:00:00.000Z"
}
```

`stale` = queue entries that have been in `processing` state for more than 5 minutes (stuck jobs).

---

### Accounts

#### `GET /accounts` — auth: client

> **No trailing slash** — `GET /accounts/` returns a 308 redirect; use `GET /accounts` (no slash).

List connected social accounts for an org.

Query params:
- `orgId`
- `platform` — any supported platform string
- `status` — `active` | `token_expired` | `disconnected` | `rate_limited`
- `page` (default 1), `limit` (default 50, max 100)

Response data: Array of account objects (tokens are never returned).

Account fields: `id`, `platform`, `platformAccountId`, `displayName`, `username`, `avatarUrl`, `profileUrl`, `accountType`, `status`, `scopes`, `platformMeta`, `connectedBy`, `connectedAt`, `lastUsed`.

#### `POST /accounts/` — auth: client

Register a social account. Tokens must be provided pre-encrypted in `encryptedTokens`. **Do not pass raw tokens.** In practice, accounts are connected via the OAuth flow (see OAuth section) — this endpoint is for manual registration only.

Required: `platform`, `displayName`

Body:
```json
{
  "orgId": "org_abc123",
  "platform": "linkedin",
  "platformAccountId": "urn:li:person:xxx",
  "displayName": "Peet Stander",
  "username": "peetstander",
  "avatarUrl": "https://...",
  "profileUrl": "https://linkedin.com/in/peetstander",
  "accountType": "personal",
  "scopes": ["w_member_social"],
  "platformMeta": {}
}
```

#### `GET /accounts/[id]` — auth: admin

Get a single account by ID (tokens stripped from response).

#### `PUT /accounts/[id]` — auth: admin

Update account metadata. Updatable fields: `displayName`, `username`, `avatarUrl`, `profileUrl`, `accountType`, `status`, `scopes`, `platformMeta`.

#### `DELETE /accounts/[id]` — auth: admin

**Soft-deletes** — sets `status: "disconnected"` and clears stored tokens. Does not remove the record.

#### `PUT /accounts/[id]/set-default` — auth: client

Marks one connected account as the default for its platform inside the active tenant. The route clears any other default account for the same `orgId` + `platform`.

Full path: `/api/v1/social/accounts/[id]/set-default`

Response: `{ "id": "acc_123" }`

#### `POST /accounts/confirm` — auth: client

Finalizes a multi-account OAuth callback after the platform returned one or more selectable accounts/pages.

Full path: `/api/v1/social/accounts/confirm`

Body:
```json
{
  "nonce": "oauth_pending_nonce",
  "selections": [
    { "index": 0, "isDefault": true },
    { "index": 1, "isDefault": false }
  ]
}
```

Rules:
- `nonce` must exist in `social_oauth_pending`, match the active tenant, and not be expired.
- `selections[].index` points into the pending `options[]` array returned by `/oauth/pending/[nonce]`.
- Only one selected account can be default for a platform.
- Personal OAuth pending records must match the current `ownerUid`.
- The route creates/updates `social_accounts` and deletes the pending selection.

Response: `{ "accountIds": ["acc_123"] }` (201)

---

### Posts

#### `GET /posts/` — auth: client

List posts for an org.

Query params:
- `orgId`
- `platform` — filter by platform (currently only `x` and `linkedin` supported for filter)
- `status` — `draft` | `pending_approval` | `approved` | `scheduled` | `publishing` | `published` | `partially_published` | `failed` | `cancelled`
- `from` — ISO 8601 date, filters by `scheduledFor` ≥ this date
- `to` — ISO 8601 date, filters by `scheduledFor` ≤ this date

**No pagination** — returns all matching posts sorted by `scheduledFor` ascending. Use `from`/`to` to narrow results.

Post object shape:
```json
{
  "id": "post_xyz",
  "orgId": "org_abc123",
  "platform": "x",
  "platforms": ["twitter"],
  "accountIds": ["acc_123"],
  "content": {
    "text": "Post text here",
    "platformOverrides": {}
  },
  "media": [],
  "hashtags": [],
  "labels": [],
  "tags": [],
  "campaign": null,
  "category": "other",
  "threadParts": [],
  "status": "scheduled",
  "scheduledAt": "2026-04-14T09:00:00Z",
  "scheduledFor": "2026-04-14T09:00:00Z",
  "publishedAt": null,
  "approvedBy": null,
  "approvedAt": null,
  "source": "api",
  "createdBy": "user_abc",
  "createdAt": "...",
  "updatedAt": "..."
}
```

`category` values: `work`, `personal`, `ai`, `sport`, `sa`, `other`

#### `POST /posts/` — auth: client

Create a new post.

Required fields:
- `content` — string OR `{ text: string, platformOverrides: {} }`
- `platforms` (array, preferred) OR `platform` (legacy, only `x`/`linkedin`)

Body:
```json
{
  "orgId": "org_abc123",
  "content": "Your post content here",
  "platforms": ["twitter", "linkedin"],
  "accountIds": ["acc_123", "acc_456"],
  "scheduledFor": "2026-04-14T09:00:00Z",
  "status": "scheduled",
  "hashtags": ["#ai"],
  "labels": [],
  "tags": [],
  "category": "work",
  "campaign": null,
  "threadParts": [],
  "media": []
}
```

Status options on create:
- `draft` — saved, not queued
- `scheduled` — queued for publish at `scheduledFor`

`scheduledFor` is the primary scheduling field. `scheduledAt` is accepted as a fallback alias.

If the org has `settings.defaultApprovalRequired: true`, creating a `draft` sends an approval notification.

Response: `{ "id": "post_xyz" }` (201)

#### `GET /posts/[id]` — auth: admin

Get a single post by ID.

#### `PUT /posts/[id]` — auth: admin

Update a post. Updatable fields: `content`, `scheduledFor`, `scheduledAt`, `status`, `category`, `tags`, `threadParts`, `labels`, `hashtags`, `media`, `accountIds`.

Valid `status` values for update: `draft`, `pending_approval`, `approved`, `scheduled`, `publishing`, `published`, `partially_published`, `failed`, `cancelled`.

Rescheduling (`scheduledFor`/`scheduledAt`) automatically syncs the queue entry.

#### `DELETE /posts/[id]` — auth: admin

**Soft-deletes** — sets `status: "cancelled"`. Also cancels the queue entry. Does not remove the record. Works on any post regardless of current status.

#### `POST /posts/[id]/publish` — auth: admin

Immediately publish a post, bypassing the schedule. Supported platforms: all standard platforms plus `youtube`, `mastodon`, `dribbble`. Returns `{ id, externalId, platform }`.

#### `POST /portal/social/posts/[id]/publish-now` — auth: client

Client-portal publish-now action for an already approved post in the active portal org. It validates final approval, publish-ready text, connected active account, and token refresh before publishing.

Full path: `/api/v1/portal/social/posts/[id]/publish-now`

Returns the updated post id/status/external id on success. Failure states update the post/queue with `status='failed'` and audit `post.failed`.

#### `POST /portal/social/posts/[id]/reschedule` — auth: client

Client-portal reschedule action for approved, unpublished, non-cancelled posts.

Full path: `/api/v1/portal/social/posts/[id]/reschedule`

Body:
```json
{ "scheduledAt": "2026-06-05T09:00:00+02:00" }
```

Requires final approval and an active publishing account. Writes both `scheduledAt` and `scheduledFor`, sets `status='scheduled'`, and upserts the matching `social_queue` entry.

#### `POST /posts/[id]/approve` — auth: admin (or client with approval role)

Approve or reject a post in `pending_approval` status.

Body: `{ "action": "approve" }` or `{ "action": "reject" }`

- `approve` → `status: "approved"`, records `approvedBy` + `approvedAt`
- `reject` → `status: "draft"`, clears approval fields

Response: `{ "id": "post_xyz", "status": "approved" }`

#### `GET /posts/[id]/comments` — auth: client

List review/collaboration comments on a post, ordered by `createdAt` ascending.

Response: Array of comment objects with `id`, `text`, `userId`, `userName`, `userRole`, `createdAt`, `agentPickedUp`, `agentPickedUpAt`, **`anchor`** (optional — see below).

#### `POST /posts/[id]/comments` — auth: client

Add a comment to a post. Body: `{ "text": "Your comment", "anchor"?: { ... } }`

**Optional `anchor` field** — set when the client commented on a specific
piece of the post in the review UI:

```json
// Comment on a text selection in the post body
{ "type": "text", "text": "Most agency owners find out…", "offset": 0 }

// Comment on an image attached to the post
{ "type": "image", "mediaUrl": "https://firebasestorage.googleapis.com/…" }
```

Strings are clamped server-side (text ≤ 400 chars, mediaUrl ≤ 1000). When
present, the activity log entry includes the anchor preview, so agents
watching `social_post_commented` events know exactly what was flagged
without re-fetching the post.

#### `DELETE /posts/[id]/comments/[commentId]` — auth: client

Delete a specific comment.

#### `PATCH /posts/[id]/comments/[commentId]` — auth: admin

Mark a comment as picked up by an AI agent. Sets `agentPickedUp: true` and `agentPickedUpAt` timestamp.

No body required. Response: full updated comment object.

#### `GET /posts/pending/` — auth: admin

List all posts with `status: "pending_approval"` across all orgs. Useful for an approval dashboard.

Query params: `limit` (default 5, max 100)

Response: Array of `{ id, content (120 chars), platform, orgId, orgName, scheduledAt }`.

#### `POST /campaigns/[id]/schedule` — auth: client (NEW — bulk schedule)

> **Route is NOT under `/social`** — full URL is `https://partnersinbiz.online/api/v1/campaigns/{id}/schedule`, not `/api/v1/social/campaigns/{id}/schedule`. The base URL for this endpoint is `/api/v1/campaigns/`, same as `GET /api/v1/campaigns`.

Bulk-schedule every `approved` social_post + video on a content-engine
campaign across the campaign's `calendar` (preferred) or a cadence. Use
this instead of PATCHing posts one at a time for content-engine campaigns.

Body (all fields optional):
```json
{
  "startDate": "2026-05-12T09:00:00+02:00",
  "mode": "auto",
  "cadence": { "postsPerDay": 1, "hours": ["09:00"], "daysOfWeek": [1,3,5] },
  "platforms": ["instagram", "linkedin"],
  "includePending": false,
  "timezone": "Africa/Johannesburg",
  "dryRun": true
}
```

- `mode`: `'auto'` (default — calendar slots if present else cadence), `'calendar'` (slots from `campaign.calendar` only), `'cadence'` (skip calendar, use cadence rules).
- `daysOfWeek`: 0=Sun..6=Sat. Default Mon/Wed/Fri.
- `includePending`: also schedule `pending_approval` posts and auto-approve them. Default `false` — recommended only when you trust the campaign content.
- `dryRun`: preview the schedule without writing. Always run once with `dryRun: true` first.

Each scheduled post gets `scheduledFor`, `status='scheduled'`, and a
matching `social_queue` entry — the cron worker (`/api/cron/social`,
5 min interval) publishes them via the connected OAuth provider.

Response:
```json
{
  "scheduled": [{ "postId": "...", "platform": "instagram", "scheduledFor": "...", "status": "scheduled" }],
  "skipped": [],
  "totals": { "scheduled": 36, "skipped": 0, "eligible": 36 },
  "startDate": "2026-05-12T07:00:00.000Z",
  "endDate": "2026-08-04T07:00:00.000Z",
  "mode": "auto",
  "dryRun": false
}
```

For non-campaign-bound posts, schedule individually via `PUT /posts/[id]`
with `{ scheduledFor, status: "scheduled" }`.

### Importing existing local content into a campaign (NEW — for any client workspace)

Many Cowork clients (AHS Law, Lumen, Loyalty Plus, etc.) have local
content folders from older runs — `marketing/social/*.md`, drafted
captions in JSON, rendered videos under `marketing/videos/V*/`, hero
images under `marketing/images/`. These need to land in the platform
as a `campaign` so the client can review, approve, and bulk-schedule
through the new flow.

The agent that lives in that client's workspace runs this end-to-end —
it has filesystem access to the local content + this skill (and
`content-engine` for campaign creation).

**Step 1 — find or create the campaign**

```
# Look for an active content-engine campaign for this org first
GET /campaigns?orgId={orgId}&status=draft

# If none, create one
POST /campaigns
{
  "name": "Q2 Backfill — local social import",
  "clientType": "service-business" | "consumer-app" | "b2b-saas",
  "orgId": "{orgId}"
}
→ returns { id: campaignId, shareToken }
```

If you only have social posts (no blogs/videos to add), `clientType`
just sets the brand-voice template. Pick whichever fits the client.

**Step 2 — upload media (images + videos) to Firebase Storage**

For every local image / video file referenced by a post, upload first
so you have a stable URL on the platform:

```
POST /social/media/upload
  multipart/form-data: file=@<path>, altText=<text>
→ returns { id, url, type, mimeType }
```

For videos with multiple format cuts (vertical Reel / 16:9 YouTube /
15s Stories), upload all three and use them in `media[0].{url,
urlYoutube, urlStories}` per `references/05-video-production.md` in
the content-engine skill.

**Step 3 — create posts with the campaignId**

> ⚠️ **KNOWN BUG — do NOT use `POST /posts/bulk/` for campaign imports.**
> The bulk endpoint silently drops `campaignId` on every post — they get
> created unlinked and won't appear in the campaign roll-up. Always use
> single `POST /social/posts` per post when `campaignId` must be preserved.

```
POST /social/posts
{
  "orgId": "{orgId}",
  "campaignId": "{campaignId}",
  "content": "<caption text from local file>",
  "platforms": ["instagram"],
  "format": "feed",
  "media": [{ "type": "image", "url": "<from step 2>", "altText": "...", "order": 0 }],
  "hashtags": ["..."],
  "tags": ["..."]
}
```

Loop this for every post — yes, one request each. It's slower but required.

Posts land as `status: "draft"` regardless of what you pass on create. To move
them into the client review queue, call `POST /posts/[id]/submit` per post
after creation. Do NOT pass `status: "pending_approval"` on create — it is
silently ignored. The org routes to `client_review` (not `pending_approval`)
if the client approval stage is enabled.

Use an `Idempotency-Key` header per post (`import-{orgId}-{campaignId}-{slug}-{platform}`)
so retries don't create duplicates.

**Step 4 — activate campaign and hand to client for review**

Before sharing the link, **two things have to be true** or the drill-in page
will either crash with `t.map is not a function` or render empty cards:

**4a — Set status to `active`.** The page guards against rendering `draft`
campaigns:
```
PATCH /campaigns/{campaignId}
{ "status": "active" }
```

**4b — Calendar must be a flat array of day-level entries**, NOT a nested
`[{week, slots:[...]}]` shape. The template calls `.map()` on each entry
expecting a flat object. Match this shape exactly:
```
calendar: [
  { day, date, pillarId, channel: "blog"|"video"|"social", format, title, week }
]
```
The `research`, `brandIdentity`, and `pillars` shapes are also strict —
see content-engine SKILL for the canonical schemas (taglines is a dict
with `{master, layered}`, brandIdentity uses `aestheticKeywords` not
`aesthetic`, audiences use `{id, label, painPoints[]}`).

**4c — Videos appear in the "Reels & TikTok" tab only when** `media[0].type === "video"`
on a regular `social_posts` doc with `campaignId` set. There is no
separate "videos" collection — the `/campaigns/[id]/assets` endpoint
filters social posts by media type to populate the videos rollup. If
the tab shows the empty "videos are produced by content-engine" state,
your video posts have `media[0].type === "image"` (or no media). Fix:
```
PUT /social/posts/{id}
{ "media": [{ "type":"video", "url":..., "thumbnailUrl":...,
              "urlYoutube":..., "urlStories":..., "durationSec":...,
              "altText":..., "order": 0 }] }
```

Then share the org-themed drill-in:

```
https://partnersinbiz.online/admin/org/{slug}/social/{campaignId}
```

Each post supports inline + image-anchored comments + WYSIWYG body
editing. Per-asset Approve & per-campaign "Approve all" both work.
The Marketing Preview UI groups posts by Reels / Stories / YouTube /
LinkedIn / Facebook / Instagram tabs automatically based on platform
+ media metadata.

**Step 5 — once approved, bulk-schedule**

Use `POST /campaigns/[id]/schedule` (documented above). Run with
`dryRun: true` first to preview the cadence.

**What to tell the client (operator brief)**

> "We've imported your existing social content into a campaign in the
> platform. To take it live:
> 1. Visit `/admin/org/{slug}/social/{campaignId}` — it's themed in your
>    brand colours and groups everything by Reels / Stories / Posts.
> 2. Highlight any text or click any image to leave inline comments;
>    use 'Edit body' for blogs to make changes yourself.
> 3. When you're happy, hit 'Approve all' or approve each post one by
>    one. Reply with which Monday you want this to start going out.
> 4. We'll bulk-schedule across that week's calendar in one go and the
>    queue auto-publishes at the scheduled times."

The agent then runs the schedule endpoint on the client's behalf with
their preferred start date.

#### `POST /posts/bulk/` — auth: admin

Bulk create up to **50** posts. Accepts JSON or CSV.

**JSON:**
```json
{
  "orgId": "org_abc123",
  "posts": [
    {
      "content": "Tweet content",
      "platforms": ["twitter"],
      "scheduledAt": "2026-04-14T09:00:00Z",
      "accountIds": [],
      "category": "work",
      "hashtags": [],
      "tags": [],
      "labels": []
    }
  ]
}
```

`content` can be string or `{ text }`. `scheduledAt` or `scheduledFor` both accepted. Posts without a date get `status: "draft"`.

**CSV (`multipart/form-data` with `file` field):**

Expected columns: `content`, `platforms` (semicolon/pipe-separated), `scheduled_at`, `category`, `hashtags`, `tags`, `labels`

Response: `{ "total": 5, "succeeded": 4, "failed": 1, "results": [{ "index": 0, "success": true, "id": "..." }, ...] }`

---

### Content Approval Flow

The approval pipeline supports a two-stage review: **staff QA → client**. Which stages are active is controlled by per-org settings (`requiresQaApproval`, `requiresClientApproval`). Stages can be combined, skipped, or bypassed based on org configuration and per-post `requiresApproval` flag.

#### Status Transitions

```
draft
  └─ POST /submit ──► qa_review  (if requiresQa)
                  ──► client_review  (if requiresClient only)
                  ──► scheduled/vaulted  (if no approval required)

qa_review
  ├─ POST /qa-approve ──► client_review  (if requiresClient)
  │                   ──► scheduled/vaulted  (if no client step)
  └─ POST /qa-reject  ──► regenerating  (AI reruns, then back to qa_review)

client_review
  ├─ POST /client-approve ──► scheduled  (if scheduledAt set)
  │                       ──► vaulted  (deliveryMode=download_only)
  │                       ──► approved  (no date, auto_publish)
  └─ POST /client-reject  ──► regenerating  (AI reruns, then back to qa_review)

regenerating  (transient — AI is rewriting the post)
  └─ (automated) ──► qa_review  (when regen completes)
```

`deliveryMode` values: `auto_publish` | `download_only` | `both`

`vaulted` = approved content stored in the content vault for manual download/use.

#### `POST /posts/[id]/submit` — auth: client

Submit a `draft` post into the approval pipeline. The endpoint resolves the next status based on org settings.

No body required (empty `{}` is fine).

Response: `{ "id": "post_xyz", "status": "qa_review" }`

Errors:
- `400` — post is not in `draft` status

#### `POST /posts/[id]/qa-approve` — auth: admin

Staff QA approves the post. Transitions from `qa_review`.

- If client review is required → status becomes `client_review`
- If no client step → status becomes `scheduled` (or `vaulted` depending on `deliveryMode`)
- If immediately scheduled, creates the queue entry.

No body required.

Response: `{ "id": "post_xyz", "status": "client_review" }`

Errors:
- `400` — invalid transition (post not in `qa_review`)

#### `POST /posts/[id]/qa-reject` — auth: admin

Staff QA rejects the post with feedback. Triggers automatic AI regeneration.

Required body:
```json
{ "reason": "The tone is too casual. Make it more professional." }
```

- Writes a `qa_rejection` comment on the post (visible to agent via `GET /posts/[id]/comments`)
- Increments `approval.rejectionCount`
- Sets status to `regenerating`
- Fires AI regeneration in the background — post returns to `qa_review` when done

Response: `{ "id": "post_xyz", "status": "regenerating" }`

#### `POST /posts/[id]/client-approve` — auth: client

Client approves the post. Transitions from `client_review` (or legacy `pending_approval`).

- Resolves final status based on `deliveryMode` and whether `scheduledAt` is set
- Creates queue entry if status becomes `scheduled`

No body required.

Response: `{ "id": "post_xyz", "status": "scheduled" }`

#### `POST /posts/[id]/client-reject` — auth: client

Client rejects the post with feedback. Triggers automatic AI regeneration.

Required body:
```json
{ "reason": "Please focus more on the product benefits, not the features." }
```

- Writes a `client_rejection` comment on the post
- Increments `approval.rejectionCount`
- Sets status to `regenerating`
- Fires AI regeneration in the background — post returns to `qa_review` when done

Response: `{ "id": "post_xyz", "status": "regenerating" }`

#### `POST /posts/[id]/regenerate` — auth: client

Manually trigger AI regeneration on a post. Use when you want to re-run the AI on a post that has unresolved rejection feedback without waiting for the automatic flow.

Accepts posts in `qa_review`, `client_review`, or `pending_approval` (legacy). Body is optional / empty.

The endpoint:
1. Immediately sets status to `regenerating` (UI can show progress)
2. Reads all rejection comments as feedback
3. Runs AI to rewrite the post content
4. Transitions back to `qa_review`

Response:
```json
{
  "id": "post_xyz",
  "status": "qa_review",
  "regenerationCount": 2,
  "oldText": "Previous content...",
  "newText": "Rewritten content...",
  "feedbackUsed": 3
}
```

Errors:
- `400` — invalid transition or regeneration failure (status is reverted on failure)

#### `GET /posts/[id]/download` — auth: client

Download a post as a JSON bundle. Used for `deliveryMode: "download_only"` or `"both"` — gives the client a portable artefact with all post content.

Response is served with `Content-Disposition: attachment; filename="post-{id}.json"` so browsers trigger a download.

Downloaded JSON shape:
```json
{
  "postId": "post_xyz",
  "orgId": "org_abc123",
  "content": { "text": "Post content here" },
  "hashtags": ["#ai", "#marketing"],
  "platforms": ["twitter", "linkedin"],
  "media": [{ "url": "https://...", "type": "image", "altText": "" }],
  "approvedAt": "2026-05-07T10:00:00Z",
  "downloadFormat": "json",
  "generatedAt": "2026-05-07T10:05:00Z"
}
```

---

### Content Vault

The vault is a filtered view of posts that have passed final approval, regardless of whether they are scheduled for publishing. It surfaces content in statuses: `approved`, `scheduled`, `published`, `partially_published`, `vaulted`, `failed`.

#### `GET /vault/` — auth: client

List posts in the content vault for an org.

Query params:
- `orgId`
- `platform` — filter by platform string
- `label` — filter by label
- `deliveryMode` — `auto_publish` | `download_only` | `both`
- `from` — ISO 8601, filters by `approvedAt` (falls back to `scheduledAt` / `updatedAt`) ≥ this date
- `to` — ISO 8601, same field ≤ this date

**No pagination** — returns all matching posts sorted by `approvedAt` desc (falls back to `updatedAt`).

Response data: Array of vault post objects:
```json
{
  "id": "post_xyz",
  "content": { "text": "..." },
  "platforms": ["twitter"],
  "hashtags": ["#ai"],
  "deliveryMode": "auto_publish",
  "approvedAt": "2026-05-07T10:00:00Z",
  "scheduledAt": "2026-05-07T12:00:00Z",
  "publishedAt": null,
  "status": "scheduled",
  "media": [],
  "labels": []
}
```

---

### Media

Two endpoints: one to upload a binary file, one to manage media metadata records.

#### `POST /media/upload` — auth: admin

**Binary file upload.** Accepts `multipart/form-data`. Uploads the file to Firebase Storage and writes a Firestore media record. Returns a public URL ready to attach to posts.

Fields:
- `file` (required) — the binary file. Allowed MIME types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `video/mp4`, `video/quicktime`. Max 512 MB.
- `altText` (optional) — accessibility text

```bash
curl -X POST \
  -H "Authorization: Bearer $AI_API_KEY" \
  -H "X-Org-Id: pib-platform-owner" \
  -F "file=@photo.jpg" \
  -F "altText=Product screenshot" \
  "https://partnersinbiz.online/api/v1/social/media/upload"
```

Response:
```json
{
  "id": "media_abc",
  "url": "https://storage.googleapis.com/bucket/social-media/org_abc123/abc123.jpg",
  "storagePath": "social-media/org_abc123/abc123.jpg",
  "mimeType": "image/jpeg",
  "altText": "Product screenshot"
}
```

Use the returned `url` in the `media` array when creating/updating a post:
```json
"media": [{ "url": "https://storage.googleapis.com/..." }]
```

#### `GET /media/` — auth: admin

List media records for an org.

Query params: `orgId`, `type` (`image`/`video`/`gif`), `status` (`uploading`/`processing`/`ready`/`failed`), `page`, `limit` (default 50, max 100)

#### `POST /media/` — auth: admin

Register a media record from an external URL. **JSON body, not file upload.** Use `POST /media/upload` instead when you have the binary file.

Required: `originalUrl`, `originalFilename`, `type`

Body:
```json
{
  "orgId": "org_abc123",
  "originalUrl": "https://storage.example.com/image.png",
  "originalFilename": "image.png",
  "originalMimeType": "image/png",
  "originalSize": 204800,
  "type": "image",
  "altText": "Product screenshot"
}
```

Response: `{ "id": "media_abc" }` (201)

#### `GET /media/[id]` — auth: admin

Get media record by ID.

#### `DELETE /media/[id]` — auth: admin

Hard-deletes the media record (does not delete the underlying file from storage).

---

### Platforms

#### `GET /platforms/` — auth: client

List all supported platforms with capabilities and constraints. Returns an array of platform constraint objects, each with an `active` boolean indicating whether the platform is currently wired for publishing.

Query params: `orgId`

Response: Array of platform objects (see `GET /platforms/[platform]` for shape).

#### `GET /platforms/[platform]` — auth: client

Get detailed constraint info for a specific platform. Useful for validating content before creating a post.

Query params: `orgId`

Response:
```json
{
  "platform": "twitter",
  "maxCharacters": 280,
  "maxMediaItems": 4,
  "supportedMediaTypes": ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4"],
  "supportsThreads": true,
  "supportsHashtags": true,
  "supportsCarousel": false,
  "active": true
}
```

Returns `404` with `"Unknown platform: {name}"` for unsupported platform strings.

---

### Analytics

All analytics endpoints require **admin** auth.

#### `GET /analytics/` — auth: admin

Multi-mode analytics endpoint controlled by the `view` param.

**Default (post analytics snapshots):**
```bash
curl -H "Authorization: Bearer $AI_API_KEY" \
  "https://partnersinbiz.online/api/v1/social/analytics/?orgId=org_abc123&platform=twitter"
```

Query params: `orgId`, `platform`, `postId` (filter to a specific post's snapshots)

**`view=best-times` — best posting time recommendations:**
```bash
curl -H "Authorization: Bearer $AI_API_KEY" \
  "https://partnersinbiz.online/api/v1/social/analytics/?orgId=org_abc123&platform=twitter&view=best-times"
```

Response:
```json
[
  { "day": "monday", "hour": 9, "timezone": "UTC", "score": 0.92 },
  { "day": "wednesday", "hour": 12, "timezone": "UTC", "score": 0.87 }
]
```

**`view=accounts` — account-level analytics:**
```bash
curl -H "Authorization: Bearer $AI_API_KEY" \
  "https://partnersinbiz.online/api/v1/social/analytics/?orgId=org_abc123&view=accounts"
```

Query params: `orgId`, `platform` (optional filter)

#### `GET /analytics/[postId]` — auth: admin

Get all analytics snapshots for a specific post, with the latest metrics per platform extracted.

Response:
```json
{
  "snapshots": [...],
  "latest": [
    { "platform": "twitter", "impressions": 1250, "engagements": 85, "collectedAt": "..." }
  ]
}
```

#### `POST /analytics/[postId]` — auth: admin

Force-refresh analytics for a post from the platform. Returns `{ "metrics": {...} }`. Only works for published posts.

---

### Stats

#### `GET /stats/` — auth: client

Lightweight stats summary for an org (cheaper than full analytics).

Query params: `orgId`

Response:
```json
{
  "total": 142,
  "byStatus": {
    "draft": 10,
    "pending_approval": 3,
    "approved": 5,
    "scheduled": 18,
    "published": 100,
    "failed": 4,
    "cancelled": 2
  },
  "byPlatform": { "twitter": 60, "linkedin": 40, "instagram": 42 },
  "approvalRate": 85,
  "last30Days": 34,
  "last30DaysSeries": [
    { "label": "W1", "value": 4 },
    { "label": "W2", "value": 7 },
    { "label": "W3", "value": 6 },
    { "label": "W4", "value": 8 },
    { "label": "W5", "value": 3 },
    { "label": "W6", "value": 5 },
    { "label": "W7", "value": 1 }
  ]
}
```

`last30DaysSeries` — 7 weekly buckets (W1 = oldest, W7 = most recent) of post counts by `createdAt`. Useful for sparkline/trend charts.
```

---

### Inbox

Monitor and manage social engagement: comments, mentions, replies, DMs, likes, shares, follows.

#### `GET /inbox/` — auth: client

List inbox items for an org.

Query params:
- `orgId`
- `status` — `unread` | `read` | `replied` | `archived`
- `type` — `comment` | `mention` | `reply` | `dm` | `like` | `share` | `follow`
- `platform`
- `limit` (default 50, max 200)
- `startAfter` — cursor (last item ID from previous page)

Response:
```json
{
  "items": [...],
  "hasMore": true,
  "cursor": "inbox_item_id"
}
```

Inbox item object:
```json
{
  "id": "inbox_abc",
  "orgId": "org_abc123",
  "platform": "twitter",
  "type": "comment",
  "fromUser": {
    "name": "Jane Smith",
    "username": "janesmith",
    "avatarUrl": "https://...",
    "profileUrl": "https://twitter.com/janesmith"
  },
  "content": "Love this post!",
  "postId": "post_xyz",
  "platformItemId": "tweet_123",
  "platformUrl": "https://twitter.com/...",
  "status": "unread",
  "priority": "normal",
  "sentiment": "positive",
  "createdAt": "...",
  "updatedAt": "..."
}
```

`sentiment`: `positive` | `neutral` | `negative` | `null`

#### `POST /inbox/` — auth: client

Create an inbox item (primarily for webhooks). Required: `platform`, `type`, `fromUser`, `content`, `platformItemId`, `platformUrl`.

#### `PATCH /inbox/[id]` — auth: client

Update an inbox item's `status` and/or `priority`.

Body: `{ "status": "read", "priority": "high" }`

Valid `status`: `unread`, `read`, `replied`, `archived`

Valid `priority`: `high`, `normal`, `low`

#### `DELETE /inbox/[id]` — auth: client

Hard-delete an inbox item.

#### `POST /inbox/webhook` — auth: none (platform webhook)

Receives real-time events from social platforms. Not called directly by agents.

#### `POST /inbox/poll` — auth: admin

Manually trigger an inbox poll for the current org. Calls the platform APIs to fetch new engagement items.

Response: `{ "polled": true, "newItems": 5 }`

---

### RSS Feeds

All RSS endpoints require **admin** auth.

#### `GET /rss/feeds/` — auth: admin

List RSS feeds for an org. Returns all feeds (no pagination).

#### `POST /rss/feeds/` — auth: admin

Create a new RSS feed subscription.

Required: `name`, `feedUrl`, `targetPlatforms[]`

Body:
```json
{
  "orgId": "org_abc123",
  "name": "Company Blog",
  "feedUrl": "https://example.com/feed.xml",
  "targetPlatforms": ["twitter", "linkedin"],
  "targetAccountIds": ["acc_123"],
  "postTemplate": "{{title}} {{url}}",
  "includeImage": false,
  "autoSchedule": false,
  "schedulingStrategy": "queue",
  "checkIntervalMinutes": 60
}
```

- `feedUrl` — must be a valid URL
- `targetPlatforms[]` — required; which platforms to post to
- `targetAccountIds[]` — which accounts to post from
- `postTemplate` — variables: `{{title}}`, `{{url}}`, `{{description}}`, `{{author}}`, `{{pubDate}}`
- `includeImage` — attach feed item image to post if available
- `autoSchedule` — auto-schedule posts vs. drafts
- `schedulingStrategy` — `"queue"` (default) or `"optimal"`
- `checkIntervalMinutes` — minimum 15, default 60

Response: Full feed object with `id` (201).

#### `GET /rss/feeds/[feedId]` — auth: admin

Get a single feed by ID.

#### `PATCH /rss/feeds/[feedId]` — auth: admin

Update feed configuration. Updatable: `name`, `feedUrl`, `targetAccountIds`, `targetPlatforms`, `postTemplate`, `includeImage`, `autoSchedule`, `schedulingStrategy`, `checkIntervalMinutes`.

#### `DELETE /rss/feeds/[feedId]` — auth: admin

Hard-delete a feed subscription.

#### `POST /rss/feeds/[feedId]` — auth: admin

Trigger an action on a feed.

Body: `{ "action": "check" }` (default), `{ "action": "pause" }`, or `{ "action": "resume" }`

- Omitting `action` or sending `"check"` triggers a manual feed check immediately
- `"pause"` — stops auto-checking
- `"resume"` — re-enables the feed and resets the error counter

---

### AI Features

#### `POST /ai/generate` — auth: admin

Generate social media content using AI.

Required: `prompt`

Body:
```json
{
  "prompt": "speed reading science breakthroughs",
  "platform": "twitter",
  "tone": "professional",
  "includeHashtags": true,
  "includeEmojis": false,
  "count": 3
}
```

- `platform` — default `"twitter"`
- `tone` — default `"professional"`. Options: `professional`, `casual`, `humorous`, `inspirational`, `educational`, `provocative`
- `count` — default 3, max 5
- `includeEmojis` — note spelling: `includeEmojis` (not `includeEmoji`)

Response: `{ "captions": [{ "text": "...", "hashtags": ["#tag"] }] }`

#### `POST /ai/hashtags` — auth: admin

Generate relevant hashtags.

Required: `text`

Body: `{ "text": "Post text", "platform": "instagram", "count": 10 }`

- `platform` — default `"twitter"`
- `count` — default 10, max 20

Response: `{ "hashtags": [{ "tag": "#speedreading", "relevance": 0.95 }, ...] }`

#### `GET /ai/best-time` — auth: admin

Get AI-recommended posting times based on historical engagement data.

Query params: `platform` (e.g. `linkedin`, `twitter`) — defaults to `twitter`

Example: `GET /ai/best-time?platform=linkedin&orgId=org_abc123`

Response:
```json
{
  "slots": [
    {
      "dayOfWeek": 2,
      "hour": 10,
      "avgScore": 0.87,
      "postCount": 14,
      "dayName": "Tuesday",
      "timeLabel": "10:00 AM",
      "label": "Tuesday 10:00 AM"
    }
  ],
  "recommendation": "Best time to post on LinkedIn is Tuesday at 10:00 AM"
}
```

#### `POST /ai/repurpose` — auth: admin

Repurpose content across platforms.

Body:
```json
{
  "text": "Original long-form content...",
  "sourcePlatform": "blog",
  "targetPlatforms": ["twitter", "linkedin", "reddit"],
  "preserveTone": true,
  "orgId": "org_abc123"
}
```

Response: `{ "versions": [{ "platform": "twitter", "text": "...", "hashtags": [...] }, ...] }`

#### `POST /ai/image` — auth: admin

Generate an image using AI (xAI Grok `grok-2-image`). **xAI only** — Gemini/Imagen was removed 2026-05-04 due to runaway billing. The `provider` parameter is no longer accepted.

Body:
```json
{
  "prompt": "A professional product banner, modern design, blue tones",
  "size": "1024x1024"
}
```

- `prompt` — required; max 4000 characters
- `size`: `"1024x1024"` (square, default) | `"1024x1536"` (portrait) | `"1536x1024"` (landscape)

Response: `{ "url": "https://...", "revisedPrompt": "...", "provider": "xai" }`

The `url` is a direct CDN URL from xAI. Upload it via `POST /media/` before attaching to a post if you need a stable Firebase Storage URL.

Errors:
- `429` — rate limit; retry later
- `400` with "content policy" — rephrase the prompt
- `500` — `XAI_API_KEY` not configured in environment

#### `GET /ai/image-templates` — auth: none

Get predefined image prompt templates for common use cases.

Response: Array of `{ id, name, description, promptTemplate, suggestedSize, category }`

Categories: `product`, `quote`, `event`, `blog`, `testimonial`, `promotion`, `comparison`, `infographic`

Templates use `{{placeholder}}` variables — fill them in before calling `/ai/image`.

---

### X/Twitter Engagement

#### `GET /x/reply-suggestions` — auth: admin

Get pre-configured X/Twitter engagement topics: search queries and reply context for finding relevant conversations.

Response: Array of `{ topic, searchQuery, draftReply, context }`

---

### OAuth

#### `GET /oauth/[platform]` — auth: client

Initiates an OAuth flow. **This endpoint redirects the browser to the platform's authorization URL** — it does not return JSON. Use it by directing the user to this URL in their browser.

Query params:
- `orgId` — org to connect the account to
- `redirectUrl` — where to redirect after callback (default: `/portal/social`)

**Platform notes:**
- `twitter` — Uses OAuth 2.0 with PKCE. Users connect via the OAuth flow like other platforms.
- `bluesky` — uses app passwords, not OAuth. Create account directly via `POST /accounts/`.

After the user authorizes, the callback automatically creates/updates the account in Firestore with encrypted tokens.

#### `GET /oauth/[platform]/callback`

Handles the redirect from the platform. Exchanges auth code for tokens, fetches profile, and creates/updates the `social_accounts` entry. Not called directly by agents.

#### `GET /oauth/pending/[nonce]` — auth: client

Reads a pending multi-account OAuth selection for the active tenant. Tokens are stripped from the response.

Full path: `/api/v1/social/oauth/pending/[nonce]`

Response:
```json
{
  "platform": "linkedin",
  "options": [
    { "index": 0, "displayName": "Company Page", "username": "company", "accountType": "page", "platformAccountId": "..." }
  ]
}
```

Use this immediately before `POST /accounts/confirm` when an OAuth callback asks the user/agent to choose which pages/accounts to connect.

---

## Workflow Guides

### 1. Schedule a Post to Multiple Platforms

```bash
# 1. Fetch connected accounts
GET /accounts/?orgId=org_abc123

# 2. Bulk create with platform-specific content
POST /posts/bulk/
{
  "orgId": "org_abc123",
  "posts": [
    {
      "content": "Short tweet (280 chars max) #hashtag",
      "platforms": ["twitter"],
      "accountIds": ["acc_twitter"],
      "scheduledAt": "2026-04-14T09:00:00Z"
    },
    {
      "content": "Longer LinkedIn version with more detail...\n\n#hashtag",
      "platforms": ["linkedin"],
      "accountIds": ["acc_linkedin"],
      "scheduledAt": "2026-04-14T09:30:00Z"
    }
  ]
}
```

### 2. Schedule a Post with Media

```
1. POST /media/upload  (multipart/form-data)  — upload binary to Firebase Storage, get back { url }
2. POST /posts/  with "media": [{ "url": "<returned url>" }] and "scheduledFor"
```

Platform media limits:
- **Twitter/X**: up to 4 images OR 1 video (chunked upload handled server-side)
- **LinkedIn**: 1 image or 1 video per post
- **Threads**: 1 image/video, or carousel (multiple URLs → carousel post)
- **Mastodon**: images and video supported
- **Bluesky**: media parameter accepted but not yet attached (AT Protocol blob upload pending)
- **Facebook/Instagram**: URL-based; upload first then pass URL

### 3. Post a Thread on X/Twitter

Set `threadParts` instead of a plain content string. Media in `post.media[].url` attaches to the first tweet only.

```json
{
  "orgId": "org_abc123",
  "content": "Part 1 of 3...",
  "threadParts": ["Part 1 of 3...", "Part 2 of 3...", "Part 3 of 3..."],
  "platforms": ["twitter"],
  "media": [{ "url": "https://storage.googleapis.com/..." }],
  "scheduledFor": "2026-04-14T09:00:00Z",
  "status": "scheduled"
}
```

### 4. Generate AI Content, Image, and Schedule

```
1. POST /ai/generate  — get content options
2. GET  /analytics/?view=best-times  — find best posting time
3. POST /ai/hashtags  — generate hashtags
4. GET  /ai/image-templates  — pick a template, fill {{placeholders}}
5. POST /ai/image  — generate image (returns xAI CDN URL)
6. POST /media/upload  — re-upload to Firebase Storage for a stable URL (optional but recommended)
7. POST /posts/  — create post with content, media URL, and time
```

### 5. Two-Stage Content Approval Workflow (QA → Client)

This is the standard flow when both `requiresQaApproval` and `requiresClientApproval` are enabled for an org.

```
1. POST /posts/                       — create with status: "draft"
2. POST /posts/[id]/submit            — enter approval pipeline → status: "qa_review"
3. GET  /posts/[id]/comments          — (agent) read any previous rejection feedback
4. POST /posts/[id]/qa-approve        — staff approves → status: "client_review"
   OR
   POST /posts/[id]/qa-reject  { "reason": "..." }  → status: "regenerating"
     └─ AI rewrites automatically → status: "qa_review" (back to step 4)
5. POST /posts/[id]/client-approve    — client approves → status: "scheduled" or "vaulted"
   OR
   POST /posts/[id]/client-reject  { "reason": "..." }  → status: "regenerating"
     └─ AI rewrites automatically → status: "qa_review" (back to step 4)
6. POST /posts/[id]/publish           — or wait for scheduled time
```

Legacy approval (single-stage via `/approve`):
```
POST /posts/[id]/approve  { "action": "approve" | "reject" }
```
Still works but does not trigger AI regeneration on reject.

### 6. Content Vault Workflow

For orgs with `deliveryMode: "download_only"` — content is approved but not auto-published.

```
1. POST /posts/          — create with status: "draft"
2. POST /posts/[id]/submit  — enter pipeline
3. (approval stages as above)
4. GET  /vault/          — client browses approved content
5. GET  /posts/[id]/download  — download specific post as JSON bundle
```

### 7. Set Up RSS Auto-Posting

```
1. POST /rss/feeds/  — create feed with feedUrl, targetPlatforms[], postTemplate
2. POST /rss/feeds/[feedId]  { "action": "check" }  — test it immediately
3. GET  /rss/feeds/  — monitor all feeds
4. PATCH /rss/feeds/[feedId]  — adjust config
5. POST /rss/feeds/[feedId]  { "action": "pause" | "resume" }
```

### 8. Check Analytics and Best Posting Times

```
1. GET /analytics/?orgId=org_abc123&view=best-times&platform=twitter
2. GET /analytics/?orgId=org_abc123&platform=twitter  — post snapshots
3. GET /analytics/[postId]  — per-post breakdown with latest per platform
4. POST /analytics/[postId]  — force-refresh from platform
5. GET /stats/?orgId=org_abc123  — quick summary (includes last30DaysSeries trend)
```

### 9. Connect a New Social Account via OAuth

```
1. Redirect user to: GET /oauth/[platform]?orgId=org_abc123
   (This redirects to the platform — the user must do this in a browser)
2. Platform redirects back to /oauth/[platform]/callback
3. Account is automatically created in Firestore
4. GET /accounts/?orgId=org_abc123  — confirm account appeared
```

For Bluesky: skip OAuth. Create the account directly with `POST /accounts/` using app password credentials.

### 10. Repurpose Content Across Platforms

```
1. POST /ai/repurpose  — pass `text` (original content) and `targetPlatforms`
2. Review the repurposed versions
3. POST /posts/bulk/  — create all platform variants
```

### 11. Monitor Inbox Engagement

```
1. GET /inbox/?orgId=org_abc123&status=unread
2. PATCH /inbox/[id]  { "status": "read" }
3. POST /inbox/poll  — manually fetch new items from platforms
4. GET /x/reply-suggestions  — engagement topics for X
```

---

## Platform Constraints — Quick Reference

| Platform | Max Characters | Media Support (via this platform) | Link Behaviour |
|----------|---------------|-----------------------------------|----------------|
| X/Twitter | 280 (25,000 long posts) | Up to 4 images OR 1 video (chunked) | Shortened, uses chars |
| LinkedIn | 3,000 | 1 image OR 1 video | Clickable, no char cost |
| Facebook | 63,206 | URL-based (pass public URL) | Preview card |
| Instagram | 2,200 | URL-based (pass public URL) | Not clickable in caption |
| TikTok | 4,000 | Not yet wired | Bio only |
| Pinterest | 500 | Not yet wired | Pin links to URL |
| Reddit | 40,000 | Not yet wired | Self-post or link |
| Bluesky | 300 | Accepted but not yet attached (AT Protocol blob pending) | Clickable |
| Threads | 500 | 1 image/video OR carousel (multiple URLs) | Clickable |
| Mastodon | 500 | Images and video supported | Clickable |

Key notes:
- Twitter/X: URLs always count ~23 chars; use `threadParts` for thread posts
- Twitter/X: GIF upload uses simple multipart (≤5 MB); larger GIFs may fail
- LinkedIn: only index 0 of `media[]` is used (one media per post)
- Threads: passing multiple `media[]` URLs triggers a carousel post
- Always verify with `GET /platforms/[platform]` — limits may change

---

## Error Reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | Validation error | Check required fields and value constraints |
| 400 | `"content policy"` (AI image) | Rephrase prompt |
| 400 | Already published / cancelled | Check post status before acting |
| 401 | Unauthorized | Check AI_API_KEY header |
| 403 | Forbidden | Token lacks access to this org |
| 404 | Not found | Verify the ID and orgId |
| 409 | Conflict | Duplicate action (e.g., re-publishing) |
| 422 | Validation error | Content exceeds limit, past date, etc. |
| 429 | Rate limited | Wait for `Retry-After` seconds |
| 500 | Server error | Retry with backoff |
| 502/503 | Platform unavailable | Target social platform is down; retry later |

Common validation error messages:
- `"content exceeds platform character limit"` — check platform constraints
- `"scheduledFor/scheduledAt must be a valid ISO date string"` — bad timestamp
- `"account not found or inactive"` — account may be disconnected
- `"Unsupported platform: X"` — check supported platform list
- `"Maximum 50 posts per bulk request"` — split into smaller batches

---

## AI Agent Patterns

### Rate Limiting

- **Standard endpoints**: 60 req/min
- **AI endpoints** (`/ai/*`): 20 req/min
- **Bulk**: 10 req/min

On 429: read `Retry-After` header and wait.

### Retry Pattern

```
Attempt 1: immediate
Attempt 2: wait 1s
Attempt 3: wait 4s
Attempt 4: wait 16s
Max: 4 attempts
```

Never retry 4xx (except 429).

### Efficient Patterns

1. **Fetch accounts once** — cache at session start; account IDs are needed for every post
2. **Bulk for standalone posts only** — use `/posts/bulk/` only when posts have NO `campaignId`. For campaign imports, always use single `POST /posts/` per post (bulk silently drops `campaignId`)
3. **Check health first** — `GET /health/` before a complex workflow if uptime is uncertain
4. **Timestamps are UTC** — convert from user's timezone: SAST = UTC+2, EST = UTC−5, PST = UTC−8
5. **Validate locally** — check content against platform char limits before the API call
6. **Use `/stats/` for summaries** — cheaper than full analytics for dashboards
7. **Pagination** — list endpoints use `page` + `limit`, not `offset`; inbox uses cursor (`startAfter`)

### Working with orgId

Every API call must include an `orgId`. There are several ways to obtain it:

1. **Ask the user** — the org ID is displayed on the organisation's Settings page at `/admin/settings` under "Organisation"
2. **List organisations** — `GET /api/v1/organizations` returns all orgs the user has access to, each with an `id` field
3. **From context** — if the user has mentioned or previously specified an org, reuse that ID

Always confirm the `orgId` before performing actions. Include it as a query param (GET) or body field (POST/PUT/PATCH) on every request.

### Content Generation Tips

- `/ai/generate`: use specific `prompt`, set `count: 3`, add `context` with company/audience details
- Always review AI output before scheduling
- Use `/ai/image-templates` to build prompts, then `/ai/image` to generate
- After image generation, register via `POST /media/` before attaching to posts

## Client Document Handoff

Use the `client-documents` skill for broader Social Media Strategy documents and client-facing campaign plans. Link broad strategy docs with `linked.campaignId` or `linked.socialPostIds`; keep individual post approval in the social post workflow unless Peet asks for a formal strategy sign-off.
