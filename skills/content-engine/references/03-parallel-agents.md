# Phase 3 — Parallel Writing Wave

This is where the bulk of the production happens, and where you save the most time. You dispatch ~15 subagents in 1–2 waves and they work in parallel for ~10 minutes wall-clock to produce all the writing.

## What gets dispatched

| Agents | What they produce | Time per agent |
|---|---|---|
| 8 blog writers (B1–B8) | One markdown blog post each, 1,200–1,800 words | 1.5 min |
| 6 video composers (V1–V6) | One HyperFrames composition each (HTML + script + README) | 1.5 min |
| 1 social-post writer | All 12 weeks of social posts (W01–W12) with 3 captions per week | 4 min |

Total: ~15 agents, 10 min wall-clock, no idle time on your end.

## How to dispatch (key pattern)

Use the `Agent` tool with `general-purpose` subagent type. Send all 8 blog writers in a SINGLE message with multiple tool calls so they run concurrently. Then a second message with the 6 video composers + the social-post writer.

```
Wave 1: 8 parallel Agent() calls — all blog writers
Wave 2: 7 parallel Agent() calls — 6 video composers + 1 social-post writer
```

If you put 15 in one message it sometimes overwhelms the orchestration. 8 + 7 is reliable.

## Agent prompt pattern

Every parallel agent gets a tight, self-contained brief. They have **no shared context** with you — assume zero memory.

### Blog writer prompt skeleton

```
You are [agent-name], the legal-content writer for [client]. Write blog post B[N].

**Read these first** (mandatory):
- <workspace>/research/<domain>-public-questions-<year>.md (Section [N]: [pillar])
- <workspace>/marketing/plans/content-master-plan.md (Section 3.1, blog template + Section 6 references)

**Task:** Write a [word-count]-word blog post titled **"[Title]"**.

**Audience:** [who reads this — "South African tenants and small landlords", "small-business owners in Australia"]. Plain English, Grade-8 reading level. [Empathetic / authoritative / etc.]

**Required structure:**
1. Hook (single sentence naming the misconception)
2. The myth (what most people believe)
3. The law — cite [Act/regulation] and [Section]
4. What you can do (numbered list)
5. What the [opposing party] cannot do (protections)
6. What to do if it goes wrong (clear next action)
7. Sources & further reading (3–5 links from the master plan reference library)
8. CTA — "Need help with [topic]? Contact [client] for a confidential consultation." Link to [client URL]/#contact

**Brand voice:** [from master plan tone table]

**Frontmatter:** YAML with title, slug, pillar, hero_image ("../images/blog/B[N]-[slug].png"), word_count, published date, references, hero_image_prompt (the exact Imagen prompt from prompts.md for B[N]).

**Output path:** <workspace>/marketing/blog-posts/B[N]-[slug].md

When done, return: word count, output path, and 1-line summary. Do NOT return the full text.
```

The "do NOT return the full text" is critical — you want the agent to write the file, not flood your context with the body.

### Video composer prompt skeleton

```
You are a HyperFrames video composer for [client]. Build video V[N].

**Read these first** (mandatory):
- /Users/peetstander/.claude/skills/media/hyperframes/SKILL.md (the framework)
- <workspace>/marketing/videos/DESIGN.md (locked visual identity)
- <workspace>/marketing/plans/content-master-plan.md (Section 5 — V[N] storyboard)
- <workspace>/research/<domain>-*.md (Section [N] for content)

**Task:** Build the HyperFrames composition for V[N]: **"[Title]"**

**Specs:**
- 1080x1920 vertical, ~[duration]s
- Brand palette ONLY: bg [hex], gold [hex], alert [hex], white text
- [Heading font] for headlines, [body font] for body, [numeric font] 800 for numbers
- Motion: power2.out / power3.inOut only
- 1.2 second minimum scene hold
- Watermark "[BRAND]" gold bottom-right every scene
- End card per DESIGN.md spec

**Content sequence:**
1. Hook (0–2s): [hook description]
2. Scene 2 (2–9s): [content]
…
N. End card (X–Y): [brand wordmark] + tagline + URL

**Create:**
1. <workspace>/marketing/videos/V[N]-[slug]/index.html (HyperFrames composition with GSAP timeline)
2. <workspace>/marketing/videos/V[N]-[slug]/script.md (narration script under 100 words)
3. <workspace>/marketing/videos/V[N]-[slug]/README.md (render instructions)

**Important HyperFrames rules:**
- Use index.html (NOT composition.html — framework expects index.html)
- Each scene needs class="scene clip" (the clip class enables timing-based visibility)
- Root composition <div data-composition-id="vN-root"> needs data-start="0" and data-duration="N"
- Layout end-state first then animate FROM offscreen with gsap.from()

When done, return ONLY: paths created and 1-line description. Do NOT return the HTML.
```

### Social-post writer prompt skeleton

The single agent that writes all 12 weeks. Give it the full 12-week plan and let it produce one .md file per week:

```
You are a social media strategist for [client].

**Read these first**:
- <workspace>/marketing/plans/content-master-plan.md (Section 3.3 social posts + Section 7 calendar + Section 8 caption templates)
- <workspace>/research/<domain>-*.md (for source content)

**Task:** Produce all 12 weekly social posts. Each post = ONE markdown file containing:
1. YAML frontmatter (week, format, image_prompt, hashtags, channels)
2. The image prompt for Gemini/xAI
3. The on-image text (what would be displayed on the visual itself)
4. A LinkedIn caption (long-form, 150–250 words, professional, with sources, max 5 hashtags)
5. An Instagram caption (visual-first, short, punchy, save-worthy, up to 15 hashtags)
6. A Facebook caption (community tone, conversational)

**The 12 posts (from the master plan calendar):**
- W1: [topic + format]
- W2: [topic + format]
… (paste full list)

**Output:** Save each as `<workspace>/marketing/social-media/W[NN]-[slug].md`

**Important — H2 headers must be exact.** The preview-site builder pulls captions by H2 name. Use `## LinkedIn Caption`, `## Instagram Caption`, `## Facebook Caption` (or the bare `## LinkedIn` / `## Instagram` / `## Facebook` — both forms are accepted). Any other heading (e.g. `## LinkedIn Post`, `### LinkedIn`) will leave the caption blank in the preview.

When done, return: list of all 12 files created, and one summary line.
```

## Why dispatch in parallel and not sequentially

Sequential = 15 agents × 1.5 min = 22 min minimum, plus your overhead reading each output and queuing the next. Parallel = 10 min wall-clock with no overhead. The 12x speedup compounds across the day.

## Picking topics from research

The research brief has 7 pillars. The 8 blog topics should:
- Hit each pillar at least once
- Lead with the **most-searched** topic (highest volume)
- Include at least one **myth-buster** (high engagement, high shareability)
- Include at least one **direct-revenue** topic (a topic that maps to a service the client sells)

For a law firm, that mix looks like:
- Highest-search: blog on the new earnings threshold OR the Labour Bill
- Myth-buster: "you cannot be arrested for debt"
- Direct-revenue: conveyancing
- Pillar coverage: one each from labour, eviction, criminal, family, debt, privacy, property

For a small-business accountant, it might look like:
- Highest-search: BAS deadlines + the new tax thresholds
- Myth-buster: "the ATO can't take your house" (or whatever the prevailing fear is)
- Direct-revenue: structuring, business sales
- Pillar coverage: cash flow, tax, BAS, payroll, software, structures, sale-prep

## Handling agent output

Each agent returns a 1–3 line summary. Don't let them dump full text into your context — you'll burn tokens fast. The sum of 15 1-line returns is ~200 lines, manageable.

Verify the file actually exists:
```bash
ls -la <workspace>/marketing/blog-posts/ | wc -l    # should be 9 (8 + .)
ls -la <workspace>/marketing/videos/V*/index.html | wc -l   # should be 6
ls -la <workspace>/marketing/social-media/W*.md | wc -l   # should be 12
```

If any are missing, retry just that one.

## Time budget

Phase 3 should take **15–20 minutes** total (10 min agent wall-clock + 5–10 min for you to verify outputs and write replacement briefs if any failed).
