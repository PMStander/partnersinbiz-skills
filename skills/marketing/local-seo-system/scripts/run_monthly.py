"""
Monthly Maintenance Runner
Runs the recurring monthly tasks for ongoing SEO management.

Runs:
- LLM Citation Check (are we showing up in AI recommendations?)
- Keyword Gap Analysis (any new keyword opportunities?)
- Monthly Report (comprehensive status update)

Usage via Hermes cron:
  Load skill "local-seo-system", then run this script via execute_code.

Or manually:
  exec(open(os.path.expanduser("~/.hermes/skills/marketing/local-seo-system/scripts/run_monthly.py")).read())
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


def run_monthly():
    """Run monthly maintenance tasks."""
    from hermes_tools import write_file

    cfg = load_config()
    if not cfg:
        return "ERROR: No config at ~/local-seo/business-config.yaml. Can't run monthly tasks."

    business_name = cfg.get("business_name", "")
    service_type = cfg.get("service_type", "")
    city = cfg.get("city", "")
    state = cfg.get("state", "")

    if not all([business_name, service_type, city]):
        return "ERROR: Config incomplete."

    scripts_dir = os.path.expanduser("~/.hermes/skills/marketing/local-seo-system/scripts")
    output_dir = os.path.expanduser("~/local-seo")
    now = datetime.now()

    print("=" * 60)
    print(f"MONTHLY SEO MAINTENANCE: {now.strftime('%B %Y')}")
    print(f"Business: {business_name} | {city}, {state}")
    print("=" * 60)

    results = []

    # Task 1: LLM Citation Check
    print("\n--- Task 1: LLM Citation Check ---")
    try:
        llm_script = os.path.join(scripts_dir, "llm_citation_check.py")
        if os.path.exists(llm_script):
            exec(open(llm_script).read())
            results.append(("LLM Citation Check", "DONE"))
        else:
            results.append(("LLM Citation Check", "SKIPPED - script not found"))
    except Exception as e:
        results.append(("LLM Citation Check", f"ERROR: {str(e)[:80]}"))

    # Task 2: Keyword Gap
    print("\n--- Task 2: Keyword Gap Analysis ---")
    try:
        kw_script = os.path.join(scripts_dir, "keyword_gap.py")
        if os.path.exists(kw_script):
            exec(open(kw_script).read())
            results.append(("Keyword Gap Analysis", "DONE"))
        else:
            results.append(("Keyword Gap Analysis", "SKIPPED - script not found"))
    except Exception as e:
        results.append(("Keyword Gap Analysis", f"ERROR: {str(e)[:80]}"))

    # Task 3: Monthly Report
    print("\n--- Task 3: Monthly Report ---")
    try:
        report_script = os.path.join(scripts_dir, "monthly_report.py")
        if os.path.exists(report_script):
            exec(open(report_script).read())
            results.append(("Monthly Report", "DONE"))
        else:
            results.append(("Monthly Report", "SKIPPED - script not found"))
    except Exception as e:
        results.append(("Monthly Report", f"ERROR: {str(e)[:80]}"))

    # Summary
    print("\n" + "=" * 60)
    print("MONTHLY MAINTENANCE COMPLETE")
    print("=" * 60)
    for task, status in results:
        icon = "OK" if "DONE" in status else "!!"
        print(f"  [{icon}] {task}: {status}")

    print(f"\nReports saved to: {output_dir}/reports/")
    print(f"Next run: schedule for same day next month")

    return f"Monthly maintenance done. {sum(1 for _, s in results if 'DONE' in s)}/{len(results)} tasks completed."


# Run
run_monthly()
