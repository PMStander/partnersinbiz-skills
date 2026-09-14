---
name: agent-runtime-gather
description: >
  Partners in Biz AI employee/runtime health gatherer. Use when checking whether agents are
  world-class and ready for daily operations, including agent_team config, enabled agents, skill
  counts, task load by agent, blocked approval tasks, Hermes run ledger status, stuck started runs,
  and dynamic chat operating readiness.
---

# Agent Runtime Gather — Partners in Biz

Use this skill to assess whether the PiB AI employees can operate reliably day to day.

## Operating Rule

1. Verify agent/team, task, Hermes run, and conversation data exists.
2. Gather current state through Firestore/API reads.
3. Classify readiness: enabled agents, task throughput, approval bottlenecks, run-ledger health.
4. Answer in dynamic Messages with status and approval cards.
5. Create temp throw-away HTML only when useful for inspection.

## Safety

Read-only by default. Do not:

- mutate agent configs, skills, profile policies, API keys, or env vars
- clean, finalize, or delete Hermes run rows
- bulk-close, unblock, or requeue tasks
- deploy, merge, or restart services

If a release, cleanup, policy apply, or task unblock is needed, use an approval card and keep the gate blocked.

## Required Output Shape

- `Data checked`: agents, tasks, Hermes runs, conversation
- `What it means`: operational interpretation
- `Next action`: safe-now evidence work and approval-needed actions
- `Blocked gates`: task IDs and release/run-ledger blockers
- `Safety readback`: what was not mutated

## Helper Script

From the `partnersinbiz-web` repo, run:

```bash
node .claude/skills/agent-runtime-gather/scripts/gather-agent-runtime.mjs --org pib-platform-owner --conversation CS0TqDu1FJGUK65jdq96 --html
```

The script reads `.env.local` from the current repo, uses Firebase Admin, prints JSON, and optionally writes a temp HTML snapshot under `/tmp`.
