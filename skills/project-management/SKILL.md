---
name: project-management
description: >
  Projects, tasks (project-nested AND standalone), time tracking, calendar events, and project docs
  on Partners in Biz. Use this skill whenever the user mentions anything about projects, tasks,
  todos, time, calendars, or meetings, including: "create a project", "project status", "project brief",
  "project doc", "project wiki", "kick off a project", "add a task", "personal todo", "todo list",
  "my tasks", "tasks due today", "overdue tasks", "assign task to", "reassign", "complete task",
  "mark done", "high priority task", "task for this deal", "task for this contact",
  "start a timer", "stop timer", "log time", "time entry", "billable hours", "non-billable",
  "running timer", "what am I working on", "bill time to invoice", "invoice for time",
  "hourly rate", "team utilization", "team capacity", "schedule a meeting", "calendar event",
  "all-day event", "RSVP", "accept meeting", "decline meeting", "reminder", "recurring event",
  "comment on task", "@mention team member", "project context for AI". If in doubt, trigger.
---

# Project Management — Partners in Biz Platform API

Projects, tasks (two systems — project-nested vs. standalone), time tracking with billing-to-invoice, calendar events with RSVP, and project docs. Plus a rich agent-context endpoint that gives AI agents everything they need about a project in one call.

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.


## Base URL & Authentication

```
https://partnersinbiz.online/api/v1
```

```
Authorization: Bearer <AI_API_KEY>
```

Prefer the user-delegation Bearer token (`pib_dlg_…`) or a device-login / personal token from `pib-skills login` (see `system-auth`). `AI_API_KEY` is for cron/system jobs only. On 403, print the API error and stop — do not retry with a god-key.

## Two task systems — know the difference

- **Project-nested tasks** (`/projects/[projectId]/tasks`) — classic Scrum-style tasks that belong to a project. Have comments subcollection.
- **Standalone tasks** (`/tasks`) — personal todos, cross-project work, or tasks linked to a contact/deal without a project. Can still reference `projectId` if needed.

Pick the system that fits: use project-nested when a project is the clear container; use standalone for personal todos or deal-linked tasks.

## PiB-owned project recipient model

Projects can be source/recipient records just like invoices:

- `orgId`, `sourceOrgId`, and `issuerOrgId` are the sender/source workspace. For Partners in Biz-created client work, this is the resolved platform owner org (`pib-platform-owner`).
- `recipientOrgId` and `targetOrgId` are the client organization that receives/collaborates on the project.
- `clientOrgId` remains populated with the recipient org for compatibility with existing project, time, and report surfaces.
- `companyId` / `sourceCompanyId` point to the sender-owned CRM Company. For PiB client projects this should be the platform CRM Company with `linkedOrgId=<clientOrgId>`.
- `contactId` / `sourceContactId` point to the sender-owned CRM Contact when the project is shared with a specific contact.
- `claimStatus`, `claimToken`, and `claimableRelationshipId` appear when a project is shared to a CRM recipient that has not joined or claimed yet.
- CRM OS command centers surface projects from the company detail page. When creating or moving projects, preserve stable links where known: `companyId`, `sourceCompanyId`, `recipientOrgId`/`targetOrgId`/`clientOrgId`, `relationshipId`, `serviceWorkspaceId`, `allowedOrgIds`, `visibility`, and `approvalState`. The command-center API uses org-scoped project reads plus in-memory matching, including active `businessRelationships`, so do not add composite-index-sensitive project queries for company visibility.

Client-created project requests remain client-originated until PiB accepts/converts them into PiB-sourced work. Client portal project screens must use `GET /projects?view=received`; do not attach unscoped Firestore listeners to the top-level `projects` collection.

## Project-context routing guard

When a chat, task, or user message originates inside a specific project, that project is the authoritative destination for lists, new tasks, docs, comments, and status updates. Do not reuse a previously mentioned project from another conversation or nearby browser context.

Before listing, creating, moving, or commenting on project work:

1. Prefer the explicit project context supplied by the runtime/message (`projectId`, project title, selected project, project route, or "I am currently in the X project").
2. If the user corrects the active project, immediately treat that correction as authoritative for the rest of the request.
3. Fetch `GET /agent/project/[projectId]` for the active project before acting when a project id is available.
4. If only a project title is available, search/list projects in the current `orgId` and match by title before acting.
5. If multiple projects share a similar title, ask for confirmation rather than filing work in the wrong board.
6. Include both the human-readable project title and project id in task/status replies so the scope is auditable.
7. Never file Saaiman & Saaiman project work into the Dare to Explore project, or any other previously used board, just because that board was active in an earlier conversation. Cross-project bleed is worse than asking one careful confirmation question.

## Cross-app handoff rule

Projects are the canonical task bus whenever work crosses module boundaries, agents,
Peet, Partners in Biz staff, or client action.

For substantial client work, start with an internal/client document for the spec, then use Projects/Kanban as the execution bus. If the spec is not approved yet, create a Pip approval-gate task and hold specialist agent tasks at `agentStatus='awaiting-input'` with `dependsOn` until approval. When approval lands, release those tasks to `pending` so the kanban watcher picks them up automatically.

Domain modules still own their own progress records:

- SEO work must update the SEO sprint.
- Social work must update the campaign/social queue.
- Ads work must update the ads campaign/ad records.
- Documents work must update the document/review surface.
- CRM work must update the CRM record, activity, or automation state.

Projects carry the execution handoff: who needs to do what, by when, what it blocks,
which agent owns it, and where the evidence lives.

When an agent discovers human work it cannot complete:

1. First update the domain record with the finding, current status, and blocker.
2. Find the active client/workstream project.
3. If no suitable project exists, create one with `POST /projects`.
4. Create a project-nested task with enough context for the assignee to act without
   reading the whole chat.
5. Assign or mention the responsible person if their user id is known.
6. If the responsible person cannot be resolved, leave the task unassigned, add a
   clear owner prefix in the title (`Peet action:`, `Client action:`, `Team action:`),
   and include `needs-assignment` in `labels`.
7. Add labels that tie the ticket back to the source module and record id, for example
   `seo`, `seo-sprint:<id>`, `ads-campaign:<id>`, `document:<id>`, `crm:<entityId>`.
8. Link the project task id or URL back into the domain record's notes/blocker field
   where the API allows it.

If there is no project yet, create it first. Do not leave actionable blockers only in
the final chat response, repo PR, or wiki.

Every blocker task must explain:

- what is wrong
- how to fix it
- what evidence/proof is required
- what message should be sent back to the agent when the blocker is resolved

For SEO blockers, the SEO module now creates/reuses the client SEO project, creates
the project task, and notifies matching admins automatically when the SEO task is
marked `blocked`. The agent remains responsible for writing a useful blocker reason.

## Business Insight Review Tasks

The Loop Engine creates conservative internal project tasks for `business-insight-review` findings. These tasks identify a growth gap, commercial risk, operational blocker, or missing-data issue and preserve approval gates for anything risky.

When handling one:

1. Inspect `metadata.businessInsightReview`, `agentInput.context.businessInsightReview`, or `agentOutput.businessInsightReview` for the source metric, evidence, owner, and required approval gate.
2. Confirm the task is internally approved before turning it into execution work.
3. Use `POST /projects/[projectId]/tasks/[taskId]/business-insight-action` to convert an approved review task into tracked action work.
4. Keep side effects gated: do not message clients, publish content, approve documents, change ad spend, alter finance records, or rewrite runtime/skill config from the review task itself.
5. Close the action only with evidence: linked source items, baseline/latest metric when measurable, owner, result, and any remaining blocker.

Document-related insight tasks can come from `client_documents_waiting_for_review`, `client_documents_changes_requested`, and `client_documents_blocking_publish_assumptions`. Use the `client-documents` skill to inspect the document and preserve `linked.projectId`.

## Collaboration primitives

- **Idempotency** on `POST /projects`, `POST /tasks`, `POST /time-entries`, `POST /time-entries/start`, `POST /calendar/events`
- **Comments** (`resourceType: 'project' | 'task' | 'time_entry' | 'calendar_event'`)
- **Assignments** — `assignedTo: { type: 'user' | 'agent', id }` on tasks and events
- **Notifications** — auto on task assignment, event invite

---

## API Reference

### Projects

#### `GET /projects` — auth: client
Filters: `orgId`, `status` (exact stored lifecycle value), `clientOrgId`, `page`, `limit`, `view`, `archive` (`active`|`only`|`include`).

Current create/update lifecycle statuses are `discovery`, `design`, `development`, `review`, `live`, and `maintenance`. Historical rows can also contain `completed` or legacy values, so use `archive=include` when auditing older work. Do not send `active`, `on_hold`, or `cancelled` when creating a project; the create route rejects unsupported statuses with `400 Invalid status`.

- Default/sent view filters by source `orgId`.
- `view=received` filters by `recipientOrgId` and compatible `clientOrgId` legacy rows.
- `view=shared` lists claim-token/shared projects.

#### `POST /projects` — auth: client (idempotent)
Body:
```json
{
  "orgId": "org_abc",
  "name": "Q2 Marketing Campaign",
  "description": "Launch new product line...",
  "brief": "# Background\n...\n## Goals\n...",
  "recipientOrgId": "org_client",
  "clientOrgId": "org_client",
  "companyId": "crm_company_id",
  "contactId": "crm_contact_id",
  "status": "discovery",
  "startAt": "2026-04-01",
  "endAt": "2026-06-30",
  "assignedTo": { "type": "user", "id": "uid123" },
  "tags": ["campaign", "q2"]
}
```

For PiB/admin-created client projects, the request `orgId` is the client/recipient org; the API resolves the platform owner as `sourceOrgId` and stores the client in `recipientOrgId`/`targetOrgId`/`clientOrgId`. For CRM-targeted project sharing, pass `companyId`/`contactId` and optional `recipientOrgId`; a Company `linkedOrgId` is reused when already present.

Response (201): `{ id }`.

After creation, read the returned project back with `GET /projects/[id]` before creating nested tasks or claiming success. If the route returns `500 Project setup resource identity is invalid`, do not keep retrying and do not describe a standalone escalation task as the requested project or as completed scoping work. That response means the deployed public route is incorrectly forwarding ordinary Next.js context as trusted setup identity; record the exact response and escalate the production release gap.

#### `DELETE /projects` — auth: admin
Deletes/archives a project through the collection route. Check current route code before use; this is admin-only and should be treated as destructive.

#### `GET /projects/[projectId]` — auth: client
Full project.

#### `PATCH /projects/[projectId]` — auth: client
Update fields. Current API accepts `name`, `status`, `description`, and `brief`.

`PUT` and `DELETE` are not exported on `/projects/[projectId]` in the current app; use collection-level `DELETE /projects` for destructive admin operations.

#### `GET/POST /projects/[projectId]/access` — auth: client
Project access surface. `GET` returns the caller's project access plus member candidates. `POST` is for project managers to add/link/invite access. Use this instead of editing access arrays directly.

#### `POST /projects/[projectId]/move` — auth: admin
Moves a project to a client org through `moveProjectToClientOrg`. Use for converting or relocating client-originated/project-shared work. This logs `project_moved` activity and should not be replaced by manual Firestore edits.

#### `GET/POST/PATCH/DELETE /projects/[projectId]/suite` — auth: client
Project Suite records are the richer operational layer for tasks, milestones, approvals, risks, capacities, and revenue rows. Reads are client-authenticated through `getProjectForUser`; writes require the project role permission for the suite type.

#### `GET /projects/reporting` — auth: client
Project reporting surface that aggregates visible project suite rows for accessible projects. Use this for project portfolio/reporting summaries instead of trying to join suite subcollections manually.

### Project-nested tasks

#### `GET /projects/[projectId]/tasks` — auth: admin
Filters: `status`, `priority`, `assignedTo`.

#### `POST /projects/[projectId]/tasks` — auth: admin
Body:
```json
{ "title": "...", "description": "...", "status": "todo", "priority": "high",
  "dueDate": "2026-04-20", "assignedTo": "uid123" }
```

##### Agent dispatch fields (optional — for assigning work to AI agents)

Tasks can be assigned to a named agent in the Partners-in-Biz team (Pip, Theo, Maya, Sage, Nora) by adding these fields to the POST or PATCH body:

```json
{
  "title": "Build /pricing page",
  "assigneeAgentId": "pip",
  "agentInput": { "spec": "Build a /pricing page using the existing design system" },
  "agentEffort": "high",
  "agentModel": "claude-sonnet-4-6",
  "dependsOn": ["task_abc123"]
}
```

- **`assigneeAgentId`** — one of `pip` | `theo` | `maya` | `sage` | `nora` (or omit/null for a human task). Setting this on create auto-initialises `agentStatus` to `pending`.
- **`agentStatus`** — `pending` | `picked-up` | `in-progress` | `awaiting-input` | `done` | `blocked`. On reassignment, status resets to `pending` unless explicitly overridden on update.
  - **Revision/requeue rule:** if an agent task in `done`, `blocked`, or `awaiting-input` is moved back to `columnId:'todo'` without an explicit `agentStatus`, the task PATCH route requeues it automatically: `agentStatus:'pending'`, `reviewStatus:'changes-requested'`, and stale `agentOutput`/conversation/heartbeat fields cleared. Humans should still add a task comment first with the requested changes; the watcher injects recent task comments into the retry prompt so the agent sees the review note.
  - **Approval-gated task gotcha:** `POST /projects/[projectId]/tasks` currently resets agent-assigned tasks to `agentStatus='pending'` even when the create payload includes `agentStatus:'awaiting-input'`. If you are creating future/approval-gated agent tasks, immediately `PATCH /projects/[projectId]/tasks/[taskId]` with `{ "agentStatus": "awaiting-input" }` after creation, then verify with `GET /projects/[projectId]/tasks` before telling Peet the tasks are gated. Otherwise the watcher can pick them up too early.
- **`agentInput`** — `{ spec: string, context?: object, constraints?: string[] }`. `spec` is required.
- **`agentEffort`** — optional per-run thinking level: `minimal` | `low` | `medium` | `high` | `xhigh` (or omit/null for profile default). Set this explicitly when fanning out agent work: research/architecture/spec/ambiguous debugging = `high`; broad implementation = `high` when risky or `medium` when straightforward; QA/review/release checks = `medium`; routine cleanup/status/reporting = `low`; emergency or deeply ambiguous platform debugging = `xhigh`.
- **`agentModel`** — optional allowlisted model override: `claude-sonnet-4-6`, `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`, or `gpt-5.3-codex-spark`. Prefer omitting this unless Peet or the task explicitly needs a model. If you set it, choose Claude for writing/review/judgment-heavy work and GPT/Codex for code execution where the profile is already configured for it.
- **`agentOutput`** — written when the agent completes: `{ summary: string, artifacts?: [{ type, ref, label? }], completedAt }`. `artifacts.type` is `url` | `file` | `commit` | `message-thread` | `doc`.
- **`dependsOn`** — array of task IDs that must reach `agentStatus='done'` before this one becomes eligible for pickup.
- **Dependency context now travels with the dispatch.** The watcher injects project name/brief, project doc titles/IDs, `agentOutput.summary` from each `dependsOn` task, recent task comments, and a standing instruction to fetch `GET /api/v1/agent/project/[projectId]` before starting.
- **`agentHeartbeatAt: true`** — pass this sentinel on PATCH to bump the heartbeat to "now" (used while an agent is actively working).

### Self-dispatch pattern

When the user asks you to "do X and create a task for it" or "track this work", create the task **assigned to yourself** so it shows on the kanban:

1. `POST /projects/{projectId}/tasks` with `assigneeAgentId: 'pip'` and `agentInput.spec`
2. Immediately do the work
3. `PATCH /projects/{projectId}/tasks/{taskId}` with `agentStatus: 'in-progress'` then later `agentStatus: 'done'` and `agentOutput.summary`

This gives the human a real audit trail on the board without you needing to ask permission for each step.

#### `GET/PATCH/DELETE /projects/[projectId]/tasks/[taskId]` — auth: admin

Use `PATCH` for project-nested task updates. `PUT` returns 405 on the current API.

#### `POST /projects/[projectId]/tasks/[taskId]/unblock` — auth: client

Unblocks a task that is actually blocked or awaiting input. The route:
- requires an authorised user role,
- checks project access through `getProjectForUser`,
- verifies the task is blocked (`columnId='blocked'` or `agentStatus='blocked'|'awaiting-input'`),
- returns `409` with readiness reasons if dependencies/input are not ready,
- moves the task to `columnId='todo'`,
- sets agent tasks back to `agentStatus='pending'`,
- sets `reviewStatus='changes-requested'` for agent tasks.

Do not call unblock on ordinary review/done tasks. For revision requests, add a task comment first, then move/patch the task so the watcher has the requested change context.

#### `GET /projects/[projectId]/tasks/[taskId]/comments` — auth: admin
List comments on a project task (pre-existing per-task comment collection — distinct from the unified `/comments`).

#### `POST /projects/[projectId]/tasks/[taskId]/comments` — auth: admin
Body: `{ text: string }`.

#### `PATCH /projects/[projectId]/tasks/[taskId]/comments/[commentId]` — auth: admin
Marks a project-task comment as picked up by an AI agent. Body: `{ "agentPickedUp": true }`.

### Project docs (wiki)

#### `GET /projects/[projectId]/docs` — auth: admin
List docs.

#### `POST /projects/[projectId]/docs` — auth: admin
Body: `{ title, content (markdown), type? }`.

#### `GET/PATCH/DELETE /projects/[projectId]/docs/[docId]` — auth: client
`PATCH` updates legacy project docs. `GET` can also resolve linked `client_documents` records when `linked.projectId` points at this project.

### Agent project context — **gold endpoint for AI**

#### `GET /agent/project/[projectId]` — auth: admin
Returns everything an agent needs to work on a project in one call:
```json
{
  "project": { "name": "...", "status": "...", "description": "...", "brief": "...", "orgId": "..." },
  "documents": [{ "title": "...", "content": "...", "type": "..." }],
  "tasks": [{
    "id": "task_abc",
    "orgId": "org_abc",
    "projectId": "proj_xyz",
    "title": "...",
    "description": "...",
    "priority": "high",
    "columnId": "review",
    "status": "in_progress",
    "assigneeAgentId": "theo",
    "agentEffort": "high",
    "agentModel": "claude-sonnet-4-6",
    "agentStatus": "done",
    "agentInput": { "spec": "...", "context": {} },
    "agentOutput": { "summary": "...", "artifacts": [{ "type": "commit", "ref": "abc123" }] },
    "dependsOn": ["task_previous"],
    "labels": ["qc", "handoff"],
    "reviewStatus": "pending",
    "agentConversationId": "run_...",
    "agentHeartbeatAt": "...",
    "attachments": []
  }],
  "plan": {
    "planningDiscovery": { "status": "confirmed", "brief": { "outcome": "..." }, "revision": 3 },
    "milestones": [],
    "approvals": [],
    "risks": [],
    "decisions": [],
    "playbooks": [],
    "automations": [],
    "capacities": [],
    "health": {},
    "timeline": {},
    "workload": {},
    "reports": {}
  },
  "recentComments": [...]
}
```

**Use this first** whenever an agent is asked to work on a project. It is the gold endpoint for project handoff/QC because it exposes task ids, org/project scope, kanban column/status, agent dispatch input/output, artifact refs, dependencies, labels, review status, **Plan suite records**, planning discovery state, and safe agent conversation/heartbeat metadata in one response.

### Interactive planning discovery (mandatory for substantive planning)

For new substantive projects and major replans, load the `interactive-project-planning` skill. The Plan tab polls every 15 seconds while visible.

```
GET  /projects/{projectId}/planning-discovery
POST /projects/{projectId}/planning-discovery
```

Action types: `start`, `record_inspection`, `ask_question`, `answer_question`, `surface_brief`, `submit_brief`, `confirm`, `plan_with_assumptions`, `reopen`.

Rules:

- Inspect brief/docs/files/Plan/tasks/tools/agents/skills before asking.
- One question + current guess at a time.
- Human managers only may `confirm` or `PLAN WITH ASSUMPTIONS`.
- Planning mutations and playbook runs fail closed with `planning_discovery_required` until the Decision Brief is confirmed or assumptions-attested.
- After confirmation, create **structured** playbook steps (assigneeAgentId, agentInput.spec, dependsOnStepIds, reviewerAgentId, requiredCapability, riskLevel, expectedArtifacts, verifierChecklist) — never bare unassigned titles for agent work.

### Standalone tasks

#### `GET /tasks` — auth: admin
Filters: `orgId` (required), `status` (`todo`|`in_progress`|`done`|`cancelled`), `priority` (`low`|`normal`|`high`|`urgent`), `assignedTo` (format `user:uid` or `agent:aid`), `projectId`, `contactId`, `dealId`, `dueBefore`, `dueAfter`, `tags`, `page`, `limit`.

#### `POST /tasks` — auth: admin (idempotent)
Body:
```json
{
  "orgId": "org_abc",
  "title": "Send proposal draft",
  "description": "...",
  "status": "todo",
  "priority": "high",
  "dueDate": "2026-04-20",
  "assignedTo": { "type": "user", "id": "uid123" },
  "projectId": "proj_xyz",
  "contactId": "contact_abc",
  "dealId": "deal_xyz",
  "tags": ["urgent", "client-facing"]
}
```

Required: `title`. Defaults: `status='todo'`, `priority='normal'`, `tags=[]`. If `assignedTo` set, notifies assignee.

**Agent dispatch fields also work on standalone tasks** — `assigneeAgentId`, `agentStatus`, `agentInput`, `agentEffort`, `agentModel`, `agentOutput`, and `dependsOn` are accepted with the same shape as project-nested tasks. See the "Agent dispatch fields" section under project-nested tasks for the full schema. Use standalone tasks when there's no specific project in scope (e.g. chatting from the org-level Agent tab); use project-nested tasks when working inside a specific project's Agent tab.

#### `GET/PUT/DELETE /tasks/[id]` — auth: admin
PUT updatable: `title`, `description`, `status`, `priority`, `dueDate`, `assignedTo`, `projectId`, `contactId`, `dealId`, `tags`, plus agent dispatch fields (`assigneeAgentId`, `agentStatus`, `agentInput`, `agentEffort`, `agentModel`, `agentOutput`, `dependsOn`, `agentHeartbeatAt:true` sentinel). Transition to `done` sets `completedAt`.

#### `POST /tasks/[id]/complete` — auth: admin
Sets `status='done'`, `completedAt`. Dispatches `task.completed`.

#### `POST /tasks/[id]/assign` — auth: admin
Body: `{ assignedTo: { type: 'user'|'agent', id } }`. Notifies new assignee.

### Time tracking

#### `GET /time-entries` — auth: admin
Filters: `orgId` (required), `userId`, `projectId`, `taskId`, `clientOrgId`, `from`, `to`, `billable`, `billed` (has invoiceId), `running` (endAt null), `page`, `limit`.

#### `POST /time-entries` — auth: admin (idempotent)
Create a completed entry. Required: `description`, `startAt`. Either `endAt` or `durationMinutes`.
Body:
```json
{ "orgId": "org_abc", "description": "Client call", "startAt": "2026-04-10T10:00:00Z",
  "endAt": "2026-04-10T11:00:00Z", "billable": true, "hourlyRate": 850, "currency": "ZAR",
  "projectId": "proj_xyz", "clientOrgId": "org_client", "tags": ["call"] }
```

Defaults: `userId=current user`, `billable=true`, `currency='ZAR'`.

#### `GET/PUT/DELETE /time-entries/[id]` — auth: admin
PUT recomputes `durationMinutes` if start/end changes. Returns 409 if already billed.

#### `POST /time-entries/start` — auth: admin
Begins a timer. Body: `{ description, projectId?, taskId?, clientOrgId?, billable?, tags?, userId? }`.

**409 if a timer is already running** for this user — returns existing entry id.

Response: `{ id, startAt }`.

#### `POST /time-entries/[id]/stop` — auth: admin
Sets `endAt=now`, computes `durationMinutes`. Returns `{ id, endAt, durationMinutes }`.

#### `POST /time-entries/bill` — auth: admin
Attach time entries to an invoice as line items.

Body: `{ entryIds: string[], invoiceId: string }`.

Each entry becomes: `{ description, quantity: durationMinutes/60 (rounded 2dp), unitPrice: hourlyRate || 0, amount: quantity * unitPrice }`. Recomputes invoice totals. Atomic batch write. 409 if any entry already billed.

Response: `{ billed: count, invoiceId, newTotal }`.

#### `GET /time-entries/running` — auth: admin
Query: `orgId`, `userId?` (default: current). Returns `{ running: entry | null }`.

### Calendar events

#### `GET /calendar/events` — auth: admin
Filters: `orgId` (required), `from` (ISO), `to`, `relatedToType`, `relatedToId`, `assignedTo` (format `user:uid`), `limit` (default 200, max 500). Sorted `startAt asc`.

#### `POST /calendar/events` — auth: admin (idempotent)
Body:
```json
{
  "orgId": "org_abc",
  "title": "Acme Demo",
  "description": "Walkthrough of Pro features",
  "startAt": "2026-04-22T14:00:00Z",
  "endAt": "2026-04-22T15:00:00Z",
  "allDay": false,
  "timezone": "Africa/Johannesburg",
  "location": "Zoom",
  "meetingUrl": "https://zoom.us/j/...",
  "attendees": [
    { "name": "Jane Doe", "email": "jane@acme.com", "status": "pending" }
  ],
  "relatedTo": { "type": "contact", "id": "contact_abc" },
  "assignedTo": { "type": "user", "id": "uid123" },
  "reminderMinutesBefore": [60, 10]
}
```

Validates `startAt < endAt`. Defaults: `allDay=false`, `timezone='UTC'`, `attendees=[]`, `recurrence=null`. Notifies `assignedTo`.

Related-to types: `contact`, `deal`, `project`, `client_org`.

#### `GET/PUT/DELETE /calendar/events/[id]` — auth: admin

#### `POST /calendar/events/[id]/rsvp` — auth: admin
Body: `{ email: string, status: 'accepted'|'declined'|'tentative'|'pending' }`.

Updates the matching attendee's status (case-insensitive email match). 404 if attendee not on event.

### Comments on project resources

```json
POST /comments
{ "orgId": "org_abc", "resourceType": "task", "resourceId": "task_xyz",
  "body": "Blocked on client signoff. @user:uid_manager" }
```

### Team utilization report

#### `GET /reports/team-utilization?orgId=X&from=...&to=...`
```json
{ "users": [{ "userId": "uid123", "totalMinutes": 9600, "billableMinutes": 7200,
              "nonBillableMinutes": 2400, "utilizationPct": 0.75 }],
  "totalMinutes": 48000, "avgUtilizationPct": 0.7 }
```

---

## Workflow guides

### 1. Create a project + kick off

```bash
POST /projects
{ "orgId": "org_abc", "name": "Q2 Campaign", "brief": "# Goals...",
  "clientOrgId": "org_client", "status": "discovery", "assignedTo": { "type": "user", "id": "uid_pm" } }

# Add initial docs
POST /projects/proj_xyz/docs
{ "title": "Project Requirements", "content": "# Requirements...", "type": "requirements" }

# Break down into tasks
POST /projects/proj_xyz/tasks
{ "title": "Creative brief", "priority": "high", "dueDate": "2026-04-18", "assignedTo": "uid_creative" }
```

### 1b. Create a PiB-sourced client project

```bash
# Admin/AI creates this while managing the client org. PiB becomes source/issuer;
# the client becomes recipient/clientOrgId.
POST /projects
{ "orgId": "org_client", "name": "Website launch", "brief": "# Goals...",
  "companyId": "pib_platform_crm_company", "status": "discovery" }

# Client portal list.
GET /projects?view=received
```

### 2. Agent picks up a project

```bash
# Single call — gets everything
GET /agent/project/proj_xyz
# Returns project + docs + tasks + recent comments
```

### 3. Personal todo workflow

```bash
# Create todo
POST /tasks
{ "orgId": "org_abc", "title": "Follow up with Acme", "priority": "high",
  "dueDate": "2026-04-17", "contactId": "contact_abc", "tags": ["sales"] }

# Filter: what's on my plate today?
GET /tasks?orgId=org_abc&assignedTo=user:uid_me&dueBefore=2026-04-18&status=todo

# Complete
POST /tasks/task_abc/complete
```

### 4. Timer workflow

```bash
# Start timer
POST /time-entries/start
{ "description": "Working on Acme deck", "projectId": "proj_xyz", "billable": true }
# → { id: "te_abc", startAt: "..." }

# ... work happens ...

# Stop
POST /time-entries/te_abc/stop
# → { id, endAt, durationMinutes }

# Check running
GET /time-entries/running?orgId=org_abc
```

### 5. Bill time to invoice

```bash
# Get billable unbilled entries
GET /time-entries?orgId=org_abc&clientOrgId=org_client&billable=true&billed=false

# Create invoice (billing-finance skill)
POST /invoices
{ "orgId": "org_client", "lineItems": [], "currency": "ZAR" }
# → { id: "inv_xyz", invoiceNumber: "CLI-042" }

# Attach time entries
POST /time-entries/bill
{ "entryIds": ["te_abc", "te_def"], "invoiceId": "inv_xyz" }
# Appends line items, recomputes invoice total
```

### 6. Schedule a meeting with a contact

```bash
POST /calendar/events
{ "orgId": "org_abc", "title": "Acme demo", "startAt": "2026-04-22T14:00:00Z",
  "endAt": "2026-04-22T15:00:00Z", "timezone": "Africa/Johannesburg",
  "meetingUrl": "https://zoom.us/j/...",
  "relatedTo": { "type": "contact", "id": "contact_abc" },
  "attendees": [{ "name": "Jane Doe", "email": "jane@acme.com", "status": "pending" }],
  "reminderMinutesBefore": [60, 10] }

# Attendee RSVPs
POST /calendar/events/evt_xyz/rsvp
{ "email": "jane@acme.com", "status": "accepted" }
```

### 7. Project brief via AI

```bash
# Fetch full context
GET /agent/project/proj_xyz
# Then feed the response into your AI prompt along with org brand profile:
GET /agent/brand/org_abc
```

### 8. Team utilization weekly report

```bash
GET /reports/team-utilization?orgId=org_abc&from=2026-04-07&to=2026-04-13
```

## Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 400 | `startAt must be before endAt` | Fix timestamps |
| 400 | `orgId is required` | Supply orgId query param |
| 404 | `Task not found` / `Event not found` | Verify IDs |
| 404 | `Attendee not found on this event` | Use an email that matches an attendee |
| 409 | `A timer is already running` | Stop existing timer first (response includes running id) |
| 409 | `Cannot modify a billed entry` | Unlink invoice or edit invoice directly |

## Agent patterns

1. **Start with `/agent/project/[id]`** — one call for full context.
2. **Use standalone tasks for personal work, project-nested for team sprint work.**
3. **Always stop timers** — running timers pile up. Check `/time-entries/running` when in doubt.
4. **Bill time before creating the next invoice** — the `/time-entries/bill` flow auto-appends line items so you don't need to manually compute totals.
5. **Relate calendar events** — set `relatedTo` so meetings show up in the contact/deal activity feed.
6. **Webhooks** — subscribe to `task.completed` to close loops (e.g., trigger review requests).
7. **Idempotency on creates** — pass `Idempotency-Key` on `POST /projects`, `/tasks`, `/time-entries`, `/calendar/events`.

## Client Document Handoff

Use the `client-documents` skill for specs, change requests, launch sign-offs, and handover packs. Link these documents with `linked.projectId` so Projects/Kanban remains the operational source of truth while `client_documents` handles presentation, comments, versions, and approvals.

Use the `research-intelligence` skill for working research that informs a project. Link Research items to `linked.projectId` and convert to a `research_report` document only when the client needs polished review or approval.
