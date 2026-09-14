#!/usr/bin/env python3
"""
DEPRECATED (2026-05-09) — Legacy throwaway-Vercel-preview-site builder.

The content-engine skill no longer deploys a separate preview site. New runs
write all assets into the PiB platform as a `campaign` and the preview lives
at https://partnersinbiz.online/c/{shareToken}.

Kept here ONLY for the AHS Law / scrolledbrain backfill flow — i.e. importing
historical local-file content into a real campaign. Do not use for new runs.

----- original docstring -----

Build the client preview site. Copy this file to marketing/preview/build.py,
fill in the CLIENT, VIDEOS, RESEARCH, and BLOG_IMAGE_MAP blocks below,
then run:  python3 build.py

AGENT INSTRUCTIONS — fill in these four blocks before running:
  1. CLIENT   — brand tokens + static strings (required)
  2. VIDEOS   — 6 video metadata dicts (required)
  3. RESEARCH — stats, categories, myths, changes, sources (required)
  4. BLOG_IMAGE_MAP — W01→B*.png mapping (required, generated from blog filenames)
Everything else is generic and should not need to change.
"""
import os, re, json, shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT.parent
BLOG_DIR = SRC / "blog-posts"
SOCIAL_DIR = SRC / "social-media"
IMAGE_SRC = SRC / "images"
VIDEO_SRC = SRC / "videos"
ASSETS_DIR = ROOT / "assets"

# ===========================================================================
# BLOCK 1 — CLIENT CONFIG (fill in per client)
# ===========================================================================
CLIENT = {
    # Display name — used everywhere: gate, header, LinkedIn, Facebook, YouTube
    "name": "FILL IN CLIENT NAME",
    # Short slug — used as localStorage / sessionStorage key (lowercase, no spaces)
    "slug": "client",
    # Campaign period label shown in header and footer
    "period": "May 2026",
    # Contact email for sign-off instructions in footer
    "email": "your@email.com",
    # Single capital letter for avatar circles (first letter of brand)
    "avatar": "C",
    # Passcode (4-digit string)
    "passcode": "5566",
    # Brand colors
    "accent": "#F5A623",       # primary accent (gold / amber etc.)
    "accent_light": "#FFB840", # slightly lighter version of accent
    "bg": "#0A0A0B",           # page background
    "bg2": "#141416",          # card background
    "bg3": "#050506",          # deep background (media placeholders)
    # Heading font name — must be a Google Fonts family
    "font": "Instrument Serif",
    # LinkedIn profile headline (shown under name in LinkedIn mockup)
    "li_headline": "Fill in LinkedIn headline · City, Country",
    # Instagram username (without @)
    "ig_username": "yourbrand",
    # Hero subtitle paragraph (shown on the overview page)
    "hero_sub": (
        "8 long-form blog posts, 6 short-form videos in 3 formats each, "
        "12 weeks of social posts across LinkedIn, Instagram, and Facebook — "
        "all built around the questions your audience is actually asking. "
        "This page shows you exactly how each piece will appear in the wild."
    ),
    # Research section — what geographic/industry context to mention
    "research_sub": (
        "Every piece of marketing on this page is grounded in 30 days of "
        "public-search analysis. Here's what we found."
    ),
    # Blog section description
    "blog_sub": (
        "Long-form articles for the website. Each runs 1,200–1,800 words with "
        "embedded references to trusted sources. Click-through CTA at the end "
        "of each article links back to the contact form."
    ),
    # Instagram section description
    "ig_sub": (
        "Square posts for the Instagram grid. The image carries the headline, "
        "the caption tells the story. These mockups show how each post will "
        "appear in a follower's feed."
    ),
    # LinkedIn section description
    "li_sub": (
        "Professional, longer-form captions with sources cited. "
        "Designed for B2B reach and professional audiences."
    ),
    # Facebook section description
    "fb_sub": (
        "Conversational, community-tone captions for the Facebook page. "
        "Mockups show how the post will look in Facebook's dark-mode feed."
    ),
}

# ===========================================================================
# BLOCK 2 — VIDEO METADATA (fill in per client)
# ===========================================================================
# id must match the folder name under marketing/videos/ (e.g. V1-your-title)
# linked_social is the W## week this video is paired with
VIDEOS = [
    {"id": "V1-fill-in", "title": "Video 1 Title", "pillar": "Pillar Name", "duration": 30, "linked_social": "W01"},
    {"id": "V2-fill-in", "title": "Video 2 Title", "pillar": "Pillar Name", "duration": 30, "linked_social": "W02"},
    {"id": "V3-fill-in", "title": "Video 3 Title", "pillar": "Pillar Name", "duration": 30, "linked_social": "W03"},
    {"id": "V4-fill-in", "title": "Video 4 Title", "pillar": "Pillar Name", "duration": 30, "linked_social": "W04"},
    {"id": "V5-fill-in", "title": "Video 5 Title", "pillar": "Pillar Name", "duration": 30, "linked_social": "W05"},
    {"id": "V6-fill-in", "title": "Video 6 Title", "pillar": "Pillar Name", "duration": 30, "linked_social": "W06"},
]

# ===========================================================================
# BLOCK 3 — RESEARCH DATA (fill in per client)
# ===========================================================================
RESEARCH = {
    "stats": [
        {"num": "7",  "label": "Content Pillars Analysed"},
        {"num": "30", "label": "Days of Search Data"},
        {"num": "8",  "label": "Sources Reviewed"},
        {"num": "12", "label": "Weeks of Content"},
    ],
    # One dict per content pillar
    "categories": [
        {
            "icon": "🌐",
            "title": "Pillar 1 — Fill In",
            "rank": "Most-searched topic",
            "questions": [
                "Question 1?",
                "Question 2?",
                "Question 3?",
                "Question 4?",
                "Question 5?",
                "Question 6?",
            ],
        },
        # Repeat for each pillar (ideally 5–7 total)
    ],
    # Major industry changes in the campaign year
    "changes_2026": [
        {
            "month": "JAN 2026",
            "title": "Change 1 — fill in",
            "detail": "Detail sentence.",
            "impact": "high",   # high / medium / low
        },
    ],
    # Most-believed myths in this industry (high shareability)
    "myths": [
        {
            "myth": "Fill in myth 1",
            "fact": "Fill in the truth.",
        },
    ],
    # Source names only (chips display in footer of research section)
    "sources": [
        "Source 1",
        "Source 2",
    ],
}

# ===========================================================================
# BLOCK 4 — SOCIAL IMAGE MAP (fill in per client)
# ===========================================================================
# Maps W-week ID prefix ("W01") → blog hero filename (e.g. "B1-your-slug.png")
# W-posts without a matching blog image fall back to a card background image
BLOG_IMAGE_MAP = {
    "W01": "B1-fill-in.png",
    "W02": "B2-fill-in.png",
    "W03": "B3-fill-in.png",
    "W04": "B4-fill-in.png",
    "W05": "B5-fill-in.png",
    "W06": "B6-fill-in.png",
    "W07": "B7-fill-in.png",
    "W08": "B8-fill-in.png",
    "W09": "B3-fill-in.png",  # reuse a hero for W09+
    "W10": "B6-fill-in.png",
    "W11": "B7-fill-in.png",
    "W12": "stat-card-bg.png",
}

# ===========================================================================
# HELPERS — do not edit below this line
# ===========================================================================

def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip()
    body = text[end + 4:].strip()
    fm = {}
    cur_key = None
    mode = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if mode == "list" and line.startswith("  -"):
            fm[cur_key].append(line.split("-", 1)[1].strip().strip('"').strip("'"))
            continue
        if mode == "scalar" and line.startswith("  "):
            existing = fm.get(cur_key, "")
            fm[cur_key] = (existing + "\n" + line[2:]).strip() if existing else line[2:]
            continue
        m = re.match(r"^([\w\-]+):\s*(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip()
            cur_key = k
            if v in ("|", ">"):
                fm[k] = ""
                mode = "scalar"
            elif v == "":
                fm[k] = []
                mode = "list"
            else:
                fm[k] = v.strip('"').strip("'")
                mode = None
    return fm, body


def section(body, name):
    """Pull a markdown section by H2 header name. Accepts either the literal
    name or the same name with " Caption" / " caption" suffix dropped — so a
    file using `## LinkedIn` matches a lookup for `LinkedIn Caption` and
    vice-versa.
    """
    candidates = [name]
    if name.lower().endswith(" caption"):
        candidates.append(name[: -len(" caption")])
    else:
        candidates.append(f"{name} Caption")
    for n in candidates:
        pattern = re.compile(rf"^##\s+{re.escape(n)}\s*$", re.M | re.I)
        m = pattern.search(body)
        if m:
            start = m.end()
            nxt = re.search(r"^##\s+", body[start:], re.M)
            chunk = body[start: start + nxt.start()] if nxt else body[start:]
            return chunk.strip().rstrip("-").strip()
    return ""


def first_words(text, n=60):
    words = re.sub(r"<[^>]+>", "", text).split()
    return " ".join(words[:n]) + ("…" if len(words) > n else "")


def sync_assets():
    """Mirror marketing/images/** and marketing/videos/V*/V*.mp4 into preview/assets/.

    Images are flattened: anything found under images/ (whether at the root,
    under blog/, social/, or any other subfolder) lands in assets/images/<name>.
    The HTML references images flat (assets/images/B1-...png), so this keeps
    the render robust whether the agent organised images in subfolders or not.
    Caught on the Deidre Ras run, May 2026 — images were silently 404ing
    because they'd been put in assets/images/blog/ instead of flat.

    Videos are mirrored into assets/videos/<id>/ preserving the per-video
    directory layout (vertical mp4 + youtube-16x9 + stories-15s siblings).
    """
    if IMAGE_SRC.exists():
        (ASSETS_DIR / "images").mkdir(parents=True, exist_ok=True)
        copied = 0
        for p in IMAGE_SRC.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
                dest = ASSETS_DIR / "images" / p.name
                if not dest.exists() or dest.stat().st_mtime < p.stat().st_mtime:
                    shutil.copy2(p, dest)
                    copied += 1
        if copied:
            print(f"   synced {copied} image(s) → assets/images/")

    if VIDEO_SRC.exists():
        (ASSETS_DIR / "videos").mkdir(parents=True, exist_ok=True)
        copied = 0
        for vid_dir in sorted(VIDEO_SRC.glob("V*-*")):
            if not vid_dir.is_dir():
                continue
            dest_dir = ASSETS_DIR / "videos" / vid_dir.name
            dest_dir.mkdir(exist_ok=True)
            for p in vid_dir.glob("*.mp4"):
                # Skip silent backups — only ship the music-muxed primary + cuts
                if "-silent" in p.name:
                    continue
                dest = dest_dir / p.name
                if not dest.exists() or dest.stat().st_mtime < p.stat().st_mtime:
                    shutil.copy2(p, dest)
                    copied += 1
            # Also pull horizontal/stories cuts that ffmpeg may have written to
            # marketing/videos/youtube/ and marketing/videos/stories/
            for sib_dir, suffix in [("youtube", "youtube-16x9"), ("stories", "stories-15s")]:
                cut = VIDEO_SRC / sib_dir / f"{vid_dir.name}-{suffix}.mp4"
                if cut.exists():
                    dest = dest_dir / cut.name
                    if not dest.exists() or dest.stat().st_mtime < cut.stat().st_mtime:
                        shutil.copy2(cut, dest)
                        copied += 1
        if copied:
            print(f"   synced {copied} video file(s) → assets/videos/")


# ---------- collect blog posts ----------
blogs = []
for p in sorted(BLOG_DIR.glob("B*.md")):
    text = p.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    title = fm.get("title", p.stem).strip("'\"")
    hero = fm.get("hero_image", "").replace("../images/blog/", "assets/images/")
    slug = fm.get("slug", p.stem)
    pillar = fm.get("pillar", "")
    word_count = fm.get("word_count", "")
    excerpt = first_words(body, 50)
    blogs.append({
        "id": p.stem,
        "title": title,
        "slug": slug,
        "pillar": pillar,
        "hero": hero,
        "excerpt": excerpt,
        "word_count": word_count,
        "body": body,
    })

# ---------- collect social posts ----------
socials = []
for p in sorted(SOCIAL_DIR.glob("W*.md")):
    text = p.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    week = fm.get("week", "")
    fmt = fm.get("format", "")
    pillar = fm.get("pillar", "")
    on_image = fm.get("on_image_text", "") or section(body, "On-Image Text")
    li = section(body, "LinkedIn Caption")
    ig = section(body, "Instagram Caption")
    fb = section(body, "Facebook Caption")
    hashtags = fm.get("hashtags", []) or []
    if isinstance(hashtags, str):
        hashtags = [h.strip() for h in hashtags.split(",") if h.strip()]
    socials.append({
        "id": p.stem,
        "week": week,
        "format": fmt,
        "pillar": pillar,
        "on_image": on_image,
        "linkedin": li,
        "instagram": ig,
        "facebook": fb,
        "hashtags": hashtags,
    })

# ---------- detect rendered MP4s per video ----------
# When an MP4 exists at assets/videos/<id>/<id>.mp4 it will be served via a
# native <video controls> element (play button, no auto-play, no scene
# overlap). Otherwise we fall back to embedding the HyperFrames HTML in an
# iframe — which only displays cleanly while a HyperFrames runtime is
# present, so the iframe path is best-effort for design preview only.
ASSETS_VIDEOS = ROOT / "assets" / "videos"
videos_with_mp4 = []
for v in VIDEOS:
    vid = v.copy()
    mp4_path = ASSETS_VIDEOS / vid["id"] / f"{vid['id']}.mp4"
    if mp4_path.exists():
        vid["src_kind"] = "mp4"
        vid["src_path"] = f"assets/videos/{vid['id']}/{vid['id']}.mp4"
    else:
        vid["src_kind"] = "html"
        vid["src_path"] = f"assets/videos/{vid['id']}/"
    videos_with_mp4.append(vid)

# ---------- assemble page data ----------
data = {"blogs": blogs, "socials": socials, "videos": videos_with_mp4, "research": RESEARCH}
data_json = json.dumps(data, ensure_ascii=False, indent=2)

# ---------- HTML template ----------
# Tokens: __DATA_JSON__ __CLIENT_NAME__ __CLIENT_SLUG__ __CLIENT_PERIOD__
#         __CLIENT_EMAIL__ __CLIENT_AVATAR__ __CLIENT_PASSCODE__
#         __CLIENT_ACCENT__ __CLIENT_ACCENT_LIGHT__ __CLIENT_BG__ __CLIENT_BG2__ __CLIENT_BG3__
#         __CLIENT_FONT__ __CLIENT_LI_HEADLINE__ __CLIENT_IG_USERNAME__
#         __CLIENT_HERO_SUB__ __CLIENT_RESEARCH_SUB__ __CLIENT_BLOG_SUB__
#         __CLIENT_IG_SUB__ __CLIENT_LI_SUB__ __CLIENT_FB_SUB__
#         __BLOG_IMAGE_MAP_JSON__
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex, nofollow" />
<title>__CLIENT_NAME__ — Marketing Preview · __CLIENT_PERIOD__</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=__CLIENT_FONT_URL__:ital@0;1&display=swap');
:root {
  --bg: __CLIENT_BG__;
  --bg-2: __CLIENT_BG2__;
  --bg-3: __CLIENT_BG3__;
  --gold: __CLIENT_ACCENT__;
  --gold-light: __CLIENT_ACCENT_LIGHT__;
  --alert: #ff6b6b;
  --text: #EDEDED;
  --text-muted: #8B8B92;
  --border: rgba(255,255,255,0.08);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: var(--bg); color: var(--text); font-family: 'Geist', -apple-system, sans-serif; -webkit-font-smoothing: antialiased; }
body { min-height: 100vh; }

/* === PASSCODE GATE === */
.gate { position: fixed; inset: 0; background: var(--bg); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.gate.hide { display: none; }
.gate-inner { text-align: center; max-width: 420px; width: 100%; }
.gate-mark { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 400; font-size: 36px; letter-spacing: -0.01em; margin-bottom: 8px; }
.gate-tag { color: var(--text-muted); font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 48px; }
.gate-title { font-family: '__CLIENT_FONT__', serif; font-weight: 400; font-size: 28px; margin-bottom: 12px; }
.gate-sub { color: var(--text-muted); font-size: 15px; line-height: 1.5; margin-bottom: 32px; }
.gate-input { width: 100%; background: var(--bg-2); border: 1px solid var(--border); color: var(--text); padding: 16px 20px; font-size: 18px; letter-spacing: 0.4em; text-align: center; font-family: '__CLIENT_FONT__', serif; font-weight: 600; border-radius: 4px; }
.gate-input:focus { outline: none; border-color: var(--gold); }
.gate-btn { margin-top: 16px; width: 100%; background: var(--gold); color: var(--bg); border: none; padding: 16px; font-family: '__CLIENT_FONT__', serif; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; font-size: 14px; cursor: pointer; border-radius: 4px; transition: background 0.2s; }
.gate-btn:hover { background: var(--gold-light); }
.gate-error { color: var(--alert); font-size: 13px; margin-top: 12px; min-height: 20px; }

/* === HEADER === */
.site-header { position: sticky; top: 0; z-index: 50; background: rgba(10,10,10,0.95); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); }
.header-inner { max-width: 1400px; margin: 0 auto; padding: 18px 32px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.brand { display: flex; align-items: center; gap: 16px; }
.brand-mark { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 800; font-size: 22px; letter-spacing: 0.15em; }
.brand-divider { width: 1px; height: 18px; background: var(--border); }
.brand-meta { color: var(--text-muted); font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; }
.header-stat { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; }

/* === HERO === */
.hero { padding: 80px 32px 60px; max-width: 1400px; margin: 0 auto; }
.hero-eyebrow { color: var(--gold); font-family: '__CLIENT_FONT__', serif; letter-spacing: 0.2em; text-transform: uppercase; font-size: 13px; margin-bottom: 20px; }
.hero-title { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: clamp(36px, 5vw, 56px); line-height: 1.1; margin-bottom: 20px; max-width: 900px; }
.hero-sub { color: var(--text-muted); font-size: 17px; line-height: 1.6; max-width: 700px; margin-bottom: 40px; }
.hero-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 24px; max-width: 800px; }
.stat-num { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 800; font-size: 40px; line-height: 1; }
.stat-label { color: var(--text-muted); font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 6px; }

/* === TABS === */
.tabs { position: sticky; top: 64px; z-index: 40; background: rgba(10,10,10,0.95); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border); overflow-x: auto; }
.tabs-inner { max-width: 1400px; margin: 0 auto; padding: 0 32px; display: flex; gap: 4px; }
.tab { padding: 16px 20px; color: var(--text-muted); font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer; border-bottom: 2px solid transparent; white-space: nowrap; transition: all 0.2s; background: none; border-left: none; border-right: none; border-top: none; }
.tab:hover { color: var(--text); }
.tab.active { color: var(--gold); border-bottom-color: var(--gold); }

/* === SECTIONS === */
.section { max-width: 1400px; margin: 0 auto; padding: 60px 32px; display: none; }
.section.active { display: block; }
.section-title { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 28px; margin-bottom: 8px; }
.section-sub { color: var(--text-muted); font-size: 15px; line-height: 1.5; margin-bottom: 40px; max-width: 700px; }

/* === GRIDS === */
.grid { display: grid; gap: 24px; }
.grid-blog { grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); }
.grid-feed { grid-template-columns: repeat(auto-fill, minmax(560px, 1fr)); }
.grid-mobile { grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); }

/* === BLOG CARD === */
.blog-card { background: var(--bg-2); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, border-color 0.2s; cursor: pointer; }
.blog-card:hover { border-color: var(--gold); transform: translateY(-2px); }
.blog-hero { width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #141416 0%, #1C1C20 60%, #0A0A0B 100%); object-fit: cover; display: block; }
.blog-hero-wrap { width: 100%; aspect-ratio: 16/9; background: linear-gradient(135deg, #141416 0%, #1C1C20 60%, #0A0A0B 100%); position: relative; overflow: hidden; }
.blog-hero-wrap img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.blog-body { padding: 28px; flex: 1; display: flex; flex-direction: column; }
.blog-pillar { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 14px; }
.blog-title { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 22px; line-height: 1.3; margin-bottom: 14px; }
.blog-excerpt { color: var(--text-muted); font-size: 14px; line-height: 1.6; flex: 1; }
.blog-foot { display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border); }
.blog-words { color: var(--text-muted); font-size: 12px; }
.blog-cta { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; }
.blog-cta:hover { color: var(--gold-light); }

/* === INSTAGRAM === */
.ig-post { background: #000; border: 1px solid #262626; border-radius: 12px; overflow: hidden; font-family: -apple-system, 'Segoe UI', sans-serif; color: #fff; max-width: 540px; margin: 0 auto; }
.ig-head { display: flex; align-items: center; padding: 12px 14px; gap: 12px; }
.ig-avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #c9a25a, #1a1a1a); display: flex; align-items: center; justify-content: center; color: #c9a25a; font-weight: 800; font-size: 12px; border: 2px solid #c9a25a; }
.ig-username { font-weight: 600; font-size: 14px; flex: 1; }
.ig-media { width: 100%; aspect-ratio: 1/1; background: var(--bg-3); object-fit: cover; display: block; }
.ig-actions { display: flex; align-items: center; padding: 10px 14px; gap: 16px; font-size: 22px; }
.ig-actions .ig-spacer { flex: 1; }
.ig-likes { padding: 0 14px 4px; font-weight: 600; font-size: 14px; }
.ig-caption { padding: 4px 14px 14px; font-size: 14px; line-height: 1.4; white-space: pre-line; }
.ig-caption .uname { font-weight: 600; margin-right: 6px; }
.ig-caption .more { color: #8e8e8e; cursor: pointer; }
.ig-time { padding: 0 14px 14px; color: #8e8e8e; font-size: 11px; text-transform: uppercase; }

/* === PHONE FRAME (Reels / Stories) === */
.phone-frame { width: 360px; height: 640px; background: #000; border-radius: 36px; overflow: hidden; position: relative; margin: 0 auto; box-shadow: 0 20px 60px rgba(0,0,0,0.6); border: 6px solid #1a1a1a; }
.phone-frame video { width: 100%; height: 100%; object-fit: cover; display: block; }
.phone-frame iframe { width: 1080px; height: 1920px; border: none; display: block; transform: scale(0.3333); transform-origin: top left; pointer-events: none; }
.phone-overlay { position: absolute; inset: 0; pointer-events: none; }
.phone-overlay.ig-reel::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 100px; background: linear-gradient(180deg, rgba(0,0,0,0.6), transparent); }
.phone-overlay.ig-reel::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 220px; background: linear-gradient(0deg, rgba(0,0,0,0.7), transparent); }
.reel-top { position: absolute; top: 12px; left: 16px; right: 16px; display: flex; justify-content: space-between; color: #fff; font-size: 13px; font-weight: 600; }
.reel-bottom-text { position: absolute; left: 16px; right: 80px; bottom: 64px; color: #fff; font-size: 13px; line-height: 1.4; }
.reel-bottom-text .uname { font-weight: 700; margin-bottom: 6px; display: block; }
.reel-side { position: absolute; right: 12px; bottom: 64px; display: flex; flex-direction: column; gap: 22px; align-items: center; color: #fff; font-size: 11px; font-weight: 600; }
.reel-side-icon { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.reel-music { position: absolute; bottom: 16px; left: 16px; right: 60px; color: #fff; font-size: 12px; display: flex; align-items: center; gap: 8px; }
.phone-overlay.story::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 60px; background: linear-gradient(180deg, rgba(0,0,0,0.5), transparent); }
.story-bar { position: absolute; top: 8px; left: 12px; right: 12px; height: 2px; background: rgba(255,255,255,0.3); border-radius: 2px; overflow: hidden; }
.story-bar::after { content: ""; display: block; width: 38%; height: 100%; background: #fff; }
.story-head { position: absolute; top: 24px; left: 16px; right: 16px; display: flex; align-items: center; gap: 10px; color: #fff; font-size: 13px; }
.story-avatar { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #c9a25a, #1a1a1a); display: flex; align-items: center; justify-content: center; color: #c9a25a; font-weight: 800; font-size: 11px; border: 2px solid #fff; }
.story-uname { font-weight: 600; }
.story-time { color: rgba(255,255,255,0.7); font-size: 11px; }

/* === FACEBOOK === */
.fb-post { background: #242526; border: 1px solid #3a3b3c; border-radius: 8px; overflow: hidden; font-family: -apple-system, 'Segoe UI', sans-serif; color: #e4e6eb; max-width: 600px; margin: 0 auto; }
.fb-head { display: flex; align-items: center; padding: 12px 16px; gap: 12px; }
.fb-avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #c9a25a, #1a1a1a); display: flex; align-items: center; justify-content: center; color: #c9a25a; font-weight: 800; font-size: 14px; }
.fb-name { font-weight: 600; font-size: 15px; }
.fb-meta { color: #b0b3b8; font-size: 12px; }
.fb-meta::after { content: " · 🌍"; }
.fb-text { padding: 0 16px 12px; font-size: 15px; line-height: 1.5; white-space: pre-line; }
.fb-media { width: 100%; max-height: 600px; background: var(--bg-3); object-fit: cover; display: block; }
.fb-stats { padding: 10px 16px; color: #b0b3b8; font-size: 13px; display: flex; justify-content: space-between; border-bottom: 1px solid #3a3b3c; }
.fb-actions { display: flex; padding: 4px 8px; }
.fb-action { flex: 1; text-align: center; padding: 8px; color: #b0b3b8; font-weight: 600; font-size: 14px; }

/* === LINKEDIN === */
.li-post { background: #1d2226; border: 1px solid #38434f; border-radius: 8px; overflow: hidden; font-family: -apple-system, 'Segoe UI', sans-serif; color: #e7e9ea; max-width: 600px; margin: 0 auto; }
.li-head { display: flex; align-items: flex-start; padding: 12px 16px; gap: 12px; }
.li-avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #c9a25a, #1a1a1a); display: flex; align-items: center; justify-content: center; color: #c9a25a; font-weight: 800; font-size: 16px; flex-shrink: 0; }
.li-name { font-weight: 600; font-size: 14px; }
.li-headline { color: #b0b3b8; font-size: 12px; line-height: 1.3; }
.li-time { color: #b0b3b8; font-size: 11px; margin-top: 2px; }
.li-text { padding: 0 16px 12px; font-size: 14px; line-height: 1.5; white-space: pre-line; }
.li-media { width: 100%; max-height: 600px; background: var(--bg-3); object-fit: cover; display: block; }
.li-stats { padding: 10px 16px; color: #b0b3b8; font-size: 12px; border-top: 1px solid #38434f; }
.li-actions { display: flex; padding: 4px 8px; border-top: 1px solid #38434f; }
.li-action { flex: 1; text-align: center; padding: 8px; color: #b0b3b8; font-weight: 600; font-size: 13px; }

/* === YOUTUBE === */
.yt-card { background: #0f0f0f; border-radius: 12px; overflow: hidden; max-width: 720px; margin: 0 auto; font-family: -apple-system, 'Roboto', sans-serif; color: #fff; }
.yt-video { width: 100%; aspect-ratio: 16/9; background: #000; position: relative; overflow: hidden; display: block; }
.yt-video video { width: 100%; height: 100%; object-fit: contain; background: #000; display: block; }
.yt-meta { padding: 14px 4px; }
.yt-title { font-size: 18px; font-weight: 600; line-height: 1.3; margin-bottom: 8px; }
.yt-channel { color: #aaa; font-size: 14px; }
.yt-stats { color: #aaa; font-size: 13px; margin-top: 4px; }

/* === RESEARCH === */
.research-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 20px; margin-bottom: 60px; }
.research-stat { background: var(--bg-2); border: 1px solid var(--border); border-radius: 8px; padding: 24px; text-align: center; }
.research-stat-num { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 800; font-size: 36px; line-height: 1; }
.research-stat-label { color: var(--text-muted); font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 8px; line-height: 1.3; }
.research-h3 { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 22px; margin-top: 60px; margin-bottom: 8px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }
.research-sub { color: var(--text-muted); font-size: 14px; line-height: 1.6; margin-bottom: 28px; max-width: 720px; }
.research-categories { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 24px; }
.research-cat { background: var(--bg-2); border: 1px solid var(--border); border-radius: 8px; padding: 28px; }
.research-cat-head { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.research-cat-icon { font-size: 22px; }
.research-cat-title { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 17px; flex: 1; }
.research-cat-rank { color: var(--gold); font-size: 12px; letter-spacing: 0.05em; margin-bottom: 18px; font-style: italic; }
.research-cat ul { list-style: none; padding: 0; margin: 0; }
.research-cat li { color: var(--text); font-size: 14px; line-height: 1.55; padding: 8px 0 8px 22px; position: relative; border-top: 1px solid var(--border); }
.research-cat li:first-child { border-top: 0; }
.research-cat li::before { content: "?"; position: absolute; left: 0; top: 8px; color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 800; }
.research-timeline { position: relative; padding-left: 32px; }
.research-timeline::before { content: ""; position: absolute; left: 8px; top: 12px; bottom: 12px; width: 2px; background: var(--border); }
.timeline-item { position: relative; margin-bottom: 28px; padding: 0 0 0 8px; }
.timeline-item::before { content: ""; position: absolute; left: -29px; top: 8px; width: 12px; height: 12px; border-radius: 50%; background: var(--gold); border: 3px solid var(--bg); }
.timeline-item.high::before { background: var(--gold); box-shadow: 0 0 0 4px rgba(201,162,90,0.2); }
.timeline-item.medium::before { background: var(--gold-light); }
.timeline-item.low::before { background: var(--text-muted); }
.timeline-month { display: inline-block; color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 800; font-size: 11px; letter-spacing: 0.15em; margin-bottom: 6px; }
.timeline-title { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 16px; margin-bottom: 4px; }
.timeline-detail { color: var(--text-muted); font-size: 14px; line-height: 1.55; }
.research-myths { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 20px; }
.myth-card { background: var(--bg-2); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.myth-row { padding: 20px 24px; }
.myth-row.myth { background: rgba(224,112,112,0.08); border-bottom: 1px solid rgba(224,112,112,0.2); }
.myth-row.fact { background: rgba(201,162,90,0.05); }
.myth-label { font-family: '__CLIENT_FONT__', serif; font-weight: 700; font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 6px; }
.myth-row.myth .myth-label { color: var(--alert); }
.myth-row.fact .myth-label { color: var(--gold); }
.myth-text { font-size: 14px; line-height: 1.5; }
.research-sources { display: flex; flex-wrap: wrap; gap: 8px; }
.source-chip { background: var(--bg-2); border: 1px solid var(--border); border-radius: 999px; padding: 8px 16px; font-size: 13px; color: var(--text-muted); }

/* === FOOTER === */
.preview-foot { text-align: center; padding: 60px 32px; color: var(--text-muted); font-size: 13px; border-top: 1px solid var(--border); margin-top: 80px; }
.preview-foot strong { color: var(--gold); }

/* === MOCKUP LABELS === */
.mockup-label { text-align: center; color: var(--text-muted); font-family: '__CLIENT_FONT__', serif; font-size: 12px; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 16px; }

/* === MODALS === */
.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 200; display: none; align-items: flex-start; justify-content: center; padding: 40px 20px; overflow-y: auto; }
.modal.show { display: flex; }
.modal-card { background: var(--bg-2); border: 1px solid var(--border); border-radius: 12px; max-width: 880px; width: 100%; position: relative; box-shadow: 0 30px 80px rgba(0,0,0,0.5); }
.modal-close { position: sticky; top: 0; float: right; z-index: 10; background: var(--bg); color: var(--text); border: 1px solid var(--border); width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 20px; line-height: 1; margin: 16px 16px 0 0; }
.modal-close:hover { background: var(--gold); color: var(--bg); border-color: var(--gold); }
.modal-body { padding: 0 48px 48px; clear: both; }
.modal-pillar { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; margin-top: 32px; margin-bottom: 12px; }
.modal-title { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 32px; line-height: 1.2; margin-bottom: 24px; }
.modal-meta { display: flex; gap: 20px; font-size: 13px; color: var(--text-muted); margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }
.modal-meta strong { color: var(--gold); }
.modal-content { font-size: 15px; line-height: 1.7; color: var(--text); }
.modal-content h1, .modal-content h2 { font-family: '__CLIENT_FONT__', serif; font-weight: 600; margin: 32px 0 16px; }
.modal-content h1 { font-size: 24px; color: var(--gold); }
.modal-content h2 { font-size: 19px; color: var(--text); }
.modal-content h3 { font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 16px; margin: 24px 0 12px; }
.modal-content p { margin-bottom: 16px; }
.modal-content ul, .modal-content ol { margin: 0 0 16px 22px; }
.modal-content li { margin-bottom: 8px; }
.modal-content strong { color: var(--gold-light); }
.modal-content a { color: var(--gold); }
.modal-content code { background: var(--bg); padding: 2px 6px; border-radius: 3px; color: var(--gold-light); font-family: 'Menlo', monospace; font-size: 13px; }
.modal-content blockquote { border-left: 3px solid var(--gold); padding-left: 20px; color: var(--text-muted); margin: 20px 0; font-style: italic; }
.modal-content hr { border: 0; border-top: 1px solid var(--border); margin: 32px 0; }
.signoff-bar { position: sticky; bottom: 0; background: var(--bg-2); border-top: 1px solid var(--border); padding: 16px 48px; display: flex; gap: 12px; align-items: center; border-radius: 0 0 12px 12px; margin: 0 -48px -48px; }
.signoff-label { color: var(--text-muted); font-size: 13px; flex: 1; }
.signoff-btn { padding: 10px 20px; border-radius: 6px; cursor: pointer; font-family: '__CLIENT_FONT__', serif; font-weight: 600; font-size: 13px; letter-spacing: 0.05em; text-transform: uppercase; border: none; }
.signoff-btn.approve { background: var(--gold); color: var(--bg); }
.signoff-btn.approve:hover { background: var(--gold-light); }
.signoff-btn.changes { background: transparent; color: var(--alert); border: 1px solid var(--alert); }
.signoff-btn.changes:hover { background: var(--alert); color: var(--bg); }
.cap-modal { max-width: 640px; }
.cap-modal-head { display: flex; align-items: center; gap: 14px; padding: 24px 32px; border-bottom: 1px solid var(--border); }
.cap-modal-head .platform { color: var(--gold); font-family: '__CLIENT_FONT__', serif; font-weight: 700; font-size: 12px; letter-spacing: 0.15em; text-transform: uppercase; }
.cap-modal-body { padding: 32px; font-size: 15px; line-height: 1.7; white-space: pre-wrap; }
.cap-status { display: inline-block; margin-left: 12px; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-family: '__CLIENT_FONT__', serif; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
.cap-status.approved { background: var(--gold); color: var(--bg); }
.cap-status.changes { background: var(--alert); color: var(--bg); }

@media (max-width: 768px) {
  .hero { padding: 48px 20px 40px; }
  .section { padding: 40px 20px; }
  .header-inner { padding: 16px 20px; }
  .tabs-inner { padding: 0 20px; }
  .grid-feed, .grid-blog { grid-template-columns: 1fr; }
  .phone-frame { width: 320px; height: 568px; }
  .modal-body { padding: 0 24px 24px; }
  .signoff-bar { padding: 12px 24px; margin: 0 -24px -24px; }
}
</style>
</head>
<body>

<!-- PASSCODE GATE -->
<div class="gate" id="gate">
  <div class="gate-inner">
    <div class="gate-mark">__CLIENT_NAME__</div>
    <div class="gate-tag">CLIENT PREVIEW · CONFIDENTIAL</div>
    <div class="gate-title">Marketing Preview · __CLIENT_PERIOD__</div>
    <div class="gate-sub">This page is private. Enter the four-digit access code shared with you.</div>
    <input type="password" class="gate-input" id="gate-input" maxlength="4" placeholder="• • • •" inputmode="numeric" autocomplete="off" />
    <button class="gate-btn" id="gate-btn">Enter Preview</button>
    <div class="gate-error" id="gate-error"></div>
  </div>
</div>

<!-- MAIN -->
<div id="main" style="display:none">

<header class="site-header">
  <div class="header-inner">
    <div class="brand">
      <div class="brand-mark">__CLIENT_NAME__</div>
      <div class="brand-divider"></div>
      <div class="brand-meta">Marketing Preview · __CLIENT_PERIOD__</div>
    </div>
    <div class="header-stat">75 ASSETS · 12 WEEKS</div>
  </div>
</header>

<section class="hero">
  <div class="hero-eyebrow">For Internal Review</div>
  <h1 class="hero-title">A complete content engine, ready to publish.</h1>
  <p class="hero-sub">__CLIENT_HERO_SUB__</p>
  <div class="hero-stats">
    <div><div class="stat-num">8</div><div class="stat-label">Blog Posts</div></div>
    <div><div class="stat-num">18</div><div class="stat-label">Videos<br>(6 × 3 formats)</div></div>
    <div><div class="stat-num">36</div><div class="stat-label">Social Captions<br>(12 × 3 platforms)</div></div>
    <div><div class="stat-num">~12k</div><div class="stat-label">Words of<br>Original Copy</div></div>
  </div>
</section>

<nav class="tabs">
  <div class="tabs-inner">
    <button class="tab active" data-target="research">Research</button>
    <button class="tab" data-target="blogs">Blog Posts</button>
    <button class="tab" data-target="instagram">Instagram</button>
    <button class="tab" data-target="reels">Reels &amp; TikTok</button>
    <button class="tab" data-target="stories">Stories</button>
    <button class="tab" data-target="facebook">Facebook</button>
    <button class="tab" data-target="linkedin">LinkedIn</button>
    <button class="tab" data-target="youtube">YouTube</button>
  </div>
</nav>

<section class="section active" id="sec-research">
  <h2 class="section-title">The Research Behind the Content</h2>
  <p class="section-sub">__CLIENT_RESEARCH_SUB__</p>
  <div class="research-stats" id="research-stats"></div>
  <h3 class="research-h3">What Your Audience Is Actually Searching For</h3>
  <p class="research-sub">Top categories ranked by public search volume and engagement. Each category lists the actual questions we found being asked.</p>
  <div class="research-categories" id="research-categories"></div>
  <h3 class="research-h3">Major 2026 Industry Changes (Timeline)</h3>
  <p class="research-sub">A chronological view of key industry changes. The asset library above is built around these.</p>
  <div class="research-timeline" id="research-timeline"></div>
  <h3 class="research-h3">The Most-Believed Myths (and the Truth)</h3>
  <p class="research-sub">High-shareability content opportunities — every one of these came up repeatedly in public discussions.</p>
  <div class="research-myths" id="research-myths"></div>
  <h3 class="research-h3">Sources Reviewed</h3>
  <div class="research-sources" id="research-sources"></div>
</section>

<section class="section" id="sec-blogs">
  <h2 class="section-title">Blog Posts (8)</h2>
  <p class="section-sub">__CLIENT_BLOG_SUB__</p>
  <div class="grid grid-blog" id="grid-blogs"></div>
</section>

<section class="section" id="sec-instagram">
  <h2 class="section-title">Instagram Feed Posts (12)</h2>
  <p class="section-sub">__CLIENT_IG_SUB__</p>
  <div class="grid grid-feed" id="grid-instagram"></div>
</section>

<section class="section" id="sec-reels">
  <h2 class="section-title">Reels &amp; TikTok (6)</h2>
  <p class="section-sub">25–35 second vertical videos with custom underscore. Same file works for Instagram Reels, TikTok, Facebook Reels, and YouTube Shorts.</p>
  <div class="grid grid-mobile" id="grid-reels"></div>
</section>

<section class="section" id="sec-stories">
  <h2 class="section-title">Stories (6 × 15s)</h2>
  <p class="section-sub">15-second vertical cuts for Instagram Stories, Facebook Stories, and WhatsApp Status.</p>
  <div class="grid grid-mobile" id="grid-stories"></div>
</section>

<section class="section" id="sec-facebook">
  <h2 class="section-title">Facebook Feed (12)</h2>
  <p class="section-sub">__CLIENT_FB_SUB__</p>
  <div class="grid grid-feed" id="grid-facebook"></div>
</section>

<section class="section" id="sec-linkedin">
  <h2 class="section-title">LinkedIn Feed (12)</h2>
  <p class="section-sub">__CLIENT_LI_SUB__</p>
  <div class="grid grid-feed" id="grid-linkedin"></div>
</section>

<section class="section" id="sec-youtube">
  <h2 class="section-title">YouTube (6)</h2>
  <p class="section-sub">16:9 horizontal versions for the YouTube main feed. Same vertical files double as YouTube Shorts.</p>
  <div class="grid" id="grid-youtube" style="grid-template-columns:1fr; max-width:760px; margin: 0 auto; gap:48px"></div>
</section>

<footer class="preview-foot">
  <p><strong>__CLIENT_NAME__</strong> · Marketing Preview · __CLIENT_PERIOD__</p>
  <p style="margin-top:8px">75 production-ready assets across 7 content pillars.</p>
  <p style="margin-top:16px; font-size:12px">Sign-off status auto-saves locally in your browser. Email <a href="mailto:__CLIENT_EMAIL__" style="color:var(--gold)">__CLIENT_EMAIL__</a> with any change requests.</p>
</footer>

</div>

<!-- BLOG MODAL -->
<div class="modal" id="blog-modal">
  <div class="modal-card" id="blog-modal-card">
    <button class="modal-close" onclick="closeModal('blog-modal')">×</button>
    <div class="modal-body" id="blog-modal-body"></div>
    <div class="signoff-bar">
      <div class="signoff-label" id="blog-signoff-label">Awaiting review</div>
      <button class="signoff-btn changes" onclick="markBlog('changes')">Request Changes</button>
      <button class="signoff-btn approve" onclick="markBlog('approve')">Approve</button>
    </div>
  </div>
</div>

<!-- CAPTION MODAL -->
<div class="modal" id="cap-modal">
  <div class="modal-card cap-modal" id="cap-modal-card">
    <button class="modal-close" onclick="closeModal('cap-modal')">×</button>
    <div class="cap-modal-head">
      <div class="platform" id="cap-platform"></div>
      <div style="flex:1; font-size:13px; color:var(--text-muted)" id="cap-week"></div>
    </div>
    <div class="cap-modal-body" id="cap-body"></div>
    <div class="signoff-bar">
      <div class="signoff-label" id="cap-signoff-label">Awaiting review</div>
      <button class="signoff-btn changes" onclick="markCaption('changes')">Request Changes</button>
      <button class="signoff-btn approve" onclick="markCaption('approve')">Approve</button>
    </div>
  </div>
</div>

<script>
const DATA = __DATA_JSON__;
const BLOG_IMAGE_MAP = __BLOG_IMAGE_MAP_JSON__;

// === Passcode gate ===
const PASS = "__CLIENT_PASSCODE__";
const SESS_KEY = "__CLIENT_SLUG___unlock";
const gate = document.getElementById("gate");
const main = document.getElementById("main");
const input = document.getElementById("gate-input");
const btn = document.getElementById("gate-btn");
const err = document.getElementById("gate-error");

function tryUnlock() {
  if (input.value === PASS) {
    gate.classList.add("hide");
    main.style.display = "block";
    sessionStorage.setItem(SESS_KEY, "1");
    render();
  } else {
    err.textContent = "Incorrect code. Try again.";
    input.value = "";
    input.focus();
  }
}
btn.addEventListener("click", tryUnlock);
input.addEventListener("keydown", (e) => { if (e.key === "Enter") tryUnlock(); });
input.addEventListener("input", () => { err.textContent = ""; });
input.focus();

// On page reload — restore state. The actual render() call is deferred to
// the bottom of the script so all `const` helpers (escapeHtml, linkify, etc.)
// are initialised by the time render() executes — otherwise top-level
// invocation here triggers a temporal-dead-zone ReferenceError.
if (sessionStorage.getItem(SESS_KEY) === "1") {
  gate.classList.add("hide");
  main.style.display = "block";
}

// === Tab switching ===
document.querySelectorAll(".tab").forEach((t) => {
  t.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".section").forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    document.getElementById("sec-" + t.dataset.target).classList.add("active");
    window.scrollTo({ top: document.querySelector(".tabs").offsetTop - 70, behavior: "smooth" });
  });
});

// === Sign-off persistence (localStorage) ===
const STORAGE_KEY = "__CLIENT_SLUG___signoff_v1";
function getSignoffs() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); } catch { return {}; } }
function setStatus(id, status) { const s = getSignoffs(); s[id] = status; localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); }
function getStatus(id) { return getSignoffs()[id] || ""; }
function badgeFor(id) {
  const status = getStatus(id);
  if (status === "approve") return ' <span class="cap-status approved">✓ Approved</span>';
  if (status === "changes") return ' <span class="cap-status changes">⚠ Changes</span>';
  return "";
}

// === Render helpers ===
const escapeHtml = (s) => (s || "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
// Hashtag regex: must start with a letter (so "#39" inside an escaped &#39;
// apostrophe doesn't match) and must NOT be preceded by '&' (so HTML entities
// like &#39; / &amp; survive intact). Without this guard, escapeHtml's `'` →
// `&#39;` gets split into `&` + <span>#39</span> + `;`, which renders as the
// literal characters "&#39;" in the page (caught on the Deidre Ras run, May 2026).
const linkify = (s) => escapeHtml(s).replace(/(https?:\/\/[^\s]+)/g, '<a style="color:#c9a25a" href="$1" target="_blank" rel="noopener">$1</a>').replace(/(^|[^&\w])(#[A-Za-z]\w*)/g, '$1<span style="color:#4dabf7">$2</span>');

// Video element factory. Prefers an MP4 (native <video controls>) when one
// was rendered into preview/assets/videos/<id>/<id>.mp4 — clean play button,
// no auto-play, no scene-overlap surprises. Falls back to the HyperFrames
// HTML in an iframe when MP4 isn't available (design preview only).
function videoMarkup(v, opts) {
  const o = opts || {};
  if (v.src_kind === "mp4") {
    const poster = o.poster ? ` poster="${escapeHtml(o.poster)}"` : "";
    const cls = o.cls || "phone-vid";
    return `<video class="${cls}" controls preload="metadata" playsinline${poster} src="${escapeHtml(v.src_path)}" title="${escapeHtml(v.title)}"></video>`;
  }
  // HTML iframe fallback — design preview only; HyperFrames runtime is not
  // present in a static iframe so scene-clipping won't apply.
  const style = o.iframeStyle || "";
  return `<iframe src="${escapeHtml(v.src_path)}" title="${escapeHtml(v.title)}" loading="lazy"${style ? ' style="' + style + '"' : ''}></iframe>`;
}

function md2html(md) {
  return (md || "")
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>")
    .replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>")
    .replace(/^---$/gm, "<hr>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/^([^<\n].+)$/gm, "$1")
    .replace(/<p><\/p>/g, "");
}

function getSocialImage(s) {
  const key = s.id.split("-")[0];
  const filename = BLOG_IMAGE_MAP[key] || "quote-card-bg.png";
  return "assets/images/" + filename;
}

// === Render: Research ===
function renderResearch() {
  const r = DATA.research;
  document.getElementById("research-stats").innerHTML = r.stats.map(s => `
    <div class="research-stat">
      <div class="research-stat-num">${escapeHtml(s.num)}</div>
      <div class="research-stat-label">${escapeHtml(s.label)}</div>
    </div>`).join("");
  document.getElementById("research-categories").innerHTML = r.categories.map(c => `
    <div class="research-cat">
      <div class="research-cat-head">
        <span class="research-cat-icon">${c.icon}</span>
        <span class="research-cat-title">${escapeHtml(c.title)}</span>
      </div>
      <div class="research-cat-rank">${escapeHtml(c.rank)}</div>
      <ul>${c.questions.map(q => `<li>${escapeHtml(q)}</li>`).join("")}</ul>
    </div>`).join("");
  document.getElementById("research-timeline").innerHTML = (r.changes_2026 || []).map(c => `
    <div class="timeline-item ${c.impact}">
      <span class="timeline-month">${escapeHtml(c.month)}</span>
      <div class="timeline-title">${escapeHtml(c.title)}</div>
      <div class="timeline-detail">${escapeHtml(c.detail)}</div>
    </div>`).join("");
  document.getElementById("research-myths").innerHTML = (r.myths || []).map(m => `
    <div class="myth-card">
      <div class="myth-row myth"><div class="myth-label">Myth</div><div class="myth-text">${escapeHtml(m.myth)}</div></div>
      <div class="myth-row fact"><div class="myth-label">Fact</div><div class="myth-text">${escapeHtml(m.fact)}</div></div>
    </div>`).join("");
  document.getElementById("research-sources").innerHTML = (r.sources || []).map(s => `
    <span class="source-chip">${escapeHtml(s)}</span>`).join("");
}

// === Render: Blogs ===
function renderBlogs() {
  const grid = document.getElementById("grid-blogs");
  grid.innerHTML = DATA.blogs.map(b => `
    <article class="blog-card" onclick="openBlog('${b.id}')">
      <div class="blog-hero-wrap">
        <img src="${escapeHtml(b.hero)}" alt="${escapeHtml(b.title)}" loading="lazy" onerror="this.style.opacity='0'" />
      </div>
      <div class="blog-body">
        <div class="blog-pillar">${escapeHtml(b.pillar)}${badgeFor("blog:" + b.id)}</div>
        <h3 class="blog-title">${escapeHtml(b.title)}</h3>
        <p class="blog-excerpt">${escapeHtml(b.excerpt)}</p>
        <div class="blog-foot">
          <span class="blog-words">${escapeHtml(b.word_count || "")} words</span>
          <span class="blog-cta">Read full post →</span>
        </div>
      </div>
    </article>`).join("");
}

// === Render: Instagram ===
function renderInstagram() {
  const grid = document.getElementById("grid-instagram");
  grid.innerHTML = DATA.socials.map(s => {
    const img = getSocialImage(s);
    const cap = (s.instagram || s.on_image || "").slice(0, 120);
    return `
    <div>
      <div class="mockup-label">Week ${s.week} · ${escapeHtml(s.format || "")}${badgeFor("cap:" + s.id + ":instagram")}</div>
      <article class="ig-post" onclick="openCaption('${s.id}','instagram')" style="cursor:pointer">
        <div class="ig-head">
          <div class="ig-avatar">__CLIENT_AVATAR__</div>
          <div class="ig-username">__CLIENT_IG_USERNAME__ <span class="verified">✓</span></div>
          <span class="ig-dots">···</span>
        </div>
        <img class="ig-media" src="${img}" loading="lazy" onerror="this.style.background='var(--bg-3)'" />
        <div class="ig-actions">❤️ 💬 📤 <span class="ig-spacer"></span> 🔖</div>
        <div class="ig-likes">${Math.floor(Math.random()*800+200)} likes</div>
        <div class="ig-caption"><span class="uname">__CLIENT_IG_USERNAME__</span>${linkify(cap)} <span class="more">… more</span></div>
        <div class="ig-time">2 hours ago</div>
      </article>
    </div>`;
  }).join("");
}

// === Render: Reels ===
function renderReels() {
  const grid = document.getElementById("grid-reels");
  grid.innerHTML = DATA.videos.map(v => {
    const social = DATA.socials.find(s => s.id.startsWith(v.linked_social)) || {};
    const cap = (social.instagram || "").slice(0, 90);
    return `
    <div>
      <div class="mockup-label">${escapeHtml(v.id)} · ${v.duration}s · Reel / Short</div>
      <div class="phone-frame">
        ${videoMarkup(v)}
        <div class="phone-overlay ig-reel">
          <div class="reel-top"><span>Reels</span><span>✦</span></div>
          <div class="reel-bottom-text">
            <span class="uname">@__CLIENT_IG_USERNAME__</span>
            ${escapeHtml(cap)}${cap.length >= 90 ? "…" : ""}
          </div>
          <div class="reel-side">
            <div><div class="reel-side-icon">❤️</div>${Math.floor(Math.random()*3000+400)}</div>
            <div><div class="reel-side-icon">💬</div>${Math.floor(Math.random()*200+30)}</div>
            <div><div class="reel-side-icon">📤</div></div>
          </div>
          <div class="reel-music"><span class="reel-music-icon">♪</span> Original audio · __CLIENT_NAME__</div>
        </div>
      </div>
    </div>`;
  }).join("");
}

// === Render: Stories ===
function renderStories() {
  const grid = document.getElementById("grid-stories");
  grid.innerHTML = DATA.videos.map(v => `
    <div>
      <div class="mockup-label">${escapeHtml(v.id)} · 15s · Story</div>
      <div class="phone-frame">
        ${videoMarkup(v)}
        <div class="phone-overlay story">
          <div class="story-bar"></div>
          <div class="story-head">
            <div class="story-avatar">__CLIENT_AVATAR__</div>
            <span class="story-uname">__CLIENT_IG_USERNAME__</span>
            <span class="story-time">now</span>
          </div>
        </div>
      </div>
    </div>`).join("");
}

// === Render: Facebook ===
function renderFacebook() {
  const grid = document.getElementById("grid-facebook");
  grid.innerHTML = DATA.socials.map(s => {
    const img = getSocialImage(s);
    return `
    <div>
      <div class="mockup-label">Week ${s.week} · Facebook${badgeFor("cap:" + s.id + ":facebook")}</div>
      <article class="fb-post" onclick="openCaption('${s.id}','facebook')" style="cursor:pointer">
        <div class="fb-head">
          <div class="fb-avatar">__CLIENT_AVATAR__</div>
          <div>
            <div class="fb-name">__CLIENT_NAME__</div>
            <div class="fb-meta">2 hrs</div>
          </div>
        </div>
        <div class="fb-text">${linkify(s.facebook || "")}</div>
        <img class="fb-media" src="${img}" loading="lazy" onerror="this.style.display='none'" />
        <div class="fb-stats"><span>👍❤️🤝 ${Math.floor(Math.random()*180+40)}</span><span>${Math.floor(Math.random()*30+4)} comments · ${Math.floor(Math.random()*20+3)} shares</span></div>
        <div class="fb-actions">
          <div class="fb-action">👍 Like</div>
          <div class="fb-action">💬 Comment</div>
          <div class="fb-action">↪ Share</div>
        </div>
      </article>
    </div>`;
  }).join("");
}

// === Render: LinkedIn ===
function renderLinkedIn() {
  const grid = document.getElementById("grid-linkedin");
  grid.innerHTML = DATA.socials.map(s => {
    const img = getSocialImage(s);
    return `
    <div>
      <div class="mockup-label">Week ${s.week} · LinkedIn${badgeFor("cap:" + s.id + ":linkedin")}</div>
      <article class="li-post" onclick="openCaption('${s.id}','linkedin')" style="cursor:pointer">
        <div class="li-head">
          <div class="li-avatar">__CLIENT_AVATAR__</div>
          <div style="flex:1">
            <div class="li-name">__CLIENT_NAME__</div>
            <div class="li-headline">__CLIENT_LI_HEADLINE__</div>
            <div class="li-time">2h · 🌍</div>
          </div>
        </div>
        <div class="li-text">${linkify(s.linkedin || "")}</div>
        <img class="li-media" src="${img}" loading="lazy" onerror="this.style.display='none'" />
        <div class="li-stats">👍 ${Math.floor(Math.random()*120+30)} reactions · ${Math.floor(Math.random()*22+3)} comments · ${Math.floor(Math.random()*18+2)} reposts</div>
        <div class="li-actions">
          <div class="li-action">👍 Like</div>
          <div class="li-action">💬 Comment</div>
          <div class="li-action">↪ Repost</div>
          <div class="li-action">→ Send</div>
        </div>
      </article>
    </div>`;
  }).join("");
}

// === Render: YouTube ===
function renderYouTube() {
  const grid = document.getElementById("grid-youtube");
  grid.innerHTML = DATA.videos.map(v => `
    <div>
      <div class="mockup-label">${escapeHtml(v.id)} · YouTube</div>
      <article class="yt-card">
        <div class="yt-video">
          ${videoMarkup(v, { iframeStyle: "width:1080px;height:1920px;border:none;transform:scale(0.3333);transform-origin:top left;pointer-events:none;" })}
        </div>
        <div class="yt-meta">
          <div class="yt-title">${escapeHtml(v.title)} | __CLIENT_NAME__</div>
          <div class="yt-channel">__CLIENT_NAME__ · ${Math.floor(Math.random()*5+2)}.${Math.floor(Math.random()*9+1)}K subscribers</div>
          <div class="yt-stats">${Math.floor(Math.random()*3000+500)} views · 2 days ago</div>
        </div>
      </article>
    </div>`).join("");
}

// === Blog modal ===
let activeBlogId = null;
function openBlog(id) {
  activeBlogId = id;
  const blog = DATA.blogs.find(b => b.id === id);
  if (!blog) return;
  document.getElementById("blog-modal-body").innerHTML = `
    <div class="blog-hero-wrap" style="border-radius:8px 8px 0 0">
      <img src="${escapeHtml(blog.hero)}" alt="${escapeHtml(blog.title)}" onerror="this.style.opacity='0'" style="width:100%;aspect-ratio:16/9;object-fit:cover;display:block;" />
    </div>
    <div class="modal-pillar">${escapeHtml(blog.pillar)}${badgeFor("blog:" + id)}</div>
    <div class="modal-title">${escapeHtml(blog.title)}</div>
    <div class="modal-meta"><span><strong>Pillar</strong> ${escapeHtml(blog.pillar)}</span><span><strong>Length</strong> ~${escapeHtml(blog.word_count || "1,400")} words</span></div>
    <div class="modal-content"><p>${md2html(blog.body)}</p></div>`;
  const label = document.getElementById("blog-signoff-label");
  const st = getStatus("blog:" + id);
  label.textContent = st === "approve" ? "✓ Approved" : st === "changes" ? "⚠ Changes requested" : "Awaiting review";
  document.getElementById("blog-modal").classList.add("show");
  document.body.style.overflow = "hidden";
}
function markBlog(status) {
  if (!activeBlogId) return;
  setStatus("blog:" + activeBlogId, status);
  const label = document.getElementById("blog-signoff-label");
  label.textContent = status === "approve" ? "✓ Approved" : "⚠ Changes requested";
  renderBlogs();
}

// === Caption modal ===
let activeSocialId = null, activePlatform = null;
function openCaption(id, platform) {
  activeSocialId = id;
  activePlatform = platform;
  const social = DATA.socials.find(s => s.id === id);
  if (!social) return;
  const cap = social[platform] || "";
  document.getElementById("cap-platform").textContent = platform.toUpperCase();
  document.getElementById("cap-week").textContent = "Week " + social.week + " · " + (social.format || "");
  document.getElementById("cap-body").textContent = cap;
  const label = document.getElementById("cap-signoff-label");
  const st = getStatus("cap:" + id + ":" + platform);
  label.textContent = st === "approve" ? "✓ Approved" : st === "changes" ? "⚠ Changes requested" : "Awaiting review";
  document.getElementById("cap-modal").classList.add("show");
  document.body.style.overflow = "hidden";
}
function markCaption(status) {
  if (!activeSocialId || !activePlatform) return;
  setStatus("cap:" + activeSocialId + ":" + activePlatform, status);
  const label = document.getElementById("cap-signoff-label");
  label.textContent = status === "approve" ? "✓ Approved" : "⚠ Changes requested";
  if (activePlatform === "linkedin") renderLinkedIn();
  else if (activePlatform === "facebook") renderFacebook();
  else renderInstagram();
}

function closeModal(id) {
  document.getElementById(id).classList.remove("show");
  document.body.style.overflow = "";
}
document.querySelectorAll(".modal").forEach(m => {
  m.addEventListener("click", e => { if (e.target === m) closeModal(m.id); });
});
document.addEventListener("keydown", e => {
  if (e.key === "Escape") document.querySelectorAll(".modal.show").forEach(m => closeModal(m.id));
});

function render() {
  renderResearch();
  renderBlogs();
  renderInstagram();
  renderReels();
  renderStories();
  renderFacebook();
  renderLinkedIn();
  renderYouTube();
}

// Final boot — runs AFTER every const helper above is initialised, so the
// reload branch and any other auto-render path can safely call render()
// without a temporal-dead-zone ReferenceError on escapeHtml / linkify.
if (sessionStorage.getItem(SESS_KEY) === "1") {
  render();
}
</script>
</body>
</html>
"""

# ---------- Apply token replacements ----------
blog_image_map_json = json.dumps(BLOG_IMAGE_MAP, ensure_ascii=False)

# Google Fonts URL needs "+" instead of spaces
font_url = CLIENT["font"].replace(" ", "+")

out_html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
out_html = out_html.replace("__BLOG_IMAGE_MAP_JSON__", blog_image_map_json)
out_html = out_html.replace("__CLIENT_NAME__", CLIENT["name"])
out_html = out_html.replace("__CLIENT_SLUG__", CLIENT["slug"])
out_html = out_html.replace("__CLIENT_PERIOD__", CLIENT["period"])
out_html = out_html.replace("__CLIENT_EMAIL__", CLIENT["email"])
out_html = out_html.replace("__CLIENT_AVATAR__", CLIENT["avatar"])
out_html = out_html.replace("__CLIENT_PASSCODE__", CLIENT["passcode"])
out_html = out_html.replace("__CLIENT_ACCENT__", CLIENT["accent"])
out_html = out_html.replace("__CLIENT_ACCENT_LIGHT__", CLIENT["accent_light"])
out_html = out_html.replace("__CLIENT_BG__", CLIENT["bg"])
out_html = out_html.replace("__CLIENT_BG2__", CLIENT["bg2"])
out_html = out_html.replace("__CLIENT_BG3__", CLIENT["bg3"])
out_html = out_html.replace("__CLIENT_FONT_URL__", font_url)
out_html = out_html.replace("__CLIENT_FONT__", CLIENT["font"])
out_html = out_html.replace("__CLIENT_LI_HEADLINE__", CLIENT["li_headline"])
out_html = out_html.replace("__CLIENT_IG_USERNAME__", CLIENT["ig_username"])
out_html = out_html.replace("__CLIENT_HERO_SUB__", CLIENT["hero_sub"])
out_html = out_html.replace("__CLIENT_RESEARCH_SUB__", CLIENT["research_sub"])
out_html = out_html.replace("__CLIENT_BLOG_SUB__", CLIENT["blog_sub"])
out_html = out_html.replace("__CLIENT_IG_SUB__", CLIENT["ig_sub"])
out_html = out_html.replace("__CLIENT_LI_SUB__", CLIENT["li_sub"])
out_html = out_html.replace("__CLIENT_FB_SUB__", CLIENT["fb_sub"])

out_path = ROOT / "index.html"
out_path.write_text(out_html, encoding="utf-8")

# Mirror images + videos from ../images/ and ../videos/ into ./assets/.
# Idempotent — only copies new or modified files. Eliminates a manual step
# (and the 404s that caused on the Deidre Ras run).
sync_assets()

print(f"OK {out_path} — blogs:{len(blogs)} socials:{len(socials)} videos:{len(VIDEOS)}")
print(f"   Total size: {out_path.stat().st_size // 1024} KB")
