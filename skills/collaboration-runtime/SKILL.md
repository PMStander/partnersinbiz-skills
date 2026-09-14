---
name: collaboration-runtime
description: Shared Partners in Biz collaboration runtime for agents. Use for updating assigned tasks, writing handoff comments, recording status, linking source documents, and keeping work visible without granting broad module-specific powers.
---

# Collaboration Runtime

This is the small shared operating skill every Partners in Biz specialist may use.
It does not grant ownership of a business module. It only lets an agent keep its
assigned work visible and auditable.

## Rules

- Read the task, project, source document, source research item, and recent comments before acting.
- Keep `agentStatus`, `agentOutput.summary`, comments, and artifacts current.
- Do not publish, spend, deploy, invoice, message a client, delete data, or change secrets through this skill.
- If blocked, write the exact blocker and set the task to `awaiting-input` or `blocked`.
- Attach evidence links whenever a task produces an output.

## Workspace folder lookup

When a task or skill needs client/project assets, Drive folders, VPS paths, or local Cowork paths, do not guess paths or assume there is only one folder per workspace.

- Resolve `orgId` from the task first.
- Read project context with `GET /api/v1/agent/project/{projectId}` when a project is in scope.
- Use the workspace folder registry/lookup context by stable fields: `orgId`, `resourceType`, `resourceId`, `tags`, `visibility`, and optional `syncTarget`.
- Choose the least-privileged folder that fits the task. Private drafts and agent notes belong in `admin_agents` or `admin_only`, not client-visible folders.
- Treat Google Drive folder/file IDs as canonical for binary/source assets. Treat VPS/local paths as working-copy hints.
- If the required folder record does not exist, create/request the folder mapping instead of inventing an undocumented path.
- Link produced assets back to the task as artifacts or comments.

Operational policy: `docs/deploy/workspace-folder-sync-v1.md`.

## Minimum Output

Every meaningful task update should include:

- source task id
- source document/spec/research ids when available
- current status
- next action
- artifacts produced
- approvals still required
