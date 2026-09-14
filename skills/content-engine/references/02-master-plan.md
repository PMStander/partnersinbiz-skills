# Phase 2 — Master Plan

The master plan is the bridge between research and production. Without it, the parallel writers in Phase 3 will produce inconsistent work because they have no shared visual identity, tone, or calendar.

## Inputs needed

- The research brief from Phase 1
- The client's existing site URL (for brand identity extraction)
- Optionally: the client's existing logos, fonts, or brand guidelines

## Step 1 — Lock the brand identity

If the client has a website, extract the identity from source. Don't ask the user — go grep.

```bash
# Extract color hex codes
grep -rh "color:\|#[0-9a-fA-F]\{6\}\|background" "<client-website>/src" 2>/dev/null \
  | grep -oE "#[0-9a-fA-F]{6}" | sort -u

# Extract fonts
grep -rh "font-family\|fontFamily" "<client-website>/src" 2>/dev/null \
  | grep -oE "'[A-Z][a-zA-Z ]+'" | sort -u
```

If no site exists, ask 4 questions:
1. Light or dark canvas?
2. Primary accent color (or brand mood — "warm", "technical", "luxury")?
3. Heading font preference (or "default to Raleway / Inter / Playfair")?
4. Mood (premium, playful, technical, warm, restrained)?

Lock these into a table at the top of the master plan:

| Element | Spec |
|---|---|
| Primary background | `#0a0a0a` (with layered tones for depth) |
| Primary accent | `#c9a25a` |
| Secondary accent | `#d2ae6d` |
| Alert (rare use) | `#e07070` |
| Text | `#ffffff` |
| Heading font | Raleway 600/700/800 |
| Body font | Open Sans / Lato 400 |
| Aesthetic keywords | Premium, restrained, gold-on-black, no clichés |

## Step 2 — Define content pillars

Pull the pillars from the research brief. There are usually 5–7 — fewer than 5 means you missed coverage; more than 8 means you're fragmenting attention.

Each pillar gets:
- An emoji or simple icon for visual identification
- A "rank" tag (e.g. "most-searched", "highest emotional engagement", "direct revenue")
- A posting cadence (weekly / bi-weekly / monthly)

## Step 3 — Build the 12-week calendar

The cadence that works:
- **Monday** — long-form blog post (1,200–1,800 words)
- **Wednesday** — short-form video (Reel / Short, 30–35s)
- **Friday** — static social post (square, gold-on-black with on-image text)

Map each week to a pillar + a specific content piece. Use the format:

| Week | Mon (Blog) | Wed (Video) | Fri (Social) |
|---|---|---|---|
| 1 | B1 PIE Act | V1 Landlord Can't | W01 Quote |
| 2 | B2 Labour Bill | V4 R22,466.74 | W02 Stat |
| … | … | … | … |

The pattern: pull the most-searched topics first. The Week 1 blog should be the single most-searched topic in your research. The Week 1 video should be the catchiest myth-buster you found.

## Step 4 — Define the three social formats

Almost every social post will fit one of three templates:

1. **Quote Card** — pull-quote from a blog post, big text on dark background
2. **Stat Card** — single big number + one line of context
3. **Myth vs Fact** — split-panel design, red MYTH / gold FACT labels

In the master plan, define the visual specs (font sizes, colors, on-image text format) so the social post writers in Phase 3 produce consistent designs.

## Step 5 — Write the caption templates

Three caption templates per platform, used by the social-post writer agent:

**LinkedIn template** (long-form, professional, sources cited):
```
[Hook — one sentence naming the misconception]

[2-3 paragraphs of plain-language explanation]

The law: [Act and section reference]

If you're dealing with [topic], you have options.

Read the full breakdown: [URL]

#[Industry] #[Pillar] #[Brand]
```

**Instagram template** (short, punchy, save-worthy):
```
[Hook punchline]

[Bullet 1]
[Bullet 2]
[Bullet 3]

Save this. Share with someone who needs it.

#[10–15 hashtags]
```

**Facebook template** (conversational, community tone):
```
[Conversational opening]

[Story / scenario]

Here's what the law actually says: [plain answer]

Questions? Drop them below or DM us.
```

## Step 6 — Reference link library

Compile a library of authoritative sources organised by pillar. Every blog post will pull 3–5 references from this library. This is a single time investment that pays off across all 8 blogs.

## Output

Save to `<workspace>/marketing/plans/content-master-plan.md`. Aim for 2,500–4,000 words. Include:

1. Brand foundation (palette + type + tone do/don't table)
2. Content pillars (all 7 with cadence)
3. Asset plan (8 blog topics with hero image briefs, 6 video storyboards, 12 social post topics)
4. 12-week calendar (full grid)
5. Three social format specs
6. Caption templates per platform
7. Reference link library by pillar
8. Distribution channels + watermark rules

The AHS Law master plan at `/Users/peetstander/Cowork/partners/AHS Law/marketing/plans/content-master-plan.md` is canonical.

## Time budget

Phase 2 should take **45–60 minutes**. The brand-extraction grep is fast; the calendar is fast; the templates take time but you only do them once.
