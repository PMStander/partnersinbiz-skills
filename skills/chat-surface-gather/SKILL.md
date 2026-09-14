---
name: chat-surface-gather
description: >
  Partners in Biz dynamic chat surface gatherer. Use when Peet or an agent needs to verify
  that CEO-facing agent output is stored in dynamic Messages, that the focused conversation
  route is release-ready, and that chat evidence is not trapped in Markdown/server files.
---

# Chat Surface Gather — Partners in Biz

Use this skill to verify the operational chat surface without creating dashboard debt.

## Operating Rule

1. Verify the target conversation and latest message are stored in Firestore.
2. Gather current conversation counts, latest messages, release gate evidence, and production route probes.
3. Identify whether CEO-facing output is readable from dynamic Messages or blocked by a route/release gap.
4. Answer in dynamic Messages with status or approval cards.
5. Create temp throw-away HTML only when a compact route/message matrix helps inspection.

Do not create permanent dashboard routes or server Markdown reports.

## Safety

Read-only by default. Do not:

- send chat replies through the public UI
- dispatch Hermes runs
- approve or unblock release gates
- merge, deploy, create PRs, or edit env vars
- change CRM records, social posts, accounts, outreach, spend, or secrets
- delete or clean up conversation records

If action is needed, report the release gate or task ID in dynamic Messages.

## Helper Script

From the `partnersinbiz-web` repo:

```bash
node .claude/skills/chat-surface-gather/scripts/gather-chat-surface.mjs --org pib-platform-owner --conversation CS0TqDu1FJGUK65jdq96 --html
```

The script reads `.env.local`, uses Firebase Admin for stored chat data, probes selected production routes without credentials, prints JSON, and writes temp HTML under `/tmp` only when `--html` is passed.
