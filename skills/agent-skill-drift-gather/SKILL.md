---
name: agent-skill-drift-gather
description: >
  Partners in Biz agent skill-policy drift gatherer. Use when checking whether live AI employee
  profiles are actually configured with the current repo-backed skills, including the CEO
  no-dashboard gatherers, dynamic chat gatherers, CRM/social gatherers, and runtime policy manifest.
---

# Agent Skill Drift Gather — Partners in Biz

Use this skill to verify whether the live `agent_team` records match the current repo skill-policy manifest.

## Operating Rule

1. Verify the repo manifest and stored `agent_team` policy data exist.
2. Gather current stored `skillPolicy`, advertised `skills`, enabled state, and base URL state.
3. Compare each agent to `config/agent-skill-policy.json`.
4. Answer in dynamic Messages with a clear operational interpretation.
5. Create temp throw-away HTML only when a matrix helps inspection.

Do not create permanent dashboards or server Markdown reports.

## Safety

This skill is read-only by default. Do not:

- apply agent skill policies
- mutate `agent_team` records
- call the admin apply route
- change Hermes/VPS profile config or symlinks
- edit env vars/secrets
- restart services, merge, deploy, or unblock approval tasks

If policy apply or live sidecar sync is needed, report the approval gate and keep it blocked.

## Required Output Shape

- `Data checked`: manifest version, agent count, stored policy versions, and skill list coverage
- `What it means`: which agents are ready, stale, or missing CEO/chat gatherer skills
- `Next action`: safe-now evidence work and approval-needed apply/sync actions
- `Blocked gates`: release/task IDs or policy apply gaps
- `Safety readback`: what was not mutated

## Helper Script

From the `partnersinbiz-web` repo, run:

```bash
node .claude/skills/agent-skill-drift-gather/scripts/gather-agent-skill-drift.mjs --org pib-platform-owner --conversation CS0TqDu1FJGUK65jdq96 --html
```

The script reads `.env.local`, uses Firebase Admin, compares stored `agent_team` policy data to the repo manifest, prints JSON, and optionally writes a temp HTML matrix under `/tmp`.
