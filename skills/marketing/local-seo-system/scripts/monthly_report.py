"""
Monthly Reporting Script
Phase 5 of the Local SEO System.

Generates a monthly report by:
1. Checking search visibility for target keywords
2. Checking if business appears in LLM recommendations
3. Reviewing competitor changes
4. Producing an action plan for next month

Usage: Run via execute_code or scheduled via Hermes cron.
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


def run_monthly_report(business_name=None, service_type=None, city=None, state=None,
                       website_url=None, services=None, output_dir=None):
    """Generate the monthly SEO report."""
    from hermes_tools import web_search, web_extract, read_file, write_file

    cfg = load_config()
    business_name = business_name or (cfg.get("business_name", ""))
    service_type = service_type or (cfg.get("service_type", "") if cfg else "")
    city = city or (cfg.get("city", "") if cfg else "")
    state = state or (cfg.get("state", "") if cfg else "")
    website_url = website_url or (cfg.get("website_url", "") if cfg else "")
    services = services or (cfg.get("services", []) if cfg else [])
    output_dir = output_dir or os.path.expanduser("~/local-seo")
    os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)

    if not all([business_name, service_type, city]):
        return "ERROR: Need business_name, service_type, and city."

    now = datetime.now()
    month_str = now.strftime("%Y-%m")
    month_name = now.strftime("%B %Y")
    prev_month = datetime(now.year, now.month - 1 if now.month > 1 else 12,
                          now.day if now.month > 1 else 28).strftime("%B %Y")

    print(f"=== Monthly SEO Report: {month_name} ===")
    print(f"Business: {business_name}\n")

    # Step 1: Check search visibility
    visibility_queries = [
        f"{business_name} {city}",
        f"{service_type} {city} {state}",
        f"best {service_type} in {city}",
    ]
    visibility_data = {}
    for q in visibility_queries:
        r = web_search(q, limit=5)
        if r and "data" in r and "web" in r["data"]:
            visibility_data[q] = r["data"]["web"]

    # Check if business website appears
    self_visibility = {}
    for q, results in visibility_data.items():
        position = None
        for i, r in enumerate(results):
            if website_url and website_url in r.get("url", ""):
                position = i + 1
                break
        self_visibility[q] = position

    # Step 2: Check LLM citation status
    llm_queries = [
        f"best {service_type} in {city} {state}",
        f"top rated {service_type} {city}",
        f"{service_type} recommendations {city}",
    ]
    llm_mentioned = []
    for q in llm_queries:
        r = web_search(q, limit=5)
        if r and "data" in r and "web" in r["data"]:
            for result in r["data"]["web"]:
                text = f"{result.get('title', '')} {result.get('description', '')}".lower()
                if business_name.lower() in text:
                    llm_mentioned.append({
                        "query": q,
                        "source": result.get("url", ""),
                        "title": result.get("title", ""),
                    })

    # Step 3: Competitor movement check
    comp_query = f"{service_type} {city} {state}"
    comp_results = web_search(comp_query, limit=8)
    current_competitors = []
    if comp_results and "data" in comp_results and "web" in comp_results["data"]:
        for r in comp_results["data"]["web"]:
            domain = r.get("url", "").split("/")[2] if "/" in r.get("url", "") else ""
            current_competitors.append({
                "domain": domain,
                "title": r.get("title", ""),
                "url": r.get("url", ""),
            })

    # Step 4: Check review profiles
    review_queries = [
        f"{business_name} google reviews",
        f"{business_name} yelp {city}",
        f"{business_name} reviews {city}",
    ]
    review_data = []
    for q in review_queries:
        r = web_search(q, limit=3)
        if r and "data" in r and "web" in r["data"]:
            for result in r["data"]["web"]:
                review_data.append({
                    "source": result.get("url", ""),
                    "title": result.get("title", ""),
                })

    # Step 5: Check NAP consistency
    nap_query = f'"{business_name}" "{city}" phone address'
    nap_results = web_search(nap_query, limit=5)
    nap_sources = []
    if nap_results and "data" in nap_results and "web" in nap_results["data"]:
        for r in nap_results["data"]["web"]:
            nap_sources.append({
                "source": r.get("url", ""),
                "title": r.get("title", ""),
                "description": r.get("description", ""),
            })

    # Step 6: Load previous report for comparison
    reports_dir = os.path.join(output_dir, "reports")
    prev_report_path = os.path.join(reports_dir, f"MONTHLY-REPORT-{now.year}-{str(now.month - 1 if now.month > 1 else 12).zfill(2)}.md")
    prev_report = ""
    if os.path.exists(prev_report_path):
        try:
            prev = read_file(prev_report_path, limit=50)
            if prev and "content" in prev:
                prev_report = prev["content"]
        except:
            pass

    # Build the report
    report = f"""# Monthly SEO Report: {month_name}
**Generated:** {now.strftime("%Y-%m-%d %H:%M")}
**Business:** {business_name}
**Service:** {service_type}
**Location:** {city}, {state}

---

## 1. Search Visibility

| Query | Your Position | Notes |
|-------|-------------|-------|
"""
    for q, pos in self_visibility.items():
        status = f"Position {pos}" if pos else "Not in top 5"
        note = "Good" if pos and pos <= 3 else ("Found" if pos else "NEEDS WORK")
        report += f'| {q[:50]} | {status} | {note} |\n'

    if not self_visibility:
        report += '| - | No data | Run a more detailed audit |\n'

    report += f"""
---

## 2. LLM Citation Status

**Business found in AI sources:** {"YES" if llm_mentioned else "NO"}

"""
    if llm_mentioned:
        report += "| Query | Source | Title |\n"
        report += "|-------|--------|-------|\n"
        for m in llm_mentioned:
            report += f'| {m["query"][:40]} | {m["source"][:40]} | {m["title"][:50]} |\n'
    else:
        report += f"""Your business was **not found** in the top sources that AI models cite for:
- "best {service_type} in {city}"
- "top rated {service_type} {city}"
- "{service_type} recommendations {city}"

**Action:** Run `llm_citation_check.py` for a full source map and action plan.
"""

    report += f"""
---

## 3. Competitor Landscape

**Top competitors for "{service_type} {city} {state}":**

| # | Competitor | URL |
|---|-----------|-----|
"""
    for i, c in enumerate(current_competitors[:8], 1):
        report += f'| {i} | {c["title"][:50]} | {c["domain"]} |\n'

    report += f"""
---

## 4. Review Profile Status

| Source | Status |
|--------|--------|
"""
    for r in review_data[:5]:
        report += f'| {r["title"][:50]} | Found |\n'

    if not review_data:
        report += "| - | No review profiles found in search |\n"

    report += f"""
---

## 5. NAP Consistency (Name, Address, Phone)

"""
    if nap_sources:
        report += "Sources with your business listing:\n\n"
        for s in nap_sources:
            report += f"- **{s['title'][:50]}**: {s['description'][:100]}\n"
        report += "\n*Verify that Name, Address, and Phone are identical across all listings.*\n"
    else:
        report += "*NAP data not found via search. Verify manually on key directories.*\n"

    report += f"""
---

## 6. Month-over-Month Comparison

"""
    if prev_report:
        report += f"*Previous report ({prev_month}) found. Key metrics compared below.*\n\n"
        report += "| Metric | This Month | Last Month | Change |\n"
        report += "|--------|-----------|-----------|--------|\n"
        report += "| Search visibility (queries in top 5) | [CURRENT] | [PREVIOUS] | [DELTA] |\n"
        report += "| LLM citations | [CURRENT] | [PREVIOUS] | [DELTA] |\n"
        report += "| Review count | [CHECK GBP] | [CHECK GBP] | [DELTA] |\n"
        report += "| New GBP posts | [CHECK GBP] | [CHECK GBP] | [DELTA] |\n"
    else:
        report += f"*No previous report found for {prev_month}. This is the baseline month.*\n"

    report += f"""
---

## 7. Action Items for Next Month

### HIGH PRIORITY (Do This Week)
1. **Verify GBP completeness** — Ensure all fields are filled, photos are current
2. **Respond to all new reviews** — Use review response templates
3. **Post to GBP 2-3x this week** — Use post calendar from GBP-POST-CALENDAR.md

### MEDIUM PRIORITY (Do This Month)
4. **Build top 3 missing city/service pages** — See KEYWORD-GAP-ANALYSIS.md
5. **Submit to 3 directories** — From LLM-SOURCE-MAP.md
6. **Send 2 outreach emails** — Using OUTREACH-PITCHES.md templates

### LOW PRIORITY (Ongoing)
7. **Monitor LLM citations** — Re-run llm_citation_check.py
8. **Update seasonal content** — Adjust for next month
9. **Engage in local online communities** — Reddit, NextDoor, Facebook groups

---

## 8. Scripts to Run This Month

Run these via execute_code for fresh data:

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `gbp_audit.py` | Full competitor GBP audit | Monthly |
| `llm_citation_check.py` | Check AI citation status | Monthly |
| `keyword_gap.py` | Find new keyword opportunities | Monthly |
| `lead_response.py` | Update response templates | Quarterly |

---

*Generated by Local SEO System v1.0*
*Next report: {(now.replace(month=now.month+1) if now.month < 12 else now.replace(year=now.year+1, month=1)).strftime("%B %Y")}*
"""

    report_path = os.path.join(reports_dir, f"MONTHLY-REPORT-{month_str}.md")
    write_file(report_path, report)

    print(f"\n{'='*50}")
    print(f"Monthly Report: {month_name}")
    print(f"Report saved: {report_path}")
    print(f"Search visibility: {sum(1 for v in self_visibility.values() if v)} queries in top 5")
    print(f"LLM citations: {len(llm_mentioned)} sources mention you")
    print(f"Competitors tracked: {len(current_competitors)}")
    print(f"{'='*50}")

    return f"Monthly report generated at {report_path}"


# Auto-run
cfg = load_config()
if cfg:
    run_monthly_report(
        business_name=cfg.get("business_name", ""),
        service_type=cfg.get("service_type", ""),
        city=cfg.get("city", ""),
        state=cfg.get("state", ""),
        website_url=cfg.get("website_url", ""),
        services=cfg.get("services", []),
    )
else:
    print("No config found. Create ~/local-seo/business-config.yaml first.")
