---
name: pib-agent-org-setup
description: Use when Peet describes an org agent structure and Pip must seed the chart, bind seats, and provision Hermes profiles on machines. Also for Messages /hire.
version: 1.1.0
author: pip
license: internal
metadata:
  hermes:
    tags: [partnersinbiz, agents, org-chart, setup, provision, multi-org, hermes-profiles, hire]
    related_skills:
      - agent-runtime-ops
      - agent-skill-drift-gather
      - pib-system-skill-authoring
      - project-management
---

# PiB agent org setup (explain structure → chart + machines)

## When to use

- Messages **`/hire`** (aliases `/agent-hire`, `/provision-agent`)
- Peet wants an **organisation-level** agent company (not only platform admin)
- “Build this org’s agents”, “Theo FE/BE as real agents”, “seed client org chart”
- Natural-language brief: hierarchy, roles, skills, models → **Firestore org chart + live Hermes profiles**
- Multi-org: each client org can have a different tree and different bound agentIds

## Non-goals

- Not an auto-router that invents work without Kanban assignment
- Chart edits alone do **not** create machine profiles
- Portal org-admins edit **chart seats**; only Pip/Theo with runtime access provision profiles
- Do not push secrets/config or production deploys without Peet approval

## Two layers (always separate)

| Layer | Where | Live work? |
|---|---|---|
| Org chart seats | Firestore `agent_org_nodes` per `orgId` | No — titles, reportsTo, defaults, bind agentId |
| Runtime agents | Hermes profiles on Mac/VPS (`pip`, `theo`, `theo-fe`…) | Yes — skills, model, tools, linked devices |

Binding `agentId` on a seat points dispatch at a real profile. Unbound seat = organisational only.

## `/hire` command

Composer: `/hire <brief>`. Executor is `agent_intent` (dispatch tier).

Pip must:

1. Load **this skill** first; load `agent-runtime-ops` only for live profile hire.
2. Resolve `orgId` (workspace org or explicit). Never invent client orgIds.
3. Default to **chart-only**. Provision machines only when the user clearly wants a live hire
   (provision / create profile / make live / hire on Mac|VPS).
4. Confirm plan in 3–6 bullets, then execute and verify.

Example briefs:

- `/hire For Partners: Engineering under Theo (Quinn QA) + Marketing under Maya (Ari, Silas, Vera); chart reshape only`
- `/hire Client Acme: Coordinator + Delivery + Marketing; minimal seed; chart only`
- `/hire Provision theo-fe on Mac mini, frontend skill pack, bind seat Theo FE`

## Recommended company shape (dev + marketing)

Default for Partners platform and serious client delivery orgs:

```
Coordinator / Pip
├── Engineering lead (Theo)
│   ├── Frontend seat (optional hire theo-fe)
│   ├── Backend seat (optional hire theo-be)
│   └── Quinn — QA & Release
├── Marketing lead (Maya)
│   ├── Ari — Paid media
│   ├── Silas — SEO
│   └── Vera — Analytics / growth data
├── Sage — Research (supports both pillars)
├── Blake — Sales
├── Iris — Documents & specs
├── Nora — Billing & ops
└── Luca — Support
```

Principles (from multi-agent ops practice):

- **Two product pillars** (build + demand), not a flat peer soup
- **Leads route work** via Kanban child tasks; chart gates assign + fills defaults
- **Do not hire FE/BE split** until concurrent load justifies a second brain
- **Shared fleet bind** is OK (same `theo` across client orgs); dedicated brains only when isolation or parallel capacity is required

## Recommended skill packs (policy allowlist)

Baseline on almost every specialist: `system-auth`, `collaboration-runtime`, `project-management`, `evidence-ledger`, `daily-workflow`, `client-manager` (lookup), `crm-sales` (lookup only).

| Role / agentId | Core ownership skills | Strong additions |
|---|---|---|
| pip | `pib-agent-org-setup`, `platform-ops`, `workflow-graph-operator`, `interactive-project-planning` | gather skills, `content-engine` (route only) |
| theo | `platform-ops`, delivery/deploy skills already on the theo allowlist | `impeccable-design-discipline`, `browser-agent` |
| theo-fe (if hired) | frontend-focused engineering pack + design discipline | accessibility, UI QA handoff |
| theo-be (if hired) | APIs, Firestore, auth, infra | release handoff to Quinn |
| qa-release | QA/release skills, smoke/prod verification | design audit gate awareness |
| maya | `content-engine`, `social-media-manager`, studio-* | `email-outreach` (draft), creative packs |
| ads | `ads-manager`, marketing/ads-* | budgets never launch without approval |
| seo | `seo-sprint-manager`, `geo-seo-service`, local-seo | research/last30days |
| data | `data-analyst`, `analytics`, `reports` | ads-math / attribution |
| sage | `research-intelligence`, open-notebook, last30days | strategy docs via Iris |
| sales | `sales-operating-system`, `crm-sales`, `crm-hygiene-gather` | interview-me, outreach drafts |
| docs | `client-documents`, `docs-lead`, studio review | planning breakdown |
| nora | `billing-finance`, reports, CRM hygiene | staff billing access when needed |
| support | `support-manager`, browser-agent | triage → Theo/Maya |

Never expand skill policy casually in a hire — prefer binding existing policy packs; use `pib-system-skill-authoring` + drift gather when a new skill must land.

## Soul quality bar

Every hired profile gets a **distinct** SOUL.md:

1. Identity (who, never “as an AI”)
2. Mission (one sharp sentence)
3. Voice (tone, length, what they never sound like)
4. Values (3–5 non-generic)
5. Operating style + startup routine
6. Boundaries + approval gates (PiB standard)
7. Handoffs (who they escalate to / receive from)

Do not clone a template with only the name swapped. Voice must be recognisable in one paragraph.

## Surfaces

| Surface | URL / API | Who |
|---|---|---|
| Platform admin chart | `/admin/agents/org-chart` + `/api/v1/admin/agent-org/**` | Super/admin, org switcher |
| Portal org chart | `/portal/settings/agents/org-chart` + `/api/v1/portal/settings/agents/org-chart/**` | Org owner/admin; **active org auto-selected** |
| Live agents | `/admin/agents` or portal Agents | Machine registry / org agent packs |
| Task bus | Projects/Kanban | Real assignment + watcher dispatch |

Portal seed defaults: `platform` template for `pib-platform-owner`, `minimal` for client orgs. Idempotent if nodes exist.

## Operator brief Peet should give Pip

Collect before acting:

1. `orgId` (never guess client org)
2. Hierarchy: root + reportsTo edges
3. Per seat: name, title, capabilities, defaultModel/effort
4. Bind vs hire: reuse `theo` vs create `theo-fe` / `theo-be`
5. Target machines: Mac mini linked-device id and/or VPS fleet
6. Skill packs per profile (policy allowlist)
7. Whether to seed empty chart first

## Procedure

### A) Chart only (fast)

1. Resolve orgId; confirm active org if portal.
2. `GET` chart:
   - Admin: `GET /api/v1/admin/agent-org?orgId=…`
   - Portal: `GET /api/v1/portal/settings/agents/org-chart`
3. If empty and Peet wants starter: `POST …/seed` with `{ template: "platform"|"minimal" }` (admin body includes `orgId`).
4. Create/patch nodes (name, title, reportsTo, capabilities, defaults, agentId bind).
5. Verify tree has one logical root and no cycles.

### B) Make seats live (hire profiles)

For each seat that must run work:

1. Choose unique `agentId` (Hermes profile name), e.g. `theo-fe`.
2. Write a distinctive SOUL.md (quality bar above).
3. Provision profile on target machine(s) via `agent-runtime-ops` (registry + profile link + skills apply). Do not invent sidecar URLs.
4. Confirm profile appears on linked computers / agent health.
5. PATCH org node `agentId` to that profile id.
6. Optional admin-only: push model/effort to live `config.yaml` (Org role “Push to live Hermes” or runtime-model PUT). Portal chart does **not** rewrite machines by default.

### C) Multi-org pattern

- Repeat A/B per orgId. Charts never share nodes across orgs.
- Client orgs usually start with **minimal** unbound seats, then bind shared specialists or hire dedicated profiles.
- Shared fleet: multiple org seats may bind the same live `agentId` (same brain, different governance). Dedicated brains need separate profiles.

### D) Delegation behaviour Peet expects

“Theo knows the task and sends to the right specialist” today means:

1. Work lands on Kanban with `assigneeAgentId` (human, Pip, or lead).
2. Lead (e.g. theo) **creates child tasks** assigned to bound specialists when relationship rules allow.
3. Org chart gates agent→agent assign and fills default model/effort when blank.
4. It does **not** auto-pick a specialist from skills without an assign step.

If Peet wants automatic skill-based routing, that is a **future** router on top of this chart — out of scope for this setup skill unless explicitly specified and approved.

## API cheat sheet

Admin (carry `orgId`):

- `GET/POST /api/v1/admin/agent-org`
- `PATCH/DELETE /api/v1/admin/agent-org/:nodeId`
- `POST /api/v1/admin/agent-org/seed` body `{ orgId, template? }`

Portal (active org from session):

- `GET/POST /api/v1/portal/settings/agents/org-chart`
- `PATCH/DELETE /api/v1/portal/settings/agents/org-chart/:nodeId`
- `POST /api/v1/portal/settings/agents/org-chart/seed` body `{ template? }`

Auth: user-delegation Bearer + `X-Org-Id` for the target org. Portal routes use portal session + owner/admin role. Agent key may work for admin agent-org when profile env is configured.

## Verification

1. Chart GET returns expected nodes/tree for that orgId only.
2. Unbound seats: agentId null; bound seats match real profile ids.
3. Kanban task to bound agentId dispatches to linked runtime (watcher / hermes_runs).
4. Client org chart empty ≠ platform chart; seed minimal does not copy platform roster.
5. After profile hire: `agent-runtime-ops` health + skill-policy drift check if skills changed.
6. `/hire` appears in Messages slash menu for dispatch-capable users.
7. Wiki: short note under `agents/partners/wiki/` when a durable multi-org pattern is established.

## Pitfalls

- Binding FE/BE both to `theo` is fine for hierarchy/defaults but is **one** brain.
- Creating chart seats without profiles looks “live” in UI titles only — cyan chips need real runtime.
- Do not run normal app work on `main`; chart/UI code ships on `development` then scoped promote when Peet asks.
- Never claim portal chart save syncs all org machines — only explicit runtime push/provision does.
- Always resolve client orgId before client chart mutations.
- Do not over-hire: unused profiles still cost skill install, config drift, and cognitive load.

## Related

- `agent-runtime-ops` — day-to-day chart ops, provision/link Hermes profiles, skills apply, health
- `agent-skill-drift-gather` — after policy/profile changes
- `pib-system-skill-authoring` — landing this skill in policy packs
