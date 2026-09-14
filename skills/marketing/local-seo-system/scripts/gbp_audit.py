"""
GBP Competitor Audit Script
Phase 1A of the Local SEO System.

Reads business config, searches for top map-pack competitors,
and produces a gap analysis report.

Usage (via execute_code):
  from hermes_tools import write_file, web_search, web_extract
  exec(open("~/.hermes/skills/marketing/local-seo-system/scripts/gbp_audit.py").read())
"""

import os
import json
from datetime import datetime

# --- Config Loading ---
def load_config():
    config_paths = [
        os.path.expanduser("~/local-seo/business-config.yaml"),
        os.path.expanduser("~/local-seo/business-config.json"),
    ]
    for p in config_paths:
        if os.path.exists(p):
            raw = open(p).read()
            if p.endswith(".json"):
                return json.loads(raw)
            # Simple YAML parse (no pyyaml dependency)
            cfg = {}
            current_section = None
            current_list = None
            for line in raw.split("\n"):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if ":" in stripped and not stripped.startswith("-"):
                    key, _, val = stripped.partition(":")
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if val:
                        # Nested key like business.name
                        if current_section and not line.startswith(" ") and not line.startswith("  "):
                            current_section = None
                        if current_section:
                            cfg[f"{current_section}.{key}"] = val
                        else:
                            cfg[key] = val
                    else:
                        current_section = key
                        current_list = None
            return cfg
    return None


def run_audit(business_name=None, service_type=None, city=None, state=None,
              website_url=None, gbp_url=None, competitors=None, output_dir=None):
    """Run the GBP competitor audit. All params optional - reads from config if not provided."""
    from hermes_tools import web_search, web_extract, write_file

    # Load config for missing params
    cfg = load_config()

    business_name = business_name or (cfg.get("business_name", ""))
    service_type = service_type or (cfg.get("service_type", "") if cfg else "")
    city = city or (cfg.get("city", "") if cfg else "")
    state = state or (cfg.get("state", "") if cfg else "")
    website_url = website_url or (cfg.get("website_url", "") if cfg else "")
    output_dir = output_dir or os.path.expanduser("~/local-seo")
    os.makedirs(output_dir, exist_ok=True)

    if not all([business_name, service_type, city]):
        return "ERROR: Need business_name, service_type, and city. Set them in ~/local-seo/business-config.yaml"

    query_base = f"{service_type} in {city}"
    if state:
        query_base += f" {state}"

    print(f"=== GBP Competitor Audit ===")
    print(f"Business: {business_name}")
    print(f"Service: {service_type}")
    print(f"Location: {city}, {state}")
    print(f"Searching for competitors...\n")

    # Step 1: Find top competitors in the map pack
    search_queries = [
        f"best {service_type} in {city} {state}",
        f"{service_type} {city} {state} reviews",
    ]

    all_results = []
    for q in search_queries:
        results = web_search(q, limit=5)
        if results and "data" in results and "web" in results["data"]:
            all_results.extend(results["data"]["web"])

    # Deduplicate by domain
    seen_domains = set()
    unique_results = []
    for r in all_results:
        domain = r.get("url", "").split("/")[2] if "/" in r.get("url", "") else r.get("url", "")
        if domain not in seen_domains:
            seen_domains.add(domain)
            unique_results.append(r)

    print(f"Found {len(unique_results)} unique competitor results\n")

    # Step 2: Extract details from top competitor pages
    competitor_data = []
    urls_to_extract = [r["url"] for r in unique_results[:3] if r.get("url")]

    if urls_to_extract:
        extracted = web_extract(urls_to_extract)
        if extracted and "results" in extracted:
            for i, result in enumerate(extracted["results"]):
                if result.get("content"):
                    competitor_data.append({
                        "name": unique_results[i].get("title", f"Competitor {i+1}"),
                        "url": result.get("url", ""),
                        "content_preview": result["content"][:2000],
                    })

    # Step 3: Search specifically for the business itself
    self_query = f"{business_name} {city} {state}"
    self_results = web_search(self_query, limit=3)
    self_info = ""
    if self_results and "data" in self_results and "web" in self_results["data"]:
        self_urls = [r["url"] for r in self_results["data"]["web"][:2] if r.get("url")]
        if self_urls:
            self_extracted = web_extract(self_urls)
            if self_extracted and "results" in self_extracted:
                for r in self_extracted["results"]:
                    if r.get("content"):
                        self_info += r["content"][:1500] + "\n\n"

    gbp_info = ""
    map_data = ""

    # Step 6: Generate the report
    # Note: This script makes ~5 web calls. Takes ~60-90 seconds.
    # For a deeper audit, run additional searches manually.
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""# GBP Competitor Audit Report
**Generated:** {now}
**Business:** {business_name}
**Service:** {service_type}
**Location:** {city}, {state}

---

## Search Landscape Analysis

### Competitors Found in Search Results

| # | Competitor | Source URL |
|---|-----------|-----------|
"""
    for i, comp in enumerate(competitor_data, 1):
        report += f'| {i} | {comp["name"]} | {comp["url"]} |\n'

    report += f"""
### Competitor Content Analysis

"""
    for i, comp in enumerate(competitor_data, 1):
        report += f"""#### {i}. {comp["name"]}
**URL:** {comp["url"]}

**Content Summary:**
{comp["content_preview"][:500]}...

---

"""
    report += f"""
## Your Business's Current Web Presence

### Search Results for "{business_name}"

{self_info if self_info else "Limited data found. This may indicate weak online presence."}

### GBP-Specific Data

{gbp_info if gbp_info else "No GBP-specific data found in search results."}

---

## Map Pack Analysis

{map_data if map_data else "Map pack data not directly available via web search. Manual check recommended."}

---

## Gap Analysis Framework

Based on the competitor data above, here are the key areas to audit:

| Element | Your Business | Top Competitors | Gap? | Priority |
|---------|--------------|-----------------|------|----------|
| GBP Primary Category | [CHECK] | [FROM DATA] | ? | HIGH |
| GBP Secondary Categories | [CHECK] | [FROM DATA] | ? | HIGH |
| Number of Photos | [CHECK] | [FROM DATA] | ? | MEDIUM |
| Number of Reviews | [CHECK] | [FROM DATA] | ? | HIGH |
| Average Rating | [CHECK] | [FROM DATA] | ? | MEDIUM |
| Services Listed | [CHECK] | [FROM DATA] | ? | HIGH |
| GBP Posts (last 30 days) | [CHECK] | [FROM DATA] | ? | MEDIUM |
| Q&A Activity | [CHECK] | [FROM DATA] | ? | LOW |
| GBP Description | [CHECK] | [FROM DATA] | ? | MEDIUM |
| Review Response Rate | [CHECK] | [FROM DATA] | ? | HIGH |
| Attributes | [CHECK] | [FROM DATA] | ? | LOW |
| Website Linked | {"YES" if website_url else "NO"} | YES | {"NO GAP" if website_url else "CRITICAL GAP"} | CRITICAL |

---

## Top 10 Action Items (Prioritized by Impact)

1. **Verify/fill in GBP data** - Open each [CHECK] field above manually on your Google Business Profile
2. **Fix primary category** - Ensure it matches what top competitors use
3. **Add missing secondary categories** - Mirror the most common ones from competitors
4. **Upload photos** - Aim to match or exceed the top competitor's photo count
5. **Complete services list** - Add every service competitors list that you also offer
6. **Write GBP description** - 750 chars with local keywords, unique value prop
7. **Start posting weekly** - Minimum 2x/week GBP updates (use gbp_content.py)
8. **Seed Q&A** - Add 10-15 questions with keyword-rich answers
9. **Respond to all reviews** - Use review templates (review_response_templates.md)
10. **Add all relevant attributes** - "Online estimates", "Women-owned", etc.

---

## Next Steps

1. Manually verify each [CHECK] field in your Google Business Profile dashboard
2. Re-run this audit after making changes to track improvement
3. Run `gbp_content.py` to generate 30 days of GBP posts
4. Run `llm_citation_check.py` to start tracking AI recommendations

*Report generated by Local SEO System v1.0*
"""

    # Write the report
    report_path = os.path.join(output_dir, "GBP-AUDIT-REPORT.md")
    write_file(report_path, report)

    print(f"\n{'='*50}")
    print(f"GBP Audit Complete!")
    print(f"Report saved to: {report_path}")
    print(f"Competitors analyzed: {len(competitor_data)}")
    print(f"{'='*50}")

    return f"GBP audit complete. {len(competitor_data)} competitors analyzed. Report at {report_path}"


# Auto-run if called with execute_code and config exists
cfg = load_config()
if cfg:
    run_audit(
        business_name=cfg.get("business_name", ""),
        service_type=cfg.get("service_type", ""),
        city=cfg.get("city", ""),
        state=cfg.get("state", ""),
        website_url=cfg.get("website_url", ""),
    )
else:
    print("No business config found. Create ~/local-seo/business-config.yaml first.")
    print("Or call run_audit() with parameters directly.")
