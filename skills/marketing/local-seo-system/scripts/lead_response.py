"""
Lead Response System Generator
Phase 2 of the Local SEO System.

Generates:
- SMS auto-reply for missed calls
- Inquiry response templates (5 types)
- Lead qualification checklist
- Follow-up sequence (1hr, 24hr, 3d, 7d)
- FAQ library for lead pre-qualification (20 Q&As)

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


def run_lead_response(business_name=None, service_type=None, city=None, state=None,
                      phone=None, services=None, owner_name=None, output_dir=None):
    """Generate the complete lead response playbook and FAQ library."""
    from hermes_tools import web_search, write_file

    cfg = load_config()
    business_name = business_name or (cfg.get("business_name", ""))
    service_type = service_type or (cfg.get("service_type", "") if cfg else "")
    city = city or (cfg.get("city", "") if cfg else "")
    state = state or (cfg.get("state", "") if cfg else "")
    phone = phone or (cfg.get("phone", "") if cfg else "[PHONE]")
    services = services or (cfg.get("services", []) if cfg else [])
    owner_name = owner_name or (cfg.get("owner_name", "") if cfg else "us")
    output_dir = output_dir or os.path.expanduser("~/local-seo")
    os.makedirs(output_dir, exist_ok=True)

    if not all([business_name, service_type, city]):
        return "ERROR: Need business_name, service_type, and city."

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Research common lead scenarios for this service type
    lead_queries = [
        f"{service_type} most common customer questions before hiring",
        f"how to respond to {service_type} leads fast",
        f"{service_type} lead follow up best practices",
    ]
    lead_context = ""
    for q in lead_queries:
        r = web_search(q, limit=2)
        if r and "data" in r and "web" in r["data"]:
            for result in r["data"]["web"][:1]:
                lead_context += f"- {result.get('title', '')}: {result.get('description', '')}\n"

    # Research common FAQs
    faq_queries = [
        f"{service_type} {city} frequently asked questions",
        f"{service_type} cost pricing questions {city}",
        f"{service_type} what to ask before hiring",
    ]
    faq_context = ""
    for q in faq_queries:
        r = web_search(q, limit=3)
        if r and "data" in r and "web" in r["data"]:
            for result in r["data"]["web"][:2]:
                faq_context += f"- {result.get('title', '')}: {result.get('description', '')}\n"

    # Build the playbook
    services_str = ", ".join(services) if services else "[your main services]"

    playbook = f"""# Lead Response Playbook
**Generated:** {now}
**Business:** {business_name}
**Service:** {service_type}
**Location:** {city}, {state}
**Phone:** {phone}

---

## 1. SMS Auto-Reply for Missed Calls

### Template 1 - During Business Hours (8am-6pm)
> Hi! This is {owner_name} from {business_name}. Sorry I missed your call — I'm probably on a job site. I'll call you back within 30 minutes. If it's urgent, text me the details and I'll respond right away. Thanks!

### Template 2 - After Hours (6pm-8am)
> Thanks for calling {business_name}! We're off the clock for the evening but {owner_name} will call you first thing tomorrow morning. If this is an emergency, text "URGENT" and we'll get back to you ASAP.

### Template 3 - Weekend
> Hey, this is {business_name}. We're enjoying the weekend but haven't forgotten about you! {owner_name} will reach out Monday morning. Need it sooner? Text us and we'll do our best.

---

## 2. Inquiry Response Templates

### Template A: Pricing Questions
> "How much does [service] cost?"

> Great question! Pricing for {service_type} work in {city} depends on a few things — the scope of the job, materials needed, and timing. Here's what I can tell you:
>
> [SERVICE-SPECIFIC RANGE — e.g., "A standard water heater install typically runs $X-$Y in our area."]
>
> The best way to get an accurate number is a quick phone call or on-site estimate. No charge, no pressure. When works for you?
>
> — {owner_name}, {business_name}

### Template B: Availability Questions
> "When can you come out?"

> Thanks for reaching out! We typically schedule within [TIMEFRAME — e.g., 24-48 hours] for standard jobs and same-day for emergencies. Tomorrow at [TIME] or [TIME] is open right now — does either work?
>
> If you can share a bit about what's going on, I can make sure we bring the right tools and parts.
>
> — {owner_name}, {business_name}

### Template C: Scope Questions ("Do you do X?")
> "Do you handle [specific service]?"

> Yes! [Or: "That's actually one of our specialties!"] We handle [SERVICE] all over {city} and [SURROUNDING AREAS].
>
> Here's what that typically looks like:
> 1. [Step 1 — e.g., "We come out, assess the situation, and give you a clear quote"]
> 2. [Step 2 — e.g., "If you approve, we get it done same-day or schedule a convenient time"]
> 3. [Step 3 — e.g., "We clean up and make sure you're 100% satisfied"]
>
> Want to tell me more about what you need?
>
> — {owner_name}, {business_name}

### Template D: Emergency Requests
> "I need someone NOW — can you come today?"

> Absolutely. We prioritize emergencies. I can be at your location in [TIMEFRAME — e.g., 60-90 minutes].
>
> Can you text me:
> 1. Your address
> 2. A brief description of what's happening
> 3. Is anyone at the location now?
>
> I'll head your way as soon as I have those details.
>
> — {owner_name}, {business_name}

### Template E: "Just Looking for a Quote"
> "Can I get a quote for [service]?"

> Of course! Happy to help. Quotes are always free — that's just how we do things.
>
> To give you the most accurate number, it helps to know:
> - [QUESTION 1 — e.g., "What's the square footage of the area?"]
> - [QUESTION 2 — e.g., "When was the last time it was serviced?"]
> - [QUESTION 3 — e.g., "Any specific issues you've noticed?"]
>
> You can reply here or call us at {phone}. Either way, no obligation.
>
> — {owner_name}, {business_name}

---

## 3. Lead Qualification Checklist

Before booking an estimate, get answers to these 6 questions:

| # | Question | Why It Matters |
|---|---------|---------------|
| 1 | **Where are you located?** | Confirms they're in your service area ({city} and surrounding areas) |
| 2 | **What exactly needs to be done?** | Determines scope — is this a 1-hour fix or a 3-day project? |
| 3 | **How soon do you need this?** | Urgency = pricing flexibility and scheduling priority |
| 4 | **Have you gotten other quotes?** | If yes, you know the competitive landscape. If no, you're first = advantage |
| 5 | **Who's making the decision?** | Make sure you're talking to the decision-maker, not just a researcher |
| 6 | **What's your budget range?** | Don't ask directly — instead: "So we can recommend the best solution, what range works for you?" |

### Scoring
- **4+ answers = Hot lead**: Book the estimate ASAP
- **3 answers = Warm lead**: Follow up within 2 hours for missing info
- **2 or fewer = Cool lead**: Nurture with follow-up sequence

---

## 4. Follow-Up Sequence

### Touch 1: 1 Hour After First Contact
**If they inquired but didn't book:**

> Hey [NAME], this is {owner_name} from {business_name}. Just wanted to follow up — do you have any questions about what we discussed? Happy to help figure out the best approach for your situation. No rush, just wanted you to have my direct line.

### Touch 2: 24 Hours After First Contact
**If no response to Touch 1:**

> Hi [NAME], checking in again from {business_name}. I know things get busy! Just wanted to let you know we still have availability this [WEEK/MONTH] if you're still thinking about getting that [SERVICE] taken care of. Here if you need us.

### Touch 3: 3 Days After First Contact
**If still no response:**

> Hey [NAME], {owner_name} here. Last check-in — promise! If the timing isn't right, no worries at all. We're here whenever you're ready. In the meantime, here's a quick tip for [SERVICE-RELATED TIP — e.g., "keeping your water heater running efficiently"]: [TIP]. Hope that helps!

### Touch 4: 7 Days After First Contact (Final)
**If still no response:**

> Hi [NAME], I'll leave you be after this! Just wanted to say thanks for considering {business_name} for your {service_type} needs. If anything comes up in the future, we're just a call or text away at {phone}. Hope everything's going well!

---

## Research Context (for content generation)

### Industry Lead Response Best Practices:
{lead_context if lead_context else "Standard lead response best practices applied."}

---

*Generated by Local SEO System v1.0*
"""

    playbook_path = os.path.join(output_dir, "LEAD-RESPONSE-PLAYBOOK.md")
    write_file(playbook_path, playbook)

    # Build FAQ Library
    faq_library = f"""# FAQ Library
**Generated:** {now}
**Business:** {business_name}
**Service:** {service_type}
**Location:** {city}, {state}

---

## Instructions
Generate 20 FAQs that real customers ask before hiring a {service_type} in {city}.
Each answer: 60-120 words, honest, local keyword included, ends with next-step invitation.

### Research Context:
{faq_context if faq_context else "Standard FAQ topics for " + service_type}

### FAQ Categories (4 questions each):
1. **Pricing/Cost** (4 questions)
2. **Timing/Scheduling** (4 questions)
3. **Scope/Services** (4 questions)
4. **Trust/Qualifications** (4 questions)
5. **Process/What to Expect** (4 questions)

### Format:
| # | Category | Question | Answer (60-120 words) | Keyword Included |

Generate all 20 rows.

---

*Generated by Local SEO System v1.0*
"""

    faq_path = os.path.join(output_dir, "FAQ-LIBRARY.md")
    write_file(faq_path, faq_library)

    print(f"\n{'='*50}")
    print(f"Lead Response System generated!")
    print(f"Playbook: {playbook_path}")
    print(f"FAQ Library: {faq_path}")
    print(f"{'='*50}")

    return "Lead response playbook and FAQ library generated."


# Auto-run
cfg = load_config()
if cfg:
    run_lead_response(
        business_name=cfg.get("business_name", ""),
        service_type=cfg.get("service_type", ""),
        city=cfg.get("city", ""),
        state=cfg.get("state", ""),
        phone=cfg.get("phone", ""),
        services=cfg.get("services", []),
        owner_name=cfg.get("owner_name", ""),
    )
else:
    print("No config found. Create ~/local-seo/business-config.yaml first.")
