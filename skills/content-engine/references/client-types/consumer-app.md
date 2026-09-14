# Client Type — Consumer App

**Examples:** Mobile apps (iOS / Android / cross-platform), B2C web apps, productivity tools, fitness/wellness apps, education apps, lifestyle apps, creator tools.

Internal Cowork examples that fit this category: **Lumen** (speed reading), **Velox** (productivity), **YouTube Shorts pipeline**, future apps.

## Pillar Structure (7)

Pillars map to **user benefits + feature areas + lifecycle stages**, not regulatory categories.

Standard mix:
1. **Use Cases** — concrete situations where the app helps (commute, studying, before bed, weekend project)
2. **Features Deep-Dive** — one major feature per post, what it does + why it matters
3. **Tutorials & How-To** — step-by-step guides with screenshots
4. **User Stories / Case Studies** — real users, real outcomes (with metrics)
5. **Comparisons** — vs competitors, vs the manual way, vs older apps
6. **Behind the Scenes** — why we built it, what we learned, design decisions
7. **Release Notes & Updates** — feature launches, version highlights

For Lumen specifically:
- Use cases: morning news catch-up, exam prep, research papers, audiobook alternative
- Features: speed reading engine, vocabulary builder, progress tracking, dark mode
- Tutorials: "how to read 500 wpm in a week", "import a PDF", "speed-read on your commute"

## Tone of Voice

| Do | Don't |
|---|---|
| Enthusiastic but not breathless | Hype-y / breathless |
| User-centric — "you" focused | Feature-list dumps |
| Concrete: "save 3 hours a week" | Vague: "boost productivity" |
| Show, don't tell — screenshots, GIFs, videos | Text walls without visuals |
| Acknowledge friction honestly | Pretend everything is perfect |
| Real user quotes (with permission) | Fake testimonials |

The vibe target: somewhere between Notion's blog and Linear's changelog. Smart, design-aware, lightly playful, never corporate.

## Blog Post Structure

7–8 sections, ~1,200–1,800 words. Different from service-business — much more visual:

1. **Hook** — the user problem in one sentence
2. **Why this matters** — the real-world cost of not solving it
3. **How [App] solves it** — feature walkthrough with **screenshots** (this is critical)
4. **A real example** — concrete scenario, ideally with a real user
5. **Tips & advanced use** — power-user moves
6. **What's next** — roadmap teaser if relevant
7. **Try it** — clear CTA: download link, sign-up, or specific feature URL
8. **Sources / further reading** — only if relevant; not always needed

## Hero Image Style

Three categories, all generated via Imagen + post-processed in Figma/Canva:

1. **App UI in device frames** — your actual app screenshots placed in iPhone / Android / MacBook frames. Imagen generates the lifestyle background; you composite the screenshot.
2. **Lifestyle + product** — person using the app in context (commute, gym, desk). The screen content is the app.
3. **Abstract / aesthetic** — typography, gradients, minimal compositions for tutorials and behind-the-scenes posts.

Master suffix shifts to:
```
modern minimalist editorial photography, soft natural light, lifestyle context,
shallow depth of field, premium consumer brand aesthetic, [app accent color],
phone or laptop visible but not the focus, clean composition,
ultra-sharp details, photorealistic, no text overlay
```

Less Hasselblad-luxury, more Apple-product-page.

**Critical:** Don't have Imagen generate the app UI itself — it'll hallucinate. Generate the surrounding context, then drop the real screenshot in via Figma.

## Video Formats (6)

For consumer apps, videos do most of the conversion work. Lean heavier into them:

1. **Feature demo** — 30-second screen recording with caption overlays
2. **Use-case story** — "Sarah uses [app] to read 5 books a month" with screen + lifestyle B-roll
3. **Before / After** — 5 seconds of the old way, 5 seconds of the new way
4. **Speed run / Tutorial** — accomplish a task in 30 seconds
5. **Founder voice / Story** — quick narrative about why it exists (works well for early-stage)
6. **Announcement / Update** — new feature reveal with the counter / stat reveal pattern

Music: same procedural underscore script works fine. For app launches you might want something more upbeat — bump BPM to 110, add a percussion layer.

## Social Post Templates

Three formats rotated weekly, but with different visuals than service-business:

- **Feature Highlight Card** — screenshot of the feature + one-line benefit caption
- **Stat Card** — user numbers, downloads, "users in 50 countries" etc.
- **User Quote Card** — real testimonial, source name (or anonymized initial)

Plus optional:
- **Carousel** (Instagram) — 5–10 slides walking through a feature

## App Store / Play Store Integration

This is the unique-to-app piece. Add to your Phase 2 calendar:
- **App Store screenshots** — use the existing `aso-appstore-screenshots` skill in your library
- **App Store description updates** — co-update with each release note blog post
- **Promo videos** for App Store / Play Store (vertical, 15s) — your Stories cuts double for this
- **Apple Search Ads creative** — repurpose the same image library

The `aso-appstore-screenshots` skill is a perfect companion — kick it off in parallel during Phase 4.

## Distribution Channels

Same as service-business **plus**:
- **App Store / Play Store listing** (screenshots, description, what's new)
- **ProductHunt** (if launching new features)
- **Reddit** subreddit-relevant posts (r/productivity for Lumen, r/iOSApps, r/ProductivityApps)
- **YouTube** (longer-form how-to videos — your YouTube horizontal cuts work here)
- **In-app announcements** — push notifications, in-app banners promoting the new content

## Reference Library

Different sources than service-business:
- **Reddit threads** for user pain points (r/productivity, r/getdisciplined, app-specific subs)
- **App Store / Play Store reviews** — direct quotes from real users (with permission)
- **Twitter / X threads** about the problem space
- **Industry research** — Pew Research on device usage, Statista on app categories
- **Indie hacker / SaaS communities** — Indie Hackers, Hacker News for distribution lessons

## What's Universal vs Specific

Universal: pipeline, scripts, video framework, preview site, deploy.

App-specific changes:
- Pillar names (use cases / features / tutorials, not practice areas)
- Image style (UI mockups + lifestyle, not editorial objects)
- Tone (enthusiastic-user-centric, not empathetic-authoritative)
- Distribution adds App Store / ProductHunt / Reddit
- App Store screenshots become a parallel deliverable (use `aso-appstore-screenshots` skill)
- Watermark is the app icon + name, not a law-firm wordmark

The 8-phase pipeline runs in the same time budget. The preview site looks identical (just with app screenshots instead of editorial photos as backgrounds).
