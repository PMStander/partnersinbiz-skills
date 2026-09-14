"""
Full Audit Runner — Master Orchestrator
Runs ALL phases of the Local SEO System in sequence.

Phase 1: GBP Competitor Audit
Phase 2: Lead Response System
Phase 3: LLM Citation Check
Phase 4: Keyword Gap Analysis
Phase 5: Monthly Report

Usage (via execute_code):
  exec(open(os.path.expanduser("~/.hermes/skills/marketing/local-seo-system/scripts/run_full_audit.py")).read())

Or call directly:
  from hermes_tools import execute_code
  run_full_audit()
"""

import os
import sys
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


def run_full_audit(phases=None):
    """
    Run the full local SEO audit system.
    
    phases: list of phase numbers to run [1,2,3,4,5]
            If None, runs all phases.
    """
    from hermes_tools import write_file, web_search

    cfg = load_config()
    if not cfg:
        return ("ERROR: No config found. Create ~/local-seo/business-config.yaml first.\n"
                "Use the template at ~/.hermes/skills/marketing/local-seo-system/templates/business-config.yaml")

    business_name = cfg.get("business_name", "")
    service_type = cfg.get("service_type", "")
    city = cfg.get("city", "")
    state = cfg.get("state", "")

    if not all([business_name, service_type, city]):
        return "ERROR: Config is incomplete. Need business.name, service_type, and city at minimum."

    if phases is None:
        phases = [1, 2, 3, 4, 5]

    output_dir = os.path.expanduser("~/local-seo")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "city-pages"), exist_ok=True)

    scripts_dir = os.path.expanduser("~/.hermes/skills/marketing/local-seo-system/scripts")
    now = datetime.now()

    results = []

    print("=" * 60)
    print(f"LOCAL SEO FULL AUDIT")
    print(f"Business: {business_name}")
    print(f"Service: {service_type}")
    print(f"Location: {city}, {state}")
    print(f"Phases: {phases}")
    print(f"Started: {now.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    # Phase 1: GBP Audit + Content
    if 1 in phases:
        print("\n" + "=" * 60)
        print("PHASE 1: Google Business Profile Audit & Content")
        print("=" * 60)
        try:
            # Run GBP audit
            gbp_audit_script = os.path.join(scripts_dir, "gbp_audit.py")
            if os.path.exists(gbp_audit_script):
                exec(open(gbp_audit_script).read())
                results.append(("Phase 1A: GBP Audit", "COMPLETE"))
            else:
                results.append(("Phase 1A: GBP Audit", "SCRIPT NOT FOUND"))

            # Run GBP content gen
            gbp_content_script = os.path.join(scripts_dir, "gbp_content.py")
            if os.path.exists(gbp_content_script):
                exec(open(gbp_content_script).read())
                results.append(("Phase 1B-D: GBP Content", "COMPLETE"))
            else:
                results.append(("Phase 1B-D: GBP Content", "SCRIPT NOT FOUND"))
        except Exception as e:
            results.append(("Phase 1", f"ERROR: {str(e)[:100]}"))

    # Phase 2: Lead Response
    if 2 in phases:
        print("\n" + "=" * 60)
        print("PHASE 2: Lead Response System")
        print("=" * 60)
        try:
            lead_script = os.path.join(scripts_dir, "lead_response.py")
            if os.path.exists(lead_script):
                exec(open(lead_script).read())
                results.append(("Phase 2: Lead Response", "COMPLETE"))
            else:
                results.append(("Phase 2: Lead Response", "SCRIPT NOT FOUND"))
        except Exception as e:
            results.append(("Phase 2", f"ERROR: {str(e)[:100]}"))

    # Phase 3: LLM Citation Check
    if 3 in phases:
        print("\n" + "=" * 60)
        print("PHASE 3: LLM Citation Engineering")
        print("=" * 60)
        try:
            llm_script = os.path.join(scripts_dir, "llm_citation_check.py")
            if os.path.exists(llm_script):
                exec(open(llm_script).read())
                results.append(("Phase 3: LLM Citations", "COMPLETE"))
            else:
                results.append(("Phase 3: LLM Citations", "SCRIPT NOT FOUND"))
        except Exception as e:
            results.append(("Phase 3", f"ERROR: {str(e)[:100]}"))

    # Phase 4: Keyword Gap
    if 4 in phases:
        print("\n" + "=" * 60)
        print("PHASE 4: Keyword Gap Analysis")
        print("=" * 60)
        try:
            kw_script = os.path.join(scripts_dir, "keyword_gap.py")
            if os.path.exists(kw_script):
                exec(open(kw_script).read())
                results.append(("Phase 4: Keyword Gap", "COMPLETE"))
            else:
                results.append(("Phase 4: Keyword Gap", "SCRIPT NOT FOUND"))
        except Exception as e:
            results.append(("Phase 4", f"ERROR: {str(e)[:100]}"))

    # Phase 5: Monthly Report
    if 5 in phases:
        print("\n" + "=" * 60)
        print("PHASE 5: Monthly Report")
        print("=" * 60)
        try:
            report_script = os.path.join(scripts_dir, "monthly_report.py")
            if os.path.exists(report_script):
                exec(open(report_script).read())
                results.append(("Phase 5: Monthly Report", "COMPLETE"))
            else:
                results.append(("Phase 5: Monthly Report", "SCRIPT NOT FOUND"))
        except Exception as e:
            results.append(("Phase 5", f"ERROR: {str(e)[:100]}"))

    # Final summary
    print("\n" + "=" * 60)
    print("FULL AUDIT COMPLETE")
    print("=" * 60)
    print()
    print("Results:")
    for phase, status in results:
        icon = "OK" if "COMPLETE" in status else "!!"
        print(f"  [{icon}] {phase}: {status}")
    print()
    print(f"Output directory: {output_dir}")
    print(f"Total time: {datetime.now().strftime('%H:%M:%S')}")
    print()

    # Write summary file
    summary = f"# Local SEO Audit Summary\n"
    summary += f"**Date:** {now.strftime('%Y-%m-%d %H:%M')}\n"
    summary += f"**Business:** {business_name}\n\n"
    summary += "| Phase | Status |\n"
    summary += "|-------|--------|\n"
    for phase, status in results:
        summary += f"| {phase} | {status} |\n"
    summary += f"\n*Run `run_monthly.py` next month for ongoing maintenance.*\n"

    write_file(os.path.join(output_dir, "AUDIT-SUMMARY.md"), summary)

    return f"Full audit complete. {len(results)} phases run. Output in {output_dir}/"


# Run it
run_full_audit()
