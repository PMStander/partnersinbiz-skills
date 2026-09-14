# Phase 5 — Video Production

After the parallel writing wave, you have 6 video scripts (`marketing/videos/V*/script.md`). This phase turns each into one MP4 in three formats (Reel 9:16, YouTube 16:9, Stories 15s), uploads everything to Firebase Storage, and registers a single `social_post` per slot with multi-format `media[0]`.

The pipeline has been validated end-to-end on AHS Law and Partners in Biz. Follow it.

## Optional Step - Higgsfield CLI creative source

Use this branch when the campaign needs AI UGC, product-demo, cinematic image-to-video, avatar/Soul continuity, viral clip extraction, or pre-publish virality analysis. For Hermes, prefer Higgsfield CLI over MCP because the official Higgsfield CLI page says Hermes/Codex/OpenClaw users are better served by CLI. MCP can stay unconfigured unless a connector-style workflow is explicitly needed.

Prerequisite checks:

```bash
which higgsfield || npm install -g @higgsfield/cli
higgsfield --version
higgsfield account status
```

If `higgsfield account status` returns `Not authenticated`, ask Peet to run `higgsfield auth login` in the Maya/VPS shell and complete the browser/device login. Do not invent output or mark live generation as working until `higgsfield model list` succeeds.

When authenticated:

1. Read `campaign.brandIdentity`, the video slot brief, target platform, CTA, and forbidden claims.
2. Use `higgsfield model list` / `higgsfield workflow list` to choose the current model or workflow instead of hard-coding stale model names.
3. Use Marketing Studio / `higgsfield-generate` for UGC ads, product demos, unboxing, TV spot, presenter videos, and virality prediction.
4. Save the returned media URL/job output in the local manifest with prompt, model/workflow, source assets, and generation ID.
5. Download/export to local MP4 if needed, then still create the same three campaign formats: vertical full, YouTube 16:9, and Stories 15s.
6. Upload all final files through `/api/v1/social/media/upload` and attach them to one `social_post` with `media[0].url`, `urlYoutube`, and `urlStories`.

Fallback rule: if Higgsfield is unauthenticated, out of credits, or the job fails, continue with the HyperFrames route below and save a Higgsfield-ready prompt pack for later regeneration.


## Step 0 — Generate or fix each composition (LINT MUST PASS)

Every `V*/index.html` MUST satisfy these hard rules or HyperFrames will refuse to render (or render black frames):

| Rule | Why it matters |
|---|---|
| Root `<div>` carries `data-composition-id`, `data-width="1080"`, `data-height="1920"`, `data-start="0"`, `data-duration="N"` | The CLI reads dimensions + total length here. |
| Each scene is `<div class="scene clip" data-start="X" data-duration="Y">` | The `clip` class is what enables timing-based visibility. |
| ONE master GSAP timeline, created with `paused: true`, registered on `window.__timelines["<comp-id>"] = tl` | The runtime calls `tl.seek(t)` per frame. Without registration, scenes stay at their `from()` start state (everything opacity 0). |
| GSAP CDN included via `<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>` at body end | Required before the timeline-builder script. |

**Patterns that BREAK the render — do not use:**
- Custom inline scene-sequencer that hides scenes with `display: none` and ticks via `requestAnimationFrame`. The runtime uses virtual time, so RAF doesn't fire — every scene stays hidden. *Both AHS Law (which works) and PiB (which initially didn't) have proven this.*
- Multiple separate timelines (`tl1, tl2, tl3, tl4`) with `delay: N`. They register only one or none, and HyperFrames seeks the wrong thing. Always combine into one master and use the absolute-position parameter on `tl.from()` / `tl.to()`.
- `.scene` rules that set `display: none` baseline. Let HyperFrames manage clip visibility natively.

**Use the bundled template.** Copy `assets/composition-template.html` into each `marketing/videos/V<N>-<slug>/index.html` and substitute the `{{...}}` placeholders. The template has the full working pattern: stamp scene → 3 numbered list items → reveal → end card, all on a single paused master timeline. Worked example values are inline at the bottom of the template file.

```bash
cd <client-workspace>/marketing/videos
for slug in V1-... V2-... V3-... V4-... V5-... V6-...; do
  mkdir -p "$slug"
  cp ~/Cowork/.claude/skills/content-engine/assets/composition-template.html "$slug/index.html"
  # then sed/python-replace the {{...}} placeholders for each video's content
done
```

After substitution, lint everything and fix anything that still flags:

```bash
for d in V1-* V2-* V3-* V4-* V5-* V6-*; do
  echo "=== $d ==="
  hyperframes lint "$d" 2>&1 | grep -E "^◇|✗"
done
```

Target: every composition shows `0 error(s), N warning(s)`. Warnings are fine; errors are not.

## Step 1 — Render in parallel

```bash
cd <client-workspace>/marketing/videos
for d in V1-* V2-* V3-* V4-* V5-* V6-*; do
  hyperframes render "$d" -o "$d/$d.mp4" -w 2 --quiet 2>/dev/null &
done
wait
```

Each render takes ~30–60 seconds. With `-w 2` and 6 in parallel, the whole batch completes in ~2–3 minutes. Output should be ~2 MB per file (a 87 KB output means the timeline didn't seek — re-check the registration).

## Step 2 — Generate procedural music

```bash
cd <client-workspace>/marketing/videos
mkdir -p audio
cp ~/Cowork/.claude/skills/content-engine/scripts/generate-underscore.py audio/
cd audio && python3 generate-underscore.py
ffmpeg -y -i ahs-underscore.wav -c:a libmp3lame -b:a 192k underscore.mp3
```

Default track: **Cmaj7 → Am7 → Fmaj7 → G7sus4 → Cmaj7** at 90 BPM, 40s, deliberately neutral. Mood adjustments documented at the top of `generate-underscore.py`. Reuse one underscore across all 6 videos in a campaign — they should feel like a series.

## Step 3 — Mux music in

```bash
cd <client-workspace>/marketing/videos
mux() {
  v=$1; total=$2; fade_start=$((total - 2))
  ffmpeg -y -loglevel error -i "$v/$v.mp4" -i audio/underscore.mp3 \
    -filter_complex "[1:a]volume=0.4,afade=t=in:st=0:d=2,afade=t=out:st=${fade_start}:d=2[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "$v/$v-music.mp4"
}
mux V1-... 32 &
mux V2-... 32 &
mux V3-... 32 &
mux V4-... 32 &
mux V5-... 32 &
mux V6-... 32 &
wait

# Promote: keep silent versions as backup, music versions become the primary file
for v in V1-* V2-* V3-* V4-* V5-* V6-*; do
  mv "$v/${v##*/}.mp4" "$v/${v##*/}-silent.mp4"
  mv "$v/${v##*/}-music.mp4" "$v/${v##*/}.mp4"
done
```

Music sits at -8dB (`volume=0.4`), 2-second fade in/out. Pass each video's exact `data-duration` as the second arg.

## Step 4 — Multi-format cuts

```bash
cd <client-workspace>/marketing/videos
mkdir -p youtube stories

for v in V1-* V2-* V3-* V4-* V5-* V6-*; do
  # YouTube 16:9 — vertical centered on a blurred-fill 1920×1080 canvas
  ffmpeg -y -loglevel error -i "$v/$v.mp4" -filter_complex "
    [0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=25:5,setsar=1[bg];
    [0:v]scale=-2:1080[fg];
    [bg][fg]overlay=(W-w)/2:0,format=yuv420p[v]
  " -map "[v]" -map 0:a -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k "youtube/$v-youtube-16x9.mp4" &

  # Stories 15s — first 15s with audio + video fade-out at the end
  ffmpeg -y -loglevel error -i "$v/$v.mp4" -t 15 \
    -vf "fade=t=out:st=14:d=1" \
    -af "afade=t=out:st=14:d=1" \
    -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k "stories/$v-stories-15s.mp4" &
done
wait
```

Output: `V*/V*.mp4` (vertical full), `youtube/V*-youtube-16x9.mp4`, `stories/V*-stories-15s.mp4`. Three formats per slot, 18 files total for a 6-video campaign.

## Step 5 — Upload EVERYTHING to Firebase Storage

This is non-negotiable. The platform is the source of truth — local mp4s are working files, not deliverables. Every render variant goes through `POST /api/v1/social/media/upload`.

```bash
upload() {
  local file="$1" alt="$2"
  curl -s -X POST "$BASE/social/media/upload" \
    -H "Authorization: Bearer $AI_API_KEY" \
    -H "X-Org-Id: $ORG_ID" \
    -F "file=@${file};type=video/mp4" \
    -F "altText=${alt}"
}

for slug in V1-... V2-... V3-... V4-... V5-... V6-...; do
  rv=$(upload "$slug/$slug.mp4" "$slug — vertical")
  ry=$(upload "youtube/$slug-youtube-16x9.mp4" "$slug — youtube")
  rs=$(upload "stories/$slug-stories-15s.mp4" "$slug — stories")
  url_v=$(echo "$rv" | jq -r .data.url)
  url_y=$(echo "$ry" | jq -r .data.url)
  url_s=$(echo "$rs" | jq -r .data.url)
  echo "$slug v=$url_v y=$url_y s=$url_s"
done
```

Capture all 18 URLs in a manifest before moving on.

## Step 6 — Register one multi-format `social_post` per slot

ONE post per video, even though it has 3 format URLs. The campaign-preview UI splits it across the Reels / YouTube / Stories tabs based on which media-format URL is present.

```bash
POST $BASE/social/posts
{
  "platforms": ["instagram"],
  "platform": "instagram",
  "content": "<caption text>",
  "campaignId": "<campaignId>",
  "format": "feed",
  "media": [{
    "type": "video",
    "url": "<vertical 1080×1920 url>",
    "thumbnailUrl": "<vertical url>",
    "urlYoutube": "<16:9 url>",
    "urlStories": "<15s vertical url>",
    "durationSec": 32,
    "altText": "<alt>",
    "order": 0,
    "width": 1080,
    "height": 1920
  }],
  "status": "pending_approval",
  "requiresApproval": true
}

Headers:
  Idempotency-Key: pib-engine-{campaignId}-{slug}-instagram-multiformat
```

`media[0].type === 'video'` is what the platform's `buildCampaignAssets` uses to split a post into the videos array (vs. the social array). `urlYoutube` + `urlStories` make the same post appear under the YouTube + Stories tabs in the admin org-themed drill-in (`/admin/org/[slug]/social/[campaignId]`).

If you're updating an EXISTING post (e.g. re-rendering after a comment-driven revision), use `PUT /api/v1/social/posts/{id}` with just `{ "media": [...] }`. The PATCH-with-anchor flow is for comments; updating media is a PUT.

## Format → distribution-channel mapping

| Format | File | Use for |
|---|---|---|
| Vertical full | `V*/V*.mp4` (1080×1920, 30–35s) | Reels, TikTok, Facebook Reels, YouTube Shorts |
| Horizontal | `youtube/V*-youtube-16x9.mp4` (1920×1080, full length) | YouTube main feed, LinkedIn feed, website embed |
| Stories | `stories/V*-stories-15s.mp4` (1080×1920, 15s) | Instagram Stories, Facebook Stories, WhatsApp Status |

Same clip, three formats — every distribution channel covered without re-laying out the composition.

## Common HyperFrames gotchas (from real production)

| Symptom | Cause | Fix |
|---|---|---|
| Render produces black frames | Custom inline sequencer hiding scenes via `display: none` while RAF doesn't fire under virtual time | Strip the inline sequencer entirely. Let HyperFrames drive clip visibility. |
| Render produces tiny ~80 KB mp4 | No timeline registered on `window.__timelines[<comp-id>]`, so seek is a no-op and `from()` start states stay frozen | Add the registration. One master timeline. |
| Lint error: `root_missing_dimensions` | Root composition missing `data-width` / `data-height` | Add `data-width="1080" data-height="1920"` on the root `<div>` |
| Lint error: `missing_timeline_registry` | Timeline never assigned to `window.__timelines` | Add `window.__timelines["<comp-id>"] = tl;` after the timeline is built |
| Render fails / black screen partway | Tween position exceeds composition `data-duration` | Verify the last GSAP position is < the root `data-duration` |
| Doctor warns "memory low" | Mac with 8 GB RAM | Render with `-w 2` instead of `-w auto` (caps Chrome workers) |
| Same payload retried twice = duplicate post | Missing idempotency | Always set `Idempotency-Key: pib-engine-{campaignId}-{slug}-{format}` on writes |

## Time budget

Phase 5 should take **30–45 minutes** end to end:
- Generate / fix compositions: 5 min (template + sed-replace)
- Lint: 1 min
- Render: ~3 min wall-clock (parallel)
- Music gen: 1 min
- Music mux: 5 min wall-clock (parallel)
- Multi-format cuts: 10 min wall-clock (parallel)
- Upload + register posts: 5 min

If a render is taking dramatically longer or producing tiny files, stop and re-check the lint output — it's almost certainly a registration / `paused: true` issue, not a render-engine issue.

## Reference examples

- **Working canonical**: `/Users/peetstander/Cowork/partners/AHS Law/marketing/videos/V1-landlord-cant-do/index.html` — the original working pattern this template was extracted from.
- **Template**: `assets/composition-template.html` (this skill) — brand-agnostic, parameterised version of the above.
- **PiB worked example**: `/Users/peetstander/Cowork/Partners in Biz — Client Growth/marketing/videos/V1-website-vs-app/index.html` — same template, PiB content + brand. Confirms the template produces a working render for a different client.
