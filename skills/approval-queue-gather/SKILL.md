---
name: approval-queue-gather
description: >
  Partners in Biz CEO approval queue gatherer. Use when Peet needs to know what decisions
  are blocking growth, release, CRM, Marketing Studio, social recovery, outreach, or daily
  agent operations. Gathers blocked/awaiting tasks plus CRM/social/conversation counts,
  creates optional throw-away HTML, and returns data for dynamic Messages approval cards.
---

# Approval Queue Gather — Partners in Biz

Use this skill to turn scattered blocked tasks into one CEO-readable decision queue.

## Operating Rule

1. Verify approval data is stored.
2. Gather current blocked/awaiting tasks, conversation state, CRM counts, and social counts.
3. Classify the queue by release, Marketing Studio, CRM/sales, operations, and follow-ups.
4. Answer in dynamic Messages with approval cards.
5. Create temp throw-away HTML only when a matrix helps inspection.

Do not create a permanent dashboard or make Markdown the CEO-facing surface.

## Safety

Read-only by default. Do not:

- approve, unblock, move, close, or delete tasks
- merge, deploy, create PRs, edit env vars, or clean Hermes runs
- change CRM values/dates/owners/stages or send outreach
- submit, approve, schedule, publish, retry, or reconnect social posts/accounts
- spend money or create ad/billing artifacts

If action is needed, report the approval gate and reply template in Messages.

## Helper Script

From the `partnersinbiz-web` repo:

```bash
node .claude/skills/approval-queue-gather/scripts/gather-approval-queue.mjs --org pib-platform-owner --conversation CS0TqDu1FJGUK65jdq96 --html
```

The script reads `.env.local`, uses Firebase Admin, prints JSON, and writes temp HTML under `/tmp` only when `--html` is passed.
