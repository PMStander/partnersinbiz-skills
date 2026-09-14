---
name: ceo-on-demand-gather
description: >
  Partners in Biz CEO on-demand analysis workflow. Use this whenever Peet asks for a dashboard,
  growth command view, executive summary, "what should we do next", "analyze the CRM/Marketing
  Studio/agents", approval queue, daily operating queue, or any question that could be answered
  from stored PiB data. This skill enforces Peet's rule: verify data is stored, gather it with a
  reusable skill/script, analyze it, then answer in dynamic chat. Only create a temporary throw-away
  HTML artifact when it directly answers the question; never create a permanent dashboard by default.
---

# CEO On-Demand Gather — Partners in Biz

Use this skill to answer CEO-level business questions without building dashboard debt.

## Operating Rule

When you think "dashboard", stop and do this instead:

1. Verify the data needed for the question is actually stored.
2. Gather the relevant data through API/Firestore reads.
3. Analyze the current state.
4. Answer in the dynamic Messages chat with rich cards when possible.
5. Create a temp throw-away HTML file only when the question needs a visual table/matrix.

Do not create durable dashboard routes, server Markdown reports, scheduled reports, or permanent files unless Peet explicitly asks for them.

## Safety

Default mode is read-only. Do not perform these actions from this skill:

- submit, approve, schedule, publish, retry, or reconnect social posts/accounts
- change CRM deal values, dates, owners, stages, sharing, or visibility
- send outreach, quotes, invoices, documents, or client-visible messages
- create ad campaigns, budgets, pixels, conversions, audiences, or spend
- edit env vars/secrets, deploy production, merge release branches, or restart services
- bulk-close review tasks, delete records, or perform destructive cleanup

If analysis shows one of those actions is needed, create or update an approval-gated task and report it in dynamic chat.

## Data Sources To Check

For org `pib-platform-owner`, gather only what the question needs:

- dynamic Messages conversation: `CS0TqDu1FJGUK65jdq96`
- CRM: contacts, companies, deals, activities, documents, quotes, invoices, forms
- Marketing Studio: social posts, accounts, media, campaigns, queues
- Agents/tasks: standalone `tasks`, project tasks, `hermes_runs`, notifications, inbox items
- Organic/paid growth: SEO records, content rows, ad connections/campaigns/budgets/pixels/conversions
- Approval gates: blocked/awaiting-input tasks plus pending approval documents/social records

Prefer production API reads when the route exists. Fall back to direct Firestore/admin reads only when the production route is missing or blocked and the task is internal/admin-only.

## Required Output Shape

Every answer should include:

- `Data checked`: exact sources and counts
- `What it means`: concise executive interpretation
- `Next action`: one or more safe actions, each marked `safe now` or `needs approval`
- `Blocked gates`: task IDs or route gaps that prevent further action
- `Safety readback`: what was not mutated

For dynamic chat, use rich parts such as `status_card`, `approval_card`, `decision_card`, or `analysis_card`.

## Throw-Away HTML

Only create temp HTML under `/tmp` when it makes the answer easier to inspect. Name it with the task/question id, for example:

`/tmp/pib-ceo-coverage-snapshot-<taskId>.html`

The HTML is an artifact, not the primary user surface. Summarize the result in Messages and include the temp path only for agent verification.

## Helper Script

From the `partnersinbiz-web` repo, run:

```bash
node .claude/skills/ceo-on-demand-gather/scripts/gather-ceo-snapshot.mjs --org pib-platform-owner --conversation CS0TqDu1FJGUK65jdq96 --html
```

The script is read-only. It uses `.env.local` in the current repo for Firebase admin credentials and writes a temp HTML snapshot when `--html` is passed.

Use the script output as evidence, then write the executive answer into dynamic Messages.
