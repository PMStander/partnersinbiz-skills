# How to Actually Use This Marketing Workspace

This guide walks you through publishing **one social post**, end-to-end, so the layout finally makes sense. Then it shows how the same logic applies to all the other content types.

---

## The Mental Model (read this first)

For every piece of content there are **three layers**:

1. **The visual** — what the eye sees (an image or video)
2. **The on-image text** — words painted ON TOP of the visual
3. **The caption** — words posted NEXT TO the visual on the platform

Think of it like a billboard:

```
┌─────────────────────────────────┐
│                                 │
│   [BIG VISUAL — gold + black]   │  ← The image (Layer 1)
│                                 │
│      "YOU CAN'T BE              │  ← On-image text (Layer 2)
│       ARRESTED FOR DEBT"        │     painted onto Layer 1
│                                 │
└─────────────────────────────────┘
        AHS Law · ahslaw.co.za     ← Watermark (still Layer 2)

CAPTION (Layer 3 — typed into Facebook/LinkedIn/Instagram):
"Debt collectors love to threaten arrest. Here's why they're lying.
[The longer story goes here. Posted as text below the image.]"
```

The image file alone has NO words on it. You add the text using a free design tool (Canva is the easiest). The caption is just typed directly into Facebook/Instagram/LinkedIn when you post.

---

## Walkthrough: Publishing W01 to Facebook

Let's do **Week 1 — the PIE Act / locks post — to Facebook**, step by step.

### Step 1: Open the post file

Open `marketing/social-media/W01-pie-act-locks.md` in any text editor. Inside, you'll find sections like:

- `image_prompt:` — the description used to generate the image
- `on_image_text:` — the words you'll paint on top
- `linkedin_caption:` — what you'll paste into LinkedIn
- `instagram_caption:` — what you'll paste into Instagram
- `facebook_caption:` — what you'll paste into Facebook

These are SEPARATE INGREDIENTS. You combine them on the platform.

### Step 2: Get the image

You already have the reusable card backgrounds at:
- `marketing/images/social/quote-card-bg.png` (1:1 — Facebook/Instagram feed)
- `marketing/images/social/quote-card-vertical.png` (9:16 — Stories/Reels)

The blog hero image also works as a Facebook image:
- `marketing/images/blog/B1-pie-act-locks.png`

For W01, use the **blog hero image** (`B1-pie-act-locks.png`) because it ties directly to the related blog post.

### Step 3: Add the on-image text using Canva (free)

This is the part that wasn't making sense before. Here it is:

1. Go to **canva.com** (free signup, no design skills needed)
2. Click **Create a design** → **Custom size** → enter **1200 × 1200** for Facebook square (or use one of Canva's "Facebook Post" templates)
3. Click **Uploads** in the left sidebar → drag `B1-pie-act-locks.png` into Canva
4. Drag the image into your blank canvas — it fills the background
5. Click **Text** in the left sidebar → click "Add a heading"
6. Type the on-image text from the post file (e.g., "Your landlord cannot change the locks.")
7. Style it:
   - **Font:** Raleway, Bold (search "Raleway" in the font picker)
   - **Color:** Gold `#c9a25a` (paste this hex code)
   - **Size:** big enough to read on a phone (~80–120pt)
8. Position it over the dark area of the image (the gold light part should stay clear so it doesn't fight the text)
9. Add a small "AHS Law" watermark in the bottom-right corner (24pt, Raleway, gold #c9a25a)
10. Click **Share** → **Download** → PNG → save as `W01-facebook.png`

You now have a finished social image with text baked in.

> **Tip:** Once you've made one, save it as a Canva "template." For Week 2 you just swap the background image and change the text — takes 60 seconds per post.

### Step 4: Post to Facebook

1. Go to your AHS Law Facebook page (`@ahstander`)
2. Click **Create post**
3. Click the **photo icon** → upload `W01-facebook.png` (the version with text on it)
4. In the caption box, paste the `facebook_caption` from `W01-pie-act-locks.md`
5. Click **Post**

That's it. The image carries the headline. The caption carries the story.

---

## Why Two Texts? (Caption AND On-Image Text)

This is the bit that confuses everyone. Here's why both exist:

| Layer | Job | Length | Read When |
|---|---|---|---|
| **On-image text** | Stop the scroll | 1 short headline (5–10 words) | The instant the image appears in feed |
| **Caption** | Tell the story | Full paragraph(s) | After the image already grabbed them |

People scroll fast. They'll see the image for 0.3 seconds. The on-image text has to land in that 0.3 seconds — so it's short and bold. If they slow down, they read the caption underneath for the full story.

**Same image, three captions:**
- LinkedIn caption is **professional and long** (150–250 words, sources cited)
- Instagram caption is **punchy and short** (people are there for visuals, not essays)
- Facebook caption is **conversational** (community tone, like a friend explaining)

You use the SAME image for all three platforms but a DIFFERENT caption for each.

---

## The Three Post Formats Explained

The master plan calls for three rotating formats. Here's what each looks like and which background to use:

### Format 1: Quote Card

**Visual:** Plain dark background, big single quote.

**Background to use:** `images/social/quote-card-bg.png` (1:1) or `quote-card-vertical.png` (9:16)

**On-image text:** A pull-quote from a blog post, e.g.:
```
"Self-help evictions are
a CRIMINAL offence."

— PIE Act 19 of 1998
```

**Used for weeks:** W01, W03, W07, W09, W11

### Format 2: Stat Card

**Visual:** Dark obsidian background with a single beam of gold light.

**Background to use:** `images/social/stat-card-bg.png`

**On-image text:** ONE big number + one line of context:
```
R22,466.74

The new earnings threshold
from 1 May 2026
```

**Used for weeks:** W02, W06, W08, W10

### Format 3: Myth vs Fact

**Visual:** Split background — red tint on left, gold on right.

**Background to use:** `images/social/myth-fact-bg.png`

**On-image text:** Two-panel design:
```
        MYTH                  FACT

You can be arrested      Debt is a CIVIL
   for debt.            matter, not criminal.
```

**Used for weeks:** W04, W05

### Format 4: Roundup (W12 only)

**Visual:** Any of the above, used as a carousel of multiple slides.

---

## Visual Cheatsheet — How to Lay Out Each Format in Canva

```
┌────────── QUOTE CARD (1:1) ──────────┐
│                                      │
│   [optional small label, gold]       │
│                                      │
│                                      │
│      "The big quote goes here.       │  ← Raleway 600, white #fff
│       Two lines max, large."         │
│                                      │
│      — Source attribution            │  ← Open Sans, gold #c9a25a
│                                      │
│                                      │
│                          AHS · ahslaw.co.za  ← bottom right
└──────────────────────────────────────┘


┌────────── STAT CARD (1:1) ───────────┐
│                                      │
│                                      │
│         R22,466.74                   │  ← Raleway 800, gold #c9a25a, HUGE
│                                      │
│   The new earnings threshold         │  ← Raleway 400, white, smaller
│   from 1 May 2026                    │
│                                      │
│                                      │
│                          AHS · ahslaw.co.za
└──────────────────────────────────────┘


┌────────── MYTH vs FACT (1:1) ────────┐
│                                      │
│  ╔══════════╗      ╔══════════╗      │
│  ║   MYTH   ║      ║   FACT   ║      │  ← Raleway 700, uppercase
│  ╚══════════╝      ╚══════════╝      │     red box / gold box
│                                      │
│   You can be       Debt is a         │  ← Open Sans body
│   arrested for     CIVIL matter,     │
│   debt.            not criminal.     │
│                                      │
│                          AHS · ahslaw.co.za
└──────────────────────────────────────┘
```

---

## Type Specs to Plug Into Canva

| Element | Font | Size (on 1200×1200) | Color | Weight |
|---|---|---|---|---|
| Big stat number | Raleway | 220–280 pt | `#c9a25a` | 800 |
| Headline / Quote | Raleway | 80–120 pt | `#ffffff` | 600 |
| Body / Caption text | Open Sans | 36–48 pt | `#ffffff` | 400 |
| MYTH label | Raleway | 60 pt | `#e07070` | 700, uppercase, letter-spacing 0.15em |
| FACT label | Raleway | 60 pt | `#c9a25a` | 700, uppercase, letter-spacing 0.15em |
| Source attribution | Open Sans | 32 pt | `#c9a25a` | 400 |
| Watermark "AHS · ahslaw.co.za" | Raleway | 28 pt | `#c9a25a` (60% opacity) | 600 |

Download the fonts from Google Fonts if Canva doesn't have them by default:
- [Raleway](https://fonts.google.com/specimen/Raleway)
- [Open Sans](https://fonts.google.com/specimen/Open+Sans)

---

## How to Use the Videos

The videos already have all text BAKED IN. You don't add anything else to the visual. The video is finished.

For each platform:

### Instagram Reels
1. Open Instagram on your phone
2. Tap **+** at the top → **Reel**
3. Tap the **gallery** icon (bottom-left) → select `marketing/videos/V1-landlord-cant-do/V1-landlord-cant-do.mp4`
4. Skip all the editing tools (it's already finished)
5. Tap **Next**
6. Paste the `instagram_caption` from `marketing/social-media/W01-pie-act-locks.md`
7. Tap **Share**

### Facebook Reels
1. Open Facebook → AHS Law page (`@ahstander`)
2. Click **Create post** → **Reel**
3. Upload the same .mp4 file
4. Paste the `facebook_caption`
5. Post

### TikTok
1. Open TikTok → tap **+**
2. Tap **Upload** → select the .mp4
3. Skip all effects (don't add TikTok text)
4. Paste the caption (use the Instagram one — it's TikTok-friendly)
5. Post

### LinkedIn (videos work but feed is mostly square)
1. Click **Start a post** → **Add media**
2. Upload the .mp4 (LinkedIn accepts vertical)
3. Paste the `linkedin_caption`
4. Post

The video file is the visual. The caption is the words. That's it.

---

## How to Use the Blog Posts

Blog posts are markdown files in `marketing/blog-posts/`. They have YAML frontmatter at the top, then the body.

### Option A: Paste into your blog CMS

1. Open the .md file (e.g., `B1-pie-act-locks.md`)
2. Copy the **body** (everything after the closing `---` of the frontmatter)
3. Paste into your CMS's article editor
4. Upload the hero image (`marketing/images/blog/B1-pie-act-locks.png`) as the article banner
5. Set the title, slug, and meta description from the frontmatter
6. Add the references list as the "Sources" section at the end
7. Publish

### Option B: Use the markdown directly (static site / Hugo / Jekyll / Astro)

Drop the .md file straight into your `content/blog/` folder. Most static-site generators read the YAML frontmatter automatically.

### LinkedIn Article (recycle the blog)

You can re-publish the same blog post as a LinkedIn Article (better reach than a regular post):
1. On LinkedIn → **Write article**
2. Paste the headline, hero image, and body
3. Add the references at the end with hyperlinks
4. Publish

---

## Posting Schedule At-a-Glance

For each Week N:

| Day | Action | File to Open |
|---|---|---|
| **Monday morning** | Publish blog post | `marketing/blog-posts/B[n]-*.md` + hero image |
| **Monday lunch** | Share blog post on LinkedIn (just paste the URL) | `marketing/blog-posts/B[n]-*.md` (use opening 2 paragraphs as the LinkedIn post text) |
| **Wednesday morning** | Post video to Reels / TikTok / FB | `marketing/videos/V[n]-*/V[n]-*.mp4` + Instagram caption from the matching social post file |
| **Wednesday afternoon** | Post the same video to LinkedIn | Same .mp4 + LinkedIn caption from the social post file |
| **Friday morning** | Post the social card | Make in Canva using `marketing/social-media/W[NN]-*.md` (image prompt + on-image text + caption) |

Each week takes ~30 minutes once you've made the Canva templates. The first week is the slow one because you're building the templates.

---

## A Worked Example: Week 1, Step by Step

1. **Monday — publish blog**
   - Open `marketing/blog-posts/B1-pie-act-locks.md`
   - Hero image: `marketing/images/blog/B1-pie-act-locks.png`
   - Paste body into your blog → publish at `ahslaw.co.za/blog/pie-act-locks`
   - Tweet/post the URL on LinkedIn with the hook line

2. **Wednesday — post video**
   - File: `marketing/videos/V1-landlord-cant-do/V1-landlord-cant-do.mp4`
   - Open Instagram → Reels → upload the file
   - Caption: open `marketing/social-media/W01-pie-act-locks.md`, copy the Instagram caption
   - Post
   - Repeat for Facebook (same file, Facebook caption)
   - Repeat for LinkedIn (same file, LinkedIn caption)

3. **Friday — social card**
   - Open Canva (free) → 1200×1200 canvas
   - Background: drag in `marketing/images/blog/B1-pie-act-locks.png`
   - Add text overlay (from `W01-pie-act-locks.md` `on_image_text` field):
     - "Your landlord cannot change the locks." (Raleway 600, white, ~100pt)
     - Sub-line: "PIE Act 19 of 1998" (Open Sans, gold, ~36pt)
   - Add "AHS · ahslaw.co.za" bottom-right (Raleway, gold, 28pt)
   - Download as PNG
   - Post to Facebook with the Facebook caption from the same .md file
   - Post to Instagram (you can post the same image as a feed post) with Instagram caption
   - Post to LinkedIn with LinkedIn caption

That's a full content week from one folder.

---

## What If I Don't Want to Use Canva?

Alternatives that work the same way:

- **Figma** (free, more powerful) — open the image, add text layers, export PNG
- **Keynote** (Mac, already installed) — drop image on slide, add text boxes, export slide as PNG
- **Photoshop / Affinity Photo** — same logic, more control

The principle is identical no matter the tool: **image as background → text on top → export as PNG → post.**

---

## Common Gotchas

- **Don't post the raw blog hero image with NO text overlay** to social feed. It will look like a stock photo. The text is what makes it a "post."
- **Don't paste the full blog body as a Facebook caption.** Facebook truncates at ~250 characters. Use the dedicated Facebook caption from the social post file.
- **Don't change the gold colour.** `#c9a25a` is the brand. Other golds will look cheap.
- **Don't use emoji-heavy captions.** AHS Law's tone is restrained. One emoji max per post.
- **Always add the watermark** ("AHS · ahslaw.co.za") to every image. People save and share screenshots — the watermark is your free advertising.

---

## When You're Ready to Scale

Once you've published a few weeks and seen what works, you can:

1. **Hire a VA** to run the Canva step (it's repetitive)
2. **Use a scheduler** (Buffer, Hootsuite, Meta Business Suite) — schedule a month ahead in one Sunday
3. **Boost the best-performing posts** with R200–R500 of paid ads
4. **Repurpose** — the video clip becomes a YouTube Short, the carousel becomes a Threads post, the blog becomes a newsletter

But none of that matters until you publish week 1. Start there.

---

*Last updated: 25 April 2026 · Maintained by Lex.*
