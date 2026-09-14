"""
Keyword Gap Analysis
Phase 4B of the Local SEO System.

Discovers keywords competitors rank for that the business doesn't,
then produces a prioritized page-building plan.

Usage: Run via execute_code.
"""

import os
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


def run_keyword_gap(business_name=None, service_type=None, city=None, state=None,
                    website_url=None, competitors=None, services=None, output_dir=None):
    """Analyze competitor keywords and identify content gaps."""
    from hermes_tools import web_search, web_extract, write_file

    cfg = load_config()
    business_name = business_name or (cfg.get("business_name", ""))
    service_type = service_type or (cfg.get("service_type", "") if cfg else "")
    city = city or (cfg.get("city", "") if cfg else "")
    state = state or (cfg.get("state", "") if cfg else "")
    website_url = website_url or (cfg.get("website_url", "") if cfg else "")
    services = services or (cfg.get("services", []) if cfg else [])
    output_dir = output_dir or os.path.expanduser("~/local-seo")
    os.makedirs(output_dir, exist_ok=True)

    if not all([business_name, service_type, city]):
        return "ERROR: Need business_name, service_type, and city."

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    location = f"{city} {state}".strip()

    print(f"=== Keyword Gap Analysis ===")
    print(f"Business: {business_name}")
    print(f"Analyzing keyword landscape...\n")

    # Step 1: Discover competitor keywords via search
    keyword_queries = [
        f"{service_type} {location} services",
        f"{service_type} {location} cost pricing",
        f"{service_type} {location} emergency",
        f"best {service_type} {location}",
        f"{service_type} repair {location}",
    ]

    # Add service-specific queries
    for s in services[:5]:
        if s:
            keyword_queries.append(f"{s} {location}")
            keyword_queries.append(f"{s} cost {location}")

    all_ranking_urls = {}
    all_keywords = {}

    for query in keyword_queries:
        print(f"  Checking: {query}")
        results = web_search(query, limit=5)
        if results and "data" in results and "web" in results["data"]:
            for r in results["data"]["web"]:
                url = r.get("url", "")
                domain = url.split("/")[2] if "/" in url else url
                if domain not in all_ranking_urls:
                    all_ranking_urls[domain] = {
                        "url": url,
                        "title": r.get("title", ""),
                        "keywords_ranking_for": [],
                    }
                all_ranking_urls[domain]["keywords_ranking_for"].append(query)

                if query not in all_keywords:
                    all_keywords[query] = []
                all_keywords[query].append({
                    "domain": domain,
                    "title": r.get("title", ""),
                    "url": url,
                })

    print(f"\n  Found {len(all_ranking_urls)} ranking domains across {len(keyword_queries)} queries\n")

    # Step 2: Check what content the business already has
    existing_pages = []
    if website_url:
        site_query = f"site:{website_url.replace('https://', '').replace('http://', '').rstrip('/')}"
        site_results = web_search(site_query, limit=10)
        if site_results and "data" in site_results and "web" in site_results["data"]:
            for r in site_results["data"]["web"]:
                existing_pages.append({
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                })

    # Step 3: Extract competitor page content for keyword analysis
    top_competitors = sorted(
        all_ranking_urls.items(),
        key=lambda x: len(x[1]["keywords_ranking_for"]),
        reverse=True
    )[:5]

    competitor_content = []
    for domain, data in top_competitors:
        if website_url and domain in website_url:
            continue  # Skip self
        urls = [data["url"]]
        ext = web_extract(urls)
        if ext and "results" in ext:
            for r in ext["results"]:
                if r.get("content"):
                    competitor_content.append({
                        "domain": domain,
                        "title": data["title"],
                        "content": r["content"][:3000],
                        "keywords": data["keywords_ranking_for"],
                    })

    # Step 4: Identify gaps
    gap_keywords = []
    for query, results in all_keywords.items():
        # Check if any result is from the business's website
        self_ranking = any(
            website_url and website_url in r["url"]
            for r in results
        ) if website_url else False
        if not self_ranking:
            gap_keywords.append({
                "keyword": query,
                "competitors_ranking": [r["domain"] for r in results[:3]],
                "intent": _classify_intent(query),
                "priority": _estimate_priority(query, results),
            })

    # Build the report
    report = f"""# Keyword Gap Analysis
**Generated:** {now}
**Business:** {business_name}
**Service:** {service_type}
**Location:** {location}

---

## Executive Summary

- **Total keywords analyzed:** {len(keyword_queries)}
- **Keywords where you DON'T rank:** {len(gap_keywords)}
- **Competitor domains found:** {len(all_ranking_urls)}
- **Your indexed pages found:** {len(existing_pages)}

---

## Your Current Indexed Pages

| # | Title | URL |
|---|-------|-----|
"""
    for i, p in enumerate(existing_pages, 1):
        report += f'| {i} | {p["title"][:60]} | {p["url"]} |\n'

    if not existing_pages:
        report += '| - | No indexed pages found | Ensure your site is submitted to Google Search Console |\n'

    report += f"""
---

## Top Competitors by Keyword Coverage

| # | Domain | Keywords Found | Top Keywords |
|---|--------|---------------|-------------|
"""
    for i, (domain, data) in enumerate(top_competitors, 1):
        kw_str = ", ".join(data["keywords_ranking_for"][:3])
        report += f'| {i} | {domain} | {len(data["keywords_ranking_for"])} | {kw_str} |\n'

    report += f"""
---

## Keyword Gaps (You Don't Rank, Competitors Do)

### Priority 1: Transactional (Ready to Buy)
*These people need a {service_type} NOW. Build these pages first.*

| # | Keyword | Competitors Ranking | Content Type Needed |
|---|---------|-------------------|-------------------|
"""
    trans_gaps = [g for g in gap_keywords if g["intent"] == "transactional"]
    for i, g in enumerate(trans_gaps, 1):
        comps = ", ".join(g["competitors_ranking"][:2])
        report += f'| {i} | {g["keyword"]} | {comps} | Service/City Page |\n'

    report += f"""
### Priority 2: Commercial Investigation (Comparing Options)
*These people are deciding who to hire.*

| # | Keyword | Competitors Ranking | Content Type Needed |
|---|---------|-------------------|-------------------|
"""
    comm_gaps = [g for g in gap_keywords if g["intent"] == "commercial"]
    for i, g in enumerate(comm_gaps, 1):
        comps = ", ".join(g["competitors_ranking"][:2])
        report += f'| {i} | {g["keyword"]} | {comps} | Comparison/Review Page |\n'

    report += f"""
### Priority 3: Informational (Researching)
*Build trust and capture early-stage leads.*

| # | Keyword | Competitors Ranking | Content Type Needed |
|---|---------|-------------------|-------------------|
"""
    info_gaps = [g for g in gap_keywords if g["intent"] == "informational"]
    for i, g in enumerate(info_gaps, 1):
        comps = ", ".join(g["competitors_ranking"][:2])
        report += f'| {i} | {g["keyword"]} | {comps} | Blog/FAQ Page |\n'

    report += f"""
---

## Competitor Content Analysis

"""
    for i, comp in enumerate(competitor_content[:3], 1):
        report += f"""### Competitor {i}: {comp['domain']}
**Ranking for:** {", ".join(comp['keywords'][:3])}

**Content structure:**
{comp['content'][:800]}...

---

"""

    report += f"""
## Priority Page-Building Plan

Based on this analysis, here are the pages to build in order:

| Priority | Page Title | Target Keyword | Type | Est. Words | Notes |
|----------|-----------|---------------|------|-----------|-------|
"""
    # Generate page recommendations
    page_recs = []
    for g in trans_gaps[:5]:
        page_recs.append(f'| {len(page_recs)+1} | {g["keyword"].title()} | {g["keyword"]} | City/Service Page | 800-1200 | High intent — build first |')
    for g in comm_gaps[:3]:
        page_recs.append(f'| {len(page_recs)+1} | {g["keyword"].title()} Guide | {g["keyword"]} | Guide/Resource | 1500-2000 | Comparison content |')
    for g in info_gaps[:3]:
        page_recs.append(f'| {len(page_recs)+1} | {g["keyword"].title()} | {g["keyword"]} | Blog Post | 800-1200 | Educational content |')

    report += "\n".join(page_recs)

    report += f"""

---

## City Page Opportunity Matrix

Based on your service area, here are the city/service page combinations to build:

"""
    areas = cfg.get("surrounding_cities", []) if cfg else []
    if areas:
        report += "| Priority | City | Service | Keyword | Status |\n"
        report += "|----------|------|---------|---------|--------|\n"
        for area in areas:
            for svc in (services[:3] if services else [service_type]):
                kw = f"{svc} in {area} {state}".strip()
                report += f"| HIGH | {area} | {svc} | {kw} | TODO |\n"
    else:
        report += "*Add surrounding_cities to your config to generate city page recommendations.*\n"

    report += f"""

---

*Generated by Local SEO System v1.0*
*Re-run monthly to track keyword movement.*
"""

    report_path = os.path.join(output_dir, "KEYWORD-GAP-ANALYSIS.md")
    write_file(report_path, report)

    print(f"\n{'='*50}")
    print(f"Keyword Gap Analysis Complete!")
    print(f"Report: {report_path}")
    print(f"Gaps found: {len(gap_keywords)} keywords")
    print(f"Transactional gaps: {len(trans_gaps)}")
    print(f"Commercial gaps: {len(comm_gaps)}")
    print(f"Informational gaps: {len(info_gaps)}")
    print(f"{'='*50}")

    return f"Keyword gap analysis done. {len(gap_keywords)} gaps found. Report at {report_path}"


def _classify_intent(query):
    q = query.lower()
    transactional = ["emergency", "same day", "near me", "hire", "book", "call", "cheap", "affordable", "cost", "price", "repair", "fix", "installation", "install"]
    commercial = ["best", "top", "review", "compare", "vs", "recommended", "rated", "vs"]
    if any(t in q for t in transactional):
        return "transactional"
    elif any(c in q for c in commercial):
        return "commercial"
    return "informational"


def _estimate_priority(query, results):
    """Estimate priority based on competition and intent."""
    intent = _classify_intent(query)
    if intent == "transactional":
        return "HIGH"
    elif intent == "commercial":
        return "MEDIUM"
    return "LOW"


# Auto-run
cfg = load_config()
if cfg:
    run_keyword_gap(
        business_name=cfg.get("business_name", ""),
        service_type=cfg.get("service_type", ""),
        city=cfg.get("city", ""),
        state=cfg.get("state", ""),
        website_url=cfg.get("website_url", ""),
        services=cfg.get("services", []),
    )
else:
    print("No config found. Create ~/local-seo/business-config.yaml first.")
