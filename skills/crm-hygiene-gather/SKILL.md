---
name: crm-hygiene-gather
description: >
  Partners in Biz CRM hygiene and sales-readiness gatherer. Use when Peet asks whether the CRM is
  top notch, when analyzing contacts/companies/deals/pipeline quality, duplicate contacts, missing
  owners/company links, proposal deal values or expected close dates, sales approval gates, or any
  CRM question that should be answered on-demand in dynamic chat instead of a dashboard.
---

# CRM Hygiene Gather — Partners in Biz

Use this skill to verify CRM quality from stored data without mutating CRM records.

## Operating Rule

1. Verify the needed CRM data exists in Firestore/API.
2. Gather contacts, companies, deals, and approval-gated sales tasks with the helper script.
3. Analyze the highest-value gaps for CEO action.
4. Answer in dynamic Messages, not server Markdown.
5. Create temp throw-away HTML only when the table helps inspect the answer.

## Safety

This skill is read-only by default. Do not:

- change deal values, stages, expected close dates, owners, or visibility
- merge contacts/companies
- send outreach, WhatsApps, email, quotes, proposals, invoices, or documents
- change client-visible sharing
- bulk-close tasks or approvals

If a CRM change is needed, write an approval card in Messages or create/update an approval-gated task.

## Required Output Shape

- `Data checked`: exact CRM counts and key query scope
- `What it means`: concise operational interpretation
- `Next action`: safe-now cleanup/gather actions and approval-needed actions
- `Blocked gates`: task IDs, deal IDs, or missing data blocking progress
- `Safety readback`: what was not mutated

## Helper Script

From the `partnersinbiz-web` repo, run:

```bash
node .claude/skills/crm-hygiene-gather/scripts/gather-crm-hygiene.mjs --org pib-platform-owner --html
```

The script reads `.env.local` from the current repo, uses Firebase Admin, prints JSON, and writes an optional temp HTML snapshot under `/tmp`.
