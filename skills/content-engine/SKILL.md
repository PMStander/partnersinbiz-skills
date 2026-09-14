---
name: content-engine
description: |
  End-to-end content engine for any PiB client. Produces a research dossier, brand identity lock, 12-week calendar, blog posts (with AI-generated bodies), 12 weeks of multi-platform social posts, hero images, and 6 short-form videos in 3 formats each (vertical Reel, 16:9 YouTube, 15s Stories) — all written directly into the Partners in Biz platform as a `campaign` that the client can review, approve, or request changes on at `/portal/campaigns/[id]`. The agent / operator monitors progress and approves at `/portal/campaigns/[id]`. A public read-only sales preview is available at `/c/[shareToken]`.

  Replaces the old `client-content-engine` skill which wrote to a separate Vercel preview site with localStorage approve buttons. Now there is one source of truth (Firestore via the PiB API), real audit logs, real tenant scoping, and shared records with the seo-sprint-manager skill.

  Use whenever the user asks to "build content", "produce a content engine", "do marketing for a client", "write blogs and social posts", "produce videos and social media", "build a content calendar", or anything that smells like a multi-channel content production run for a PiB client. Especially trigger on phrases like "do all of it", "produce everything", "12-week content plan", or "campaign for [client]".
---

# Content Engine (platform-first)

Take a PiB client from a research brief to ~75 production assets, all written into the platform as a single `campaign`. The pipeline output:

- **1 research dossier** — audiences, voice, taglines, channel mix, citations (saved on `campaign.research`)
- **1 brand identity lock** — palette, typography, aesthetic keywords, tone (saved on `campaign.brandIdentity`)
- **N content pillars + 12-week calendar** — saved on `campaign.pillars` and `campaign.calendar`
- **8 blog posts** — `seo_content` rows with AI-generated bodies in `seo_drafts`, status `review`, optionally linked to an active SEO sprint
- **6 short-form videos** rendered locally (HyperFrames + ffmpeg + procedural music), each in 3 formats (vertical Reel, 16:9 YouTube, 15s Stories) — uploaded via `/social/media/upload` and registered as a single `social_post` per slot with `media[0].type === 'video'`
- **12 weeks of social posts** — `social_post` rows, one per platform variant, status `pending_approval`, scheduled into `scheduledFor` slots from the calendar
- **Hero images + social card backgrounds** — uploaded via `/social/media/upload`, attached to the right blogs / posts

After the run, the agent prints:
- The campaign cockpit URL (`/portal/campaigns/[id]`) for ops
- The client portal URL (`/portal/campaigns/[id]`) for the client
- The public share URL (`/c/[shareToken]`) for sales pitches

When the run happens inside Messages, also emit a web-native `uiActions` entry so the human can open the side canvas with platform-faithful previews:

```json
{
  "id": "open-campaign",
  "type": "open_context",
  "label": "Preview campaign",
  "payload": { "kind": "campaign", "id": "<campaignId>", "label": "<campaign name>" }
}
```

Messages attaches the campaign context and opens the Context Dock with Instagram/LinkedIn/Facebook/X/YouTube/blog cards. For a single social post use `{ "kind": "social", "id": "<postId>" }` instead. Still include the cockpit/share URLs in the message text.

The user's job is to give you the client's domain, brand, and any constraints. Your job is to execute the pipeline — most of it parallelised across subagents — and surface a campaign the client can review.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## When to Use

- "build content for [client]" / "produce a content engine"
- "marketing materials for [client]" / "do all of it for [client]"
- "create a 12-week content plan with blog posts and videos"
- "I need a campaign with [N] posts and [M] videos"
- "do this for our [app / SaaS product]"
- Any time the user wants a multi-channel content production run for a PiB client

The skill is also useful for **subsets** — e.g. just videos, just blogs, just the calendar. Each phase is independent enough to run alone; just create the campaign first so everything has a home.

## Step 0 — Identify the Client Type (READ FIRST)

Before any other phase, identify which of three categories the client falls into. This determines the pillar names, tone, blog structure, image style, and distribution channels for the rest of the run. The pipeline + scripts are identical across types — only the content templates differ.

| Type | When to use | Examples | Read |
|---|---|---|---|
| **Service business** | Law, accounting, agencies, consultancies, advisors, brokers | AHS Law (default), small-business accountants, marketing agencies | [`references/client-types/service-business.md`](references/client-types/service-business.md) |
| **Consumer app** | Mobile apps, B2C web apps, lifestyle/productivity tools, creator software | Lumen (speed reading), Velox, fitness apps, education apps | [`references/client-types/consumer-app.md`](references/client-types/consumer-app.md) |
| **B2B SaaS** | Enterprise SaaS, vertical SaaS, dev tools, ops/HR/finance platforms | Loyalty Plus, Covalonic, sales tools | [`references/client-types/b2b-saas.md`](references/client-types/b2b-saas.md) |

If unclear, ask the user **once**. Don't ask for more detail than that.

After identifying, **read the relevant client-type file** before Phase 2. Mixed cases default to **B2B SaaS** for anything sold to a business, **service business** for anything where the company itself is the service.

## The Pipeline (9 phases — platform-first)

Run them in order. Phases 3–6 inside the production day can run heavily in parallel via subagents.

| Phase | What | Output destination | Reference |
|---|---|---|---|
| **0. Identify client type** | service / consumer-app / B2B SaaS | (decision) | [`references/client-types/`](references/client-types/) |
| **0a. Create campaign** | `POST /api/v1/campaigns` with `name`, `clientType`, empty placeholders | `campaigns/{id}` (capture `id` + `shareToken`) | (this file) |
| **1. Research** | last30days + WebSearch on the client's domain | `PATCH /campaigns/[id]` with `{ research }` | [`references/01-research.md`](references/01-research.md) |
| **2. Master plan** | Brand identity lock + pillars + 12-week calendar | `PATCH /campaigns/[id]` with `{ brandIdentity, pillars, calendar }` | [`references/02-master-plan.md`](references/02-master-plan.md) |
| **3. Parallel writing wave** | Dispatch 8 blog writers + 6 video composers + social writer | `seo_content` + `seo_drafts` + `social_posts` (all with `campaignId`) | [`references/03-parallel-agents.md`](references/03-parallel-agents.md) |
| **4. Image generation** | Imagen 4.0 + master style suffix | `/social/media/upload` → URLs attached to posts/blogs | [`references/04-image-generation.md`](references/04-image-generation.md) |
| **5. Video production** | HyperFrames + ffmpeg + procedural music by default; Higgsfield CLI optional for UGC/cinematic/product-demo clips when authenticated — runs LOCALLY | `/social/media/upload` × 3 → single `social_post` with multi-format `media[0]` | [`references/05-video-production.md`](references/05-video-production.md) |
| **6. Social card backgrounds** | Reusable card images | `/social/media/upload` → URLs referenced on relevant posts | (covered in master plan) |
| **7. Preview** | Public share URL: `https://partnersinbiz.online/c/[shareToken]` | (no work — already live the moment the campaign exists) | (this file) |
| **8. Final summary** | Print campaign cockpit + portal + share URLs and asset counts | (stdout) | (this file) |
| **9. Import from local** | Skip Phases 1–6 entirely when local content already exists from a previous run — use this canonical playbook to push existing `marketing/` content into a campaign on the platform | All four collections (`campaigns`, `seo_content`, `seo_drafts`, `social_posts`) | [`references/09-import-from-local.md`](references/09-import-from-local.md) |

**Always read the relevant reference file before executing the phase.** They contain the prompts, code snippets, and gotchas that took a real production run to learn.

> **For repeat runs / clients with existing content:** Phase 9 is the entry point, not Phase 0. If the client's `marketing/` folder already has blog-posts/, videos/, and social-media/ markdown, jump straight to [`references/09-import-from-local.md`](references/09-import-from-local.md) — running Phases 1–6 will regenerate content that may already be approved.

For **app-specific work** (consumer apps), Phase 4 has a parallel sibling — run the `aso-appstore-screenshots` skill alongside Phase 4 to produce App Store / Play Store screenshots. The two skills compose cleanly.

## Auth + base URL

```
Authorization: Bearer <pib_dlg_...>        # interactive/human-triggered runs (see Auth (mandatory) above)
Authorization: Bearer ${AI_API_KEY}        # cron/system runs only, from env or ~/.env, NEVER hard-coded
X-Org-Id: <org id resolved via GET /api/v1/organizations and slug match>
Base URL: https://partnersinbiz.online/api/v1
```

The `ai` role (system key, cron/system only) bypasses tenant restrictions, so the engine can run for any client. Resolve `X-Org-Id` once at the start of a run from the client's slug or name and reuse it for every call.

Idempotency: every write that could be retried uses an `Idempotency-Key` header. Keys follow the pattern `pib-engine-{campaignId}-{slot}-{platform}-{format}` so a retry on the same slot is safe.

## ⚠ Firestore-direct writes for fields the API can't set

Several blog fields are NOT in any API allow-list and MUST be written via Firebase Admin SDK directly into Firestore. The platform's own [import-pib-content.py](https://github.com/anthropics/) script does this and leaves a comment `"# fields not in PATCH allow-list"`. Stop trying to attach them via PATCH — you'll get `success: true` but the fields silently disappear.

| Field | Set how | Why |
|---|---|---|
| `heroImageUrl` (on `seo_content`) | Firestore Admin: `db.collection("seo_content").doc(id).update({heroImageUrl: ...})` | Not in PATCH allow-list |
| `draftPostId` (on `seo_content`)  | Firestore Admin (same as above)       | Not in PATCH allow-list, but the `POST /seo/content/[id]/draft` endpoint returns it — capture and persist it manually |
| Blog body for **imported** content | Firestore Admin: `db.collection("seo_drafts").doc(id).set({body, ...})` | The `/draft` endpoint always invokes AI; if you want imported markdown, write the draft directly |

**Setup** (once per Cowork session, takes ~10 lines of Python):

```python
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

ENV_PATH = Path("/Users/peetstander/Cowork/Partners in Biz — Client Growth/partnersinbiz-web/.env.local")
env = {k:v.strip().strip('"') for k,_,v in (l.partition("=") for l in ENV_PATH.read_text().splitlines() if "=" in l and not l.startswith("#"))}

if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate({
        "type": "service_account",
        "project_id":   env["FIREBASE_ADMIN_PROJECT_ID"],
        "client_email": env["FIREBASE_ADMIN_CLIENT_EMAIL"],
        "private_key":  env["FIREBASE_ADMIN_PRIVATE_KEY"].replace("\\n", "\n"),
        "token_uri":    "https://oauth2.googleapis.com/token",
    }))
db = firestore.client()

# Now you can write:
db.collection("seo_content").document(blog_id).update({
    "heroImageUrl": uploaded_url,
    "draftPostId":  draft_id,
})
```

Use this for **every blog you create**, immediately after generating the draft. The page template at `/admin/org/[slug]/social/[campaignId]?tab=blogs` won't render images or open the body editor unless these two fields are set on the `seo_content` doc.

## API endpoints used

```
# Campaigns (Slice A)
POST   /campaigns                              create campaign at start of run
GET    /campaigns/[id]                         re-read after patches
PATCH  /campaigns/[id]                         patch research, brand, pillars, calendar
GET    /campaigns/[id]/assets                  roll-up to verify output
GET    /public/campaigns/[shareToken]          public read-only campaign share payload

# SEO (existing)
GET    /seo/sprints?status=active&clientId={orgId}    find an active sprint to attach blogs to
POST   /seo/sprints                                   create sprint — REQUIRES siteUrl + siteName
POST   /seo/sprints/{sprintId}/content                create blog (with campaignId)
POST   /seo/content/[id]/draft                        generate AI body — returns draftPostId
PATCH  /seo/content/[id]                              ⚠ allow-list now includes heroImageUrl +
                                                        draftPostId (verified 2026-08-04 in
                                                        app/api/v1/seo/content/[id]/route.ts ALLOWED)
                                                        — no Firebase Admin write needed anymore

# Social (existing)
POST   /social/posts                                  create social post (with campaignId)
PUT    /social/posts/[id]                             attach media (image OR video multi-format)
POST   /social/media/upload                           multipart upload, returns { url }

# Tenant resolution
GET    /organizations                                 resolve org id from slug

# Inline review surface (NEW — clients use this; agents read from it)
GET    /seo/content/[id]/comments                     list comments incl. `anchor`
POST   /seo/content/[id]/comments                     accepts `{ text, anchor? }` — see below
GET    /social/posts/[id]/comments                    list comments incl. `anchor`
POST   /social/posts/[id]/comments                    accepts `{ text, anchor? }` — see below
PATCH  /seo/drafts/[id]                               client/admin edit `{ body, title?, metaDescription? }` — emits `seo_content_edited`
```

### The `anchor` field (NEW — read this when picking up changes)

When a client leaves feedback in the org-themed review UI
(`/admin/org/[slug]/social/[id]/blog/[blogId]`), comments carry an optional
`anchor` so we know exactly what they pointed at:

```json
{
  "id": "...",
  "text": "Tone is too corporate here, can we soften?",
  "userRole": "client",
  "anchor": { "type": "text", "text": "Most agency owners find out their site maintenance process…" }
}
```

`anchor.type` is `"text"` (selection in the body) or `"image"` (with `mediaUrl`
instead of `text`). Activity log entries (`seo_content_commented`,
`seo_content_changes_requested`, `social_post_commented`) already include the
anchor preview in their `description`, so an agent loop that watches activity
sees what was flagged without re-fetching.

**When you regenerate a section in response to a comment, log a reply on the
same comment** (or post a follow-up) so the client sees you addressed it.

### Client-edited bodies (NEW — don't overwrite without checking)

Clients can now click "Edit body" in the review UI and save changes via
`PATCH /seo/drafts/[id]`. That fires a `seo_content_edited` activity event
with `actorRole: "client"`. Before regenerating a draft, check for this event
on the entity — if a client has edited recently, confirm with the operator
before clobbering their changes. Treat the post-edit body as the new source
of truth.

### Taking a campaign live (NEW — bulk schedule + auto-publish to /insights)

After approval, two endpoints turn the campaign into live distribution:

```
POST /api/v1/campaigns/[id]/schedule
  body: { startDate?, mode?: 'auto'|'calendar'|'cadence', cadence?: { postsPerDay, hours, daysOfWeek }, platforms?, includePending?, dryRun? }
```

Bulk-schedules every `approved` social_post + video on the campaign across
the campaign's `calendar` (preferred) or a configurable cadence. Each post
gets `scheduledFor` + `status='scheduled'` plus a matching `social_queue`
entry — the existing `/api/cron/social` worker (5 min interval Cloud Function
+ daily Vercel cron) picks them up and publishes via the connected OAuth
provider. Use `dryRun: true` first to preview the schedule.

```
POST /api/v1/seo/content/[id]/publish
  → now also persists a `slug` on seo_content
```

The public reader at `/insights/[slug]` queries `seo_content` where
`status='live'` AND `slug == ?` and hydrates the body from `seo_drafts`.
Approving a blog now actually publishes it to the public site — no manual
`lib/content/posts.ts` edit. The slug is derived from `body.slug` →
`data.slug` → `targetUrl` path → slugified title, in that order.

For end-of-run handoff, point the operator at:
1. Connect social accounts: `/portal/social/accounts`
2. Bulk schedule: `POST /api/v1/campaigns/[id]/schedule { startDate, dryRun: true }`, review, then run again with `dryRun: false`
3. Approve all blogs (each fires the publish flow): `POST /api/v1/campaigns/[id]/approve-all { type: 'seo_content' }`

### Review URLs (prefer the org-scoped routes)

The admin marketing-preview UI (Research / Blog Posts / Instagram / Reels
& TikTok / Stories / Facebook / LinkedIn / YouTube tabs) lives at:

```
/admin/org/[slug]/social                       campaign index for the client
/admin/org/[slug]/social/[campaignId]          drill-in (replaces /portal/campaigns/[id])
/admin/org/[slug]/social/[campaignId]/blog/[blogId]   inline-comment + WYSIWYG-edit blog detail
```

Use these in run-summary output and end-of-run handoff messages instead of
the older flat `/portal/campaigns/[id]/...` paths — the org-scoped route
applies the client's brand colours to the chrome.

## How this composes with seo-sprint-manager

Three explicit seams:

1. **Active sprint linkage.** Phase 3 calls `GET /seo/sprints?status=active&clientId={orgId}` first. If a sprint exists, blogs are created via `POST /seo/sprints/{sprintId}/content` with `campaignId` set — they show up in BOTH the sprint pipeline and the campaign roll-up. If no active sprint, blogs are created via the campaign-only path and the run summary flags this so the operator can attach a sprint later.
2. **Shared `seo_content` rows.** A blog written by content-engine is a real `seo_content` row with `campaignId` AND optionally `sprintId`. The seo-sprint-manager's daily flow (`/seo/today`, ranking checks, refresh suggestions) operates on the same row. There is one record, not two.
3. **Refresh path.** When seo-sprint-manager later flags a blog for refresh, it works against the same `seo_content` ID. The campaign roll-up keeps showing the blog with its current draft. The campaign is a moment-in-time grouping; the SEO sprint is a continuously maintained strategy. They share the artefact.

## Folder Structure to Create (much smaller now)

Almost everything lives in the platform. The local workspace is now just for things that have to be rendered locally and for working scratch:

```
<client-workspace>/
└── content-engine/
    ├── tmp/                          ← scratch / partial JSON / cached research
    ├── images/
    │   └── blog/                     ← Imagen output BEFORE upload to /media/upload
    └── videos/
        ├── audio/
        │   └── <slug>-underscore.{wav,mp3}    ← procedural music
        ├── V1-…/{index.html, script.md, README.md, *.mp4}
        ├── youtube/                  ← 16:9 horizontal cuts
        └── stories/                  ← 15s vertical cuts
```

After each asset is uploaded to the platform, the local file is no longer the source of truth — `tmp/` and `images/blog/` can be cleaned up. `videos/` is worth keeping for re-render runs.

## Firebase Storage discipline (every asset, every time)

The platform — not the local filesystem — is where every deliverable lives. Each render variant of a video, each hero image, each social-card background MUST be uploaded to Firebase Storage via `POST /api/v1/social/media/upload` and referenced by URL on the relevant `social_post` / `seo_content` record.

**For videos** that means **all three** format files per slot — vertical Reel, 16:9 YouTube cut, 15s Stories cut — all uploaded, then registered on a single post via `media[0].{url, urlYoutube, urlStories, durationSec}`. A campaign with 6 videos = 18 storage uploads + 6 social_posts. See `references/05-video-production.md` for the upload + post-registration flow.

**Re-renders** (e.g. responding to a client comment that requested changes) follow the same path: render → upload → `PUT /api/v1/social/posts/{id}` with the new `media` array. Do not edit the local mp4 in place and call it done — it must round-trip through `/social/media/upload` so the URL and the `social_media` row exist in Firestore.

If you find an asset on disk that has no corresponding Firebase URL, treat it as work-in-progress, not a deliverable. The campaign roll-up reads from the platform; if it's not there, it doesn't exist.

## Brand Identity (Always Lock First)

Before writing any content, lock the brand. These go on `campaign.brandIdentity`:

| Element | Why it matters |
|---|---|
| Palette (hex codes for bg / accent / alert / text / muted) | Used in image prompts, video DESIGN.md, social card overlays, and by the platform-mockup review UI to render real-looking previews |
| Typography (heading / body / numeric fonts) | Used in video compositions, social card design specs, and the review UI |
| Logo URL + aesthetic keywords + tone | Used everywhere — image prompts, blog tone-of-voice block, social caption agents |

Inspect the client's existing website source if available — `grep` for hex codes and `font-family`. That's faster than asking. If the client has no site, ask the user 4 questions: light or dark canvas, primary accent colour, headline font preference, mood (premium / playful / technical).

Once locked, `PATCH /campaigns/[id]` with the brand identity. Every subsequent asset references this same record, so brand changes mid-run automatically re-render in the review UI mockups.

## The Production Day Cadence

A realistic single-day run looks like:

- **Hour 0** (5 min): Phase 0a — create campaign, capture id + shareToken
- **Hour 1**: Phase 1 (research) + Phase 2 (master plan) → both PATCH the campaign
- **Hours 2–3**: Phase 3 (dispatch ~15 parallel agents → all 8 blogs + 6 video scripts + social posts come back, written straight into the platform)
- **Hour 4**: Phase 4 (image gen, parallel via Imagen) + Phase 5 starts (video render, parallel via HyperFrames) + Phase 6 (social card backgrounds)
- **Hour 5**: Music generation + multi-format video renders (YouTube horizontal + Stories 15s cuts) + uploads
- **Hour 6**: Phase 7 — print the share URL. Phase 8 summary. Done.

Spend most of your active time on Phase 3's prompts (the agent briefs determine quality) and on Phase 2's brand lock (the review UI mockups depend on it).

## Higgsfield creative generation option

Use Higgsfield through the CLI, not MCP, for Hermes/Codex/OpenClaw-style agent work. Official Higgsfield docs say the CLI path is preferred for Hermes; MCP remains possible for connector-style clients but is not required for this content-engine pipeline.

Current runtime rule:
- If `higgsfield account status` succeeds, Phase 5 may use Higgsfield for UGC ads, product demos, cinematic image-to-video, Soul character continuity, viral clip generation, and virality prediction.
- If Higgsfield is not authenticated, do not block the campaign. Produce Higgsfield-ready prompt packs and continue with the deterministic HyperFrames/ffmpeg video route.
- Every generated Higgsfield asset is still work-in-progress until uploaded through `/social/media/upload` and attached to the campaign social post. The PiB platform remains the source of truth.
- Do not publish, schedule, client-send, or launch ads from Higgsfield output without the normal approval gate.

Useful CLI checks:

```bash
which higgsfield
higgsfield --version
higgsfield account status
higgsfield model list
```

Official skills discovered from `higgsfield-ai/skills`: `higgsfield-generate`, `higgsfield-product-photoshoot`, `higgsfield-marketplace-cards`, and `higgsfield-soul-id`. In PiB campaign work, prefer `higgsfield-generate` for videos/UGC/virality, `higgsfield-product-photoshoot` for hero and ad images, and `higgsfield-soul-id` only when approved reference photos exist.

## Bundled Scripts (use these — don't rewrite)

1. **`scripts/generate-image.py`** — Imagen 4.0 wrapper. Auto-appends a configurable master style suffix to every prompt. Supported aspect ratios: `1:1, 9:16, 16:9, 4:3, 3:4` (NOT `3:2`). Output goes to local `images/blog/` first, then is uploaded via `/social/media/upload`.
2. **`scripts/generate-underscore.py`** — Procedural music generator. Writes a 40-second cinematic underscore in Cmaj7. Outputs WAV; convert with `ffmpeg -i in.wav -c:a libmp3lame -b:a 192k out.mp3`.
3. **`scripts/build-preview.py`** — **DEPRECATED / LEGACY.** Old throwaway-Vercel preview-site builder. Kept only for backfill flows (importing historical AHS Law / scrolledbrain content into a real campaign). Do not use for new runs.

## Bundled Assets (copy these as starters)

- **`assets/composition-template.html`** — **REQUIRED** for Phase 5. Brand-agnostic HyperFrames composition with the working pattern (paused master timeline, single `window.__timelines` registration, no inline sequencer). Copy + sed-substitute for each video. Worked example values are inline at the bottom of the file. Do NOT generate compositions from scratch — the lint requirements are easy to violate and produce black frames.
- **`assets/DESIGN-template.md`** — HyperFrames DESIGN.md skeleton with palette/typography/motion fields
- **`assets/prompts-template.md`** — Image prompt library skeleton (master suffix + per-blog prompts)
- **`assets/HOW-TO-USE-template.md`** — The 3-layer mental model guide (image → on-image text → caption)
- **`assets/vercel.json`** — Legacy, only relevant for the deprecated preview builder

## Phase summary output (end of run)

After all phases complete, the skill prints:

```
Campaign created: <campaignId>
Share URL: https://partnersinbiz.online/c/<shareToken>
Admin cockpit: https://partnersinbiz.online/admin/org/<slug>/social/<campaignId>
Client portal: https://partnersinbiz.online/portal/campaigns/<campaignId>

Assets produced:
  - Blogs: N (all in `review` status)
  - Social posts: N (all in `pending_approval` status)
  - Videos: N (with 3-format renders each)
  - Images: N (attached to posts/blogs)

SEO sprint: <linked sprintId | "no active sprint — flag for operator">

Next step: <human> reviews at <admin cockpit url>, approves or requests changes.
Approved assets schedule into the platform's social queue and SEO publish flow automatically.
```

## Quality gate before sharing a campaign preview

Before handing a campaign URL to Peet/client/operator, verify the public or admin preview itself, not just API counts:

1. Open the share/admin URL and confirm the visible cards show the correct client brand name/avatar, not `yourbrand`, `Your Brand`, or `NO IMAGE` placeholders.
2. If using `campaign.brandIdentity` directly in the public `/c/[shareToken]` preview, include both content-engine fields and preview-card aliases: `name`, `logoUrl`, `palette.bg`, `palette.accent`, `palette.alert`, `palette.text`, plus the usual `background/surface/accent/text` keys. Otherwise the preview chrome falls back to generic placeholders.
3. Do not create social-post records that are only Higgsfield prompts/scripts unless the campaign is explicitly a prompt-pack deliverable. For reviewable content, each social/video record must have final media attached or be clearly held outside the campaign.
4. For video campaigns, `content` should be clean publish/review copy, not a pasted prompt dump. Keep Higgsfield prompts in a document/manifest, comment, or wiki note.
5. If avoiding Higgsfield credit spend, use existing approved media or deterministic screenshot/app-demo videos from real client screenshots; still upload through `/social/media/upload` and attach `media[0].type = 'video'`, `url`, `urlYoutube`, and `urlStories`.
6. Verify `/campaigns/[id]/assets` after repair: expected video count, zero empty-media social stragglers, all assets still in draft/review state unless approval covers scheduling/publishing.

## Critical Lessons (from the real run — preserved verbatim)

These are the gotchas that cost real time on the AHS Law run. Don't repeat them.

| Issue | Fix |
|---|---|
| HyperFrames lint error: composition not found | Use `index.html` as the filename, not `composition.html` |
| Scenes invisible during render | Add `class="scene clip"` (the `clip` class is what enables timing-based visibility) |
| Root composition warning | Add `data-start="0" data-duration="N"` to the root `<div data-composition-id="…">` |
| Imagen rejects 3:2 aspect | Use `16:9` for blog heroes — it's close enough |
| Imagen-3 returns 404 | The current model is `imagen-4.0-generate-001`, not `imagen-3.0-generate-002` |
| Suno API "skill" requires manual web UI | Use `scripts/generate-underscore.py` for procedural music — good enough for B2B underscore |
| macOS bash 3.2 doesn't support `declare -A` | Use shell functions or parallel arrays instead |
| `awk` inside heredoc with double-quoted ffmpeg filter | Escaping mangles the awk script — hardcode values instead |
| last30days X auth fails (HTTP 400) | The token may be expired; compensate with heavier WebSearch coverage |
| Videos show blank / `<video>` tag | HyperFrames produces HTML — render to MP4 with the bundled ffmpeg script before uploading |
| Old client brand bleeding into a new run | Read `campaign.brandIdentity` from the API at the start of every phase — never cache it across runs |
| Same payload retried twice = duplicate post | Always set `Idempotency-Key: pib-engine-{campaignId}-{slot}-{platform}-{format}` on writes |
| `/seo/content` 404 because no active sprint | Skip the sprint linkage and flag in the run summary; campaign-only path still works |
| AI_API_KEY missing | Read from env; fall back to `~/.env`; never hard-code or log it |

## Output to the User Each Phase

After each phase, give the user a short status report — endpoints called, IDs returned, counts, any decisions. The user can interrupt mid-pipeline to redirect (different blog topic, different palette, different platforms). Don't ask for permission at every step — execute and report.

After the final phase, print the **campaign cockpit URL**, the **client portal URL**, and the **public share URL** (see "Phase summary output" above), with asset counts and the SEO-sprint linkage status.

## Reference Examples

- **Partners in Biz** itself (service business / B2B SaaS hybrid): `/Users/peetstander/Cowork/Partners in Biz — Client Growth/` — canonical example.
- **AHS Law** (service business): `/Users/peetstander/Cowork/partners/AHS Law/` — older local-files-only example. Use only for content format reference, not as a template — it predates the platform-first flow.

When in doubt about blog format: read an existing `seo_content` row + its `seo_drafts` body via the API.  
When in doubt about social format: read an existing `social_post` row via the API.  
When in doubt about video format: read [`references/05-video-production.md`](references/05-video-production.md).

## Client Document Handoff

For major client-facing runs, create or link a Content Campaign Plan document through the `client-documents` skill. Link it with `linked.campaignId` and use the document for strategy, assumptions, comments, and client approval; keep individual post approval in the social campaign workflow.
