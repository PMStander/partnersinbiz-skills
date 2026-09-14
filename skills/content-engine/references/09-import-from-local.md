# Phase 9 — Import Existing Local Content into a Campaign

When a client's `marketing/` folder already contains blog posts, videos, social
captions, and images from a previous content-engine run (or a manual production
sprint), use this playbook to land them on the platform as a single approvable
campaign. **Do not run Phases 1–6 from scratch** — those would regenerate
content the client may have already approved.

This is the playbook used to import AHS Law on 2026-05-09. It is canonical.
Every step here was forced by a real platform constraint discovered by reading
the route handlers — do not skip steps "because it looks like the API allows it".

## Pre-flight checklist

Run these once at the top — abort if any fail:

```bash
WORKSPACE="/Users/peetstander/Cowork/partners/<CLIENT>"

# 1. Marketing folder structure — at minimum need ONE of (blogs / videos / social)
ls "$WORKSPACE/marketing/blog-posts/"   2>/dev/null | head -3
ls "$WORKSPACE/marketing/videos/"       2>/dev/null | head -3
ls "$WORKSPACE/marketing/social-media/" 2>/dev/null | head -3
ls "$WORKSPACE/marketing/images/blog/"  2>/dev/null | head -3

# 2. Master plan (we read brand identity, pillars, calendar from this)
ls "$WORKSPACE/marketing/plans/content-master-plan.md" || \
  ls "$WORKSPACE/marketing/CONTENT_MASTER_PLAN.md"      || \
  echo "WARNING: no master plan — pillars/research will need to be inferred"

# 3. Platform credentials
[ -n "$AI_API_KEY" ] || echo "set AI_API_KEY"
[ -f "/Users/peetstander/Cowork/Partners in Biz — Client Growth/partnersinbiz-web/.env.local" ] \
  || { echo "Firebase admin creds missing — heroImageUrl writes will fail"; exit 1; }

# 4. SF Pro Display fonts present (for compositing card images)
ls /Library/Fonts/SF-Pro-Display-Bold.otf || echo "install SF Pro before compositing"
```

## The 9 steps (in order — no skipping)

```
0. Resolve org_id from client slug          → GET /organizations
1. Create campaign + capture id + token     → POST /campaigns
2. Upload brand profile to org              → PUT /agent/brand/{orgId}
3. PATCH campaign with the four template-strict fields:
       research, brandIdentity, pillars, calendar
4. Create SEO sprint                        → POST /seo/sprints
5. Create + populate 8 blogs:
       a. POST /seo/sprints/{sid}/content   (one per blog)
       b. POST /seo/content/{cid}/draft     (AI body — capture draftPostId)
       c. Upload hero image                 → POST /social/media/upload
       d. ⚠ Firebase Admin direct write    db.collection("seo_content")
              .doc(cid).update({heroImageUrl, draftPostId})
6. Composite + upload 12 social card images → Pillow + POST /social/media/upload
7. Create 36 social posts (W01-W12 × 3):
       POST /social/posts (one at a time — bulk drops campaignId)
       POST /social/posts/{id}/submit
8. Create 6 video posts:
       POST /social/posts with media[0]={type:"video", url, urlYoutube, urlStories}
       POST /social/posts/{id}/submit
9. Activate campaign                        → PATCH /campaigns/{id} {status:"active"}
```

## Field shapes the template demands (THESE ARE STRICT)

If you get any of these wrong, the drill-in page either crashes with
`t.map is not a function` or renders empty cards.

```python
# campaign.research
research = {
  "audiences":  [{"id": "A", "label": "...", "painPoints": ["..."]}, ...],
  "voice":      {"do": ["..."], "dont": ["..."]},
  "taglines":   {"master": "...", "layered": {"hero": "...", "sub": "...", "cta": "..."}},
  "citations":  [{"quote": "...", "source": "https://..."}, ...],
  "channels":   {"primary": ["blog","linkedin"], "secondary": [...], "experimental": []},
  "confidence": "high",
  "notes":      "..."
}

# campaign.brandIdentity (note: aestheticKEYWORDS, not aesthetic)
brandIdentity = {
  "palette":   {"bg": "#...", "accent": "#...", "alert": "#...", "text": "#...", "muted": "#...", "surface": "#..."},
  "typography":{"heading": "Font, sans-serif", "body": "Font, sans-serif", "mono": "...", "weights": "400, 600, 700"},
  "aestheticKeywords": ["minimal", "premium", ...],   # array of strings
  "tone":      "..."
}

# campaign.pillars — flat array
pillars = [{"id": "kebab-id", "name": "...", "description": "...", "weight": 1.5}, ...]

# campaign.calendar — flat day-level entries (NOT [{week, slots}])
calendar = [
  {"day": 1, "date": "2026-05-12", "pillarId": "labour", "channel": "blog",   "format": "pillar-blog",         "title": "...", "week": 1},
  {"day": 3, "date": "2026-05-14", "pillarId": "labour", "channel": "video",  "format": "short-form-video",    "title": "...", "week": 1},
  {"day": 5, "date": "2026-05-16", "pillarId": "labour", "channel": "social", "format": "multi-platform-social","title": "...", "week": 1},
  ...
]
```

## Firebase Admin SDK — legacy for heroImageUrl + draftPostId

As of 2026-08-04 the `PATCH /seo/content/[id]` allow-list includes
`heroImageUrl` and `draftPostId` (see route ALLOWED const), so the Firebase
Admin direct write below is no longer required. Keep it as a fallback if a
deployed API version lags the repo.

```python
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

ENV_PATH = Path("/Users/peetstander/Cowork/Partners in Biz — Client Growth/partnersinbiz-web/.env.local")
env = {k:v.strip().strip('"') for k,_,v in
       (l.partition("=") for l in ENV_PATH.read_text().splitlines()
        if "=" in l and not l.startswith("#"))}

if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate({
        "type":         "service_account",
        "project_id":   env["FIREBASE_ADMIN_PROJECT_ID"],
        "client_email": env["FIREBASE_ADMIN_CLIENT_EMAIL"],
        "private_key":  env["FIREBASE_ADMIN_PRIVATE_KEY"].replace("\\n", "\n"),
        "token_uri":    "https://oauth2.googleapis.com/token",
    }))
db = firestore.client()

# After every blog draft creation:
db.collection("seo_content").document(content_id).update({
    "heroImageUrl": uploaded_hero_url,
    "draftPostId":  draft_id_from_post_response,
})
```

## Video posts — exact media shape

The "Reels & TikTok" tab on the campaign page filters `social_posts` for
`media[0].type === "video"`. There is no separate videos collection.

```python
{
  "orgId":      ORG,
  "campaignId": CAMP,
  "platforms":  ["instagram"],
  "content":    {"text": "<caption>"},
  "media": [{
    "type":         "video",
    "url":          "https://firebasestorage.../V1.mp4",
    "thumbnailUrl": "<same as url or a poster frame>",
    "urlYoutube":   "https://firebasestorage.../V1-youtube.mp4",
    "urlStories":   "https://firebasestorage.../V1-stories.mp4",
    "durationSec":  32,
    "altText":      "<video title>",
    "order":        0,
  }],
  "tags":     ["video:V1-slug", "pillar:..."],
  "category": "work",
}
```

After creating: `POST /social/posts/{id}/submit` to push to client_review.

## Social cards — composite text on backgrounds

The 3 social card backgrounds (`quote-card-bg.png`, `stat-card-bg.png`,
`myth-fact-bg.png`) need text overlaid before posts look right. Use Pillow
+ SF Pro Display. Reference: `/tmp/ahs_composite_cards.py` from the AHS run.
Pattern: render → save to `/tmp/<client>_social_cards/W01.png` → upload via
`POST /social/media/upload` → use the returned URL when creating each of the
3 platform posts (LinkedIn, Instagram, Facebook) for that week.

## Common API gotchas (re-stating, since they bite every run)

| Symptom | Cause | Fix |
|---|---|---|
| Campaign drill-in page 404s | `status: "draft"` | PATCH to `"active"` |
| Drill-in page crashes `t.map is not a function` | Calendar is nested `[{week,slots}]` | Flatten to day-level entries |
| Posts created but `campaignId` is null | Used `POST /social/posts/bulk` | Use single `POST /social/posts` |
| Posts stuck as `draft` after creation | `pending_approval` ignored on create | Call `POST /social/posts/{id}/submit` |
| Reels & TikTok tab is empty | `media[0].type !== "video"` on video posts | PUT updates with correct shape |
| Blog cards have no images | `heroImageUrl` wasn't set (silently dropped by PATCH) | Firebase Admin direct write |
| Blog detail page has no body | No `draftPostId` on seo_content | POST /draft, then Firebase Admin write |
| Firestore writes fail | `.env.local` not loaded or private_key not unescaped | `.replace("\\n", "\n")` on private_key |
| `POST /seo/sprints` 400 | Missing `siteUrl` or `siteName` | Both are required |
| Image upload returns "X-Org-Id required" | Missing header on multipart upload | Add `-H "X-Org-Id: $ORG"` |
| Video upload corrupts | Default mime type | Use `-F "file=@path;type=video/mp4"` |

## Output the operator brief at the end

The handoff message to print after the import succeeds:

```
Campaign created: <id>
Status: active
Review URL:    https://partnersinbiz.online/admin/org/<slug>/social/<id>
Public share:  https://partnersinbiz.online/c/<shareToken>

Assets imported:
  - Blogs:  N (all with hero + AI-drafted body, status: review)
  - Social: 36 (all with composited card images, status: client_review)
  - Videos: 6 (multi-format, status: client_review)

To take it live:
  1. Operator reviews + approves at the review URL
  2. Once approved, run: POST /campaigns/<id>/schedule { startDate, dryRun: true }
  3. Confirm the dry-run looks right, then run again with dryRun: false
```

## Time budget

A clean import run on a fully-prepared marketing folder: **20–30 minutes**.
Anything longer means something hit a "common gotcha" above and the recipe
above wasn't followed in order.
