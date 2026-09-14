---
name: local-seo-system
description: "AI-powered local SEO system for local businesses. Runs the full stack: Google Business Profile optimization, LLM citation engineering (ChatGPT/Perplexity/Claude recommendations), competitor gap analysis, lead response playbooks, content generation, and automated reporting. Triggers on: local SEO, Google Business Profile, GBP, map pack, local search, LLM citations, local business SEO, get found on Google, local lead gen, AI recommendations, city pages, citation monitoring."
user-invokable: false
---

# Local SEO System: AI-Powered SEO for Local Businesses

Runs the entire local SEO operation that agencies charge $2-5k/month for:
GBP audits, competitor gap analysis, LLM citation engineering, content generation, lead response systems, and automated reporting.

## Prerequisites

Before running any workflow, collect these from the user:

1. **Business name**
2. **Service type** (e.g., plumber, HVAC, dentist, roofer)
3. **City, State** (primary service area)
4. **Google Business Profile URL** (if they have one)
5. **Website URL** (if they have one)
6. **List of core services** they offer
7. **Top 3-5 competitors** (names or let the system find them)
8. **Neighborhoods/areas served** (beyond the main city)

Store these as a client context object. If any are missing, ask before proceeding.

---

## PHASE 1: Google Business Profile Domination

The GBP is the #1 local ranking factor. Most competitors have half-empty profiles. This is the fastest win.

### 1A. Competitor GBP Audit

**Goal**: Compare the business's GBP against the top 3 map pack competitors and produce a gap analysis.

**Steps**:
1. Use web_search to find top 3 competitors ranking in the local map pack for `[service type] in [city]`
2. For each competitor AND the user's business, extract:
   - Primary and secondary GBP categories
   - Number of photos
   - Number of reviews and average rating
   - Services listed on GBP
   - Attributes (e.g., "Women-owned", "Online estimates")
   - Posting frequency (recent posts?)
   - Q&A activity
   - Description text
3. Build a gap analysis table with columns:
   | Element | Your Business | Competitor 1 | Competitor 2 | Competitor 3 | Gap? |
4. Produce a prioritized action list of the 10 highest-impact changes ranked by estimated ranking impact
5. Save as `GBP-AUDIT-REPORT.md`

**Search queries to use**:
- `"[service type]" "[city]" "near me"`
- `"best [service type] in [city]"`
- `"[service type] [city]" reviews`
- `[city] [service type] google maps`

### 1B. 30-Day GBP Post Calendar

**Goal**: Generate 30 ready-to-post GBP updates with keyword targeting.

**Post type mix**:
- 10 service highlight posts
- 8 customer success stories (with `[CUSTOMER NAME]` and `[JOB DETAILS]` placeholders)
- 6 seasonal/timely posts (current month/season in the city)
- 4 FAQ-style posts
- 2 special offer posts

**Each post must**:
- Be 150-300 characters
- Include one primary local keyword naturally
- End with a clear CTA (Call, Book Online, Visit Website)
- Have a suggested photo description

**Output format**: Table with columns:
| Day | Post Type | Headline | Body | Keyword Targeted | CTA | Suggested Photo |

Save as `GBP-POST-CALENDAR.md`

### 1C. Service Descriptions, Q&A, and Category Recommendations

**Goal**: Generate all supporting GBP content.

**Deliverables**:

1. **Service descriptions** (one per service listed in prerequisites):
   - 750-1,000 characters each
   - 2-3 local keywords naturally integrated
   - Structure: problem → approach → differentiator
   - Include city/area name at least once

2. **15 Q&A pairs** for GBP:
   - Questions real customers ask before booking
   - Answers that subtly include local keywords
   - Mix of pricing, timing, scope, and trust questions

3. **Category recommendations**:
   - Primary category (best match for search intent)
   - 5-9 secondary categories (based on competitor analysis)
   - Rationale for each

Save as `GBP-CONTENT-KIT.md`

### 1D. Review Response Template Library

**Goal**: Templates for fast, keyword-rich, human-sounding review replies.

**Templates needed**:
- 5 for 5-star reviews (varying length/tone)
- 3 for 4-star reviews (acknowledge positive, invite more feedback)
- 5 for 3-star-or-below reviews (de-escalate, professional, not defensive)
- 3 for reviews mentioning specific services

**Each template must**:
- Naturally include city name or neighborhood
- Reference specific service when possible
- End warmly
- Use `[BRACKETS]` for personalizable details

Save as `REVIEW-RESPONSE-TEMPLATES.md`

### 1E. GBP Category & Attribute Optimization

**Goal**: Ensure every GBP category and attribute matches or exceeds competitors.

**Steps**:
1. List all categories and attributes used by top 3 competitors
2. Compare to the business's current selections
3. Recommend additions with reasoning
4. Flag any that might be hurting (wrong primary category, conflicting attributes)

---

## PHASE 2: Lead Response System

The #1 reason local businesses lose jobs: slow follow-up. Customer calls, gets voicemail, calls the next guy.

### 2A. Inbound Response Playbook

**Deliverables**:

1. **SMS auto-reply for missed calls**:
   - Acknowledges the missed call
   - Sets callback time expectation
   - Offers to text details
   - Warm, local-tradesperson voice (NOT corporate)

2. **5 inquiry response templates**:
   - Pricing questions
   - Availability questions
   - Scope questions ("do you do X?")
   - Emergency requests
   - "Just looking for a quote"

3. **Qualification checklist** (6 questions):
   - Location (within service area?)
   - Scope of work
   - Timing/urgency
   - Budget range
   - Decision-maker confirmed?
   - Previous experience with similar providers

4. **Follow-up sequence**:
   - 1 hour after first contact
   - 24 hours if no response
   - 3 days if cold
   - 7 days (final touch)
   - Each with specific message template

Save as `LEAD-RESPONSE-PLAYBOOK.md`

### 2B. FAQ Library for Lead Pre-Qualification

**Goal**: 20 FAQs that rank on Google AND pre-qualify leads.

**Each answer must be**:
- 60-120 words
- Honest about pricing ranges where possible
- Set realistic expectations on timing
- Subtly reinforce value without bragging
- End by inviting the next step (call, form, booking)

Save as `FAQ-LIBRARY.md`

---

## PHASE 3: LLM Citation Engineering

This is the frontier. Getting recommended when people ask AI assistants "who's the best [service] in [city]?"

### 3A. Source Discovery

**Goal**: Find exactly which sources AI models cite for local service recommendations.

**Steps**:
1. Search across these queries using web_search and browser:
   - `"best [service type] in [city]"`
   - `"top-rated [service type] [city]"`
   - `"[service type] near [neighborhood]"`
   - `"[service type] recommendations [city]"`
   - `"who is the best [service type] in [city]"`

2. For each query, identify:
   - Which websites/articles are cited as sources
   - What those articles have in common (structure, length, signals)
   - Domain Authority estimates
   - Content type (listicle, directory, press, blog)

3. Build a source map table:
   | Query | Source URL | Domain Authority | Content Type | Difficulty to Get Listed |

4. For the user's business, assess: what would need to be true for their business to be cited?

Save as `LLM-SOURCE-MAP.md`

### 3B. Better Content Creation

**Goal**: Create content that surpasses the top-cited sources so AI models prefer it.

**For each top-cited "best of" listicle**:
1. Analyze the article's structure, length, depth
2. Draft a more comprehensive version that:
   - Covers every business in the original + 3-5 additions
   - Includes specific selection criteria (years in business, license numbers, specialties, response time, service area)
   - Mentions the user's business naturally and honestly
   - Includes a comparison table
   - Is at least 2,000 words
   - Has clear H2s and H3s for each business
   - Written in neutral, journalistic tone (NOT sales pitch)
3. Optimize for the same keywords + additional long-tail terms

Save as `BETTER-CONTENT-[topic].md`

### 3C. Outreach Pitch Templates

**Goal**: Get the business mentioned on external sites that AI models pull from.

**5 pitch emails targeting**:
- Local news sites
- Neighborhood blogs
- Chamber of Commerce
- Industry association directories
- "Best of [city]" listicles

**Each pitch must**:
- Be under 150 words
- Offer genuine value (data point, quote, free service, story hook)
- Reference a specific recent article they published (with placeholder)
- Make a clear ask
- Have a high-open-rate subject line

Save as `OUTREACH-PITCHES.md`

---

## PHASE 4: Website & Content Optimization

### 4A. City/Service Page Generation

**Goal**: Create optimized location pages for every city/neighborhood in the service area.

**For each [service x city] combination**:
- Unique title: "[Service] in [City], [State] | [Business Name]"
- Meta description with city name and primary keyword
- H1 with service + city
- Content structure:
  - Opening paragraph with local reference (landmark, neighborhood, etc.)
  - Service description specific to the area
  - Why locals choose [Business Name]
  - Service area map description
  - FAQ section (3-5 questions unique to this page)
  - CTA section
- Internal links to related service pages
- Minimum 800 words per page
- NO duplicate content across pages (each must be substantively unique)

Save each as `CITY-PAGE-[service]-[city].md`

### 4B. Keyword Gap Analysis

**Steps**:
1. Identify top 10 competitor keywords using web search
2. Map to existing pages on the user's site
3. Find gaps (competitor ranks, user doesn't have a page)
4. Prioritize by:
   - Search intent (transactional > informational)
   - Competition level
   - Estimated traffic value
   - Ease of creating content

**Output**: Priority-ranked list of pages to build with target keywords and content brief for each.

Save as `KEYWORD-GAP-ANALYSIS.md`

---

## PHASE 5: Monthly Reporting & Monitoring

### Monthly Report Template

Pull/assess:
1. **GBP insights**: Views, clicks, calls, direction requests (month over month)
2. **Review velocity**: New reviews this month, average rating trend
3. **Post activity**: GBP posts published, engagement
4. **Keyword movement**: Track 10 priority keywords in local search
5. **LLM citation check**: Does the business appear in ChatGPT/Perplexity/Claude for target queries?
6. **Citation consistency**: NAP (Name, Address, Phone) across directories
7. **Action items for next month**: Top 5 priorities

Save as `MONTHLY-REPORT-[YYYY-MM].md`

---

## Automation Layer (Scripts + Cron)

The skill includes 7 Python scripts that run via `execute_code`. No VPS needed -- Hermes cron handles scheduling.

### Setup

1. Copy the config template to `~/local-seo/business-config.yaml` and fill it in:
```bash
mkdir -p ~/local-seo
cp ~/.hermes/skills/marketing/local-seo-system/templates/business-config.yaml ~/local-seo/business-config.yaml
# Then edit ~/local-seo/business-config.yaml with your business details
```

2. That's it. Scripts auto-read from the config.

### Scripts

| Script | What It Does | When to Run |
|--------|-------------|-------------|
| `gbp_audit.py` | Phase 1A: Competitor GBP gap analysis | Once, then monthly |
| `gbp_content.py` | Phase 1B-D: Post calendar, descriptions, Q&A, review templates, categories | Once, then quarterly refresh |
| `lead_response.py` | Phase 2: SMS templates, inquiry responses, follow-up sequences, FAQ library | Once |
| `llm_citation_check.py` | Phase 3: Source discovery + outreach pitches | Monthly |
| `keyword_gap.py` | Phase 4: Keyword gaps + page-building plan | Monthly |
| `monthly_report.py` | Phase 5: Full monthly status report | Monthly |
| `run_full_audit.py` | Runs ALL phases in sequence | Once (initial setup) |
| `run_monthly.py` | Runs citation check + keyword gap + monthly report | Monthly (cron) |

### Running Scripts

**Run a single script:**
```
exec(open(os.path.expanduser("~/.hermes/skills/marketing/local-seo-system/scripts/gbp_audit.py")).read())
```

**Run everything (first time):**
```
exec(open(os.path.expanduser("~/.hermes/skills/marketing/local-seo-system/scripts/run_full_audit.py")).read())
```

**Run monthly maintenance:**
```
exec(open(os.path.expanduser("~/.hermes/skills/marketing/local-seo-system/scripts/run_monthly.py")).read())
```

### Setting Up Monthly Cron

Use Hermes `cronjob` to schedule the monthly runner:

```
cronjob action=create name="local-seo-monthly" schedule="0 9 1 * *" prompt="Load the local-seo-system skill. Read ~/local-seo/business-config.yaml. Run the monthly maintenance script via execute_code: exec(open(os.path.expanduser('~/.hermes/skills/marketing/local-seo-system/scripts/run_monthly.py')).read()). After it completes, summarize the results: which tasks succeeded, any errors, and the top 3 action items for this month."
```

This runs at 9am on the 1st of every month automatically.

### What Gets Generated

All output goes to `~/local-seo/`:
```
~/local-seo/
├── business-config.yaml          # Your business config
├── GBP-AUDIT-REPORT.md           # Competitor gap analysis
├── GBP-POST-CALENDAR.md          # 30 days of posts
├── GBP-CONTENT-KIT.md            # Descriptions, Q&A, categories
├── LEAD-RESPONSE-PLAYBOOK.md     # SMS, inquiry templates, follow-ups
├── FAQ-LIBRARY.md                # 20 pre-qualifying FAQs
├── LLM-SOURCE-MAP.md             # AI citation source analysis
├── OUTREACH-PITCHES.md           # 5 pitch email templates
├── KEYWORD-GAP-ANALYSIS.md       # Keyword opportunities
├── AUDIT-SUMMARY.md              # Full audit summary
├── city-pages/                   # Generated city/service pages
└── reports/
    └── MONTHLY-REPORT-YYYY-MM.md # Monthly status reports
```

---

## Tone & Voice Guidelines for All Content

**DO**:
- Write like a friendly local expert, not a marketing agency
- Use specific local references (neighborhoods, landmarks, local events)
- Include real numbers, real timelines, real outcomes where possible
- Write at 8th grade reading level (accessible, not dumbed down)
- Use contractions and natural speech patterns

**DON'T**:
- Use jargon like "synergy", "leverage", "comprehensive solutions"
- Write like a corporation (no "We are committed to excellence")
- Stuff keywords unnaturally
- Make claims that can't be backed up
- Use stock phrases ("your trusted partner", "family-owned and operated" unless actually true and relevant)

---

## Output File Structure

All outputs go into a `local-seo/` directory in the current workspace:

```
local-seo/
├── GBP-AUDIT-REPORT.md
├── GBP-POST-CALENDAR.md
├── GBP-CONTENT-KIT.md
├── REVIEW-RESPONSE-TEMPLATES.md
├── LEAD-RESPONSE-PLAYBOOK.md
├── FAQ-LIBRARY.md
├── LLM-SOURCE-MAP.md
├── BETTER-CONTENT-[topic].md
├── OUTREACH-PITCHES.md
├── KEYWORD-GAP-ANALYSIS.md
├── city-pages/
│   ├── CITY-PAGE-[service]-[city].md
│   └── ...
└── reports/
    ├── MONTHLY-REPORT-[YYYY-MM].md
    └── ...
```

---

## Quick Start

When a user asks to run this system:

1. Collect prerequisites (business name, service type, city, URLs, services, competitors, areas)
2. Ask which phase to start with (or run all sequentially)
3. Create the `local-seo/` output directory
4. Execute phase by phase, saving outputs as you go
5. After all phases, provide a summary of what was produced and recommended next steps

**Time estimates**:
- Phase 1 (GBP): ~30 minutes with web search
- Phase 2 (Lead Response): ~15 minutes
- Phase 3 (LLM Citations): ~45 minutes with research
- Phase 4 (Website/Content): ~30 minutes per city page
- Phase 5 (Reporting): Set up template, then 10 minutes/month

**Total initial setup**: 2-3 hours for a complete system. Then 30 minutes/week maintenance.
