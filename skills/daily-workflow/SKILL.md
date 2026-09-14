---
name: daily-workflow
description: Start and end work sessions safely from natural language. Use whenever a user says “start day”, “start the day”, “begin work”, “end day”, “end the day”, “close out”, or asks to wrap up the current work session. Resolves live workspace context, syncs code conservatively, reads and persists durable context, verifies work, and manages only session-owned development processes.
version: 1.2.0
author: Partners in Biz
license: MIT
metadata:
  hermes:
    tags: [partnersinbiz, daily-workflow, start-day, end-day, session-closeout]
    triggers: ["start day", "start the day", "begin work", "end day", "end the day", "close out", "wrap up"]
---

# Daily Workflow

Recognize ordinary start-of-day and end-of-day language without requiring the user to name this skill. Apply the workflow to the active workspace and authenticated human only.

## Non-negotiable safety

- Read the nearest workspace instructions and manifest before acting: `AGENTS.md`, `CLAUDE.md`, and `.pib-workspace.json` when present.
- Resolve paths, organisation, project, agent domain, branch rules, and runtime target from live context. Do not rely on a hardcoded client registry or machine-specific home path.
- Keep organisations and user conversations isolated. Never infer permission to enter another client workspace.
- Inspect git status before pull, commit, or push. Never force-pull, force-push, reset, discard, or overwrite local work.
- Never stage every file blindly. Review the intended paths and exclude secrets, environment files, dependencies, generated output, and unrelated concurrent work.
- Never delete dependencies, build output, caches, media, workspace files, or source code as part of routine closeout.
- Do not reorganise files unless the user requested it or the workspace contract clearly requires it.
- Public publishing, client-visible messages, production deployment, paid spend, finance changes, secret/config changes, and destructive actions still require their normal explicit approval gates.
- Only stop development servers started during the current session. Never kill an unrelated process just because it uses the expected port.

## Resolve the active workspace

Use this order:

1. Runtime-injected workspace, organisation, project, user, and linked-device context.
2. Current working directory and nearest `AGENTS.md`, `CLAUDE.md`, and `.pib-workspace.json`.
3. Active Hermes profile identity and configured working directory.
4. The workspace manifest’s `agentDomain`, `localAgentDomainPath`, or runtime-matching domain path.
5. Ask one focused question only if the workspace or organisation remains genuinely ambiguous.

For Partners in Biz parent-workspace work, use org `pib-platform-owner` and the `partners` agent domain. For client work, require the resolved client org and domain before client-scoped reads or writes.

## Start-day workflow

When the user asks to start the day or begin work:

1. Read workspace instructions and manifest.
2. Read context in this order when available:
   - `wiki/hot.md` for immediate state;
   - `index.md` for discoverability;
   - the most recent dated log under `logs/`;
   - the active Projects/Kanban record when a project or task is in scope.
3. Inspect repository state with `git status --short --branch`.
4. Follow the repository’s own sync policy:
   - if clean, pull with the exact safe command required by that repo;
   - if dirty and the repo requires checkpoint-before-sync, checkpoint only after reviewing the diff, then rebase/pull as instructed;
   - otherwise preserve the dirty work and report the blocker;
   - never invent a branch policy or work on a production-only branch for ordinary changes.
5. Give a concise readiness update:
   - active workspace/domain and branch;
   - last meaningful session state;
   - open task or blocker context;
   - two or three grounded next actions.
6. Start a development server only when the user’s request and project instructions make that useful:
   - inspect package scripts and lockfiles first;
   - install dependencies only when required;
   - run long-lived servers in a tracked background process;
   - verify readiness through logs plus a local health or browser check;
   - report the verified URL.
7. End with a clear ready state. Do not claim the workspace is synced, a server is ready, or a task is unblocked without tool evidence.

## End-day workflow

When the user says “end day”, “end the day”, “close out”, “wrap up”, or equivalent:

1. Summarise the current session from the conversation and tool evidence. Use session history lookup when needed.
2. Re-read the active task/project record if one exists. Keep its status, blockers, evidence, and artifact links current.
3. Verify changed work with the smallest meaningful tests, lint, typecheck, build, or runtime check required by the repository. Record exact failures instead of hiding them.
4. Inspect git status and the intended diff.
5. Commit and push only when the user explicitly requested it or the workspace/repository instructions require closeout delivery:
   - obey the allowed working branch and remote;
   - stage only reviewed task files;
   - keep unrelated concurrent work out of the commit;
   - never include secrets, environment files, dependencies, or generated build output;
   - never promote to production without explicit production approval;
   - verify the resulting commit and remote branch.
6. Persist durable knowledge in the runtime-matching agent domain:
   - append `logs/YYYY-MM-DD.md` with the session outcome and evidence;
   - update `wiki/<topic>.md` for reusable decisions or operational knowledge;
   - update `wiki/hot.md` only when the next run needs immediate context;
   - update `index.md` when a durable topic must be discoverable;
   - keep binaries and source assets in the workspace or linked storage, not the wiki.
7. Save stable user preferences or environment facts to memory only when they will remain useful. Do not save temporary task progress as memory.
8. Only stop development servers started during the current session, then verify they stopped.
9. Return a concise closeout:
   - `DAY ENDED.`
   - work completed and remaining blockers;
   - tests/build result;
   - task/project status;
   - commit and push result or clean/no-commit state;
   - wiki/log paths updated;
   - session-owned server status;
   - next recommended action.

## Partners in Biz delivery rules

- Projects/Kanban is the durable task bus for material work. Do not leave blockers or implementation evidence only in chat.
- Carry the resolved `orgId` on every tenant-scoped API call.
- Preserve source document, approval, reviewer, risk, capability, and expected-artifact links when present.
- Normal Partners web work stays on `development`; production promotion remains a separate approval-gated action.
- Client-delivered agents receive this skill through the versioned Partners in Biz system skills core pack and their policy-filtered agent skill pack. Presence in a shared cache alone is not proof of delivery.

## Completion evidence

A start or end workflow is complete only when every claimed action has read-back evidence. If a prerequisite is blocked, state the exact blocker, preserve all existing work, update the task when possible, and stop before any unsafe fallback.
