"""
GBP Content Generator Script
Phase 1B-1D of the Local SEO System.

Generates:
- 30-day GBP post calendar
- Service descriptions
- Q&A pairs
- Review response templates
- Category recommendations

This script gathers competitor data via web search, then the AGENT
generates the actual content using LLM reasoning (the script provides
the structure and data; the agent fills in the creative content).

Usage: Run via execute_code after gbp_audit.py has completed.
"""

import os
import json
from datetime import datetime, timedelta

def load_config():
    config_paths = [
        os.path.expanduser("~/local-seo/business-config.yaml"),
    ]
    for p in config_paths:
        if os.path.exists(p):
            raw = open(p).read()
            cfg = {}
            current_section = None
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


def run_content_gen(business_name=None, service_type=None, city=None, state=None,
                    services=None, owner_name=None, tone=None, output_dir=None):
    """
    Generate all GBP content.
    Returns structured data that the agent will use to produce final content.
    """
    from hermes_tools import web_search, web_extract, write_file

    cfg = load_config()

    business_name = business_name or (cfg.get("business_name", ""))
    service_type = service_type or (cfg.get("service_type", "") if cfg else "")
    city = city or (cfg.get("city", "") if cfg else "")
    state = state or (cfg.get("state", "") if cfg else "")
    services = services or (cfg.get("services", []) if cfg else [])
    owner_name = owner_name or (cfg.get("owner_name", "") if cfg else "the team")
    tone = tone or (cfg.get("tone", "friendly_local_expert") if cfg else "friendly_local_expert")
    output_dir = output_dir or os.path.expanduser("~/local-seo")
    os.makedirs(output_dir, exist_ok=True)

    if not all([business_name, service_type, city]):
        return "ERROR: Need business_name, service_type, and city."

    now = datetime.now()
    current_month = now.strftime("%B")
    current_season = _get_season(now.month)
    start_date = now + timedelta(days=1)

    print(f"=== GBP Content Generator ===")
    print(f"Business: {business_name}")
    print(f"Generating content for {current_month} {now.year}...\n")

    # Gather seasonal/event data for the city
    seasonal_query = f"{city} {state} {current_month} {current_season} events weather"
    seasonal_data = web_search(seasonal_query, limit=3)
    seasonal_context = ""
    if seasonal_data and "data" in seasonal_data and "web" in seasonal_data["data"]:
        for r in seasonal_data["data"]["web"][:2]:
            seasonal_context += f"- {r.get('title', '')}: {r.get('description', '')}\n"

    # Gather competitor GBP post ideas
    comp_post_query = f"{service_type} {city} google business profile posts updates"
    comp_data = web_search(comp_post_query, limit=3)

    # Gather common questions for the service type
    faq_query = f"{service_type} {city} common questions before hiring"
    faq_search = web_search(faq_query, limit=5)

    # Build the master content prompt for the agent
    # This is what the agent will use to generate the actual content

    services_str = "\n".join([f"  - {s}" for s in services]) if services else "  - [List your services]"

    content_kit = f"""# GBP Content Kit
**Generated:** {now.strftime("%Y-%m-%d %H:%M")}
**Business:** {business_name}
**Service:** {service_type}
**Location:** {city}, {state}
**Month:** {current_month} ({current_season})
**Tone:** {tone}

---

## PART 1: 30-Day GBP Post Calendar

**Posting starts:** {start_date.strftime("%A, %B %d, %Y")}

### Instructions for Content Generation
Generate 30 GBP posts following this mix:
- 10 service highlight posts (one for each major service)
- 8 customer success stories (use [CUSTOMER NAME], [JOB DETAILS] placeholders)
- 6 seasonal/timely posts for {current_month} in {city}
- 4 FAQ-style posts
- 2 special offer posts

### Seasonal Context for {city}:
{seasonal_context if seasonal_context else "General seasonal content appropriate for " + current_month}

### Post Format
| Day | Date | Post Type | Headline | Body (150-300 chars) | Keyword Targeted | CTA | Suggested Photo |

Generate all 30 rows.

---

## PART 2: Service Descriptions

### Services to Describe:
{services_str}

### Instructions
For each service, write a description that is:
- 750-1,000 characters
- Includes 2-3 local keywords naturally ("{service_type} in {city}", "{city} {service}", etc.)
- Structure: Problem → Approach → What makes {business_name} different
- References {city} or local neighborhoods at least once

---

## PART 3: Q&A Pairs (15 total)

### Instructions
Generate 15 Q&A pairs that real customers ask before hiring a {service_type} in {city}.

Mix these question types:
- 3 pricing/cost questions
- 3 timing/scheduling questions
- 3 scope questions ("do you handle X?")
- 3 trust/qualification questions
- 3 process questions ("what happens when...")

Each answer should:
- Be 60-120 words
- Include a local keyword naturally
- Be honest and helpful
- Subtly reinforce why {business_name} is the right choice

---

## PART 4: Review Response Templates

### Instructions
Create templates for responding to Google reviews:

**5-Star Review Templates (5 variations):**
- Short & warm (2 sentences)
- Medium with service mention (3-4 sentences)
- Long with community reference (4-5 sentences, mentions {city})
- Grateful with future invitation (3-4 sentences)
- Personal from {owner_name} (3 sentences, first person)

**4-Star Review Templates (3 variations):**
- Thank + acknowledge mostly positive
- Thank + invite specific feedback
- Thank + mention improvement commitment

**3-Star-or-Below Templates (5 variations):**
- Professional de-escalation (no defensiveness)
- Empathetic acknowledgment (3-4 sentences)
- Solution-oriented (offer to make it right)
- Facts-based response (address specific issues mentioned)
- Graceful + offline invite (move conversation to private channel)

**Service-Specific Templates (3 total):**
- One for each of the top 3 services listed above

Every template must:
- Include [BRACKETS] for personalizable parts
- Reference {city} or a local area naturally
- Sound human, not corporate
- End warmly

---

## PART 5: Category Recommendations

### Instructions
Based on what top-ranking {service_type} competitors in {city} use, recommend:

1. **Primary Category** (best match for search intent - the single most important GBP decision)
2. **5-9 Secondary Categories** (based on competitor analysis)
3. For each category, explain WHY it matters for local ranking

Also recommend which GBP Attributes to enable:
- Service attributes (Online estimates, Onsite services, etc.)
- Business attributes (Women-owned, Veteran-owned, etc.)
- Access attributes (Wheelchair accessible, etc.)

---

## Part 6: GBP Bio/Description

Write a GBP description (max 750 characters) that:
- Opens with what {business_name} does and where
- Highlights 2-3 key differentiators
- Includes primary local keyword
- Ends with a CTA
- Reads naturally, not stuffed

---

*Content kit prepared by Local SEO System v1.0*
*The agent should now generate all content sections above.*
"""

    # Write the content kit
    kit_path = os.path.join(output_dir, "GBP-CONTENT-KIT.md")
    write_file(kit_path, content_kit)

    # Generate the 30-day post calendar template
    post_calendar = f"# 30-Day GBP Post Calendar\n"
    post_calendar += f"**Business:** {business_name}\n"
    post_calendar += f"**Start Date:** {start_date.strftime('%A, %B %d, %Y')}\n"
    post_calendar += f"**Month:** {current_month}\n\n"
    post_calendar += "| Day | Date | Post Type | Headline | Body | Keyword | CTA | Photo |\n"
    post_calendar += "|-----|------|-----------|----------|------|---------|-----|-------|\n"

    post_types = (
        ["service"] * 10 +
        ["customer_success"] * 8 +
        ["seasonal"] * 6 +
        ["faq"] * 4 +
        ["offer"] * 2
    )

    for i, ptype in enumerate(post_types):
        date = (start_date + timedelta(days=i)).strftime("%b %d")
        post_calendar += f"| {i+1} | {date} | {ptype} | [HEADLINE] | [BODY] | [KEYWORD] | [CTA] | [PHOTO] |\n"

    calendar_path = os.path.join(output_dir, "GBP-POST-CALENDAR.md")
    write_file(calendar_path, post_calendar)

    print(f"\n{'='*50}")
    print(f"GBP Content Kit generated!")
    print(f"Content kit: {kit_path}")
    print(f"Post calendar: {calendar_path}")
    print(f"\nNEXT: The agent should now fill in all [PLACEHOLDERS]")
    print(f"with actual content using the instructions in the kit.")
    print(f"{'='*50}")

    return f"Content kit ready at {kit_path}. Agent should generate content from the instructions."


def _get_season(month):
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"


# Auto-run if config exists
cfg = load_config()
if cfg:
    run_content_gen(
        business_name=cfg.get("business_name", ""),
        service_type=cfg.get("service_type", ""),
        city=cfg.get("city", ""),
        state=cfg.get("state", ""),
        services=cfg.get("services", []),
        owner_name=cfg.get("owner_name", ""),
        tone=cfg.get("tone", ""),
    )
else:
    print("No business config found. Create ~/local-seo/business-config.yaml first.")
