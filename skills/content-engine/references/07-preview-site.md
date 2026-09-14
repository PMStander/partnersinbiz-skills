# Phase 7 — Preview Site

The preview site is the single deliverable the client actually sees. It's a passcode-protected static HTML page that mocks every platform (Instagram feed, Reels, Stories, Facebook, LinkedIn, YouTube, blog) so the client knows exactly how each piece of content will look in the wild — and approves or requests changes per asset.

## Quick start

```bash
# Copy and configure builder
mkdir -p <workspace>/marketing/preview
cp ~/.claude/skills/client-content-engine/scripts/build-preview.py <workspace>/marketing/preview/build.py
cp ~/.claude/skills/client-content-engine/assets/vercel.json <workspace>/marketing/preview/vercel.json

# Fill in CLIENT, VIDEOS, RESEARCH, BLOG_IMAGE_MAP in build.py (see below)
# Then run the build — it will auto-mirror images and videos into preview/assets/
cd <workspace>/marketing/preview
python3 build.py
```

`build.py` runs `sync_assets()` on every build:

- **Images** — anything under `marketing/images/**` (recursive: flat, `blog/`, `social/`, or any other subfolder) is flattened into `preview/assets/images/<filename>`. The HTML expects flat paths like `assets/images/B1-...png`, so this layer makes the build robust regardless of how the agent organised the images upstream.
- **Videos** — for each `marketing/videos/V*-*/` directory, the primary MP4 (and any `youtube/V*-youtube-16x9.mp4` / `stories/V*-stories-15s.mp4` siblings) are copied into `preview/assets/videos/<id>/`. `*-silent.mp4` backups are skipped — only the music-muxed primary ships.
- **Idempotent** — only copies new or modified files (compares mtimes), so reruns are fast.

If for some reason a video has not been rendered to MP4 yet (very early preview, before Phase 5 finishes), copy the HyperFrames `index.html` into `preview/assets/videos/<id>/` manually and apply the auto-play patch:

```python
# Patch standalone HF iframe to auto-play on load (the host runtime isn't there)
p = "preview/assets/videos/V1-foo/index.html"
src = open(p).read()
src = src.replace("gsap.timeline({ paused: true })",
                  "gsap.timeline({ paused: false, repeat: -1, repeatDelay: 1.2 })")
src = src.replace("gsap.timeline({paused: true})",
                  "gsap.timeline({paused: false, repeat: -1, repeatDelay: 1.2})")
open(p, "w").write(src)
```

But this is rare — the normal flow has all 6 MP4s rendered before Phase 7 starts.

The builder reads `../blog-posts/B*.md` and `../social-media/W*.md`, embeds the captions and metadata, and emits `index.html` (~170–200 KB) that's fully self-contained.

## Videos: native <video controls> preferred over iframes

The preview build script auto-detects whether a rendered MP4 exists for each video at `preview/assets/videos/<id>/<id>.mp4`:

- **MP4 present** → renders `<video controls preload="metadata" playsinline>` — clean play button, no auto-play, no scene overlap. This is the canonical path post-render and is what every client sees.
- **MP4 missing** → falls back to `<iframe src="assets/videos/<id>/">`. Only used during early design preview, before MP4s render. Standalone HF iframes need the auto-play patch above (`paused: false, repeat: -1`) because the runtime that normally drives playback isn't loaded.

The pick happens at build time — the Python script tags each video with `src_kind: "mp4"` or `"html"` in the embedded JSON. The JS `videoMarkup(v)` helper emits the right element from there.

Why not just use HF iframes for everything: HyperFrames compositions ship with `gsap.timeline({ paused: true })` because the renderer drives `.play()` at MP4-render time. In a standalone iframe with no HF runtime, scenes don't get clipped — all 6 scenes render simultaneously and the GSAP fades collide. The patch in the bash above is a partial workaround (forces auto-play and loop) but doesn't fix scene-clipping; only MP4 truly works.

Phone-frame CSS (already in the script):
```css
.phone-frame video { width: 100%; height: 100%; object-fit: cover; }
.phone-frame iframe { width: 1080px; height: 1920px; transform: scale(0.3333); transform-origin: top left; pointer-events: none; }
.yt-video video { width: 100%; height: 100%; object-fit: contain; background: #000; }
```

## Customising for a new client — fill in the CLIENT block

The script has 4 blocks at the top to fill in. Everything else is generic HTML and should not be changed.

### BLOCK 1 — CLIENT config

```python
CLIENT = {
    "name": "Partners in Biz",          # display name everywhere
    "slug": "pib",                       # lowercase, no spaces — used in localStorage key
    "period": "May 2026",                # campaign period label
    "email": "peet@partnersinbiz.online",
    "avatar": "P",                       # single letter for avatar circles
    "passcode": "5566",                  # 4-digit string
    "accent": "#F5A623",                 # primary accent color
    "accent_light": "#FFB840",           # slightly lighter accent
    "bg": "#0A0A0B",
    "bg2": "#141416",
    "bg3": "#050506",
    "font": "Instrument Serif",          # Google Fonts family name
    "li_headline": "Web Development & AI Integration · Cape Town, SA",
    "ig_username": "partnersinbiz",
    "hero_sub": "8 long-form blog posts, 6 short-form videos...",
    "research_sub": "Every piece of marketing is grounded in...",
    "blog_sub": "Long-form articles for the website...",
    "ig_sub": "Square posts for the Instagram grid...",
    "li_sub": "Professional, longer-form captions...",
    "fb_sub": "Conversational, community-tone captions...",
}
```

### BLOCK 2 — VIDEOS (6 entries)

```python
VIDEOS = [
    {"id": "V1-website-vs-app", "title": "Website or App?", "pillar": "Web Presence", "duration": 28, "linked_social": "W02"},
    # ... 5 more
]
```

`id` must exactly match the folder name under `marketing/videos/` (and `preview/assets/videos/`).

### BLOCK 3 — RESEARCH

Fill in `stats`, `categories`, `changes_2026`, `myths`, `sources` from the research brief.

### BLOCK 4 — BLOG_IMAGE_MAP

```python
BLOG_IMAGE_MAP = {
    "W01": "B1-website-minimum-price.png",
    "W02": "B2-website-vs-app.png",
    # ...
}
```

Maps each W-week (by prefix) to a blog hero filename. Falls back to `"quote-card-bg.png"` if not found.

## What the preview includes

| Section | What it shows |
|---|---|
| **Research** (first tab) | Stats, "what people are searching for", 2026 timeline, myths, sources |
| **Blog Posts** | 8 magazine cards with hero images. Click any → modal opens the FULL article body with Approve / Request Changes buttons |
| **Instagram** | 12 native feed mockups with avatar, like UI, full caption preview |
| **Reels & TikTok** | 6 phone-frame mockups with live HyperFrames compositions |
| **Stories** | 6 phone-frames with live HyperFrames + Stories progress bar overlay |
| **Facebook** | 12 dark-mode feed mockups. Click any → full caption + sign-off |
| **LinkedIn** | 12 LinkedIn dark-mode mockups. Click any → full caption + sign-off |
| **YouTube** | 6 watch-page mockups with live HyperFrames compositions |

## Image fallbacks (built in)

Images use a gradient fallback — no blank space if the file is missing:

```css
.blog-hero-wrap {
  background: linear-gradient(135deg, #141416 0%, #1C1C20 60%, #0A0A0B 100%);
}
```

And `onerror="this.style.opacity='0'"` on all hero `<img>` tags hides the broken image icon while the gradient shows through.

## After build, verify locally

```bash
cd <workspace>/marketing/preview
python3 -m http.server 8765
open http://localhost:8765
```

Enter the passcode. Click through each tab. Test that:
- Blog cards open modals with full text
- Social posts open caption modals
- Approve / Request Changes buttons toggle the badge state
- Videos render (live HyperFrames in phone frames)
- Images load or fall back to gradient

## Known gotchas

| Issue | Fix |
|---|---|
| LinkedIn/Facebook/YouTube sections empty on page reload | Fixed in script: `render()` runs in BOTH `tryUnlock()` AND a final boot block at the very END of the script (after every `const` helper). NEVER call `render()` at top level before the helpers — that triggers a TDZ `ReferenceError: Cannot access 'escapeHtml' before initialization`. |
| Social sections empty on first load | The `section()` helper now accepts both `## LinkedIn Caption` and `## LinkedIn` (case-insensitive). If still empty, check the H2 spelling. |
| Reels/Stories/YouTube videos don't play in iframes | HyperFrames compositions default to `gsap.timeline({ paused: true })` — the player calls `.play()` at MP4-render time. For preview iframes, post-process each `preview/assets/videos/V*/index.html` to swap `paused: true` → `paused: false, repeat: -1, repeatDelay: 1.2` so the animation auto-plays and loops on view. |
| Iframe video not showing | Check that `preview/assets/videos/V1-xxx/index.html` exists |
| Brand name bleeding from previous client | Use `CLIENT["name"]` — no hardcoded strings in HTML template |

## Sign-off mechanics

`localStorage` key is `<slug>_signoff_v1`. Stores `{ "blog:B1-…": "approve", "cap:W01-…:linkedin": "changes", … }`. Per-browser. To share review across stakeholders, give each the URL + passcode separately.

## When to regenerate

Any time blog or social .md files are edited:
```bash
cd <workspace>/marketing/preview
python3 build.py    # rebuild index.html
vercel --prod --yes --scope <team-scope>
```

Rebuild + redeploy cycle is < 90 seconds.

## Time budget

Phase 7 should take **15–25 minutes**:
- Fill in CLIENT, VIDEOS, RESEARCH, BLOG_IMAGE_MAP blocks: 10–15 min
- Build (asset sync runs automatically): < 1 min
- Spin up `python3 -m http.server` and walk through every tab to spot bugs: 5 min
