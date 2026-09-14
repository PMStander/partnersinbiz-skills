---
name: ads-creative
description: "End-to-end ad creative pipeline and creative-quality audits: brand DNA extraction, campaign concepts and copy briefs, AI ad-image generation, product photoshoots, landing page quality assessment, and cross-platform creative fatigue/format-diversity audits. Consolidates ads-create, ads-dna, ads-generate, ads-landing, and ads-photoshoot into the original ads-creative audit skill. Use when user says brand DNA, brand profile, campaign brief, ad concepts, write ad copy, generate ads, create images, make ad creatives, ad creative, product photo, photoshoot, landing page, post-click experience, creative audit, creative fatigue, ad copy, ad design, or creative review."
argument-hint: "dna <url> | create | generate | photoshoot | landing | audit"
license: MIT
---

# Ads Creative: Production Pipeline & Quality Audits

Owns everything about *making and grading* ad creative. This skill covers the
production pipeline (brand DNA → campaign brief → image generation /
photoshoot) as well as standalone quality audits (landing pages,
cross-platform creative fatigue and format diversity). For platform mechanics
(what checks each network runs) use `marketing/ads-platforms`. For strategy,
budget, and full multi-platform audits use `marketing/ads-strategy`.

> **Consolidation note:** This skill absorbs the former `ads-create`,
> `ads-dna`, `ads-generate`, `ads-landing`, and `ads-photoshoot` skills on top
> of its original cross-platform creative-audit content. Those folders remain
> on disk for one release as reference but are no longer loaded by agents;
> treat this file as canonical.

## Quick Reference

| Command | What it does | Pipeline stage |
|---------|-------------|-----------------|
| `/ads-creative dna <url>` | Extract brand DNA → `brand-profile.json` | 1. Brand |
| `/ads-creative create` | Campaign concepts + copy → `campaign-brief.md` | 2. Concept |
| `/ads-creative generate` | AI ad images from brief → `ad-assets/` | 3. Production |
| `/ads-creative photoshoot` | Product photography in 5 styles | 3. Production (standalone) |
| `/ads-creative landing` | Landing page quality assessment | Standalone audit |
| `/ads-creative audit` | Cross-platform creative fatigue/format audit | Standalone audit |

**Production pipeline order** (each step independently runnable):
`/ads-creative dna <url>` → `campaign-brief.md` via `/ads-creative create` →
`/ads-creative generate` (or `/ads-creative photoshoot` for product shots) →
`./ad-assets/` / `./product-photos/`.

Requires `GOOGLE_API_KEY` (Gemini default) or `ADS_IMAGE_PROVIDER` + matching
key for image generation steps (`generate`, `photoshoot`). If missing, those
steps display setup instructions and exit — they never fail silently.

---

## 1. Brand DNA Extraction (`/ads-creative dna <url>`)

Scans a website to extract visual identity, tone of voice, color palette,
typography, and imagery style into `brand-profile.json` for use by `create`,
`generate`, and `photoshoot`.

### Process

1. **Collect URL** (ask if not provided). `--quick` flag = homepage only.
2. **Fetch pages** via WebFetch: homepage → about (`/about`, `/about-us`,
   `/our-story`) → product/services (`/product`, `/products`, `/services`).
   Continue gracefully on 404s, noting lower confidence.
3. **Capture brand screenshots** (skip on `--quick` or capture failure):
   `python ~/.claude/skills/ads/scripts/capture_screenshot.py [url]` for
   homepage, `/products`, and `/about` → `./brand-screenshots/{domain}_*.png`.
   These anchor `/ads-creative generate` image style to the real brand
   aesthetic.
4. **Extract elements**:
   - **Colors**: `og:image` dominant colors, CSS `background-color`/`color`
     on body/header/hero/buttons → primary, secondary, background, text
   - **Typography**: Google Fonts `@import` URLs, CSS `font-family` on
     headings/body
   - **Voice**: score 6 axes (formal_casual, rational_emotional,
     playful_serious, bold_subtle, traditional_innovative,
     expert_accessible) 1-10 from hero/About/CTA copy signals; each axis gets
     a confidence rating (High 3+ signals, Medium 2, Low 1)
   - **Imagery style**: photography vs illustration vs flat design, subjects,
     composition
   - **Forbidden elements**: inferred from positioning (e.g. Enterprise/B2B →
     exclude cheesy stock photos; Healthcare → exclude unqualified medical
     claims; Finance → exclude get-rich-quick imagery)
5. **Build `brand-profile.json`** per the schema below (read
   `ads/references/brand-dna-template.md` for the canonical schema); use
   `null` for fields that can't be confidently extracted — never guess.
6. **Write** to `./brand-profile.json` in the current working directory,
   including a `screenshots` field only for successfully captured pages.
7. **Confirm and summarize** brand name, voice descriptors, primary color,
   typography, target audience, and screenshot count to the user; suggest
   `/ads-creative create` as the next step.

### Limitations

Sparse content (<200 words) → lower confidence; JS-rendered/SPA sites may not
be captured (Playwright not used by default); one profile per URL for
multi-brand enterprises; dark-mode sites need background/text value swap;
CSS-in-JS sites fall back to og:image colors.

### `brand-profile.json` Schema

```json
{
  "schema_version": "1.0",
  "brand_name": "string",
  "website_url": "string",
  "extracted_at": "ISO-8601",
  "voice": {
    "formal_casual": 1, "rational_emotional": 1, "playful_serious": 1,
    "bold_subtle": 1, "traditional_innovative": 1, "expert_accessible": 1,
    "descriptors": ["adjective1", "adjective2", "adjective3"]
  },
  "colors": {
    "primary": "#hexcode or null", "secondary": ["#hex1", "#hex2"],
    "forbidden": ["#hex or color name"], "background": "#hexcode", "text": "#hexcode"
  },
  "typography": {
    "heading_font": "Font Name or null", "body_font": "Font Name or system-ui",
    "pairing_descriptor": "brief description"
  },
  "imagery": {
    "style": "professional photography | illustration | flat design | mixed",
    "subjects": ["subject1", "subject2"], "composition": "brief description",
    "forbidden": ["element1", "element2"]
  },
  "aesthetic": {
    "mood_keywords": ["keyword1", "keyword2", "keyword3"],
    "texture": "minimal | textured | mixed", "negative_space": "generous | moderate | dense"
  },
  "brand_values": ["value1", "value2", "value3"],
  "target_audience": {
    "age_range": "e.g. 25-45", "profession": "brief description",
    "pain_points": ["pain1", "pain2"], "aspirations": ["aspiration1", "aspiration2"]
  }
}
```

---

## 2. Campaign Concepts & Copy Briefs (`/ads-creative create`)

Generates structured campaign concepts and platform-specific copy from
`brand-profile.json` and optional audit results, producing `campaign-brief.md`
for `/ads-creative generate`.

### Process

1. **Brand profile**: look for `brand-profile.json`. If missing, offer to run
   `/ads-creative dna <url>` or collect brand info manually (name, website,
   primary color, 3 voice words, target audience, product/service).
2. **Audit results**: look for `ADS-AUDIT-REPORT.md` or `*-audit-results.md`
   (from `marketing/ads-strategy` audits). If found, note top 3 weaknesses to
   target; if not, generalize concepts and note the gap.
3. **Collect parameters** (skip any already provided via `--platforms` /
   `--objective` flags): platforms, objective (Sales/Leads/Installs/
   Awareness/Retargeting), offer/brief, number of concepts (default 3).
4. **Select copy framework** from `ads/references/copy-frameworks.md` based
   on goal + platform + audience temperature: AIDA (cold/awareness), PAS
   (pain-point), BAB (transformation), 4P (direct response/high-intent), FAB
   (comparison shoppers), Star-Story-Solution (brand storytelling).
5. **Spawn creative agents sequentially** (never parallel — `copy-writer`
   reads the file `creative-strategist` writes, so parallel execution races
   on `campaign-brief.md`):
   - **`creative-strategist`** creates `campaign-brief.md` with `## Brand DNA
     Summary`, `## Campaign Concepts`, `## Image Generation Briefs`, `## Next
     Steps`. For e-commerce, also read
     `ads-plan/assets/ecommerce-creative.md` for the matching playbook
     (Product Launch, Sale/Promotion, Seasonal, Retargeting, Brand
     Awareness). Include banana domain-mode recommendations (Product,
     Editorial, Cinema, UI/Web, Portrait) per Image Generation Brief. Wait
     for full completion.
   - **`copy-writer`** (after strategist completes) appends `## Copy Deck`
     with platform-specific headlines, primary text, and CTAs — 2 framework
     variants per platform (primary + A/B alternative).
6. **Review and present** a summary of concepts/platforms/copy deck/image
   briefs and next steps (review brief → `/ads-creative generate` → upload).

### `campaign-brief.md` Format (parsing contract — headings are exact)

```markdown
# Campaign Brief: [brand_name]
**Generated:** [date]  **Website:** [website_url]  **Platforms:** [list]
**Objective:** [objective]  **Concepts:** [N]

## Brand DNA Summary
[3-sentence synthesis: voice, visual identity, target audience]

## Audit Context
[Top 3 weaknesses being addressed, or "No audit data; run ads-strategy audit"]

## Campaign Concepts

### Concept 1: [Name]
**Hypothesis:** ...  **Primary Message:** ...  **Tone:** ...
**Visual Direction:** ...  **Target Platforms:** ...  **CTA:** ...
**Addresses:** [audit finding or "general brand awareness"]

[repeat per concept]

## Copy Deck
[appended by copy-writer: headlines, primary text, CTAs per concept x platform]

## Image Generation Briefs

### Brief 1: [Concept Name]: [Platform]
**Prompt:** ...  **Dimensions:** WxH  **Safe zone notes:** ... or "None"

[one brief per concept x platform combination]

## Next Steps
1. Review concepts and select which to move forward with
2. Run /ads-creative generate to produce images
3. Adjust CTAs/offers for the specific promotion
4. Upload final assets to ad platform managers
```

### Quality Gates

Minimum 3 concepts (unless fewer requested); distinct angles (no shared
primary-message angle); TikTok concepts must acknowledge vertical-only +
sound-on; if user provided a specific offer, ≥1 concept must lead with it;
every concept needs ≥1 image brief per requested platform. For Meta: favor
diverse concepts (different motivators/styles/angles) — Andromeda suppresses
>60% similarity clusters.

---

## 3. AI Ad Image Generation (`/ads-creative generate`)

Generates platform-sized ad creative images from `campaign-brief.md` and
`brand-profile.json` via banana-claude.

### Setup

Requires banana-claude (v1.4.1+) with nanobanana-mcp (`/banana setup`). If
unavailable, alternatives: OpenAI gpt-image-1 ($0.040/img), Stability SD 3.5
($0.065), Replicate FLUX.1 Pro ($0.055) via `ADS_IMAGE_PROVIDER` env var. If
banana is not installed, display setup instructions and exit — never fail
silently.

### Process

1. **Verify banana-claude**; exit with instructions if missing.
2. **Locate sources**: `campaign-brief.md` (Image Generation Briefs job list)
   + optional `brand-profile.json`. No brief → standalone mode: ask for
   prompt, target platform, output filename.
3. **Read provider config** (`ads/references/image-providers.md`) for
   pricing/limits; show cost estimate.
4. **Read platform specs** per platform in the brief: `ads/references/meta-creative-specs.md`,
   `google-creative-specs.md`, `tiktok-creative-specs.md`,
   `linkedin-creative-specs.md`, `youtube-creative-specs.md`,
   `microsoft-creative-specs.md`.
5. **Prepare banana config**: create/reuse brand preset at
   `~/.banana/presets/{brand-slug}.json`; select domain mode — Product
   (e-commerce/packshots), Editorial (brand awareness/lifestyle), Cinema
   (video thumbnails/dramatic), UI/Web (app install/SaaS), Portrait
   (testimonials/people).
6. **Spawn `visual-designer`** (Task tool, `context: fork`) to parse briefs,
   inject brand colors/mood, generate via banana, save to
   `./ad-assets/[platform]/[concept]/`, write `generation-manifest.json`.
7. **Validate with `format-adapter`** (Task tool, `context: fork`) for
   dimension/spec compliance.
8. **Quality gate**: score each image 1-10 (brand alignment, composition,
   platform fit) via Claude vision. 9-10 professional/ready · 7-8 good, minor
   tweaks possible · 5-6 regenerate once (readability/composition/brand
   mismatch) · <5 reject and regenerate with adjusted prompt.
9. **Aggregate costs** from `~/.banana/costs.json` into the manifest.
10. **Report results**: generated assets list, format validation summary,
    total cost, next steps.

### Standalone Mode Dimensions (no campaign-brief.md)

```
meta-feed → 1080×1350 (4:5)     meta-reels → 1080×1920 (9:16)
tiktok → 1080×1920 (9:16)       google-pmax → 1200×628 (1.91:1)
linkedin → 1080×1080 (1:1)      youtube → 1280×720 (16:9)
youtube-short → 1080×1920 (9:16)
```

Cost transparency: count briefs, show estimated cost, confirm before
proceeding if >$1.00.

---

## 4. Product Photoshoot (`/ads-creative photoshoot`)

Transforms a product image/description into 5 professional ad-ready
photography styles, each at 1:1 (Meta/LinkedIn) and 9:16 (TikTok/Reels/
Stories). Requires banana-claude (v1.4.1+) — see Section 3 setup.

### Process

1. **Collect**: product image path/URL/description, key features, styles
   wanted (default all 5), target platforms (default Meta + TikTok → 1:1 +
   9:16).
2. **Load `brand-profile.json`** if present for style injection (colors,
   mood keywords, target audience, forbidden imagery elements).
3. **Verify banana-claude**.
4. **Construct prompts per style**:

| Style | Focus | Composition | Sizes |
|-------|-------|-------------|-------|
| Studio | Clean e-commerce shot, white seamless bg | Centered / 3/4 angle | 1080×1080, 1080×1920 |
| Floating | Dramatic levitation, gradient bg | Vertically centered | 1080×1080, 1080×1920 |
| Ingredient | Flat lay with components/materials | Top-down, product centered | 1080×1080 (+ 9:16) |
| In Use | Hands using product, natural light | Hands prominent, soft bg (no full face) | 1080×1080, 1080×1920 |
| Lifestyle | Aspirational full-context scene | Environmental, product as hero | 1080×1080, 1080×1920 |

5. **Generate**: banana **Product** mode for Studio/Floating/Ingredient,
   **Editorial** mode for In Use/Lifestyle; 2K resolution; set aspect ratio
   per size via banana MCP `set_aspect_ratio`. Save to
   `./product-photos/[style]/[product-slug]-[style]-[WxH].png`. Retry once
   with simplified prompt on failure.
6. **Report**: image count, per-style output paths, cost
   (`~/.banana/costs.json`), platform recommendations, next step
   (`/ads-creative generate` for full campaign).

### Platform Recommendations

| Style | Best Platforms | Rationale |
|-------|---------------|-----------|
| Studio | Meta Feed, LinkedIn, Google PMax | Universal, clean, safe |
| Floating | Meta Reels, TikTok, Stories | High-impact vertical |
| Ingredient | Meta Feed, Pinterest | Square, tells product story |
| In Use | TikTok, Meta Reels, Stories | Authentic, native-feeling |
| Lifestyle | All platforms | Aspirational, broad appeal |

Cost estimate before generating (styles × 2 sizes); confirm if >$0.50.

---

## 5. Landing Page Quality Assessment (`/ads-creative landing`)

Evaluates the post-click experience for ad campaigns.

### Process

1. Collect landing page URLs from active ad campaigns
2. Read `ads/references/benchmarks.md` (conversion benchmarks) and
   `ads/references/conversion-tracking.md` (pixel/tag verification)
3. Assess each page for ad-specific quality factors
4. Score and identify improvement opportunities prioritized by conversion
   impact

### Health Score

`Score = (Message Match × 0.25) + (Page Speed × 0.25) + (Mobile × 0.20) +
(Trust × 0.15) + (Form × 0.15)`. Grade: A (90-100) → F (<40).

### Message Match (the #1 landing page issue)

| Level | Description | Score |
|-------|-------------|-------|
| Exact match | Headline, offer, CTA all align | 100% |
| Partial match | Headline matches, offer/CTA differs | 60% |
| Weak match | Generic page, loosely related | 30% |
| Mismatch | Page doesn't reflect ad promise | 0% |

### Page Speed (1s delay ≈ 7% CVR drop)

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| LCP | <2.5s | 2.5-4.0s | >4.0s |
| INP | <200ms | 200-500ms | >500ms |
| CLS | <0.1 | 0.1-0.25 | >0.25 |
| Page weight | <2MB | 2-5MB | >5MB |

### Mobile (75%+ of ad clicks)

Tap targets ≥48×48px with ≥8px spacing; body text ≥16px; correct keyboard
types; full-width CTA visible without scroll; no horizontal scroll or
blocking interstitials; clickable `tel:` links.

### Trust Signals & Form Optimization

Above-fold: logo, social proof, security badges, ratings. Below-fold: full
testimonials, case studies, certifications. Form length impact: 1-3 fields
highest CVR (top-of-funnel) down to 9+ fields lowest CVR (only for high-value
offers); use multi-step forms with progress indicators for 5+ fields.

### Consent Banner Impact

Flag banners that cover the primary CTA, delay form interaction >1s, push
critical content below the fold, or can't be dismissed on mobile without
scrolling. Verify Consent Mode V2 for EU/EEA traffic (without it, conversion
modeling degrades and remarketing audiences shrink).

### Quick Wins

| Priority | Fix | Expected Impact |
|----------|-----|-----------------|
| 1 | Move primary CTA above the fold (all devices) | +15-25% CVR |
| 2 | Reduce form fields to essentials | +10-20% CVR |
| 3 | Add trust badges near CTA | +5-15% CVR |
| 4 | Optimize hero image (WebP/AVIF, <200KB) | -1-2s load time |
| 5 | Fix mobile tap targets (≥48×48px, ≥8px spacing) | +5-10% mobile CVR |

### Ad-Specific Elements

UTM parameter capture + click ID preservation (gclid, fbclid, ttclid,
msclkid); dynamic keyword insertion; location-specific content; conversion
event firing verification for thank-you pages, form submissions, calls, and
chat triggers.

### Deliverables

`LANDING-PAGE-REPORT.md`: per-page scores, message-match analysis,
speed/mobile/form priorities, Quick Wins sorted by conversion impact.

---

## 6. Cross-Platform Creative Quality Audit (`/ads-creative audit`)

Detects creative fatigue, evaluates platform-native compliance, and
prioritizes production. This is the original `ads-creative` scope.

### Process

1. Collect creative assets or performance data from active platforms
2. Read `ads/references/platform-specs.md` (specs) and
   `ads/references/benchmarks.md` (CTR/engagement benchmarks)
3. Read `ads/references/scoring-system.md` for weighting
4. **Validate**: confirm at least one platform has creative data before
   proceeding
5. Evaluate creative quality per platform; assess cross-platform consistency
6. **Validate**: fatigue signals must reference actual performance trends,
   not assumptions
7. Generate production priority recommendations

### Per-Platform Assessment (summary — full checks in `marketing/ads-platforms`)

| Platform | Key creative checks |
|----------|---------------------|
| Google | RSA ≥8 headlines/≥3 descriptions, ad strength Good/Excellent, extensions, PMax asset diversity |
| Meta | ≥3 formats, ≥5 creatives/ad set, fatigue >20% CTR drop/14 days = FAIL, UGC tested, Advantage+ Creative |
| LinkedIn | Thought Leader Ads ≥30% B2B budget, ≥2 formats, refresh 4-6 weeks |
| TikTok | ≥6 creatives/ad group [Critical], 9:16 vertical only [Critical], hook 1-2s, safe zone X:40-940 Y:150-1470 |
| Microsoft | RSA ≥8/≥3, Multimedia Ads, Action Extension, Bing-appropriate tone |

### Creative Fatigue Detection

| Signal | Threshold | Action |
|--------|-----------|--------|
| CTR declining | >20% over 14 days | Refresh creative |
| Frequency (Meta) | >5.0 prospecting, >12.0 retargeting | New audience or creative |
| Watch time declining (TikTok) | <3s average | New hook needed |
| QS declining (Google) | Drop of 2+ points | Refresh ad copy |
| Engagement rate drop | >30% decline | Full creative overhaul |

### Refresh Cadence

TikTok 7-10 days (fastest) · Meta 14-21 days · LinkedIn 4-6 weeks · Google
Search 8-12 weeks · Microsoft 8-12 weeks · YouTube 4-8 weeks.

### Format Diversity Matrix

| Format | Google | Meta | LinkedIn | TikTok | Microsoft |
|--------|--------|------|----------|--------|-----------|
| Static Image | RSA image ext | ✅ | ✅ | ❌ | Multimedia |
| Video | YouTube, PMax | ✅ | ✅ | ✅ required | ✅ 9:16 (Apr 2025) |
| Carousel | ❌ | ✅ | ✅ | ❌ | ❌ |
| Collection | ❌ | ✅ | ❌ | ❌ | ❌ |
| Document | ❌ | ❌ | ✅ | ❌ | ❌ |
| Shopping | PMax/Shopping | Catalog | ❌ | Shop | Shopping |

Apple Ads: Static Image ✅ (CPPs), Video ✅ (preview videos), Search Tab ✅
(banner), Today Tab ✅ (editorial-style).

### Andromeda Similarity (Meta) & Symphony Automation (TikTok)

Meta's Andromeda (Oct 2025) suppresses ads with >60% similarity — flag
accounts relying on iterative variations rather than genuinely distinct
concepts. TikTok's Symphony AI (2025) generates variations from product URLs
— assess AI-generated vs original quality and refresh-cadence impact.

### Creative Health Scoring Weights

Format Diversity 25% · Fatigue Signals 25% · Platform Compliance 20% ·
Refresh Cadence 15% · Volume 15%. Grade A (90-100) → F (<40).

### Creative Check IDs

| ID | Check | Severity |
|----|-------|----------|
| CR-01 | Format diversity ≥3 formats/platform | High |
| CR-02 | Creative volume meets platform minimums | High |
| CR-03 | Fatigue detection (CTR/engagement decline) | Critical |
| CR-04 | Refresh cadence within recommended cycle | High |
| CR-05 | Platform compliance (specs, safe zones, text limits) | Critical |
| CR-06 | Hook quality (first 1-5s video / headline impact static) | High |
| CR-07 | UGC ratio tested (Meta, TikTok) | Medium |
| CR-08 | Video specs (codec, resolution, aspect ratio) | Medium |
| CR-09 | Safe zone compliance (900×1000px usable area) | Medium |
| CR-10 | Andromeda diversity: genuinely distinct concepts (Meta) | High |

### Universal Creative Best Practices

Cross-platform safe zone: 900×1000px usable area, test on mobile (75%+ of
impressions). Ad copy: lead with benefit, clear CTA, message match to landing
page, numbers over vague claims. Video: H.264/AAC/MP4, ≥720p (1080p
preferred), captions always, brand mention within first 5s.

### Deliverables

`CREATIVE-AUDIT-REPORT.md`: per-platform creative assessment, fatigue alerts,
format diversity gaps, production priority list, Quick Wins.

---

## Reference Files

Paths are relative to `marketing/` (siblings of this skill).

- `ads/references/brand-dna-template.md` — brand profile schema
- `ads/references/image-providers.md` — provider config, pricing, limits
- `ads/references/copy-frameworks.md` — 6 ad copy frameworks (AIDA, PAS, BAB, 4P, FAB, Star-Story-Solution)
- `ads/references/voice-to-style.md` — brand voice axis → visual attribute mapping
- `ads/references/meta-creative-specs.md`, `google-creative-specs.md`,
  `tiktok-creative-specs.md`, `linkedin-creative-specs.md`,
  `youtube-creative-specs.md`, `microsoft-creative-specs.md` — per-platform
  creative specs
- `ads/references/platform-specs.md` — cross-platform creative spec summary
- `ads/references/benchmarks.md`, `ads/references/scoring-system.md` —
  benchmarks and scoring weights
- `ads/references/conversion-tracking.md` — pixel/tag verification for
  landing page audits
- `ads-plan/assets/ecommerce-creative.md` — e-commerce creative playbooks
