---
name: workflow-graph-operator
description: Use when Peet asks to run a workflow graph, start a prod template pack, check graph status on a project, or how Workflow Graph works day-to-day (not residual/engine build).
version: 1.0.0
author: Partners in Biz
license: MIT
metadata:
  hermes:
    tags: [partnersinbiz, workflow-graph, kanban, operator, graph-template, workflow-run]
    triggers:
      - run a workflow graph
      - start workflow graph
      - workflow graph template
      - research draft approve pack
      - content prepare publish gate
      - engineering change promote
      - is graph running
      - GraphTemplate
      - WorkflowRun
---

# Workflow Graph Operator (day-to-day)

Path A product law: **one sequencer, one Kanban task bus** — never a second board.

Use this skill for normal operation. Do **not** use it to re-open Path A engine residual, perfect-bar rebuild, or promote thrash work unless something is actually broken in production.

## Related skills (do not mix triggers)

| Skill | When |
|---|---|
| **workflow-graph-operator** (this) | Start/list/inspect runs, pick prod templates, explain how to use graph, route owners |
| `pib-workflow-graph-operations` | Residual / world-class bar / thrash / false promote / live golden missing |
| Theo `workflow-graph-kanban-sequencer` | Engine code, APIs, playbook flip, unit tests, implementation |
| `pib-production-promote-verification` | main/Vercel promote proof |
| `pib-kanban-agent-runtime` | Watcher write-back, claim thrash, stream-idle |

If Peet asks “is it perfect / residual / thrash,” load the residual skill. If he asks “run the research pack / start a graph / how do I use this,” stay here.

## Opt-in only

Workflow Graph does **not** start on every Messages chat.

- Normal chats → Pip + selected agents + ordinary Kanban tasks.
- Graph runs only when someone starts a run from a **GraphTemplate** (Suite UI or API), or a domain-event/playbook path creates a **WorkflowRun**.
- Never auto-flip every playbook to `workflow_graph`. Never invent a second board.

## Product shape (stable)

- Records: `GraphTemplate` + `WorkflowRun` ledger on top of Projects/Kanban.
- **Materialize to Kanban:** only `agent` + `human_gate`.
- **Stay on run ledger only:** `code_check`, `system`, `wait_*` (never pile up as cards).
- Fail-closed gates: publish, spend, deploy, finance, client-visible, secrets, human-review — agents cannot silently approve.
- Quiet success / alert-on-block are template notify fields; humans are not paged on every green run.
- Human gates = template-declared risk stops, not babysitting every node.

## Production templates (parent org reference pack)

Org `pib-platform-owner` reference pack (pilot=false, status=active). Prefer these names; re-list live before hard-coding if IDs drift.

| Name | Id | Shape |
|---|---|---|
| `prod-research-draft-approve` | `8TotIMWJIik8NSf7XWB9` | sage research → code_check → docs draft → code_check → human-review gate |
| `prod-content-prepare-publish-gate` | `fSsBZNRla4aTf9jJAks9` | maya prepare → code_check → public-publishing gate → system publish_noop |
| `prod-engineering-change-promote` | `PoH0NQdlrOZvq9GZMN07` | theo implement (gpt-5.3-codex-spark) → code_check → qa-release review (claude-sonnet-4-6) → production-deploy gate (no auto-merge) |
| `workflow-graph-golden-e2e` | `wIihkjJ93tulKVpJrhC4` | Deterministic QA reference only — not day-to-day client work |

Archived pilot/QA templates must stay archived. Do not reactivate hgate/qa-live debris for normal ops.

Other orgs may have their own templates — always `GET /api/v1/graph-templates` with the resolved `orgId` before starting a run.

## Per-node model routing (cost-tiered packs)

Each `agent` node may declare `agentModel` (allowlist: grok-4.6, grok-4.5, claude-sonnet-4-6, gpt-5.5, gpt-5.4, gpt-5.4-mini, gpt-5.3-codex-spark). The Suite/Plan graph editor shows an `agentModel` picker on agent nodes; absent = platform default.

- Cheap code/implementation workers → `gpt-5.3-codex-spark`
- Strong judge/review nodes → `claude-sonnet-4-6`
- `human_gate` nodes never carry a model (the human approves)
- The model flows: GraphNodeTemplate.agentModel → WorkflowRun node → MaterializeIntent → Kanban task `agentModel` → watcher dispatch
- API validates: non-allowlisted `agentModel` on an agent node is rejected with 400 (`outside the allowlist`)
- Live stamping verified 2026-08-04: production `partnersinbiz.online` persists `agentModel` on template PATCH/GET (pack promoted via PR #278; template `PoH0NQdlrOZvq9GZMN07` v3 carries implement→gpt-5.3-codex-spark, review→claude-sonnet-4-6). Before the promote, the live API stripped `agentModel` on save while keeping structure — if a template looks like it lost models, re-PATCH the per-node values.

## How operators start a run

### UI

1. Open the target **project**.
2. Suite / Plan → **Workflow Graph** templates panel.
3. Select an active template (prefer prod-* names).
4. Start run.
5. Watch Kanban for materialized **agent** + **human_gate** cards only.
6. Complete human gates with real approval evidence when the risk stop is ready.

### API

Base: `https://partnersinbiz.online/api/v1`  
Auth: interactive = user-delegation Bearer + `X-Org-Id`. Cron/system keys only for non-interactive.

```http
GET /graph-templates?orgId=<orgId>
GET /graph-templates?orgId=<orgId>&status=active

POST /workflow-runs
Idempotency-Key: <uuid>
X-Org-Id: <orgId>
Content-Type: application/json

{
  "orgId": "<orgId>",
  "templateId": "8TotIMWJIik8NSf7XWB9",
  "projectId": "<projectId>",
  "triggerType": "manual"
}
```

```http
GET /workflow-runs?orgId=<orgId>&status=all&limit=20
GET /workflow-runs?orgId=<orgId>&id=<runId>
GET /workflow-runs/<runId>          # ledger + inspect (cost/nodes/blocker/gateMap/stuck)
POST /workflow-runs/<runId>/cancel
```

Optional tick/terminal paths stay internal to watcher/engine — do not hand-drive production runs unless diagnosing a break (then residual skill).

On start success: return run id, status, project link, and which nodes will appear as Kanban cards. Do not claim succeeded until inspect/ledger says so.

## Routing (who owns what)

| Ask / situation | Owner |
|---|---|
| “Run X pack”, “is a graph running”, explain usage, sequence board work | **Pip** |
| Template/engine bug, materialize fail, write-back, API 404, code change | **Theo** |
| Live certify, post-promote re-verify, failure-path QA | **Quinn (qa-release)** |
| Ops polish, quiet/alert, budgets, admin hygiene, debris cleanup | **Nora** |
| Node work inside a run (research/doc/content/code) | Specialist on the materialized agent card (Sage/Iris/Maya/Theo/…) |

Pip coordinates. Specialists execute their node cards like normal Kanban agent tasks — with graph `expectedArtifacts` as the done bar.

## Approval gates (unchanged)

Starting a **template run** that only prepares internal work is normal write ops when Peet asked for it.

Still require explicit approval before:

- client-visible messages
- public publish / store submission
- paid spend / campaign launch
- production deploy / release promote
- invoice/payment/finance mutations
- secret/env/live profile config
- destructive delete/archive

Human_gate cards exist so those stops stay fail-closed. Completing a gate means recording the scoped approval artifact the node expects (typically `approval_ref`) — not bypassing platform approval policy.

`requiredCapability` ≠ `approvalGate`. Never copy publish/approval capability strings into Kanban `approvalGate`.

## Chat behaviour checklist

When Peet asks to use Workflow Graph:

1. Resolve `orgId` + `projectId` (do not guess client org).
2. List active templates for that org; prefer prod-* pack when on parent/platform.
3. Confirm which template and project if ambiguous — one short clarify, not a new engine phase.
4. Start run via UI guidance or `POST /workflow-runs` with Idempotency-Key.
5. Report: run id, link to project board, expected human gates (if any), that code_check/system will not appear as cards.
6. Do **not** open Path A residual cards, re-seed pilot templates, or “perfect bar” work unless live proof shows a real regression.

When Peet asks “will I babysit every project?”:

- No. Gates only where the template declares risk.
- Thin templates may have zero gates or one final CEO gate.
- Busy boards full of “QA human gate sample” are pilot debris, not the product UX.

## Broken vs normal

Treat as **broken** (hand residual / Theo / Quinn) only if:

- graph-templates / workflow-runs missing or non-JSON on production
- human_gate materialize invalid_spec again
- write-back never advances after agent done + artifacts
- zero ability to reach `status=succeeded` on a known-good template after correct artifacts/approvals
- review thrash wipes artifacts after human accept on graph proof cards

Otherwise operate with this skill only.

## Project reference

Build project (historical): Workflow Graph Engine `8f4vajS3vyOIBUoMrIs1` — status live; Path A complete. Day-to-day runs should target **the project Peet cares about**, not only the engine build board.

Wiki: `agents/partners/wiki/workflow-graph-productization-cleanup-2026-08-04.md`  
Wiki: `agents/partners/wiki/workflow-graph-per-node-model-routing-2026-08-04.md` (per-node model routing + chain status)  
Ops residual (if needed): skill `pib-workflow-graph-operations`
