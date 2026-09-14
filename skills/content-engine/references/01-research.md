# Phase 1 — Research

The research phase grounds the entire content engine in what the public is actually searching for and what's actually changing in the client's industry. Without it, you'll produce generic content that doesn't rank and doesn't address real pain.

## Inputs needed

- The client's industry/domain (e.g., "South African law", "small-business accounting in Australia", "B2B SaaS marketing for HR tech")
- The client's geography (matters for legal/regulatory content; less so for pure B2B)
- Optional: the client's existing site URL (to extract brand identity in Phase 2)

## Two-pronged approach

### Prong 1 — Use the `last30days` skill

If available, invoke `last30days` for the client's domain. This pulls Reddit, X/Twitter, YouTube, TikTok, and HN data on what people are discussing right now. Save the raw output to `~/Documents/Last30Days/` (the skill does this automatically with `--save-dir`).

The X auth often fails (HTTP 400) — don't worry about it. Reddit and WebSearch alone are enough.

Provide a focused topic, e.g.:
> "South African law - what people are searching, asking, and discussing online right now"

### Prong 2 — Deep WebSearch sweep

Dispatch a single subagent that runs 6–8 parallel WebSearches across the client's pillars. For a law firm, those pillars are labour, eviction, criminal, family, debt, privacy, conveyancing. For a small-business accountant, swap in cash flow, tax, BAS, payroll, software choice, structures.

The subagent prompt should look like this (skeleton — adapt the queries):

```
Do 6–8 parallel WebSearches and return FULL results (titles, URLs, snippets) for each:

1. WebSearch("most common [domain] questions [audience] ask 2025 2026")
2. WebSearch("[country] [pillar 1] changes 2026")
3. WebSearch("[country] [pillar 2] [audience] rights 2026")
… (one per pillar)

Return as much detail as possible — I'm building a research briefing.
```

Run it via `Agent` tool with the `Explore` subagent type if available (it's read-only, fast).

## Output format

Save to `<workspace>/research/<domain>-public-questions-<year>.md`. Structure the file as:

1. **Why this document exists** — one paragraph: what the client will use it for
2. **The most-searched topics** — ranked list (highest engagement first)
3. **One section per content pillar** — each section contains:
   - "What people are actually asking" (10+ verbatim questions)
   - "The latest changes" (timeline of regulatory/industry updates)
   - "Common misconceptions" (3+ myths to bust — these become high-engagement content)
   - "Action steps" (what the audience should do)
4. **Trending issues — watch list for 2026** (anticipates the next 6–12 months of search volume)
5. **Content strategy recommendations** — distill the research into 8 blog topics + social angles
6. **Sources & methodology** — every publication consulted, every Act/document cited

The AHS Law brief at `/Users/peetstander/Cowork/partners/AHS Law/research/sa-law-public-questions-2026.md` is the canonical template — match its structure.

## Length

Aim for **5,000–8,000 words**. Less than 5k means you missed pillars. More than 8k usually means you're padding with generic explanation instead of specific evidence.

## Time budget

Phase 1 should take **45–75 minutes**. If it's taking longer, dispatch more parallel WebSearches instead of doing them serially.
