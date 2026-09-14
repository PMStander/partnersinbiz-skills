---
name: ads-platforms
description: "Multi-platform paid ads deep analysis: Google (Search/PMax/Display/YouTube/Demand Gen), Meta (Facebook/Instagram/Advantage+), LinkedIn (B2B/ABM/Thought Leader Ads), Microsoft/Bing (Copilot/Import), TikTok (Creative/Shop/Smart+), YouTube (Shorts/CTV/Demand Gen), and Apple Ads (Search/CPP/AdAttributionKit). Consolidates ads-google, ads-meta, ads-linkedin, ads-microsoft, ads-tiktok, ads-youtube, and ads-apple. Use when user says Google Ads, Google PPC, search ads, PMax, Meta Ads, Facebook Ads, Instagram Ads, Advantage+, LinkedIn Ads, B2B ads, sponsored content, Microsoft Ads, Bing Ads, Copilot ads, TikTok Ads, TikTok Shop, Smart+, YouTube Ads, video ads, Shorts, CTV, Apple Ads, Apple Search Ads, or App Store ads."
argument-hint: "google | meta | linkedin | microsoft | tiktok | youtube | apple"
license: MIT
---

# Ads Platforms: Per-Platform Deep Analysis

Deep, single-platform paid-advertising audits. This skill owns *platform
mechanics* (what checks to run, what "good" looks like per platform, and
platform-specific features/limits). For cross-platform strategy (planning,
budget, math, full audits, competitor intel, A/B tests) use
`marketing/ads-strategy`. For creative production and creative-fatigue audits
use `marketing/ads-creative`. For live campaign CRUD against the Partners in
Biz platform API use `ads-manager`.

> **Consolidation note:** This skill replaces the standalone `ads-google`,
> `ads-meta`, `ads-linkedin`, `ads-microsoft`, `ads-tiktok`, `ads-youtube`,
> and `ads-apple` skills. Those folders remain on disk for one release as
> reference but are no longer loaded by agents; treat this file as canonical.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/ads-platforms google` | Google Ads deep analysis (Search, PMax, YouTube, Demand Gen) — 80 checks |
| `/ads-platforms meta` | Meta Ads deep analysis (FB, IG, Advantage+) — 50 checks |
| `/ads-platforms linkedin` | LinkedIn Ads deep analysis (B2B, Lead Gen, ABM) — 27 checks |
| `/ads-platforms microsoft` | Microsoft/Bing Ads deep analysis (Copilot, Import) — 24 checks |
| `/ads-platforms tiktok` | TikTok Ads deep analysis (Creative, Shop, Smart+) — 28 checks |
| `/ads-platforms youtube` | YouTube Ads analysis (Skippable/Bumper/Shorts/Demand Gen/CTV) |
| `/ads-platforms apple` | Apple Ads deep analysis (CPP, MMP, Maximize Conversions) |

## Shared Process (applies to every platform below)

1. Collect the platform's account data (export, screenshots, or pasted metrics)
2. Read the platform's audit reference under `ads/references/` (see table below)
3. Read `ads/references/benchmarks.md` for platform-specific benchmarks and
   `ads/references/scoring-system.md` for the weighted scoring algorithm
4. Evaluate all applicable checks as PASS, WARNING, or FAIL
5. Calculate the platform's Health Score (0-100) and letter grade (A 90-100,
   B 75-89, C 60-74, D 40-59, F <40)
6. Generate a findings report with a prioritized action plan

| Platform | Audit checklist reference | Check count |
|----------|---------------------------|-------------|
| Google | `ads/references/google-audit.md` | 80 |
| Meta | `ads/references/meta-audit.md` | 50 |
| LinkedIn | `ads/references/linkedin-audit.md` | 27 |
| Microsoft | `ads/references/microsoft-audit.md` | 24 |
| TikTok | `ads/references/tiktok-audit.md` | 28 |

---

## 1. Google Ads (`/ads-platforms google`)

Covers Search, Performance Max, Display, YouTube, and Demand Gen.

### Category Weights

| Category | Weight | Key checks |
|----------|--------|------------|
| Conversion Tracking | 25% | gtag.js firing, Enhanced Conversions, Consent Mode v2, offline import, server-side GTM, data-driven attribution |
| Wasted Spend | 20% | Search Terms review (≥30 days), negative keyword coverage, Broad Match only with Smart Bidding, invalid click rate <10% |
| Account Structure | 15% | Ad groups themed tightly (15-20 kw max), RSA ad groups ≥3 active ads, PMax asset groups/signals structured |
| Keywords | 15% | Match type progression, Quality Score ≥7 avg, cannibalization check |
| Ads | 15% | RSA ≥8 headlines/≥3 descriptions, ad strength Good/Excellent, extensions (sitelinks ≥4, callouts ≥4) |
| Settings | 10% | ECPC deprecated → full Smart Bidding, budget pacing, location targeting "Presence" |

**Negative keyword rules**: source from actual Search Terms Report (never
guess), default Exact/Phrase match (never Broad negatives without
justification), group into themed lists (Informational, Job-seeker,
Competitor, Free-intent), recommend Shared Negative Lists at account level.

**GAQL & data accuracy** (see `ads/references/gaql-notes.md`): dedupe
keywords by `(ad_group_id + keyword_text + match_type)`; only analyze ENABLED
campaigns/ad groups; filter to keywords with impressions >0 for theme
coherence; legacy BMM heuristic = BROAD + Manual CPC; only flag wasted spend
on terms >$10 spend AND 0 conversions; count shared + campaign-level
negatives together.

**PMax deep dive**: asset group diversity, audience signals, URL expansion
opt-outs, brand exclusions (now available to all advertisers), campaign-level
negatives (now available to all advertisers), search themes, insights tab.

**AI Max for Search (2026)**: layers broad match + keywordless targeting on
Search campaigns; 14% avg conversion lift; requires strong negative lists;
DSA likely consolidated into AI Max Q2 2026.

**Demand Gen** (replaced Video Action Campaigns, April 2026): video + image
mix drives 20% more conversions; frequency capping NOT supported.

**Google Ads MCP (optional)**: connect the
[Google Ads MCP server](https://github.com/googleads/google-ads-mcp) for
automated GAQL pulls (`search`, `list_accessible_customers`); fall back to
manual export if unavailable.

### Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| Quality Score (avg) | ≥7 | 5-6 | <5 |
| CTR (Search) | ≥6.66% | 3-6.66% | <3% |
| CVR (Search) | ≥7.52% | 3-7.52% | <3% |
| CPC (Search) | ≤$5.26 | $5.26-8.00 | >$8.00 |
| Wasted Spend | <10% | 10-20% | >20% |
| Invalid Clicks | <5% | 5-10% | >10% |

### Deliverables

`GOOGLE-ADS-REPORT.md` (80-check findings), wasted-spend estimate ($/mo),
Quick Wins, PMax recommendations, keyword health matrix.

---

## 2. Meta Ads (`/ads-platforms meta`)

Covers Facebook and Instagram; includes Advantage+ assessment.

**Andromeda AI engine** (Oct 2025): filters ads with 10,000x more complex
models. Creative diversity is the #1 lever — ads with >60% Similarity Score
get retrieval suppression. 100 minor variations perform no better than 10
genuinely distinct concepts (cross-reference `marketing/ads-creative`).

### Category Weights

| Category | Weight | Key checks |
|----------|--------|------------|
| Pixel/CAPI Health | 30% | Pixel firing, CAPI active (30-40% data loss without it post-iOS 14.5), dedup ≥90%, EMQ ≥8.0 for Purchase, AEM configured, domain verified |
| Creative | 30% | ≥3 formats active, ≥5 creatives/ad set, fatigue detection (CTR drop >20%/14 days = FAIL), UGC tested, DCO tested |
| Account Structure | 20% | CBO vs ABO intentional, 1-3 campaigns total, Learning Limited <30%, budget ≥5x target CPA/ad set |
| Audience & Targeting | 20% | Prospecting freq <3.0, retargeting freq <8.0, Custom/Lookalike/Advantage+ audiences tested |

**EMQ optimization**: 8.0-10.0 Excellent (maintain) → 6.0-7.9 Good (add
customer_information params) → 4.0-5.9 Fair (implement CAPI) → <4.0 Poor
(CAPI + Enhanced Matching critical). Key params: `em`, `ph`, `fn`/`ln`,
`ct`/`st`/`zp`, `external_id`.

**Advantage+ assessment**: catalog connected + existing-customer cap
(Sales), performance vs manual (Audience), enhancements enabled (Creative),
placement mix (Placements), fair test budget.

**Special Ad Categories**: verify declaration + targeting restrictions (no
ZIP, age 18-65+ only, no Lookalike) for housing/employment/credit ads — see
`ads/references/compliance.md`.

**Threads placement** (GA Jan 2026, 400M+ MAU): lower CPMs, currently ~0.04%
of spend, early-mover opportunity — check if enabled in Advantage+ Placements.

### Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| EMQ (Purchase) | ≥8.0 | 6.0-7.9 | <6.0 |
| Dedup rate | ≥90% | 70-90% | <70% |
| CTR | ≥1.0% | 0.5-1.0% | <0.5% |
| Creatives per ad set | ≥5 | 3-4 | <3 |
| Learning Limited | <30% | 30-50% | >50% |

### Deliverables

`META-ADS-REPORT.md` (50-check findings), EMQ improvement roadmap, creative
fatigue alerts, Advantage+ adoption recommendations.

---

## 3. LinkedIn Ads (`/ads-platforms linkedin`)

B2B advertising. **Terminology (Oct 2025)**: Campaign Groups are now
"Campaigns"; Campaigns are now "Ad Sets".

### Category Weights

| Category | Weight | Key checks |
|----------|--------|------------|
| Technical Setup | 25% | Insight Tag firing, CAPI active (2025), full-funnel conversion events, CRM integration (Jun 2025) |
| Audience Targeting | 25% | Specific job titles (not just functions), Matched Audiences, ABM lists (up to 300K companies), Predictive Audiences (replaced Lookalikes Feb 2024) |
| Creative Quality | 20% | Thought Leader Ads ≥30% budget for B2B, ≥2 formats tested, refresh every 4-6 weeks |
| Lead Gen & Performance | 15% | Lead Gen Form ≤5 fields (13% CVR benchmark), synced to CRM real-time |
| Bidding & Budget | 15% | Start Manual CPC (Maximum Delivery = most expensive), daily budget ≥$50 Sponsored Content |

**Thought Leader Ads (TLA)**: employee/non-employee (since Mar 2025)
personal-post sponsorship; CPC $2.29-$4.14 vs $13.23 standard; 2-5x higher
engagement. Evaluate adoption, ≥30% budget share, right employees selected,
authentic content.

**LinkedIn Audience Network**: expert consensus is OFF (poor quality, dilutes
data) unless isolated-budget testing.

**ABM strategy** (B2B Enterprise): tiered company lists, per-tier content,
account penetration tracking, CRM/ABM platform integration.

**EU note**: Sponsored Messaging (InMail/Conversation Ads) discontinued since
Jan 2022.

### Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| CTR (Sponsored Content) | ≥0.44% | 0.30-0.44% | <0.30% |
| CPC (average) | ≤$7.00 | $7-10 | >$10.00 |
| Lead Gen CVR | ≥10% | 5-10% | <5% |
| TLA budget share | ≥30% | 15-30% | <15% |

### Deliverables

`LINKEDIN-ADS-REPORT.md` (27-check findings), TLA adoption roadmap, ABM
recommendations, Lead Gen Form priorities.

---

## 4. Microsoft/Bing Ads (`/ads-platforms microsoft`)

Covers Search, PMax, Audience Network, Copilot integration.

### Category Weights

| Category | Weight | Key checks |
|----------|--------|------------|
| Technical Setup | 25% | UET tag firing, enhanced conversions, Google Ads import validated (URLs, extensions, bids, goals) |
| Syndication & Bidding | 20% | Search partner network reviewed, bid targets 20-35% lower than Google, PMax Target New Customers (Beta 2026) |
| Campaign Structure | 20% | Mirrors Google or best practices, budget 20-30% of Google volume, LinkedIn profile targeting for B2B |
| Creative & Extensions | 20% | RSA ≥8 headlines/≥3 descriptions, Multimedia Ads, Action Extension, Filter Link Extension |
| Settings & Performance | 15% | Copilot chat placement enabled (73% CTR lift), CPC 20-40% lower than Google |

**Google import validation**: URLs, extensions, bid amounts (should be
20-35% lower, never import as-is), conversion goals (recreate natively),
audiences, negative keywords all need manual review post-import. Deactivate
scheduled imports after initial setup (they can re-enable paused campaigns).

**Copilot integration**: Copilot Chat Ads in PMax (73% CTR lift), Copilot
Checkout (Jan 2026), Copilot ads shown beneath AI responses with Sponsored
labels.

**Microsoft-unique features**: CTV Ads (Netflix/Max/Hulu/Roku), Multimedia
Ads, Action/Filter Link Extensions, LinkedIn Profile Targeting (High priority
for B2B), auto-generated RSA (default Jan 2026), 9:16 vertical video (Apr
2025, 90s max).

**Bing demographic context**: older, higher-income, desktop-heavy, enterprise
users — favor professional tone and desktop-optimized landing pages.

### Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| CTR (Search) | ≥2.83% | 1.5-2.83% | <1.5% |
| CPC (Search) | ≤$1.55 | $1.55-2.50 | >$2.50 |
| CPC vs Google | 20-40% lower | 10-20% lower | Same or higher |
| Impression share (brand) | ≥80% | 60-80% | <60% |

### Deliverables

`MICROSOFT-ADS-REPORT.md` (24-check findings), Google import validation,
Copilot readiness, cost-advantage analysis, unique-feature checklist.

---

## 5. TikTok Ads (`/ads-platforms tiktok`)

Creative-first platform — success depends primarily on creative quality more
than targeting/bidding.

### Category Weights

| Category | Weight | Key checks |
|----------|--------|------------|
| Creative Quality | 30% | ≥6 creatives/ad group [Critical], all video 9:16 1080x1920 [Critical], hook in 1-2s, Spark Ads tested, safe zone compliance |
| Technical Setup | 25% | Pixel firing, Events API + ttclid passback, advanced matching |
| Bidding & Budget | 20% | Daily budget ≥50x target CPA/ad group, learning phase ≥50 conv/7 days, no mid-learning edits |
| Structure & Settings | 15% | Separate prospecting/retargeting, Smart+ tested, Search Ads Toggle enabled |
| Performance | 10% | CTR ≥1.0%, 3x Kill Rule applies, watch time ≥6s |

**Creative-first strategy**: native feel (not polished), sound-on always
(93% consume with sound), hook in 1-2s, trend alignment, UGC outperforms
studio, vertical only (9:16 non-negotiable). Testing framework: 3-5 hooks per
concept, rotate every 5-7 days, kill at CTR <0.5% after 3 days, scale by
duplicating (not budget-only).

**Safe zone**: X:40-940px, Y:150-1470px (900×1320px usable area).

**TikTok Shop**: catalog connected, complete PDPs, Video Shopping Ads, Shop
tab configured, affiliate program; Shop CVR benchmark >10%. **GMV Max**
mandatory for all Shop Ads since July 2025.

**Smart+ campaigns**: 42% adoption, avg ROAS 1.41-1.67; modular control
(2025) locks targeting/creative/budget/placement independently.

**Symphony automation**: AI-generated creative variations from product URLs —
evaluate quality vs manual and impact on refresh cadence.

### Key Thresholds

| Metric | Pass | Warning | Fail |
|--------|------|---------|------|
| CTR (in-feed) | ≥1.0% | 0.5-1.0% | <0.5% |
| Creatives per ad group | ≥6 | 3-5 | <3 |
| Video watch time | ≥6s | 3-6s | <3s |
| Daily budget | ≥50x CPA | 20-49x CPA | <20x CPA |

### Deliverables

`TIKTOK-ADS-REPORT.md` (28-check findings), creative scorecard, Smart+ vs
manual comparison, TikTok Shop readiness (e-commerce).

---

## 6. YouTube Ads (`/ads-platforms youtube`)

Video ad formats: Skippable In-Stream, Non-Skippable, Bumper, Shorts, Demand
Gen, Connected TV.

### Campaign Types

| Format | Length | Bidding | Notes |
|--------|--------|---------|-------|
| Skippable In-Stream (TrueView) | 12s min, 15-30s rec | Target CPV/CPA | Skip rate 65-80% normal; view rate ≥15% good |
| Non-Skippable | up to 60s (expanded 2025) | Target CPM | Brand awareness/reach |
| Bumper | exactly 6s | Target CPM | Reach extension, single message |
| Shorts | ≤60s, 9:16, sound-on | — | Music/VO boosts conversions >20%; CTA at 3s (PMax/App/Demand Gen) or 10s (Video View/Reach) |
| Demand Gen | (replaced VAC, Apr 2026) | — | Video+image mix = 20% more conversions at same CPA; **no frequency capping** |
| Connected TV | 30s non-skippable exclusive | — | 75% of YouTube spend now on CTV; **Floodlight does not measure CTV** — use GA4/Google Ads conversion tracking |

Flag any remaining VAC campaigns as deprecated (all auto-upgraded to Demand
Gen by April 2026).

### Creative Quality

Hook analysis (first 5s): brand mention early, problem/benefit upfront, no
slow intros. ABCD framework (Attention → Branding → Connection → Direction)
delivers 30% lift in short-term sales likelihood. Production: HD minimum,
captions present, end screen CTA. Volume: ≥3 variations, vertical + horizontal
versions, refresh every 4-8 weeks.

### Audience Targeting

Custom Intent, In-Market, Affinity, Customer Match, Similar Audiences,
Placement Targeting. Separate prospecting vs retargeting campaigns; exclude
converted users from prospecting.

### Frequency & Measurement

Use frequency capping (3-5/week awareness, 1-2/week direct response; Target
Frequency campaigns up to 4/week). **Demand Gen does not support frequency
capping** — DV360 lifetime caps deprecated after Feb 28, 2025 (max period now
30 days). Track view-through conversions; use data-driven attribution; use
Brand Lift Studies for awareness.

| Metric | Benchmark |
|--------|-----------|
| View Rate (skippable) | ≥15% |
| CPV (skippable) | $0.01-0.10 |
| VTR (bumper) | 90%+ |
| CTR (Demand Gen) | ≥0.5% |

### Deprecated

Video Action Campaigns (fully deprecated Apr 2026), overlay ads (discontinued
2023), rule-based attribution (auto-upgraded to DDA), DV360 lifetime
frequency caps.

### Deliverables

`YOUTUBE-ADS-REPORT.md` (campaign-by-campaign analysis), creative quality
scorecard, audience strategy recommendations, measurement gap analysis.

---

## 7. Apple Ads (`/ads-platforms apple`)

Formerly "Apple Search Ads" (rebranded Apr 2025). Mobile app advertising:
Search Results, Search Tab, Today Tab, Product Pages.

### Scoring Weights

| Category | Weight |
|----------|--------|
| Campaign Structure | 25% |
| Bid Health | 20% |
| Custom Product Pages | 15% |
| Attribution & MMP | 15% |
| Budget Pacing | 10% |
| TAP Coverage | 10% |
| Goal KPI Assessment | 5% |

**Campaign structure**: BOFU (Brand/Competitor/Category, Exact Match) kept
separate from MOFU (Search Match discovery, isolated ad groups — never mix
with Exact Match); promote Search Match winners to Exact Match campaigns.

**Bid health**: CPT vs category benchmarks; TTR >2.5% (Search Results) / >1.5%
(Search Tab); **Maximize Conversions** (GA Feb 26, 2026) is the AI auto-bidder
using Search Match with weekly-average Target CPA (replacing CPA Cap);
recommend daily budget ≥5x target CPA; two-week learning minimum; currently
installs-only (no post-install event optimization yet).

**Custom Product Pages**: Creative Sets fully deprecated — CPPs are the sole
variation mechanism (up to 70 per app since Oct 2025). ≥3 variants per
campaign type aligned to keyword themes; CPPs lift CVR ~8% games / ~6.6%
non-gaming. 78% of App Store search volume comes from devices with
Personalized Ads off — use creative-based targeting, not demographic filters.

**Attribution & MMP**: AppsFlyer/Adjust/Branch/Singular integrated via
AdAttributionKit + ATT; dual attribution since Apr 10, 2025 (SKAN/AAK
postbacks + AdServices API); monitor ATT opt-in rate.

**Budget pacing**: daily cap (ASA pacing is daily, not monthly); flag if
consistently hitting cap (missing volume) or <50% of cap (creative/bid
issue).

### TAP Coverage

| Placement | Best for | Benchmark CPT |
|-----------|----------|----------------|
| Search Results | High intent, bottom funnel | $0.50-$3.00 |
| Search Tab | Discovery, mid funnel | $0.30-$1.50 |
| Today Tab | Brand awareness (only if >$3k/mo) | $1.00-$5.00 |
| Product Pages | Competitor conquesting | $0.50-$2.00 |

### Overall Benchmarks (2025 SplitMetrics, Search Results avg)

TTR 9.7% · Conversion Rate 66.2% · CPT $2.25 · CPA $3.76. US highest-cost
market; AMEI most cost-efficient. International markets often deliver 3-5x
better CPI than US with comparable subscription LTV.

**Deprecated**: Creative Sets (CPPs only now), CPA Cap (retiring for Target
CPA via Maximize Conversions), demographic targeting as primary strategy.

### Deliverables

```
## Apple Ads Audit
**ASA Health Score: [X]/100**
### Critical Issues / High Priority
### Campaign Structure (PASS/WARNING/FAIL per category)
### Benchmark Comparison
### Quick Wins (this week)
### Recommended Next Steps
```

---

## Cross-Platform Notes

- For creative production, creative-fatigue detection, and format-diversity
  audits, hand off to `marketing/ads-creative` — it owns
  `ads/references/platform-specs.md` and the `*-creative-specs.md` files.
- For budget/bidding cross-platform allocation, PPC math, full audits, and
  competitor intelligence, hand off to `marketing/ads-strategy`.
- For live campaign CRUD (create/launch/pause campaigns, ad sets, ads,
  audiences, pixels, budgets, experiments) against the Partners in Biz
  platform, use `ads-manager`.

## Reference Files

Paths are relative to `marketing/` (siblings of this skill).

- `ads/references/google-audit.md`, `ads/references/meta-audit.md`,
  `ads/references/linkedin-audit.md`, `ads/references/tiktok-audit.md`,
  `ads/references/microsoft-audit.md` — full audit checklists
- `ads/references/benchmarks.md` — industry benchmarks by platform
- `ads/references/scoring-system.md` — weighted scoring algorithm
- `ads/references/gaql-notes.md` — Google Ads Query Language field notes
- `ads/references/conversion-tracking.md` — pixel/CAPI/EMQ/ttclid setup
- `ads/references/compliance.md` — regulatory and ad-policy requirements
- `ads/references/additional-platforms.md` — smaller/emerging platform notes
