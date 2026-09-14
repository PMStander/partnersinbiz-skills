"""
LLM Citation Check & Source Discovery
Phase 3 of the Local SEO System.

Checks whether the business appears in AI-generated recommendations
(ChatGPT, Perplexity, Google AI Overviews) and discovers the sources
those AIs cite.

Usage: Run via execute_code.
"""

import os
import json
from datetime import datetime


def load_config():
    config_path = os.path.expanduser("~/local-seo/business-config.yaml")
    if os.path.exists(config_path):
        raw = open(config_path).read()
        cfg = {}
        current_key = None
        in_list = False
        list_items = []
        for line in raw.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("- ") and current_key:
                list_items.append(stripped[2:].strip('"').strip("'"))
                in_list = True
                continue
            if in_list and current_key:
                cfg[current_key] = list_items
                in_list = False
                list_items = []
            if ":" in stripped and not stripped.startswith("-"):
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val:
                    cfg[key] = val
                else:
                    current_key = key
                    list_items = []
        if in_list and current_key:
            cfg[current_key] = list_items
        return cfg
    return None


def run_llm_citation_check(business_name=None, service_type=None, city=None,
                           state=None, output_dir=None):
    """Check LLM citation sources and track if business appears in AI recommendations."""
    from hermes_tools import web_search, web_extract, write_file

    cfg = load_config()
    business_name = business_name or (cfg.get("business_name", ""))
    service_type = service_type or (cfg.get("service_type", "") if cfg else "")
    city = city or (cfg.get("city", "") if cfg else "")
    state = state or (cfg.get("state", "") if cfg else "")
    output_dir = output_dir or os.path.expanduser("~/local-seo")
    os.makedirs(output_dir, exist_ok=True)

    if not all([business_name, service_type, city]):
        return "ERROR: Need business_name, service_type, and city."

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"=== LLM Citation Check ===")
    print(f"Checking AI recommendation sources for: {business_name}")
    print()

    # Step 1: Search for "best of" queries that AIs would cite
    target_queries = [
        f"best {service_type} in {city} {state}",
        f"top rated {service_type} {city}",
        f"{service_type} recommendations {city}",
    ]

    all_sources = {}
    query_results = {}

    for query in target_queries:
        print(f"  Searching: {query}")
        results = web_search(query, limit=5)
        if results and "data" in results and "web" in results["data"]:
            query_results[query] = results["data"]["web"]
            for r in results["data"]["web"]:
                url = r.get("url", "")
                domain = url.split("/")[2] if "/" in url else url
                if domain not in all_sources:
                    all_sources[domain] = {
                        "url": url,
                        "title": r.get("title", ""),
                        "description": r.get("description", ""),
                        "cited_for_queries": [],
                        "count": 0,
                    }
                all_sources[domain]["cited_for_queries"].append(query)
                all_sources[domain]["count"] += 1

    print(f"\n  Found {len(all_sources)} unique source domains across {len(target_queries)} queries\n")

    # Step 2: Categorize sources
    directory_domains = ["yelp", "angi", "homeadvisor", "thumbtack", "houzz", "bbb",
                         "yellowpages", "superpages", "manta", "foursquare"]
    listicle_indicators = ["best", "top", "review", "recommended", "rank", "number"]
    press_indicators = ["news", "times", "post", "herald", "gazette", "journal", "tribune",
                        "chronicle", "dispatch", "examiner"]

    categorized = {
        "listicle": [],
        "directory": [],
        "press": [],
        "blog": [],
        "other": [],
    }

    for domain, data in all_sources.items():
        title_lower = data["title"].lower()
        desc_lower = data["description"].lower()
        domain_lower = domain.lower()

        if any(d in domain_lower for d in directory_domains):
            categorized["directory"].append((domain, data))
        elif any(p in domain_lower for p in press_indicators):
            categorized["press"].append((domain, data))
        elif any(i in title_lower or i in desc_lower for i in listicle_indicators):
            categorized["listicle"].append((domain, data))
        else:
            categorized["other"].append((domain, data))

    # Step 3: Check if business appears in any top results
    business_mentioned = []
    for domain, data in all_sources.items():
        combined_text = f"{data['title']} {data['description']}".lower()
        if business_name.lower() in combined_text:
            business_mentioned.append((domain, data))

    # Step 4: Extract content from top listicle sources for deeper analysis
    top_listicles = sorted(
        categorized["listicle"],
        key=lambda x: x[1]["count"],
        reverse=True
    )[:5]

    listicle_details = []
    if top_listicles:
        urls = [data["url"] for _, data in top_listicles if data.get("url")]
        if urls:
            extracted = web_extract(urls)
            if extracted and "results" in extracted:
                for r in extracted["results"]:
                    if r.get("content"):
                        listicle_details.append({
                            "url": r["url"],
                            "content_preview": r["content"][:2000],
                            "has_business": business_name.lower() in r["content"].lower(),
                        })

    # Step 5: Check Perplexity/ChatGPT-style result patterns
    ai_queries = [
        f"site:perplexity.ai best {service_type} {city}",
        f"site:reddit.com best {service_type} {city} recommendations",
    ]
    ai_context = ""
    for q in ai_queries:
        r = web_search(q, limit=3)
        if r and "data" in r and "web" in r["data"]:
            for result in r["data"]["web"][:2]:
                ai_context += f"- {result.get('title', '')}: {result.get('description', '')}\n"

    # Build the report
    report = f"""# LLM Citation Check & Source Map
**Generated:** {now}
**Business:** {business_name}
**Service:** {service_type}
**Location:** {city}, {state}

---

## Executive Summary

{"**YOUR BUSINESS WAS FOUND** in search results for some queries!" if business_mentioned else "**YOUR BUSINESS WAS NOT FOUND** in the top AI-cited sources for any target query."}

- Total sources discovered: {len(all_sources)}
- Queries checked: {len(target_queries)}
- Business mentions found: {len(business_mentioned)}

{"### Where You Appear:" if business_mentioned else ""}
"""
    for domain, data in business_mentioned:
        report += f"- **{domain}**: {data['title']}\n"

    report += f"""
---

## Source Map by Category

### Listicles & "Best Of" Articles
*These are the articles AI models are most likely to cite when recommending local businesses.*

| # | Source | Title | Queries It Ranks For | Difficulty |
|---|--------|-------|---------------------|------------|
"""
    for i, (domain, data) in enumerate(sorted(categorized["listicle"],
                                                key=lambda x: x[1]["count"], reverse=True), 1):
        queries_str = ", ".join([q.split(service_type)[0].strip().strip('"') for q in data["cited_for_queries"][:3]])
        report += f'| {i} | {domain} | {data["title"][:60]} | {queries_str} | [ASSESS] |\n'

    report += f"""
### Directories
*Yelp, Angi, HomeAdvisor, etc. AI models reference these heavily.*

| # | Source | Title | Est. Difficulty |
|---|--------|-------|----------------|
"""
    for i, (domain, data) in enumerate(categorized["directory"], 1):
        report += f'| {i} | {domain} | {data["title"][:60]} | Easy-Medium |\n'

    report += f"""
### Local Press & News
*Local news citations carry high authority in AI recommendations.*

| # | Source | Title |
|---|--------|-------|
"""
    for i, (domain, data) in enumerate(categorized["press"], 1):
        report += f'| {i} | {domain} | {data["title"][:60]} |\n'

    report += f"""
---

## Top Listicle Analysis
*Deep dive into the "best of" articles most likely to be cited by AI.*

"""
    for i, detail in enumerate(listicle_details, 1):
        report += f"""### Listicle {i}: {detail['url']}
**Business mentioned:** {"YES" if detail['has_business'] else "NO"}

**Content preview:**
{detail['content_preview'][:500]}...

---

"""

    report += f"""
## Reddit & Community Mentions

{ai_context if ai_context else "No Reddit/community results found for these queries."}

---

## Action Plan: How to Get Cited by AI

### Immediate (This Week)
1. **Claim/update profiles on all directories found above** — Ensure NAP consistency everywhere
2. **Get listed on the top 3 listicle sources** — Either submit your business or create your own better version
3. **Respond to any Reddit threads** about {service_type} in {city} (helpful, not promotional)

### Short-Term (This Month)
4. **Create a "Best {service_type.capitalize()} in {city}" article** on your own website
   - Make it genuinely comprehensive (cover 10-15 businesses, not just yourself)
   - Include selection criteria, comparison tables, specific details
   - Target 2,000+ words with clear H2/H3 structure
5. **Pitch 2-3 local publications** — Use the outreach templates from OUTREACH-PITCHES.md
6. **Get active on NextDoor and local Facebook groups** — Answer questions, be helpful

### Ongoing (Monthly)
7. **Re-run this check monthly** — Track if your business starts appearing
8. **Monitor new listicles** — Reach out to authors of new "best of" articles
9. **Build local backlinks** — Chamber of Commerce, local sponsors, community events

---

## Target Source Priority Matrix

| Priority | Source Type | Action | Timeline |
|----------|------------|--------|----------|
| 1 | Top listicles | Submit/pitch for inclusion | This week |
| 2 | Major directories | Claim and optimize profiles | This week |
| 3 | Your own "best of" article | Create comprehensive guide | This month |
| 4 | Local press outreach | Pitch stories and expertise | This month |
| 5 | Reddit/community | Engage authentically | Ongoing |
| 6 | Industry associations | Get listed in directories | This month |

---

*Generated by Local SEO System v1.0*
*Re-run monthly to track citation progress.*
"""

    report_path = os.path.join(output_dir, "LLM-SOURCE-MAP.md")
    write_file(report_path, report)

    # Generate outreach pitch templates
    outreach = f"""# Outreach Pitch Templates
**Generated:** {now}
**Business:** {business_name}
**Target:** Local publications, blogs, and directories in {city}, {state}

---

## Pitch 1: Local News Site
**Subject:** {city}'s most asked {service_type} question — we have the data

> Hi [EDITOR NAME],
>
> I noticed [PUBLICATION] recently covered [ARTICLE TOPIC] — great piece.
>
> I run {business_name}, and after [X years] serving {city} homeowners, we've noticed a pattern: [SPECIFIC INSIGHT — e.g., "80% of emergency calls we get could have been prevented with basic maintenance"].
>
> Happy to share a quick data-backed tip sheet or quote for any future articles about home maintenance in {city}. No catch — just want to be a helpful resource.
>
> Best,
> {owner_name if cfg and cfg.get('owner_name') else '[YOUR NAME]'}
> {business_name}

---

## Pitch 2: Neighborhood Blog
**Subject:** Free resource for {city} homeowners — [SEASON] {service_type} checklist

> Hi [BLOGGER NAME],
>
> Love [BLOG NAME] — especially the recent piece on [ARTICLE].
>
> I put together a [SEASON] maintenance checklist specifically for {city} homes (covers [SERVICE TYPE] stuff that's easy to overlook). It's free, no signup required.
>
> Would your readers find this useful? Happy to let you share it or write a guest version tailored to your audience.
>
> Cheers,
> [YOUR NAME]
> {business_name}

---

## Pitch 3: Chamber of Commerce
**Subject:** New member introduction — {business_name} ({service_type} in {city})

> Hi [CONTACT NAME],
>
> I'm [YOUR NAME] with {business_name}. We've been serving {city} for [X YEARS] and just joined the Chamber.
>
> We specialize in [TOP 2 SERVICES] and are available as a local resource for any Chamber members who need {service_type} work — happy to offer a [DISCOUNT/PRIORITY SCHEDULING] for fellow members.
>
> Also available if you ever need a quote or expert input for Chamber communications about home/business maintenance.
>
> Looking forward to being involved!
>
> [YOUR NAME]
> {business_name}

---

## Pitch 4: "Best Of" Listicle Author
**Subject:** Quick resource for your {city} {service_type} roundup

> Hi [AUTHOR NAME],
>
> I came across your article "[ARTICLE TITLE]" while researching {service_type} options in {city}. Really well done.
>
> I run {business_name} — we've been at it for [X YEARS] with [NUMBER]+ reviews averaging [RATING] stars. A few things that might be useful if you update the piece:
>
> - [SPECIFIC DIFFERENTIATOR 1]
> - [SPECIFIC DIFFERENTIATOR 2]
> - [RECENT ACHIEVEMENT or CERTIFICATION]
>
> No pressure to include us, but wanted to make sure you had current info. Happy to provide any details you need.
>
> Best,
> [YOUR NAME]

---

## Pitch 5: Industry Association
**Subject:** {business_name} — {city}'s licensed {service_type} for your directory

> Hi [DIRECTORY CONTACT],
>
> I'd like to submit {business_name} for inclusion in your [ASSOCIATION NAME] directory.
>
> Quick details:
> - Licensed in {state} ([LICENSE NUMBER])
> - [X YEARS] serving {city} and surrounding areas
> - Specialties: [TOP 3 SERVICES]
> - [NUMBER]+ verified reviews, [RATING]-star average
> - Insured and bonded
>
> Please let me know what additional information you need. Happy to provide photos, references, or anything else.
>
> Thanks!
> [YOUR NAME]
> {business_name}

---

*Generated by Local SEO System v1.0*
"""

    outreach_path = os.path.join(output_dir, "OUTREACH-PITCHES.md")
    write_file(outreach_path, outreach)

    print(f"\n{'='*50}")
    print(f"LLM Citation Check Complete!")
    print(f"Source map: {report_path}")
    print(f"Outreach pitches: {outreach_path}")
    print(f"Sources found: {len(all_sources)}")
    print(f"Business mentioned in: {len(business_mentioned)} sources")
    print(f"{'='*50}")

    return f"LLM citation check done. {len(all_sources)} sources mapped. Business found in {len(business_mentioned)}."


# Auto-run
cfg = load_config()
if cfg:
    run_llm_citation_check(
        business_name=cfg.get("business_name", ""),
        service_type=cfg.get("service_type", ""),
        city=cfg.get("city", ""),
        state=cfg.get("state", ""),
    )
else:
    print("No config found. Create ~/local-seo/business-config.yaml first.")
