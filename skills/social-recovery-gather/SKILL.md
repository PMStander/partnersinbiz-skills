---
name: social-recovery-gather
description: >
  Partners in Biz Marketing Studio failed-post and campaign-readiness gatherer. Use when analyzing
  failed social posts, reconnect/retry blockers, draft campaign readiness, social account health,
  Marketing Studio activation gates, or when Peet asks what can safely be used from marketing
  without publishing or scheduling yet.
---

# Social Recovery Gather — Partners in Biz

Use this skill to classify Marketing Studio recovery work without triggering external actions.

## Operating Rule

1. Verify social posts, accounts, media, and campaign state are stored.
2. Gather failures and campaign readiness through Firestore/API reads.
3. Classify blockers by account, auth, media, content, and approval.
4. Answer in dynamic Messages with approval cards.
5. Create temp throw-away HTML only when useful for inspection.

## Safety

Read-only by default. Do not:

- submit, approve, schedule, publish, retry, or reconnect posts/accounts
- change provider credentials, tokens, env vars, or app scopes
- delete, cancel, or bulk-edit posts
- mutate campaign timing or approval state
- spend money or create ads

If retry/reconnect/schedule/publish is needed, produce an approval card and keep the gate blocked.

## Required Output Shape

- `Data checked`: post/account/media counts and campaign IDs
- `What it means`: recovery classification and activation readiness
- `Next action`: safe-now actions and approval-needed actions
- `Blocked gates`: task IDs, account IDs, or provider issues
- `Safety readback`: what was not mutated

## Helper Script

From the `partnersinbiz-web` repo, run:

```bash
node .claude/skills/social-recovery-gather/scripts/gather-social-recovery.mjs --org pib-platform-owner --campaign pib-daily-growth-decisions-20260701-0905 --html
```

The script reads `.env.local` from the current repo, uses Firebase Admin, prints JSON, and optionally writes a temp HTML snapshot under `/tmp`.
