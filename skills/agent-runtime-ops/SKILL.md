---
name: agent-runtime-ops
description: >
  Hermes agent runtime administration on Partners in Biz: named-agent registry and
  provisioning, Hermes profile links/controls/dashboard/conversations/jobs/runs proxying,
  agent memory (hybrid lookup + admin reindex + incremental cron), Loop Engine
  self-improvement and business-insight review internals, Hermes/model-provider health
  verification (systemd, profile health, model canary), and linked-computer pairing/adoption
  for legacy project locations. Owner: theo. Critical risk — this skill can read/write live
  agent config, env, skills, and Hermes runs. Use this skill whenever the user mentions:
  "agent registry", "provision agent", "agent config", "agent env", "agent health",
  "agent logs", "agent files", "agent cron", "agent skill-policy apply", "Hermes profile",
  "Hermes run", "Hermes job", "Hermes conversation", "Hermes dashboard", "hermes profile link",
  "agent memory", "memory lookup", "semantic memory", "Obsidian memory", "reindex memory",
  "agent evolution review", "business insight review", "loop engine", "loop run telemetry",
  "self-improvement loop", "proactive insight", "what can the agent do",
  "systemctl hermes", "profile health", "model canary", "CODEXOK", "provider outage",
  "openai-codex auth", "NRestarts", "linked computer", "pairing required",
  "adopt legacy location", "no ready project computers", "sync now disabled". If in doubt, trigger.
---

# Agent Runtime Ops — Partners in Biz Platform API

Admin/VPS orchestration for named agents and their Hermes profile links, agent memory
subsystem, Loop Engine internals, runtime/provider health verification, and linked-computer
pairing. This is **not** ordinary client-facing task API surface — these routes inspect and
operate agent runtimes on Peet's behalf. Use them only when asked to manage agents, inspect
agent health/logs/files/skills, apply skill policy, control a Hermes run/job, review loop
telemetry, diagnose a provider outage, or pair/adopt a linked computer.

## Related skills

- `platform-ops` — general platform primitives (API keys, health, webhooks, files, search, notifications, comments)
- `platform-admin-users` — Platform Users (staff) super-admin CRUD
- `system-auth` — auth/delegation mint & resolve rules

## Auth (mandatory)

Interactive Hermes runs use the **user-delegation** token injected by Messages / minted via `system-auth` (`Authorization: Bearer pib_dlg_…` + `X-Org-Id`).

- Prefer the injected delegation token for all `/api/v1/*` calls in a human-triggered run.
- `AI_API_KEY` / agent system keys are **cron/system only**.
- Never claim a write succeeded without read-back (see pack `verificationContract` / skill success gate).
- See skill `system-auth` for mint/resolve rules.

- Call `GET /api/v1/oauth/whoami` first. If `memberRole` is not owner/admin (or super-admin for staff routes), say so and stop. On 403 print the API `error` — do not retry with `AI_API_KEY`.

## Base URL & Authentication

```
https://partnersinbiz.online/api/v1
```

```
Authorization: Bearer <AI_API_KEY>
```

Prefer the user-delegation Bearer token (`pib_dlg_…`) or `pib-skills login` / `pib_usr_` personal token for interactive work. Per-agent `pib_ag_...` keys are cron/system only. On 403, print the API error and stop.

For AI/agent bearer requests to tenant-scoped routes, also send:

```
X-Org-Id: <orgId>
```

## API Reference

### Agent memory (hybrid lookup + reindex)

#### `POST /agent/lookup` — auth: admin/agent
Hybrid memory lookup for agents. Use this for questions like "get me the client called John" or "what context do we have around this company?"

Body:
```json
{
  "query": "client John",
  "orgId": "org_abc",
  "sourceTypes": ["obsidian", "crm_contact", "crm_company"],
  "limit": 8,
  "requestingUserId": "uid_123",
  "delegationEvidenceId": "delegation_abc"
}
```

Response:
```json
{
  "intent": "entity_lookup",
  "entityCandidates": [],
  "selectedEntity": { "type": "contact", "id": "contact_abc", "label": "John" },
  "memory": [],
  "nextActions": [],
  "citations": []
}
```

Operating model:
- Exact/normalized Firestore entity resolution runs first across organizations, companies, contacts, and aliases.
- Vector retrieval runs only after structured tenant/org filters are applied.
- Memory comes from `agent_memory_chunks`, including compiled Obsidian/Hermes `index`, `wiki`, `raw`, `logs`, and selected operational Firestore data.
- Use vector memory for semantic recall and citations, not as the primary database operation.

Security model:
- VPS Hermes agents (`pip`, `theo`, `maya`, `sage`, `nora`, and specialists) are `role: "ai"` bearer-key callers.
- A Hermes agent lookup must include `requestingUserId` plus valid `agent_memory_delegations` evidence scoped to actor, org, user, status, expiry, and `read`, unless the agent has explicit `agent_memory_system:<orgId>` or `agent_memory_system:*`.
- Delegated lookup runs with the requesting user's effective org permissions.
- Client-effective lookups return only `public` memory chunks by default; internal, restricted, and sensitive chunks are hidden.
- Sensitive mailbox/support/social/ads snippets stay redacted unless source-specific delegated permission is present.
- Direct client Firestore access to `agent_memory_chunks` is denied; all retrieval goes through this API.

#### `POST /admin/agent-memory/reindex` — auth: admin
Manual/admin reindex. Use after new source connectors, schema changes, or backfills.

Body:
```json
{ "orgId": "org_abc", "sourceTypes": ["obsidian", "crm_contact"], "full": false }
```

#### `POST /cron/agent-memory-index`
Incremental scheduled indexing endpoint. Intended for Vercel cron or platform scheduler use, not direct client use.

### Admin agent registry

These are admin UI/VPS orchestration routes, not ordinary client-facing task APIs. They let platform admins inspect and operate named agents. Use them only when Peet asks to manage agents, inspect agent health/logs/files, apply skill policy, or control an agent's cron/config/env.

| Method | Path | Auth | Use |
|---|---|---|---|
| GET/POST | `/admin/agents` | admin; POST super-admin | List or provision named agents. |
| PUT | `/admin/agents/[agentId]` | admin | Update agent metadata/config reference. |
| GET/PUT | `/admin/agents/[agentId]/config` | admin | Read/write live agent config. |
| GET/PATCH | `/admin/agents/[agentId]/env` | admin | Read/update safe env keys. |
| GET | `/admin/agents/[agentId]/health` | admin | Read runtime health. |
| GET | `/admin/agents/[agentId]/logs` | admin | Read recent logs. |
| GET | `/admin/agents/[agentId]/files` | admin | List agent files. |
| GET/PUT | `/admin/agents/[agentId]/files/[...filePath]` | admin | Read/write a file through the agent file proxy. |
| GET/POST | `/admin/agents/[agentId]/cron` | admin | List/create cron jobs. |
| DELETE/POST | `/admin/agents/[agentId]/cron/[jobId]` | admin | Delete or trigger a cron job. |
| GET | `/admin/agents/[agentId]/runs/[runId]` | admin | Inspect a run. |
| GET | `/admin/agents/[agentId]/runs/[runId]/events` | admin | Stream/list run events. |
| POST | `/admin/agents/[agentId]/runs/[runId]/approval` | admin | Approve/reject a gated run action. |
| GET/POST | `/admin/agents/[agentId]/skills` | admin | List/install skills for the agent. |
| DELETE | `/admin/agents/[agentId]/skills/[skillName]` | admin | Remove an installed skill. |
| GET/POST | `/admin/agents/[agentId]/skill-policy` | admin; POST super-admin | Preview/apply the platform skill policy. |
| GET | `/admin/agent-tasks` | admin | List platform-visible agent tasks. |

`POST /admin/agents` provisions through Pip's VPS profile and is super-admin only. `POST /admin/agents/[agentId]/skill-policy` may rewrite live Hermes config, so preview with GET first.

### Hermes profile links and controls

| Method | Path | Auth | Use |
|---|---|---|---|
| GET/PUT/DELETE | `/admin/hermes/profiles/[orgId]` | GET client; PUT/DELETE super-admin | Read/configure/disable a Hermes profile link for an org. |
| GET/POST/PUT/PATCH/DELETE | `/admin/hermes/profiles/[orgId]/controls/[control]/[[...path]]` | admin/client with capability | Proxy a resolved Hermes admin control. |
| GET/POST/PUT/PATCH/DELETE | `/admin/hermes/profiles/[orgId]/dashboard/[...path]` | admin/client with capability | Proxy Hermes dashboard paths for the org profile. |
| GET/POST | `/admin/hermes/profiles/[orgId]/conversations` | admin/client with capability | List/start Hermes conversations. |
| GET/PATCH/DELETE | `/admin/hermes/profiles/[orgId]/conversations/[convId]` | admin/client with capability | Manage a conversation. |
| GET/POST | `/admin/hermes/profiles/[orgId]/conversations/[convId]/messages` | admin/client with capability | List/send messages. |
| POST | `/admin/hermes/profiles/[orgId]/conversations/[convId]/messages/[msgId]/finalize` | admin/client with capability | Finalize a message. |
| GET/POST | `/admin/hermes/profiles/[orgId]/jobs` | admin/client with capability | List/create jobs. |
| GET/PATCH/PUT/DELETE | `/admin/hermes/profiles/[orgId]/jobs/[jobId]` | admin/client with capability | Manage a job. |
| POST | `/admin/hermes/profiles/[orgId]/jobs/[jobId]/run` | admin/client with capability | Run a job now. |
| POST | `/admin/hermes/profiles/[orgId]/jobs/[jobId]/pause` | admin/client with capability | Pause a job. |
| POST | `/admin/hermes/profiles/[orgId]/jobs/[jobId]/resume` | admin/client with capability | Resume a job. |
| POST | `/admin/hermes/profiles/[orgId]/runs` | admin/client with capability | Start a run. |
| GET | `/admin/hermes/profiles/[orgId]/runs/[runId]` | admin/client with capability | Inspect a run. |
| GET | `/admin/hermes/profiles/[orgId]/runs/[runId]/events` | admin/client with capability | Stream/list run events. |
| POST | `/admin/hermes/profiles/[orgId]/runs/[runId]/approval` | admin/client with capability | Approve/reject a gated run action. |
| POST | `/admin/hermes/profiles/[orgId]/runs/[runId]/stop` | admin/client with capability | Stop a run. |
| GET/POST | `/admin/hermes/profiles/[orgId]/skills` | admin/client with capability | List/install profile skills. |
| DELETE | `/admin/hermes/profiles/[orgId]/skills/[skillName]` | admin/client with capability | Remove a profile skill. |

Hermes controls go through `requireHermesProfileAccess` and `resolveHermesAdminControl`; do not construct arbitrary VPS URLs from the client side. The API capability gate is the source of truth.

### Loop Engine self-improvement and business insight review

Use this section when Peet asks whether the agents are self-improving, whether the system is being proactive, or whether business insight gaps are being surfaced.

The active review loops are:

- `agent-evolution-review` — turns repeated agent blockers, rework, stale instructions, and review failures into evidence-backed learning proposals.
- `business-insight-review` — turns commercial, operational, and data-quality signals into internal insight cards/tasks before Peet has to inspect every workstream manually.

Loop Engine routes:

| Method | Path | Auth | Use |
|---|---|---|---|
| POST | `/admin/loop-engine/evaluate` | admin/ai | Evaluate a loop manually. Use dry-run first; set `persist` and `persistReviewTasks` only when review task creation is intended. |
| GET | `/admin/loop-engine/runs` | admin/ai | List recent org-scoped `loop_engine_runs`; use these records as evidence for candidates, actions, telemetry, and skipped reasons. |
| POST | `/projects/[projectId]/tasks/[taskId]/business-insight-action` | client/admin/ai with project access | Convert an approved `business-insight-review` task into tracked internal action work. |
| GET | `/api/cron/loop-review` | cron/admin | Scheduled loop-review worker; persists `loop_engine_runs` and conservative review task drafts. |

Business insight signal sources include CRM contacts/deals, capture sources, SEO sprints, ad campaigns, social posts/inbox, invoices, support tickets, reports, projects, agent outputs, previous `loop_engine_runs`, and client document review state.

Client document business metrics are:

- `client_documents_waiting_for_review` — `client_review` documents older than 7 days.
- `client_documents_changes_requested` — documents currently in `changes_requested`.
- `client_documents_blocking_publish_assumptions` — documents with open `blocks_publish` assumptions.

Guardrails:

- These loops may read, draft, create internal tasks, and report. They must not automatically rewrite skills/wiki/prompts/runtime config, message clients, publish content, change spend, approve finance, or change client-visible document access.
- Preserve approval gates from the loop registry: `human-review`, `client-visible`, `public-publishing`, `paid-spend`, and `finance`.
- Exact agent model/token/cost/duration evidence must come from existing task/run telemetry. Never estimate token/cost numbers; when telemetry is absent, record a tooling-gap instead of inventing data.
- Agent learning proposals need source task/run ids, repeated pattern counts, reviewer context, proposed instruction change, and validation plan before any skill or wiki update.
- Business insight proposals need source item ids, metric snapshot, opportunity/risk hypothesis, owner, recommended next action, and approval requirement.

### Hermes runtime and provider health

Treat these as separate acceptance gates:

1. `systemctl is-active hermes@<profile>` proves only that the gateway process is alive.
2. `/profiles/<profile>/health` proves only that the profile API is serving.
3. A real authenticated `POST /profiles/<profile>/v1/responses` with the prompt `Reply with exactly CODEXOK and nothing else.` proves the configured model provider can answer.

For a VPS provider incident, run the model canary across every routed active profile (`ads`, `data`, `docs`, `maya`, `nora`, `pip`, `qa-release`, `sage`, `sales`, `seo`, `support`, `theo`) before claiming the scope. The `default` unit is intentionally API-less and is verified through systemd stability and clean logs.

Keep platform API authentication separate from model-provider authentication:

- Test PiB credentials against an authoritative PiB endpoint, including `X-Org-Id` where required.
- `401 token_invalidated`, `token_revoked`, or `token_expired` from `openai-codex` is a Hermes provider credential failure, not a PiB API-key failure.
- A healthy profile endpoint plus a failed `CODEXOK` response is still an outage.
- A fallback that returns billing/credit, organisation-policy, or missing-provider errors is not a successful fallback.

For one failing Codex profile, use a profile-specific device flow; do not copy another working profile's `auth.json` or refresh token:

```bash
sudo -iu hermes bash -lc 'export HERMES_HOME=/var/lib/hermes; cd /var/lib/hermes/hermes-agent; /usr/local/bin/hermes -p <profile> auth add openai-codex --type oauth --no-browser --timeout 600'
```

After successful sign-in:

1. Restart only `hermes@<profile>`.
2. Wait at least 30 seconds and require `NRestarts` not to increase.
3. Require the public profile health route to return HTTP 200.
4. Require the real model canary to return exact `CODEXOK`.
5. Requeue blocked agent work only after all four checks pass.

Never print API keys, OAuth access tokens, refresh tokens, or raw profile environment values during this workflow.

### Linked computers — adopt legacy project locations (system path)

Use when Messages shows **Legacy · pairing required**, Sync now is disabled, or project chats have **No ready project computers**.

Wiki: `agents/partners/wiki/system-legacy-location-adoption-2026-07-22.md`

#### Adopt onto an already-paired device

```bash
POST /linked-computers/:deviceId/adopt-location
Authorization: Bearer $AI_API_KEY
{
  "adoptLocationId": "peets-mac-mini",   # or partners-vps
  "actorUserId": "zcpAJ4NXWQfjXWPXkl6nYwt7Gmm1"
}
```

Or from the repo with Firebase admin:

```bash
npx tsx scripts/list-linked-adoption-targets.ts
npx tsx scripts/adopt-project-location-onto-device.ts --dry-run \
  --device-id <id> --location-id peets-mac-mini
npx tsx scripts/adopt-project-location-onto-device.ts --apply \
  --device-id <id> --location-id partners-vps
```

#### Fresh VPS/Mac with no linked device yet

1. `POST /linked-computers/pairing` with `deviceKind`, `ownerType`, `adoptLocationId`
2. On the machine: `pib-runtime pair --challenge <id> --platform linux|macos`
3. Confirm workspace map if mapping status is pending

Do **not** tell the user to wait on Sync now while any linked location is still legacy. Sync also needs `PROJECT_SYNC_STORAGE_LIFECYCLE_VERIFIED` after TTL/lifecycle readback — separate from project chat readiness.

## Adding a new skill to the pib-system-skills pack (VPS rollout)

To ship a new PiB skill to agents (e.g. `impeccable-design-discipline`, pack 0.1.8):

1. Author `packs/pib-system-skills/skills/<name>/SKILL.md` (+ `references/`, `templates/` as needed) and mirror byte-identical into `.claude/skills/<name>/` (pack README requires the mirror; `diff -rq` to confirm).
2. Bump `packs/pib-system-skills/manifest.json` (`packVersion`, `catalogVersion` like `2026-08-08.system-skills-v0.1.8`, tier list, `skills.<name>` metadata) and add a CHANGELOG entry.
3. In `config/agent-skill-policy.json`: add `skillCatalog.<name>` (ownerAgentId, allowedAgentIds, riskLevel, syncTarget:'vps', pack, packTier), add to `repoPibSkills`, bump `catalogVersion` to match the manifest (lockstep enforced by `bin/verify-contracts.mjs`).
4. **GOTCHA — add to BOTH `pibSkills` AND `runtimeSkills`** on every allowed agent: `apply-agent-skill-policy.mjs` uses `runtimeSkills` when present (it overrides `pibSkills`), so a skill added only to `pibSkills` silently never links at runtime. Dry-run proves it: `node scripts/apply-agent-skill-policy.mjs --root /var/lib/hermes --no-config --allow-missing-global <agent>` — but the dry-run reports `missingPibSkills` until the shared cache symlink exists at `/var/lib/hermes/pib-skills/partnersinbiz/<name>` (created by `install-vps-skills.sh`). To verify wiring before publish, create a temporary symlink from the pack dir, dry-run, then remove it — never persist.
5. Publish/install are **config/secret-adjacent**: `bash scripts/publish-pib-system-skills-repo.sh` (force-push to `Partners-in-Biz/pib-system-skills` + tag) and `sudo -u hermes bash .../scripts/install-vps-skills.sh` (clone/pull pack → symlink shared cache → policy apply), then restart touched `hermes@<agent>` services. Flag for explicit approval — do not run unprompted.

## Error reference

| HTTP | Error | Fix |
|------|-------|-----|
| 401 | Unauthorized | Check `AI_API_KEY` or key expiry |
| 403 | Forbidden | Key lacks org access, or caller isn't super-admin for a super-admin-only route |
| 404 | `Agent not found` / `Profile not found` | Verify `agentId`/`orgId` |
| 429 | Rate limited | Respect `Retry-After` header |

## Agent patterns

1. **Dry-run before persisting.** For skill-policy apply and Loop Engine evaluate, GET/dry-run first, then apply/persist only when intended.
2. **Never claim provider health from one signal alone.** Require systemd + profile health + model canary all passing before declaring an incident resolved.
3. **Read-back after config/env writes.** Confirm the agent config or env change actually landed before reporting success.
4. **Preserve Loop Engine approval gates** — these loops draft and report; they never auto-publish, spend, or message clients.
5. **Never print secrets** during profile auth recovery workflows.
